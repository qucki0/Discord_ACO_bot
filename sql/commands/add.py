from ..client import SqlClient

sql_client = SqlClient()


def member(member_to_add: dict) -> None:
    sql_client.add_data("DiscordMembers", member_to_add)


def mint(mint_to_add: dict) -> None:
    sql_client.add_data("Mints", mint_to_add)


def transaction(transaction_to_add: dict) -> None:
    sql_client.add_data("Transactions", transaction_to_add)


def wallet(wallet_to_add: dict) -> None:
    sql_client.add_data("Wallets", wallet_to_add)


def payment(payment_to_add: dict) -> None:
    sql_client.add_data("Payments", payment_to_add)
