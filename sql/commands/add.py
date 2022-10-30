from base_classes.member import Member
from base_classes.mint import Mint
from base_classes.payment import Payment
from base_classes.wallet import Wallet
from blockchains.solana.classes import Transaction
from ..client import SqlClient

sql_client = SqlClient()


def member(member_to_add: Member) -> None:
    sql_client.add_data("DiscordMembers", member_to_add.dict())


def mint(mint_to_add: Mint) -> None:
    data = mint_to_add.dict()
    sql_client.add_data("Mints", {key: data[key] for key in data if key != "id"})


def transaction(transaction_to_add: Transaction) -> None:
    sql_client.add_data("Transactions", transaction_to_add.dict())


def wallet(wallet_to_add: Wallet) -> None:
    sql_client.add_data("Wallets", wallet_to_add.dict())


def payment(payment_to_add: Payment) -> None:
    data = payment_to_add.dict()
    sql_client.add_data("Payments", {key: data[key] for key in data if key != "mint_name"})
