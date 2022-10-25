import asyncio
import time

import discord

from additions.all_data import aco_members, config
from additions.embeds import unpaid_successes
from classes.classes import ACOMember, Drop


def add_checkouts(member: ACOMember, mint: Drop, amount_to_add: int) -> None:
    if mint.id not in member.payments:
        member.payments[mint.id] = {"amount_of_checkouts": amount_to_add,
                                    "unpaid_amount": amount_to_add}
    else:
        member.payments[mint.id]["amount_of_checkouts"] += amount_to_add
        member.payments[mint.id]["unpaid_amount"] += amount_to_add
    mint.checkouts += amount_to_add


async def send_notifications(client: discord.Client) -> None:
    response = ""
    for member in aco_members:
        content = f"<@{member.id}>\nFriendly reminder to pay for checkouts."
        if any(member.payments[key]["unpaid_amount"] != 0 for key in member.payments):
            try:
                await client.get_user(member.id).send(content=content, embed=unpaid_successes(member))
            except discord.errors.Forbidden:
                if member.ticket_id is not None:
                    await client.get_channel(member.ticket_id).send(content=content,
                                                                    embed=unpaid_successes(member))
                else:
                    response += f"<@{member.id}>\n"
    await client.get_channel(config.notifications_channel_id).send(f"Can't reach this members:\n{response}\n")


async def auto_send_notifications(client: discord.Client) -> None:
    timestamp_to_send = 1666515600
    week = 7 * 24 * 60 * 60

    while True:
        while timestamp_to_send < int(time.time()):
            timestamp_to_send += week
        time_to_wait = timestamp_to_send - int(time.time())
        await asyncio.sleep(time_to_wait)
        await send_notifications(client)
