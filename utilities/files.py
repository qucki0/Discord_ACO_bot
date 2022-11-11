import asyncio
import csv
import os

import discord

from utilities.encryption import encrypt_string


def delete_mint_files(mint_name: str) -> None:
    mint_name = mint_name.lower()
    if not os.path.exists("wallets_to_send"):
        return
    for file_name in os.listdir("wallets_to_send"):
        if file_name[:len(mint_name)] == mint_name:
            os.remove(os.path.join("wallets_to_send", file_name))


async def auto_backup(client: discord.Client) -> None:
    from setup import config
    while not client.is_closed():
        await asyncio.sleep(config.seconds_between_backups)
        await create_backup(client.get_channel(config.backup_channel_id))


async def create_backup(channel_to_send: discord.TextChannel) -> None:
    from sql.client import SqlClient
    sql_client = SqlClient()
    if not os.path.exists('./backups'):
        os.mkdir('backups')
    data = ""
    tables = [t[f"Tables_in_{sql_client.db_name}"] for t in (await sql_client.execute_query("SHOW TABLES"))]
    for table in tables:
        data += f"DROP TABLE IF EXISTS `{table}`;"

        response = await sql_client.execute_query(f"SHOW CREATE TABLE `{table}`;")
        data += f'\n{response[0]["Create Table"]};\n\n'

        rows = await sql_client.select_data(table)
        for row in rows:
            keys = ", ".join(row.keys())
            values = "', '".join([str(row[key]) for key in row])
            data += f"INSERT INTO `{table}`({keys}) VALUES('{values}');\n"
        data += "\n\n"

    path_to_file = os.path.join("backups", f"backup.sql")
    with open(path_to_file, "w", encoding="utf-8") as file:
        file.write(encrypt_string(data))
    await channel_to_send.send(file=discord.File(path_to_file))


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
