from dataclasses import dataclass

import discord
from pydantic import BaseModel

from additions import embeds


class Drop:
    def __init__(self, mint_id=None, link=None, timestamp=None, wallets_limit=None, json_file=None):
        if json_file is None:
            self.id = mint_id.strip()
            self.wallets_limit = wallets_limit
            self.timestamp = timestamp
            self.link = link
            self.wallets = {}
            self.checkouts = 0
        else:
            self.id = json_file["id"]
            self.wallets_limit = int(json_file["wallets_limit"])
            self.timestamp = json_file["timestamp"]
            self.link = json_file["link"]
            self.wallets = {int(key): set(json_file["wallets"][key]) for key in json_file["wallets"]}
            self.checkouts = int(json_file["checkouts"])

    def get_as_dict(self):
        data = {"id": self.id,
                "wallets_limit": self.wallets_limit,
                "timestamp": self.timestamp,
                "link": self.link,
                "wallets": {key: list(self.wallets[key]) for key in self.wallets},
                "checkouts": self.checkouts}
        return data

    def get_drop_data(self):
        data = ""
        data += f"**{self.id}** "
        if self.timestamp is not None:
            data += f"<t:{self.timestamp}> "
        if self.link is not None:
            data += f"{self.link.strip()}"
        return data

    def get_wallets_by_id(self, member_id):
        if member_id in self.wallets:
            return self.wallets[member_id]

    def get_as_embed(self):
        return embeds.mint_data(self.id, self.link, self.timestamp, self.wallets_limit)


class ACOMember:
    def __init__(self, member: discord.Member = None, json_file=None):
        if json_file is None:
            self.id = member.id
            self.name = member.name
            self.mints = {}
            self.payments = {}
        else:
            self.id = int(json_file["id"])
            self.name = json_file["name"]
            self.mints = json_file["mints"]
            self.payments = json_file["payments"]

    def get_as_dict(self):
        data = {"id": self.id,
                "name": self.name,
                "mints": self.mints,
                "payments": self.payments
                }
        return data


class Transaction:
    def __init__(self, member: discord.Member = None, transaction_hash=None, amount=None, timestamp=None,
                 json_file=None):
        if json_file is None:
            self.member_id = member.id
            self.member_name = member.name
            self.hash = transaction_hash
            self.amount = amount
            self.timestamp = timestamp
        else:
            self.member_id = int(json_file["member_id"])
            self.member_name = json_file["member_name"]
            self.hash = json_file["hash"]
            self.amount = json_file["amount"]
            self.timestamp = int(json_file["timestamp"])

    def get_as_dict(self):
        data = {"member_id": self.member_id,
                "member_name": self.member_name,
                "hash": self.hash,
                "amount": self.amount,
                "timestamp": self.timestamp
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


@dataclass
class BackupData:
    last_backup_timestamp: int
    files_to_backup: list[tuple[list, str]]
