from pycomm3 import LogixDriver
import time
from config import PLC_3L3, PLC_3L6


def main():
    pass


def send_signal(robot, line, signal=True):
    plc_ip = PLC_3L3 if line == "3L3" else PLC_3L6
    tag = ("OK_" if signal else "NG_") + str(robot)
    try:
        with LogixDriver(plc_ip) as plc:
            plc.write(tag, True)
            time.sleep(1)
            plc.write(tag, False)
    except Exception as e:
        return


if __name__ == "__main__":
    main()
