"""
Power to Choose electricity plan price alert scraper.
Refactored to use the modular price alert core.
"""

import re
from price_alert_core import PriceAlertScraper, run_async_scraper, EmailTemplate

class PowerToChooseScraper(PriceAlertScraper):
    """
    Scraper for Power to Choose electricity plans.
    Monitors for plans with prices <= 12.4¢/kWh.
    """
    
    def __init__(self, zip_code: str = "76092", contract_min: str = "12", contract_max: str = "60", price_threshold_cents: float = 12.4, max_results: int = 5, base_url: str = None):
        super().__init__()
        self.zip_code = zip_code
        self.contract_min = contract_min
        self.contract_max = contract_max
        self.price_threshold_cents = price_threshold_cents
        self.max_results = max_results
        self.base_url = base_url or "https://www.powertochoose.org/en-us"
    
    def get_scraping_url(self) -> str:
        return self.base_url
    
    def get_email_subject(self) -> str:
        return "Power to Choose - Electricity Plan Alert"
    
    def check_alert_condition(self, df) -> bool:
        """Check if any plan has price <= threshold"""
        return any(df["Price 1,000 kWh"] <= self.price_threshold_cents)
    
    def get_email_body(self, df) -> str:
        """Generate HTML email body for Power to Choose results"""
        # Format links for the email HTML
        df_email = df.copy()
        df_email['Fact Sheet'] = df_email['Fact Sheet'].apply(
            lambda url: f'<a href="{url}" target="_blank">Link</a>'
        )
        df_email['Ordering Info'] = df_email['Ordering Info'].apply(
            lambda url: f'<a href="{url}" target="_blank">Link</a>'
        )

        # Create configuration information section
        config_info = f"""
        <div class="config-item">
            <span class="config-label">ZIP Code:</span> {self.zip_code}
        </div>
        <div class="config-item">
            <span class="config-label">Contract Length:</span> {self.contract_min} - {self.contract_max} months
        </div>
        <div class="config-item">
            <span class="config-label">Price Threshold:</span> {self.price_threshold_cents}¢/kWh or less
        </div>
        <div class="config-item">
            <span class="config-label">Max Results:</span> {self.max_results} plans
        </div>
        """

        return EmailTemplate.create_html_body(
            title="Power to Choose - Electricity Plan Alert",
            message=f"A plan meeting your criteria (<= {self.price_threshold_cents}¢/kWh) was found. Here are the top {self.max_results} results:",
            table_html=df_email.to_html(escape=False, index=False),
            config_info=config_info
        )
    
    async def scrape_data(self, page) -> list:
        """Scrape electricity plan data from Power to Choose"""
        results_data = []
        
        try:
            # Fill in zip code and search
            await page.locator("#homezipcode").fill(self.zip_code)
            await page.locator("#view_all_results").click()
            await page.wait_for_load_state('networkidle')
            
            # Set contract length filters
            await page.locator("#plan_mo_from").fill(self.contract_min)
            await page.locator("#plan_mo_to").fill(self.contract_max)
            await page.get_by_role("link", name="Refresh Results").first.click()
            await page.locator("#loading-image-grid").wait_for(state="hidden", timeout=15000)
            print("Filtered results are now displayed.")
            
            print("\nScraping and cleaning the top 5 results...")
            rows = page.locator("#dataTable tr.row.active")
            
            for i in range(min(5, await rows.count())):
                row = rows.nth(i)
                plan_details_raw = await row.locator("td.td-plan").inner_text()
                price_kwh_raw = await row.locator("td.td-price").inner_text()
                pricing_details_raw = await row.locator("td.td-details").inner_text()
                
                # Extract price information using regex
                price_1000 = re.search(r"1,000 kWh\s*([\d.]+)", price_kwh_raw)
                price_500 = re.search(r"500 kWh\s*([\d.]+\¢)", price_kwh_raw)
                price_2000 = re.search(r"2000 kWh\s*([\d.]+\¢)", price_kwh_raw)
                plan_length = re.search(r"(\d+\s*Months)", plan_details_raw)
                cancellation_fee = re.search(r"Cancellation Fee: (.*)", pricing_details_raw)
                
                # Get URLs
                fact_sheet_url = await row.get_by_role("link", name="Fact Sheet").get_attribute("href")
                ordering_info_link = await row.get_by_role("link", name="Additional Information").get_attribute("href")
                
                results_data.append({
                    "Plan Length": plan_length.group(1) if plan_length else "N/A",
                    "Price 1,000 kWh": float(price_1000.group(1)) if price_1000 else 0.0,
                    "Price 500 kWh": price_500.group(1) if price_500 else "N/A",
                    "Price 2,000 kWh": price_2000.group(1) if price_2000 else "N/A",
                    "Cancellation Fee": cancellation_fee.group(1).strip() if cancellation_fee else "N/A",
                    "Fact Sheet": fact_sheet_url,
                    "Ordering Info": ordering_info_link
                })
                
        except Exception as e:
            print(f"Error during data scraping: {e}")
            
        return results_data

if __name__ == "__main__":
    scraper = PowerToChooseScraper()
    run_async_scraper(scraper)
