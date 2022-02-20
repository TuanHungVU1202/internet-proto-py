import paho.mqtt.client as mqtt

import constant


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Unable to connect to MQTT Broker...")
    else:
        print("Connected with MQTT Broker")
        client.subscribe(constant.MQTT_TOPIC_BASE)


# Save Data into DB Table
def on_message(client, userdata, message):
    # For details of "sensor_Data_Handler" function please refer "sensor_data_to_db.py"
    print("MQTT Data Received...")
    print("MQTT Topic: " + message.topic)
    print("Data: " + message.payload.decode("utf-8"))
    # sensor_Data_Handler(message.topic, message.payload)


def create_client(client_number):
    client_list = []
    # connecting to the broker
    for client_id in range(client_number):
        client = mqtt.Client("Sub - " + str(client_id))
        client.connect(constant.MQTT_BROKER)
        client.on_connect = on_connect
        client.on_message = on_message

        client.loop_start()
        client_list.append(client)

    return client_list


def run():
    try:
        client_list = create_client(1)
        while True:
            for client_id, client in enumerate(client_list):
                pass
    except KeyboardInterrupt:
        print("Interrupted by Keyboard")


if __name__ == "__main__":
    run()
