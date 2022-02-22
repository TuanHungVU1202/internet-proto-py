import time

import paho.mqtt.client as mqtt

import constant


def publish_to_topic(client, topic, message):
    client.publish(topic, message)
    print("Published: " + str(message) + " " + "on MQTT Topic: " + str(topic))
    print(" ")
    time.sleep(2)


def create_client(client_number):
    client_list = []
    # connecting to the broker
    for client_id in range(client_number):
        client = mqtt.Client()
        client.connect(constant.MQTT_BROKER)
        client.loop_start()
        client_list.append(client)

    return client_list


def run(number_of_client, topic):
    try:
        client_list = create_client(number_of_client)
        n = 0

        while True:
            if topic == constant.MQTT_TOPIC_3:
                for client_id, client in enumerate(client_list):
                    publish_to_topic(client, topic + str(client_id), "testing message: " + str(client_id) + str(n))
                    n += 1
            else:
                for client_id, client in enumerate(client_list):
                    publish_to_topic(client, topic, "testing message: " + str(client_id) + str(n))
                    n += 1
    except KeyboardInterrupt:
        print("Interrupted by Keyboard")