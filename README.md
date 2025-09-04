# Price Alert Scrapers

A modular system for monitoring prices across different websites and sending email alerts when conditions are met.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Set Up Credentials
```bash
cp env.sample .env
# Edit .env with your Gmail credentials
```

### 3. Run a Scraper
```bash
# Run Power to Choose scraper
python run_scraper.py power_to_choose

# Run Villa del Arco scraper
python run_scraper.py villa_del_arco

# Run all scrapers
python run_scraper.py all
```

## 📋 What It Does

- **Power to Choose**: Monitors electricity plan prices in Texas
- **Villa del Arco**: Monitors hotel prices in Cabo San Lucas
- **Modular Design**: Easy to add new price monitoring sites
- **Email Alerts**: Automatic notifications when price conditions are met

## 🏗️ Architecture

- **`price_alert_core.py`** - Base classes and shared functionality
- **`config.py`** - Centralized configuration management
- **`run_scraper.py`** - Unified runner for all scrapers
- **`scraper_template.py`** - Template for creating new scrapers

## ⚙️ Configuration

### Required Environment Variables
- `SENDER_EMAIL` - Your Gmail address
- `SENDER_PASSWORD` - Your Gmail app password
- `RECIPIENT_EMAIL` - Email address to receive alerts

### Optional Variables
- `SCRAPER_NAME` - Which scraper to run (default: all)
- `PTC_ZIP_CODE` - ZIP code for electricity plans
- `VDA_CHECK_IN/OUT` - Hotel check-in/out dates

## 🐳 Docker Support

For Docker usage, see [DOCKER_README.md](DOCKER_README.md).

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup and configuration guide
- **[DOCKER_README.md](DOCKER_README.md)** - Docker usage and deployment
- **[scraper_template.py](scraper_template.py)** - How to create new scrapers

## 🔧 Troubleshooting

### Common Issues
1. **Gmail Authentication**: Use app passwords, not regular passwords
2. **Playwright**: Run `playwright install chromium`
3. **Environment Variables**: Check `.env` file exists and is configured

### Get Help
```bash
# List available scrapers
python run_scraper.py --list

# Show configuration
python run_scraper.py --config

# Get help
python run_scraper.py --help
```

## 📄 License

This project is licensed under the terms specified in the LICENSE file.
