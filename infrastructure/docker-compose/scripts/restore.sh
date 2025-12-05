#!/bin/bash

# TalentAI Platform - Restore Script
# Restores PostgreSQL, Redis, and MinIO from backup

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo "Example: $0 20250109_120000"
    echo ""
    echo "Available backups:"
    ls -lh /backups/postgres/*.dump.gz 2>/dev/null | awk '{print "  " $9}'
    exit 1
fi

TIMESTAMP="$1"
BACKUP_DIR="${BACKUP_DIR:-/backups}"

echo "🔄 TalentAI Platform Restore - $TIMESTAMP"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will overwrite current data!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# PostgreSQL restore
POSTGRES_BACKUP="$BACKUP_DIR/postgres/talentai_$TIMESTAMP.dump.gz"
if [ -f "$POSTGRES_BACKUP" ]; then
    echo "📥 Restoring PostgreSQL from $POSTGRES_BACKUP..."
    gunzip -c "$POSTGRES_BACKUP" > /tmp/restore.dump
    
    PGPASSWORD="$POSTGRES_PASSWORD" pg_restore \
        -h "${POSTGRES_HOST:-postgres}" \
        -p "${POSTGRES_PORT:-5432}" \
        -U "${POSTGRES_USER:-talentai}" \
        -d "${POSTGRES_DB:-talentai}" \
        --clean \
        --if-exists \
        /tmp/restore.dump
    
    rm /tmp/restore.dump
    echo "  ✅ PostgreSQL restored"
else
    echo "  ⚠️  PostgreSQL backup not found: $POSTGRES_BACKUP"
fi

# Redis restore
REDIS_BACKUP="$BACKUP_DIR/redis/dump_$TIMESTAMP.rdb.gz"
if [ -f "$REDIS_BACKUP" ]; then
    echo "📥 Restoring Redis from $REDIS_BACKUP..."
    gunzip -c "$REDIS_BACKUP" > /tmp/dump.rdb
    docker cp /tmp/dump.rdb talentai-redis:/data/dump.rdb
    docker restart talentai-redis
    rm /tmp/dump.rdb
    echo "  ✅ Redis restored"
else
    echo "  ⚠️  Redis backup not found: $REDIS_BACKUP"
fi

# MinIO restore
MINIO_BACKUP="$BACKUP_DIR/minio/data_$TIMESTAMP.tar.gz"
if [ -f "$MINIO_BACKUP" ]; then
    echo "📥 Restoring MinIO from $MINIO_BACKUP..."
    mkdir -p /tmp/minio_restore
    tar -xzf "$MINIO_BACKUP" -C /tmp/minio_restore
    docker cp /tmp/minio_restore/data_$TIMESTAMP/. talentai-minio:/data/
    docker restart talentai-minio
    rm -rf /tmp/minio_restore
    echo "  ✅ MinIO restored"
else
    echo "  ⚠️  MinIO backup not found: $MINIO_BACKUP"
fi

echo ""
echo "✅ Restore complete!"
echo "   Timestamp: $TIMESTAMP"
