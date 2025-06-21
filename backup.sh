#!/bin/bash

echo "📦 Создание бэкапа PostgreSQL..."

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=./backup
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"
LATEST_BACKUP="$BACKUP_DIR/backup_latest.sql"

mkdir -p "$BACKUP_DIR"

# Исправлено имя контейнера!
docker exec project-db-1 pg_dump -U shopuser shopdb > "$BACKUP_FILE"

# Также обновим latest
cp "$BACKUP_FILE" "$LATEST_BACKUP"

echo "✅ Бэкап сохранён в $BACKUP_FILE"
