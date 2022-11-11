from ..client import SqlClient

sql_client = SqlClient()


async def wallet(private_key: str, mint_id: int) -> None:
    await sql_client.delete_data("Wallets", {"private_key": private_key, "mint_id": mint_id})
