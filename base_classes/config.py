from pydantic import BaseModel


class SqlData(BaseModel):
    user: str
    password: str
    db_name: str
    host: str
    port: int


class MembersIDs(BaseModel):
    admins: list[int]
    owners: list[int]


class ChannelsIDs(BaseModel):
    backup_channel_id: int
    closed_category_id: int
    notifications_channel_id: int
    alert_channel_id: int


class IDs(BaseModel):
    members: MembersIDs
    channels: ChannelsIDs


class Blockchain(BaseModel):
    payment_wallet: str
    rpc_link: str


class Blockchains(BaseModel):
    solana: Blockchain


class ConfigClass(BaseModel):
    token: str
    seconds_between_backups: int
    ids: IDs
    blockchains: Blockchains
    sql_data: SqlData
    wallet_manager_link: str
