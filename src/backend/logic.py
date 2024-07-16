import time
import threading
import logging
from queue import Queue

from sfcs.sfcs_lib import (
    check_route,
    send_complete,
    upload_USN_item_with_barcode_validation,
    validate_hdd,
)

from plc.communication import send_signal
from config import MAX_RETRIES, RETRY_DELAY, ROUTES

# Create a logger object.
logger = logging.getLogger(__name__)

# Global ThreadPoolExecutor for making the SFCS requests.
tasks_queue = Queue()


class PLCAutoScanningLogic:
    def __init__(self, app):
        self.app = app

    def handle_serials_submit(self, event=None):
        serial_number = self.app.serial_numbers.get()
        if serial_number:
            if serial_number.startswith("WTR"):
                if serial_number == self.app.old_USN:
                    self.app.update_text_widget(
                        self.app.error_text,
                        f"The current USN is the same as the scanned before.",
                        "red",
                    )
                    send_signal(self.app.robot_number, self.app.line, False)
                    return
                tasks_queue.put((self.process_check_route, (serial_number,)))
            else:
                if self.app.current_USN:
                    tasks_queue.put((self.process_serial, (serial_number,)))
                else:
                    self.app.update_text_widget(
                        self.app.error_text, "Please scan a valid L10.", "red"
                    )
                    send_signal(self.app.robot_number, self.app.line, False)

    def process_serial(self, serial_number: str):
        # Check if counter is less than the quantity.
        if self.app.counter >= self.app.quantity:
            self.app.update_text_widget(
                self.app.error_text, f"Quantity limit reached.", "red"
            )
            send_signal(self.app.robot_number, self.app.line, False)
            return

        # Flag to check if the upload was successful.
        successful_upload = False

        for attempt in range(MAX_RETRIES):
            logger.info(
                f"Processing Upload for {serial_number} - Attempt {attempt + 1}"
            )
            response = upload_USN_item_with_barcode_validation(
                self.app.current_USN,
                serial_number,
                self.app.line,
                self.app.workstation,
                self.app.employee_id,
            )
            logger.info(f"Upload Response for {serial_number}: {response}")
            if response == "OK":
                self.app.counter += 1
                self.app.update_labels(
                    self.app.quantity_label,
                    "Quantity",
                    f"{self.app.counter}/{self.app.quantity}",
                )
                self.app.update_text_widget(
                    self.app.response_text,
                    f"Upload Response for {serial_number}: {response}",
                    "green",
                )
                # Mark the upload as successful.
                successful_upload = True

                # Exit the loop since upload was successful.
                break
            elif "unique constraint" in response:
                self.app.update_text_widget(
                    self.app.error_text,
                    f"Upload Failed for {serial_number}: {response}",
                    "red",
                )
                self.app.update_text_widget(
                    self.app.error_text,
                    f"Retrying for {serial_number} due to unique constraint error. Attempt {attempt + 1}",
                    "orange",
                )

                # Wait before retrying.
                time.sleep(RETRY_DELAY)
            else:
                self.app.update_text_widget(
                    self.app.error_text,
                    f"Upload Failed for {serial_number}: {response}",
                    "red",
                )
                send_signal(self.app.robot_number, self.app.line, False)

                # Break on first non-retryable error.
                break

        if not successful_upload and attempt == MAX_RETRIES - 1:
            # If after all retries, upload wasn't successful, log the final failure.
            self.app.update_text_widget(
                self.app.error_text,
                f"Upload Failed after {MAX_RETRIES} retries for {serial_number}: {response}",
                "red",
            )
            send_signal(self.app.robot_number, self.app.line, False)

        # Check if the counter needs to set to 0 and the current USN needs to be set to None.
        self.check_restart()

    def process_check_route(self, serial_number: str):
        logger.info(f"Processing Check Route for {serial_number}")
        check_route_response = check_route(serial_number)
        logger.info(f"Check Route Response for {serial_number}: {check_route_response}")
        if check_route_response != "OK":
            self.app.update_text_widget(
                self.app.error_text,
                f"Check Route Failed for {serial_number}: {check_route_response}",
                "red",
            )
            send_signal(self.app.robot_number, self.app.line, False)
        else:
            current_usn = self.app.current_USN
            if not current_usn:
                # Clear the Text widgets before processing a new serial number.
                self.app.clean_text_widget(self.app.response_text)
                self.app.clean_text_widget(self.app.error_text)
                self.app.current_USN = serial_number
                self.app.update_text_widget(
                    self.app.response_text, f"USN: {serial_number}"
                )
                self.app.update_labels(
                    self.app.unit_serial_number_label,
                    "Unit Serial Number",
                    serial_number,
                )
                self.app.update_labels(
                    self.app.quantity_label,
                    f"Quantity",
                    f"{self.app.counter}/{self.app.quantity}",
                )
            else:
                self.app.update_text_widget(
                    self.app.error_text,
                    f"Please scan a valid Serial or Validator",
                    "red",
                )
                send_signal(self.app.robot_number, self.app.line, False)

    def check_restart(self):
        should_restart = False
        if self.app.counter >= self.app.quantity:
            # Validate the quantity of HDDs scanned.
            goal_qty = ROUTES["GC"][self.app.robot_number]
            logger.info(f"Validating HDD Quantity for {self.app.current_USN}")
            current_qty = validate_hdd(self.app.current_USN)
            logger.info(
                f"Quantity Validation Response for {self.app.current_USN}: {current_qty}"
            )

            # Check for errors.
            if "NG" in current_qty:
                self.app.update_text_widget(
                    self.app.error_text,
                    f"Error: HDD Quantity and Validators Quantity don't match for {self.app.current_USN}",
                    "red",
                )
                send_signal(self.app.robot_number, self.app.line, False)
                return

            if current_qty != goal_qty:
                self.app.update_text_widget(
                    self.app.error_text,
                    f"HDD Quantity Mismatch for {self.app.current_USN}: Expected {goal_qty}, Got {current_qty}",
                    "red",
                )
                send_signal(self.app.robot_number, self.app.line, False)
                return
            else:
                # Send the complete for the previous USN if robot number is 3.
                if self.app.robot_number == 3:
                    logger.info(f"Sending Complete for {self.app.current_USN}")
                    complete_response = send_complete(
                        self.app.current_USN,
                        self.app.line,
                        self.app.workstation,
                        self.app.employee_id,
                    )
                    logger.info(
                        f"Complete Response for {self.app.current_USN}: {complete_response}"
                    )
                    if complete_response != "OK":
                        self.app.update_text_widget(
                            self.app.error_text,
                            f"Complete Failed for {self.app.current_USN}: {complete_response}",
                            "red",
                        )
                    else:
                        self.app.update_text_widget(
                            self.app.response_text,
                            f"Complete Response for {self.app.current_USN}: {complete_response}",
                            "green",
                        )
                        should_restart = True
                else:
                    should_restart = True
        if should_restart:
            self.app.counter = 0
            self.app.old_USN = self.app.current_USN
            self.app.current_USN = None

    def start_tasks_workers(self, number_of_workers=12):
        def task_worker():
            while True:
                task, args = tasks_queue.get(block=True)
                try:
                    task(*args)
                finally:
                    tasks_queue.task_done()

        for _ in range(number_of_workers):
            worker = threading.Thread(target=task_worker)
            worker.daemon = True
            worker.start()
