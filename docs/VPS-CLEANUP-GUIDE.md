# VPS Disk Space Cleanup Guide

## Current Status
- **Total Space**: 45GB
- **Used**: 44GB (97%)
- **Available**: 1.4GB ⚠️
- **Problem**: Docker needs ~2-3GB for building with full ML dependencies

## Quick Fix: Clean Docker (Run on VPS)

```bash
# SSH into your VPS
ssh ubuntu@your-vps-ip

# Run Docker cleanup
docker system prune -a -f --volumes

# Check space freed
df -h /
```

This should free **5-10GB** by removing:
- Stopped containers
- Unused images
- Build cache
- Unused volumes

## Option 1: Use Lightweight Build (Current - Recommended)

✅ **Already configured** - Your latest commit uses `requirements-prod.txt`
- Build size: ~50MB
- Build time: ~30 seconds
- **Works with 1.4GB free space**
- Face recognition in mock mode

## Option 2: Full ML Dependencies (After Cleanup)

If you clean up Docker and have **3GB+ free**, you can switch back:

### Update Dockerfile:
```dockerfile
# Change line 16 from:
COPY requirements-prod.txt requirements.txt ./
# To:
COPY requirements.txt .

# Change line 19 from:
RUN pip install --no-cache-dir -r requirements-prod.txt
# To:
RUN pip install --no-cache-dir -r requirements.txt

# Remove line 25:
# ENV FORCE_MOCK_MODE=true
```

### Benefits:
- Real face recognition with DeepFace
- Actual biometric verification
- Production-ready ML models

### Drawbacks:
- Build size: ~600MB
- Build time: ~5 minutes
- Requires 3GB+ free space
- Slower server startup

## Recommended Action

1. **Keep lightweight build** (current setup)
2. **Clean Docker** to prevent future issues:
   ```bash
   # On VPS
   docker system prune -a -f --volumes
   ```
3. **Monitor disk usage** regularly
4. **Consider upgrading VPS** if you need real face recognition

## Additional Cleanup (If Needed)

```bash
# Remove old logs
sudo journalctl --vacuum-time=7d

# Remove old kernels (Ubuntu)
sudo apt autoremove --purge

# Find large files
sudo du -h / | sort -rh | head -20

# Clean apt cache
sudo apt clean
```

## Coolify-Specific Cleanup

```bash
# Remove old Coolify deployments
cd /data/coolify
docker compose down
docker system prune -a -f --volumes
docker compose up -d
```
