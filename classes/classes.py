import discord
from pydantic import BaseModel


class PropertyModel(BaseModel):
    def __setattr__(self, key, val):
        method = self.__config__.property_set_methods.get(key)
        if method is None:
            super().__setattr__(key, val)
        else:
            getattr(self, method)(val)

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        new_data = {}
        for key in data:
            if key.endswith("_"):
                new_key = key[::-1].replace("_", "", 1)[::-1]
                new_data[new_key] = data[key]
            else:
                new_data[key] = data[key]
        return new_data


class Mint(PropertyModel):
    id: int = None
    name_: str
    wallets_limit_: int
    timestamp_: int = None
    link_: str = None
    checkouts_: int = 0
    valid_: bool = True

    def __init__(self, **data):
        super().__init__(**data)
        from functions import sql_commands
        if not sql_commands.check_exist.mint(mint_name=self.name):
            sql_commands.add.mint(self)
        self.id = sql_commands.get.mint_id_by_name(self.name)

    def get_as_embed(self) -> discord.Embed:
        from additions import embeds
        return embeds.mint_data(self)

    def update_data(self, **kwargs):
        from functions import sql_commands
        sql_commands.update.mint(self.id, **kwargs)

    @property
    def name(self):
        return self.name_

    @name.setter
    def name(self, value):
        pass

    def set_name(self, value):
        self.update_data(name=value)
        self.name_ = value

    @property
    def wallets_limit(self):
        return self.wallets_limit_

    @wallets_limit.setter
    def wallets_limit(self, value):
        pass

    def set_wallets_limit(self, value):
        self.update_data(wallets_limit=value)
        self.wallets_limit_ = value

    @property
    def timestamp(self):
        return self.timestamp_

    @timestamp.setter
    def timestamp(self, value):
        pass

    def set_timestamp(self, value):
        self.update_data(timestamp=value)
        self.timestamp_ = value

    @property
    def link(self):
        return self.link_

    @link.setter
    def link(self, value):
        pass

    def set_link(self, value):
        self.update_data(link=value)
        self.link_ = value

    @property
    def checkouts(self):
        return self.checkouts_

    @checkouts.setter
    def checkouts(self, value):
        pass

    def set_checkouts(self, value):
        self.update_data(checkouts=value)
        self.checkouts_ = value

    @property
    def valid(self):
        return self.valid_

    @valid.setter
    def valid(self, value):
        pass

    def set_valid(self, value):
        self.update_data(valid=value)
        self.valid_ = value

    class Config:
        attributes_to_change = ["name", "wallets_limit", "timestamp", "link", "checkouts", "valid"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


class ACOMember(PropertyModel):
    id: int
    name_: str
    ticket_id_: int = None

    def __init__(self, **data):
        super().__init__(**data)
        from functions import sql_commands
        if not sql_commands.check_exist.member(self.id):
            sql_commands.add.member(self)

    def update_data(self, **kwargs):
        from functions import sql_commands
        sql_commands.update.mint(self.id, **kwargs)

    @property
    def ticket_id(self):
        return self.ticket_id_

    @ticket_id.setter
    def ticket_id(self, value):
        pass

    def set_ticket_id(self, value):
        self.update_data(ticket_id=value)
        self.ticket_id_ = value

    @property
    def name(self):
        return self.name_

    @name.setter
    def name(self, value):
        pass

    def set_name(self, value):
        self.update_data(name=value)
        self.name_ = value

    class Config:
        attributes_to_change = ["ticket_id", "name"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


class Wallet(PropertyModel):
    private_key: str
    mint_id: int
    member_id: int

    def __init__(self, **data):
        super().__init__(**data)
        from functions import sql_commands
        if not sql_commands.check_exist.wallet(self.private_key):
            sql_commands.add.wallet(self)


class Payment(PropertyModel):
    mint_id: int
    mint_name: str
    member_id: int
    amount_of_checkouts_: int

    def __init__(self, **data):
        super().__init__(**data)
        from functions import sql_commands
        if not sql_commands.check_exist.payment(self.mint_id, self.member_id):
            sql_commands.add.payment(self)

    def update_data(self, **kwargs):
        from functions import sql_commands
        sql_commands.update.payment(self.mint_id, self.member_id, **kwargs)

    @property
    def amount_of_checkouts(self):
        return self.amount_of_checkouts_

    @amount_of_checkouts.setter
    def amount_of_checkouts(self, value):
        pass

    def set_amount_of_checkouts(self, value):
        self.update_data(amount_of_checkouts=value)
        self.amount_of_checkouts_ = value

    class Config:
        attributes_to_change = ["amount_of_checkouts"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


class SqlData(BaseModel):
    user: str
    password: str
    db_name: str
    host: str
    port: int


class Config(BaseModel):
    token: str
    admins: list[int]
    owners: list[int]
    alert_channel_id: int
    seconds_between_backups: int
    backup_channel_id: int
    wallet_manager_link: str
    rpc_link: str
    payment_wallet: str
    closed_category_id: int
    notifications_channel_id: int
    sql_data: SqlData
