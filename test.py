##### Helper
def get_delay_list(file_path):
    delay_list = [0]
    for index, file in enumerate(file_path): #1539 files -> index 0-1538
        if index == 0:
            continue
        delay_list.append(file_path[index] - file_path[index - 1])

def get_unique_road_list(file_path):
    pass

def get_file_list(file_path):
    pass

def get_topic_for_client(unique_road_list, no_of_clients):
    # 1, 7, 56, 112
    client_topic_dict = {}
    road_list_len = len(unique_road_list)
    road_batch = int(road_list_len/no_of_clients)
    start = 0
    stop = road_batch
    publisher_id = 0

    while start < road_list_len:
        road_list_per_client = []
        for road_index in range(start, stop):
            road_name = unique_road_list[road_index]
            road_list_per_client.append[road_name]
        start += road_batch
        stop += road_batch

        client_topic_dict[publisher_id] = road_list_per_client
        # increase publisher id after each batch
        publisher_id += 1

    return client_topic_dict

# topic = road_name
def create_data_to_publish(road_name):
    file = os.open('path')
    json_obj = json.load(file)
    data = []
    if road_name in json_obj:
        data.append[json_obj[road_name]]
    
    return data


##### Publisher
# topic = road_name
def publish_message(client, road_name, index):
    topic = 'base_path' + road_name
    time.sleep(delay_list[index])
    timestamp = time.time()

    data = create_data_to_publish(road_name)
    payload = json.dumps().encode()

    client.publish(topic, payload)
    

def main(no_of_clients):
    # run once
    file_list = get_file_list(file_dir)
    delay_list = get_delay_list(file_path)
    unique_road_list = get_unique_road_list(file_path)
    client_topic_dict = get_topic_for_client(unique_road_list, no_of_clients)
    client_list = create_client(no_of_clients)
    
    # road_name = topic
    for pub_id, road_name in client_topic_dict.items():
            for file_index in range(len(file_list)):
                publish_message(client_list[pub_id], road_name, file_index)
