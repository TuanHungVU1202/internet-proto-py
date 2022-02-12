import base64
import json
from io import BytesIO

from PIL import Image

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


def extract_json(received_data):
    img = json.loads(received_data)['image']
    image_id = json.loads(received_data)['image_id']
    lat = json.loads(received_data)['lat']
    long = json.loads(received_data)['long']

    return image_id, img, lat, long


def b64_to_img(image_b64):
    img = Image.open(BytesIO(base64.b64decode(image_b64)))
    return img


def save_img_to_disk(path, img):
    img.save(path, 'PNG')
    return path
