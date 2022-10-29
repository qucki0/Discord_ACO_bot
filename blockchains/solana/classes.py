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
            sql.commands.add.transaction(self)
