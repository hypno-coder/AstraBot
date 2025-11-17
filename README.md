
# Технологический стек
- **Python 3.10+ / 3.11** — основной язык проектов бота и воркера.
- **Aiogram 3** и **Aiogram-Dialog** — реализация бота и сценариев общения с пользователем.
- **FastStream** и **nats-py** — асинхронный воркер, получающий задания через NATS JetStream.
- **PostgreSQL 17** — основная база данных.
- **SQLAlchemy** и **Alembic** — ORM-уровень и миграции базы.
- **Dynaconf** и **Pydantic** — конфигурации и валидация настроек.
- **Structlog** — структурированное логирование.
- **Pillow** — нанесение водяных знаков во воркере изображений.
- **Docker Compose** — запуск всех сервисов и инфраструктуры.

# Создание миграции  + строка для CITEXT

## 1) Создать пустую ревизию для сидов (данные)
Выполните команду (используются те же переменные подключения, что и для схемы):
```bash
docker compose run --rm \
  -e APP_CONF__DB__DB_TYPE=postgresql \
  -e APP_CONF__DB__ADAPTER=asyncpg \
  -e APP_CONF__DB__DB_NAME=bot \
  -e APP_CONF__DB__USERNAME=username \
  -e APP_CONF__DB__PASSWORD=password \
  -e APP_CONF__DB__HOST=postgres:5432 \
  app poetry run alembic revision --autogenerate -m "init"
```

после этого в созданую миграцию дописываем строку которая нужна для корректной работы
поля email из за citext. в функцию upgrade(), перед строкой op.create_table() вставляем строку
op.execute("CREATE EXTENSION IF NOT EXISTS citext")

## 2) Установка новых моделей:
```Bash
docker compose run --rm \
  -e APP_CONF__DB__DB_TYPE=postgresql \
  -e APP_CONF__DB__ADAPTER=asyncpg \
  -e APP_CONF__DB__DB_NAME=bot \
  -e APP_CONF__DB__USERNAME=username \
  -e APP_CONF__DB__PASSWORD=password \
  -e APP_CONF__DB__HOST=postgres:5432 \
  app poetry run alembic upgrade head
```
## 3) Проверка таблиц
```bash
docker compose exec postgres psql -U username -d bot -c "\dt"
docker compose exec postgres psql -U username -d bot -c "\d+ users"
docker compose exec postgres psql -U username -d bot -c "\d+ products"
docker compose exec postgres psql -U username -d bot -c "\d+ purchases"

```
## 4) Проверка установки CITEXT
```bash
docker compose exec postgres psql -U username -d bot -c "\dx"
```


## 5) Запуск через Docker Compose
1. **Поднимите инфраструктуру (PostgreSQL и NATS с ресурсами JetStream):**
   ```bash
   docker compose --profile infrastructure up -d
   ```
   Профиль запускает сервисы `postgres`, `nats` и одноразовый контейнер `nats-migrate`, подготавливающий хранилища NATS.

2. **Примените миграции базы данных (при первом запуске или изменении моделей):**
   ```bash
   docker compose run --rm \
     -e APP_CONF_SETTINGS_FILES=/app/settings.toml,/app/.secrets.toml \
     app poetry run alembic upgrade head
   ```
   Команда стартует временный контейнер `app`, загружает конфигурацию Dynaconf и запускает Alembic.

3. **Запустите бота и воркер:**
   ```bash
   docker compose --profile all up --build
   ```
   Профиль `all` поднимет `app` (Telegram-бот) и `worker` (обработчик изображений) вместе с инфраструктурой. Для фонового запуска добавьте флаг `-d`.

4. Остановить и удалить запущенные сервисы можно командой:
   ```bash
   docker compose down
