import os
import sys
import socket


def main():
    pass


def get_workstation_name():
    # The workstation name, for example, "3L06B1AO17".
    if getattr(sys, "frozen", False):
        return socket.gethostname()
    else:
        return "3L06B1AO17"


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
