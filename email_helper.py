"""
Email Helper Functions
Handles email notifications for errors and daily reports using SMTP.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr
from datetime import datetime
from collections import defaultdict
from loguru import logger


class EmailHelper:
    def __init__(self, server, port, use_tls, username, password, sender):
        """
        Initialize email helper with SMTP configuration.
        
        Args:
            server (str): SMTP server address
            port (int): SMTP port
            use_tls (bool): Whether to use TLS
            username (str): SMTP username
            password (str): SMTP password
            sender (str): Sender email address
        """
        self.server = server
        self.port = port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self.sender = sender
    
    def send_email(self, subject, html_body, to_email, screenshot_path=None):
        """
        Send an email with optional screenshot attachment.
        
        Args:
            subject (str): Email subject
            html_body (str): HTML email body
            to_email (str): Recipient email address
            screenshot_path (str, optional): Path to screenshot file
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            if not all([self.server, self.username, self.password, self.sender, to_email]):
                logger.error("SMTP configuration incomplete")
                return False
            
            # Create message
            msg = MIMEMultipart("related")
            msg["From"] = formataddr(("Texila WhatsApp Bot", self.sender))
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_body, "html"))
            
            # Attach screenshot if provided
            if screenshot_path and os.path.exists(screenshot_path):
                with open(screenshot_path, "rb") as f:
                    img = MIMEImage(f.read(), _subtype="png")
                    img.add_header("Content-ID", "<screenshot>")
                    img.add_header(
                        "Content-Disposition",
                        "inline",
                        filename=os.path.basename(screenshot_path)
                    )
                    msg.attach(img)
            
            # Send email
            with smtplib.SMTP(self.server, self.port, timeout=15) as smtp:
                if self.use_tls:
                    smtp.starttls()
                smtp.login(self.username, self.password)
                smtp.send_message(msg)
            
            logger.success(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_error_notification(self, name, phone, program, bot_name, 
                                error_text, screenshot_path, to_email):
        """
        Send error notification email with details and screenshot.
        
        Args:
            name (str): Lead name
            phone (str): Phone number
            program (str): Program name
            bot_name (str): Bot identifier
            error_text (str): Error traceback
            screenshot_path (str): Path to error screenshot
            to_email (str): Recipient email
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #d32f2f;">⚠️ WhatsApp Bot Error</h2>
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Bot:</strong> {bot_name}</p>
                <p><strong>Lead Name:</strong> {name}</p>
                <p><strong>Phone:</strong> {phone}</p>
                <p><strong>Program:</strong> {program}</p>
            </div>
            
            <h3 style="color: #666;">Error Details:</h3>
            <pre style="background: #f4f4f4; padding: 15px; border-left: 4px solid #d32f2f; 
                        overflow-x: auto; font-size: 12px;">{error_text}</pre>
            
            <h3 style="color: #666;">Screenshot:</h3>
            <img src="cid:screenshot" style="max-width: 800px; border: 1px solid #ddd;">
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #999; font-size: 12px;">
                This is an automated notification from the WhatsApp Bot System.
            </p>
        </body>
        </html>
        """
        
        subject = f"🚨 WhatsApp Bot Error - {name} ({bot_name})"
        return self.send_email(subject, html_body, to_email, screenshot_path)
    
    def send_daily_report(self, stats_rows, to_email):
        """
        Send daily statistics report email.
        
        Args:
            stats_rows (list): List of tuples (campus, status, count)
            to_email (str): Recipient email
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not stats_rows:
            logger.info("No data for daily report")
            return False
        
        # Group by campus
        campus_data = defaultdict(lambda: {"Sent": 0, "Failed-Send": 0, 
                                           "NotFound": 0, "total": 0})
        
        for row in stats_rows:
            campus = row.mx_Program_Campus or "NULL"
            status = row.Status_lead
            count = row.cnt
            campus_data[campus][status] += count
            campus_data[campus]["total"] += count
        
        # Calculate totals
        total_sent = sum(d["Sent"] for d in campus_data.values())
        total_failed = sum(d["Failed-Send"] for d in campus_data.values())
        total_notfound = sum(d["NotFound"] for d in campus_data.values())
        grand_total = total_sent + total_failed + total_notfound
        success_rate = round(total_sent / grand_total * 100, 1) if grand_total else 0
        
        # Build table rows
        table_rows = ""
        for campus, data in sorted(campus_data.items()):
            table_rows += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>{campus}</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center; 
                           color: #4caf50;">{data['Sent']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center; 
                           color: #f44336;">{data['Failed-Send']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">
                    {data['NotFound']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center; 
                           font-weight: bold;">{data['total']}</td>
            </tr>
            """
        
        # Total row
        total_row = f"""
        <tr style="background: #e3f2fd; font-weight: bold;">
            <td style="padding: 10px; border: 1px solid #ddd;">TOTAL</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; 
                       color: #4caf50;">{total_sent}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; 
                       color: #f44336;">{total_failed}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">
                {total_notfound}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">
                {grand_total}</td>
        </tr>
        """
        
        # Determine success color
        if success_rate >= 70:
            rate_color = "#4caf50"
        elif success_rate >= 40:
            rate_color = "#ff9800"
        else:
            rate_color = "#f44336"
        
        # Build HTML
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1976d2;">📊 Daily WhatsApp Report</h2>
            <p style="color: #666; font-size: 16px;">
                {datetime.now().strftime('%A, %d %B %Y')}
            </p>
            
            <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; 
                        margin: 20px 0;">
                <p style="font-size: 18px; margin: 5px 0;">
                    <strong>Messages Sent:</strong> {total_sent} / {grand_total}
                </p>
                <p style="font-size: 24px; margin: 10px 0;">
                    <strong style="color: {rate_color};">Success Rate: {success_rate}%</strong>
                </p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0; 
                          box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background: #1976d2; color: white;">
                        <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">
                            Campus</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Sent</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Failed</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Not Found</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                    {total_row}
                </tbody>
            </table>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #999; font-size: 12px;">
                <em>Report generated at {datetime.now().strftime('%I:%M %p IST')}</em><br>
                This is an automated daily report from the WhatsApp Bot System.
            </p>
        </body>
        </html>
        """
        
        subject = f"📊 WhatsApp Daily Report - {total_sent}/{grand_total} ({success_rate}%)"
        return self.send_email(subject, html_body, to_email)
