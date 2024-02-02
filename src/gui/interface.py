import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image
from utils.gui_utils import (
    handle_serials_submit,
    create_employee_id_window,
    create_robot_number_window,
    create_quantity_window,
    get_workstation_name,
    get_line,
    resource_path,
)

aqua = "#4dcbbd"
green = "#6ccc9c"
yellow = "#c1c95a"
persisted_data = {"employee_id": None, "current_USN": None, "counter": 0}


def create_serial_number_window():
    root = tk.Tk()
    root.title("PLC Serial Scanning App")

    root.state("zoomed")

    # Load logo image.
    logo_path = resource_path("assets/logo.png")
    logo_photo = ImageTk.PhotoImage(Image.open(logo_path))
    root.iconphoto(False, logo_photo)

    # Font Style.
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Helvetica", size=24)
    root.option_add("*Font", default_font)

    # Header frame.
    header_frame = tk.Frame(root, bg=yellow)
    header_frame.pack(fill="x", padx=20, pady=10)

    # Left column frame.
    left_frame = tk.Frame(header_frame)
    left_frame.pack(side="left", fill="both", expand=True)

    # Right column frame.
    right_frame = tk.Frame(header_frame)
    right_frame.pack(side="right", fill="both", expand=True)

    # Employee ID Label.
    employee_id_label = tk.Label(left_frame, text="Employee ID:", bg=green)
    employee_id_label.pack(fill="x", padx=5, pady=5)

    # Workstation Label.
    workstation = get_workstation_name()
    workstation_label = tk.Label(
        right_frame, text=f"Workstation: {workstation}", bg=aqua
    )
    workstation_label.pack(fill="x", padx=5, pady=5)

    # Line Label.
    line = get_line(workstation)
    line_label = tk.Label(right_frame, text=f"Line: {line}", bg=green)
    line_label.pack(fill="x", padx=5, pady=5)

    # Robot Number Label.
    robot_number_label = tk.Label(left_frame, text="Robot Number:", bg=aqua)
    robot_number_label.pack(fill="x", padx=5, pady=5)

    # Quantity Label.
    quantity_label = tk.Label(left_frame, text="Quantity:", bg=green)
    quantity_label.pack(fill="x", padx=5, pady=5)

    # Unit Serial Number Label.
    unit_serial_number_label = tk.Label(
        right_frame, text="Unit Serial Number:", bg=aqua
    )
    unit_serial_number_label.pack(fill="x", padx=5, pady=5)

    # Serial Numbers Entry.
    serial_numbers = tk.StringVar()
    tk.Label(root, text="Serial Numbers:").pack(padx=5, pady=5)
    serials_entry = tk.Entry(root, textvariable=serial_numbers, state="disabled")
    serials_entry.pack(padx=20, pady=10)
    serials_entry.bind(
        "<Return>",
        lambda event: (
            handle_serials_submit(
                serial_numbers,
                workstation,
                line,
                persisted_data,
                response_listbox,
                quantity_label,
                unit_serial_number_label,
                event,
            ),
            serial_numbers.set(""),
        ),
    )

    # Add a Listbox to display the response responses.
    response_listbox = tk.Listbox(root, height=15, width=80)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=response_listbox.yview)
    response_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    response_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Open the modal window for employee ID on top of the main window.
    create_employee_id_window(root, employee_id_label, persisted_data)

    root.update()
    root.after(100)

    create_robot_number_window(root, robot_number_label, persisted_data)

    root.update()
    root.after(100)

    create_quantity_window(root, serials_entry, quantity_label, persisted_data)

    root.mainloop()


def run_app():
    create_serial_number_window()


if __name__ == "__main__":
    run_app()
