import discord
from discord import app_commands

from base_classes.member import add_member
from base_classes.mint import get_mint_by_name
from base_classes.wallet import delete_wallets_from_mint, get_member_wallets_for_mint
from my_discord.autocomplete import release_id_autocomplete
from my_discord.views import SendWalletsView

__all__ = ["Wallets"]


@app_commands.guild_only()
class Wallets(app_commands.Group):
    @app_commands.command(name="send", description="Send wallets separated by spaces for chosen release")
    @app_commands.autocomplete(release_name=release_id_autocomplete)
    @app_commands.describe(release_name="Release name from /mints get-all")
    @discord.app_commands.rename(release_name="release_name")
    async def send_wallets(self, interaction: discord.Interaction, release_name: str) -> None:
        member_id = interaction.user.id
        add_member(interaction.user)

        mint = get_mint_by_name(release_name)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as `{release_name}`")
            return
        view = SendWalletsView(interaction, member_id, mint)
        await interaction.response.send_message(f"Send your wallets for `{mint.name}` using button below:", view=view)

    @app_commands.command(name="check", description="Check the wallets that you sent")
    @app_commands.autocomplete(release_name=release_id_autocomplete)
    @app_commands.describe(release_name="Release name from /mints get-all")
    @discord.app_commands.rename(release_name="release_name")
    async def check_wallets(self, interaction: discord.Interaction, release_name: str) -> None:
        await interaction.response.defer()
        mint = get_mint_by_name(release_name)
        if mint is None:
            await interaction.edit_original_response(content=f"There are no releases named as {release_name}")
            return

        member_id = interaction.user.id
        member_name = interaction.user.name

        messages_to_send = [f"{member_name} wallets for `{mint.name}`:\n```\n"]
        member_wallets = get_member_wallets_for_mint(member_id, mint.id)
        if not member_wallets:
            await interaction.edit_original_response(content=messages_to_send[0] + "Nothing\n```\n")
            return

        for i, wallet in enumerate(member_wallets):
            if i % 15 == 0 and i != 0:
                messages_to_send.append("```\n")
            messages_to_send[i // 15] += f"{wallet.private_key}\n"
            if i % 15 == 14:
                messages_to_send[i // 15] += "```"
        if messages_to_send[-1][-3:] != "```":
            messages_to_send[-1] += "```"

        await interaction.edit_original_response(content=messages_to_send[0])
        for i in range(1, len(messages_to_send)):
            await interaction.client.get_channel(interaction.channel_id).send(content=messages_to_send[i])

    @app_commands.command(name="delete",
                          description='Delete wallets separated by spaces for chosen release, "all" for all')
    @app_commands.autocomplete(release_name=release_id_autocomplete)
    @app_commands.describe(release_name="Release name from /mints get-all",
                           wallets='Private keys that you want to delete. Use "all" for select all wallets')
    @discord.app_commands.rename(release_name="release_name", wallets="private_keys")
    async def delete_wallets(self, interaction: discord.Interaction, release_name: str, wallets: str) -> None:
        mint = get_mint_by_name(release_name)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_name}")
            return

        member_id = interaction.user.id
        member_wallets = get_member_wallets_for_mint(member_id, mint.id)
        if not member_wallets:
            await interaction.response.send_message(f"First you need to send wallets!")
            return

        deleted_wallets = delete_wallets_from_mint(wallets, mint, member_id)
        await interaction.response.send_message(
            f"Successfully deleted {deleted_wallets} wallets")
