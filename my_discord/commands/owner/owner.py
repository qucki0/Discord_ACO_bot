import discord
from discord import app_commands

from base_classes.payment import send_notifications
from my_discord.checkers import owner_checker
from my_discord.embeds import tickets_menu
from my_discord.views.tickets import CreateTicketView
from setup import config
from utilities.logging import get_logger

logger = get_logger(__name__)
__all__ = ["Owner"]


@app_commands.guild_only()
class Owner(app_commands.Group):
    @app_commands.command(name="add-admin", description="OWNER COMMAND add member to admins list")
    @app_commands.check(owner_checker)
    @app_commands.describe(user="User that will receive admin role")
    async def add_admin(self, interaction: discord.Interaction, user: discord.Member) -> None:
        config.ids.members.admins.append(user.id)
        logger.info(f"{interaction.user.id}, {interaction.user.name} added Admin role to {user.id}, {user.name}")
        await interaction.response.send_message(f"Added {user.name} to admins list")

    @app_commands.command(name="delete-admin", description="OWNER COMMAND add member to admins list")
    @app_commands.check(owner_checker)
    @app_commands.describe(user="User that will lose admin role")
    async def delete_admin(self, interaction: discord.Interaction, user: discord.Member) -> None:
        await interaction.response.defer()
        if user.id not in config.ids.members.admins:
            await interaction.followup.send(f"{user.name} is not admin", ephemeral=True)
        config.ids.members.admins.remove(user.id)
        logger.info(f"{interaction.user.id}, {interaction.user.name} deleted Admin role from {user.id}, {user.name}")
        await interaction.followup.send(f"Deleted {user.name} from admins list", ephemeral=True)

    @app_commands.command(name="create-ticket-menu", description="OWNER COMMAND creates ticket menu")
    @app_commands.check(owner_checker)
    async def create_ticket_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.channel.send(embed=tickets_menu(),
                                       view=CreateTicketView(config.ids.channels.closed_category_id))
        await interaction.followup.send("Menu created", ephemeral=True)

    @app_commands.command(name="send-notifications", description="OWNER COMMAND sends payment notifications for users")
    @app_commands.check(owner_checker)
    async def send_notifications(self, interaction: discord.Interaction):
        await interaction.response.defer()
        logger.info(f"{interaction.user.id}, {interaction.user.name} started payments notifications sending")
        await send_notifications(interaction.client)
        await interaction.followup.send(f"Notifications gone, check <#{config.ids.channels.notifications_channel_id}>")

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await interaction.followup.send(
            "An unexpected error occurred, try again. If that doesn't work, ping the admin")
        logger.exception(f"{interaction.user} {interaction.user.id} got error \n {error}")
