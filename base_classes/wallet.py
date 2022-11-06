import sql.commands
from base_classes.base import PropertyModel
from base_classes.mint import Mint
from blockchains.solana.functions import is_hash_length_correct
from utilities.logging import get_logger
from utilities.strings import get_wallets_from_string

logger = get_logger(__name__)


class Wallet(PropertyModel):
    private_key: str
    mint_id: int
    member_id: int

    def __init__(self, **data):
        super().__init__(**data)

        if not sql.commands.check_exist.wallet(self.private_key):
            sql.commands.add.wallet(self.dict())


def add_wallets_to_mint(wallets_to_add: list[str], mint: Mint, member_id: int) -> str:
    not_private_keys = []
    already_exist_keys = []
    added_wallets = 0
    for wallet in wallets_to_add:
        if not is_hash_length_correct(wallet):
            not_private_keys.append(wallet)
            continue
        if sql.commands.check_exist.wallet(wallet):
            already_exist_keys.append(wallet)
            continue
        Wallet(private_key=wallet, mint_id=mint.id, member_id=member_id)
        added_wallets += 1
    mint.wallets_limit -= added_wallets
    logger.debug(f"Member {member_id} added {added_wallets} wallets for {mint.name.upper()}")
    response = add_wallets_response(not_private_keys, already_exist_keys, added_wallets)
    return response


def add_wallets_response(not_private_keys: list[str], already_exist_keys: list[str], added_wallets: int) -> str:
    response_message = f"Successfully sent {added_wallets} wallets. \n"
    if already_exist_keys:
        already_exist_string = '\n'.join(already_exist_keys)
        response_message += f"{len(already_exist_keys)} wallets already exist:\n```\n{already_exist_string}\n```\n"
    if not_private_keys:
        not_keys_string = '\n'.join(not_private_keys)
        response_message += f"Not private keys:\n```\n{not_keys_string}\n```"
    return response_message


def delete_wallets_from_mint(wallets_to_delete: str, mint: Mint, member_id: int) -> int:
    deleted_wallets = 0
    if wallets_to_delete.lower().strip() == "all":
        wallets = [Wallet.parse_obj(d) for d in sql.commands.get.member_wallets_for_mint(member_id, mint.id)]
        wallets_to_delete = [wallet.private_key for wallet in wallets]
    else:
        wallets_to_delete = get_wallets_from_string(wallets_to_delete)
    for wallet in wallets_to_delete:
        if sql.commands.check_exist.wallet(wallet):
            sql.commands.delete.wallet(wallet)
            deleted_wallets += 1

    mint.wallets_limit += deleted_wallets
    logger.debug(f"Member {member_id} deleted {deleted_wallets} wallets for {mint.name.upper()}")
    return deleted_wallets


def get_wallets_for_mint(mint_data: int | str) -> list[Wallet]:
    return [Wallet.parse_obj(d) for d in sql.commands.get.wallets_for_mint(mint_data)]


def get_member_wallets_for_mint(member_id: int, mint_id: int) -> list[Wallet]:
    return [Wallet.parse_obj(d) for d in sql.commands.get.member_wallets_for_mint(member_id, mint_id)]
