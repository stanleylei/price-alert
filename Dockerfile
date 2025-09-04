# Start from the recommended Python 3.12 slim image
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and system dependencies
RUN playwright install --with-deps chromium

# Copy all project files into the container
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Create a proper .env.example file for users
RUN echo "# Price Alert Scraper Environment Configuration" > .env.example && \
    echo "# Copy this file to .env and fill in your actual credentials" >> .env.example && \
    echo "# DO NOT commit your .env file to version control!" >> .env.example && \
    echo "" >> .env.example && \
    echo "# Email Configuration (REQUIRED - Replace with your actual credentials)" >> .env.example && \
    echo "SENDER_EMAIL=your-email@gmail.com" >> .env.example && \
    echo "SENDER_PASSWORD=your-gmail-app-password" >> .env.example && \
    echo "RECIPIENT_EMAIL=recipient@example.com" >> .env.example && \
    echo "" >> .env.example && \
    echo "# Scraper Selection (OPTIONAL - defaults to 'all')" >> .env.example && \
    echo "# Options: power_to_choose, villa_del_arco, all" >> .env.example && \
    echo "SCRAPER_NAME=all" >> .env.example && \
    echo "" >> .env.example && \
    echo "# Power to Choose Configuration (OPTIONAL - Customize for your needs)" >> .env.example && \
    echo "PTC_ZIP_CODE=your-zip-code" >> .env.example && \
    echo "PTC_CONTRACT_MIN=12" >> .env.example && \
    echo "PTC_CONTRACT_MAX=60" >> .env.example && \
    echo "PTC_PRICE_THRESHOLD=12.4" >> .env.example && \
    echo "PTC_MAX_RESULTS=5" >> .env.example && \
    echo "" >> .env.example && \
    echo "# Villa del Arco Configuration (OPTIONAL - Customize for your needs)" >> .env.example && \
    echo "VDA_CHECK_IN=your-check-in-date" >> .env.example && \
    echo "VDA_CHECK_OUT=your-check-out-date" >> .env.example && \
    echo "VDA_ADULTS=2" >> .env.example && \
    echo "VDA_CHILDREN=2" >> .env.example && \
    echo "VDA_PRICE_THRESHOLD=1100" >> .env.example && \
    echo "" >> .env.example && \
    echo "# Web Scraping Configuration (OPTIONAL - Advanced settings)" >> .env.example && \
    echo "SCRAPING_TIMEOUT=60000" >> .env.example && \
    echo "SCRAPING_WAIT_TIMEOUT=30000" >> .env.example && \
    echo "BROWSER_HEADLESS=true" >> .env.example && \
    echo "BROWSER_NO_SANDBOX=true" >> .env.example

# Set the command to run when the container starts
CMD ["./start.sh"]