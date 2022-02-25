import json


# number of unique road will be the number of publishers
def get_unique_road_list(file_path, road_list):
    input_file = open(file_path)
    road_array = json.load(input_file)

    for road in road_array:
        road_name = road['road_name']
        if road_name not in road_list:
            road_list.append(road_name)


def get_delay_list(file_list):
    delay_list = [0]
    # 1539 files -> index 0-1538
    file_list.sort()
    for index, file in enumerate(file_list):
        if index == 0:
            continue
        delay_list.append(int(file_list[index]) - int(file_list[index - 1]))

    return delay_list


def get_topic_for_client(unique_road_list, no_of_clients):
    # 1, 7, 56, 112
    client_topic_dict = {}
    road_list_len = len(unique_road_list)
    road_batch = int(road_list_len / no_of_clients)
    start = 0
    stop = road_batch
    publisher_id = 0

    while start < road_list_len:
        road_list_per_client = []
        for road_index in range(start, stop):
            road_name = unique_road_list[road_index]
            road_list_per_client.append(road_name)
        start += road_batch
        stop += road_batch

        client_topic_dict[publisher_id] = road_list_per_client
        # increase publisher id after each batch
        publisher_id += 1

    return client_topic_dict


# topic = road_name
def create_data_to_publish(file_path, road_name):
    input_file = open(file_path)
    road_array = json.load(input_file)
    data = []
    for road in road_array:
        if road_name == road['road_name']:
            data.append(road)

    return data


def get_client_object_id(client):
    client_str = str(client).replace('<', '').replace('>', '').split(' ')
    return client_str[3]
