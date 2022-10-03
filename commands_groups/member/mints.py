import discord
from discord import app_commands

from additions.all_data import actual_mints, config
from functions.members import check_admin
from functions.mints import add_mint_to_mints_list, check_mint_exist


@app_commands.guild_only()
class Mints(app_commands.Group):
    @app_commands.command(name="get-all", description="Get actual mints")
    async def get_mints(self, interaction: discord.Interaction):
        data_to_send = [mint.get_as_embed() for mint in actual_mints]
        message_to_send = "**Let us know if we lost something. Just use `/mints request` for it!**"
        await interaction.response.send_message(message_to_send, embeds=data_to_send[:min(10, len(data_to_send))])
        for i in range(1, len(data_to_send) // 10 + 1):
            await interaction.client.get_channel(interaction.channel_id).send(
                embeds=data_to_send[10 * i:min(10 * (i + 1), len(data_to_send))])

    @app_commands.command(name="request", description="Create request to add mint")
    @app_commands.describe(release_id="Name of release you want to request",
                           link="Link for mint page if you got",
                           mint_time="Mint timestamp you can use https://www.epochconverter.com/ for it")
    async def request_mint(self, interaction: discord.Interaction, release_id: str, link: str = None,
                           mint_time: str = None):
        admins_to_ping = ""
        if check_mint_exist(release_id):
            await interaction.response.send_message(f"`{release_id}` already exist!", ephemeral=True)
            return
        for admin_id in config.admins:
            admins_to_ping += "<@" + str(admin_id) + "> "
        accept_button = discord.ui.Button(label="Accept", style=discord.ButtonStyle.green)
        reject_button = discord.ui.Button(label="Reject", style=discord.ButtonStyle.red)

        async def accept_response(accept_interaction: discord.Interaction):
            if not check_admin(accept_interaction.user.id):
                await accept_interaction.response.send_message(
                    "You do not have enough permissions to do perform this operation.", ephemeral=True)
                return
            await add_mint_to_mints_list(accept_interaction, release_id, link, mint_time)
            await interaction.delete_original_response()
            await accept_interaction.client.get_channel(accept_interaction.channel_id).send(
                f":green_circle:Request for {release_id} Accepted")

        async def reject_response(reject_interaction: discord.Interaction):
            if not check_admin(reject_interaction.user.id):
                await reject_interaction.response.send_message(
                    "You do not have enough permissions to do perform this operation.", ephemeral=True)
                return
            await interaction.delete_original_response()
            await reject_interaction.client.get_channel(reject_interaction.channel_id).send(
                ":red_circle:Request Rejected")

        accept_button.callback = accept_response
        reject_button.callback = reject_response
        view = discord.ui.View(timeout=None)
        view.add_item(accept_button)
        view.add_item(reject_button)

        await interaction.response.send_message(
            f"{admins_to_ping}, please add `{release_id}`, link:`{link}`, time: `{mint_time}`", view=view)
