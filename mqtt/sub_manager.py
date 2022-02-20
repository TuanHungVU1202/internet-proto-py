import threading

import constant
from mqtt import subscriber


def run(config_number):
    # Main subscribers
    if config_number == 1:
        subscribers = threading.Thread(target=subscriber.run(number_of_client=3, topic=constant.MQTT_TOPIC_BASE, unsubscribe=False))
        subscribers.start()
    elif config_number == 2:
        subscribers = threading.Thread(target=subscriber.run(number_of_client=2, topic=constant.MQTT_TOPIC_2, unsubscribe=False))
        subscribers.start()
    elif config_number == 3:
        subscribers = threading.Thread(target=subscriber.run(number_of_client=2, topic=constant.MQTT_TOPIC_BASE, unsubscribe=True))
        subscribers.start()


if __name__ == "__main__":
    run(3)
