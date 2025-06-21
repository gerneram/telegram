stop:
	@echo "🛑 Остановка и сохранение бэкапа..."
	@./backup.sh
	@docker compose down

start:
	@echo "🚀 Запуск контейнеров и восстановление из бэкапа (если нужно)..."
	@docker compose build
	@docker compose up -d

logs:
	@docker compose logs -f
