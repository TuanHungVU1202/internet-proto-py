import base64
import json

import constant


def parse_json_file(file_path):
    file = open(file_path)
    return str(json.load(file))


def pretty_print(json_data):
    obj = json.loads(json_data)
    return json.dumps(obj, indent=4)


def img_to_b64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return encoded_string


def get_serialized_img(image_path):
    b64_str = img_to_b64(image_path).decode(constant.ENCODE_UTF8)
    return b64_str
