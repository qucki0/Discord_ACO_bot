import discord

from additions.all_data import config
from classes.classes import Mint, Wallet
from functions import sql_commands
from functions.blockchain import is_hash_length_correct
from functions.other import get_wallets_from_string


async def add_mint_to_mints_list(interaction: discord.Interaction, release_name: str, link: str, timestamp: int,
                                 wallets_limit: int = 10) -> None:
    if check_mint_exist(release_name):
        await interaction.response.send_message(f"{release_name} already exist!", ephemeral=True)
    else:
        mint = Mint(name=release_name, link=link, timestamp=timestamp, wallets_limit=wallets_limit)
        await interaction.client.get_channel(config.alert_channel_id).send("New mint found", embed=mint.get_as_embed())
        await interaction.response.send_message(f"Added `{release_name}` to drop list!", ephemeral=True)


def check_mint_exist(release_name: str) -> bool:
    return sql_commands.check_exist.mint(mint_name=release_name)


def get_mint_by_name(release_name: str) -> Mint | None:
    return sql_commands.get.mint(mint_name=release_name)


def get_unpaid_mints() -> dict[str: list[int, int]]:
    unpaid_checkouts = sql_commands.get.unpaid_checkouts()
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
        if sql_commands.check_exist.wallet(wallet):
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
                             sql_commands.get.member_wallets_for_mint(member_id, mint.id)]
    else:
        wallets_to_delete = get_wallets_from_string(wallets_to_delete)
    for wallet in wallets_to_delete:
        if sql_commands.check_exist.wallet(wallet):
            sql_commands.delete.wallet(wallet)
            deleted_wallets += 1
    mint.wallets_limit += deleted_wallets
    return deleted_wallets
