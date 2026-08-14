# Wallet API

Сервис управления балансами кошельков с конкурентной обработкой запросов.

## Стек
- Python 3.12, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16
- Docker, docker-compose, Alembic, Pytest

## Быстрый запуск
```bash
docker-compose up --build

После запуска:

API: http://localhost:8000

Swagger: http://localhost:8000/docs

Эндпоинты
POST /api/v1/wallets/{wallet_uuid}/operation
Пополнение или снятие средств.

Тело:

json
{ "operation_type": "DEPOSIT", "amount": 1000.50 }
или

json
{ "operation_type": "WITHDRAW", "amount": 500.00 }
Ответ:

json
{ "wallet_id": "uuid", "balance": "1500.50" }
GET /api/v1/wallets/{wallet_uuid}
Получение текущего баланса.

Ответ: аналогичный.

Тестирование
bash
docker-compose exec app pytest
Конкурентность
Используется SELECT ... FOR UPDATE на уровне БД – гарантирует корректность при параллельных запросах к одному кошельку.

Структура
app/models.py – модели SQLAlchemy

app/schemas.py – Pydantic-схемы

app/repository/ – работа с БД (блокировки)

app/services/ – бизнес-логика

app/routers/ – эндпоинты

app/database.py – подключение к БД

migrations/ – Alembic-миграции

tests/ – тесты

Переменные окружения
В .env или через environment в compose:

text
BASE_URL_DB=postgresql+asyncpg://user:pass@host:port/db
Разработка (без Docker)
bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
Лицензия
MIT