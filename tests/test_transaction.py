import random
import time

import pytest
import pytest_asyncio

from base_classes.errors import TransactionNotExist
from base_classes.member import Member
from base_classes.transaction import Transaction, is_transaction_exist, get_transaction

VALID_TRANSACTION_HASH = "3AYcfZR7w4JbUnPNEouCn9P9xgMki72ozFPM16fCoWSYbuArjdfgP5ZVaij7bPx8ckeZX9FjJ2xWXorBXrNYbLb3"


@pytest_asyncio.fixture(scope="function")
async def member():
    member_name = f"member_name{random.randint(10 ** 0, 10 ** 20)}"
    m = await Member(id=random.randint(10 ** 0, 10 ** 18), name=member_name)
    yield m


class TestTransaction:
    @pytest.mark.asyncio
    async def test_create_transaction(self, member):
        await Transaction(member_id=member.id, hash=VALID_TRANSACTION_HASH, amount=1, timestamp=int(time.time()))
        assert await is_transaction_exist(VALID_TRANSACTION_HASH)

    @pytest.mark.asyncio
    async def test_get_transaction(self, member):
        amount = random.randint(1, 100)
        await Transaction(member_id=member.id, hash=VALID_TRANSACTION_HASH, amount=amount, timestamp=int(time.time()))
        transaction = await get_transaction(VALID_TRANSACTION_HASH)
        assert transaction.member_id == member.id
        assert transaction.hash == VALID_TRANSACTION_HASH
        assert transaction.amount == amount

    @pytest.mark.asyncio
    async def test_is_transaction_exist(self, member):
        assert not await is_transaction_exist(VALID_TRANSACTION_HASH)
        await Transaction(member_id=member.id, hash=VALID_TRANSACTION_HASH, amount=1, timestamp=int(time.time()))
        assert await is_transaction_exist(VALID_TRANSACTION_HASH)

    @pytest.mark.asyncio
    async def test_get_transaction_if_not_exist(self):
        with pytest.raises(TransactionNotExist):
            await get_transaction("some not exist hash")
