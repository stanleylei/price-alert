# Price Alert Service - Long-Running Mode Documentation

## Overview

The Price Alert scraper now supports running as a **long-running service** with configurable check intervals. Instead of running once and exiting, the container can continuously monitor prices at specified intervals (e.g., every hour, every 3 hours, etc.).

## Service Modes

The container supports three operational modes:

### 1. **Scheduler Mode** (Default - Long-Running Service)
- Runs continuously as a service
- Checks prices at configurable intervals
- Provides health check endpoints for monitoring
- Ideal for production deployments

### 2. **Single Mode** (One-Time Batch Run)
- Runs all enabled scrapers once
- Exits after completion
- Useful for cron jobs or manual runs

### 3. **Oneshot Mode** (Legacy Compatibility)
- Runs specific scraper(s) once
- Exits after completion
- Maintains backward compatibility

## Quick Start

### Running as a Long-Running Service

```bash
# Using docker-compose (recommended)
docker-compose up -d scheduler

# Using docker run
docker run -d \
  --name price-alert-service \
  -e SERVICE_MODE=scheduler \
  -e SCHEDULER_PTC_INTERVAL=60 \
  -e SCHEDULER_VDA_INTERVAL=180 \
  -e SCHEDULER_ALASKA_INTERVAL=120 \
  -p 8080:8080 \
  --env-file .env \
  your-image-name
```

### Running Once (Single Pass)

```bash
# Using docker-compose
docker-compose run --rm single-run

# Using docker run
docker run --rm \
  -e SERVICE_MODE=single \
  --env-file .env \
  your-image-name
```

## Configuration

### Environment Variables

#### Service Mode Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_MODE` | `scheduler` | Operating mode: `scheduler`, `single`, or `oneshot` |
| `HEALTH_CHECK_ENABLED` | `true` | Enable/disable health check endpoint |
| `HEALTH_CHECK_PORT` | `8080` | Port for health check HTTP server |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

#### Scheduler Intervals (in minutes)

| Variable | Default | Description |
|----------|---------|-------------|
| `SCHEDULER_PTC_INTERVAL` | `180` | Power to Choose check interval (3 hours) |
| `SCHEDULER_VDA_INTERVAL` | `360` | Villa del Arco check interval (6 hours) |
| `SCHEDULER_ALASKA_INTERVAL` | `120` | Alaska Airlines check interval (2 hours) |

#### Enable/Disable Scrapers

| Variable | Default | Description |
|----------|---------|-------------|
| `SCHEDULER_PTC_ENABLED` | `true` | Enable Power to Choose scraper |
| `SCHEDULER_VDA_ENABLED` | `true` | Enable Villa del Arco scraper |
| `SCHEDULER_ALASKA_ENABLED` | `true` | Enable Alaska Airlines scraper |

#### Run Immediately on Startup

| Variable | Default | Description |
|----------|---------|-------------|
| `SCHEDULER_PTC_RUN_IMMEDIATELY` | `true` | Run Power to Choose on startup |
| `SCHEDULER_VDA_RUN_IMMEDIATELY` | `true` | Run Villa del Arco on startup |
| `SCHEDULER_ALASKA_RUN_IMMEDIATELY` | `true` | Run Alaska Airlines on startup |

### Example .env File

```env
# Email Configuration (Required)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=alerts@example.com

# Service Configuration
SERVICE_MODE=scheduler
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_PORT=8080

# Scheduler Intervals (minutes)
SCHEDULER_PTC_INTERVAL=60      # Check every hour
SCHEDULER_VDA_INTERVAL=180     # Check every 3 hours
SCHEDULER_ALASKA_INTERVAL=120  # Check every 2 hours

# Enable/Disable Scrapers
SCHEDULER_PTC_ENABLED=true
SCHEDULER_VDA_ENABLED=true
SCHEDULER_ALASKA_ENABLED=false  # Disable Alaska scraper

# Scraper-specific settings
PTC_ZIP_CODE=76092
PTC_PRICE_THRESHOLD=12.4
VDA_CHECK_IN=2025-12-16
VDA_CHECK_OUT=2025-12-19
VDA_PRICE_THRESHOLD=1100
```

## Docker Compose Profiles

The `docker-compose.yml` includes several profiles for different use cases:

### Default Profile (Long-Running Service)

```bash
# Start the scheduler service
docker-compose up -d scheduler

# View logs
docker-compose logs -f scheduler

# Stop the service
docker-compose down
```

### Single Run Profile

```bash
# Run all scrapers once
docker-compose run --rm single-run
```

### Individual Scrapers Profile

```bash
# Run specific scrapers
docker-compose --profile scrapers run --rm power-to-choose
docker-compose --profile scrapers run --rm villa-del-arco
docker-compose --profile scrapers run --rm alaska-award-ticket
```

### Development Profile (Short Intervals)

```bash
# Start with shorter intervals for testing
docker-compose --profile dev up -d scheduler-dev

# This runs with:
# - Power to Choose: every 5 minutes
# - Villa del Arco: every 10 minutes
# - Alaska Airlines: every 15 minutes
```

