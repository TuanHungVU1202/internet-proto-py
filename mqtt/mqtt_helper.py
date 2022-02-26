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


def get_topic_for_publisher(unique_road_list, no_of_clients):
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


def get_topic_for_subscriber(unique_road_list, no_of_clients):
    # 112, 112x3, x5, x7
    topic_client_dict = {}
    road_list_len = len(unique_road_list)
    subscriber_batch = int(no_of_clients/road_list_len)
    start = 0
    stop = subscriber_batch
    batch_id = 0

    while start < no_of_clients and batch_id < road_list_len:
        client_list_per_road = []

        for subscriber_index in range(start, stop):
            client_list_per_road.append(subscriber_index)

        start += subscriber_batch
        stop += subscriber_batch
        topic_client_dict[unique_road_list[batch_id]] = client_list_per_road
        # increase batch id after iteration
        batch_id += 1

    return  topic_client_dict


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


def write_result_to_file(file_path, file_name, pub_number, sub_number, broker_number, data):
    # file_name are: delay, message_sent, message_received
    file_path_full = file_path \
                     + file_name + '_' \
                     + str(pub_number) + '_' \
                     + str(sub_number) + '_' \
                     + str(broker_number)
    print(file_path_full)
    with open(file_path_full, 'w') as file:
        file.write(data)
