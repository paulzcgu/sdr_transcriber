from whisper import Whisper_client
from scp_client import Scp_client
from mqtt import MQTT_client
import json
import logging
import util
from queue import Queue

util.init_logger()
logger = logging.getLogger()


def get_config():
    with open("config/settings.json") as config_file:
        configs = json.load(config_file)
    return configs


def init():
    configs = get_config()
    logger.info("*Init Seq.* - Config Loaded")

    # Task Queue
    scp_tasks = Queue()
    whisper_tasks = Queue()
    logger.info("*Init Seq.* - Queue Created")

    # MQTT client
    mqtt_client = MQTT_client(configs["HOST_MQTT"], scp_tasks)
    mqtt_client.subscribe(configs["TOPIC_TASKS"])
    mqtt_client.run()

    # SCP client
    scp_client = Scp_client(scp_tasks, whisper_tasks,
                            configs["LOCAL_REC_PATH"],
                            configs["HOST_PI"],
                            configs["SSH_ID"],
                            configs["SSH_PW"],
                            configs["N_SCP_WORKERS"])

    scp_client.loop_start()

    # Whisper client
    wsp_client = Whisper_client(configs[configs["MODEL_AT_USE"]],
                                whisper_tasks,
                                configs["WHISPER_PATH"],
                                configs["DB_PATH"])

    wsp_client.loop_start()

    while (True):
        continue


if __name__ == '__main__':
    init()
