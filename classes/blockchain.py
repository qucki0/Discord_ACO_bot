from pydantic import BaseModel


class Transaction(BaseModel):
    member_id: int
    hash: str
    amount: float
    timestamp: int
