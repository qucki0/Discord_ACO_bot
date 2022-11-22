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


class BinanceSmartChainHandler(EthereumHandlerBase):
    def get_payment_wallet(self) -> str:
        return config.blockchains.binance_smart_chain.payment_wallet

    @staticmethod
    def get_currency_symbol() -> str:
        return "BNB"

    @staticmethod
    def get_block_scan_base_link() -> str:
        return "https://bscscan.com/tx/"


class PolygonHandler(EthereumHandlerBase):
    def get_payment_wallet(self) -> str:
        return config.blockchains.polygon.payment_wallet

    @staticmethod
    def get_currency_symbol() -> str:
        return "MATIC"

    @staticmethod
    def get_block_scan_base_link() -> str:
        return "https://https://polygonscan.com//tx/"
