import asyncio
import time

import discord

import sql.commands
from base_classes.base import PropertyModel, AsyncObject
from base_classes.member import Member, get_member_by_id
from base_classes.mint import Mint
from utilities.logging import get_logger

logger = get_logger(__name__)


class Payment(PropertyModel, AsyncObject):
    mint_id: int
    mint_name: str
    member_id: int
    amount_of_checkouts_: int

    async def __ainit__(self, *args, **kwargs):
        if not await is_payment_exist(self.mint_id, self.member_id):
            await create_payment(self)

    @property
    def amount_of_checkouts(self):
        return self.amount_of_checkouts_

    @amount_of_checkouts.setter
    def amount_of_checkouts(self, value):
        pass

    async def set_amount_of_checkouts(self, value):
        await update_payment(self, amount_of_checkouts=value)
        self.amount_of_checkouts_ = value

    class Config:
        attributes_to_change = ["amount_of_checkouts"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


async def create_payment(payment: Payment) -> None:
    await sql.commands.add.payment({key: payment.dict()[key] for key in payment.dict() if key != "mint_name"})


async def update_payment(payment: Payment, **kwargs) -> None:
    await sql.commands.update.payment(payment.mint_id, payment.member_id, **kwargs)


async def is_payment_exist(release_data: str | int, member_id: int) -> bool:
    return await sql.commands.check_exist.payment(release_data, member_id)


async def get_member_unpaid_payments(member_id: int) -> list[Payment]:
    return [Payment.parse_obj(d) for d in await sql.commands.get.member_unpaid_payments(member_id)]


async def get_payment(release_name: str, member_id: int) -> Payment | None:
    if not await is_payment_exist(release_name, member_id):
        return None
    return Payment.parse_obj(await sql.commands.get.payment(release_name, member_id))


async def get_unpaid_checkouts() -> list[Payment]:
    return [Payment.parse_obj(d) for d in await sql.commands.get.unpaid_checkouts()]


async def add_checkout(member: Member, mint: Mint, amount_to_add: int) -> Payment:
    if await is_payment_exist(mint.id, member.id):
        payment = await get_payment(mint.name, member.id)
    else:
        payment = await Payment(mint_id=mint.id, mint_name=mint.name, member_id=member.id, amount_of_checkouts=0)
    payment.amount_of_checkouts += amount_to_add
    mint.checkouts += amount_to_add
    return payment


async def send_notifications(client: discord.Client) -> None:
    from my_discord.embeds import unpaid_successes
    response = ""
    payments = await get_unpaid_checkouts()
    for payment in payments:
        content = f"<@{payment.member_id}>\nFriendly reminder to pay for checkouts."
        member = await get_member_by_id(payment.member_id)
        logger.info(f"Sending payment notification to {member.id=}, {member.name=}")
        try:
            await client.get_user(member.id).send(content=content, embed=await unpaid_successes(member))
            logger.info(f"Notification for {member.id}, {member.name} sent to direct message")
        except discord.errors.Forbidden:
            if member.ticket_id is not None:
                await client.get_channel(member.ticket_id).send(content=content,
                                                                embed=await unpaid_successes(member))
                logger.info(f"Notification for {member.id}, {member.name} sent to ticket {member.ticket_id=}")
            else:
                response += f"<@{member.id}>\n"
                logger.info(f"Notification doesnt sent to {member.id=}, {member.name=}")

    from setup import config
    await client.get_channel(config.ids.channels.notifications_channel_id).send(
        f"Can't reach this members:\n{response}\n")


async def auto_send_notifications(client: discord.Client) -> None:
    timestamp_to_send = 1666515600
    week = 7 * 24 * 60 * 60
    while True:
        while timestamp_to_send < int(time.time()):
            timestamp_to_send += week
        time_to_wait = timestamp_to_send - int(time.time()) + 10
        logger.info(f"Waiting {time_to_wait} seconds to send payment notifications")
        await asyncio.sleep(time_to_wait)
        await send_notifications(client)


async def get_unpaid_mints() -> dict[str: list[int, int]]:
    unpaid_checkouts = await get_unpaid_checkouts()
    data = {}
    for payment in unpaid_checkouts:
        if payment.mint_name not in data:
            data[payment.mint_name] = []
        data[payment.mint_name].append([payment.member_id, payment.amount_of_checkouts])
    return data
