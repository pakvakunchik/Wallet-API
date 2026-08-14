import pytest
from httpx import AsyncClient
from uuid import uuid4
from decimal import Decimal

async def create_wallet(client: AsyncClient, wallet_id: uuid4, balance: Decimal = Decimal('0.00')):
    from app.database import async_session
    from app.models import Wallet
    async with async_session() as session:
        wallet = Wallet(id=wallet_id, balance=balance)
        session.add(wallet)
        await session.commit()

@pytest.mark.asyncio
async def test_deposit(client: AsyncClient):
    wallet_id = uuid4()
    await create_wallet(client, wallet_id, Decimal('0.00'))
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.50"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_id"] == str(wallet_id)
    assert Decimal(data["balance"]) == Decimal("100.50")
    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("100.50")

@pytest.mark.asyncio
async def test_withdraw(client: AsyncClient):
    wallet_id = uuid4()
    await create_wallet(client, wallet_id, Decimal('200.00'))
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "50.00"}
    )
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("150.00")
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "200.00"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"

@pytest.mark.asyncio
async def test_concurrent_operations(client: AsyncClient):
    import asyncio
    wallet_id = uuid4()
    await create_wallet(client, wallet_id, Decimal('100.00'))
    async def deposit():
        return await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "10.00"}
        )
    tasks = [deposit() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in results)
    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("200.00")  # 100 + 10*10

@pytest.mark.asyncio
async def test_wallet_not_found(client: AsyncClient):
    wallet_id = uuid4()
    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 404
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "10.00"}
    )
    assert response.status_code == 404