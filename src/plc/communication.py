import time
import threading
import logging
from pycomm3 import LogixDriver
from config import PLC_3L3, PLC_3L6, PLC_DELAY

# Create a logger object.
logger = logging.getLogger(__name__)


def main():
    pass


def send_signal(robot, line, signal=True):
    def task():
        plc_ip = PLC_3L3 if line == "3L3" else PLC_3L6
        tag = ("OK_" if signal else "NG_") + str(robot)
        try:
            logger.info(f"Attempting to send signal to {plc_ip} for tag {tag}.")
            with LogixDriver(plc_ip) as plc:
                plc.write(tag, True)
                logger.info(f"Signal ON sent to {plc_ip} for tag {tag}.")
                time.sleep(PLC_DELAY)
                plc.write(tag, False)
                logger.info(f"Signal OFF sent to {plc_ip} for tag {plc_ip}.")
        except Exception as e:
            logger.error(
                f"Failed to send signal to {plc_ip} with tag: {tag}. Error: {e}."
            )
            return

    # Start the task in a new thread.
    thread = threading.Thread(target=task)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    main()
