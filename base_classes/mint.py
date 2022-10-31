import discord

import sql.commands
from base_classes.base import PropertyModel
from base_classes.wallet import Wallet
from blockchains.solana.functions import is_hash_length_correct
from setup import config
from utilities.strings import get_wallets_from_string


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

        if not sql.commands.check_exist.mint(mint_name=self.name):
            sql.commands.add.mint(self)
        self.id = sql.commands.get.mint_id_by_name(self.name)

    def get_as_embed(self) -> discord.Embed:
        from my_discord import embeds
        return embeds.mint_data(self)

    def update_data(self, **kwargs):
        sql.commands.update.mint(self.id, **kwargs)

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


async def add_mint_to_mints_list(interaction: discord.Interaction, release_name: str, link: str, timestamp: int,
                                 wallets_limit: int = 10) -> None:
    if is_mint_exist(mint_name=release_name):
        await interaction.response.send_message(f"{release_name} already exist!", ephemeral=True)
    else:
        mint = Mint(name=release_name, link=link, timestamp=timestamp, wallets_limit=wallets_limit)
        await interaction.client.get_channel(config.alert_channel_id).send("New mint found", embed=mint.get_as_embed())
        await interaction.response.send_message(f"Added `{release_name}` to drop list!", ephemeral=True)


def is_mint_exist(mint_id=None, mint_name=None) -> bool:
    return sql.commands.check_exist.mint(mint_id=mint_id, mint_name=mint_name)


def get_mint_by_name(release_name: str) -> Mint | None:
    if not is_mint_exist(release_name):
        return None
    return sql.commands.get.mint(mint_name=release_name)


def get_unpaid_mints() -> dict[str: list[int, int]]:
    unpaid_checkouts = sql.commands.get.unpaid_checkouts()
    data = {}
    for payment in unpaid_checkouts:
        if payment.mint_name not in data:
            data[payment.mint_name] = []
        data[payment.mint_name].append([payment.member_id, payment.amount_of_checkouts])
    return data


def add_wallets_to_mint(wallets_to_add: list[str], mint: Mint, member_id: int) -> tuple[list[str], list[str], int]:
    not_private_keys = []
    already_exist_keys = []
    added_wallets = 0
    for wallet in wallets_to_add:
        if not is_hash_length_correct(wallet):
            not_private_keys.append(wallet)
            continue
        if sql.commands.check_exist.wallet(wallet):
            already_exist_keys.append(wallet)
            continue
        Wallet(private_key=wallet, mint_id=mint.id, member_id=member_id)
        added_wallets += 1
    mint.wallets_limit -= added_wallets
    return not_private_keys, already_exist_keys, added_wallets


def delete_wallets_from_mint(wallets_to_delete: str, mint: Mint, member_id: int) -> int:
    deleted_wallets = 0
    if wallets_to_delete.lower().strip() == "all":
        wallets_to_delete = [wallet.private_key for wallet in
                             sql.commands.get.member_wallets_for_mint(member_id, mint.id)]
    else:
        wallets_to_delete = get_wallets_from_string(wallets_to_delete)
    for wallet in wallets_to_delete:
        if sql.commands.check_exist.wallet(wallet):
            sql.commands.delete.wallet(wallet)
            deleted_wallets += 1
    mint.wallets_limit += deleted_wallets
    return deleted_wallets


def get_all_mints() -> list[Mint]:
    return sql.commands.get.all_mints()


def get_wallets_for_mint(mint_data: int | str) -> list[Wallet]:
    return sql.commands.get.wallets_for_mint(mint_data)


def get_actual_mints() -> list[Mint]:
    return sql.commands.get.actual_mints()


def get_member_wallets_for_mint(member_id: int, mint_id: int) -> list[Wallet]:
    return sql.commands.get.member_wallets_for_mint(member_id, mint_id)
