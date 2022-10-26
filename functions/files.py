import asyncio
import csv
import json
import os

import discord

from additions.all_data import config, backup_data
from classes.blockchain import Transaction
from classes.classes import Mint, ACOMember
from functions.encryption import encrypt_string


def save_json(arr: list[Mint | ACOMember | Transaction], filename: str) -> None:
    with open(os.path.join("data", filename), "w", encoding="utf-8") as file:
        file.write(encrypt_string(json.dumps(get_list_for_backup(arr), sort_keys=True)))


def get_list_for_backup(arr: list[Mint | ACOMember | Transaction]) -> list[dict]:
    return [a.get_as_dict() for a in arr]


async def auto_backup(client: discord.Client) -> None:
    while not client.is_closed():
        await asyncio.sleep(config.seconds_between_backups)
        await create_backup_files(client.get_channel(config.backup_channel_id))


async def create_backup_files(channel_to_send: discord.TextChannel) -> None:
    try:  # phantom error found, trying to figure it out
        if not os.path.exists("data"):
            os.mkdir("data")

        files_to_send = []
        for file in backup_data.files_to_backup:
            save_json(*file)
            path_to_file = os.path.join("data", file[1])
            files_to_send.append(discord.File(path_to_file))

        await channel_to_send.send(files=files_to_send)
    except TypeError as ex:
        print(ex)
        for file in backup_data.files_to_backup:
            print(get_list_for_backup(file[0]))


def delete_mint_files(mint_name: str) -> None:
    mint_name = mint_name.lower()
    if not os.path.exists("wallets_to_send"):
        return
    for file_name in os.listdir("wallets_to_send"):
        if file_name[:len(mint_name)] == mint_name:
            os.remove(os.path.join("wallets_to_send", file_name))


def create_wallets_files(wallets: list[tuple[str, str]], files: dict[str: str]) -> None:
    urban_file = open(files["urban"], "w")

    pepper_file = open(files["pepper"], "w")
    pepper_writer = csv.writer(pepper_file)
    pepper_writer.writerow(["ALIAS", "PRIVATE_KEY"])

    ms_file = open(files["minter_suite"], "w")
    ms_writer = csv.writer(ms_file)
    ms_writer.writerow(["Name", "Private Key", "Public Key"])
    for wallet_name, wallet_key in wallets:
        urban_file.write(f"{wallet_name}:{wallet_key}\n")
        pepper_writer.writerow([wallet_name, wallet_key])
        ms_writer.writerow([wallet_name, wallet_key, ""])

    urban_file.close()
    pepper_file.close()
    ms_file.close()
