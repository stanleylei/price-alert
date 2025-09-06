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

### 3. Run with Docker Compose

```bash
# Run Power to Choose scraper (runs once and exits)
docker-compose up power-to-choose && docker-compose down

# Run Villa del Arco scraper (runs once and exits)
docker-compose up villa-del-arco && docker-compose down

# Run Alaska Airlines scraper (runs once and exits)
docker-compose up alaska-award-ticket && docker-compose down

# Run all scrapers sequentially (runs once and exits)
docker-compose up all && docker-compose down
```

## Using Docker Compose

### 1. Run Individual Services (One-time execution)

```bash
# Run only Power to Choose scraper (runs once and exits)
docker-compose up power-to-choose

# Run only Villa del Arco scraper (runs once and exits)
docker-compose up villa-del-arco

# Run only Alaska Airlines scraper (runs once and exits)
docker-compose up alaska-award-ticket

# Run all scrapers sequentially (runs once and exits)
docker-compose up all
```

**Note**: After containers exit, remove them with `docker-compose down` to clean up.

### 2. Run and Auto-Cleanup (Recommended for scheduled jobs)

```bash
# Run Power to Choose scraper and remove containers after completion
docker-compose up power-to-choose && docker-compose down

# Run Villa del Arco scraper and remove containers after completion
docker-compose up villa-del-arco && docker-compose down

# Run all scrapers and remove containers after completion
docker-compose up all && docker-compose down
```

### 3. Manual One-time Execution

```bash
# Run with docker-compose and cleanup
docker-compose up power-to-choose && docker-compose down
```

### 4. Scheduled Execution with Cron

For production scheduled jobs, use these commands:

```bash
# Run Power to Choose scraper every hour
0 * * * * cd /path/to/your/project && docker-compose up power-to-choose && docker-compose down

# Run Villa del Arco scraper daily at 9 AM
0 9 * * * cd /path/to/your/project && docker-compose up villa-del-arco && docker-compose down

# Run Alaska Airlines scraper every 2 hours
0 */2 * * * cd /path/to/your/project && docker-compose up alaska-award-ticket && docker-compose down

# Run all scrapers daily at 6 AM
0 6 * * * cd /path/to/your/project && docker-compose up all && docker-compose down
```

**Important Notes**:
- `--rm` flag only works with `docker run`, not `docker-compose up`
- For docker-compose, use `&& docker-compose down` to remove containers after completion
- Containers will exit automatically after completing their task
- Always run `docker-compose down` after execution to clean up

### 5. Custom Environment Variables

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

# Alaska Airlines Configuration
ALASKA_DEPARTURE_STATIONS=DFW
ALASKA_ARRIVAL_STATIONS=SNA,ONT
ALASKA_ADULTS=3
ALASKA_CHILDREN=2
ALASKA_TARGET_POINTS=7500
ALASKA_SEARCH_DATE=2025-11-14
```

Then run:

```bash
docker-compose up power-to-choose && docker-compose down
```

## Environment Variables Reference

### Core Configuration
- `SCRAPER_NAME` - Which scraper to run (`power_to_choose`, `villa_del_arco`, `alaska_award_ticket`, or `all`)
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

### Alaska Airlines Configuration
- `ALASKA_DEPARTURE_STATIONS` - Departure airport codes, comma-separated (default: DFW)
- `ALASKA_ARRIVAL_STATIONS` - Arrival airports, comma-separated (default: SNA,ONT)
- `ALASKA_ADULTS` - Number of adults (default: 3)
- `ALASKA_CHILDREN` - Number of children (default: 2)
- `ALASKA_TARGET_POINTS` - Target points threshold (default: 7500)
- `ALASKA_SEARCH_DATE` - Search date (YYYY-MM-DD) (default: 2025-11-14)

### Web Scraping Configuration (Advanced)
- `SCRAPING_TIMEOUT` - Maximum time to wait for page load in milliseconds (default: 60000)
- `SCRAPING_WAIT_TIMEOUT` - Maximum time to wait for elements in milliseconds (default: 30000)
- `BROWSER_HEADLESS` - Run browser in headless mode (default: true)
- `BROWSER_NO_SANDBOX` - Disable browser sandbox for Docker compatibility (default: true)

## Why Not Docker Run?

The `docker run` command won't work properly because:

1. **Missing environment variables** - No access to the `.env` file
2. **Missing default values** - No access to defaults defined in docker-compose.yml
3. **Missing volume mounts** - No access to the logs directory
4. **Missing build context** - Would need to specify the full image path

**Use docker-compose instead** - it handles all these requirements automatically.

## Advanced Usage

### 1. Persistent Logs

```bash
# Create logs directory
mkdir -p logs

