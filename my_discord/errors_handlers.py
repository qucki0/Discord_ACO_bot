import discord
from discord import app_commands

from base_classes.errors import *
from utilities.logging import get_logger

logger = get_logger(__name__)


class AppCommandsErrorsHandler:
    @staticmethod
    async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandInvokeError):
            message = AppCommandsErrorsHandler.handle_command_invoke_errors(interaction, error)
        elif isinstance(error, app_commands.CheckFailure):
            message = "You do not have enough permissions to perform this operation."
        else:
            message = "An unexpected error occurred, try again. If that doesn't work, ping the admin"
            logger.exception(f"{interaction.user} {interaction.user.id} got error \n {error}")

        await AppCommandsErrorsHandler.send_response(interaction, message)

    @staticmethod
    async def send_response(interaction: discord.Interaction, message: str):
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    @staticmethod
    def handle_command_invoke_errors(interaction: discord.Interaction, error: app_commands.CommandInvokeError):
        match error.original:
            case MintNotExist():
                return f"There are no releases named as `{error.original.mint_name}`"
            case MintAlreadyExist():
                return f"`{error.original.mint_name}` already exist!"
            case PaymentNotExist():
                return f"There are no payments for `{error.original.mint_name}`"
            case WrongCheckoutsQuantity():
                return "Wrong checkouts quantity"
            case WalletsNotExist():
                return "No wallets for this mint"
            case _:
                logger.exception(f"{interaction.user} {interaction.user.id} got error \n {error}")
                return "An unexpected error occurred, try again. If that doesn't work, ping the admin"
