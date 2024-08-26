from config import logger
from gui.interface import PLCAutoScanningInterface

if __name__ == "__main__":
    app = PLCAutoScanningInterface(logger=logger)
    app.run_app()
