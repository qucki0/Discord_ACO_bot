from classes.classes import ACOMember


class Transaction:
    def __init__(self, member: ACOMember = None, transaction_hash: str = None, amount: float = None,
                 timestamp: int = None, input_dict: dict = None) -> None:
        if input_dict is None:
            self.member_id = member.id
            self.member_name = member.name
            self.hash = transaction_hash
            self.amount = amount
            self.timestamp = timestamp
        else:
            self.member_id = int(input_dict["member_id"])
            self.member_name = input_dict["member_name"]
            self.hash = input_dict["hash"]
            self.amount = float(input_dict["amount"])
            self.timestamp = int(input_dict["timestamp"])

    def get_as_dict(self) -> dict:
        data = {"member_id": self.member_id,
                "member_name": self.member_name,
                "hash": self.hash,
                "amount": self.amount,
                "timestamp": self.timestamp
                }
        return data
