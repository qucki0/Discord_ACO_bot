import discord

from additions.all_data import aco_members, config
from classes.classes import ACOMember
from functions.other import remove_emoji, get_data_by_id_from_list


def add_member(member: discord.Member):
    if all(member.id != aco_member.id for aco_member in aco_members):
        aco_members.append(ACOMember(member))


def get_member_name_by_id(member_id):
    return remove_emoji(get_member_by_id(member_id).name)


def check_admin(member_id):
    return member_id in config.admins


def get_member_by_id(member_id):
    return get_data_by_id_from_list(member_id, aco_members)


def get_member_for_payments(user: discord.Member):
    member = get_member_by_id(user.id)
    if member is None:
        add_member(user)
        member = get_member_by_id(user.id)
    return member
