"""
Alaska Airlines award ticket price alert scraper.
Monitors for 7.5k points availability on DFW → SNA and DFW → ONT routes.
"""

import re
from price_alert_core import PriceAlertScraper, run_async_scraper, EmailTemplate, logger

class AlaskaAwardTicketScraper(PriceAlertScraper):
    """
    Scraper for Alaska Airlines award ticket availability.
    Monitors for 7.5k points on DFW → SNA and DFW → ONT routes.
    """
    
    def __init__(self, 
                 departure_stations: list = None,
                 arrival_stations: list = None,
                 adults: int = 3,
                 children: int = 2,
                 target_points: int = 7500,
                 search_date: str = "2025-11-14",
                 base_search_url: str = None):
        super().__init__()
        self.departure_stations = departure_stations or ["DFW"]
        self.arrival_stations = arrival_stations or ["SNA", "ONT"]
        self.adults = adults
        self.children = children
        self.target_points = target_points
        self.search_date = search_date
        self.base_search_url = base_search_url or "https://www.alaskaair.com/search/results?A={adults}&C={children}&L=0&O={departure}&D={arrival}&OD={date}&RT=false&ShoppingMethod=onlineaward"
    
    def get_scraping_url(self) -> str:
        """Return the first search URL (for backward compatibility)"""
        if self.departure_stations and self.arrival_stations:
            return self._build_search_url(self.departure_stations[0], self.arrival_stations[0])
        return self.base_search_url.format(
            adults=self.adults,
            children=self.children,
            departure="DFW",  # fallback
            arrival="SNA",    # fallback
            date=self.search_date
        )
    
    def _build_search_url(self, departure_station: str, arrival_station: str) -> str:
        """Build search URL for a specific departure and arrival station"""
        return self.base_search_url.format(
            adults=self.adults,
            children=self.children,
            departure=departure_station,
            arrival=arrival_station,
            date=self.search_date
        )
    
    def get_email_subject(self) -> str:
        departure_str = ",".join(self.departure_stations)
        arrival_str = ",".join(self.arrival_stations)
        return f"Alaska Airlines Alert: {self.target_points} Points Available for {departure_str} → {arrival_str}"
    
    def check_alert_condition(self, df) -> bool:
        """Check if any route has target points for target departure/arrival station combinations"""
        if df.empty:
            return False
        
        condition = (
            (df['Departure Station'].isin(self.departure_stations)) &
            (df['Arrival Station'].isin(self.arrival_stations)) & 
            (df['Points'] <= self.target_points)
        )
        return condition.any()
    
    def get_email_body(self, df) -> str:
        """Generate HTML email body for Alaska Airlines results"""
        df_email = df.copy()
        condition = (
            (df_email['Departure Station'].isin(self.departure_stations)) &
            (df_email['Arrival Station'].isin(self.arrival_stations)) & 
            (df_email['Points'] <= self.target_points)
        )
        df_email['Alert'] = condition.apply(lambda x: '✅' if x else '')
        
        columns = ['Alert', 'Departure Station', 'Arrival Station', 'Departure Time', 
                  'Arrival Time', 'Points', 'Price (USD)', 'Flight Number']
        df_email = df_email[columns]
        
        departure_str = ",".join(self.departure_stations)
        arrival_str = ",".join(self.arrival_stations)
        
        # Create configuration information section
        config_info = f"""
        <div class="config-item">
            <span class="config-label">Search Date:</span> {self.search_date}
        </div>
        <div class="config-item">
            <span class="config-label">Departure Stations:</span> {departure_str}
        </div>
        <div class="config-item">
            <span class="config-label">Arrival Stations:</span> {arrival_str}
        </div>
        <div class="config-item">
            <span class="config-label">Passengers:</span> {self.adults} adults, {self.children} children
        </div>
        <div class="config-item">
            <span class="config-label">Target Points:</span> {self.target_points:,} points or less
        </div>
        """
        
        return EmailTemplate.create_html_body(
            title="Alaska Airlines Award Ticket Alert",
            message=f"Found flights with {self.target_points:,} points or less for {departure_str} → {arrival_str} routes! Matching routes are marked with '✅'.",
            table_html=df_email.to_html(escape=False, index=False, classes='alert-row'),
            booking_url=self.get_scraping_url(),
            config_info=config_info
        )
    
    async def scrape_data(self, page) -> list:
        """Scrape flight data from Alaska Airlines award search results"""
        all_results = []
        
        total_combinations = len(self.departure_stations) * len(self.arrival_stations)
        current_combination = 0
        
        for departure_station in self.departure_stations:
            for arrival_station in self.arrival_stations:
                current_combination += 1
                logger.info(f"\n--- Searching for {departure_station} → {arrival_station} ({current_combination}/{total_combinations}) ---")
                
                try:
                    search_url = self._build_search_url(departure_station, arrival_station)
                    logger.info(f"Navigating to: {search_url}")
                    await page.goto(search_url, timeout=60000)
                    
                    # Wait for page to load completely
                    logger.info("Waiting for page to load...")
                    await page.wait_for_load_state('domcontentloaded')
                    await page.wait_for_load_state('networkidle', timeout=30000)
                    await page.wait_for_timeout(3000)  # Extra wait for JS rendering
                    
                    logger.info("Looking for flight options...")
                    
                    # Try multiple selector strategies
                    matrix_rows = []
                    
                    # Strategy 1: Original data-testid
                    try:
                        els = await page.locator('[data-testid="matrix-row"]').all()
                        if els and len(els) > 0:
                            matrix_rows = els
                            logger.info(f"✓ Found {len(matrix_rows)} rows via [data-testid='matrix-row']")
                    except Exception:
                        pass
                    
                    # Strategy 2: Auro buttons or generic interactive elements
                    if not matrix_rows:
                        try:
                            els = await page.locator('auro-button[type="button"]').all()
                            if els and len(els) > 3:  # Filter out nav buttons
                                matrix_rows = els
                                logger.info(f"✓ Found {len(matrix_rows)} buttons via auro-button")
                        except Exception:
                            pass
                    
                    # Strategy 3: Divs with role button
                    if not matrix_rows:
                        try:
                            els = await page.locator('div[role="button"], button[role="option"]').all()
                            if els and len(els) > 0:
                                matrix_rows = els
                                logger.info(f"✓ Found {len(matrix_rows)} interactive elements")
                        except Exception:
                            pass
                    
                    # Strategy 4: Search for any element with flight-related text
                    if not matrix_rows:
                        body_text = await page.locator('body').text_content()
                        if '0 results' in body_text.lower() or 'no flights' in body_text.lower():
                            logger.info(f"⚠ No flights available for {departure_station} → {arrival_station} (0 results page)")
                            continue
                        else:
                            # Fallback: try common result containers
                            els = await page.locator('button, [data-testid*="result"], [class*="result"]').all()
                            if els and len(els) > 5:
                                matrix_rows = els
                                logger.info(f"✓ Found {len(matrix_rows)} potential result elements (fallback)")
                    
                    if not matrix_rows:
                        logger.warning(f"⚠ No flight elements found for {departure_station} → {arrival_station}")
                        continue
                    
                    # Extract data from all found elements
                    route_results = []
                    for row in matrix_rows:
                        try:
                            row_text = await row.text_content()
                            if not row_text or len(row_text.strip()) < 5:
                                continue
                            
                            # Parse all data from row text
                            points = self._parse_points(row_text)
                            price = self._parse_price(row_text)
                            departure_time = self._parse_departure_time(row_text)
                            arrival_time = self._parse_arrival_time(row_text)
                            flight_number = self._parse_flight_number(row_text)
                            
                            # Only include if we found meaningful points or price
                            if points > 0 or price > 0:
                                row_data = {
                                    "Departure Station": departure_station,
                                    "Arrival Station": arrival_station,
                                    "Departure Time": departure_time,
                                    "Arrival Time": arrival_time,
                                    "Points": points,
                                    "Price (USD)": price,
                                    "Flight Number": flight_number
                                }
                                route_results.append(row_data)
                                logger.info(f"  Found flight: {flight_number} at {departure_time} → {arrival_time} ({points} pts)")
                        except Exception as e:
                            continue
                    
                    logger.info(f"✓ Found {len(route_results)} valid flights for {departure_station} → {arrival_station}")
                    all_results.extend(route_results)
                    
                except Exception as e:
                    logger.error(f"✗ Error searching for {departure_station} → {arrival_station}: {str(e)[:80]}")
                    continue
    
        logger.info(f"\n{'='*60}")
        logger.info(f"TOTAL FLIGHTS FOUND: {len(all_results)}")
        logger.info(f"{'='*60}")
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
            logger.error(f"Error extracting row data: {e}")
            
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
    
    def _parse_departure_time(self, text: str) -> str:
        """Parse departure time from text like '6:30 AM' or '6:30am'"""
        if not text:
            return "N/A"
        
        # Look for time pattern HH:MM (am|pm|AM|PM)
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*([AaPp][Mm])', text)
        if time_match:
            return f"{time_match.group(1)}:{time_match.group(2)} {time_match.group(3).upper()}"
        
        # Fallback: just look for first time-like pattern
        time_match = re.search(r'(\d{1,2}):(\d{2})', text)
        if time_match:
            return f"{time_match.group(1)}:{time_match.group(2)}"
        
        return "N/A"
    
    def _parse_arrival_time(self, text: str) -> str:
        """Parse arrival time - typically the second time in the text"""
        if not text:
            return "N/A"
        
        # Find all time patterns in the text
        times = re.findall(r'(\d{1,2}):(\d{2})\s*([AaPp][Mm])?', text)
        
        if len(times) > 1:
            # Return the second time found (arrival)
            match = times[1]
            if match[2]:  # Has AM/PM
                return f"{match[0]}:{match[1]} {match[2].upper()}"
            else:
                return f"{match[0]}:{match[1]}"
        elif len(times) == 1:
            # If only one time, assume it's departure only
            return "N/A"
        
        return "N/A"
    
    def _parse_flight_number(self, text: str) -> str:
        """Parse flight number from text like 'AS 1639' or 'AS1639'"""
        if not text:
            return "N/A"
        
        # Look for airline code + number pattern (AS, AA, etc.)
        flight_match = re.search(r'\b([A-Z]{2})\s*(\d{3,4})\b', text)
        if flight_match:
            return f"{flight_match.group(1)} {flight_match.group(2)}"
        
        return "N/A"

if __name__ == "__main__":
    scraper = AlaskaAwardTicketScraper()
    run_async_scraper(scraper)