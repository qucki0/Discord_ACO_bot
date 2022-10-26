import discord

from additions.all_data import actual_mints, all_mints, config, aco_members
from classes.classes import Mint
from functions.blockchain import is_hash_length_correct
from functions.other import get_data_by_id_from_list, get_wallets_from_string


async def add_mint_to_mints_list(interaction: discord.Interaction, release_id: str, link: str, timestamp: int,
                                 wallets_limit: int = 10) -> None:
    if check_mint_exist(release_id):
        await interaction.response.send_message(f"{release_id} already exist!", ephemeral=True)
    else:
        mint = Mint(release_id, link, timestamp, wallets_limit)
        actual_mints.append(mint)
        all_mints.append(mint)
        await interaction.client.get_channel(config.alert_channel_id).send("New mint found", embed=mint.get_as_embed())
        await interaction.response.send_message(f"Added `{release_id}` to drop list!", ephemeral=True)


def check_mint_exist(release_id: str) -> bool:
    return any(release_id.lower().strip() == drop.id.lower() for drop in all_mints)


def get_mint_by_id(release_id: str) -> Mint | None:
    return get_data_by_id_from_list(release_id, actual_mints)


def get_unpaid_mints() -> dict[str: list[int, int]]:
    data = {}
    for member in aco_members:
        for release_id in member.payments:
            if unpaid_amount := member.payments[release_id]["unpaid_amount"]:
                if release_id not in data:
                    data[release_id] = []
                data[release_id].append([member.id, unpaid_amount])
    return data


def add_wallets_to_mint(wallets_to_add: list[str], mint: Mint, member_id: int) -> tuple[list[str], list[str], int]:
    if member_id not in mint.wallets:
        mint.wallets[member_id] = set()

    member_wallets = mint.get_wallets_by_id(member_id)
    wallets_before_adding = len(member_wallets)
    not_private_keys = []
    already_exist_keys = []

    for wallet in wallets_to_add:
        if not is_hash_length_correct(wallet):
            not_private_keys.append(wallet)
            continue
        if wallet in member_wallets:
            already_exist_keys.append(wallet)
            continue
        member_wallets.add(wallet)

    added_wallets = len(member_wallets) - wallets_before_adding
    mint.wallets_limit -= added_wallets
    return not_private_keys, already_exist_keys, added_wallets


def delete_wallets_from_mint(wallets_to_delete: str, mint: Mint, member_id: int) -> int:
    member_wallets = mint.get_wallets_by_id(member_id)
    wallets_len_before_deleting = len(member_wallets)
    if wallets_to_delete.lower().strip() == "all":
        member_wallets.clear()
    else:
        wallets_to_delete = get_wallets_from_string(wallets_to_delete)
        for wallet in wallets_to_delete:
            member_wallets.discard(wallet)
    deleted_wallets = wallets_len_before_deleting - len(member_wallets)
    mint.wallets_limit += deleted_wallets
    return deleted_wallets
