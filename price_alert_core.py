"""
Core module for price alert functionality.
Contains common utilities for web scraping, email sending, and data processing.
"""

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import os

# Import configuration functions
from config import get_email_config, validate_email_config, print_setup_instructions
import logging

def setup_logging():
    """Configure logging with timestamp and level"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger('playwright').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

class PriceAlertScraper(ABC):
    """
    Abstract base class for price alert scrapers.
    Each specific scraper should inherit from this class and implement the required methods.
    """
    
    def __init__(self):
        # Set pandas display options for better console output
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 1000)
    
    @abstractmethod
    async def scrape_data(self, page) -> List[Dict[str, Any]]:
        """
        Abstract method to be implemented by each scraper.
        Should return a list of dictionaries containing the scraped data.
        """
        pass
    
    @abstractmethod
    def check_alert_condition(self, df: pd.DataFrame) -> bool:
        """
        Abstract method to check if alert condition is met.
        Should return True if alert should be sent.
        """
        pass
    
    @abstractmethod
    def get_email_subject(self) -> str:
        """
        Abstract method to get the email subject line.
        """
        pass
    
    @abstractmethod
    def get_email_body(self, df: pd.DataFrame) -> str:
        """
        Abstract method to get the email HTML body.
        """
        pass
    
    @abstractmethod
    def get_scraping_url(self) -> str:
        """
        Abstract method to get the URL to scrape.
        """
        pass

class EmailTemplate:
    """Base class for email templates with common HTML structure."""
    
    @staticmethod
    def create_html_body(title: str, message: str, table_html: str, booking_url: str = None, config_info: str = None) -> str:
        """
        Create standardized HTML email body with optional configuration information.
        
        Args:
            title: Email title
            message: Main message content
            table_html: HTML table with results
            booking_url: Optional booking URL
            config_info: Optional configuration information to display
        """
        booking_link = ""
        if booking_url:
            booking_link = f'<p><a href="{booking_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Click here to book</a></p>'
        
        config_section = ""
        if config_info:
            config_section = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #007bff;">Search Configuration</h3>
                {config_info}
            </div>
            """
        
        return f"""
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; margin: 20px; }}
              table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
              th, td {{ border: 1px solid #dddddd; text-align: left; padding: 12px; }}
              th {{ background-color: #f2f2f2; font-weight: bold; }}
              tr:nth-child(even) {{ background-color: #f9f9f9; }}
              .alert-row {{ background-color: #d4edda !important; }}
              h2 {{ color: #333; }}
              h3 {{ color: #007bff; }}
              .config-item {{ margin: 5px 0; }}
              .config-label {{ font-weight: bold; color: #555; }}
            </style>
          </head>
          <body>
            <h2>{title}</h2>
            <p>{message}</p>
            {config_section}
            {table_html}
            {booking_link}
          </body>
        </html>
        """

class EmailSender:
    """Handles email sending functionality."""
    
    @staticmethod
    def send_email(subject: str, html_body: str, recipient: str = None):
        """
        Sends an HTML email using Gmail SMTP.
        
        Args:
            subject: Email subject line
            html_body: HTML content of the email
            recipient: Recipient email address (optional, uses config if not provided)
        """
        # Validate email configuration first
        if not validate_email_config():
            print("\n" + "="*60)
            logger.error("EMAIL CONFIGURATION ERROR")
            logger.info("="*60)
            print_setup_instructions()
            raise RuntimeError("Email configuration is incomplete. Please set your credentials.")
        
        email_config = get_email_config()
        sender_email = email_config["sender_email"]
        sender_password = email_config["sender_password"]
        recipient_email = recipient or email_config["recipient_email"]
        
        
        logger.info(f"Condition met! Preparing to send email to {recipient_email}...")
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        message.attach(MIMEText(html_body, "html"))
        
        try:
            with smtplib.SMTP_SSL(email_config["smtp_server"], email_config["smtp_port"]) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
            logger.info("✓ Email sent successfully!")
        except Exception as e:
            logger.error(f"✗ Failed to send email. Error: {e}")
            logger.info("Troubleshooting tips:")
            logger.info("- Check that your Gmail credentials are correct")
            logger.info("- Ensure 2-Factor Authentication is enabled")
            logger.info("- Use an App Password, not your regular password")
            logger.info("- Check that 'Less secure app access' is disabled")
            raise

class WebScraper:
    """Handles web scraping infrastructure."""
    
    @staticmethod
    async def scrape_with_playwright(scraper: PriceAlertScraper) -> Optional[pd.DataFrame]:
        """
        Generic web scraping method using Playwright.
        
        Args:
            scraper: PriceAlertScraper instance with specific scraping logic
            
        Returns:
            DataFrame with scraped data or None if scraping failed
        """
        results_data = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            try:
                logger.info("--- Starting Automation ---")
                url = scraper.get_scraping_url()
                logger.info(f"Scraping URL: {url}")
                await page.goto(url, timeout=60000)
                
                # Call the specific scraper's data extraction method
                results_data = await scraper.scrape_data(page)
                
            except Exception as e:
                logger.error(f"An error occurred during scraping: {e}")
            finally:
                await browser.close()
                
        if results_data:
            return pd.DataFrame(results_data)
        else:
            return None

async def run_price_alert(scraper: PriceAlertScraper):
    """
    Main function to run a price alert scraper.
    
    Args:
        scraper: PriceAlertScraper instance to run
    """
    df = await WebScraper.scrape_with_playwright(scraper)
    
    df = await WebScraper.scrape_with_playwright(scraper)
    
    if df is not None and not df.empty:
        logger.info(f"--- Scraped Data ---")
        # Log basic stats instead of full dataframe to keep logs clean
        logger.info(f"Retrieved {len(df)} records")
        
        # Check if alert condition is met
        if scraper.check_alert_condition(df):
            email_body = scraper.get_email_body(df)
            EmailSender.send_email(
                subject=scraper.get_email_subject(),
                html_body=email_body
            )
        else:
            logger.info("No alert condition met. No email sent.")
    else:
        logger.info("No data was scraped.")

def run_async_scraper(scraper: PriceAlertScraper):
    """
    Helper function to run an async scraper from a synchronous context.
    
    Args:
        scraper: PriceAlertScraper instance to run
    """
    asyncio.run(run_price_alert(scraper))
