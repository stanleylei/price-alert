"""
Alaska Airlines award ticket price alert scraper.
Monitors for 7.5k points availability on DFW → SNA and DFW → ONT routes.
"""

import re
from price_alert_core import PriceAlertScraper, run_async_scraper, EmailTemplate

class AlaskaAwardTicketScraper(PriceAlertScraper):
    """
    Scraper for Alaska Airlines award ticket availability.
    Monitors for 7.5k points on DFW → SNA and DFW → ONT routes.
    """
    
    def __init__(self, 
                 departure_station: str = "DFW",
                 target_arrival_stations: list = None,
                 target_points: int = 7500,
                 search_date: str = "2025-11-14",
                 base_search_url: str = None):
        super().__init__()
        self.departure_station = departure_station
        self.target_arrival_stations = target_arrival_stations or ["SNA", "ONT"]
        self.target_points = target_points
        self.search_date = search_date
        self.base_search_url = base_search_url or "https://www.alaskaair.com/search/results?A=3&C=2&L=0&O={departure}&D={arrival}&OD={date}&RT=false&ShoppingMethod=onlineaward"
    
    def get_scraping_url(self) -> str:
        """Return the first search URL (for backward compatibility)"""
        if self.target_arrival_stations:
            return self._build_search_url(self.target_arrival_stations[0])
        return self.base_search_url.format(
            departure=self.departure_station,
            arrival="LA5",  # fallback
            date=self.search_date
        )
    
    def _build_search_url(self, arrival_station: str) -> str:
        """Build search URL for a specific arrival station"""
        return self.base_search_url.format(
            departure=self.departure_station,
            arrival=arrival_station,
            date=self.search_date
        )
    
    def get_email_subject(self) -> str:
        return "Alaska Airlines Alert: 7.5k Points Available for DFW → SNA/ONT"
    
    def check_alert_condition(self, df) -> bool:
        """Check if any route has 7.5k points for target arrival stations"""
        if df.empty:
            return False
        
        condition = (
            (df['Arrival Station'].isin(self.target_arrival_stations)) & 
            (df['Points'] <= self.target_points)
        )
        return condition.any()
    
    def get_email_body(self, df) -> str:
        """Generate HTML email body for Alaska Airlines results"""
        df_email = df.copy()
        condition = (
            (df_email['Arrival Station'].isin(self.target_arrival_stations)) & 
            (df_email['Points'] <= self.target_points)
        )
        df_email['Alert'] = condition.apply(lambda x: '✅' if x else '')
        
        columns = ['Alert', 'Departure Station', 'Arrival Station', 'Departure Time', 
                  'Arrival Time', 'Points', 'Price (USD)', 'Flight Number']
        df_email = df_email[columns]
        
        return EmailTemplate.create_html_body(
            title="Alaska Airlines Award Ticket Alert",
            message="Found flights with 7.5k points or less for DFW → SNA/ONT routes! Currently monitoring for SNA and ONT routes. Matching routes are marked with '✅'.",
            table_html=df_email.to_html(escape=False, index=False, classes='alert-row'),
            booking_url=self.get_scraping_url()
        )
    
    async def scrape_data(self, page) -> list:
        """Scrape flight data from Alaska Airlines award search results for all target airports"""
        all_results = []
        
        for arrival_station in self.target_arrival_stations:
            print(f"\n--- Searching for {self.departure_station} → {arrival_station} ---")
            
            try:
                # Navigate to the specific search URL
                search_url = self._build_search_url(arrival_station)
                print(f"Navigating to: {search_url}")
                await page.goto(search_url, timeout=60000)
                
                # Wait for page to load
                print("Waiting for page to load...")
                await page.wait_for_load_state('networkidle', timeout=30000)
                print("Page loaded. Looking for flight data...")
                
                # Wait for matrix rows to appear
                try:
                    await page.locator('[data-testid="matrix-row"]').first.wait_for(timeout=30000)
                    print("Found matrix rows, extracting data...")
                except Exception as e:
                    print(f"Matrix rows not found for {arrival_station}: {e}")
                    continue
                
                # Extract data from all matrix rows
                matrix_rows = await page.locator('[data-testid="matrix-row"]').all()
                print(f"Found {len(matrix_rows)} matrix rows for {arrival_station}")
                
                station_results = []
                for row in matrix_rows:
                    try:
                        row_data = await self._extract_row_data(row)
                        if row_data:
                            # Ensure the arrival station matches what we're searching for
                            if row_data.get("Arrival Station") == arrival_station:
                                station_results.append(row_data)
                    except Exception as e:
                        print(f"Error extracting row data: {e}")
                        continue
                
                print(f"Found {len(station_results)} flights for {arrival_station}")
                all_results.extend(station_results)
                
            except Exception as e:
                print(f"Error searching for {arrival_station}: {e}")
                continue
        
        print(f"\nTotal flights found across all searches: {len(all_results)}")
        return all_results
    
    async def _extract_row_data(self, row) -> dict:
        """Extract data from a single row element"""
        try:
            # Extract basic flight info
            departure_station = await self._extract_text(row, [
                '[data-testid*="departure"]', '.departure', '[class*="departure"]', 'td:first-child', '.origin'
            ])
            
            arrival_station = await self._extract_text(row, [
                '[data-testid*="arrival"]', '.arrival', '[class*="arrival"]', 'td:nth-child(2)', '.destination'
            ])
            
            # Extract price and points from the same text element
            price_points_text = await self._extract_text(row, [
                '[class*="price"]', '[class*="points"]', '[class*="award"]', 'td:nth-child(3)', 'td:nth-child(4)'
            ])
            
            price = self._parse_price(price_points_text)
            points = self._parse_points(price_points_text)
            
            # Extract flight number
            flight_number_text = await self._extract_text(row, [
                '[data-testid*="flight"]', '.flight-number', '[class*="flight"]', 'td:nth-child(1)'
            ])
            flight_number = self._parse_flight_number(flight_number_text)
            
            # Extract times
            departure_time = await self._extract_text(row, [
                '.departureTime .yield', '.departureTime span', '[class*="departureTime"] .yield', '[class*="departureTime"] span'
            ])
            
            arrival_time = await self._extract_text(row, [
                '.arrivalTime .yield', '.arrivalTime span', '[class*="arrivalTime"] .yield', '[class*="arrivalTime"] span'
            ])
            
            # Return data if we found meaningful information
            if departure_station or arrival_station or points > 0:
                return {
                    "Departure Station": departure_station or "N/A",
                    "Arrival Station": arrival_station or "N/A",
                    "Departure Time": departure_time or "N/A",
                    "Arrival Time": arrival_time or "N/A",
                    "Points": points,
                    "Price (USD)": price,
                    "Flight Number": flight_number
                }
            
        except Exception as e:
            print(f"Error extracting row data: {e}")
            
        return {}
    
    async def _extract_text(self, row, selectors) -> str:
        """Try multiple selectors to extract text from a row"""
        for selector in selectors:
            try:
                elements = await row.locator(selector).all()
                if elements:
                    text = await elements[0].inner_text()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return ""
    
    def _parse_price(self, text: str) -> float:
        """Parse price from text like '+ $19' or '$19'"""
        if not text:
            return 0.0
        
        # Look for dollar amounts
        dollar_match = re.search(r'\+\s*\$(\d+(?:\.\d+)?)|\$(\d+(?:\.\d+)?)', text)
        if dollar_match:
            return float(dollar_match.group(1) or dollar_match.group(2))
        
        # Fallback to any number
        fallback_match = re.search(r'(\d+(?:\.\d+)?)', text)
        return float(fallback_match.group(1)) if fallback_match else 0.0
    
    def _parse_points(self, text: str) -> int:
        """Parse points from text like '7.5k' or '7500'"""
        if not text:
            return 0
        
        # Look for 'X.Xk' or 'Xk' pattern
        k_match = re.search(r'(\d+(?:\.\d+)?)[kK]', text)
        if k_match:
            return int(float(k_match.group(1)) * 1000)
        
        # Look for comma-separated numbers like '7,500'
        comma_match = re.search(r'(\d{1,2}(?:,\d{3})?)', text)
        if comma_match:
            return int(comma_match.group(1).replace(',', ''))
        
        # Fallback to any number
        fallback_match = re.search(r'(\d+)', text)
        return int(fallback_match.group(1)) if fallback_match else 0
    
    def _parse_flight_number(self, text: str) -> str:
        """Parse flight number from text like 'AA 1639'"""
        if not text:
            return "N/A"
        
        # Look for airline code + number pattern
        flight_match = re.search(r'([A-Z]{2})\s*(\d+)', text)
        if flight_match:
            return f"{flight_match.group(1)} {flight_match.group(2)}"
        
        # Fallback to first part of text
        return text.split('\n')[0].strip() or "N/A"

if __name__ == "__main__":
    scraper = AlaskaAwardTicketScraper()
    run_async_scraper(scraper)