# Wallet API

REST-сервис управления балансами кошельков с корректной обработкой конкурентных запросов.

[![CI](https://github.com)](https://github.com/pakvakunchik/wallet-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688)
![License](https://img.shields.io/badge/license-MIT-green)

## О проекте

Сервис позволяет пополнять и списывать средства с кошелька. Ключевая особенность — безопасная обработка параллельных операций через `SELECT ... FOR UPDATE` на уровне PostgreSQL: даже при десятках одновременных запросов баланс остаётся консистентным, а списание никогда не уводит баланс в минус.

## Стек

- Python 3.12
- FastAPI + Pydantic v2
- SQLAlchemy 2.0 (async, `asyncpg`)
- PostgreSQL 16
- Alembic (миграции)
- Docker + Docker Compose
- Pytest + `pytest-asyncio` + `httpx`
- Ruff (линтер)

## Быстрый запуск (Docker)

```bash
git clone https://github.com/USERNAME/wallet-api.git
cd wallet-api
cp .env.example .env
docker compose up --build
```
## Сервис доступен:

### API: http://localhost:8000

### Swagger: http://localhost:8000/docs

### Health: http://localhost:8000/health

### POST `/api/v1/wallets`

Создать новый кошелёк.

**Request:**
```json
{
  "balance": "0.00"
}
balance опционален, по умолчанию 0.00. Должен быть ≥ 0.


Запуск локально
bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

### поднять PostgreSQL (можно через docker)
docker compose up -d db

cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
API
POST /api/v1/wallets/{wallet_uuid}/operation
Пополнение или списание.

Request:

json
{
  "operation_type": "DEPOSIT",
  "amount": "100.50"
}
operation_type: DEPOSIT | WITHDRAW. amount — положительное число.

Response 200:

json
{
  "wallet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": "100.50"
}
Ошибки:

404 — кошелёк не найден

400 — недостаточно средств

422 — невалидный запрос (amount ≤ 0, неизвестный тип операции)

GET /api/v1/wallets/{wallet_uuid}
Получить баланс.

Response 200: то же, что выше.

app/
├── main.py                 # точка входа, lifespan, health
├── config.py               # pydantic-settings
├── database.py             # engine, session, get_db
├── models.py               # SQLAlchemy-модель Wallet
├── schemas.py              # Pydantic-схемы
├── repository/
│   └── wallet_repository.py # SELECT ... FOR UPDATE
├── services/
│   └── wallet_services.py  # бизнес-логика операций
└── routers/
    └── wallets.py          # HTTP-эндпоинты
migrations/                 # Alembic
tests/                      # pytest

Слои разделены по принципу: router → service → repository. Router отвечает только за HTTP, service — за бизнес-правила, repository — за SQL.

Конкурентность
Операции над одним кошельком сериализуются через SELECT ... FOR UPDATE:

python
stmt = select(Wallet).where(Wallet.id == wallet_id).with_for_update()
Это блокирует строку на время транзакции, поэтому 10 одновременных депозитов по 10.00 на баланс 100.00 дадут ровно 200.00. Тест test_concurrent_operations это проверяет.

Тесты
bash
#### локально (нужен PostgreSQL)
docker compose up -d db
TEST_DATABASE_URL=postgresql+asyncpg://wallet_user:wallet_pass@localhost:5432/wallet_test_db pytest

#### в docker
docker compose exec app pytest
Покрытие:

успешный депозит / списание

недостаточно средств

кошелёк не найден

конкурентные депозиты (10 параллельных)

конкурентные списания (баланс не уходит в минус)