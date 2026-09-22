import asyncio
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient
from app.models import Wallet


async def test_create_wallet(client: AsyncClient):
    response = await client.post(
        "/api/v1/wallets",
        json={"balance": "0.00"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "wallet_id" in data
    assert Decimal(data["balance"]) == Decimal("0.00")


async def test_create_wallet_with_initial_balance(client: AsyncClient):
    response = await client.post(
        "/api/v1/wallets",
        json={"balance": "100.00"},
    )
    assert response.status_code == 201
    assert Decimal(response.json()["balance"]) == Decimal("100.00")


async def test_deposit(client: AsyncClient):
    create_resp = await client.post("/api/v1/wallets", json={"balance": "0.00"})
    wallet_id = create_resp.json()["wallet_id"]

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.50"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_id"] == wallet_id
    assert Decimal(data["balance"]) == Decimal("100.50")
    get_resp = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert get_resp.status_code == 200
    assert Decimal(get_resp.json()["balance"]) == Decimal("100.50")


async def test_withdraw(client: AsyncClient):
    create_resp = await client.post("/api/v1/wallets", json={"balance": "200.00"})
    wallet_id = create_resp.json()["wallet_id"]

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "50.00"},
    )
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("150.00")

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "200.00"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"


async def test_wallet_not_found(client: AsyncClient):
    wallet_id = uuid4()
    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 404
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "10.00"},
    )
    assert response.status_code == 404


async def test_invalid_amount(client: AsyncClient):
    create_resp = await client.post("/api/v1/wallets", json={"balance": "10.00"})
    wallet_id = create_resp.json()["wallet_id"]

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "0"},
    )
    assert response.status_code == 422  # gt=0 в схеме

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "-5.00"},
    )
    assert response.status_code == 422


async def test_concurrent_operations(client: AsyncClient):
    create_resp = await client.post("/api/v1/wallets", json={"balance": "100.00"})
    wallet_id = create_resp.json()["wallet_id"]

    async def deposit():
        return await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "10.00"},
        )

    results = await asyncio.gather(*[deposit() for _ in range(10)])
    assert all(r.status_code == 200 for r in results)

    final = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert Decimal(final.json()["balance"]) == Decimal("200.00")  # 100 + 10*10


async def test_concurrent_withdrawals_never_go_negative(client: AsyncClient):
    create_resp = await client.post("/api/v1/wallets", json={"balance": "100.00"})
    wallet_id = create_resp.json()["wallet_id"]

    async def withdraw():
        return await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": "30.00"},
        )

    results = await asyncio.gather(*[withdraw() for _ in range(5)])
    successful = [r for r in results if r.status_code == 200]
    failed = [r for r in results if r.status_code == 400]

    assert len(successful) == 3
    assert len(failed) == 2

    final = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert Decimal(final.json()["balance"]) == Decimal("10.00")