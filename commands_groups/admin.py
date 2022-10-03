import os
import time
from typing import Literal

import discord
from discord import app_commands

from additions import embeds
from additions.all_data import actual_mints, aco_members, all_mints, config
from additions.autocomplete import release_id_autocomplete
from additions.checkers import admin_checker, owner_checker
from additions.functions import get_mint_by_id, get_data_by_id_from_list, add_member, \
    get_member_name_by_id, add_mint_to_mints_list, do_backup, create_csv_from_dict


@app_commands.guild_only()
class AdminMints(app_commands.Group):
    @app_commands.command(name="add", description="ADMIN COMMAND Add mint to mints list")
    @app_commands.check(admin_checker)
    @app_commands.describe(release_id="Mint name",
                           wallets_limit="Limit of wallets we can handle",
                           link="Mint link",
                           timestamp="Drop timestamp")
    async def add_mint(self, interaction: discord.Interaction, release_id: str, wallets_limit: int, link: str = None,
                       timestamp: str = None):
        await add_mint_to_mints_list(interaction, release_id, link, timestamp, wallets_limit)

    @app_commands.command(name="change-info", description="ADMIN COMMAND Change mint [id, link, time or wallets limit]")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_id=release_id_autocomplete)
    @app_commands.describe(release_id="Mint name from /admin-mints get-all-mints-list or /mints get-all",
                           change_type="Change type",
                           new_value="Value that will be set. For wallet limit type + or"
                                     " - than amount you want to add/delete. Example: +10 or -5")
    async def change_mint_info(self, interaction: discord.Interaction, release_id: str,
                               change_type: Literal["id", "link", "time", "wallets limit"], new_value: str):
        change_type = change_type.lower().strip()
        new_value = new_value.lower().strip()

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
        if change_type == "wallets limit":
            amount = int(new_value)
            if mint.wallets_limit + amount < 0:
                await interaction.response.send_message(f"You can reduce wallets limit"
                                                        f" no more than {mint.wallets_limit}", ephemeral=True)
                return
            mint.wallets_limit += amount
        await interaction.client.get_channel(config.alert_channel_id).send("Something changed, check it!",
                                                                           embed=mint.get_as_embed())
        await interaction.response.send_message(f"Successfully changed {change_type} to {new_value}",
                                                ephemeral=True)

    @app_commands.command(name="get-all-mints-list", description="ADMIN COMMAND Get all mints")
    @app_commands.check(admin_checker)
    async def get_mints_list(self, interaction: discord.Interaction):
        data_to_send = '```\n'
        for mint in all_mints:
            data_to_send += f"{mint.id}\n"
        data_to_send += "```"
        await interaction.response.send_message(data_to_send)

    @app_commands.command(name="delete", description="ADMIN COMMAND Delete mint from mints list")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_id=release_id_autocomplete)
    @app_commands.describe(release_id="Mint name only from /mints get-all")
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


@app_commands.guild_only()
class AdminWallets(app_commands.Group):
    @app_commands.command(name="get-all", description="ADMIN COMMAND Get all wallets for specific release")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_id=release_id_autocomplete)
    @app_commands.describe(release_id="Mint name only from /mints get-all")
    async def get_wallets(self, interaction: discord.Interaction, release_id: str):
        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return
        base_wallets_dir = "wallets_to_send"
        wallets = ""
        wallets_as_dict = []
        another_wallets_as_dict = []
        for member_id in mint.wallets:
            for i, wallet in enumerate(mint.wallets[member_id], 1):
                wallets += f"{get_member_name_by_id(member_id)}{i}:{wallet}\n"
                wallets_as_dict.append({"ALIAS": f"{get_member_name_by_id(member_id)}{i}",
                                        "PRIVATE_KEY": wallet})
                another_wallets_as_dict.append({"Name": f"{get_member_name_by_id(member_id)}{i}",
                                                "Private Key": wallet,
                                                "Public Key": ""})
        if not os.path.exists(base_wallets_dir):
            os.mkdir(base_wallets_dir)
        timestamp = int(time.time())
        txt_file_name = os.path.join(base_wallets_dir, f"{release_id}{timestamp}UR.txt")
        csv_file_name = os.path.join(base_wallets_dir, f"{release_id}{timestamp}PP.csv")
        another_csv_file_name = os.path.join(base_wallets_dir, f"{release_id}{timestamp}MS.csv")
        with open(txt_file_name, "w") as file:
            file.write(wallets)
        create_csv_from_dict(csv_file_name, wallets_as_dict)
        create_csv_from_dict(another_csv_file_name, another_wallets_as_dict)
        time.sleep(1)
        await interaction.response.send_message(files=[discord.File(txt_file_name), discord.File(csv_file_name),
                                                       discord.File(another_csv_file_name)])


@app_commands.guild_only()
class AdminPayments(app_commands.Group):
    @app_commands.command(name="add-success", description="ADMIN COMMAND Add success to chosen release for chosen user")
    @app_commands.check(admin_checker)
    @app_commands.describe(release_id="Mint name from /admin-mints get-all-mints-list or /mints get-all",
                           amount="amount of checkouts")
    async def add_success(self, interaction: discord.Interaction, release_id: str, amount: int, user: discord.Member):
        mint = get_data_by_id_from_list(release_id, all_mints)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return
        member = get_data_by_id_from_list(user.id, aco_members)
        if member is None:
            add_member(user)
        member = get_data_by_id_from_list(user.id, aco_members)
        if mint.id not in member.payments:
            member.payments[mint.id] = {"amount_of_checkouts": amount,
                                        "unpaid_amount": amount}
        else:
            member.payments[mint.id]["amount_of_checkouts"] += amount
            member.payments[mint.id]["unpaid_amount"] += amount
        mint.checkouts += amount
        await interaction.response.send_message(f"Added {amount} checkouts", ephemeral=True)
        await interaction.client.get_channel(interaction.channel_id).send(
            embed=embeds.success(user.name, release_id, member.payments[mint.id]["amount_of_checkouts"]))

    @app_commands.command(name="check-payments", description="Command to check your unpaid successes")
    @app_commands.check(admin_checker)
    async def check_payments(self, interaction: discord.Interaction, user: discord.Member):
        member = get_data_by_id_from_list(user.id, aco_members)
        await interaction.response.send_message(embed=embeds.unpaid_successes(member))


@app_commands.guild_only()
class Admin(app_commands.Group):
    @app_commands.command(name="backup", description="ADMIN COMMAND just doing backup")
    @app_commands.check(admin_checker)
    async def backup(self, interaction: discord.Interaction):
        await do_backup(interaction, skip_timestamp=True)
        await interaction.response.send_message(f"Backup successful, check <#{config.backup_channel_id}>")

    @app_commands.command(name="add", description="ADMIN COMMAND add member to admins list")
    @app_commands.check(owner_checker)
    @app_commands.describe(user="User that will receive admin role")
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        config.admins.append(user.id)
        await interaction.response.send_message(f"Added {user.name} to admins list")

    @app_commands.command(name="delete", description="ADMIN COMMAND add member to admins list")
    @app_commands.check(owner_checker)
    @app_commands.describe(user="User that will lose admin role")
    async def delete(self, interaction: discord.Interaction, user: discord.Member):
        if user.id not in config.admins:
            await interaction.response.send_message(f"{user.name} is not admin", ephemeral=True)
        config.admins.remove(user.id)
        await interaction.response.send_message(f"Deleted {user.name} from admins list", ephemeral=True)
