import os
import sys
import socket
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import simpledialog, messagebox
from sfcs.sfcs_lib import (
    upload_USN_item_with_barcode_validation,
    send_complete,
    check_route,
)

# Global ThreadPoolExecutor for making the SFCS requests.
executor = ThreadPoolExecutor(max_workers=12)


def main():
    pass


def handle_serials_submit(
    serials,
    workstation,
    line,
    persisted_data,
    response_listbox,
    quantity_label,
    unit_serial_number_label,
    event=None,
):
    current_USN = persisted_data["current_USN"]
    employee_id = persisted_data["employee_id"]
    robot_number = persisted_data["robot_number"]
    serial_number = serials.get()
    if serial_number:
        # Clear the Listbox before processing a new serial number
        response_listbox.delete(0, tk.END)
        if serial_number.startswith("WTR"):
            executor.submit(
                process_check_route,
                serial_number,
                persisted_data,
                unit_serial_number_label,
                quantity_label,
                response_listbox,
            )
        else:
            if current_USN:
                executor.submit(
                    process_serial,
                    current_USN,
                    serial_number,
                    line,
                    robot_number,
                    workstation,
                    employee_id,
                    persisted_data,
                    quantity_label,
                    response_listbox,
                )
            else:
                update_listbox(response_listbox, "Please scan a valid L10.", "red")


def process_serial(
    usn,
    serial_number,
    line,
    robot_number,
    workstation,
    employee_id,
    persisted_data,
    quantity_label,
    response_listbox,
):
    response = upload_USN_item_with_barcode_validation(
        usn, serial_number, line, workstation, employee_id
    )
    if response == "OK":
        persisted_data["counter"] += 1
        update_labels(
            quantity_label,
            f"Quantity",
            f'{persisted_data["counter"]}/{persisted_data["quantity"]}',
        )
    color = "green" if response == "OK" else "red"
    update_listbox(
        response_listbox, f"Upload Response for {serial_number}: {response}", color
    )
    if persisted_data["counter"] >= persisted_data["quantity"]:
        # Send the complete for the previous USN if robot number is 3.
        if robot_number == "3":
            complete_response = send_complete(
                usn,
                line,
                workstation,
                persisted_data["employee_id"],
            )
            if complete_response != "OK":
                update_listbox(
                    response_listbox,
                    f"Complete Failed for {usn}: {complete_response}",
                    "red",
                )
            else:
                update_listbox(
                    response_listbox,
                    f"Complete Response for {usn}: {complete_response}",
                    "green",
                )
                persisted_data["counter"] = 0
                persisted_data["current_USN"] = None


def process_check_route(
    serial_number,
    persisted_data,
    unit_serial_number_label,
    quantity_label,
    response_listbox,
):
    check_route_response = check_route(serial_number)
    if check_route_response != "OK":
        update_listbox(
            response_listbox,
            f"Check Route Failed for {serial_number}: {check_route_response}",
            "red",
        )
    else:
        current_usn = persisted_data.get("current_USN")
        if not current_usn:
            persisted_data["current_USN"] = serial_number
            update_listbox(response_listbox, f"USN: {serial_number}")
            update_labels(unit_serial_number_label, "Unit Serial Number", serial_number)
            update_labels(
                quantity_label,
                f"Quantity",
                f'{persisted_data["counter"]}/{persisted_data["quantity"]}',
            )


def update_listbox(listbox, message, color=None):
    def _update():
        listbox.insert(tk.END, message)
        if color:
            listbox.itemconfig(listbox.size() - 1, {"bg": color})

    listbox.after(0, _update)


def create_employee_id_window(parent, employee_id_label, persisted_data):
    employee_id = simpledialog.askstring(
        "Employee ID", "Please enter your Employee ID:", parent=parent
    )

    allowed_users = read_allowed_users("users.txt")

    if employee_id and employee_id in allowed_users:
        persisted_data["employee_id"] = employee_id
        update_labels(employee_id_label, "Employee ID", employee_id)
    elif employee_id:
        messagebox.showwarning(
            "Unauthorized", "You are not authorized to use this application."
        )
        parent.destroy()
    else:
        parent.destroy()


def create_robot_number_window(parent, robot_number_label, persisted_data):
    robot_number = simpledialog.askstring(
        "Robot Number", "Please enter the Robot Number:", parent=parent
    )

    if robot_number:
        persisted_data["robot_number"] = robot_number
        update_labels(robot_number_label, "Robot Number", robot_number)
    else:
        parent.destroy()


def create_quantity_window(parent, serials_entry, quantity_label, persisted_data):
    quantity = simpledialog.askinteger(
        "Quantity", "Please enter the quantity to be built:"
    )
    if quantity:
        persisted_data["quantity"] = int(quantity)
        update_labels(quantity_label, "Quantity", quantity)
        serials_entry.config(state="normal")
        parent.lift()
        parent.focus_force()
        serials_entry.focus_set()
    else:
        parent.destroy()


def update_labels(label, value_text, value):
    label.config(text=f"{value_text}: {value}")


def get_workstation_name():
    # The workstation name, for example, "3L06B1AO17".
    return socket.gethostname()


def get_line(workstation):
    # Get the first 4 characters of the workstation.
    line = workstation[0:4]

    # Split the line into parts (assuming the format is like '3L06').
    parts = [line[:2], line[2:]]  # Split into '3L' and '06'

    # Remove leading zeros from the second part and combine.
    cleaned_line = parts[0] + str(int(parts[1]))

    return cleaned_line


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, "frozen", False):
        # If the application is run as a bundled executable, use the temporary folder.
        base_path = sys._MEIPASS
    else:
        script_dir = os.path.dirname(__file__)
        base_path = os.path.join(script_dir, os.pardir)

    return os.path.join(base_path, relative_path)


def find_users_file():
    # If the application is run as a bundled executable, look in the executable's directory.
    if getattr(sys, "frozen", False):
        application_path = os.path.dirname(sys.executable)
    else:
        # If it's in development, look in the project's root directory
        application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    users_file_path = os.path.join(application_path, "users.txt")
    if not os.path.exists(users_file_path):
        return None
    return users_file_path


def read_allowed_users(filename):
    try:
        with open(filename, "r") as f:
            return {line.strip() for line in f}
    except FileNotFoundError:
        return set()


if __name__ == "__main__":
    main()
