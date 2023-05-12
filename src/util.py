import logging
import time
import threading
import datetime
import os


def init_logger(logPath="logs", logging_level=logging.DEBUG):
    # instantiate logger
    logger = logging.getLogger()
    logger.setLevel(logging_level)

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-10.12s] "
                                     "[%(levelname)-5.5s]  %(message)s")

    # define handler and formatter
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logFormatter)

    fileName = "log_{}".format(time.strftime("%Y%m%d_%H%M%S"))

    fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
    fileHandler.setFormatter(logFormatter)

    # add handler to logger
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)

    logger.info("Logger Initialized")


def file_name_process(fileName):
    ex_format = "%Y%m%d-%H%M%S"
    dt_format = "%Y-%m-%d %H:%M:%S"

    fileName = os.path.basename(fileName)
    # F_145.368_20230421-045531.cf32.wav
    tmp = fileName.replace(".cf32.wav", "").split("_")
    freq = float(tmp[1])
    time = datetime.datetime.strptime(tmp[2], ex_format)
    return freq, time.strftime(dt_format)


def name_curr_thread(tName):
    thread = threading.current_thread()
    thread.name = tName
