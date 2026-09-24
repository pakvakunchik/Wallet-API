# Wallet API

REST-сервис управления балансами кошельков с корректной обработкой конкурентных запросов.

[![CI](https://github.com/pakvakunchik/wallet-api/actions/workflows/ci.yml/badge.svg)](https://github.com/pakvakunchik/wallet-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688)
![License](https://img.shields.io/badge/license-MIT-green)

## О проекте

Сервис позволяет создавать кошельки, пополнять и списывать средства.
Ключевая особенность — безопасная обработка параллельных операций через
`SELECT ... FOR UPDATE` на уровне PostgreSQL: даже при десятках
одновременных запросов баланс остаётся консистентным, а списание никогда
не уводит баланс в минус.

## Стек

- Python 3.12
- FastAPI + Pydantic v2
- SQLAlchemy 2.0 (async, asyncpg)
- PostgreSQL 16
- Alembic (миграции)
- Docker + Docker Compose
- Pytest + pytest-asyncio + httpx
- Ruff (линтер)

## Требования

- Docker Desktop (с WSL2 на Windows) **или** локальный PostgreSQL 16
- Python 3.12+ (если запускаете без Docker)

> ⚠️ Порт 5432 должен быть свободен — docker-compose публикует его на хост.
> Если у вас уже запущен локальный PostgreSQL, остановите его перед
> `docker compose up`.

## Быстрый запуск

```bash
git clone https://github.com/pakvakunchik/wallet-api.git
cd wallet-api
cp .env.example .env
docker compose up --build
```
### Сервис доступен:

API: http://localhost:8000

Swagger: http://localhost:8000/docs

Health: http://localhost:8000/health

### Запуск локально (без Docker для приложения)

python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

#### PostgreSQL (можно через docker)
docker compose up -d db

cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload

## API

POST /api/v1/wallets
Создать новый кошелёк.

Request:

json
{
  "balance": "0.00"
}
balance опционален, по умолчанию 0.00. Должен быть ≥ 0.

Response 201:

json
{
  "wallet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": "0.00"
}
POST /api/v1/wallets/{wallet_uuid}/operation
Пополнение или списание.

Request:

json
`{
  "operation_type": "DEPOSIT",
  "amount": "100.50"
}`
operation_type: DEPOSIT | WITHDRAW. amount — положительное число.

#### Response 200:

json
`{
  "wallet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": "100.50"
}`
#### Ошибки:

404 — кошелёк не найден

400 — недостаточно средств

422 — невалидный запрос (amount ≤ 0, неизвестный тип операции)

GET /api/v1/wallets/{wallet_uuid}
Получить текущий баланс.

Response 200: то же, что у операции.

GET /health
Healthcheck для Docker / K8s / LB.

Архитектура
app/
├── main.py                    # точка входа, lifespan, health
├── config.py                  # pydantic-settings
├── database.py                # engine, session, get_db
├── models.py                  # SQLAlchemy-модель Wallet
├── schemas.py                 # Pydantic-схемы
├── repository/
│   └── wallet_repository.py   # SELECT ... FOR UPDATE
├── services/
│   └── wallet_services.py     # бизнес-логика операций
└── routers/
    └── wallets.py             # HTTP-эндпоинты
migrations/                    # Alembic
tests/                         # pytest
Слои: router → service → repository. Router отвечает только за HTTP,
service — за бизнес-правила, repository — за SQL.

Конкурентность
Операции над одним кошельком сериализуются через SELECT ... FOR UPDATE: