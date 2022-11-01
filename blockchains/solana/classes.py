from pydantic import BaseModel

import sql.commands


class Transaction(BaseModel):
    member_id: int
    hash: str
    amount: float
    timestamp: int

    def __init__(self, **data):
        super().__init__(**data)
        if not sql.commands.check_exist.transaction(self.hash):
            sql.commands.add.transaction(self.dict())


def is_transaction_exist(tx_hash: str) -> bool:
    return sql.commands.check_exist.transaction(tx_hash)


def get_transaction(tx_hash: str) -> Transaction | None:
    if not is_transaction_exist(tx_hash):
        return None
    return get_transaction(tx_hash)
