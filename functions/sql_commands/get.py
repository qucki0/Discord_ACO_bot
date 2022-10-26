from additions.all_data import sql_client
from classes.blockchain import Transaction
from classes.classes import ACOMember, Mint, Wallet, Payment


def member(member_id: int) -> ACOMember:
    data = sql_client.select_data("DiscordMembers", condition={"id": member_id})[0]
    return ACOMember.parse_obj(data)


def mint(mint_id: int = None, mint_name: str = None) -> Mint:
    condition = {}
    if mint_id is not None:
        condition["id"] = mint_id
    if mint_name is not None:
        condition["name"] = mint_name
    data = sql_client.select_data("Mints", condition=condition)[0]
    return Mint.parse_obj(data)


def transaction(transaction_hash: str) -> Transaction:
    data = sql_client.select_data("Transactions", condition={"hash": transaction_hash})[0]
    return Transaction.parse_obj(data)


def wallet(private_key: str) -> Wallet:
    data = sql_client.select_data("Wallets", condition={"private_key": private_key})[0]
    return Wallet.parse_obj(data)


def payment(mint_id: int, member_id: int) -> Payment:
    data = sql_client.select_data("Payments", condition={"mint_id": mint_id, "member_id": member_id})[0]
    return Payment.parse_obj(data)
