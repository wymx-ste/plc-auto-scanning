from src.helpers import utils


def test_get_workstation_name():
    # Test the obtained workstation name.
    assert utils.get_workstation_name() == "3L06B1AO17"


def test_get_line():
    # Test when the workstation name is "3L06B1AO17".
    workstation = "3L06B1AO17"
    assert utils.get_line(workstation) == "3L6"
