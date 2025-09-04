# Setup Guide for Price Alert Scrapers

This guide will help you set up the price alert scrapers securely without exposing your credentials in the public repository.

## 🔐 Security First

**IMPORTANT**: Never commit your actual email credentials to this repository. The repository is public and your credentials would be exposed to everyone.

## 📋 Prerequisites

1. **Gmail Account** with 2-Factor Authentication enabled
2. **App Password** generated for Gmail (not your regular password)
3. **Python 3.8+** installed on your system
4. **Docker** (optional, for containerized execution)

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd synology-price-alert
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Set Up Email Credentials

#### Option A: Environment Variables (Recommended)

```bash
# Set your credentials as environment variables
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-gmail-app-password"
export RECIPIENT_EMAIL="recipient@example.com"

# Make them permanent (add to your shell profile)
echo 'export SENDER_EMAIL="your-email@gmail.com"' >> ~/.bashrc
echo 'export SENDER_PASSWORD="your-gmail-app-password"' >> ~/.bashrc
echo 'export RECIPIENT_EMAIL="recipient@example.com"' >> ~/.bashrc
```

#### Option B: .env File (Easiest for Docker)

```bash
# Copy the sample environment file
cp env.sample .env

# Edit the .env file with your actual credentials
nano .env
```

**Important**: Replace the sample values in `.env` with your actual credentials:
- `SENDER_EMAIL` - Your Gmail address
- `SENDER_PASSWORD` - Your Gmail app password (not regular password)
- `RECIPIENT_EMAIL` - Where to send alerts

**Example .env file content:**
```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password
RECIPIENT_EMAIL=recipient@example.com
SCRAPER_NAME=all
```

### 4. Test the Setup

```bash
# Check configuration
python run_scraper.py --config

# Test a specific scraper
python run_scraper.py power_to_choose
```

## 🔑 Gmail App Password Setup

### Step 1: Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click on "2-Step Verification"
3. Follow the setup process

### Step 2: Generate App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click on "App passwords" (under 2-Step Verification)
3. Select "Mail" and "Other (Custom name)"
4. Enter a name like "Price Alert Scraper"
5. Click "Generate"
6. **Copy the 16-character password** (this is your `SENDER_PASSWORD`)

### Step 3: Use the App Password

- Use your regular Gmail address as `SENDER_EMAIL`
- Use the 16-character app password as `SENDER_PASSWORD`
- **Never use your regular Gmail password**

## 🐳 Docker Setup

### 1. Build the Image

```bash
docker build -t price-alert .
```

### 2. Run with Environment Variables

```bash
# Run all scrapers (default)
docker run \
  -e SENDER_EMAIL="your-email@gmail.com" \
  -e SENDER_PASSWORD="your-gmail-app-password" \
  -e RECIPIENT_EMAIL="recipient@example.com" \
  price-alert

# Run specific scraper
docker run \
  -e SCRAPER_NAME=power_to_choose \
  -e SENDER_EMAIL="your-email@gmail.com" \
  -e SENDER_PASSWORD="your-gmail-app-password" \
  -e RECIPIENT_EMAIL="recipient@example.com" \
  price-alert
```

### 3. Run with .env File

```bash
# Create .env file first, then run
docker run --env-file .env price-alert
```

### 4. Using Docker Compose

```bash
# Run all scrapers
docker-compose up all-scrapers

# Run specific scraper
docker-compose up power-to-choose
```

## ⚙️ Configuration Options

### Scraper Selection

- `SCRAPER_NAME=all` - Run all scrapers (default)
- `SCRAPER_NAME=power_to_choose` - Run only Power to Choose
- `SCRAPER_NAME=villa_del_arco` - Run only Villa del Arco

### Power to Choose Configuration

```bash
export PTC_ZIP_CODE="75001"           # Your ZIP code
export PTC_CONTRACT_MIN="6"           # Min contract months
export PTC_CONTRACT_MAX="36"          # Max contract months
export PTC_PRICE_THRESHOLD="11.5"    # Price threshold (cents/kWh)
```

### Villa del Arco Configuration

```bash
export VDA_CHECK_IN="2025-01-15"     # Check-in date
export VDA_CHECK_OUT="2025-01-18"    # Check-out date
export VDA_ADULTS="4"                 # Number of adults
export VDA_CHILDREN="0"               # Number of children
export VDA_PRICE_THRESHOLD="1200"    # Price threshold (USD)
```

## 🧪 Testing Your Setup

### 1. Test Configuration

```bash
python run_scraper.py --config
```

### 2. Test Individual Scrapers

```bash
# Test Power to Choose
python run_scraper.py power_to_choose

# Test Villa del Arco
python run_scraper.py villa_del_arco
```

### 3. Test Email Functionality

The scrapers will only send emails when alert conditions are met. To test email functionality:

1. Set a very low price threshold (e.g., `PTC_PRICE_THRESHOLD=1.0`)
2. Run the scraper
3. Check if you receive an email alert

## 🚨 Troubleshooting

### Common Issues

#### 1. "Email configuration is incomplete"

**Solution**: Set your environment variables or create a .env file

```bash
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-gmail-app-password"
export RECIPIENT_EMAIL="recipient@example.com"
```

#### 2. "Authentication failed" or "Invalid credentials"

**Solutions**:
- Ensure 2-Factor Authentication is enabled
- Use an App Password, not your regular password
- Check that the App Password is correct
- Ensure "Less secure app access" is disabled

#### 3. "Module not found" errors

**Solution**: Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

#### 4. Browser/Playwright issues

**Solution**: Reinstall Playwright

```bash
pip uninstall playwright
pip install playwright
playwright install --with-deps chromium
```

### Debug Mode

```bash
# Run with verbose output
python run_scraper.py power_to_choose --help

# Check environment variables
env | grep -E "(SENDER|RECIPIENT)"
```

## 🔄 Automation

### Cron Jobs

```bash
# Run every hour
0 * * * * cd /path/to/synology-price-alert && python run_scraper.py power_to_choose

# Run daily at 9 AM
0 9 * * * cd /path/to/synology-price-alert && python run_scraper.py villa_del_arco
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
WorkingDirectory=/path/to/synology-price-alert
Environment=SENDER_EMAIL=your-email@gmail.com
Environment=SENDER_PASSWORD=your-gmail-app-password
Environment=RECIPIENT_EMAIL=recipient@example.com
ExecStart=/usr/bin/python3 run_scraper.py all

[Install]
WantedBy=multi-user.target
```

## 📚 Next Steps

1. **Customize thresholds** for your specific needs
2. **Add new scrapers** using the template in `scraper_template.py`
3. **Set up monitoring** to track scraper performance
4. **Configure alerts** for when scrapers fail

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your Gmail App Password setup
3. Check that all environment variables are set
4. Review the logs for specific error messages

## 🔒 Security Reminders

- ✅ Use Gmail App Passwords
- ✅ Enable 2-Factor Authentication
- ✅ Never commit credentials to Git
- ✅ Use environment variables or .env files
- ✅ Keep your .env file secure and local

Your setup is now secure and ready to use! 🎉

