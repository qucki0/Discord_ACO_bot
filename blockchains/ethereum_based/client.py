from web3 import Web3
from web3.eth import AsyncEth, HexStr


class EthereumClientBase:
    def __init__(self, rpc_link):
        self.w3 = Web3(Web3.AsyncHTTPProvider(rpc_link), modules={'eth': (AsyncEth,)}, middlewares=[])

    async def get_transaction(self, transaction_hash: str) -> dict:
        tx = await self.w3.eth.get_transaction(HexStr(transaction_hash))
        return tx
