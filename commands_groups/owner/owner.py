import discord
from discord import app_commands

from additions.all_data import config, aco_members
from additions.checkers import owner_checker
from classes.discord_classes import CreateTicketView
from additions.embeds import unpaid_successes


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

    @app_commands.command(name="send-notifications", description="OWNER COMMAND sends payment notifications for users")
    async def send_notifications(self, interaction: discord.Interaction):
        data_to_send = ""
        for member in aco_members:
            content = f"<@{member.id}>\nFriendly reminder to pay for checkouts."
            if any(member.payments[key]["unpaid_amount"] != 0 for key in member.payments):
                try:
                    await interaction.client.get_user(member.id).send(content=content, embed=unpaid_successes(member))
                except discord.errors.Forbidden:
                    if member.ticket_id is not None:
                        await interaction.client.get_channel(member.ticket_id).send(content=content,
                                                                                    embed=unpaid_successes(member))
                    else:
                        data_to_send += f"<@{member.id}>\n"
        await interaction.response.send_message(f"Can't reach this members:\n{data_to_send}\n")
