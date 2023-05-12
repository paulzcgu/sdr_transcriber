#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import threading
import logging
from time import sleep
import util
from database import Database_client

logger = logging.getLogger()

WHISPER_DIR_DEFAULT = "/Users/zcgu/whispercpp/whisper.cpp/main"


class Whisper_client():
    def __init__(self, model, wsp_queue,
                 wsp_dir=WHISPER_DIR_DEFAULT,
                 db_path=None):
        self._wsp_dir = wsp_dir
        self._model = model
        self._thread = None
        self._wsp_queue = wsp_queue
        self._db_path = db_path

    def inference(self, dir_wav_file, _db_client):
        logger.debug("Inferencing - {}".format(dir_wav_file))
        cmd = "{} -t 4 -otxt -f {} -m {}" \
            .format(self._wsp_dir, dir_wav_file, self._model)
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output, error = process.communicate()
        freq, time = util.file_name_process(dir_wav_file)
        logger.info("F{}MHz - T{} - M={}".format(freq, time, output))
        if _db_client is not None:
            sql_query = "INSERT INTO recording ( path_to_recording, timestamp, msg_body, freq) VALUES ( \"{}\", \"{}\", \"{}\", \"{}\");".format(dir_wav_file, time, output, freq)
            logger.debug("SQL Insert: {}".format(sql_query))
            _db_client.query(sql_query)
            _db_client.commit()
            logger.debug("Written into DB")

    def loop_start(self):
        if self._thread is not None:
            WSP_ERR_INVAL
        self._thread_terminate = False
        self._thread = threading.Thread(target=self._thread_main)
        # self._thread.daemon = True
        self._thread.start()

    def loop_stop(self):
        if self._thread is None:
            return WSP_ERR_INVAL

        self._thread_terminate = True
        if threading.current_thread() != self._thread:
            self._thread.join()
            self._thread = None

    def _thread_main(self):
        self.wsp_manager()

    def wsp_manager(self):
        if self._db_path is not None:
            _db_client = Database_client(self._db_path)
        util.name_curr_thread("WSP_M0")
        while (True):
            logger.info("Whisper Module is ready...")
            dir_wav_file = self._wsp_queue.get()
            if not dir_wav_file:
                sleep(0)
            else:
                self.inference(dir_wav_file, _db_client)


# Error Enums
WSP_ERR_INVAL = 1


# Error:
def error_string(errno):
    if errno == WSP_ERR_INVAL:
        return "Invalid function argument provided"
