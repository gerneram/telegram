echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.5
done

echo "Running migrations..."
python manage.py migrate

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "🚨 Создание суперпользователя Django..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin")
    print("✅ Суперпользователь создан: admin / admin")
else:
    print("ℹ️ Суперпользователь уже существует.")
END

echo "🚀 Starting Gunicorn..."
exec gunicorn shop_project.wsgi:application --bind 0.0.0.0:8000
