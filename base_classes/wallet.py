from base_classes.base import PropertyModel
import sql.commands


class Wallet(PropertyModel):
    private_key: str
    mint_id: int
    member_id: int

    def __init__(self, **data):
        super().__init__(**data)

        if not sql.commands.check_exist.wallet(self.private_key):
            sql.commands.add.wallet(self)
