import discord
from discord import app_commands

from additions.all_data import config
from additions.checkers import owner_checker
from additions.embeds import tickets_menu
from classes.discord_classes import CreateTicketView
from functions.paymnets import send_notifications


@app_commands.guild_only()
class Owner(app_commands.Group):
    @app_commands.command(name="add-admin", description="OWNER COMMAND add member to admins list")
    @app_commands.check(owner_checker)
    @app_commands.describe(user="User that will receive admin role")
    async def add_admin(self, interaction: discord.Interaction, user: discord.Member) -> None:
        config.admins.append(user.id)
        await interaction.response.send_message(f"Added {user.name} to admins list")

    @app_commands.command(name="delete-admin", description="OWNER COMMAND add member to admins list")
    @app_commands.check(owner_checker)
    @app_commands.describe(user="User that will lose admin role")
    async def delete_admin(self, interaction: discord.Interaction, user: discord.Member) -> None:
        if user.id not in config.admins:
            await interaction.response.send_message(f"{user.name} is not admin", ephemeral=True)
        config.admins.remove(user.id)
        await interaction.response.send_message(f"Deleted {user.name} from admins list", ephemeral=True)

    @app_commands.command(name="create-ticket-menu", description="OWNER COMMAND creates ticket menu")
    @app_commands.check(owner_checker)
    async def create_ticket_menu(self, interaction: discord.Interaction):
        await interaction.channel.send(embed=tickets_menu(), view=CreateTicketView(config.closed_category_id))
        await interaction.response.send_message("Menu created", ephemeral=True)

    @app_commands.command(name="send-notifications", description="OWNER COMMAND sends payment notifications for users")
    @app_commands.check(owner_checker)
    async def send_notifications(self, interaction: discord.Interaction):
        await send_notifications(interaction.client)
        await interaction.response.send_message(f"Notifications gone, check <#{config.notifications_channel_id}>")
