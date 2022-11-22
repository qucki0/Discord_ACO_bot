import time
from abc import ABC, abstractmethod

from base_classes.mint import Mint
from base_classes.transaction import Transaction
from base_classes.transaction import get_all_transactions
from utilities.logging import get_logger

logger = get_logger(__name__)


class AbstractHandler(ABC):
    client: any

    @abstractmethod
    async def addition_checks(self, transaction_data: dict) -> tuple[str, float]:
        return "Something went wrong. Ping admin.", -1

    async def submit_transaction(self, transaction_info: str, member_id: int, mint: Mint,
                                 checkouts_quantity: int) -> tuple[str, float]:
        logger.info(f"Member {member_id} trying to submit {transaction_info=} for {mint.name.upper()}"
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

    async def check_transaction(self, transaction_hash: str) -> tuple[str, float]:
        if not self.is_private_key_correct(transaction_hash):
            return "Wrong input.", -1
        if await self.is_hash_already_submitted(transaction_hash):
            return "This transaction already exist.", -1
        transaction_data = await self.get_transaction(transaction_hash)
        if transaction_data is None:
            return "Transaction not found. Maybe not confirmed yet.", -1
        if not self.is_payment_address_correct(transaction_data):
            return "Wrong payment address.", -1
        return await self.addition_checks(transaction_data)

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

    @abstractmethod
    def is_payment_address_correct(self, transaction_data: dict) -> bool:
        ...

    @staticmethod
    async def is_hash_already_submitted(transaction_hash: str) -> bool:
        submitted_transactions = await get_all_transactions()
        return any(tx.hash == transaction_hash for tx in submitted_transactions)

    @abstractmethod
    async def get_transaction(self, transaction_hash: str) -> dict | None:
        ...

    @staticmethod
    @abstractmethod
    def get_currency_symbol() -> str:
        ...

    @staticmethod
    @abstractmethod
    def get_block_scan_base_link() -> str:
        ...
