# Docker Setup and Deployment Guide - Updated ✅

## Overview

This project provides multiple Docker configurations for different deployment scenarios:

- **Development**: Hot-reloading, debug logging, volume mounting for code changes
- **Standard**: Production-ready with basic configuration  
- **Production**: Optimized multi-stage build with security, monitoring, and scaling features

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- Required API keys (see Environment Variables section)

### 1. Setup Environment
```bash
# Copy and edit environment file
make setup-env
# Edit .env with your API keys
```

### 2. Start Development Environment
```bash
make dev
```

### 3. Check Health
```bash
make health
```

## Docker Configurations

### Standard Configuration (`docker-compose.yml`)
- **Use case**: Testing and basic production
- **Features**: MongoDB, Bot service, Mongo Express UI, Enhanced logging
- **Start**: `make run` or `docker-compose up -d`

### Development Configuration (`docker-compose.dev.yml`)  
- **Use case**: Local development
- **Features**: Hot reloading, debug logging, code volume mounting
- **Start**: `make dev`

### Production Configuration (`docker-compose.production.yml`)
- **Use case**: Production deployment
- **Features**: Multi-stage builds, Nginx reverse proxy, resource limits, log aggregation
- **Start**: `make prod`

## Services

### telegram-bot
- **Main application** with FastAPI and Telegram Bot
- **Ports**: 8000 (HTTP API)
- **Health Check**: `/health` endpoint
- **Volumes**: uploads, logs, app data
- **Enhanced**: Comprehensive logging system with 7 specialized log files

### mongodb
- **Database** for storing messages and documents
- **Ports**: 27017
- **Volumes**: Persistent data storage
- **Health Check**: MongoDB ping command

### nginx (Production only)
- **Reverse proxy** with rate limiting and SSL termination
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Features**: Rate limiting, security headers, compression

### mongo-express (Optional)
- **Database UI** for development and debugging
- **Ports**: 8081
- **Credentials**: admin/pass (configurable)

## Updated Docker Images

### Enhanced Standard Dockerfile
- **Base**: python:3.11-slim
- **Size**: ~900MB (includes document processing libraries)
- **New Dependencies**: 
  - `libmagic1`, `libmagic-dev`: File type detection
  - `poppler-utils`: PDF processing
  - `tesseract-ocr`: OCR capabilities
- **Security**: Non-root user, proper permissions
- **Logging**: Pre-configured log directories

### Optimized Production Dockerfile
- **Base**: Multi-stage build
- **Size**: ~650MB (optimized)
- **Features**: 
  - Security hardening
  - Minimal runtime dependencies
  - Optimized Python package installation
  - Enhanced health checks
- **Build**: `docker build -f Dockerfile.production -t telegram-bot:prod .`

## Comprehensive Logging System

### Log Files (in `/app/logs`)
- `bot.log`: Main application logs (10MB, 5 backups)
- `database.log`: Database operations (5MB, 3 backups)
- `document_pipeline.log`: Document processing (5MB, 3 backups)
- `message_pipeline.log`: Message handling (5MB, 3 backups)
- `embedding_service.log`: Embedding operations (5MB, 3 backups)
- `performance.log`: Performance metrics (5MB, 3 backups)
- `user_interactions.log`: User activity tracking (5MB, 3 backups)

### Log Features
- **Automatic rotation**: Size-based with configurable backups
- **Structured format**: Consistent formatting with context
- **Performance tracking**: Function execution times and success/failure rates
- **User analytics**: Interaction patterns and session data
- **Error context**: Detailed error information with stack traces

## Enhanced Makefile Commands

### Development
- `make dev`: Start development environment with enhanced logging
- `make dev-logs`: View development logs
- `make dev-stop`: Stop development

### Production
- `make build`: Build optimized production images
- `make prod`: Start production with monitoring
- `make prod-logs`: View production logs
- `make prod-stop`: Stop production

### New Logging Commands
- `make test-logging`: Test the comprehensive logging system
- `make logs-db`: View database-specific logs
- `make logs-all`: View all service logs

### Enhanced Maintenance
- `make db-backup`: Automated database backup
- `make security-scan`: Security vulnerability scanning
- `make clean`: Smart cleanup preserving important data
- `make clean-all`: Complete cleanup including logs

