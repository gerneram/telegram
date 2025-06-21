set -e

echo "🛠 Восстановление базы из последнего бэкапа..."

LATEST_BACKUP=$(ls -t /docker-entrypoint-initdb.d/*.sql 2>/dev/null | head -n 1)

if [ -f "$LATEST_BACKUP" ]; then
    echo "⏳ Восстанавливаем из: $LATEST_BACKUP"
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$LATEST_BACKUP"
    echo "✅ Восстановление завершено"
else
    echo "❗️Бэкап не найден. Пропуск восстановления."
fi
