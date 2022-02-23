import json
import time

import paho.mqtt.client as mqtt

import constant
from mqtt.mqtt_helper import get_unique_road_list, get_topic_for_client, get_delay_list, create_data_to_publish
from util import get_file_list, get_full_path_file_list

MQTT_DATA_PATH_BASE = '../../resources/samples_p2/'


def create_client(client_number):
    client_list = []
    # connecting to the broker
    for client_id in range(client_number):
        client = mqtt.Client()
        client.connect(constant.MQTT_BROKER)
        client.loop_start()
        client_list.append(client)

    return client_list


# topic = road_name
def publish_message(pub_id, client, road_name, delay_list, index, file):
    topic = constant.MQTT_TOPIC_SCALE_BASE + road_name
    time.sleep(delay_list[index]/1000)
    timestamp = time.time()

    data = create_data_to_publish(file, road_name)
    payload = json.dumps(
        {"message_id": 'ss', "time_sent": timestamp, "data": data}, indent=4
    ).encode("utf8")

    print("Pub_id: " + str(pub_id) + " publishing to: " + topic)
    # print("Publishing to topic: " + topic + ' data: ' + str(payload))
    client.publish(topic, payload)


def run(number_of_client):
    try:
        # run once
        list_file_path, list_file_name, list_file_name_non_extension = get_full_path_file_list(MQTT_DATA_PATH_BASE)
        delay_list = get_delay_list(list_file_name_non_extension)

        unique_road_list = []
        for index, path in enumerate(list_file_path):
            get_unique_road_list(path, unique_road_list)

        client_topic_dict = get_topic_for_client(unique_road_list, number_of_client)
        client_list = create_client(number_of_client)
        # while True:
        # road_name = topic
        for file_index, file in enumerate(list_file_path):
            for pub_id, road_name_list in client_topic_dict.items():
                for road_name in road_name_list:
                    publish_message(pub_id, client_list[pub_id], road_name, delay_list, file_index, file)
    except KeyboardInterrupt:
        print("Interrupted by Keyboard")


if __name__ == "__main__":
    # 1, 7, 56, 112
    run(1)

