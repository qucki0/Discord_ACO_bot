from dataclasses import dataclass

import discord
from pydantic import BaseModel


class Drop:
    def __init__(self, mint_id: str = None, link: str = None, timestamp: int = None, wallets_limit: int = None,
                 input_dict: dict = None) -> None:
        if input_dict is None:
            self.id = mint_id.strip()
            self.wallets_limit = wallets_limit
            self.timestamp = timestamp
            self.link = link
            self.wallets = {}
            self.checkouts = 0
        else:
            self.id = input_dict["id"]
            self.wallets_limit = int(input_dict["wallets_limit"])
            self.timestamp = input_dict["timestamp"]
            self.link = input_dict["link"]
            self.wallets = {int(key): set(input_dict["wallets"][key]) for key in input_dict["wallets"]}
            self.checkouts = int(input_dict["checkouts"])

    def get_as_dict(self) -> dict:
        data = {"id": self.id,
                "wallets_limit": self.wallets_limit,
                "timestamp": self.timestamp,
                "link": self.link,
                "wallets": {key: list(self.wallets[key]) for key in self.wallets},
                "checkouts": self.checkouts}
        return data

    def get_wallets_by_id(self, member_id: int) -> set[str]:
        if member_id in self.wallets:
            return self.wallets[member_id]

    def get_as_embed(self) -> discord.Embed:
        from additions import embeds
        return embeds.mint_data(self)


class ACOMember:
    def __init__(self, member: discord.Member = None, input_dict: dict = None) -> None:
        if input_dict is None:
            self.id = member.id
            self.name = member.name
            self.mints = {}
            self.payments: dict[str, dict[str, int]] = {}
            self.ticket_id: int | None = None
        else:
            self.id = int(input_dict["id"])
            self.name = input_dict["name"]
            self.mints = input_dict["mints"]
            self.payments = input_dict["payments"]
            if "ticket_id" in input_dict:
                self.ticket_id = input_dict["ticket_id"]
                if self.ticket_id is not None:
                    self.ticket_id = int(self.ticket_id)
            else:
                self.ticket_id = None

    def get_as_dict(self) -> dict:
        data = {"id": self.id,
                "name": self.name,
                "mints": self.mints,
                "payments": self.payments,
                "ticket_id": self.ticket_id
                }
        return data


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


@dataclass
class BackupData:
    files_to_backup: list[tuple[list, str]]
