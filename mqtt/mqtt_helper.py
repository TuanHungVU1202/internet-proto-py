import json

import constant
import util


# number of unique road will be the number of publishers
def get_unique_road_list(file_path, road_list):
    input_file = open(file_path)
    road_array = json.load(input_file)

    for road in road_array:
        road_name = road['road_name']
        if road_name not in road_list:
            road_list.append(road_name)

    return road_list


def get_road_data(file_path, road_name):
    input_file = open(file_path)
    road_array = json.load(input_file)
    road_data = []
    for road in road_array:
        if road_name == road['road_name']:
            road_data.append(road)

    return road_data


# use publisher_id to get responsible for each road
def create_publish_payload(publisher_id):
    ##############################################################################################
    road_list = []
    road_data_list = []
    list_path, list_file, list_file_name_non_extension = util.get_full_path_file_list(constant.MQTT_DATA_PATH_BASE)

    # Get unique road list - all are 112 in this assignment => 2 ways 224
    for index, path in enumerate(list_path):
        get_unique_road_list(path, road_list)
        road_data_list = get_road_data(path, road_list[publisher_id])
    ################################################################################################
        for road_data in road_data_list:
            timestamp = util.get_current_timestamp()
            # TODO: EACH json file, get list of road data, create payload list then feed for "data" field
            # TODO: get json file name for "message_id" field
            payload = json.dumps(
                {"message_id": list_file_name_non_extension[index], "time_sent": timestamp, "data": road_data}, indent=4
            ).encode("utf8")
    ################################################################################################
    # TODO: Publish message from here or inside the previous loop
    # TODO: Divide this function into smaller ones
    return payload


def create_topic(base_path, road_name):
    pass


create_publish_payload(9)
