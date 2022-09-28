import json
import os
import time

import discord

from additions.all_data import actual_mints, aco_members, all_mints, config, backup_data
from additions.classes import ACOMember, Drop


def check_admin(member_id):
    return member_id in config.admins


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
    return [a.get_as_dict() for a in arr]


async def add_mint_to_mints_list(interaction: discord.Interaction, release_id, link, timestamp, wallets_limit=10):
    if check_mint_exist(release_id):
        await interaction.response.send_message(f"{release_id} already exist!", ephemeral=True)
    else:
        mint = Drop(release_id, link, timestamp, wallets_limit)
        actual_mints.append(mint)
        all_mints.append(mint)
        await interaction.client.get_channel(config.alert_channel_id).send("New mint found", embed=mint.get_as_embed())
        await interaction.response.send_message(f"Added `{release_id}` to drop list!", ephemeral=True)


def check_mint_exist(release_id):
    return any(release_id.lower().strip() == drop.id.lower() for drop in all_mints)


def save_json(arr, filename):
    with open(os.path.join("data", filename), "w") as file:
        file.write(json.dumps(get_list_for_backup(arr), sort_keys=True, indent=4))


async def do_backup(interaction: discord.Interaction, skip_timestamp=False):
    if backup_data.last_backup_timestamp + config.seconds_between_backups > time.time() and not skip_timestamp:
        return
    if not os.path.exists("data"):
        os.mkdir("data")
    files_to_send = []
    for file in backup_data.files_to_backup:
        save_json(*file)
        files_to_send.append(discord.File(os.path.join("data", file[1])))
    await interaction.client.get_channel(config.backup_channel_id).send(files=files_to_send)
    backup_data.last_backup_timestamp = int(time.time())
