import os
import logging
import threading
from multiprocessing.pool import ThreadPool
from time import sleep
import util

import paramiko
from scp import SCPClient

logger = logging.getLogger()


class Scp_client():
    def __init__(self, scq_queue, whisper_queue,
                 local_rec_path="",
                 remote_ip="192.168.2.2",
                 remote_id="ubuntu",
                 remote_pw="dragon",
                 n_worker=2):
        self._thread = None
        self._thread_terminate = False
        self._n_worker = n_worker
        self._scp_queue = scq_queue
        self._whisper_queue = whisper_queue
        self._local_rec_path = local_rec_path
        self._remote_ip = remote_ip
        self._remote_id = remote_id
        self._remote_pw = remote_pw

    def loop_start(self):
        if self._thread is not None:
            SCP_ERR_INVAL
        self._thread_terminate = False
        self._thread = threading.Thread(target=self._thread_main)
        #self._thread.daemon = True
        self._thread.start()

    def loop_stop(self):
        if self._thread is None:
            return SCP_ERR_INVAL

        self._thread_terminate = True
        if threading.current_thread() != self._thread:
            self._thread.join()
            self._thread = None

    # scp task
    def scp_worker(self, id):
        util.name_curr_thread("SCP_S{}".format(id))
        # run until there is no more work
        ssh = paramiko.client.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self._remote_ip, username=self._remote_id,
                    password=self._remote_pw)
        logger.debug("SSH client created - id = {}".format(id))

        while True:
            if self._thread_terminate:
                break
            dir_file = self._scp_queue.get()
            if not dir_file:
                sleep(0)
            else:
                # block for a moment to simulate work
                fileName = "{}.wav".format(dir_file.decode("utf-8"))
                logger.debug("Remote file name = {}".format(fileName))
                with SCPClient(ssh.get_transport()) as scp:
                    scp.get(fileName, local_path=self._local_rec_path)
                localFile = "{}/{}".format(self._local_rec_path,
                                           os.path.basename(fileName))
                self._whisper_queue.put(localFile)
                logger.info("File Copied to local - {} by worker {}"
                            .format(localFile, id))

    # scp manager
    def scp_manager(self):
        util.name_curr_thread("SCP_M0")
        # create thread pool
        logger.debug("SCP Manager Starting ...")
        with ThreadPool(self._n_worker) as pool:
            # start consumer tasks
            _ = [pool.apply_async(self.scp_worker, args=(id,))
                 for id in range(self._n_worker)]
            # wait for all tasks to complete
            pool.close()
            pool.join()

    def _thread_main(self):
        self.scp_manager()

#TODO: CHEKC DIRECTORY

# Error Enums
SCP_ERR_INVAL = 1


# Error:
def error_string(errno):
    if errno == SCP_ERR_INVAL:
        return "Invalid function argument provided"
