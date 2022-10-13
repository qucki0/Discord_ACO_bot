import discord
from discord import app_commands

from additions.all_data import actual_mints, all_mints
from functions.members import get_member_by_id


async def release_id_autocomplete(interaction: discord.Interaction, current: str):
    mints = [mint.id for mint in actual_mints if current.strip().lower() in mint.id.lower()]
    return get_choices_from_list(mints, current)


async def unpaid_release_ids_autocomplete(interaction: discord.Interaction, current: str):
    member = get_member_by_id(interaction.user.id)
    mints = [mint for mint in member.payments if member.payments[mint]["unpaid_amount"] > 0]
    return get_choices_from_list(mints, current)


async def all_releases_autocomplete(interaction: discord.Interaction, current: str):
    mints = [mint.id for mint in reversed(all_mints) if current.strip().lower() in mint.id.lower()]
    return get_choices_from_list(mints, current)


def get_choices_from_list(arr, current):
    if len(arr) > 25:
        arr = arr[:24] + ["..."]
    return [app_commands.Choice(name=a, value=a) for a in arr if current.lower() in a.lower()]
