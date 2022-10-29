import discord
from discord import app_commands

from additions.all_data import config
from classes.discord_classes import RequestMintView
from functions import sql_commands
from functions.mints import check_mint_exist


@app_commands.guild_only()
class Mints(app_commands.Group):
    @app_commands.command(name="get-all", description="Get actual mints")
    async def get_mints(self, interaction: discord.Interaction) -> None:
        actual_mints = sql_commands.get.actual_mints()
        embeds_to_send = [mint.get_as_embed() for mint in actual_mints]
        message_to_send = "**Let us know if we lost something. Just use `/mints request` for it!**"
        await interaction.response.send_message(message_to_send, embeds=embeds_to_send[:min(10, len(embeds_to_send))])

        for i in range(1, len(embeds_to_send) // 10 + 1):
            await interaction.client.get_channel(interaction.channel_id).send(
                embeds=embeds_to_send[10 * i:min(10 * (i + 1), len(embeds_to_send))])

    @app_commands.command(name="request", description="Create request to add mint")
    @app_commands.describe(release_id="Name of release you want to request")
    @discord.app_commands.rename(release_id="release_name")
    async def request_mint(self, interaction: discord.Interaction, release_id: str) -> None:
        admins_to_ping = ""
        if check_mint_exist(release_id):
            await interaction.response.send_message(f"`{release_id}` already exist!", ephemeral=True)
            return
        for admin_id in config.admins:
            admins_to_ping += "<@" + str(admin_id) + "> "
        view = RequestMintView(interaction, release_id)

        await interaction.response.send_message(
            f"{admins_to_ping}, please add `{release_id}`", view=view)
