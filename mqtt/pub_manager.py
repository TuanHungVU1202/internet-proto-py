import threading

import constant
from mqtt import publisher


def run(config_number):
    if config_number == 1:
        # Main publisherse
        publishers = threading.Thread(target=publisher.run(number_of_client=3, topic=constant.MQTT_TOPIC_BASE))
        publishers.start()
    elif config_number == 2:
        publishers = threading.Thread(target=publisher.run(number_of_client=2, topic=constant.MQTT_TOPIC_2))
        publishers.start()


if __name__ == "__main__":
    run(1)
