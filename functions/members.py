import discord

from additions.all_data import config
from classes.classes import ACOMember
from functions import sql_commands
from functions.other import remove_emoji


def add_member(member: discord.Member) -> None:
    ACOMember(id=member.id, name=member.name)


def get_member_name_by_id(member_id: int) -> str:
    return remove_emoji(get_member_by_id(member_id).name)


def check_admin(member_id: int) -> bool:
    return member_id in config.admins


def get_member_by_id(member_id: int) -> ACOMember | None:
    return sql_commands.get.member(member_id)


def get_member_by_user(user: discord.Member) -> ACOMember:
    return ACOMember(id=user.id, name=user.name)
