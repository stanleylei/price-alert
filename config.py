"""
Configuration file for price alert scrapers.
Centralizes all settings and makes them easily configurable.

IMPORTANT: For security, do NOT commit your actual email credentials to this repository.
Instead, set them as environment variables or create a local .env file.
"""

import os
from typing import Dict, Any

# Email Configuration
# WARNING: These are placeholder values. Set your actual credentials via environment variables.
EMAIL_CONFIG = {
    "sender_email": os.getenv("SENDER_EMAIL", ""),
    "sender_password": os.getenv("SENDER_PASSWORD", ""),
    "recipient_email": os.getenv("RECIPIENT_EMAIL", ""),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465
}

# Power to Choose Configuration
POWER_TO_CHOOSE_CONFIG = {
    "zip_code": os.getenv("PTC_ZIP_CODE", "76092"),
    "contract_min_months": os.getenv("PTC_CONTRACT_MIN", "12"),
    "contract_max_months": os.getenv("PTC_CONTRACT_MAX", "60"),
    "price_threshold_cents": float(os.getenv("PTC_PRICE_THRESHOLD", "12.4")),
    "max_results": int(os.getenv("PTC_MAX_RESULTS", "5"))
}

# Villa del Arco Configuration
VILLA_DEL_ARCO_CONFIG = {
    "check_in_date": os.getenv("VDA_CHECK_IN", "2025-12-16"),
    "check_out_date": os.getenv("VDA_CHECK_OUT", "2025-12-19"),
    "adults": int(os.getenv("VDA_ADULTS", "2")),
    "children": int(os.getenv("VDA_CHILDREN", "2")),
    "price_threshold_usd": int(os.getenv("VDA_PRICE_THRESHOLD", "1100"))
}

# Web Scraping Configuration
SCRAPING_CONFIG = {
    "timeout": int(os.getenv("SCRAPING_TIMEOUT", "60000")),
    "wait_timeout": int(os.getenv("SCRAPING_WAIT_TIMEOUT", "30000")),
    "headless": os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
    "no_sandbox": os.getenv("BROWSER_NO_SANDBOX", "true").lower() == "true"
}

def get_config(scraper_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific scraper.
    
    Args:
        scraper_name: Name of the scraper ('power_to_choose' or 'villa_del_arco')
        
    Returns:
        Dictionary containing the scraper's configuration
    """
    configs = {
        "power_to_choose": POWER_TO_CHOOSE_CONFIG,
        "villa_del_arco": VILLA_DEL_ARCO_CONFIG
    }
    
    return configs.get(scraper_name, {})

def get_email_config() -> Dict[str, Any]:
    """Get email configuration"""
    return EMAIL_CONFIG.copy()

def get_scraping_config() -> Dict[str, Any]:
    """Get web scraping configuration"""
    return SCRAPING_CONFIG.copy()

def validate_email_config() -> bool:
    """
    Validate that email configuration is properly set.
    
    Returns:
        True if email configuration is valid, False otherwise
    """
    email_config = get_email_config()
    
    if not email_config["sender_email"]:
        print("ERROR: SENDER_EMAIL environment variable is not set")
        print("Please set it to your Gmail address")
        return False
    
    if not email_config["sender_password"]:
        print("ERROR: SENDER_PASSWORD environment variable is not set")
        print("Please set it to your Gmail app password")
        return False
    
    if not email_config["recipient_email"]:
        print("ERROR: RECIPIENT_EMAIL environment variable is not set")
        print("Please set it to the email address where you want to receive alerts")
        return False
    
    return True

def print_setup_instructions():
    """Print setup instructions for users"""
    print("=" * 60)
    print("PRICE ALERT SCRAPER SETUP INSTRUCTIONS")
    print("=" * 60)
    print()
    print("1. Set your email credentials as environment variables:")
    print("   export SENDER_EMAIL='your-email@gmail.com'")
    print("   export SENDER_PASSWORD='your-gmail-app-password'")
    print("   export RECIPIENT_EMAIL='recipient@example.com'")
    print()
    print("2. Or create a .env file in this directory:")
    print("   SENDER_EMAIL=your-email@gmail.com")
    print("   SENDER_PASSWORD=your-gmail-app-password")
    print("   RECIPIENT_EMAIL=recipient@example.com")
    print()
    print("3. For Gmail, you need to:")
    print("   - Enable 2-Factor Authentication")
    print("   - Generate an App Password (not your regular password)")
    print("   - Use the App Password in SENDER_PASSWORD")
    print()
    print("4. Test the setup:")
    print("   python run_scraper.py --config")
    print("=" * 60)
