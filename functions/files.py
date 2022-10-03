import csv
import json
import os
import time

import discord

from additions.all_data import config, backup_data
from functions.encryption import encrypt_string


def save_json(arr, filename):
    with open(os.path.join("data", filename), "w", encoding="utf-8") as file:
        file.write(encrypt_string(json.dumps(get_list_for_backup(arr), sort_keys=True)))


def get_list_for_backup(arr):
    return [a.get_as_dict() for a in arr]


async def do_backup(interaction: discord.Interaction, skip_timestamp=False):
    try:  # phantom error found, trying to figure it out
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
    except TypeError as ex:
        print(ex)
        for file in backup_data.files_to_backup:
            print(get_list_for_backup(file[0]))


def create_csv_from_dict(file_path, data_dict):
    with open(file_path, "w", newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=data_dict[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(data_dict)
