#!/usr/bin/env python3
"""
Unified runner for price alert scrapers.
Can execute any configured scraper based on command line arguments.
"""

import argparse
import sys
from typing import Optional

from price_alert_core import PriceAlertScraper, run_async_scraper, logger
from power_to_choose_scraper import PowerToChooseScraper
from villa_del_arco_scraper import VillaDelArcoScraper
from alaska_award_ticket_scraper import AlaskaAwardTicketScraper
from config import get_config

# Centralized scraper registry
SCRAPER_REGISTRY = {
    "power_to_choose": {
        "class": PowerToChooseScraper,
        "description": "Monitor electricity plan prices from Power to Choose"
    },
    "villa_del_arco": {
        "class": VillaDelArcoScraper,
        "description": "Monitor hotel prices from Villa del Arco"
    },
    "alaska_award_ticket": {
        "class": AlaskaAwardTicketScraper,
        "description": "Monitor Alaska Airlines award ticket availability (7.5k points)"
    }
}

def create_scraper(scraper_name: str) -> Optional[PriceAlertScraper]:
    """
    Create a scraper instance based on the name.
    
    Args:
        scraper_name: Name of the scraper to create
        
    Returns:
        PriceAlertScraper instance or None if invalid name
    """
    scraper_info = SCRAPER_REGISTRY.get(scraper_name)
    if not scraper_info:
        return None
    
    config = get_config(scraper_name)
    return scraper_info["class"](**config)

def list_available_scrapers():
    """List all available scrapers"""
    print("Available scrapers:")
    for name, info in SCRAPER_REGISTRY.items():
        print(f"  {name:<20} - {info['description']}")
    print("\nUsage: python run_scraper.py <scraper_name>")
    print("Example: python run_scraper.py alaska_award_ticket")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run price alert scrapers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py power_to_choose
  python run_scraper.py villa_del_arco
  python run_scraper.py alaska_award_ticket
  python run_scraper.py --list
        """
    )
    
    parser.add_argument(
        "scraper_name",
        nargs="?",
        help="Name of the scraper to run"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available scrapers"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_scrapers()
        return
    
    if args.config:
        print("Current configuration:")
        print(f"Power to Choose: {get_config('power_to_choose')}")
        print(f"Villa del Arco: {get_config('villa_del_arco')}")
        print(f"Alaska Award Ticket: {get_config('alaska_award_ticket')}")
        return
    
from price_alert_core import PriceAlertScraper, run_async_scraper, logger

def run_scraper_safe(name: str, scraper: PriceAlertScraper) -> bool:
    """Run a scraper and catch any exceptions"""
    try:
        logger.info(f"Starting {name} scraper...")
        run_async_scraper(scraper)
        logger.info(f"✓ {name} scraper completed successfully")
        return True
    except Exception as e:
        logger.error(f"✗ {name} scraper failed: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run price alert scrapers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py power_to_choose
  python run_scraper.py villa_del_arco
  python run_scraper.py alaska_award_ticket
  python run_scraper.py all
  python run_scraper.py --list
        """
    )
    
    parser.add_argument(
        "scraper_name",
        nargs="?",
        default="all",
        help="Name of the scraper to run (default: all)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available scrapers"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_scrapers()
        return
    
    if args.config:
        print("Current configuration:")
        print(f"Power to Choose: {get_config('power_to_choose')}")
        print(f"Villa del Arco: {get_config('villa_del_arco')}")
        print(f"Alaska Award Ticket: {get_config('alaska_award_ticket')}")
        return
    
    # Handle 'all' case
    if args.scraper_name == "all":
        logger.info("Running all scrapers sequentially...")
        results = {}
        for name in SCRAPER_REGISTRY:
            scraper = create_scraper(name)
            if scraper:
                results[name] = run_scraper_safe(name, scraper)
            else:
                logger.error(f"Failed to create scraper {name}")
                results[name] = False
                
        # Summary
        logger.info("\n=== All Scrapers Completed ===")
        success = all(results.values())
        for name, result in results.items():
            status = "✓" if result else "✗"
            logger.info(f"{status} {name}")
            
        sys.exit(0 if success else 1)
        
    # Run specific scraper
    scraper = create_scraper(args.scraper_name)
    
    if scraper is None:
        logger.error(f"Error: Unknown scraper '{args.scraper_name}'")
        print("Use --list to see available scrapers.")
        sys.exit(1)
    
    if run_scraper_safe(args.scraper_name, scraper):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
