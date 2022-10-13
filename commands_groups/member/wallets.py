import discord
from discord import app_commands

from additions.autocomplete import release_id_autocomplete
from functions.members import add_member, get_member_by_id
from functions.mints import get_mint_by_id, add_wallets_to_mint, delete_wallets_from_mint
from functions.other import get_wallets_from_string


@app_commands.guild_only()
class Wallets(app_commands.Group):
    @app_commands.command(name="send", description="Send wallets separated by spaces for chosen release")
    @app_commands.autocomplete(release_id=release_id_autocomplete)
    @app_commands.describe(release_id="Release name from /mints get-all",
                           wallets_str="Your wallets private keys separated by spaces")
    @discord.app_commands.rename(release_id="release_name", wallets_str="private_keys")
    async def send_wallets(self, interaction: discord.Interaction, release_id: str, wallets_str: str):
        member_id = interaction.user.id
        member = get_member_by_id(member_id)
        if member is None:
            add_member(interaction.user)
        wallets = get_wallets_from_string(wallets_str)

        if not len(wallets):
            await interaction.response.send_message("Please input wallets keys")
            return

        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return

        if mint.wallets_limit < len(wallets):
            await interaction.response.send_message(f"There are only {mint.wallets_limit} spots left for {mint.id}")
            return

        not_private_keys, already_exist_keys, added_wallets = add_wallets_to_mint(wallets, mint, member_id)

        response_message = f"Successfully sent {added_wallets} wallets. \n"
        if already_exist_keys:
            already_exist_string = '\n'.join(already_exist_keys)
            response_message += f"{len(already_exist_keys)} wallets already exist:\n```\n{already_exist_string}\n```\n"
        if not_private_keys:
            not_keys_string = '\n'.join(not_private_keys)
            response_message += f"Not private keys:\n```\n{not_keys_string}\n```"
        await interaction.response.send_message(response_message)

    @app_commands.command(name="check", description="Check the wallets that you sent")
    @app_commands.autocomplete(release_id=release_id_autocomplete)
    @app_commands.describe(release_id="Release name from /mints get-all")
    @discord.app_commands.rename(release_id="release_name")
    async def check_wallets(self, interaction: discord.Interaction, release_id: str):
        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}", ephemeral=True)
            return

        member_id = interaction.user.id
        member_name = interaction.user.name

        message_to_send = f"{member_name} wallets for `{mint.id}`:\n```\n"
        member_wallets = mint.get_wallets_by_id(member_id)
        if not member_wallets:
            await interaction.response.send_message(message_to_send + "Nothing\n```\n")
            return

        for wallet in member_wallets:
            message_to_send += f"{wallet}\n"
        message_to_send += "```"

        await interaction.response.send_message(message_to_send)

    @app_commands.command(name="delete",
                          description='Delete wallets separated by spaces for chosen release, "all" for all')
    @app_commands.autocomplete(release_id=release_id_autocomplete)
    @app_commands.describe(release_id="Release name from /mints get-all",
                           wallets='Private keys that you want to delete. Use "all" for select all wallets')
    @discord.app_commands.rename(release_id="release_name", wallets="private_keys")
    async def delete_wallets(self, interaction: discord.Interaction, release_id: str, wallets: str):
        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return

        member_id = interaction.user.id
        member_wallets = mint.get_wallets_by_id(member_id)
        if not member_wallets:
            await interaction.response.send_message(f"First you need to send wallets!")
            return

        deleted_wallets = delete_wallets_from_mint(wallets, mint, member_id)
        await interaction.response.send_message(
            f"Successfully deleted {deleted_wallets} wallets")
