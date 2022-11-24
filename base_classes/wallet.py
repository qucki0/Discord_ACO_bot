import asyncio
import enum

import pymysql

import sql.commands
from base_classes.base import PropertyModel
from base_classes.mint import Mint
from blockchains.handlers import is_private_key_correct
from utilities.logging import get_logger
from utilities.strings import get_wallets_from_string
from .errors import WalletsNotExist

logger = get_logger(__name__)


class Wallet(PropertyModel):
    private_key: str
    mint_id: int
    member_id: int


class AddWalletStatus(enum.Enum):
    valid = 1
    not_private_key = 2
    already_exist = 3


class DeleteWalletStatus(enum.Enum):
    deleted = 1
    not_exist = 2


async def create_wallet(private_key: str, mint: Mint, member_id: int) -> AddWalletStatus:
    if not is_private_key_correct(private_key, mint):
        return AddWalletStatus.not_private_key
    if await is_wallet_exists(private_key, mint.id):
        return AddWalletStatus.already_exist
    try:
        await sql.commands.add.wallet({"private_key": private_key, "mint_id": mint.id, "member_id": member_id})
    except pymysql.err.IntegrityError:
        return AddWalletStatus.already_exist
    return AddWalletStatus.valid


async def is_wallet_exists(private_key: str, mint_id: int) -> bool:
    return await sql.commands.check_exist.wallet(private_key, mint_id)


async def delete_wallet(private_key: str, mint_id: int) -> DeleteWalletStatus:
    if not await is_wallet_exists(private_key, mint_id):
        return DeleteWalletStatus.not_exist
    await sql.commands.delete.wallet(private_key, mint_id)
    return DeleteWalletStatus.deleted


async def get_wallets_for_mint(mint_data: int | str) -> list[Wallet]:
    return [Wallet.parse_obj(d) for d in await sql.commands.get.wallets_for_mint(mint_data)]


async def get_member_wallets_for_mint(member_id: int, mint_id: int) -> list[Wallet]:
    wallets = [Wallet.parse_obj(d) for d in await sql.commands.get.member_wallets_for_mint(member_id, mint_id)]
    if not wallets:
        raise WalletsNotExist()
    return wallets


async def add_wallets_to_mint(wallets_to_add: list[str], mint: Mint, member_id: int) -> (list[str], list[str], int):
    not_private_keys = []
    already_exist_keys = []
    added_wallets = []

    tasks = [asyncio.create_task(create_wallet(wallet, mint, member_id)) for wallet in wallets_to_add]
    await asyncio.gather(*tasks)

    for index, status in enumerate(tasks):
        match status.result():
            case AddWalletStatus.valid:
                added_wallets.append(wallets_to_add[index])
            case AddWalletStatus.not_private_key:
                not_private_keys.append(wallets_to_add[index])
            case AddWalletStatus.already_exist:
                already_exist_keys.append(wallets_to_add[index])

    mint.wallets_limit -= len(added_wallets)
    logger.debug(f"Member {member_id} added {len(added_wallets)} wallets for {mint.name.upper()}")
    return not_private_keys, already_exist_keys, len(added_wallets)


def add_wallets_response(not_private_keys: list[str], already_exist_keys: list[str], added_wallets: int) -> str:
    response_message = f"Successfully sent {added_wallets} wallets. \n"
    if already_exist_keys:
        already_exist_string = '\n'.join(already_exist_keys)
        response_message += f"{len(already_exist_keys)} wallets already exist:\n```\n{already_exist_string}\n```\n"
    if not_private_keys:
        not_keys_string = '\n'.join(not_private_keys)
        response_message += f"Not private keys:\n```\n{not_keys_string}\n```"
    return response_message


async def delete_wallets_from_mint(wallets_to_delete: str, mint: Mint, member_id: int) -> int:
    deleted_wallets = 0
    if wallets_to_delete.lower().strip() == "all":
        wallets = await get_member_wallets_for_mint(member_id, mint.id)
        wallets_to_delete = [wallet.private_key for wallet in wallets]
    else:
        wallets_to_delete = get_wallets_from_string(wallets_to_delete)
    tasks = [asyncio.create_task(delete_wallet(wallet, mint.id)) for wallet in wallets_to_delete]
    await asyncio.gather(*tasks)
    for status in tasks:
        match status.result():
            case DeleteWalletStatus.deleted:
                deleted_wallets += 1

    mint.wallets_limit += deleted_wallets
    logger.debug(f"Member {member_id} deleted {deleted_wallets} wallets for {mint.name.upper()}")
    return deleted_wallets
