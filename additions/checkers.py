import discord

from additions.all_data import config
from additions.functions import check_admin


async def admin_checker(interaction: discord.Interaction):
    if check_admin(interaction.user.id):
        return True
    else:
        await interaction.response.send_message("You do not have enough permissions to perform this operation.",
                                                ephemeral=True)
        return False


async def owner_checker(interaction: discord.Interaction):
    if interaction.user.id in config.owners:
        return True
    else:
        await interaction.response.send_message("You do not have enough permissions to perform this operation.",
                                                ephemeral=True)
        return False
