import discord
from discord import app_commands

from additions.all_data import actual_mints, aco_members, all_mints
from functions.mints import get_data_by_id_from_list


async def release_id_autocomplete(interaction: discord.Interaction, current: str):
    mints = [mint.id for mint in actual_mints if current.strip().lower() in mint.id.lower()]
    if len(mints) > 25:
        mints = mints[:24] + ["..."]
    return [app_commands.Choice(name=mint, value=mint) for mint in mints if current.lower() in mint.lower()]


async def unpaid_release_ids_autocomplete(interaction: discord.Interaction, current: str):
    member = get_data_by_id_from_list(interaction.user.id, aco_members)
    mints = [mint for mint in member.payments if member.payments[mint]["unpaid_amount"] > 0]
    if len(mints) > 25:
        mints = mints[:24] + ["..."]
    return [app_commands.Choice(name=mint, value=mint) for mint in mints if current.lower() in mint.lower()]


async def possible_releases_to_add_payment(interaction: discord.Interaction, current: str):
    mints = [mint.id for mint in reversed(all_mints) if current.strip().lower() in mint.id.lower()]
    if len(mints) > 25:
        mints = mints[:24] + ["..."]
    return [app_commands.Choice(name=mint, value=mint) for mint in mints if current.lower() in mint.lower()]
