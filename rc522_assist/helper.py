import logging
import time
import threading
from pirc522 import RFID

"""Assist handling reading from RFID RC522 card reader"""

LOG_LEVEL = logging.DEBUG

logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(asctime)s] %(levelname)s:%(name)s.%(funcName)s:%(message)s"
)


class RFIDHelper(object):
    """
    Helper to handle RFID card operations.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialised = False
        self.activated = False
        self.wake_event = threading.Event()
        self.done_event = threading.Event()
        self.runner = threading.Thread(target=self.do, args=(self.wake_event, self.done_event,))
        self.runner.do_run = False
        self.rc522 = RFID()

    def activate(self):
        """
        Activate the helper.
        :return: None
        """
        if self.activated:
            return

        if not self.initialised:
            self.logger.log(logging.DEBUG, "Starting !")
            self.runner.start()
            self.initialised = True
            self.runner.do_stop = False
        self.logger.log(logging.DEBUG, "Activating !")
        self.runner.do_run = True
        self.wake_event.set()
        self.logger.log(logging.DEBUG, "Activated !")
        self.activated = True

    def is_activated(self):
        """
        Return the status of the helper.
        :return: False or True
        """
        return self.activated

    def deactivate(self):
        """
        Deactivate the helper.
        :return: None
        """
        if not self.activated:
            return

        self.logger.log(logging.DEBUG, "Deactivating !")
        self.runner.do_run = False
        self.done_event.wait()
        self.clear()
        self.logger.log(logging.DEBUG, "Deactivated !")
        self.activated = False

    def terminate(self):
        """
        Terminate the helper.
        :return: None
        """
        self.logger.log(logging.DEBUG, "Terminating !")
        self.runner.do_stop = True
        self.runner.do_run = False
        self.wake_event.set()
        if self.runner.isAlive:
            try:
                self.runner.join()
            except RuntimeError:
                pass
        self.logger.log(logging.DEBUG, "Terminated !")
        self.activated = False
        self.rc522.cleanup()

    def __str__(self):
        """
        Textual definition of the helper.
        :return:
        """
        return "Helper {!s}".format(self.__class__.__name__)

    def do(self, event, done):
        """
        Perform the helper's business.
        :return: None
        """
        current_runner = threading.currentThread()
        while event.wait():
            event.clear()
            self.apply(current_runner)
            done.set()
            if getattr(current_runner, "do_stop", True):
                return

    def apply(self, current_runner):
        """
        Perform the strategy's business.
        :param current_runner: The threading runner.
        :type current_runner: threading.Event
        :return: None
        """
        try:
            while getattr(current_runner, "do_run", True):
                self.rc522.wait_for_tag()
                (error, tag_type) = self.rc522.request()
                if not error:
                    (error, uid) = self.rc522.anticoll()
                    if not error:
                        print("UID: " + str(uid))
                    else:
                        self.logger.error(error)
                else:
                    self.logger.error(error)
                time.sleep(0.1)
        except Exception as ex:
            self.logger.error(ex)


def main():
    helper = RFIDHelper()
    helper.activate()
    wait_read = 10
    wait_tempo = 2
    time.sleep(wait_read)
    helper.deactivate()
    time.sleep(wait_tempo)
    helper.terminate()

if __name__ == '__main__':
    main()
