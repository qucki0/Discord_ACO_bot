import json
import os

from additions.classes import Drop, ACOMember


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


mints_list = get_list_from_json("mints_list.json", Drop)
aco_members = get_list_from_json("aco_members.json", ACOMember)
payments = get_list_from_json("payments.json", Drop)
