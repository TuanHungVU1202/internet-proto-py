import json


def parse_json_file(file_path):
    file = open(file_path)
    return str(json.load(file))


def pretty_print(json_data):
    obj = json.loads(json_data)
    return json.dumps(obj, indent=4)
