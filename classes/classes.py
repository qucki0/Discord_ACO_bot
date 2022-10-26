import discord
from pydantic import BaseModel


class Mint(BaseModel):
    name: str
    wallets_limit: int
    timestamp: int = None
    link: str = None
    checkouts: int = 0

    def get_as_embed(self) -> discord.Embed:
        from additions import embeds
        return embeds.mint_data(self)


class ACOMember(BaseModel):
    id: int
    name: str
    ticket_id: int = None


class Wallet(BaseModel):
    private_key: str
    mint_id: int
    member_id: int


class Payment(BaseModel):
    mint_id: int
    member_id: int
    amount_of_checkouts: int


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
