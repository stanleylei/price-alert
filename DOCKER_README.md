# Docker Usage Guide

This guide explains how to use Docker with the new modular price alert scraper structure. **This setup is designed for scheduled jobs that run once and exit.**

## Overview

The containers are designed to:
- Run the specified scraper(s) once
- Exit automatically when the job is complete
- Clean up after themselves (no persistent containers)
- Be perfect for cron jobs and scheduled tasks

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t price-alert .
```

### 2. Set Up Environment Variables

Create a `.env` file in your project directory by copying the sample:

```bash
cp env.sample .env
```

Then edit `.env` with your actual credentials and configuration.

### 3. Run a Specific Scraper

```bash
# Run Power to Choose scraper (runs once and exits)
docker run --rm -e SCRAPER_NAME=power_to_choose price-alert

# Run Villa del Arco scraper (runs once and exits)
docker run --rm -e SCRAPER_NAME=villa_del_arco price-alert
```

### 4. Run with Custom Configuration

```bash
# Custom email settings
docker run \
  -e SCRAPER_NAME=power_to_choose \
  -e SENDER_EMAIL="your-email@gmail.com" \
  -e SENDER_PASSWORD="your-app-password" \
  -e RECIPIENT_EMAIL="recipient@example.com" \
  price-alert

# Custom Power to Choose settings
docker run \
  -e SCRAPER_NAME=power_to_choose \
  -e PTC_ZIP_CODE="75001" \
  -e PTC_PRICE_THRESHOLD="11.5" \
  price-alert

# Custom Villa del Arco settings
docker run \
  -e SCRAPER_NAME=villa_del_arco \
  -e VDA_CHECK_IN="2025-01-15" \
  -e VDA_CHECK_OUT="2025-01-18" \
  -e VDA_ADULTS="4" \
  -e VDA_CHILDREN="0" \
  price-alert
```

## Using Docker Compose

### 1. Run Individual Services (One-time execution)

```bash
# Run only Power to Choose scraper (runs once and exits)
docker-compose up power-to-choose

# Run only Villa del Arco scraper (runs once and exits)
docker-compose up villa-del-arco

# Run both scrapers sequentially (runs once and exits)
docker-compose up all
```

### 2. Run in Background

```bash
# Start services in background
docker-compose up -d power-to-choose
docker-compose up -d villa-del-arco

# View logs
docker-compose logs -f power-to-choose
docker-compose logs -f villa-del-arco

# Stop services
docker-compose down
```

### 3. Manual One-time Execution

```bash
# Run and remove container automatically
docker-compose up --rm power-to-choose

# Run with custom environment variables
SCRAPER_NAME=power_to_choose docker-compose up --rm power-to-choose
```

### 4. Scheduled Execution with Cron

For production scheduled jobs, use these commands:

```bash
# Run Power to Choose scraper every hour
0 * * * * cd /path/to/your/project && docker-compose up --rm power-to-choose

# Run Villa del Arco scraper daily at 9 AM
0 9 * * * cd /path/to/your/project && docker-compose up --rm villa-del-arco

# Run all scrapers daily at 6 AM
0 6 * * * cd /path/to/your/project && docker-compose up --rm all
```

**Note**: Containers will exit automatically after completing their task. No need to manually stop them.

### 4. Custom Environment Variables

Create a `.env` file in your project directory:

```bash
# Email Configuration
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com

# Power to Choose Configuration
PTC_ZIP_CODE=75001
PTC_CONTRACT_MIN=6
PTC_CONTRACT_MAX=36
PTC_PRICE_THRESHOLD=11.5

