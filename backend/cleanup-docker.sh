#!/bin/bash
# Docker Cleanup Script for Coolify VPS
# Run this to free up disk space

echo "🧹 Starting Docker cleanup..."
echo ""

# Show current disk usage
echo "📊 Current disk usage:"
df -h /
echo ""

# Stop all containers (optional - comment out if you want to keep running containers)
# echo "⏸️  Stopping all containers..."
# docker stop $(docker ps -aq)

# Remove stopped containers
echo "🗑️  Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "🗑️  Removing unused images..."
docker image prune -a -f

# Remove unused volumes
echo "🗑️  Removing unused volumes..."
docker volume prune -f

# Remove build cache
echo "🗑️  Removing build cache..."
docker builder prune -a -f

# Remove unused networks
echo "🗑️  Removing unused networks..."
docker network prune -f

# Show disk usage after cleanup
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Disk usage after cleanup:"
df -h /
echo ""

# Show Docker disk usage
echo "📦 Docker disk usage:"
docker system df
