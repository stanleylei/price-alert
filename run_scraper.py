#!/usr/bin/env python3
"""
Unified runner for price alert scrapers.
Can execute any configured scraper based on command line arguments.
"""

import argparse
import sys
from typing import Optional

from price_alert_core import PriceAlertScraper, run_async_scraper
from power_to_choose_scraper import PowerToChooseScraper
from villa_del_arco_scraper import VillaDelArcoScraper
from config import get_config

def create_scraper(scraper_name: str) -> Optional[PriceAlertScraper]:
    """
    Create a scraper instance based on the name.
    
    Args:
        scraper_name: Name of the scraper to create
        
    Returns:
        PriceAlertScraper instance or None if invalid name
    """
    if scraper_name == "power_to_choose":
        config = get_config("power_to_choose")
        return PowerToChooseScraper(
            zip_code=config["zip_code"],
            contract_min=config["contract_min_months"],
            contract_max=config["contract_max_months"]
        )
    elif scraper_name == "villa_del_arco":
        config = get_config("villa_del_arco")
        return VillaDelArcoScraper(
            check_in_date=config["check_in_date"],
            check_out_date=config["check_out_date"],
            adults=config["adults"],
            children=config["children"]
        )
    else:
        return None

def list_available_scrapers():
    """List all available scrapers"""
    print("Available scrapers:")
    print("  power_to_choose  - Monitor electricity plan prices from Power to Choose")
    print("  villa_del_arco   - Monitor hotel prices from Villa del Arco")
    print("\nUsage: python run_scraper.py <scraper_name>")
    print("Example: python run_scraper.py power_to_choose")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run price alert scrapers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scraper.py power_to_choose
  python run_scraper.py villa_del_arco
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
        return
    
    if not args.scraper_name:
        print("Error: No scraper name specified.")
        print("Use --list to see available scrapers.")
        sys.exit(1)
    
    # Create and run the specified scraper
    scraper = create_scraper(args.scraper_name)
    
    if scraper is None:
        print(f"Error: Unknown scraper '{args.scraper_name}'")
        print("Use --list to see available scrapers.")
        sys.exit(1)
    
    print(f"Running {args.scraper_name} scraper...")
    run_async_scraper(scraper)

if __name__ == "__main__":
    main()
