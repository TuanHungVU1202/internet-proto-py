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
        client = mqtt.Client("Pub - " + str(client_id))
        client.connect(constant.MQTT_BROKER)
        client.loop_start()
        client_list.append(client)

    return client_list


def run():
    try:
        client_list = create_client(1)
        n = 0
        while True:
            for client_id, client in enumerate(client_list):
                publish_to_topic(client, constant.MQTT_TOPIC_BASE, "testing message: " + str(client_id) + str(n))
                n += 1
    except KeyboardInterrupt:
        print("Interrupted by Keyboard")


if __name__ == "__main__":
    run()
