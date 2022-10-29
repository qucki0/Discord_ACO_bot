from pydantic import BaseModel


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
