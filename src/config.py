import os
import sys
from environs import Env

env = Env()
env.read_env()

if getattr(sys, "frozen", False):
    # If the application is run as a bundled executable.
    application_path = sys._MEIPASS
else:
    # If it's run as a regular script.
    application_path = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(application_path, ".env")
env.read_env(env_path)

PLC_3L3 = env.str("PLC_3L3")
PLC_3L6 = env.str("PLC_3L6")
SFCS_SERVER = env.str("SFCS_SERVER")
STAGE = env.str("STAGE")
CATEGORY = env.str("CATEGORY")
PLC_DELAY = env.float("PLC_DELAY")
