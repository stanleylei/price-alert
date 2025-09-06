#!/bin/bash

# Set default scraper if not specified (default to running all scrapers)
SCRAPER_NAME=${SCRAPER_NAME:-"all"}

# Set default email configuration if not provided (will fail gracefully if not set)
SENDER_EMAIL=${SENDER_EMAIL:-""}
SENDER_PASSWORD=${SENDER_PASSWORD:-""}
RECIPIENT_EMAIL=${RECIPIENT_EMAIL:-""}

# Export environment variables for Python scripts
export SENDER_EMAIL
export SENDER_PASSWORD
export RECIPIENT_EMAIL

echo "=== Price Alert Scraper Container ==="
echo "Mode: $SCRAPER_NAME"
echo "Sender Email: ${SENDER_EMAIL:-"NOT SET - will use default from config"}"
echo "Recipient Email: ${RECIPIENT_EMAIL:-"NOT SET - will use default from config"}"
echo "====================================="

# Check if required credentials are set
if [ -z "$SENDER_EMAIL" ] || [ -z "$SENDER_PASSWORD" ]; then
    echo "Warning: SENDER_EMAIL or SENDER_PASSWORD not set."
    echo "The scrapers will use default credentials from config.py"
    echo "For production use, set these environment variables:"
    echo "  SENDER_EMAIL=your-email@gmail.com"
    echo "  SENDER_PASSWORD=your-app-password"
    echo ""
fi

# Function to run a specific scraper
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

# Main execution logic
case "$SCRAPER_NAME" in
    "power_to_choose")
        run_scraper "power_to_choose"
        ;;
    "villa_del_arco")
        run_scraper "villa_del_arco"
        ;;
    "alaska_award_ticket")
        run_scraper "alaska_award_ticket"
        ;;
    "all"|"")
        echo "Running all scrapers sequentially..."
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
        ;;
    *)
        echo "Error: Unknown scraper '$SCRAPER_NAME'"
        echo "Available options:"
        echo "  power_to_choose      - Run only Power to Choose scraper"
        echo "  villa_del_arco       - Run only Villa del Arco scraper"
        echo "  alaska_award_ticket  - Run only Alaska Award Ticket scraper"
        echo "  all                  - Run all scrapers (default)"
        echo ""
        echo "Usage examples:"
        echo "  docker run -e SCRAPER_NAME=power_to_choose your-image"
        echo "  docker run -e SCRAPER_NAME=villa_del_arco your-image"
        echo "  docker run -e SCRAPER_NAME=alaska_award_ticket your-image"
        echo "  docker run your-image  # Runs all scrapers by default"
        exit 1
        ;;
esac
