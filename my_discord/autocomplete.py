import discord
from discord import app_commands

import sql.commands


async def release_id_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    actual_mints = sql.commands.get.actual_mints()
    mints = [mint.name for mint in actual_mints if current.strip().lower() in mint.name.lower()]
    return get_choices_from_list(mints, current)


async def unpaid_release_ids_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    payments = sql.commands.get.member_unpaid_payments(interaction.user.id)
    mints = [payment.mint_name for payment in payments if payment.amount_of_checkouts > 0]
    return get_choices_from_list(mints, current)


async def all_releases_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    all_mints = sql.commands.get.all_mints()
    mints = [mint.name for mint in reversed(all_mints) if current.strip().lower() in mint.name.lower()]
    return get_choices_from_list(mints, current)


def get_choices_from_list(arr: list[str], current: str) -> list[app_commands.Choice]:
    if len(arr) > 25:
        arr = arr[:24] + ["..."]
    return [app_commands.Choice(name=a, value=a) for a in arr if current.lower() in a.lower()]