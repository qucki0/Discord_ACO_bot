import discord
from discord import app_commands

from additions.all_data import aco_members
from additions.autocomplete import release_id_autocomplete
from functions.members import add_member
from functions.mints import get_mint_by_id, get_data_by_id_from_list


@app_commands.guild_only()
class Wallets(app_commands.Group):
    @app_commands.command(name="send", description="Send wallets separated by commas for chosen release")
    @app_commands.autocomplete(release_id=release_id_autocomplete)
    @app_commands.describe(release_id="Release name from /mints get-all",
                           wallets="Your wallets private keys separated by comma")
    @discord.app_commands.rename(release_id="release_name", wallets="private_keys")
    async def send_wallets(self, interaction: discord.Interaction, release_id: str, wallets: str):
        member_id = interaction.user.id
        member = get_data_by_id_from_list(member_id, aco_members)
        if member is None:
            add_member(interaction.user)

        wallets = [wallet.strip() for wallet in wallets.split(",")]
        if not len(wallets):
            await interaction.response.send_message("Please input wallets keys")
            return

        mint = get_mint_by_id(release_id)
        if mint is None:
            await interaction.response.send_message(f"There are no releases named as {release_id}")
            return

        if mint.wallets_limit < len(wallets):
            await interaction.response.send_message(f"There are only {mint.wallets_limit} spots left for {mint.id}")

        if member_id not in mint.wallets:
            mint.wallets[member_id] = set()
        wallets_before_adding = len(mint.wallets[member_id])
        not_private_keys = []
        already_exist_keys = []
        for wallet in wallets:
            if len(wallet) >= 85:
                if wallet not in mint.wallets[member_id]:
                    mint.wallets[member_id].add(wallet)
                else:
                    already_exist_keys.append(wallet)
            else:
                not_private_keys.append(wallet)
        mint.wallets_limit -= len(mint.wallets[member_id]) - wallets_before_adding
        response_message = f"Successfully sent {len(mint.wallets[member_id]) - wallets_before_adding} wallets. \n"
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
        if member_id not in mint.wallets:
            await interaction.response.send_message(message_to_send + "Nothing\n```\n")
            return
        for wallet in mint.get_wallets_by_id(member_id):
            message_to_send += f"{wallet}\n"
        message_to_send += "```"
        await interaction.response.send_message(message_to_send)

    @app_commands.command(name="delete",
                          description='Delete wallets separated by commas for chosen release, "all" for all')
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
        if member_id not in mint.wallets:
            await interaction.response.send_message(f"First you need to send wallets!")
            return

        wallets_len_before_deleting = len(mint.wallets[member_id])
        if wallets.lower().strip() == "all":
            mint.wallets[member_id].clear()
        else:
            wallets_to_delete = [wallet.strip() for wallet in wallets.split(",")]
            for wallet in wallets_to_delete:
                mint.wallets[member_id].discard(wallet)
        deleted_wallets = wallets_len_before_deleting - len(mint.wallets[member_id])
        mint.wallets_limit += deleted_wallets
        await interaction.response.send_message(
            f"Successfully deleted {deleted_wallets} wallets")
