from pydantic import BaseModel


class Transaction(BaseModel):
    member_id: int
    hash: str
    amount: float
    timestamp: int

    def __init__(self, **data):
        super().__init__(**data)
        from functions import sql_commands
        if not sql_commands.check_exist.transaction(self.hash):
            sql_commands.add.transaction(self)
