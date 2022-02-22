import json

import constant
import util


def get_unique_road_list(file_path, road_list):
    input_file = open(file_path)
    road_array = json.load(input_file)

    for road in road_array:
        road_name = road['road_name']
        if road_name not in road_list:
            road_list.append(road_name)


def get_road_data(file_path, road_name):
    input_file = open(file_path)
    road_array = json.load(input_file)
    return_road = []
    for road in road_array:
        if road_name == road['road_name']:
            return_road.append(road)

    return return_road


# use publisher_id to get responsible for each road
def create_publish_payload(publisher_id):
    ######################
    road_list = []
    list_path, list_file = util.get_full_path_file_list(constant.MQTT_DATA_PATH_BASE)

    # Get unique road list - all are 112 in this assignment
    for path in list_path:
        get_unique_road_list(path, road_list)

    ret = get_road_data(list_path[0], road_list[publisher_id])
    ########################
    timestamp = util.get_current_timestamp()
    # TODO: EACH json file, get list of road data, create payload list then feed for "data" field
    data = 'data'
    # TODO: get json file name for "message_id" field
    payload = json.dumps(
        {"message_id": "this is json file name", "time_sent": timestamp, "data": data}, indent=4
    ).encode("utf8")

    return payload


def create_topic(base_path, road_name):
    pass


create_publish_payload(9)
