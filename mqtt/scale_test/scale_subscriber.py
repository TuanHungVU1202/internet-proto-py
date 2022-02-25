import json
import time
from sqlite3 import OperationalError

import paho.mqtt.client as mqtt

import constant
import util
from mqtt import db_handler
from mqtt.mqtt_helper import get_client_object_id

client_list = []
client_info = {}
client_message_received = {}
client_delay = {}
MQTT_TOPIC_BASE = 'InternetProtocol/Scale/Road/'


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Unable to connect to MQTT Broker...")
    else:
        topic = client_info['topic']
        client.subscribe(topic)
        print("Subscribed topic: " + topic)


# Save Data into DB Table
def on_message(client, userdata, message):
    time_received = util.get_current_timestamp()
    topic = message.topic
    msg = message.payload.decode("utf-8")
    # TODO: write delay to file
    msg_json = json.loads(msg)
    time_sent = msg_json['time_sent']
    msg_id = msg_json['file_index']
    delay = time_received - time_sent
    delay_list = [delay]
    client_obj_id = get_client_object_id(client)

    if client_obj_id in client_message_received:
        client_message_received[client_obj_id] += 1
        client_delay[client_obj_id].extend(delay_list)
    else:
        client_message_received[client_obj_id] = 1
        client_delay[client_obj_id] = delay_list

    # print("Sub_id - " + client_obj_id + " - msg: " + msg)
    print("Sub_id: " + client_obj_id + " received message from topic: " + topic)

    # TODO: implement queue here maybe, then pop out and save that to db
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


def disconnect():
    for client in client_list:
        client.unsubscribe(topic)
        client.disconnect()
        client.loop_stop()
        client_obj_id = get_client_object_id(client)
        print("Sub_id: " + client_obj_id + " disconnect")


def run(number_of_client, topic, unsubscribe, sub_multi_topic):
    try:
        if sub_multi_topic:
            topic = MQTT_TOPIC_BASE + "#"

        client_info['topic'] = topic
        create_client(number_of_client)
        if unsubscribe:
            time.sleep(2)
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
        print(client_delay)
        print(client_message_received)
        disconnect()


if __name__ == "__main__":
    topic = 'InternetProtocol/Scale/Road/Kauppalantie'
    # Init database table
    db_handler.create_table()
    # sub_multi_topic = subscribe to 112 topics instead of specific one from variable topic
    run(number_of_client=1,
        topic=topic,
        unsubscribe=False,
        sub_multi_topic=True)
