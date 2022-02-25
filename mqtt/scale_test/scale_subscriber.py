import json
import time

import paho.mqtt.client as mqtt

import constant
import util
from mqtt import db_handler
from mqtt.mqtt_helper import get_client_object_id

client_list = []
client_info = {}
client_message_received = {}
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
    # For details of "sensor_Data_Handler" function please refer "sensor_data_to_db.py"
    time_received = util.get_current_timestamp()
    topic = message.topic
    msg = message.payload.decode("utf-8")
    time_sent = json.loads(msg)['time_sent']

    # TODO: write delay to file
    delay = time_received - time_sent
    client_obj_id = get_client_object_id(client)

    # print("Sub_id - " + client_obj_id + " - msg: " + msg)
    print("Sub_id: " + client_obj_id + " received message from topic: " + topic)
    db_handler.persist_data(msg, client_obj_id, time_received)


def create_client(client_number):
    for client_id in range(client_number):
        client = mqtt.Client()

        client.connect(constant.MQTT_BROKER, constant.MQTT_PORT)
        client.on_connect = on_connect
        client.on_message = on_message

        client.loop_start()
        client_list.append(client)

    return client_list


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


if __name__ == "__main__":
    # 'InternetProtocol/Scale/Road/Kauppalantie'
    topic = 'InternetProtocol/Scale/Road/Kauppalantie'
    db_handler.create_table()
    # sub_multi_topic = subscribe to 112 topics instead of specific one from variable topic
    run(number_of_client=2, topic=topic, unsubscribe=False, sub_multi_topic=True)
