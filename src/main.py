# -----------------
# MQTT_client as producer
# Multi-thread SCP Copier as first consumer
# whisper-python is on other process
# ------------------

import os
from multiprocessing.pool import ThreadPool
from queue import Queue
from threading import Thread
from time import sleep

import paramiko
from scp import SCPClient

from mqtt import MQTT_client

import subprocess

import util
import logging

# ----------------
# Settings
# TODO: Move to Seperate JSON file
# ----------------
util.init_logger()
logger = logging.getLogger(__name__)

HOST_MQTT = "192.168.2.1"
HOST_PI = "192.168.2.2"

TOPIC_TASKS = "SDR/station_1/whisper_remote_tasks"

MODEL_TINY = "/Users/zcgu/whispercpp/whisper.cpp/models/ggml-tiny.en.bin"
MODEL_BASE = "/Users/zcgu/whispercpp/whisper.cpp/models/ggml-base.en.bin"
MODEL_SMALL = "/Users/zcgu/whispercpp/whisper.cpp/models/ggml-small.en.bin"
MODEL_AT_USE = MODEL_BASE

N_SCP_WORKERS = 2
N_WHISPER_WORKERS = 1
N_WHISPER_THREAD = 4

LOCAL_PATH = "/Users/zcgu/sdr_transcriber/data/recordings"


def init_mqtt(scp_taskQueue):
    mqtt_client = MQTT_client(HOST_MQTT, scp_taskQueue)
    mqtt_client.subscribe(TOPIC_TASKS)
    return mqtt_client


# scp task
def scp_worker(scp_queue, whisper_queue, id):
    # run until there is no more work
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('192.168.2.2', username="ubuntu", password="dragon")
    print("SSH client created - id = {}".format(id))

    while True:
        dir_file = scp_queue.get()
        print(dir_file)
        if not dir_file:
            sleep(0)
        else:
            # block for a moment to simulate work
            fileName = "{}.wav".format(dir_file.decode("utf-8"))
            print("Remote file name = {}".format(fileName))
            with SCPClient(ssh.get_transport()) as scp:
                scp.get(fileName, local_path=LOCAL_PATH)
            print("SCP done")
            localFile = "{}/{}".format(LOCAL_PATH, os.path.basename(fileName))
            whisper_queue.put(localFile)
            print("File Copied to local - {} by worker {}"
                  .format(localFile, id))


# scp manager
def scp_manager(scp_queue, whisper_queue):
    # create thread pool
    with ThreadPool(N_SCP_WORKERS) as pool:
        # start consumer tasks
        _ = [pool.apply_async(scp_worker,
                              args=(scp_queue, whisper_queue, id,))
             for id in range(N_SCP_WORKERS)]
        # wait for all tasks to complete
        pool.close()
        pool.join()


def whisper2(dir_wav_file):
    cmd = "/Users/zcgu/whispercpp/whisper.cpp/main -t 4 -otxt -f {} -m {}" \
          .format(dir_wav_file, MODEL_AT_USE)
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output, error = process.communicate()


if __name__ == '__main__':
    # Queues:
    # scp_task is the queue to process the scp (same process multiple thread)
    # whisper_task is the queue to process the whispers (on different
    # process to ensure speed?)

    scp_tasks = Queue()
    whisper_tasks = Queue()

    # MQTT
    # --------------------
    mqtt_client = init_mqtt(scp_tasks)
    # Start the MQTT Listener:
    mqtt_client.subscribe(TOPIC_TASKS)
    mqtt_client.run()

    # SCP
    # --------------------
    # Start the SCP workers:
    scp_consumer = Thread(target=scp_manager, args=(scp_tasks, whisper_tasks,))
    scp_consumer.start()

    # Whipser
    # whisper_consumer = Thread(target=whisper_manager, args=(whisper_tasks,))
    # whisper_consumer.start()
    # whisper_consumer.join()
    while (1):
        print("whisper start listening")
        dir_wav_file = whisper_tasks.get()
        if (dir_wav_file):
            whisper2(dir_wav_file)
