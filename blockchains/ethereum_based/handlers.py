from setup import config
from .handler_base import EthereumHandlerBase


class EthereumHandler(EthereumHandlerBase):
    def get_payment_wallet(self) -> str:
        return config.blockchains.ethereum.payment_wallet
