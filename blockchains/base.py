import time
from abc import ABC, abstractmethod

from base_classes.mint import Mint
from base_classes.transaction import Transaction
from utilities.logging import get_logger

logger = get_logger(__name__)


class AbstractHandler(ABC):

    @abstractmethod
    async def check_transaction(self, transaction_hash: str) -> bool:
        ...

    async def submit_transaction(self, transaction_info: str, member_id: int, mint: Mint,
                                 checkouts_quantity: int) -> tuple[str, float]:
        logger.info(
            f"Member {member_id} trying to submit {transaction_info=} for {mint.name.upper()}"
            f" to pay for {checkouts_quantity=}")
        tx_hash = self.get_possible_transaction_hash_from_string(transaction_info)
        status, paid_amount = await self.check_transaction(tx_hash)
        if paid_amount != -1:
            from base_classes.payment import get_payment
            payment = await get_payment(mint.name, member_id)
            await Transaction(member_id=member_id, hash=tx_hash, amount=paid_amount, timestamp=int(time.time()))
            logger.info(
                f"Member {member_id} submitted {tx_hash=} for {mint.name.upper()} to pay for {checkouts_quantity=}")
            payment.amount_of_checkouts = max(0, payment.amount_of_checkouts - checkouts_quantity)
        return status, paid_amount

    @staticmethod
    @abstractmethod
    def is_private_key_correct(private_key: str) -> bool:
        ...

    @staticmethod
    @abstractmethod
    def is_transaction_hash_correct(transaction_hash: str) -> bool:
        ...

    @abstractmethod
    def get_possible_transaction_hash_from_string(self, some_hash: str) -> str:
        ...

    @abstractmethod
    def get_payment_wallet(self) -> str:
        ...
