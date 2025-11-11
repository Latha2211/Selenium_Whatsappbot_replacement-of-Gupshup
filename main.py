"""
WhatsApp Sales Bot - Main Application
Multi-threaded WhatsApp automation system for educational lead management.
"""

import os
import sys
import json
import time
import random
import threading
import traceback
import re
import pyautogui
import schedule
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

from helpers import DatabaseHelper, WhatsAppHelper, MessageHelper, EmailHelper

# Load environment variables
load_dotenv()

# Configuration from environment
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
MESSAGES_FILE = os.getenv("MESSAGES_FILE")
CONFIG_FILE = os.getenv("CONFIG_FILE", "config.json")
REPORT_ERROR_TO = os.getenv("REPORT_ERROR_TO")
REPORT_DAILY_TO = os.getenv("REPORT_DAILY_TO")
DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "13:04")

# Database connection string
DB_CONN_STR = (
    f"Driver={{{os.getenv('DB_DRIVER')}}};"
    f"Server={os.getenv('DB_SERVER')};"
    f"Database={os.getenv('DB_NAME')};"
    f"Trusted_Connection={os.getenv('DB_TRUSTED')};"
)

# Load bot configuration
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

BOTS_CONFIG = CONFIG["bots"]
SETTINGS = CONFIG["settings"]

# Settings
POLL_INTERVAL = SETTINGS.get("poll_interval", 30)
BATCH_SIZE = SETTINGS.get("batch_size", 5)
DELAY_MIN = SETTINGS.get("message_delay_min", 3)
DELAY_MAX = SETTINGS.get("message_delay_max", 6)
ANTI_LOCK_INTERVAL = SETTINGS.get("anti_lock_interval", 240)

# Setup logging
os.makedirs("logs", exist_ok=True)
os.makedirs("errors", exist_ok=True)
logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <white>{message}</white>"
)
logger.add(
    "logs/bot_{time:YYYYMMDD}.log",
    level="DEBUG",
    rotation="7 days",
    retention="30 days",
    compression="zip"
)

# Initialize helpers
db_helper = DatabaseHelper(DB_CONN_STR)
whatsapp_helper = WhatsAppHelper(CHROMEDRIVER_PATH)
message_helper = MessageHelper(MESSAGES_FILE)
email_helper = EmailHelper(
    server=os.getenv("MAIL_SERVER"),
    port=int(os.getenv("MAIL_PORT", "587")),
    use_tls=os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1", "yes"),
    username=os.getenv("MAIL_USERNAME"),
    password=os.getenv("MAIL_PASSWORD"),
    sender=os.getenv("MAIL_DEFAULT_SENDER")
)


