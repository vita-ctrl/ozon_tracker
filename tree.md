ozon_tracker/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── backend/
    ├── Dockerfile
    ├── alembic.ini
    ├── alembic/
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    ├── pyproject.toml
    └── src/
        ├── __init__.py
        ├── main.py                 # Точка входа (FastAPI + lifespan для aiogram и APScheduler)
        ├── core/
        │   ├── __init__.py
        │   ├── config.py           # Pydantic Settings (чтение переменных окружения)
        │   └── database.py         # Подключение SQLModel/SQLAlchemy (async engine, session)
        ├── models/
        │   ├── __init__.py
        │   ├── user.py             # SQLModel таблица пользователей
        │   ├── product.py          # SQLModel таблица товаров
        │   └── price_history.py    # SQLModel таблица истории цен
        ├── schemas/
        │   ├── __init__.py
        │   ├── user.py             # Pydantic схемы для пользователей
        │   └── product.py          # Pydantic схемы для запросов/ответов по товарам
        ├── api/
        │   ├── __init__.py
        │   ├── deps.py             # Зависимости FastAPI (текущая сессия БД, валидация initData)
        │   └── v1/
        │       ├── __init__.py
        │       ├── router.py       # Главный роутер API v1
        │       ├── auth.py         # Проверка HMAC initData от Telegram
        │       └── products.py     # CRUD эндпоинты для товаров и графиков
        ├── bot/
        │   ├── __init__.py
        │   ├── bot.py              # Инициализация Bot и Dispatcher
        │   ├── handlers/
        │   │   ├── __init__.py
        │   │   └── start.py        # Команда /start и кнопка открытия Mini App
        │   └── keyboards/
        │       ├── __init__.py
        │       └── main.py         # Клавиатуры с WebApp-кнопкой
        ├── services/
        │   ├── __init__.py
        │   ├── parser.py           # Парсинг данных товара с Ozon
        │   ├── scheduler.py        # APScheduler для периодической проверки цен
        │   └── notifications.py    # Логика отправки алертов в Telegram
        └── tests/
            ├── __init__.py
            ├── conftest.py         # Фикстуры pytest (тестовая БД, тестовый клиент)
            ├── test_api.py         # Тесты на API и авторизацию
            └── test_parser.py      # Тесты на парсер
