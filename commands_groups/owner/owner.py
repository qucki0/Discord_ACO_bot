import discord
from discord import app_commands

from additions.all_data import config
from additions.checkers import owner_checker
from classes.discord_classes import CreateTicketView


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
    async def create_ticket_menu(self, interaction: discord.Interaction):
        await interaction.channel.send(content="Take your ACO", view=CreateTicketView(config.closed_category_id))
        await interaction.response.send_message("Menu created")
