import discord

import sql.commands
from base_classes.base import PropertyModel, AsyncObject
from setup import config
from utilities.logging import get_logger
from utilities.strings import remove_emoji

logger = get_logger(__name__)


class Member(PropertyModel, AsyncObject):
    id: int
    name_: str
    ticket_id_: int = None

    async def __ainit__(self, *args, **kwargs):
        if not await is_member_exists(self.id):
            await create_member(self)

    @property
    def ticket_id(self):
        return self.ticket_id_

    @ticket_id.setter
    def ticket_id(self, value):
        pass

    async def set_ticket_id(self, value):
        await update_member(self, ticket_id=value)
        self.ticket_id_ = value

    @property
    def name(self):
        return self.name_

    @name.setter
    def name(self, value):
        pass

    async def set_name(self, value):
        await update_member(self, name=value)
        self.name_ = value

    class Config:
        attributes_to_change = ["ticket_id", "name"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


async def create_member(member: Member) -> None:
    await sql.commands.add.member(member.dict())


async def is_member_exists(member_id: int) -> bool:
    return await sql.commands.check_exist.member(member_id)


async def update_member(member: Member, **kwargs) -> None:
    await sql.commands.update.member(member.id, **kwargs)


async def get_member_by_id(member_id: int) -> Member | None:
    return Member.parse_obj(await sql.commands.get.member(member_id))


async def add_member(member: discord.Member) -> None:
    logger.debug(f"Adding member {member.id=}, {member.name=}")
    await Member(id=member.id, name=member.name)


async def get_member_name_by_id(member_id: int) -> str:
    return remove_emoji((await get_member_by_id(member_id)).name)


def is_member_admin(member_id: int) -> bool:
    return member_id in config.admins


def is_member_owner(member_id: int) -> bool:
    return member_id in config.owners


async def get_member_by_user(user: discord.Member) -> Member:
    return await Member(id=user.id, name=user.name)
