import discord

from additions.all_data import aco_members, config
from classes.classes import ACOMember
from functions.other import remove_emoji


def add_member(member: discord.Member):
    if all(member.id != aco_member.id for aco_member in aco_members):
        aco_members.append(ACOMember(member))


def get_member_name_by_id(member_id):
    for member in aco_members:
        if int(member.id) == int(member_id):
            return remove_emoji(member.name)


def check_admin(member_id):
    return member_id in config.admins
