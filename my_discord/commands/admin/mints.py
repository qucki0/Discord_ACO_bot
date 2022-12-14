from typing import Literal

import discord
from discord import app_commands

from base_classes.mint import add_mint_to_mints_list, get_mint_by_name, get_all_mints, Chains
from my_discord.autocomplete import release_id_autocomplete
from my_discord.checkers import admin_checker
from setup import config
from utilities.files import delete_mint_files
from utilities.logging import get_logger

logger = get_logger(__name__)
__all__ = ["AdminMints"]


@app_commands.guild_only()
class AdminMints(app_commands.Group):
    @app_commands.command(name="add", description="ADMIN COMMAND Add mint to mints list")
    @app_commands.check(admin_checker)
    @app_commands.describe(release_name="Mint name",
                           wallets_limit="Limit of wallets we can handle",
                           link="Mint link",
                           timestamp="Drop timestamp")
    async def add_mint(self, interaction: discord.Interaction, release_name: str, wallets_limit: int, link: str = None,
                       timestamp: int = None, chain: Literal[Chains.tuple()] = "sol") -> None:
        await add_mint_to_mints_list(interaction, release_name, link, timestamp, wallets_limit, chain)

    @app_commands.command(name="change-info", description="ADMIN COMMAND Change mint [id, link, time or wallets limit]")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_name=release_id_autocomplete)
    @app_commands.describe(release_name="Mint name from /admin-mints get-all-mints-list or /mints get-all",
                           change_type="Change type",
                           new_value="Value that will be set. For wallet limit type + or"
                                     " - than amount you want to add/delete. Example: +10 or -5")
    async def change_mint_info(self, interaction: discord.Interaction, release_name: str,
                               change_type: Literal["name", "link", "timestamp", "wallets limit"],
                               new_value: str) -> None:
        change_type = change_type.strip()
        new_value = new_value.strip()
        mint = await get_mint_by_name(release_name)
        match change_type:
            case "name" | "link" | "timestamp":
                mint.__setattr__(change_type, new_value)
            case "wallets limit":
                amount = int(new_value)
                if mint.wallets_limit + amount < 0:
                    await interaction.response.send_message(f"You can reduce wallets limit"
                                                            f" no more than {mint.wallets_limit}",
                                                            ephemeral=True)
                    return
                mint.wallets_limit += amount
        await interaction.client.get_channel(config.ids.channels.alert_channel_id).send("Something changed, check it!",
                                                                                        embed=mint.get_as_embed())
        await interaction.response.send_message(f"Successfully changed {change_type} to {new_value}",
                                                ephemeral=True)

    @app_commands.command(name="get-all-mints-list", description="ADMIN COMMAND Get all mints")
    @app_commands.check(admin_checker)
    async def get_mints_list(self, interaction: discord.Interaction) -> None:
        data_to_send = '```\n'
        all_mints = await get_all_mints()
        for mint in all_mints:
            data_to_send += f"{mint.name}\n"
        data_to_send += "```"
        await interaction.response.send_message(data_to_send)

    @app_commands.command(name="delete", description="ADMIN COMMAND Delete mint from mints list")
    @app_commands.check(admin_checker)
    @app_commands.autocomplete(release_name=release_id_autocomplete)
    @app_commands.describe(release_name="Mint name only from /mints get-all")
    async def delete_mint(self, interaction: discord.Interaction, release_name: str) -> None:
        mint = await get_mint_by_name(release_name)
        delete_mint_files(mint.name)
        mint.valid = False
        await interaction.response.send_message(f"Deleted `{release_name}` from drop list!", ephemeral=True)
