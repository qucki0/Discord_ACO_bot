from additions.all_data import sql_client
from classes.classes import ACOMember, Mint, Wallet, Payment
from classes.blockchain import Transaction


def member(member_to_add: ACOMember) -> None:
    sql_client.add_data("DiscordMembers", member_to_add.dict())


def mint(mint_to_add: Mint) -> None:
    sql_client.add_data("Mints", mint_to_add.dict())


def transaction(transaction_to_add: Transaction) -> None:
    sql_client.add_data("Transactions", transaction_to_add.dict())


def wallet(wallet_to_add: Wallet) -> None:
    sql_client.add_data("Wallets", wallet_to_add.dict())


def payment(payment_to_add: Payment) -> None:
    sql_client.add_data("Payments", payment_to_add.dict())