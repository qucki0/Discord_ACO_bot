import csv
import os
import time

import discord
from discord import app_commands

import config
from additions.all_data import actual_mints, aco_members, all_mints
from additions.functions import check_admin, get_mint_by_id, save_json, get_data_by_id_from_list, add_member, \
    get_member_name_by_id, add_mint_to_mints_list


class AdminMints(app_commands.Group):
    @app_commands.command(name="add", description="ADMIN COMMAND Add mint to mints list")
    async def add_mint(self, interaction: discord.Interaction, release_id: str, link: str = None,
                       timestamp: str = None):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        await add_mint_to_mints_list(interaction, release_id, link, timestamp)

    @app_commands.command(name="change-info", description="ADMIN COMMAND Change mint [id, link or time]")
    async def change_mint_info(self, interaction: discord.Interaction, release_id: str, change_type: str,
                               new_value: str):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return

        change_type = change_type.lower().strip()
        new_value = new_value.lower().strip()
        if change_type not in ["id", "link", "time"]:
            await interaction.response.send_message("Invalid change type!", ephemeral=True)
            return

        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return

        if change_type == "id":
            mint.id = new_value
        if change_type == "link":
            mint.link = new_value
        if change_type == "time":
            mint.timestamp = new_value
        await interaction.client.get_channel(config.ALERT_CHANNEL_ID).send("Something changed, check it!",
                                                                           embed=mint.get_as_embed())
        await interaction.response.send_message(f"Successfully changed {change_type} to {new_value}",
                                                ephemeral=True)

    @app_commands.command(name="get-all-mints-list", description="ADMIN COMMAND Get all mints")
    async def get_mints_list(self, interaction: discord.Interaction):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        data_to_send = '```'
        for mint in all_mints:
            data_to_send += f"{mint.id}\n"
        data_to_send += "```"
        await interaction.response.send_message(data_to_send)

    @app_commands.command(name="delete", description="ADMIN COMMAND Delete mint from mints list")
    async def delete_mint(self, interaction: discord.Interaction, release_id: str):
        for i in range(len(actual_mints)):
            mint_name = actual_mints[i].id
            if release_id.lower().strip() == mint_name.lower():
                for file_name in os.listdir("wallets_to_send"):
                    if file_name[:len(mint_name)] == mint_name:
                        os.remove(os.path.join("wallets_to_send", file_name))
                actual_mints.pop(i)
                await interaction.response.send_message(f"Deleted `{release_id}` from drop list!", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"There are no releases named as {release_id}", ephemeral=True)


class AdminWallets(app_commands.Group):
    @app_commands.command(name="get-all", description="ADMIN COMMAND Get all wallets for specific release")
    async def get_wallets(self, interaction: discord.Interaction, release_id: str):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return

        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return

        wallets = ""
        wallets_as_dict = []
        for member_id in mint.wallets:
            for i, wallet in enumerate(mint.wallets[member_id], 1):
                wallets += f"{get_member_name_by_id(member_id)}{i}:{wallet}\n"
                wallets_as_dict.append({"ALIAS": f"{get_member_name_by_id(member_id)}{i}",
                                        "PRIVATE_KEY": wallet})

        timestamp = int(time.time())
        txt_file_name = os.path.join("wallets_to_send", f"{release_id}{timestamp}.txt")
        csv_file_name = os.path.join("wallets_to_send", f"{release_id}{timestamp}.csv")
        with open(txt_file_name, "w") as file:
            file.write(wallets)
        with open(csv_file_name, "w", newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=wallets_as_dict[0].keys())
            csv_writer.writeheader()
            csv_writer.writerows(wallets_as_dict)
        time.sleep(1)
        await interaction.response.send_message(files=[discord.File(txt_file_name), discord.File(csv_file_name)])


class AdminPayment(app_commands.Group):
    @app_commands.command(name="add-success", description="ADMIN COMMAND Add success to chosen release for chosen user")
    async def add_success(self, interaction: discord.Interaction, release_name: str, amount: int, user: discord.Member):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        mint = get_data_by_id_from_list(release_name, all_mints)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_name}")
            return
        member = get_data_by_id_from_list(user.id, aco_members)
        if member is None:
            add_member(user)
        member = get_data_by_id_from_list(user.id, aco_members)
        if mint.id not in member.payments:
            member.payments[mint.id] = {"amount_of_checkouts": amount,
                                        "paid": False}
        else:
            member.payments[mint.id]["amount_of_checkouts"] += amount
        mint.checkouts += amount
        await interaction.response.send_message(f"Added {amount} checkouts")


class Admin(app_commands.Group):
    @app_commands.command(name="backup", description="ADMIN COMMAND just doing backup")
    async def backup(self, interaction: discord.Interaction):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        files = [(actual_mints, "actual_mints.json"), (aco_members, "aco_members.json"), (all_mints, "all_mints.json")]
        for file in files:
            save_json(*file)
        await interaction.response.send_message(files=[discord.File(os.path.join("data", file[1])) for file in files])
