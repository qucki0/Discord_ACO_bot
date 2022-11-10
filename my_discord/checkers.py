import discord

from base_classes.member import is_member_admin, is_member_owner
from utilities.logging import get_logger

logger = get_logger(__name__)


async def admin_checker(interaction: discord.Interaction) -> bool:
    logger.info(f"Checking {interaction.user.id}, {interaction.user.name} for admin role")
    return await base_checker(interaction, is_member_admin(interaction.user.id))


async def owner_checker(interaction: discord.Interaction) -> bool:
    logger.info(f"Checking {interaction.user.id}, {interaction.user.name} for owner role")
    return await base_checker(interaction, is_member_owner(interaction.user.id))


async def base_checker(interaction: discord.Interaction, condition: bool) -> bool:
    if condition:
        return True
    else:
        await interaction.response.send_message("You do not have enough permissions to perform this operation.",
                                                ephemeral=True)
        return False
