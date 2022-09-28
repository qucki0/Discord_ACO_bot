import json
import os
import time

from additions.classes import Drop, ACOMember, Config, BackupData


def get_list_from_json(file_name, inner_class):
    if os.path.exists(file_name):
        with open(file_name) as file:
            json_data = json.loads(file.read())
        data = []
        for element in json_data:
            data.append(inner_class(json_file=element))
        return data
    else:
        return []


actual_mints = get_list_from_json(os.path.join("data", "actual_mints.json"), Drop)
aco_members = get_list_from_json(os.path.join("data", "aco_members.json"), ACOMember)
all_mints = get_list_from_json(os.path.join("data", "all_mints.json"), Drop)
config = Config.parse_file("config.json")
backup_data = BackupData(int(time.time()),
                         [(actual_mints, "actual_mints.json"), (aco_members, "aco_members.json"),
                          (all_mints, "all_mints.json")])
