from setup import config
from .handler_base import EthereumHandlerBase


class EthereumHandler(EthereumHandlerBase):
    def get_payment_wallet(self) -> str:
        return config.blockchains.ethereum.payment_wallet

    @staticmethod
    def get_currency_symbol() -> str:
        return "ETH"

    @staticmethod
    def get_block_scan_base_link() -> str:
        return "https://etherscan.io/tx/"