def send_whatsapp_message(driver, name, program, phone, bot_name):
    """
    Send a WhatsApp message to a lead.
    
    Args:
        driver: Selenium WebDriver instance
        name (str): Lead name
        program (str): Program name
        phone (str): Phone number
        bot_name (str): Bot identifier
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    logger.info(f"[{bot_name}] → {name} | {program}")
    
    try:
        # Format message using template
        message_text = message_helper.format_message(name, program, phone)
        
        # Send message via WhatsApp
        success = whatsapp_helper.send_message(driver, message_text)
        
        if success:
            logger.success(f"[{bot_name}] Message sent to {name}")
        else:
            logger.error(f"[{bot_name}] Failed to send message to {name}")
        
        return success
        
    except Exception as e:
        # Capture error screenshot
        error_id = datetime.now().strftime("%H%M%S")
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        screenshot_path = f"errors/error_{error_id}_{safe_name}_{bot_name}.png"
        
        try:
            driver.save_screenshot(screenshot_path)
        except:
            screenshot_path = None
        
        # Log and send error notification
        error_text = traceback.format_exc()
        logger.error(f"[{bot_name}] Error sending message: {error_text}")
        
        if REPORT_ERROR_TO:
            email_helper.send_error_notification(
                name=name,
                phone=phone,
                program=program,
                bot_name=bot_name,
                error_text=error_text,
                screenshot_path=screenshot_path,
                to_email=REPORT_ERROR_TO
            )
        
        return False


def process_lead(driver, lead, bot_name):
    """
    Process a single lead: search contact and send message.
    
    Args:
        driver: Selenium WebDriver instance
        lead: Database row containing lead information
        bot_name (str): Bot identifier
        
    Returns:
        dict: Result dictionary with status information
    """
    raw_phone = str(lead.Phone)
    name = lead.FirstName or "Student"
    program = lead.mx_Program_Name or "Unknown"
    owner = lead.OwnerIdName
    campus = lead.mx_Program_Campus or "NULL"
    
    # Clean and validate phone number
    phone = message_helper.clean_phone_number(raw_phone)
    if not phone:
        return None
    
    status = "Pending"
    
    # Attempt to send message (with retry)
    for attempt in range(2):
        try:
            # Click new chat button
            if not whatsapp_helper.click_new_chat(driver):
                status = "Failed-NewChat"
                break
            
            # Search and open contact
            if not whatsapp_helper.search_and_open_contact(driver, phone):
                status = "NotFound"
                whatsapp_helper.close_chat(driver)
                break
            
            # Send message
            if send_whatsapp_message(driver, name, program, phone, bot_name):
                status = "Sent"
                break
            else:
                status = "Failed-Send"
                break
                
        except Exception as e:
            logger.error(f"[{bot_name}] Attempt {attempt + 1} failed: {e}")
            if attempt == 1:
                status = "Error"
            time.sleep(5)
    
    # Close chat and add delay
    whatsapp_helper.close_chat(driver)
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    
    # Return result
    return {
        'lead_name': name,
        'Phone': phone.replace('+', ''),
        'Program': program,
        'Degree_Awarding_Body': owner,
        'mx_Program_Campus': str(campus),
        'Status_lead': status,
        'Date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def run_bot(bot_name, campuses, profile_path):
    """
    Main bot loop - continuously processes leads.
    
    Args:
        bot_name (str): Bot identifier
        campuses (list): List of campuses to process
        profile_path (str): Chrome profile path
    """
    logger.info(f"[{bot_name}] Starting bot for campuses: {campuses}")
    
    # Setup Chrome driver
    driver = whatsapp_helper.setup_driver(profile_path, bot_name)
    if not driver:
        logger.critical(f"[{bot_name}] Failed to initialize driver")
        return
    
    # Load WhatsApp Web
    driver.get("https://web.whatsapp.com")
    if not whatsapp_helper.wait_for_whatsapp_load(driver, bot_name):
        driver.quit()
        return
    
    # Track processed phones to avoid duplicates
    processed_phones = set()
    
    # Main loop
    while True:
        try:
            # Fetch new leads from database
            leads = db_helper.fetch_leads(campuses, processed_phones, BATCH_SIZE)
            
            if not leads:
                time.sleep(POLL_INTERVAL)
                continue
            
            logger.success(f"[{bot_name}] Processing {len(leads)} leads")
            results = []
            
            # Process each lead
            for lead in leads:
                result = process_lead(driver, lead, bot_name)
                if result:
                    results.append(result)
                    processed_phones.add(str(lead.Phone))
            
            # Save results to database
            if results:
                db_helper.insert_lead_status(results)
                
                sent_count = sum(1 for r in results if r['Status_lead'] == 'Sent')
                logger.info(f"[{bot_name}] Batch complete: {sent_count} sent")
            
        except KeyboardInterrupt:
            logger.warning(f"[{bot_name}] Keyboard interrupt received")
            break
        except Exception as e:
            logger.critical(f"[{bot_name}] Unexpected error: {e}")
            time.sleep(POLL_INTERVAL)
    
    # Cleanup
    driver.quit()
    logger.info(f"[{bot_name}] Bot stopped")


def anti_lock_thread():
    """
    Background thread to prevent system sleep/lock.
    Simulates mouse and keyboard activity at regular intervals.
    """
    logger.info("Anti-lock system started")
    
    while True:
        try:
            # Get current mouse position
            x, y = pyautogui.position()
            
            # Small mouse wiggle
            pyautogui.moveTo(x + 1, y + 1, duration=0.1)
            pyautogui.moveTo(x, y, duration=0.1)
            
            # Press Shift key
            pyautogui.press('shift')
            
            # Log activity
            current_time = time.strftime('%H:%M:%S')
            logger.debug(f"Anti-lock activity at {current_time}")
            
            # Sleep until next interval
            time.sleep(ANTI_LOCK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Anti-lock error: {e}")
            time.sleep(60)


def daily_report_task():
    """
    Generate and send daily statistics report via email.
    """
    try:
        logger.info("Generating daily report...")
        
        # Fetch statistics from database
        stats = db_helper.get_daily_stats()
        
        if not stats:
            logger.info("No data for daily report")
            return
        
        # Send report email
        if REPORT_DAILY_TO:
            success = email_helper.send_daily_report(stats, REPORT_DAILY_TO)
            if success:
                logger.success("Daily report sent successfully")
            else:
                logger.error("Failed to send daily report")
        
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")


def scheduler_thread():
    """
    Background thread for scheduled tasks (daily reports).
    """
    report_time = DAILY_REPORT_TIME.strip()
    logger.info(f"Scheduler started - Daily report at {report_time}")
    
    schedule.every().day.at(report_time).do(daily_report_task)
    
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """
    Main application entry point.
    Initializes all bots and background threads.
    """
    logger.info("=" * 70)
    logger.info(" TEXILA WHATSAPP SALES BOT SYSTEM")
    logger.info(" Multi-Campus Lead Management & Automation")
    logger.info("=" * 70)
    
    # Start anti-lock thread
    threading.Thread(target=anti_lock_thread, daemon=True).start()
    
    # Start scheduler thread
    threading.Thread(target=scheduler_thread, daemon=True).start()
    
    # Wait for user confirmation
    input("\nPress ENTER to start all bots...\n")
    
    # Launch all bots in separate threads
    bot_threads = []
    for bot_name, config in BOTS_CONFIG.items():
        thread = threading.Thread(
            target=run_bot,
            args=(bot_name, config["campuses"], config["profile"]),
            daemon=True
        )
        thread.start()
        bot_threads.append(thread)
        time.sleep(15)  # Stagger bot launches
    
    logger.success(f"All {len(BOTS_CONFIG)} bots launched successfully!")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.warning("Shutting down all bots...")


if __name__ == "__main__":
    main()
