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
    echo "" >> .env.example && \
    echo "# Email Configuration (REQUIRED)" >> .env.example && \
    echo "SENDER_EMAIL=your-email@gmail.com" >> .env.example && \
    echo "SENDER_PASSWORD=your-gmail-app-password" >> .env.example && \
    echo "RECIPIENT_EMAIL=recipient@example.com" >> .env.example && \
    echo "" >> .env.example && \
    echo "# Scraper Selection (OPTIONAL - defaults to 'all')" >> .env.example && \
    echo "SCRAPER_NAME=all" >> .env.example && \
    echo "" >> .env.example && \
    echo "# Power to Choose Configuration (OPTIONAL)" >> .env.example && \
    echo "PTC_ZIP_CODE=76092" >> .env.example && \
    echo "PTC_CONTRACT_MIN=12" >> .env.example && \
    echo "PTC_CONTRACT_MAX=60" >> .env.example && \
    echo "PTC_PRICE_THRESHOLD=12.4" >> .env.example && \
    echo "" >> .env.example && \
    echo "# Villa del Arco Configuration (OPTIONAL)" >> .env.example && \
    echo "VDA_CHECK_IN=2025-12-16" >> .env.example && \
    echo "VDA_CHECK_OUT=2025-12-19" >> .env.example && \
    echo "VDA_ADULTS=2" >> .env.example && \
    echo "VDA_CHILDREN=2" >> .env.example && \
    echo "VDA_PRICE_THRESHOLD=1100" >> .env.example

# Set the command to run when the container starts
CMD ["./start.sh"]