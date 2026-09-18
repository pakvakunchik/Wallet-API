import asyncio
from decimal import Decimal
from uuid import uuid4

from httpx import AsyncClient

from app.database import async_session
from app.models import Wallet


async def create_wallet(wallet_id, balance: Decimal = Decimal("0.00")):
    async with async_session() as session:
        session.add(Wallet(id=wallet_id, balance=balance))
        await session.commit()


async def test_deposit(client: AsyncClient, db_session):
    wallet_id = uuid4()
    db_session.add(Wallet(id=wallet_id, balance=Decimal("0.00")))
    await db_session.commit()

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.50"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_id"] == str(wallet_id)
    assert Decimal(data["balance"]) == Decimal("100.50")


async def test_concurrent_withdrawals_never_go_negative(client: AsyncClient, db_session):
    wallet_id = uuid4()
    db_session.add(Wallet(id=wallet_id, balance=Decimal("100.00")))
    await db_session.commit()

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


async def test_withdraw(client: AsyncClient):
    wallet_id = uuid4()
    await create_wallet(client, wallet_id, Decimal("200.00"))
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


async def test_concurrent_operations(client: AsyncClient):
    import asyncio

    wallet_id = uuid4()
    await create_wallet(client, wallet_id, Decimal("100.00"))

    async def deposit():
        return await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "10.00"},
        )

    tasks = [deposit() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in results)
    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("200.00")  # 100 + 10*10


async def test_wallet_not_found(client: AsyncClient):
    wallet_id = uuid4()
    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 404
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "10.00"},
    )
    assert response.status_code == 404
