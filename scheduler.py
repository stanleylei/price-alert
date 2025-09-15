#!/usr/bin/env python3
"""
Scheduler module for running price alert scrapers at configurable intervals.
Supports running scrapers as a long-running service with periodic checks.
"""

import asyncio
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging
import threading

from price_alert_core import PriceAlertScraper, run_async_scraper
from run_scraper import create_scraper, SCRAPER_REGISTRY
from config import get_scheduler_config, get_service_config, validate_email_config
from health_check import HealthStatus, start_health_check_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scheduler.log')
    ]
)
logger = logging.getLogger(__name__)


class ScraperScheduler:
    """
    Manages scheduled execution of price alert scrapers.
    Supports running multiple scrapers at different intervals.
    """
    
    def __init__(self, scrapers_config: Dict[str, Dict]):
        """
        Initialize the scheduler with scraper configurations.
        
        Args:
            scrapers_config: Dictionary mapping scraper names to their configurations
                            including 'enabled' and 'interval_minutes' keys
        """
        self.scrapers_config = scrapers_config
        self.running = False
        self.tasks = []
        self.shutdown_event = threading.Event()
        self.last_run_times = {}
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.stop()
        
    def _calculate_next_run(self, scraper_name: str, interval_minutes: int) -> datetime:
        """Calculate the next run time for a scraper"""
        if scraper_name in self.last_run_times:
            return self.last_run_times[scraper_name] + timedelta(minutes=interval_minutes)
        return datetime.now()
    
    def _run_scraper_safe(self, scraper_name: str) -> bool:
        """
        Run a scraper with error handling.
        
        Returns:
            True if successful, False otherwise
        """
        health = HealthStatus()
        
        try:
            logger.info(f"Starting {scraper_name} scraper...")
            scraper = create_scraper(scraper_name)
            
            if scraper is None:
                logger.error(f"Failed to create scraper: {scraper_name}")
                health.update_scraper_status(scraper_name, "failure", "Failed to create scraper instance")
                return False
            
            # Run the scraper
            run_async_scraper(scraper)
            
            logger.info(f"Successfully completed {scraper_name} scraper")
            self.last_run_times[scraper_name] = datetime.now()
            health.update_scraper_status(scraper_name, "success")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error running {scraper_name} scraper: {error_msg}", exc_info=True)
            health.update_scraper_status(scraper_name, "failure", error_msg)
            return False
    
    def _format_interval(self, minutes: int) -> str:
        """Format interval in human-readable format"""
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        hours = minutes / 60
        if hours == int(hours):
            hours = int(hours)
            return f"{hours} hour{'s' if hours != 1 else ''}"
        return f"{hours:.1f} hours"
    
    async def _run_scraper_loop(self, scraper_name: str, config: Dict):
        """
        Run a single scraper in a loop with the specified interval.
        """
        interval_minutes = config.get('interval_minutes', 60)
        interval_seconds = interval_minutes * 60
        run_immediately = config.get('run_immediately', True)
        
        logger.info(f"Scheduling {scraper_name} to run every {self._format_interval(interval_minutes)}")
        
        # Run immediately if configured
        if run_immediately:
            logger.info(f"Running {scraper_name} immediately on startup")
            self._run_scraper_safe(scraper_name)
        
        while self.running:
            try:
                # Calculate time until next run
                next_run = self._calculate_next_run(scraper_name, interval_minutes)
                wait_seconds = max(0, (next_run - datetime.now()).total_seconds())
                
                if wait_seconds > 0:
                    logger.info(f"Next run of {scraper_name} in {self._format_interval(int(wait_seconds/60))}")
                    
                    # Wait with periodic checks for shutdown
                    start_wait = time.time()
                    while self.running and (time.time() - start_wait) < wait_seconds:
                        await asyncio.sleep(min(10, wait_seconds - (time.time() - start_wait)))
                
                if not self.running:
                    break
                
                # Run the scraper
                self._run_scraper_safe(scraper_name)
                
            except asyncio.CancelledError:
                logger.info(f"Scraper loop for {scraper_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scraper loop for {scraper_name}: {str(e)}", exc_info=True)
                # Wait before retrying
                await asyncio.sleep(60)
    
    async def _run_async(self):
        """Run all enabled scrapers asynchronously"""
        self.running = True
        
        # Create tasks for each enabled scraper
        for scraper_name, config in self.scrapers_config.items():
            if config.get('enabled', False):
                task = asyncio.create_task(self._run_scraper_loop(scraper_name, config))
                self.tasks.append(task)
                logger.info(f"Started scheduler task for {scraper_name}")
            else:
                logger.info(f"Scraper {scraper_name} is disabled")
        
        if not self.tasks:
            logger.warning("No scrapers are enabled. Exiting...")
            return
        
        # Wait for all tasks to complete (they won't unless stopped)
        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("All scraper tasks cancelled")
    
    def run(self):
        """Start the scheduler and run until stopped"""
        logger.info("=" * 60)
        logger.info("PRICE ALERT SCHEDULER STARTED")
        logger.info("=" * 60)
        
        # Validate email configuration
        if not validate_email_config():
            logger.warning("Email configuration is not properly set. Alerts may not work.")
        
        # Log enabled scrapers
        enabled_scrapers = [name for name, config in self.scrapers_config.items() 
                          if config.get('enabled', False)]
        
        if enabled_scrapers:
            logger.info(f"Enabled scrapers: {', '.join(enabled_scrapers)}")
        else:
            logger.error("No scrapers are enabled!")
            return
        
        try:
            # Run the async event loop
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            logger.info("Scheduler stopped")
    
    def stop(self):
        """Stop the scheduler gracefully"""
        logger.info("Stopping scheduler...")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        self.shutdown_event.set()


