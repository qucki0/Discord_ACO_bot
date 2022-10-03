import os
from typing import Literal

import discord
from discord import app_commands

from additions.all_data import actual_mints, all_mints, config
from additions.autocomplete import release_id_autocomplete
from additions.checkers import admin_checker
from functions.mints import get_mint_by_id, add_mint_to_mints_list


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
