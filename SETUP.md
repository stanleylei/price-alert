# Setup Guide for Price Alert Scrapers

This guide will help you set up the price alert scrapers securely without exposing your credentials.

## 🔐 Security First

**IMPORTANT**: Never commit your actual email credentials to this repository. The repository is public and your credentials would be exposed to everyone.

## 📋 Prerequisites

- **Gmail Account** with 2-Factor Authentication enabled
- **App Password** generated for Gmail (not your regular password)
- **Python 3.8+** installed on your system
- **Docker** (optional, for containerized execution)

## 🚀 Quick Setup

### 1. Clone and Install
```bash
git clone <repository-url>
cd price-alert
pip install -r requirements.txt
playwright install chromium
```

### 2. Set Up Email Credentials

#### Option A: .env File (Recommended)
```bash
cp env.sample .env
# Edit .env with your actual credentials
```

**Required in .env:**
```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password
RECIPIENT_EMAIL=recipient@example.com
SCRAPER_NAME=all
```

#### Option B: Environment Variables
```bash
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-gmail-app-password"
export RECIPIENT_EMAIL="recipient@example.com"
```

### 3. Test Setup
```bash
# Check configuration
python run_scraper.py --config

# Test a specific scraper
python run_scraper.py power_to_choose
```

## 🔑 Gmail App Password Setup

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click on "2-Step Verification" and follow setup

### Step 2: Generate App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click "App passwords" (under 2-Step Verification)
3. Select "Mail" and "Other (Custom name)"
4. Enter name like "Price Alert Scraper"
5. **Copy the 16-character password** (this is your `SENDER_PASSWORD`)

## ⚙️ Configuration Options

### Power to Choose (Electricity)
```bash
PTC_ZIP_CODE=76092                    # Your ZIP code
PTC_CONTRACT_MIN=12                   # Min contract months
PTC_CONTRACT_MAX=60                   # Max contract months
PTC_PRICE_THRESHOLD=12.4             # Price threshold (cents/kWh)
PTC_MAX_RESULTS=5                     # Max results to process
```

### Villa del Arco (Hotel)
```bash
VDA_CHECK_IN=2025-12-16              # Check-in date (YYYY-MM-DD)
VDA_CHECK_OUT=2025-12-19             # Check-out date (YYYY-MM-DD)
VDA_ADULTS=2                          # Number of adults
VDA_CHILDREN=2                        # Number of children
VDA_PRICE_THRESHOLD=1100             # Price threshold (USD)
```

### Alaska Airlines (Award Tickets)
```bash
ALASKA_DEPARTURE_STATIONS=DFW         # Departure airport codes (comma-separated)
ALASKA_ARRIVAL_STATIONS=SNA,ONT       # Arrival airports (comma-separated)
ALASKA_ADULTS=3                       # Number of adults
ALASKA_CHILDREN=2                     # Number of children
ALASKA_TARGET_POINTS=7500             # Target points threshold
ALASKA_SEARCH_DATE=2025-11-14         # Search date (YYYY-MM-DD)
```

### Web Scraping (Advanced)
```bash
SCRAPING_TIMEOUT=60000                # Page load timeout (ms)
SCRAPING_WAIT_TIMEOUT=30000           # Element wait timeout (ms)
BROWSER_HEADLESS=true                 # Run browser in background
BROWSER_NO_SANDBOX=true               # Docker compatibility
```

## 🔄 Automation

### Cron Jobs
```bash
# Run every hour
0 * * * * cd /path/to/price-alert && python run_scraper.py power_to_choose

# Run daily at 9 AM
0 9 * * * cd /path/to/price-alert && python run_scraper.py villa_del_arco

# Run Alaska Airlines every 2 hours
0 */2 * * * cd /path/to/price-alert && python run_scraper.py alaska_award_ticket

# Run all scrapers daily at 6 AM
0 6 * * * cd /path/to/price-alert && python run_scraper.py all
```

### Systemd Service
Create `/etc/systemd/system/price-alert.service`:
```ini
[Unit]
Description=Price Alert Scraper
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/price-alert
Environment=SENDER_EMAIL=your-email@gmail.com
Environment=SENDER_PASSWORD=your-gmail-app-password
Environment=RECIPIENT_EMAIL=recipient@example.com
ExecStart=/usr/bin/python3 run_scraper.py all

[Install]
WantedBy=multi-user.target
```

## 🔧 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Authentication failed" | Use Gmail App Password, not regular password |
| "Module not found" | Run `pip install -r requirements.txt` |
| Browser/Playwright issues | Run `playwright install --with-deps chromium` |
| Environment variables not found | Check `.env` file exists and is configured |

### Debug Commands
```bash
# Check environment variables
env | grep -E "(SENDER|RECIPIENT)"

# Run with verbose output
python run_scraper.py power_to_choose --help

# Check configuration
python run_scraper.py --config
```

## 📚 Next Steps

1. **Customize thresholds** for your specific needs
2. **Add new scrapers** using `scraper_template.py`
3. **Set up monitoring** to track scraper performance
4. **Configure alerts** for when scrapers fail

## 🔒 Security Checklist

- ✅ Use Gmail App Passwords
- ✅ Enable 2-Factor Authentication
- ✅ Never commit credentials to Git
- ✅ Use `.env` file or environment variables
- ✅ Keep `.env` file secure and local

Your setup is now secure and ready to use! 🎉

