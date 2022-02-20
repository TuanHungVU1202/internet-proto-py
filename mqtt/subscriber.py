import time

import paho.mqtt.client as mqtt

import constant

client_list = []
client_info = {}


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
    print("Subscriber - " + str(client) + " - msg: " + msg)
    # sensor_Data_Handler(message.topic, message.payload)


def create_client(client_number):
    for client_id in range(client_number):
        client = mqtt.Client()
        client.connect(constant.MQTT_BROKER)
        client.on_connect = on_connect
        client.on_message = on_message

        client.loop_start()
        client_list.append(client)

    return client_list


def run(number_of_client, topic, unsubscribe):
    try:
        if topic == constant.MQTT_TOPIC_3:
            topic = constant.MQTT_TOPIC_3 + "#"
        client_info['topic'] = topic
        create_client(number_of_client)
        if unsubscribe:
            time.sleep(10)
            client_list[0].unsubscribe(topic)
            print("Client instance - " + str(client_list[0]) + " unsubscribed topic: " + topic)
            client_list[0].disconnect()
            client_list[0].loop_stop()
        while True:
            pass
    except KeyboardInterrupt:
        print("Interrupted by Keyboard")
