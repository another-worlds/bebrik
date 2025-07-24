# Docker Setup Guide

This document provides instructions for setting up and running the Telegram Multi-Agent AI Bot using Docker.

## Quick Start

### 1. Environment Setup
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
nano .env
```

Required environment variables:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `XAI_API_KEY`: Your xAI (X.AI) API key

### 2. Build and Run
```bash
# Build and start all services
make docker-run

# Or manually with docker-compose
docker-compose up -d
```

### 3. Check Status
```bash
# View bot logs
make docker-logs

# View all services logs
make docker-logs-all

# Check health
curl http://localhost:8000/health
```

## Available Services

| Service | Port | Description |
|---------|------|-------------|
| telegram-bot | 8000 | Main bot application |
| mongodb | 27017 | MongoDB database |
| mongo-express | 8081 | MongoDB admin UI (optional) |

## Access Points

- **Bot API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **MongoDB Admin**: http://localhost:8081 (admin/pass)

## Docker Commands

### Development
```bash
# Start in development mode (with auto-reload)
docker-compose -f docker-compose.dev.yml up

# Build without cache
docker-compose build --no-cache
```

### Production
```bash
# Start services
make docker-run

# Stop services
make docker-stop

# Restart bot only
make docker-restart

# View logs
make docker-logs

# Clean up everything
make docker-clean
```

### Maintenance
```bash
# Remove stopped containers and unused images
docker system prune

# Remove all volumes (WARNING: data loss)
docker-compose down -v

# Rebuild from scratch
make docker-clean
make docker-build
make docker-run
```

## Environment Variables

### Required
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
XAI_API_KEY=your_xai_api_key
```

### Optional
```env
MONGODB_URI=mongodb://admin:password@mongodb:27017/telegram_bot?authSource=admin
MONGODB_DB_NAME=telegram_bot
DOCUMENT_UPLOAD_PATH=uploads
LOG_LEVEL=INFO
```

## Volumes

The following directories are mounted as volumes:
- `./uploads:/app/uploads` - Document uploads
- `./logs:/app/logs` - Application logs
- `mongodb_data:/data/db` - MongoDB data persistence

## Troubleshooting

### Bot Not Starting
1. Check environment variables in `.env`
2. Verify Telegram bot token
3. Check logs: `make docker-logs`

### MongoDB Connection Issues
1. Ensure MongoDB container is running: `docker-compose ps`
2. Check MongoDB logs: `docker-compose logs mongodb`
3. Verify connection string in `.env`

### Permission Issues
```bash
# Fix upload directory permissions
sudo chown -R $USER:$USER uploads/
chmod 755 uploads/
```

### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

## Development Setup

For development with auto-reload:
```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up

# The application will auto-reload on code changes
```

## Health Monitoring

The application includes health checks:
- Docker health check every 30 seconds
- Health endpoint: `GET /health`
- Automatic container restart on failure

Check container health:
```bash
docker ps
# Look for "healthy" status
```
