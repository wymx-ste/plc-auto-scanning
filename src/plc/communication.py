from pycomm3 import LogixDriver
import time
from config import PLC_3L3, PLC_3L6, PLC_DELAY
import threading


def main():
    pass


def send_signal(robot, line, signal=True):
    def task():
        plc_ip = PLC_3L3 if line == "3L3" else PLC_3L6
        tag = ("OK_" if signal else "NG_") + str(robot)
        try:
            with LogixDriver(plc_ip) as plc:
                plc.write(tag, True)
                time.sleep(PLC_DELAY)
                plc.write(tag, False)
        except Exception as e:
            return

    # Start the task in a new thread.
    thread = threading.Thread(target=task)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    main()
