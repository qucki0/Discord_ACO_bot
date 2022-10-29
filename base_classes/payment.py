import asyncio
import time

import discord

from base_classes.base import PropertyModel
from base_classes.member import Member
from base_classes.mint import Mint
from my_discord.embeds import unpaid_successes
from setup import config
import sql.commands


class Payment(PropertyModel):
    mint_id: int
    mint_name: str
    member_id: int
    amount_of_checkouts_: int

    def __init__(self, **data):
        super().__init__(**data)
        if not sql.commands.check_exist.payment(self.mint_id, self.member_id):
            sql.commands.add.payment(self)

    def update_data(self, **kwargs):
        sql.commands.update.payment(self.mint_id, self.member_id, **kwargs)

    @property
    def amount_of_checkouts(self):
        return self.amount_of_checkouts_

    @amount_of_checkouts.setter
    def amount_of_checkouts(self, value):
        pass

    def set_amount_of_checkouts(self, value):
        self.update_data(amount_of_checkouts=value)
        self.amount_of_checkouts_ = value

    class Config:
        attributes_to_change = ["amount_of_checkouts"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


def add_checkout(member: Member, mint: Mint, amount_to_add: int) -> Payment:
    if sql.commands.check_exist.payment(mint.id, member.id):
        payment = sql.commands.get.payment(mint.id, member.id)
    else:
        payment = Payment(mint_id=mint.id, mint_name=mint.name, member_id=member.id, amount_of_checkouts=0)
    payment.amount_of_checkouts += amount_to_add
    mint.checkouts += amount_to_add
    return payment


async def send_notifications(client: discord.Client) -> None:
    response = ""
    payments = sql.commands.get.unpaid_checkouts()
    for payment in payments:
        content = f"<@{payment.member_id}>\nFriendly reminder to pay for checkouts."
        member = sql.commands.get.member(payment.member_id)
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