# Villa del Arco Configuration
VDA_CHECK_IN=2025-01-15
VDA_CHECK_OUT=2025-01-18
VDA_ADULTS=4
VDA_CHILDREN=0
VDA_PRICE_THRESHOLD=1200
```

Then run:

```bash
docker-compose up --rm power-to-choose
```

## Environment Variables Reference

### Core Configuration
- `SCRAPER_NAME` - Which scraper to run (`power_to_choose`, `villa_del_arco`, or `all`)
- `SENDER_EMAIL` - Gmail address for sending emails
- `SENDER_PASSWORD` - Gmail app password
- `RECIPIENT_EMAIL` - Email address to receive alerts

### Power to Choose Configuration
- `PTC_ZIP_CODE` - ZIP code for electricity plan search (default: 76092)
- `PTC_CONTRACT_MIN` - Minimum contract length in months (default: 12)
- `PTC_CONTRACT_MAX` - Maximum contract length in months (default: 60)
- `PTC_PRICE_THRESHOLD` - Price threshold in cents per kWh (default: 12.4)
- `PTC_MAX_RESULTS` - Maximum number of results to process (default: 5)

### Villa del Arco Configuration
- `VDA_CHECK_IN` - Check-in date (YYYY-MM-DD) (default: 2025-12-16)
- `VDA_CHECK_OUT` - Check-out date (YYYY-MM-DD) (default: 2025-12-19)
- `VDA_ADULTS` - Number of adults (default: 2)
- `VDA_CHILDREN` - Number of children (default: 2)
- `VDA_PRICE_THRESHOLD` - Price threshold in USD (default: 1100)

### Web Scraping Configuration (Advanced)
- `SCRAPING_TIMEOUT` - Maximum time to wait for page load in milliseconds (default: 60000)
- `SCRAPING_WAIT_TIMEOUT` - Maximum time to wait for elements in milliseconds (default: 30000)
- `BROWSER_HEADLESS` - Run browser in headless mode (default: true)
- `BROWSER_NO_SANDBOX` - Disable browser sandbox for Docker compatibility (default: true)

## Advanced Usage

### 1. Persistent Logs

```bash
# Create logs directory
mkdir -p logs

# Run with volume mount for persistent logs
docker run \
  -v $(pwd)/logs:/app/logs \
  -e SCRAPER_NAME=power_to_choose \
  price-alert
```

### 2. Scheduled Execution

```bash
# Run scraper every hour using cron
0 * * * * docker run --rm price-alert -e SCRAPER_NAME=power_to_choose

# Run scraper daily at 9 AM
0 9 * * * docker run --rm price-alert -e SCRAPER_NAME=villa_del_arco
```

### 3. Health Checks

```bash
# Check container status
docker ps

# View container logs
docker logs <container_id>

# Execute commands in running container
docker exec -it <container_id> /bin/bash
```

## Troubleshooting

### Common Issues

1. **Playwright Installation**
   ```bash
   # Rebuild with fresh Playwright installation
   docker build --no-cache -t price-alert .
   ```

2. **Permission Issues**
   ```bash
   # Fix file permissions
   chmod +x start.sh
   ```

3. **Email Authentication**
   - Ensure you're using Gmail app passwords, not regular passwords
   - Check that 2FA is enabled on your Gmail account

4. **Browser Issues**
   ```bash
   # Run with debug mode (non-headless)
   docker run -e BROWSER_HEADLESS=false price-alert
   ```

### Debug Mode

```bash
# Run with interactive shell for debugging
docker run -it --entrypoint /bin/bash price-alert

# Inside container, run scraper manually
python run_scraper.py power_to_choose --help
```

## Production Deployment

### 1. Environment Variables

```bash
# Use Docker secrets or environment files
docker run \
  --env-file .env.production \
  price-alert
```

### 2. Resource Limits

```bash
# Set memory and CPU limits
docker run \
  --memory="512m" \
  --cpus="1.0" \
  -e SCRAPER_NAME=power_to_choose \
  price-alert
```

### 3. Restart Policies

```bash
# Automatic restart on failure
docker run \
  --restart unless-stopped \
  -e SCRAPER_NAME=power_to_choose \
  price-alert
```

## Monitoring and Logging

### 1. View Logs

```bash
# Follow logs in real-time
docker logs -f <container_id>

# View last 100 lines
docker logs --tail 100 <container_id>
```

### 2. Container Metrics

```bash
# View resource usage
docker stats

# View container information
docker inspect <container_id>
```

## Best Practices

1. **Use Environment Files**: Store sensitive configuration in `.env` files
2. **Resource Limits**: Set appropriate memory and CPU limits
3. **Log Rotation**: Mount logs directory for persistent storage
4. **Health Checks**: Monitor container health and restart on failure
5. **Security**: Use app passwords, not regular passwords for Gmail
6. **Backup**: Regularly backup configuration and log files

## Examples

### Complete Example with All Options

```bash
docker run \
  --name price-alert-ptc \
  --restart unless-stopped \
  --memory="512m" \
  --cpus="1.0" \
  -v $(pwd)/logs:/app/logs \
  -e SCRAPER_NAME=power_to_choose \
  -e SENDER_EMAIL="your-email@gmail.com" \
  -e SENDER_PASSWORD="your-app-password" \
  -e RECIPIENT_EMAIL="recipient@example.com" \
  -e PTC_ZIP_CODE="75001" \
  -e PTC_PRICE_THRESHOLD="11.5" \
  price-alert
```

This setup provides a robust, configurable Docker environment for running your price alert scrapers with the new modular architecture.
