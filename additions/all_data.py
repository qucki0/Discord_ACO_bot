import json
import os

from solana.rpc.api import Client

from classes.blockchain import Transaction
from classes.classes import Drop, ACOMember, Config, BackupData
from functions.encryption import decrypt_string
from typing import TypeVar

T = TypeVar("T", Drop, ACOMember, Transaction)


# to prevent circular import this function must be in this file
def get_list_from_json(file_name: str, inner_class: type[T]) -> list[T]:
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as file:
            string = file.read()
            if "BACKUP" == string[0:6]:
                string = decrypt_string(string)
            json_data = json.loads(string)
        data = []
        for element in json_data:
            data.append(inner_class(input_dict=element))
        return data
    else:
        return []


actual_mints = get_list_from_json(os.path.join("data", "actual_mints.json"), Drop)
aco_members = get_list_from_json(os.path.join("data", "aco_members.json"), ACOMember)
all_mints = get_list_from_json(os.path.join("data", "all_mints.json"), Drop)
submitted_transactions = get_list_from_json(os.path.join("data", "submitted_transactions.json"), Transaction)
config = Config.parse_file("config.json")
backup_data = BackupData([(actual_mints, "actual_mints.json"),
                          (aco_members, "aco_members.json"),
                          (all_mints, "all_mints.json"),
                          (submitted_transactions, "submitted_transactions.json")])
solana_client = Client(config.rpc_link)
