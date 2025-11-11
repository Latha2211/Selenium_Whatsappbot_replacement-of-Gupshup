"""
WhatsApp Helper Functions
Handles all WhatsApp Web automation using Selenium.
"""

import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from loguru import logger


class WhatsAppHelper:
    def __init__(self, chromedriver_path):
        """
        Initialize WhatsApp helper.
        
        Args:
            chromedriver_path (str): Path to ChromeDriver executable
        """
        self.chromedriver_path = chromedriver_path
    
    def setup_driver(self, profile_path, bot_name):
        """
        Set up Chrome driver with WhatsApp-specific options.
        
        Args:
            profile_path (str): Path to Chrome profile directory
            bot_name (str): Name of the bot for logging
            
        Returns:
            webdriver.Chrome or None: Configured Chrome driver
        """
        logger.info(f"[{bot_name}] Setting up Chrome driver...")
        try:
            options = Options()
            options.add_argument(f"--user-data-dir={profile_path}")
            options.add_argument("--profile-directory=Default")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--log-level=3")
            
            service = Service(self.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            # Remove webdriver property for anti-detection
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            logger.success(f"[{bot_name}] Chrome driver ready")
            return driver
        except Exception as e:
            logger.critical(f"[{bot_name}] Driver setup failed: {e}")
            return None
    
    @staticmethod
    def wait_for_whatsapp_load(driver, bot_name, timeout=30):
        """
        Wait for WhatsApp Web to fully load.
        
        Args:
            driver: Selenium WebDriver instance
            bot_name (str): Name of the bot for logging
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        logger.info(f"[{bot_name}] Waiting for WhatsApp Web to load...")
        try:
            # Wait for main app div
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='app']"))
            )
            time.sleep(3)
            
            # Check for QR code (first-time login)
            if driver.find_elements(By.XPATH, "//canvas[@aria-label='Scan me!']"):
                logger.warning(f"[{bot_name}] QR code detected - please scan to login")
                WebDriverWait(driver, 60).until_not(
                    EC.presence_of_element_located(
                        (By.XPATH, "//canvas[@aria-label='Scan me!']")
                    )
                )
            
            logger.success(f"[{bot_name}] WhatsApp Web loaded successfully")
            return True
        except TimeoutException:
            logger.error(f"[{bot_name}] WhatsApp Web load timeout")
            return False
    
    @staticmethod
    def click_new_chat(driver):
        """
        Click the 'New Chat' button in WhatsApp Web.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        selectors = [
            "//div[@title='New chat']",
            "//button[@aria-label='New chat']",
            "//span[@data-icon='new-chat-outline']/../.."
        ]
        
        for selector in selectors:
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
                return True
            except:
                continue
        
        logger.warning("Failed to click 'New Chat' button")
        return False
    
    @staticmethod
    def search_and_open_contact(driver, phone):
        """
        Search for and open a contact in WhatsApp Web.
        
        Args:
            driver: Selenium WebDriver instance
            phone (str): Phone number to search
            
        Returns:
            bool: True if contact found and opened, False otherwise
        """
        try:
            # Find search box
            search_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
                )
            )
            
            # Clear and enter phone number
            search_box.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            search_box.send_keys(phone)
            time.sleep(3)
            
            # Press Enter to open chat
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)
            
            # Verify chat opened by checking for message box
            message_box_selectors = [
                "//div[@contenteditable='true'][@data-tab='10']",
                "//div[@title='Type a message']",
                "//span[@data-icon='clip']"
            ]
            
            for selector in message_box_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.warning(f"Search and open contact failed: {e}")
            return False
    
    @staticmethod
    def send_message(driver, message_text):
        """
        Send a message in the currently open WhatsApp chat.
        
        Args:
            driver: Selenium WebDriver instance
            message_text (str): Message to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Find message input box
            message_box = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                )
            )
            
            # Use clipboard to preserve formatting and emojis
            pyperclip.copy(message_text)
            message_box.click()
            message_box.clear()
            message_box.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            # Send message
            message_box.send_keys(Keys.ENTER)
            time.sleep(2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    @staticmethod
    def close_chat(driver):
        """
        Close the current chat and return to main screen.
        
        Args:
            driver: Selenium WebDriver instance
        """
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
        except:
            pass
