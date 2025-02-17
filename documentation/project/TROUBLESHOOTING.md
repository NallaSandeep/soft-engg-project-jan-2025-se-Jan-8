# StudyHub Troubleshooting Guide

## Quick Reference

### Common Issues by Service

1. **Frontend**
   - White screen
   - API connection errors
   - Authentication issues
   - Performance problems

2. **Backend**
   - Database connection
   - Authentication failures
   - API errors
   - Performance issues

3. **StudyIndexer**
   - ML model loading
   - Vector search issues
   - Document processing
   - Memory problems

4. **Infrastructure**
   - Docker problems
   - Network issues
   - Resource constraints
   - Service health

## Detailed Solutions

### Frontend Issues

#### 1. White Screen / Blank Page
```bash
# Check console errors
F12 -> Console

# Clear cache and rebuild
rm -rf node_modules
npm cache clean --force
npm install
npm run build
```

**Common Causes:**
- JavaScript runtime errors
- Missing environment variables
- Broken dependencies
- Build artifacts corruption

#### 2. API Connection Errors
```javascript
// Check API configuration
console.log(process.env.REACT_APP_API_URL)

// Verify CORS headers
curl -I -X OPTIONS http://localhost:5000/api/v1/health
```

**Common Causes:**
- Incorrect API URL
- CORS configuration
- Network issues
- Service unavailability

### Backend Issues

#### 1. Database Connection Errors
```python
# Check database file
ls -l instance/studyhub.db

# Reset database
rm instance/studyhub.db
python scripts/init_db.py
```

**Common Causes:**
- File permissions
- Corrupted database
- Migration issues
- Connection pool exhaustion

#### 2. Authentication Failures
```bash
# Check JWT configuration
echo $JWT_SECRET_KEY

# Clear token cache
redis-cli
> KEYS "token:*"
> DEL token:user123
```

**Common Causes:**
- Invalid JWT secret
- Token expiration
- Redis connection
- Role configuration

### StudyIndexer Issues

#### 1. ML Model Loading
```python
# Check model cache
ls -l ~/.cache/torch/sentence_transformers/

# Clear and redownload
rm -rf ~/.cache/torch/sentence_transformers/
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**Common Causes:**
- Corrupted model files
- Insufficient memory
- Network issues
- CUDA configuration

#### 2. Vector Search Problems
```bash
# Check ChromaDB connection
curl http://localhost:8001/api/v1/heartbeat

# Reset vector database
docker compose down -v
docker compose up -d chromadb
```

**Common Causes:**
- ChromaDB connection
- Index corruption
- Memory constraints
- Query timeout

### Infrastructure Issues

#### 1. Docker Problems
```bash
# Check service status
docker compose ps

# View detailed logs
docker compose logs -f service_name

# Reset environment
docker compose down -v
docker system prune -f
docker compose up -d
```

**Common Causes:**
- Resource exhaustion
- Network conflicts
- Volume permissions
- Configuration errors

#### 2. Resource Constraints
```bash
# Check resource usage
docker stats

# Monitor system resources
htop  # or Task Manager on Windows
```

**Common Causes:**
- Insufficient memory
- CPU bottleneck
- Disk space
- Network bandwidth

## Performance Issues

### 1. Slow Queries
```sql
-- Check slow queries
SELECT * FROM sqlite_master WHERE type='table';
EXPLAIN QUERY PLAN SELECT * FROM documents WHERE user_id = ?;
```

**Solutions:**
1. Add indexes
2. Optimize queries
3. Implement caching
4. Batch operations

### 2. Memory Leaks
```bash
# Monitor memory usage
docker stats

# Check Python memory
python -m memory_profiler app.py
```

**Solutions:**
1. Profile application
2. Implement garbage collection
3. Fix resource cleanup
4. Add memory limits

## Security Issues

### 1. Authentication
```python
# Check token validity
from jose import jwt
token = "your.jwt.token"
try:
    payload = jwt.decode(token, key, algorithms=["HS256"])
    print(payload)
except Exception as e:
    print(f"Invalid token: {e}")
```

### 2. Authorization
```python
# Verify user permissions
@require_role(['admin'])
def protected_route():
    pass
```

## Development Environment

### 1. Setup Issues
```bash
# Clean development environment
./scripts/reset-dev.sh

# Rebuild services
docker compose build --no-cache
```

### 2. IDE Problems
```json
// VSCode settings.json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true
}
```

## Deployment Issues

### 1. Build Failures
```bash
# Clean build artifacts
docker builder prune

# Rebuild with debug
docker compose build --progress=plain
```

### 2. Runtime Errors
```bash
# Check container logs
docker compose logs -f

# Inspect container
docker compose exec service_name sh
```

## Monitoring and Debugging

### 1. Health Checks
```bash
# Check all services
./scripts/health-check.sh

# Individual service check
curl http://localhost:5000/health
```

### 2. Logging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# View application logs
tail -f logs/app.log
```

## Recovery Procedures

### 1. Data Recovery
```bash
# Backup database
cp instance/studyhub.db instance/studyhub.db.bak

# Restore from backup
cp instance/studyhub.db.bak instance/studyhub.db
```

### 2. Service Recovery
```bash
# Restart single service
docker compose restart service_name

# Full system restart
./scripts/restart-system.sh
```

## Known Issues and Workarounds

### 1. ChromaDB Persistence
**Issue:** ChromaDB occasionally loses persistence after container restart
**Workaround:**
```bash
# Force sync before shutdown
curl -X POST http://localhost:8001/api/v1/sync

# Use volume mount
docker compose up -d -v chroma_data:/chroma/data
```

### 2. Celery Task Timeouts
**Issue:** Long-running tasks timeout during document processing
**Workaround:**
```python
@celery_app.task(soft_timeout=3600, hard_timeout=7200)
def process_large_document():
    pass
```

## Version History
- v1.0 (Feb 2025) - Initial troubleshooting guide
- v1.1 (Feb 2025) - Added known issues and recovery procedures 