def run_service_mode():
    """
    Run scrapers in service mode with scheduled intervals.
    This is the main entry point for long-running service mode.
    """
    logger.info("Starting Price Alert Service in scheduled mode")
    
    # Get configurations
    scheduler_config = get_scheduler_config()
    service_config = get_service_config()
    
    # Start health check server if enabled
    health_server = None
    if service_config.get('health_check_enabled', True):
        health_port = service_config.get('health_check_port', 8080)
        health_server = start_health_check_server(health_port)
    
    # Log configuration
    logger.info("Scheduler Configuration:")
    for scraper_name, config in scheduler_config.items():
        if config.get('enabled', False):
            interval = config.get('interval_minutes', 60)
            logger.info(f"  {scraper_name}: Every {interval} minutes")
        else:
            logger.info(f"  {scraper_name}: Disabled")
    
    # Create and run scheduler
    scheduler = ScraperScheduler(scheduler_config)
    
    try:
        scheduler.run()
    except Exception as e:
        logger.error(f"Fatal error in scheduler: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        if health_server:
            health_server.stop()


def run_single_pass():
    """
    Run all enabled scrapers once and exit.
    This is useful for cron jobs or one-time runs.
    """
    logger.info("Running scrapers in single-pass mode")
    
    scheduler_config = get_scheduler_config()
    success_count = 0
    failure_count = 0
    
    for scraper_name, config in scheduler_config.items():
        if config.get('enabled', False):
            logger.info(f"Running {scraper_name}...")
            scraper = create_scraper(scraper_name)
            
            if scraper is None:
                logger.error(f"Failed to create scraper: {scraper_name}")
                failure_count += 1
                continue
            
            try:
                run_async_scraper(scraper)
                success_count += 1
                logger.info(f"Successfully ran {scraper_name}")
            except Exception as e:
                logger.error(f"Failed to run {scraper_name}: {str(e)}")
                failure_count += 1
    
    logger.info(f"Single pass complete. Success: {success_count}, Failures: {failure_count}")
    return failure_count == 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Price Alert Scheduler - Run scrapers at scheduled intervals"
    )
    
    parser.add_argument(
        "--mode",
        choices=["service", "single"],
        default="service",
        help="Run mode: 'service' for continuous scheduling, 'single' for one-time run"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode - run each scraper once immediately"
    )
    
    args = parser.parse_args()
    
    if args.test:
        logger.info("TEST MODE: Running each scraper once")
        run_single_pass()
    elif args.mode == "single":
        success = run_single_pass()
        sys.exit(0 if success else 1)
    else:
        run_service_mode()