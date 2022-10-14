import discord
from discord import app_commands

from additions import embeds


@app_commands.command(name="help", description="Displays the description of supported commands")
@app_commands.guild_only()
async def ask_help(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(embeds=embeds.help_embeds())
