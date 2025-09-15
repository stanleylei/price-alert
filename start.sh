#!/bin/bash

# Service Mode Configuration
SERVICE_MODE=${SERVICE_MODE:-"scheduler"}  # Options: scheduler, single, oneshot
SCRAPER_NAME=${SCRAPER_NAME:-""}  # Used for oneshot mode

# Set default email configuration if not provided (will fail gracefully if not set)
SENDER_EMAIL=${SENDER_EMAIL:-""}
SENDER_PASSWORD=${SENDER_PASSWORD:-""}
RECIPIENT_EMAIL=${RECIPIENT_EMAIL:-""}

# Export environment variables for Python scripts
export SENDER_EMAIL
export SENDER_PASSWORD
export RECIPIENT_EMAIL
export SERVICE_MODE

echo "========================================="
echo "   Price Alert Scraper Container"
echo "========================================="
echo "Service Mode: $SERVICE_MODE"

if [ "$SERVICE_MODE" = "scheduler" ]; then
    echo ""
    echo "Scheduler Configuration:"
    echo "  Power to Choose: Every ${SCHEDULER_PTC_INTERVAL:-180} minutes (Enabled: ${SCHEDULER_PTC_ENABLED:-true})"
    echo "  Villa del Arco: Every ${SCHEDULER_VDA_INTERVAL:-360} minutes (Enabled: ${SCHEDULER_VDA_ENABLED:-true})"
    echo "  Alaska Airlines: Every ${SCHEDULER_ALASKA_INTERVAL:-120} minutes (Enabled: ${SCHEDULER_ALASKA_ENABLED:-true})"
    echo ""
    echo "Health Check: http://localhost:${HEALTH_CHECK_PORT:-8080}/health"
fi

echo ""
echo "Email Configuration:"
echo "  Sender: ${SENDER_EMAIL:-"NOT SET - will use default from config"}"
echo "  Recipient: ${RECIPIENT_EMAIL:-"NOT SET - will use default from config"}"
echo "========================================="
echo ""

# Check if required credentials are set
if [ -z "$SENDER_EMAIL" ] || [ -z "$SENDER_PASSWORD" ]; then
    echo "⚠️  Warning: SENDER_EMAIL or SENDER_PASSWORD not set."
    echo "   The scrapers will use default credentials from config.py"
    echo "   For production use, set these environment variables:"
    echo "     SENDER_EMAIL=your-email@gmail.com"
    echo "     SENDER_PASSWORD=your-app-password"
    echo ""
fi

# Function to run a specific scraper (for oneshot mode)
run_scraper() {
    local scraper_name=$1
    echo "Starting $scraper_name scraper..."
    python run_scraper.py "$scraper_name"
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✓ $scraper_name scraper completed successfully"
    else
        echo "✗ $scraper_name scraper failed with exit code $exit_code"
    fi
    return $exit_code
}

# Main execution logic based on SERVICE_MODE
case "$SERVICE_MODE" in
    "scheduler")
        echo "🚀 Starting Price Alert Service in SCHEDULER mode"
        echo "   This is a long-running service that will check prices at configured intervals."
        echo ""
        
        # Run the scheduler service
        exec python scheduler.py --mode service
        ;;
        
    "single")
        echo "🔄 Running scrapers in SINGLE-PASS mode"
        echo "   All enabled scrapers will run once and then exit."
        echo ""
        
        # Run all enabled scrapers once
        python scheduler.py --mode single
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            echo ""
            echo "✅ All scrapers completed successfully"
        else
            echo ""
            echo "⚠️  Some scrapers encountered errors"
        fi
        exit $exit_code
        ;;
        
    "oneshot")
        echo "⚡ Running in ONESHOT mode"
        
        # This mode is for backward compatibility - runs specific scraper or all
        if [ -z "$SCRAPER_NAME" ] || [ "$SCRAPER_NAME" = "all" ]; then
            echo "   Running all scrapers sequentially..."
            echo ""
            
            # Run Power to Choose scraper
            run_scraper "power_to_choose"
            ptc_exit_code=$?
            
            echo ""
            
            # Run Villa del Arco scraper
            run_scraper "villa_del_arco"
            vda_exit_code=$?
            
            echo ""
            
            # Run Alaska Award Ticket scraper
            run_scraper "alaska_award_ticket"
            alaska_exit_code=$?
            
            echo ""
            echo "=== All Scrapers Completed ==="
            if [ $ptc_exit_code -eq 0 ] && [ $vda_exit_code -eq 0 ] && [ $alaska_exit_code -eq 0 ]; then
                echo "✓ All scrapers completed successfully"
                exit 0
            else
                echo "⚠ Some scrapers had issues:"
                [ $ptc_exit_code -ne 0 ] && echo "  - Power to Choose: Failed"
                [ $vda_exit_code -ne 0 ] && echo "  - Villa del Arco: Failed"
                [ $alaska_exit_code -ne 0 ] && echo "  - Alaska Award Ticket: Failed"
                exit 1
            fi
        else
            # Run specific scraper
            echo "   Running $SCRAPER_NAME scraper..."
            run_scraper "$SCRAPER_NAME"
            exit $?
        fi
        ;;
        
    *)
        echo "❌ Error: Unknown SERVICE_MODE '$SERVICE_MODE'"
        echo ""
        echo "Available modes:"
        echo "  scheduler  - Long-running service with scheduled intervals (default)"
        echo "  single     - Run all enabled scrapers once and exit"
        echo "  oneshot    - Run specific scraper(s) once and exit (legacy mode)"
        echo ""
        echo "Usage examples:"
        echo "  # Run as a long-running service (default)"
        echo "  docker run -e SERVICE_MODE=scheduler your-image"
        echo ""
        echo "  # Run all scrapers once"
        echo "  docker run -e SERVICE_MODE=single your-image"
        echo ""
        echo "  # Run specific scraper once (legacy)"
        echo "  docker run -e SERVICE_MODE=oneshot -e SCRAPER_NAME=power_to_choose your-image"
        echo ""
        echo "Configure intervals with:"
        echo "  SCHEDULER_PTC_INTERVAL=60      # Check every 60 minutes"
        echo "  SCHEDULER_VDA_INTERVAL=180     # Check every 3 hours"
        echo "  SCHEDULER_ALASKA_INTERVAL=120  # Check every 2 hours"
        exit 1
        ;;
esac