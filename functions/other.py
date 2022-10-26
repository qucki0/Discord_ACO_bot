import re
from typing import TypeVar

from classes.classes import Mint, ACOMember


def remove_emoji(string: str) -> str:
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


T = TypeVar("T", Mint, ACOMember)


def get_data_by_id_from_list(id_to_find: int | str, array_to_check: list[T]) -> T | None:
    id_to_find = str(id_to_find).strip().lower()
    for element in array_to_check:
        if str(element.id).lower() == id_to_find:
            return element


def get_wallets_from_string(wallets_str: str) -> list[str]:
    wallets_str = wallets_str.replace("\n", " ")
    wallets = []
    for group in wallets_str.split():
        wallets += [wallet.strip() for wallet in group.split(",") if len(wallet.strip()) != 0]
    return wallets
