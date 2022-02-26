import json
import time
from sqlite3 import OperationalError
from threading import Lock

import paho.mqtt.client as mqtt

import constant
import util
from mqtt import db_handler, mqtt_helper
from mqtt.mqtt_helper import get_client_object_id, get_unique_road_list, get_topic_for_subscriber
from mqtt.scale_test.scale_publisher import MQTT_DATA_PATH_BASE

client_list = []
client_info = {}
client_message_received = {}
client_delay = {}
MQTT_TOPIC_BASE = 'InternetProtocol/Scale/Road/'
# sub_mode
# one_v_many: 1 sub 112 topics
# one_v_one: 1 sub 1 topic
one_to_many = 'one_to_many'
one_to_one = 'one_to_one'
unique_road_list = []
topic_client_dict = {}


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Unable to connect to MQTT Broker...")
    else:
        # 1 subscriber subscribes to 112 topics
        if client_info['sub_mode'] == one_to_many:
            topic = client_info['topic']
            client.subscribe(topic)
            client_obj_id = get_client_object_id(client)
            print("Sub_id: " + client_obj_id + " subscribed topic: " + topic)
        else:
            # sub_mode = one_to_one: 1 subscriber subscribes to 1 topic
            client_subscribe()


# Save Data into DB Table
def on_message(client, userdata, message):
    time_received = util.get_current_timestamp()
    topic = message.topic
    msg = message.payload.decode("utf-8")
    client_obj_id = get_client_object_id(client)

    msg_json = json.loads(msg)
    time_sent = msg_json['time_sent']
    delay = time_received - time_sent
    delay_list = [delay]

    if client_obj_id in client_message_received:
        client_message_received[client_obj_id] += 1
        client_delay[client_obj_id].extend(delay_list)
    else:
        client_message_received[client_obj_id] = 1
        client_delay[client_obj_id] = delay_list

    # print("Sub_id - " + client_obj_id + " - msg: " + msg)
    print("Sub_id: " + client_obj_id + " received message from topic: " + topic)
    try:
        db_handler.persist_data(msg, client_obj_id, time_received)
    except OperationalError:
        pass


def create_client(client_number):
    for client_id in range(client_number):
        client = mqtt.Client()

        client.connect(constant.MQTT_BROKER, constant.MQTT_PORT)
        client.on_connect = on_connect
        client.on_message = on_message

        client.loop_start()
        client_list.append(client)

    return client_list


def client_subscribe():
    while not len(client_list) == constant.MQTT_NO_OF_SUBSCRIBERS:
        time.sleep(0.05)

    for road, clients in topic_client_dict.items():
        for client_index in clients:
            client = client_list[client_index]
            topic = MQTT_TOPIC_BASE + road
            client.subscribe(topic)
            client_obj_id = get_client_object_id(client)
            print("Sub_id: " + client_obj_id + " subscribed topic: " + topic)


def disconnect(topic):
    for client in client_list:
        client.unsubscribe(topic)
        client.disconnect()
        client.loop_stop()
        client_obj_id = get_client_object_id(client)
        print("Sub_id: " + client_obj_id + " disconnect")


def run(number_of_client, number_of_broker, topic, unsubscribe, sub_multi_topic, sub_mode):
    try:
        global client_list
        global topic_client_dict
        # run once
        client_info['sub_mode'] = sub_mode
        # 1 subscriber subscribes to 1 topic
        if sub_mode == one_to_one:
            list_file_path, list_file_name, list_file_name_non_extension = util.get_full_path_file_list(
                MQTT_DATA_PATH_BASE)
            for index, path in enumerate(list_file_path):
                get_unique_road_list(path, unique_road_list)

            topic_client_dict = get_topic_for_subscriber(unique_road_list, constant.MQTT_NO_OF_SUBSCRIBERS)
            # Wait until finish distributing clients for each topic
            while not len(topic_client_dict) == constant.MQTT_NO_OF_TOPIC:
                time.sleep(0.1)

        # 1 subscriber subscribes to 112 topics
        if sub_multi_topic and sub_mode != one_to_one:
            topic = MQTT_TOPIC_BASE + "#"

        client_info['topic'] = topic
        create_client(number_of_client)

        if unsubscribe:
            time.sleep(5)
            client_list[0].unsubscribe(topic)
            print('------------------------------------------------------------------------')
            print("UNSUBSCRIBED topic: " + topic + " from Sub - " + str(client_list[0]))
            print('------------------------------------------------------------------------')
            client_list[0].disconnect()
            client_list[0].loop_stop()

        while True:
            pass
    except KeyboardInterrupt:
        print("Interrupted by Keyboard")
        # file_path, file_name, pub_number, sub_number, broker_number, data
        mqtt_helper.write_result_to_file(constant.MQTT_OUTPUT_PATH,
                                         constant.MQTT_OUTPUT_DELAY,
                                         constant.MQTT_NO_OF_PUBLISHERS,
                                         number_of_client,
                                         number_of_broker,
                                         str(client_delay))
        mqtt_helper.write_result_to_file(constant.MQTT_OUTPUT_PATH,
                                         constant.MQTT_OUTPUT_MSG_RECEIVED,
                                         constant.MQTT_NO_OF_PUBLISHERS,
                                         number_of_client,
                                         number_of_broker,
                                         str(client_message_received))
        disconnect(topic)


if __name__ == "__main__":
    sample_topic = 'InternetProtocol/Scale/Road/Kauppalantie'
    # Init database table
    db_handler.create_table()

    # sub_multi_topic = subscribe to 112 topics instead of specific one from variable topic

    # Un-subscription case - Run publisher first
    # run(number_of_client=constant.MQTT_NO_OF_SUBSCRIBERS,
    #     number_of_broker=1,
    #     topic=sample_topic,
    #     unsubscribe=True,
    #     sub_multi_topic=True,
    #     sub_mode=one_to_many)

    run(number_of_client=constant.MQTT_NO_OF_SUBSCRIBERS,
        number_of_broker=1,
        topic=sample_topic,
        unsubscribe=False,
        sub_multi_topic=True,
        sub_mode=one_to_one)
