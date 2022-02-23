import time

import paho.mqtt.client as mqtt

import constant
from mqtt import db_handler

client_list = []
client_info = {}
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
    topic = message.topic
    msg = message.payload.decode("utf-8")
    # print("Sub - " + str(client) + " - msg: " + msg)
    print("\nSub - " + str(client) + " received message from topic: " + topic)
    db_handler.persist_data(msg, str(client))


def create_client(client_number):
    for client_id in range(client_number):
        client = mqtt.Client()
        client.connect(constant.MQTT_BROKER)
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
    run(number_of_client=10, topic=topic, unsubscribe=False, sub_multi_topic=True)
