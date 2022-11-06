import discord

from base_classes.member import check_admin
from setup import config
from utilities.logging import get_logger

logger = get_logger(__name__)


async def admin_checker(interaction: discord.Interaction) -> bool:
    logger.info(f"Checking {interaction.user.id}, {interaction.user.name} for admin role")
    return await base_checker(interaction, check_admin(interaction.user.id))


async def owner_checker(interaction: discord.Interaction) -> bool:
    logger.info(f"Checking {interaction.user.id}, {interaction.user.name} for owner role")
    return await base_checker(interaction, interaction.user.id in config.owners)


async def base_checker(interaction: discord.Interaction, condition: bool) -> bool:
    if condition:
        return True
    else:
        await interaction.response.send_message("You do not have enough permissions to perform this operation.",
                                                ephemeral=True)
        return False
