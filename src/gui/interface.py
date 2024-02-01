import tkinter as tk
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

green = "#00A36C"
blue = "#004C8C"
persisted_data = {"employee_id": None, "current_USN": None, "counter": 0}


def create_serial_number_window():
    root = tk.Tk()
    root.title("PLC Serial Scanning App")

    root.geometry("800x600")

    # Load logo image.
    logo_path = resource_path("assets/logo.png")
    logo_photo = ImageTk.PhotoImage(Image.open(logo_path))
    root.iconphoto(False, logo_photo)

    # Styling.
    label_font = ("Arial", 18, "bold")
    entry_font = ("Arial", 18)

    # Employee ID.
    employee_id_label = tk.Label(
        root, text="Employee ID:", bg=green, fg="white", font=label_font
    )
    employee_id_label.pack(fill="x", padx=5, pady=5)

    # Workstation.
    workstation = get_workstation_name()
    workstation_label = tk.Label(
        root,
        text=f"Workstation: {workstation}",
        bg=blue,
        fg="white",
        font=label_font,
    )
    workstation_label.pack(fill="x", padx=5, pady=5)

    # Line.
    line = get_line(workstation)
    line_label = tk.Label(
        root, text=f"Line: {line}", bg=green, fg="white", font=label_font
    )
    line_label.pack(fill="x", padx=5, pady=5)

    # Robot Number.
    robot_number_label = tk.Label(
        root, text="Robot Number:", bg=blue, fg="white", font=label_font
    )
    robot_number_label.pack(fill="x", padx=5, pady=5)

    # Quantity.
    quantity_label = tk.Label(
        root, text="Quantity: 0/0", bg=green, fg="white", font=label_font
    )
    quantity_label.pack(fill="x", padx=5, pady=5)

    # Unit Serial Number.
    unit_serial_number_label = tk.Label(
        root, text="Unit Serial Number:", bg=blue, fg="white", font=label_font
    )
    unit_serial_number_label.pack(fill="x", padx=5, pady=5)

    # Serial Numbers.
    serial_numbers = tk.StringVar()
    tk.Label(root, text="Serial Numbers:", font=label_font).pack(padx=5, pady=5)
    serials_entry = tk.Entry(
        root, textvariable=serial_numbers, state="disabled", font=entry_font
    )
    serials_entry.pack(padx=5, pady=5)
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
    response_listbox = tk.Listbox(root, height=15, width=90)
    response_listbox.pack(padx=10, pady=10)

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
