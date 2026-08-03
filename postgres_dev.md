docker run --name ozon_tracker_postgres_dev -e POSTGRES_PASSWORD=ozon_tracker -p 5431:5432 -v postgres-data:/var/lib/postgresql/18/data -d postgres:18.4


Временный redis: docker run -d --rm --name ozon_tracker_redis_test -p 6379:6379 redis:alpine. Остановить: docker stop ozon_tracker_redis_test.

После настройки моделей и Alembic вы сможете создавать и применять миграции:
- Создание миграции: alembic revision --autogenerate -m "Init db"
- Применение к БД: alembic upgrade head
