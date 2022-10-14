import discord

from additions.all_data import config
from functions.members import check_admin


async def admin_checker(interaction: discord.Interaction) -> bool:
    return await base_checker(interaction, check_admin(interaction.user.id))


async def owner_checker(interaction: discord.Interaction) -> bool:
    return await base_checker(interaction, interaction.user.id in config.owners)


async def base_checker(interaction: discord.Interaction, condition: bool) -> bool:
    if condition:
        return True
    else:
        await interaction.response.send_message("You do not have enough permissions to perform this operation.",
                                                ephemeral=True)
        return False