## Environment Variables

### Required
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
XAI_API_KEY=your_xai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

### Enhanced Optional
```bash
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
LOGS_DIR=/app/logs               # Log directory path
EMBEDDING_SERVICE=huggingface     # huggingface, openai
MONGO_ROOT_USERNAME=admin         # MongoDB admin username
MONGO_ROOT_PASSWORD=password      # MongoDB admin password
```

## Security Enhancements

### Container Security
- **Non-root user**: All processes run as `app` user
- **Proper permissions**: Log and upload directories with correct ownership
- **Resource limits**: Memory and CPU constraints in production
- **Network isolation**: Custom bridge network with controlled access

### Production Security Features
- **Nginx rate limiting**: Prevents abuse and DoS attacks
- **Security headers**: XSS, CSRF, clickjacking protection
- **File access restrictions**: Blocks access to sensitive files
- **SSL/TLS ready**: HTTPS configuration templates included

## Performance Monitoring

### Built-in Metrics
- **Function performance**: Execution time tracking with decorators
- **Database operations**: Query performance and connection health
- **User interactions**: Activity patterns and usage analytics
- **System resources**: Memory, CPU, and disk usage monitoring

### Monitoring Commands
```bash
# Real-time performance monitoring
docker exec telegram-bot tail -f /app/logs/performance.log

# User interaction analytics
docker exec telegram-bot tail -f /app/logs/user_interactions.log

# System resource usage
docker stats telegram-bot
```

## Production Deployment

### Multi-Stage Optimization
```bash
# Build optimized production image
make build

# Run security scan
make security-scan

# Deploy with monitoring
make prod

# Monitor deployment
make prod-logs
```

### Scaling Considerations
- **Horizontal scaling**: Multiple bot instances with load balancing
- **Database scaling**: MongoDB replica sets for high availability
- **Log management**: Centralized logging with retention policies
- **Resource monitoring**: Automated alerting and scaling triggers

## Troubleshooting

### Enhanced Diagnostics
```bash
# Check comprehensive service health
make health

# View specific component logs
make logs-db      # Database logs
docker exec telegram-bot tail -f /app/logs/document_pipeline.log

# Test logging system integrity
make test-logging

# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Common Issues and Solutions

#### Logging Issues
```bash
# Check log directory permissions
docker exec telegram-bot ls -la /app/logs/

# Verify logging configuration
make test-logging

# Monitor log rotation
docker exec telegram-bot find /app/logs -name "*.log*" -ls
```

#### Performance Issues
```bash
# Analyze performance logs
docker exec telegram-bot grep "completed in" /app/logs/performance.log | tail -20

# Check memory usage for embeddings
docker exec telegram-bot grep "embedding" /app/logs/performance.log

# Monitor database performance
docker exec telegram-bot grep "database" /app/logs/performance.log
```

## Backup and Recovery

### Enhanced Backup Strategy
```bash
# Automated database backup
make db-backup

# Backup logs and configuration
docker run --rm -v telegram-multi-agent-ai-bot_logs_data:/logs -v $(pwd):/backup alpine tar czf /backup/logs_backup.tar.gz /logs

# Full system backup
docker run --rm \
  -v telegram-multi-agent-ai-bot_mongodb_data:/data/db \
  -v telegram-multi-agent-ai-bot_logs_data:/data/logs \
  -v telegram-multi-agent-ai-bot_uploads_data:/data/uploads \
  -v $(pwd):/backup alpine \
  tar czf /backup/full_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

## Updates and Improvements ✅

### What's New
1. **Enhanced Dockerfile**: Added document processing dependencies
2. **Production Dockerfile**: Multi-stage optimized build
3. **Comprehensive Logging**: 7 specialized log files with rotation
4. **Security Hardening**: Non-root user, proper permissions, rate limiting
5. **Performance Monitoring**: Built-in metrics and analytics
6. **Production-Ready**: Nginx reverse proxy, resource limits, health checks
7. **Enhanced Makefile**: 20+ commands for complete lifecycle management
8. **Better Documentation**: Comprehensive guides and troubleshooting

### Status: Complete ✅
The Docker setup is now production-ready with comprehensive logging, monitoring, and security features!
