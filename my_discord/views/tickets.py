import discord

from base_classes.member import get_member_by_user
from my_discord import embeds
from utilities.logging import get_logger

logger = get_logger(__name__)


class CreateTicketView(discord.ui.View):
    closed_category_id = None

    def __init__(self, closed_category_id: int):
        self.closed_category_id = closed_category_id
        super().__init__(timeout=None)

    @discord.ui.button(label="Create ticket", style=discord.ButtonStyle.gray, custom_id="ticket_button")
    async def create_ticket(self, ticket_interaction: discord.Interaction, button: discord.ui.Button) -> None:
        ticket_name = f"{ticket_interaction.user.name}-{ticket_interaction.user.discriminator}".lower().replace(" ",
                                                                                                                "-")
        ticket = discord.utils.get(ticket_interaction.guild.text_channels, name=ticket_name)
        if ticket is not None:
            await ticket_interaction.response.send_message(f"You already have a ticket at {ticket.mention}",
                                                           ephemeral=True)
            return

        overwrites = {ticket_interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                      ticket_interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                                           attach_files=True)}
        category = ticket_interaction.channel.category
        channel = await ticket_interaction.guild.create_text_channel(name=ticket_name, overwrites=overwrites,
                                                                     category=category,
                                                                     reason=f"Ticket for"
                                                                            f" {ticket_interaction.user.mention}")
        logger.debug(f"Ticket created for {ticket_interaction.user}, {ticket_interaction.user.name}")
        await channel.send(view=TicketView(self.closed_category_id), embed=embeds.ticket())
        await ticket_interaction.response.send_message(f"Ticket created {channel.mention}", ephemeral=True)
        member = await get_member_by_user(ticket_interaction.user)
        member.ticket_id = channel.id


class TicketView(discord.ui.View):
    closed_category_id = None

    def __init__(self, closed_category: int):
        self.closed_category_id = closed_category
        super().__init__(timeout=None)

    @discord.ui.button(label="Close ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def close_ticket(self, close_interaction: discord.Interaction, button: discord.ui.Button):
        closed_category = discord.utils.get(close_interaction.guild.categories, id=self.closed_category_id)
        channel_name = close_interaction.channel.name
        await close_interaction.channel.edit(category=closed_category, name=f"closed-{channel_name}",
                                             sync_permissions=True)
        await close_interaction.response.send_message(f"Ticket closed by {close_interaction.user.mention}")
        logger.debug(f"Ticket closed for {close_interaction.user.id}, {close_interaction.user.name}")
        member = await get_member_by_user(close_interaction.user)
        member.ticket_id = None
        self.stop()

    @discord.ui.button(label="Help", style=discord.ButtonStyle.blurple, custom_id="get_help")
    async def get_help(self, help_interaction: discord.Interaction, button: discord.ui.Button):
        await help_interaction.response.send_message(embeds=embeds.help_embeds())
