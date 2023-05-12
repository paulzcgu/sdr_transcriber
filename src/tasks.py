from Queue import Queue


class Tasks():
    def __init__(self):
        self._scp_queue = Queue()
        self._wsp_queue = Queue()
