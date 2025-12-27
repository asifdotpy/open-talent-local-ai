#!/bin/bash

# OpenTalent Platform - Backup Script
# Backs up PostgreSQL, Redis, and MinIO data

set -e

BACKUP_DIR="${BACKUP_DIR:-/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

echo "🔄 OpenTalent Platform Backup - $TIMESTAMP"
echo "========================================"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"/{postgres,redis,minio}

# PostgreSQL backup
echo "📦 Backing up PostgreSQL..."
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
    -h "${POSTGRES_HOST:-postgres}" \
    -p "${POSTGRES_PORT:-5432}" \
    -U "${POSTGRES_USER:-OpenTalent}" \
    -d "${POSTGRES_DB:-OpenTalent}" \
    -F c \
    -f "$BACKUP_DIR/postgres/OpenTalent_$TIMESTAMP.dump"

if [ -f "$BACKUP_DIR/postgres/OpenTalent_$TIMESTAMP.dump" ]; then
    gzip "$BACKUP_DIR/postgres/OpenTalent_$TIMESTAMP.dump"
    echo "  ✅ PostgreSQL backup: OpenTalent_$TIMESTAMP.dump.gz"
else
    echo "  ❌ PostgreSQL backup failed"
fi

# Redis backup
echo "📦 Backing up Redis..."
redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" \
    -a "$REDIS_PASSWORD" --no-auth-warning SAVE

if docker cp OpenTalent-redis:/data/dump.rdb "$BACKUP_DIR/redis/dump_$TIMESTAMP.rdb" 2>/dev/null; then
    gzip "$BACKUP_DIR/redis/dump_$TIMESTAMP.rdb"
    echo "  ✅ Redis backup: dump_$TIMESTAMP.rdb.gz"
else
    echo "  ⚠️  Redis backup skipped (no data or error)"
fi

# MinIO backup (copy bucket data)
echo "📦 Backing up MinIO..."
if docker cp OpenTalent-minio:/data "$BACKUP_DIR/minio/data_$TIMESTAMP" 2>/dev/null; then
    tar -czf "$BACKUP_DIR/minio/data_$TIMESTAMP.tar.gz" -C "$BACKUP_DIR/minio" "data_$TIMESTAMP"
    rm -rf "$BACKUP_DIR/minio/data_$TIMESTAMP"
    echo "  ✅ MinIO backup: data_$TIMESTAMP.tar.gz"
else
    echo "  ⚠️  MinIO backup skipped (no data or error)"
fi

# Clean up old backups
echo "🧹 Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -type f -name "*.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -type f -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Backup summary
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo ""
echo "✅ Backup complete!"
echo "   Total backup size: $TOTAL_SIZE"
echo "   Location: $BACKUP_DIR"
