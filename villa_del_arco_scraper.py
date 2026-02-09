"""
Villa del Arco hotel price alert scraper.
Refactored to use the modular price alert core.
"""

import re
from price_alert_core import PriceAlertScraper, run_async_scraper, EmailTemplate, logger

class VillaDelArcoScraper(PriceAlertScraper):
    """
    Scraper for Villa del Arco hotel prices.
    Monitors for All-Inclusive plans below $1,100.
    """
    
    def __init__(self, 
                 check_in_date: str = "2025-12-16",
                 check_out_date: str = "2025-12-19",
                 adults: int = 2,
                 children: int = 2,
                 price_threshold_usd: int = 1100,
                 base_url: str = None):
        super().__init__()
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.adults = adults
        self.children = children
        self.price_threshold_usd = price_threshold_usd
        self.base_url = base_url or "https://booking.villadelarco.com/bookcore/availability/villarco/{check_in}/{check_out}/{adults}/{children}/?lang=en&rrc=1&adults={adults}&ninos={children}"
    
    def get_scraping_url(self) -> str:
        return self.base_url.format(
            check_in=self.check_in_date,
            check_out=self.check_out_date,
            adults=self.adults,
            children=self.children
        )
    
    def get_email_subject(self) -> str:
        return "Price Alert: Villa del Arco All-Inclusive Plan Below $1,100"
    
    def check_alert_condition(self, df) -> bool:
        """Check if any All-Inclusive plan is below the price threshold"""
        condition = (df['Board Type'] == 'All Inclusive') & (df['Price (USD)'] < self.price_threshold_usd)
        return condition.any()
    
    def get_email_body(self, df) -> str:
        """Generate HTML email body for Villa del Arco results"""
        # Add the 'Alert' column with a checkmark for matching rows
        df_email = df.copy()
        condition = (df_email['Board Type'] == 'All Inclusive') & (df_email['Price (USD)'] < self.price_threshold_usd)
        df_email['Alert'] = condition.apply(lambda x: '✅' if x else '')
        
        # Reorder columns to make 'Alert' the first column
        df_email = df_email[['Alert', 'Room Name', 'Rate Name', 'Board Type', 'Price (USD)']]
        
        # Create configuration information section
        config_info = f"""
        <div class="config-item">
            <span class="config-label">Check-in Date:</span> {self.check_in_date}
        </div>
        <div class="config-item">
            <span class="config-label">Check-out Date:</span> {self.check_out_date}
        </div>
        <div class="config-item">
            <span class="config-label">Guests:</span> {self.adults} adults, {self.children} children
        </div>
        <div class="config-item">
            <span class="config-label">Price Threshold:</span> ${self.price_threshold_usd:,} or less
        </div>
        <div class="config-item">
            <span class="config-label">Target Plan:</span> All-Inclusive
        </div>
        """
        
        return EmailTemplate.create_html_body(
            title="Price Alert: Villa del Arco All-Inclusive Plan Below Threshold",
            message=f"An All-Inclusive plan below your ${self.price_threshold_usd:,} threshold was found. See the full list of available plans below. Matching plans are marked with '✅'.",
            table_html=df_email.to_html(escape=False, index=False),
            booking_url=self.get_scraping_url(),
            config_info=config_info
        )
    
    async def scrape_data(self, page) -> list:
        """Scrape hotel room and pricing data from Villa del Arco"""
        results_data = []
        
        try:
            logger.info("Waiting for dynamic content to load...")
            await page.locator('div[data-testid="fn-room-item-container"]').first.wait_for(timeout=30000)
            logger.info("Page loaded. Scraping room data...")

            room_items = page.locator('div[data-testid="fn-room-item-container"]')
            count = await room_items.count()
            logger.info(f"Found {count} room items.")
            
            if count == 0:
                logger.error("No rooms found. The page structure may have changed or no rooms are available for these dates.")
                return results_data
            
            for i in range(count):
                room_item = room_items.nth(i)
                room_name = await room_item.locator("h3").first.inner_text()
                logger.info(f"Scraping room: {room_name}")
                
                rate_sections = room_item.locator('div[data-testid="fn-accordion"]')
                
                for j in range(await rate_sections.count()):
                    rate_section = rate_sections.nth(j)
                    rate_name = await rate_section.locator("h3").first.inner_text()
                    boards = rate_section.locator('div[data-testid="fn-board"]')
                    board_count = await boards.count()
                    
                    if board_count == 0:
                        logger.warning(f"No board options found for rate '{rate_name}' in room '{room_name}'.")
                        continue

                    for k in range(board_count):
                        board = boards.nth(k)
                        # Use fn-board-total-price selector (the website structure changed from fn-loyalty-locked-price)
                        price_elem = board.locator('span[data-testid="fn-board-total-price"]')
                        if await price_elem.count() > 0:
                            board_type = await board.locator('span[class*="TooltipNameStyles"]').first.inner_text()
                            price_raw = await price_elem.first.inner_text()
                            
                            price_match = re.search(r'[\d,]+', price_raw)
                            price = int(price_match.group(0).replace(',', '')) if price_match else 0
                            
                            results_data.append({
                                "Room Name": room_name,
                                "Rate Name": rate_name,
                                "Board Type": board_type,
                                "Price (USD)": price
                            })
                            logger.info(f"  Found rate: {rate_name} - {board_type} - ${price}")
                        else:
                            # Log when we skip a board because it doesn't match criteria or selector
                            logger.debug(f"Skipping board option in {rate_name} (no total price found)")
                            
        except Exception as e:
            logger.error(f"Error during data scraping: {e}")
        
        if len(results_data) == 0:
            logger.error("Scraping completed but no rates were extracted. Check for HTML structure changes.")
            
        return results_data

if __name__ == "__main__":
    scraper = VillaDelArcoScraper()
    run_async_scraper(scraper)
