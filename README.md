# Price Alert Scrapers

A modular system for monitoring prices across different websites and sending email alerts when conditions are met.

## Overview

This project has been refactored from two separate price alert scripts into a modular, extensible system. The core functionality is now shared across all scrapers, making it easy to add new price monitoring capabilities.

## Architecture

### Core Components

- **`price_alert_core.py`** - Base classes and shared functionality
- **`config.py`** - Centralized configuration management
- **`run_scraper.py`** - Unified runner for all scrapers

### Scrapers

- **`power_to_choose_scraper.py`** - Monitors electricity plan prices
- **`villa_del_arco_scraper.py`** - Monitors hotel prices
- **`scraper_template.py`** - Template for creating new scrapers

## Features

- **Modular Design**: Common functionality is shared across all scrapers
- **Easy Extension**: Add new scrapers by implementing the `PriceAlertScraper` interface
- **Centralized Configuration**: All settings managed in one place with environment variable support
- **Unified Interface**: Run any scraper using a single command
- **Email Alerts**: Automatic email notifications when price conditions are met
- **Web Scraping**: Uses Playwright for reliable web automation

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

3. Set up environment variables (required):
   ```bash
   # Copy the sample environment file
   cp env.sample .env
   
   # Edit .env with your actual credentials
   nano .env
   ```

   **Required variables:**
   - `SENDER_EMAIL` - Your Gmail address
   - `SENDER_PASSWORD` - Your Gmail app password
   - `RECIPIENT_EMAIL` - Email address to receive alerts

   **Optional variables:**
   - `SCRAPER_NAME` - Which scraper to run (default: all)
   - `PTC_ZIP_CODE` - ZIP code for electricity plans
   - `VDA_CHECK_IN/OUT` - Hotel check-in/out dates

## Usage

### Running Individual Scrapers

```bash
# Run Power to Choose scraper
python run_scraper.py power_to_choose

# Run Villa del Arco scraper
python run_scraper.py villa_del_arco
```

### Available Commands

```bash
# List all available scrapers
python run_scraper.py --list

# Show current configuration
python run_scraper.py --config

# Get help
python run_scraper.py --help
```

### Running Original Scripts

The original scripts are still available and functional:
```bash
python price-alert-power-to-choose.py
python price-alert-villa-del-arco.py
```

## Configuration

### Environment Variables

All configuration can be overridden using environment variables:

#### Email Configuration
- `SENDER_EMAIL` - Gmail address for sending emails
- `SENDER_PASSWORD` - Gmail app password
- `RECIPIENT_EMAIL` - Email address to receive alerts

#### Power to Choose Configuration
- `PTC_ZIP_CODE` - ZIP code for electricity plan search
- `PTC_CONTRACT_MIN` - Minimum contract length in months
- `PTC_CONTRACT_MAX` - Maximum contract length in months
- `PTC_PRICE_THRESHOLD` - Price threshold in cents per kWh
- `PTC_MAX_RESULTS` - Maximum number of results to process

#### Villa del Arco Configuration
- `VDA_CHECK_IN` - Check-in date (YYYY-MM-DD)
- `VDA_CHECK_OUT` - Check-out date (YYYY-MM-DD)
- `VDA_ADULTS` - Number of adults
- `VDA_CHILDREN` - Number of children
- `VDA_PRICE_THRESHOLD` - Price threshold in USD

#### Scraping Configuration
- `SCRAPING_TIMEOUT` - Page load timeout in milliseconds
- `SCRAPING_WAIT_TIMEOUT` - Element wait timeout in milliseconds
- `BROWSER_HEADLESS` - Run browser in headless mode (true/false)
- `BROWSER_NO_SANDBOX` - Disable browser sandbox (true/false)

## Adding New Scrapers

### 1. Create Scraper Class

Copy `scraper_template.py` and implement the required methods:

```python
class NewWebsiteScraper(PriceAlertScraper):
    def __init__(self, **kwargs):
        super().__init__()
        # Store configuration parameters
        
    def get_scraping_url(self) -> str:
        return "https://example.com"
        
    def get_email_subject(self) -> str:
        return "Price Alert: [Product] Below [Threshold]"
        
    def check_alert_condition(self, df) -> bool:
        # Implement your alert logic
        return False
        
    def get_email_body(self, df) -> str:
        # Generate HTML email content
        return "<html>...</html>"
        
    async def scrape_data(self, page) -> list:
        # Implement web scraping logic
        return []
```

### 2. Add Configuration

Update `config.py` to include your scraper's configuration:

```python
NEW_WEBSITE_CONFIG = {
    "param1": os.getenv("NEW_PARAM1", "default_value"),
    "param2": os.getenv("NEW_PARAM2", "default_value")
}

def get_config(scraper_name: str) -> Dict[str, Any]:
    configs = {
        "power_to_choose": POWER_TO_CHOOSE_CONFIG,
        "villa_del_arco": VILLA_DEL_ARCO_CONFIG,
        "new_website": NEW_WEBSITE_CONFIG  # Add this line
    }
    return configs.get(scraper_name, {})
```

### 3. Integrate with Runner

Update `run_scraper.py` to include your scraper:

```python
def create_scraper(scraper_name: str) -> Optional[PriceAlertScraper]:
    # ... existing code ...
    elif scraper_name == "new_website":
        config = get_config("new_website")
        return NewWebsiteScraper(**config)
    # ... existing code ...

def list_available_scrapers():
    print("Available scrapers:")
    # ... existing code ...
    print("  new_website      - Monitor prices from New Website")
```

## Docker Support

The existing Dockerfile and start.sh are compatible with the new modular structure. You can run any scraper using:

```bash
# Build and run with specific scraper
docker build -t price-alert .
docker run -e SCRAPER_NAME=power_to_choose price-alert
```

### Docker Compose

```bash
# Run all scrapers
docker-compose up all-scrapers

# Run specific scraper
docker-compose up power-to-choose
```

## Benefits of the New Structure

1. **Code Reuse**: Common functionality is shared across all scrapers
2. **Easy Maintenance**: Changes to core functionality benefit all scrapers
3. **Simple Extension**: Adding new scrapers requires minimal code
4. **Consistent Interface**: All scrapers follow the same pattern
5. **Better Testing**: Core functionality can be tested independently
6. **Configuration Management**: Centralized settings with environment variable support

## Troubleshooting

### Common Issues

1. **Playwright Installation**: Ensure you've run `playwright install chromium`
2. **Gmail Authentication**: Use app passwords, not regular passwords
3. **Environment Variables**: Check that environment variables are properly set
4. **Browser Issues**: Some environments may require `--no-sandbox` flag

### Debug Mode

To run scrapers with more verbose output, you can modify the browser launch options in `price_alert_core.py`:

```python
browser = await p.chromium.launch(
    headless=False,  # Set to False to see browser
    args=["--no-sandbox"]
)
```

## Contributing

When adding new scrapers:

1. Follow the existing naming conventions
2. Implement all required abstract methods
3. Add appropriate error handling
4. Include configuration options
5. Update documentation
6. Test thoroughly before submitting

## License

This project is licensed under the terms specified in the LICENSE file.
