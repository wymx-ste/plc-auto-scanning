import logging
import tkinter as tk
from tkinter import font, simpledialog, messagebox
from PIL import ImageTk, Image
from helpers.utils import (
    get_workstation_name,
    get_line,
    resource_path,
    read_allowed_users,
)

from backend.logic import PLCAutoScanningLogic

# Create a logger object.
logger = logging.getLogger(__name__)


class PLCAutoScanningApp:

    def __init__(self) -> None:
        self.logic = PLCAutoScanningLogic(self)
        self.aqua = "#4dcbbd"
        self.green = "#6ccc9c"
        self.yellow = "#c1c95a"
        self.employee_id = None
        self.current_USN = None
        self.counter = 0
        self.old_USN = None
        self.robot_number = None
        self.line = None
        self.quantity = None

    def create_serial_number_window(self):
        self.root = tk.Tk()
        logger.info("Application started.")
        self.root.title("PLC Auto Scanning App")
        self.root.state("zoomed")

        # Load logo image.
        logo_path = resource_path("assets/logo.png")
        logo_photo = ImageTk.PhotoImage(Image.open(logo_path))
        self.root.iconphoto(False, logo_photo)

        # Font Style.
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Helvetica", size=24)
        text_widget_font = font.Font(family="Helvetica", size=14)
        self.root.option_add("*Font", default_font)

        # Header frame.
        header_frame = tk.Frame(self.root, bg=self.yellow)
        header_frame.pack(fill="x", padx=20, pady=10)

        # Left column frame.
        left_frame = tk.Frame(header_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        # Right column frame.
        right_frame = tk.Frame(header_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        # Employee ID Label.
        self.employee_id_label = tk.Label(
            left_frame, text="Employee ID:", bg=self.green
        )
        self.employee_id_label.pack(fill="x", padx=5, pady=5)

        # Workstation Label.
        self.workstation = get_workstation_name()
        workstation_label = tk.Label(
            right_frame, text=f"Workstation: {self.workstation}", bg=self.aqua
        )
        workstation_label.pack(fill="x", padx=5, pady=5)

        # Line Label.
        self.line = get_line(self.workstation)
        line_label = tk.Label(right_frame, text=f"Line: {self.line}", bg=self.green)
        line_label.pack(fill="x", padx=5, pady=5)

        # Robot Number Label.
        self.robot_number_label = tk.Label(
            left_frame, text="Robot Number:", bg=self.aqua
        )
        self.robot_number_label.pack(fill="x", padx=5, pady=5)

        # Quantity Label.
        self.quantity_label = tk.Label(left_frame, text="Quantity:", bg=self.green)
        self.quantity_label.pack(fill="x", padx=5, pady=5)

        # Unit Serial Number Label.
        self.unit_serial_number_label = tk.Label(
            right_frame, text="Unit Serial Number:", bg=self.aqua
        )
        self.unit_serial_number_label.pack(fill="x", padx=5, pady=5)

        # Serial Numbers Entry.
        self.serial_numbers = tk.StringVar()
        tk.Label(self.root, text="Serial Numbers:").pack(padx=5, pady=5)
        self.serials_entry = tk.Entry(
            self.root, textvariable=self.serial_numbers, state="disabled"
        )
        self.serials_entry.pack(padx=20, pady=10)
        self.serials_entry.bind(
            "<Return>",
            lambda event: (
                self.logic.handle_serials_submit(event),
                self.serial_numbers.set(""),
            ),
        )

        # Main frame for Text widgets.
        main_text_frame = tk.Frame(self.root)
        main_text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure the main_text_frame to expand its children equally.
        main_text_frame.grid_columnconfigure(0, weight=1)
        main_text_frame.grid_rowconfigure(0, weight=1)
        main_text_frame.grid_rowconfigure(1, weight=1)

        # Frame for the PASS responses Text widget.
        pass_frame = tk.Frame(main_text_frame)
        pass_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # Label for the PASS responses Text widget.
        pass_label = tk.Label(pass_frame, text="PASS:", font=text_widget_font)
        pass_label.pack(side="top", fill="x")

        # Text widget to display the PASS responses.
        self.response_text = tk.Text(pass_frame, wrap="word")
        self.response_text.config(state=tk.DISABLED)
        scrollbar = tk.Scrollbar(
            pass_frame, orient="vertical", command=self.response_text.yview
        )
        self.response_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.response_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Frame for the ERROR responses Text widget.
        error_frame = tk.Frame(main_text_frame)
        error_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Label for the ERROR responses Text widget.
        error_label = tk.Label(error_frame, text="ERROR:", font=text_widget_font)
        error_label.pack(side="top", fill="x")

        # Text widget to display the ERROR responses.
        self.error_text = tk.Text(error_frame, wrap="word")
        self.error_text.config(state=tk.DISABLED)
        scrollbar = tk.Scrollbar(
            error_frame, orient="vertical", command=self.error_text.yview
        )
        self.error_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.error_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Open the modal window for employee ID on top of the main window.
        self.create_employee_id_window()

        self.root.update()
        self.root.after(100)

        self.create_robot_number_window()

        self.root.update()
        self.root.after(100)

        self.create_quantity_window()

        self.root.mainloop()

    def create_employee_id_window(self):
        employee_id = simpledialog.askstring(
            "Employee ID", "Please enter your Employee ID:", parent=self.root
        )
        logger.info(f"Employee ID entered: {employee_id}")
        allowed_users = read_allowed_users("users.txt")

        if employee_id and employee_id.upper() in allowed_users:
            self.employee_id = employee_id
            self.update_labels(self.employee_id_label, "Employee ID", employee_id)
        elif employee_id:
            messagebox.showwarning(
                "Unauthorized", "You are not authorized to use this application."
            )
            self.root.destroy()
        else:
            self.root.destroy()

    def create_robot_number_window(self):
        robot_number = simpledialog.askinteger(
            "Robot Number", "Please enter the Robot Number:", parent=self.root
        )
        logger.info(f"Robot Number entered: {robot_number}")

        if robot_number:
            self.robot_number = robot_number
            self.update_labels(self.robot_number_label, "Robot Number", robot_number)
        else:
            self.root.destroy()

    def create_quantity_window(self):
        quantity = simpledialog.askinteger(
            "Quantity", "Please enter the quantity to be built:"
        )
        logger.info(f"Quantity entered: {quantity}")
        if quantity:
            self.quantity = int(quantity)
            self.update_labels(self.quantity_label, "Quantity", quantity)
            self.serials_entry.config(state="normal")
            self.root.lift()
            self.root.focus_force()
            self.serials_entry.focus_set()
        else:
            self.root.destroy()

    def clean_text_widget(self, text_widget):
        text_widget.delete("1.0", tk.END)

    def update_text_widget(self, text_widget, message: str, color: str = None):
        def _update():

            # Enable the text widget to insert the message.
            text_widget.config(state=tk.NORMAL)

            if text_widget.get("1.0", tk.END).strip():
                text_widget.insert(tk.END, "\n")
            text_widget.insert(tk.END, message)
            text_widget.yview(tk.END)
            if color:
                text_widget.tag_add("colored", "1.0", "end")
                text_widget.tag_config(
                    "colored",
                    background=color,
                    foreground="white",
                    spacing3=5,
                )

            # Disable the text widget to prevent editing.
            text_widget.config(state=tk.DISABLED)

        text_widget.after(0, _update)

    def update_labels(self, label, value_text, value):
        label.config(text=f"{value_text}: {value}")

    def run_app(self):
        self.logic.start_tasks_workers()
        self.create_serial_number_window()


if __name__ == "__main__":
    app = PLCAutoScanningApp()
    app.run_app()