# Run with volume mount for persistent logs
docker-compose up power-to-choose && docker-compose down
```

### 2. Debug Mode

```bash
# Run with interactive shell for debugging
docker-compose run --rm --entrypoint /bin/bash power-to-choose

# Inside container, run scraper manually
python run_scraper.py power_to_choose --help
```

### 3. Production Environment

```bash
# Use environment files
cp .env .env.production
# Edit .env.production with production values
docker-compose --env-file .env.production up power-to-choose && docker-compose down
```

### 4. Resource Limits

```bash
# Set memory and CPU limits in docker-compose.yml
# Add to your service:
# deploy:
#   resources:
#     limits:
#       memory: 512M
#       cpus: '1.0'

docker-compose up power-to-choose && docker-compose down
```

## Monitoring and Logging

### 1. View Logs

```bash
# Follow logs in real-time
docker-compose logs -f power-to-choose

# View last 100 lines
docker-compose logs --tail 100 power-to-choose
```

### 2. Container Metrics

```bash
# View resource usage
docker stats

# View container information
docker-compose ps
```

## Best Practices

1. **Use Environment Files**: Store sensitive configuration in `.env` files
2. **Use Docker Compose**: Leverage docker-compose.yml for consistent execution
3. **Resource Limits**: Set appropriate memory and CPU limits in docker-compose.yml
4. **Log Rotation**: Mount logs directory for persistent storage
5. **Auto-Cleanup**: Always use `&& docker-compose down` after execution
6. **Security**: Use app passwords, not regular passwords for Gmail
7. **Backup**: Regularly backup configuration and log files

## Container Cleanup Options

### Option 1: Docker Compose with Manual Cleanup (Recommended)
```bash
# Run service and cleanup
docker-compose up power-to-choose && docker-compose down

# Run with .env file (recommended for production)
docker-compose up power-to-choose && docker-compose down
```

**Pros**: Uses .env file, easier environment management, consistent with project setup
**Cons**: Requires manual cleanup command

### Option 2: Docker Compose with Script
Create a wrapper script for easier execution:

```bash
#!/bin/bash
# run-scraper.sh
SCRAPER_NAME=$1
docker-compose up $SCRAPER_NAME && docker-compose down
```

Then use:
```bash
./run-scraper.sh power-to-choose
./run-scraper.sh all
```

**Pros**: One command execution, consistent cleanup, easy to use
**Cons**: Requires creating a script file

### Option 3: Cron Jobs with Auto-Cleanup
```bash
# Run Power to Choose scraper every hour
0 * * * * cd /path/to/your/project && docker-compose up power-to-choose && docker-compose down

# Run all scrapers daily at 6 AM
0 6 * * * cd /path/to/your/project && docker-compose up all && docker-compose down
```

**Pros**: Fully automated, consistent cleanup, perfect for production
**Cons**: Requires cron setup

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
   BROWSER_HEADLESS=false docker-compose up power-to-choose && docker-compose down
   ```

## Examples

### Complete Example with All Options

```bash
# Set up environment variables in .env file
# Then run with docker-compose

# For production with resource limits, add to docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 512M
#       cpus: '1.0'

docker-compose up power-to-choose && docker-compose down
```

This setup provides a robust, configurable Docker environment for running your price alert scrapers with the new modular architecture.
