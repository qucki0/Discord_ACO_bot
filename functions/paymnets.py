import asyncio
import time

import discord

from additions.all_data import config
from additions.embeds import unpaid_successes
from classes.classes import ACOMember, Mint, Payment
from functions import sql_commands


def add_checkout(member: ACOMember, mint: Mint, amount_to_add: int) -> Payment:
    if sql_commands.check_exist.payment(mint.id, member.id):
        payment = sql_commands.get.payment(mint.id, member.id)
    else:
        payment = Payment(mint_id=mint.id, mint_name=mint.name, member_id=member.id, amount_of_checkouts=0)
    payment.amount_of_checkouts += amount_to_add
    mint.checkouts += amount_to_add
    return payment


async def send_notifications(client: discord.Client) -> None:
    response = ""
    payments = sql_commands.get.unpaid_checkouts()
    for payment in payments:
        content = f"<@{payment.member_id}>\nFriendly reminder to pay for checkouts."
        member = sql_commands.get.member(payment.member_id)
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
