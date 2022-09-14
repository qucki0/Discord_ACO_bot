import json

import discord

import config
from additions.all_data import mints_list, aco_members
from additions.classes import ACOMember


def check_admin(member_id):
    return member_id in config.ADMINS_IDS


def get_mint_by_name(release_name):
    release_name = release_name.strip().lower()
    for mint in mints_list:
        if mint.name.lower() == release_name:
            return mint


def add_member(member: discord.Member):
    if not any(member.id == aco_member.id for aco_member in aco_members):
        aco_members.append(ACOMember(member))


def get_list_for_backup(arr):
    data = []
    for a in arr:
        data.append(a.get_as_dict())
    return data


def save_json(arr, filename):
    with open(filename, "w") as file:
        file.write(json.dumps(get_list_for_backup(arr), sort_keys=True, indent=4))
