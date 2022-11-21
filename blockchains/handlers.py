from base_classes.base import SingletonBase
from base_classes.mint import Mint, Chains
from setup import config
from utilities.logging import get_logger
from .base import AbstractHandler
from .solana.handler import SolanaHandler

logger = get_logger(__name__)


class HandlersFactory(SingletonBase):
    def __init__(self):
        self.solana_handler = SolanaHandler(config.blockchains.solana.rpc_link)

    def get_handler_by_mint(self, mint: Mint) -> AbstractHandler:
        match mint.chain:
            case Chains.solana.value:
                return self.solana_handler


handlers_factory = HandlersFactory()


async def submit_transaction(transaction_info: str, member_id: int, mint: Mint,
                             checkouts_quantity: int) -> tuple[str, float]:
    handler = handlers_factory.get_handler_by_mint(mint)
    return await handler.submit_transaction(transaction_info, member_id, mint, checkouts_quantity)


def get_transaction_hash_from_string(some_hash: str, mint: Mint):
    handler = handlers_factory.get_handler_by_mint(mint)
    return handler.get_possible_transaction_hash_from_string(some_hash)


def is_private_key_correct(private_key: str, mint: Mint) -> bool:
    handler = handlers_factory.get_handler_by_mint(mint)
    return handler.is_private_key_correct(private_key)


def is_transaction_hash_correct(transaction_hash: str, mint: Mint) -> bool:
    handler = handlers_factory.get_handler_by_mint(mint)
    return handler.is_transaction_hash_correct(transaction_hash)
