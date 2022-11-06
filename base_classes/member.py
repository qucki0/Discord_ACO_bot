import discord

import sql.commands
from base_classes.base import PropertyModel
from setup import config
from utilities.logging import get_logger
from utilities.strings import remove_emoji

logger = get_logger(__name__)


class Member(PropertyModel):
    id: int
    name_: str
    ticket_id_: int = None

    def __init__(self, **data):
        super().__init__(**data)
        if not sql.commands.check_exist.member(self.id):
            sql.commands.add.member(self.dict())

    def update_data(self, **kwargs):
        sql.commands.update.member(self.id, **kwargs)

    @property
    def ticket_id(self):
        return self.ticket_id_

    @ticket_id.setter
    def ticket_id(self, value):
        pass

    def set_ticket_id(self, value):
        self.update_data(ticket_id=value)
        self.ticket_id_ = value

    @property
    def name(self):
        return self.name_

    @name.setter
    def name(self, value):
        pass

    def set_name(self, value):
        self.update_data(name=value)
        self.name_ = value

    class Config:
        attributes_to_change = ["ticket_id", "name"]
        fields = {f"{a}_": a for a in attributes_to_change}
        property_set_methods = {a: f"set_{a}" for a in attributes_to_change}


def add_member(member: discord.Member) -> None:
    logger.debug(f"Adding member {member.id=}, {member.name=}")
    Member(id=member.id, name=member.name)


def get_member_name_by_id(member_id: int) -> str:
    return remove_emoji(get_member_by_id(member_id).name)


def check_admin(member_id: int) -> bool:
    return member_id in config.admins


def get_member_by_id(member_id: int) -> Member | None:
    return Member.parse_obj(sql.commands.get.member(member_id))


def get_member_by_user(user: discord.Member) -> Member:
    return Member(id=user.id, name=user.name)
