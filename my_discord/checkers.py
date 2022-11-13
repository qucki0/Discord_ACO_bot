import discord

from base_classes.member import is_member_admin, is_member_owner
from utilities.logging import get_logger

logger = get_logger(__name__)


async def admin_checker(interaction: discord.Interaction) -> bool:
    logger.info(f"Checking {interaction.user.id}, {interaction.user.name} for admin role")
    return is_member_admin(interaction.user.id)


async def owner_checker(interaction: discord.Interaction) -> bool:
    logger.info(f"Checking {interaction.user.id}, {interaction.user.name} for owner role")
    return is_member_owner(interaction.user.id)
