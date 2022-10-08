import discord

from additions.all_data import actual_mints, all_mints, config, aco_members
from classes.classes import Drop
from functions.other import get_data_by_id_from_list


async def add_mint_to_mints_list(interaction: discord.Interaction, release_id, link, timestamp, wallets_limit=10):
    if check_mint_exist(release_id):
        await interaction.response.send_message(f"{release_id} already exist!", ephemeral=True)
    else:
        mint = Drop(release_id, link, timestamp, wallets_limit)
        actual_mints.append(mint)
        all_mints.append(mint)
        await interaction.client.get_channel(config.alert_channel_id).send("New mint found", embed=mint.get_as_embed())
        await interaction.response.send_message(f"Added `{release_id}` to drop list!", ephemeral=True)


def check_mint_exist(release_id):
    return any(release_id.lower().strip() == drop.id.lower() for drop in all_mints)


def get_mint_by_id(release_name):
    return get_data_by_id_from_list(release_name, actual_mints)


def get_unpaid_mints():
    data = {}
    for member in aco_members:
        for release_id in member.payments:
            if unpaid_amount := member.payments[release_id]["unpaid_amount"]:
                if release_id in data:
                    data[release_id].append([member.id, unpaid_amount])
                else:
                    data[release_id] = [[member.id, unpaid_amount]]
    return data
