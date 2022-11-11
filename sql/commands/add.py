from ..client import SqlClient

sql_client = SqlClient()


async def member(member_to_add: dict) -> None:
    await sql_client.add_data("DiscordMembers", member_to_add)


async def mint(mint_to_add: dict) -> None:
    await sql_client.add_data("Mints", mint_to_add)


async def transaction(transaction_to_add: dict) -> None:
    await sql_client.add_data("Transactions", transaction_to_add)


async def wallet(wallet_to_add: dict) -> None:
    await sql_client.add_data("Wallets", wallet_to_add)


async def payment(payment_to_add: dict) -> None:
    await sql_client.add_data("Payments", payment_to_add)
