import asyncio
import csv
import json
import os

import discord

from additions.all_data import config, backup_data
from functions.encryption import encrypt_string


def save_json(arr, filename):
    with open(os.path.join("data", filename), "w", encoding="utf-8") as file:
        file.write(encrypt_string(json.dumps(get_list_for_backup(arr), sort_keys=True)))


def get_list_for_backup(arr):
    return [a.get_as_dict() for a in arr]


async def auto_backup(client: discord.Client):
    while not client.is_closed():
        await asyncio.sleep(config.seconds_between_backups)
        await create_backup_files(client.get_channel(config.backup_channel_id))


async def create_backup_files(channel_to_send):
    try:  # phantom error found, trying to figure it out
        if not os.path.exists("data"):
            os.mkdir("data")

        files_to_send = []
        for file in backup_data.files_to_backup:
            save_json(*file)
            files_to_send.append(discord.File(os.path.join("data", file[1])))

        await channel_to_send.send(files=files_to_send)
    except TypeError as ex:
        print(ex)
        for file in backup_data.files_to_backup:
            print(get_list_for_backup(file[0]))


def create_csv_from_dict(file_path, data_dict):
    with open(file_path, "w", newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=data_dict[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(data_dict)
