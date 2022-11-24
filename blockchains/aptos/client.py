import aiohttp


class AptosClient:
    def __init__(self, rpc_link: str):
        self.rpc_link = rpc_link

    async def get_transaction(self, transaction_hash: str) -> dict | None:
        url = f"{self.rpc_link}v1/transactions/by_hash/{transaction_hash}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
        if data["vm_status"] != "Executed successfully":
            return None
        return data
