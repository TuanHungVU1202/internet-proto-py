import ast
import base64
import json
import os
import time
from io import BytesIO
from os import walk

from PIL import Image

import constant


def parse_json_file_to_str(file_path):
    file = open(file_path)
    return str(json.load(file))


def parse_json_file(file_path):
    file = open(file_path)
    return json.load(file)


def pretty_print(json_data):
    obj = json.loads(json_data)
    return json.dumps(obj, indent=4)


def img_to_b64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return encoded_string


def get_serialized_img(img_id):
    image_path = "../resources/trace/gsv_" + str(img_id) + ".jpg"
    b64_str = img_to_b64(image_path).decode(constant.ENCODE_UTF8)
    return b64_str


def extract_post_img_json(received_data):
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


def extract_route_json(file_path, img_index):
    route_json_obj = parse_json_file(file_path)['route']
    # convert to list
    route = ast.literal_eval(str(route_json_obj))
    # extract image lat and long
    lat = route[img_index][0]
    long = route[img_index][1]
    return route, lat, long


def extract_coord_from_uri(uri):
    raw_coord = uri.replace('/put/', '').split("%2C")
    lat = raw_coord[0].strip()
    long = raw_coord[1].strip()
    return lat, long


# Deprecated, use next one
def get_file_list(path):
    filenames = next(walk(path), (None, None, []))[2]  # [] if no file
    return filenames


def get_full_path_file_list(dir_name):
    list_file_path = list()
    list_file_name = list()
    for (dir_path, dir_names, file_names) in os.walk(dir_name):
        # Exclude .DStore
        if file_names and not file_names[0].startswith('.'):
            list_file_path += [os.path.join(dir_path, file) for file in file_names]
            list_file_name += file_names

    return list_file_path, list_file_name


def get_current_timestamp():
    return time.time()
