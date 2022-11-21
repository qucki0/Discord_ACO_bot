import re


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


def get_wallets_from_string(wallets_str: str) -> list[str]:
    wallets_str = wallets_str.replace("\n", " ")
    wallets = []
    for group in wallets_str.split():
        wallets += [wallet.strip() for wallet in group.split(",") if len(wallet.strip()) != 0]
    return wallets


def get_sql_str_from_dict(data_to_change: dict[str: int | str], separator: str, lower: bool) -> str:
    changes = []
    for key in data_to_change:
        value = data_to_change[key]
        match value:
            case str():
                if lower:
                    changes.append(f"LOWER({key}) = LOWER('{value}')")
                else:
                    changes.append(f"{key} = '{value}'")
            case int() | float():
                changes.append(f"{key} = {value}")
            case None:
                changes.append(f"{key} = NULL")
    return separator.join(changes)


def get_transaction_hash_from_string(transaction: str, is_hash_correct_function: callable) -> str:
    if "/" in transaction:
        for possible_hash in transaction.split("/"):
            possible_hash = possible_hash.strip()
            if is_hash_correct_function(possible_hash):
                return possible_hash
    return transaction.strip()
