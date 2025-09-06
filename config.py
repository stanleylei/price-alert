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
    "max_results": int(os.getenv("PTC_MAX_RESULTS", "5")),
    "base_url": os.getenv("PTC_BASE_URL", "https://www.powertochoose.org/en-us")
}

# Villa del Arco Configuration
VILLA_DEL_ARCO_CONFIG = {
    "check_in_date": os.getenv("VDA_CHECK_IN", "2025-12-16"),
    "check_out_date": os.getenv("VDA_CHECK_OUT", "2025-12-19"),
    "adults": int(os.getenv("VDA_ADULTS", "2")),
    "children": int(os.getenv("VDA_CHILDREN", "2")),
    "price_threshold_usd": int(os.getenv("VDA_PRICE_THRESHOLD", "1100")),
    "base_url": os.getenv("VDA_BASE_URL", "https://booking.villadelarco.com/bookcore/availability/villarco/{check_in}/{check_out}/{adults}/{children}/?lang=en&rrc=1&adults={adults}&ninos={children}")
}

# Alaska Airlines Award Ticket Configuration
ALASKA_AWARD_TICKET_CONFIG = {
    "departure_station": os.getenv("ALASKA_DEPARTURE", "DFW"),
    "target_arrival_stations": os.getenv("ALASKA_ARRIVAL_STATIONS", "SNA,ONT").split(","),
    "target_points": int(os.getenv("ALASKA_TARGET_POINTS", "7500")),
    "search_date": os.getenv("ALASKA_SEARCH_DATE", "2025-11-14"),
    "base_search_url": os.getenv("ALASKA_BASE_SEARCH_URL", "https://www.alaskaair.com/search/results?A=3&C=2&L=0&O={departure}&D={arrival}&OD={date}&RT=false&ShoppingMethod=onlineaward")
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
        scraper_name: Name of the scraper ('power_to_choose', 'villa_del_arco', or 'alaska_award_ticket')
        
    Returns:
        Dictionary containing the scraper's configuration
    """
    configs = {
        "power_to_choose": POWER_TO_CHOOSE_CONFIG,
        "villa_del_arco": VILLA_DEL_ARCO_CONFIG,
        "alaska_award_ticket": ALASKA_AWARD_TICKET_CONFIG
    }
    
    config = configs.get(scraper_name, {})
    
    # Map config keys to match scraper constructor parameters
    if scraper_name == "power_to_choose":
        return {
            "zip_code": config["zip_code"],
            "contract_min": config["contract_min_months"],
            "contract_max": config["contract_max_months"],
            "base_url": config["base_url"]
        }
    elif scraper_name == "villa_del_arco":
        return {
            "check_in_date": config["check_in_date"],
            "check_out_date": config["check_out_date"],
            "adults": config["adults"],
            "children": config["children"],
            "base_url": config["base_url"]
        }
    elif scraper_name == "alaska_award_ticket":
        return {
            "departure_station": config["departure_station"],
            "target_arrival_stations": config["target_arrival_stations"],
            "target_points": config["target_points"],
            "search_date": config["search_date"],
            "base_search_url": config["base_search_url"]
        }
    
    return config

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
