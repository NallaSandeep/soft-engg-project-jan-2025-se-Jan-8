# Docker Fixes and Solutions

## Common Issues and Solutions

### 1. ML Dependencies in Celery Worker
**Issue**: Celery worker fails to process documents due to missing ML libraries
**Fix**:
```dockerfile
# Add to Dockerfile
RUN apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgomp1
```

### 2. Line Ending Issues
**Issue**: `exec format error` in entrypoint scripts
**Fix**:
```bash
# Fix line endings
docker compose exec service_name sh -c "apt-get update && apt-get install -y dos2unix && dos2unix /docker-entrypoint.sh"
```

### 3. Volume Permissions
**Issue**: Permission denied errors for mounted volumes
**Fix**:
```dockerfile
# Add to Dockerfile
RUN mkdir -p /app/data && chown -R nobody:nobody /app/data
USER nobody
```

### 4. Health Check Timing
**Issue**: Services marked unhealthy due to slow startup
**Fix**:
```yaml
# docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Best Practices

1. **Layer Caching**
   - Use BuildKit cache
   - Order dependencies properly
   - Minimize layer size

2. **Resource Management**
   - Set appropriate limits
   - Monitor resource usage
   - Use resource reservations

3. **Network Configuration**
   - Use internal networks
   - Configure proper DNS
   - Handle service discovery

## Version History
- v1.0 (Feb 2025) - Initial documentation
- v1.1 (Feb 2025) - Added best practices 