## Health Monitoring

### Health Check Endpoints

When running in scheduler mode, the service provides HTTP endpoints for monitoring:

#### `/health` - Full Health Status
```bash
curl http://localhost:8080/health
```

Returns detailed health information:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-15T10:30:00",
  "uptime_seconds": 3600,
  "uptime_human": "1h",
  "statistics": {
    "total_runs": 15,
    "successful_runs": 14,
    "failed_runs": 1,
    "success_rate": 93.33
  },
  "scrapers": {
    "power_to_choose": {
      "status": "success",
      "last_run": "2025-09-15T10:25:00"
    },
    "villa_del_arco": {
      "status": "success",
      "last_run": "2025-09-15T10:00:00"
    }
  }
}
```

#### `/ready` - Readiness Check
```bash
curl http://localhost:8080/ready
```

Returns readiness status (useful for container orchestration):
```json
{
  "ready": true,
  "message": "Service is ready"
}
```

#### `/metrics` - Prometheus Metrics
```bash
curl http://localhost:8080/metrics
```

Returns Prometheus-compatible metrics for monitoring:
```
# HELP price_alert_up Service up status
# TYPE price_alert_up gauge
price_alert_up 1

# HELP price_alert_uptime_seconds Service uptime in seconds
# TYPE price_alert_uptime_seconds counter
price_alert_uptime_seconds 3600

# HELP price_alert_total_runs Total number of scraper runs
# TYPE price_alert_total_runs counter
price_alert_total_runs 15
```

### Docker Health Check

The container includes a built-in health check:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' price-alert-scheduler

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' price-alert-scheduler
```

## Deployment Examples

### Production Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  price-alert:
    image: your-registry/price-alert:latest
    container_name: price-alert-production
    restart: always
    environment:
      - SERVICE_MODE=scheduler
      - SCHEDULER_PTC_INTERVAL=180      # 3 hours
      - SCHEDULER_VDA_INTERVAL=360      # 6 hours
      - SCHEDULER_ALASKA_INTERVAL=240   # 4 hours
      - HEALTH_CHECK_ENABLED=true
      - LOG_LEVEL=INFO
    env_file:
      - .env.production
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 60s
      timeout: 10s
      retries: 3
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: price-alert-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: price-alert
  template:
    metadata:
      labels:
        app: price-alert
    spec:
      containers:
      - name: price-alert
        image: your-registry/price-alert:latest
        env:
        - name: SERVICE_MODE
          value: "scheduler"
        - name: SCHEDULER_PTC_INTERVAL
          value: "180"
        - name: SCHEDULER_VDA_INTERVAL
          value: "360"
        envFrom:
        - secretRef:
            name: price-alert-secrets
        ports:
        - containerPort: 8080
          name: health
        livenessProbe:
          httpGet:
            path: /health
            port: health
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: health
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

## Monitoring with Prometheus

If you're using Prometheus for monitoring, add this scrape configuration:

```yaml
scrape_configs:
  - job_name: 'price-alert'
    static_configs:
      - targets: ['price-alert-service:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

## Troubleshooting

### Service Not Starting

1. Check logs:
```bash
docker-compose logs scheduler
```

2. Verify environment variables:
```bash
docker-compose exec scheduler env | grep SCHEDULER
```

3. Test health endpoint:
```bash
curl http://localhost:8080/health
```

### Scrapers Not Running

1. Check if scrapers are enabled:
```bash
docker-compose exec scheduler env | grep ENABLED
```

2. Verify intervals are set correctly:
```bash
docker-compose exec scheduler env | grep INTERVAL
```

3. Check scraper-specific logs in the container logs

### Memory Issues

If the container uses too much memory over time:

1. Restart the service periodically:
```bash
docker-compose restart scheduler
```

2. Set memory limits in docker-compose:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

## Best Practices

1. **Set Appropriate Intervals**: Don't check too frequently to avoid rate limiting
   - Minimum recommended: 30 minutes for any scraper
   - Consider website load and courtesy

2. **Monitor Health Endpoints**: Set up alerts based on health check failures

3. **Log Rotation**: Configure log rotation to prevent disk space issues:
```bash
# Add to docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

4. **Use Secrets Management**: Store sensitive data (passwords, API keys) in Docker secrets or environment files

5. **Graceful Shutdown**: The service handles SIGTERM signals for clean shutdown

## Migration from One-Shot to Service Mode

If you're currently using cron jobs to run the scrapers:

### Before (Cron Job)
```cron
0 */3 * * * docker run --rm price-alert
```

### After (Long-Running Service)
```bash
# Start once
docker-compose up -d scheduler

# Service runs continuously with configured intervals
# No cron job needed
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs scheduler`
2. Verify health status: `curl http://localhost:8080/health`
3. Review configuration: `docker-compose exec scheduler env`
4. Check the main README.md for general setup instructions