from pydantic import BaseModel

import sql.commands
from base_classes.base import AsyncObject
from base_classes.errors import PaymentNotExist


class Transaction(BaseModel, AsyncObject):
    member_id: int
    hash: str
    amount: float
    timestamp: int

    async def __ainit__(self, *args, **kwargs):
        if not await is_transaction_exist(self.hash):
            await create_transaction(self)


async def create_transaction(transaction: Transaction) -> None:
    await sql.commands.add.transaction(transaction.dict())


async def is_transaction_exist(tx_hash: str) -> bool:
    return await sql.commands.check_exist.transaction(tx_hash)


async def get_transaction(tx_hash: str) -> Transaction | None:
    if not await is_transaction_exist(tx_hash):
        raise PaymentNotExist
    return Transaction.parse_obj(await sql.commands.get.transaction(tx_hash))


async def get_all_transactions() -> list[Transaction]:
    return [Transaction.parse_obj(d) for d in await sql.commands.get.all_transactions()]
