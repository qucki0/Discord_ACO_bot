import json
import os

import discord

import config
from additions.all_data import actual_mints, aco_members, all_mints
from additions.classes import ACOMember, Drop


def check_admin(member_id):
    return member_id in config.ADMINS_IDS


def get_mint_by_id(release_name):
    return get_data_by_id_from_list(release_name, actual_mints)


def get_data_by_id_from_list(data_to_find, array_to_check):
    data_to_find = str(data_to_find).strip().lower()
    for element in array_to_check:
        if str(element.id).lower() == data_to_find:
            return element


def add_member(member: discord.Member):
    if not any(member.id == aco_member.id for aco_member in aco_members):
        aco_members.append(ACOMember(member))


def get_member_name_by_id(member_id):
    for member in aco_members:
        if member.id == member_id:
            return member.name


def get_list_for_backup(arr):
    data = []
    for a in arr:
        data.append(a.get_as_dict())
    return data


async def add_mint_to_mints_list(interaction: discord.Interaction, release_id, link, timestamp, wallets_limit=10):
    if check_mint_exist(release_id):
        await interaction.response.send_message(f"{release_id} already exist!", ephemeral=True)
    else:
        mint = Drop(release_id, link, timestamp, wallets_limit)
        actual_mints.append(mint)
        all_mints.append(mint)
        await interaction.client.get_channel(config.ALERT_CHANNEL_ID).send("New mint found", embed=mint.get_as_embed())
        await interaction.response.send_message(f"Added `{release_id}` to drop list!", ephemeral=True)


def check_mint_exist(release_id):
    return any(release_id.lower().strip() == drop.id.lower() for drop in all_mints)


def save_json(arr, filename):
    with open(os.path.join("data", filename), "w") as file:
        file.write(json.dumps(get_list_for_backup(arr), sort_keys=True, indent=4))
