import csv
import os
import time

import discord
from discord import app_commands

import config
from additions.all_data import mints_list, aco_members, payments
from additions.classes import Drop
from additions.functions import check_admin, get_mint_by_id, save_json, get_data_by_id_from_list, add_member


class Mints(app_commands.Group):

    @app_commands.command(name="add", description="Add mint to mints list")
    async def add_mint(self, interaction: discord.Interaction, drop_name: str, link: str = None, timestamp: str = None):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        if any(drop_name.lower().strip() == drop.id.lower() for drop in mints_list):
            await interaction.response.send_message(f"{drop_name} already exist!", ephemeral=True)
        else:
            mint = Drop(drop_name, timestamp, link)
            mints_list.append(mint)
            payments.append(mint)
            await interaction.client.get_channel(1019024498571350086).send("New mint found", embed=mint.get_as_embed())
            await interaction.response.send_message(f"Added `{drop_name}` to drop list!", ephemeral=True)

    @app_commands.command(name="get_all", description="Get actual mints")
    async def get_mints(self, interaction: discord.Interaction):
        data_to_send = [mint.get_as_embed() for mint in mints_list]
        message_to_send = "**Let us know if we lost something. Just use `/mints request` for it!**"
        await interaction.response.send_message(message_to_send, embeds=data_to_send[:min(10, len(data_to_send))])
        for i in range(1, len(data_to_send) // 10 + 1):
            await interaction.client.get_channel(interaction.channel_id).send(
                embeds=data_to_send[10 * i:min(10 * (i + 1), len(data_to_send))])

    @app_commands.command(name="change_info", description="Change mint [id, link or timestamp]")
    async def change_mint_info(self, interaction: discord.Interaction, mint_id: str, change_type: str,
                               new_value: str):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return

        change_type = change_type.lower().strip()
        new_value = new_value.lower().strip()
        if change_type not in ["id", "link", "timestamp"]:
            await interaction.response.send_message("Invalid change type!", ephemeral=True)
            return

        mint = get_mint_by_id(mint_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {mint_id}")
            return

        if change_type == "id":
            mint.id = new_value
        if change_type == "link":
            mint.link = new_value
        if change_type == "timestamp":
            mint.timestamp = new_value
        await interaction.client.get_channel(1019024498571350086).send("Something changed, check it!",
                                                                       embed=mint.get_as_embed())
        await interaction.response.send_message(f"Successfully changed {change_type} to {new_value}",
                                                ephemeral=True)

    @app_commands.command(name="request", description="Create request to add mint")
    async def request_mint(self, interaction: discord.Interaction, drop_name: str, link: str = None,
                           mint_time: str = None):
        admins_to_ping = ""
        for admin_id in config.ADMINS_IDS:
            admins_to_ping += "<@" + str(admin_id) + "> "
        await interaction.response.send_message(
            f"{admins_to_ping}, please add `{drop_name}`, link:`{link}`, time: `{mint_time}`")

    @app_commands.command(name="delete", description="Delete mint from mints list")
    async def delete_mint(self, interaction: discord.Interaction, drop_name: str):
        for i in range(len(mints_list)):
            mint_name = mints_list[i].id
            if drop_name.lower().strip() == mints_list[i].id.lower():
                for file_name in os.listdir("wallets_to_send"):
                    if file_name[:len(mint_name)] == mint_name:
                        os.remove(os.path.join("wallets_to_send", file_name))
                mints_list.pop(i)
                await interaction.response.send_message(f"Deleted `{drop_name}` from drop list!", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"There are no releases named as {drop_name}", ephemeral=True)


class Aco(app_commands.Group):
    @app_commands.command(name="send_wallets", description="Send wallets separated by commas for chosen release")
    async def send_wallets(self, interaction: discord.Interaction, release_name: str, wallets: str):
        member_id = interaction.user.id
        member = get_data_by_id_from_list(interaction.user.id, aco_members)
        if member is None:
            add_member(interaction.user)
        if not len(wallets):
            await interaction.response.send_message("Please input wallets keys")
            return

        wallets = [wallet.strip() for wallet in wallets.split(",")]

        mint = get_mint_by_id(release_name)
        if mint is not None:
            if member_id not in mint.wallets:
                mint.wallets[member_id] = []
            mint.wallets[member_id].extend(wallets)
            await interaction.response.send_message(f"Successfully sent {len(wallets)} wallets")
        else:
            await interaction.response.send_message(f"There are no releases named as {release_name}")

    @app_commands.command(name="check_wallets", description="Check the wallets that you sent")
    async def check_wallets(self, interaction: discord.Interaction, release_name: str):
        mint = get_mint_by_id(release_name)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_name}", ephemeral=True)
            return
        member_id = interaction.user.id
        member_name = interaction.user.name
        message_to_send = f"{member_name} wallets for `{mint.id}`:\n```\n"
        if member_id not in mint.wallets:
            await interaction.response.send_message(message_to_send + "Nothing\n```\n")
            return
        for wallet in mint.get_wallets_by_id(member_id):
            message_to_send += f"{wallet}\n"
        message_to_send += "```"
        await interaction.response.send_message(message_to_send)

    @app_commands.command(name="delete_wallets", description="Delete wallets separated by commas for chosen release")
    async def delete_wallets(self, interaction: discord.Interaction, release_name: str, wallets: str):
        mint = get_mint_by_id(release_name)
        member_id = interaction.user.id
        wallets_to_delete = [wallet.strip() for wallet in wallets.split(",")]
        counter = 0
        for wallet in reversed(mint.wallets[member_id]):
            if wallet in wallets_to_delete:
                mint.wallets[member_id].remove(wallet)
                counter += 1
        await interaction.response.send_message(f"Successfully deleted {counter} wallets")

    @app_commands.command(name="get_wallets", description="Get all wallets for specific release")
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
        for member in mint.wallets:
            for i, wallet in enumerate(mint.wallets[member], 1):
                wallets += f"{member}{i}:{wallet}\n"
                wallets_as_dict.append({"ALIAS": f"{member}{i}",
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


class Admin(app_commands.Group):
    @app_commands.command(name="backup", description="Just doing backup")
    async def backup(self, interaction: discord.Interaction):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        files = [(mints_list, "mints_list.json"), (aco_members, "aco_members.json"), (payments, "payments.json")]
        for file in files:
            save_json(*file)
        await interaction.response.send_message(
            files=[discord.File(file[1]) for file in files])


class Payment(app_commands.Group):
    @app_commands.command(name="add_success", description="Add success to chosen release for chosen user")
    async def add_success(self, interaction: discord.Interaction, release_name: str, amount: int, user: discord.Member):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message("Not enough rights to do it", ephemeral=True)
            return
        mint = get_data_by_id_from_list(release_name, payments)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_name}")
            return
        member = get_data_by_id_from_list(user.id, aco_members)
        if member is None:
            add_member(user)
        member = get_data_by_id_from_list(user.id, aco_members)
        if mint.id not in member.payments:
            member.payments[mint.id] = {"mint_id": mint.id,
                                        "amount_of_checkouts": amount,
                                        "paid": False}
        else:
            member.payments[mint.id]["amount_of_checkouts"] += amount
        mint.checkouts += amount
        await interaction.response.send_message(f"Added {amount} checkouts")

    @app_commands.command(name="pay", description="Add success to chosen release for chosen user")
    async def pay(self, interaction: discord.Interaction, release_name: str, amount_to_pay: float):
        button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.green)
        member_id = interaction.user.id

        async def first_response(first_interaction: discord.Interaction):
            admins_to_ping = ""
            for admin_id in config.ADMINS_IDS:
                admins_to_ping += "<@" + str(admin_id) + "> "
            button.callback = second_response
            await first_interaction.response.edit_message(content=f"{admins_to_ping}, check this payment.", view=view)

        async def second_response(second_interaction: discord.Interaction):
            if not check_admin(second_interaction.user.id):
                await second_interaction.response.send_message("Not enough rights to do it", ephemeral=True)
                return
            member = get_data_by_id_from_list(member_id, aco_members)
            member.payments[release_name]["paid"] = True
            await second_interaction.response.edit_message(
                content=f"Payment {amount_to_pay} $SOL for {release_name} successful", view=None)

        button.callback = first_response
        view = discord.ui.View(timeout=None)
        view.add_item(button)

        await interaction.response.send_message(
            f"Send {amount_to_pay} $SOL to `pay1L1NNvAgjgWiPQMR3G5RwSLcDLpPtbG2VGchZWEh` and click button below after "
            f"success",
            view=view)
