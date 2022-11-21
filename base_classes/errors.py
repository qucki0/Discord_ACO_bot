class MintNotExist(Exception):
    def __init__(self, mint_name):
        self.mint_name = mint_name


class PaymentNotExist(Exception):
    def __init__(self, mint_name):
        self.mint_name = mint_name


class WrongCheckoutsQuantity(Exception):
    pass


class MintAlreadyExist(Exception):
    def __init__(self, mint_name):
        self.mint_name = mint_name


class WalletsNotExist(Exception):
    pass


class TransactionNotExist(Exception):
    pass
