import pytest

from src.backend.logic import PLCAutoScanningLogic, tasks_queue


@pytest.fixture(autouse=True)
def patch_dependencies(mocker):
    mock_check_route = mocker.patch("src.backend.logic.check_route")
    mock_send_complete = mocker.patch("src.backend.logic.send_complete")
    mock_upload_USN_item = mocker.patch(
        "src.backend.logic.upload_USN_item_with_barcode_validation"
    )
    mock_validate_HDD = mocker.patch("src.backend.logic.validate_hdd")
    mock_send_signal = mocker.patch("src.backend.logic.send_signal")
    return {
        "check_route": mock_check_route,
        "send_complete": mock_send_complete,
        "upload_USN_item_with_barcode_validation": mock_upload_USN_item,
        "validate_hdd": mock_validate_HDD,
        "send_signal": mock_send_signal,
    }


@pytest.fixture
def app(mocker):
    app = mocker.Mock()
    app.serial_numbers.get.return_value = "WTR1234567"
    app.old_USN = "WTROLD123"
    app.current_USN = None
    app.counter = 0
    app.quantity = 24
    app.robot_number = 1
    app.line = "line1"
    app.workstation = "WS1"
    app.employee_id = "EMP1"

    return app


@pytest.fixture
def logic(app):
    return PLCAutoScanningLogic(app)


@pytest.fixture(autouse=True)
def patch_sleep(mocker):
    return mocker.patch("time.sleep", return_value=None)


# Test the handle_serials_submit method.


def test_handle_serials_submit_with_invalid_serial(logic, app, patch_dependencies):
    """Test handle_serials_submit with an invalid serial number."""
    app.serial_numbers.get.return_value = "INVALID"
    logic.handle_serials_submit()
    app.update_text_widget.assert_called_with(
        app.error_text, "Please scan a valid L10.", "red"
    )
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


def test_handle_serials_submit_with_valid_WTR_serial(logic, app):
    """Test handle_serials_submit with a valid WTR serial number."""
    logic.handle_serials_submit()
    app.update_text_widget.assert_not_called()
    assert not tasks_queue.empty()
    task, args = tasks_queue.get()
    assert task == logic.process_check_route
    assert args == ("WTR1234567",)


def test_handle_serials_submit_with_valid_USN_serial(logic, app):
    """Test handle_serials_submit with a valid USN serial number."""
    app.serial_numbers.get.return_value = "USN123"
    app.current_USN = "WTR123DDE21"
    logic.handle_serials_submit()
    app.update_text_widget.assert_not_called()
    assert not tasks_queue.empty()
    task, args = tasks_queue.get()
    assert task == logic.process_serial
    assert args == ("USN123",)


def test_handle_serials_submit_with_same_serial_number(logic, app, patch_dependencies):
    """Test handle_serials_submit with the same WTR serial number."""
    app.serial_numbers.get.return_value = "WTROLD123"
    logic.handle_serials_submit()
    app.update_text_widget.assert_called_with(
        app.error_text,
        "The current USN is the same as the scanned before.",
        "red",
    )
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


# Test the process_serial method.


def test_process_serial_with_quantity_limit(logic, app, patch_dependencies):
    """Test process_serial with the quantity limit reached."""
    app.counter = app.quantity
    logic.process_serial("SERIAL123")
    app.update_text_widget.assert_called_with(
        app.error_text, "Quantity limit reached.", "red"
    )
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


def test_process_serial_success(logic, app, patch_dependencies):
    """Test process_serial with a successful upload."""
    patch_dependencies["upload_USN_item_with_barcode_validation"].return_value = "OK"
    logic.process_serial("SERIAL123")
    app.update_text_widget.assert_called_with(
        app.response_text, "Upload Response for SERIAL123: OK", "green"
    )
    app.update_labels.assert_called_with(
        app.quantity_label, "Quantity", f"1/{app.quantity}"
    )
    assert app.counter == 1


def test_process_serial_failure(logic, app, patch_dependencies):
    """Test process_serial with a failed upload."""
    patch_dependencies["upload_USN_item_with_barcode_validation"].return_value = "ERROR"
    logic.process_serial("SERIAL123")
    app.update_text_widget.assert_called_with(
        app.error_text, "Upload Failed for SERIAL123: ERROR", "red"
    )
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


def test_process_serial_with_retry(logic, app, patch_dependencies, mocker):
    """Test process_serial with a failed upload and retry."""
    patch_dependencies["upload_USN_item_with_barcode_validation"].side_effect = [
        "unique constraint",
        "OK",
    ]
    logic.process_serial("SERIAL123")
    retry_calls = [
        mocker.call(
            app.error_text,
            "Upload Failed for SERIAL123: unique constraint",
            "red",
        ),
        mocker.call(
            app.error_text,
            "Retrying for SERIAL123 due to unique constraint error. Attempt 1",
            "orange",
        ),
        mocker.call(
            app.response_text,
            "Upload Response for SERIAL123: OK",
            "green",
        ),
    ]
    app.update_text_widget.assert_has_calls(retry_calls)
    assert app.counter == 1


def test_process_serial_with_max_retries(logic, app, patch_dependencies):
    """Test process_serial with a failed upload and max retries."""
    patch_dependencies["upload_USN_item_with_barcode_validation"].side_effect = [
        "unique constraint",
        "unique constraint",
        "unique constraint",
    ]
    logic.process_serial("SERIAL123")
    app.update_text_widget.assert_called_with(
        app.error_text,
        "Upload Failed after 3 retries for SERIAL123: unique constraint",
        "red",
    )
    assert app.counter == 0
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


# Test the process_check_route method.


def test_process_check_route_success(logic, app, patch_dependencies):
    """Test process_check_route when check route is successful."""
    serial_number = "WTR1234567"
    patch_dependencies["check_route"].return_value = "OK"
    logic.process_check_route(serial_number)
    app.update_text_widget.assert_called_with(
        app.response_text, f"USN: {serial_number}"
    )
    assert app.current_USN == serial_number


def test_process_check_route_failure(logic, app, patch_dependencies):
    """Test process_check_route when check route fails."""
    serial_number = "WTR1234567"
    error_message = "ROUTE ERROR"
    patch_dependencies["check_route"].return_value = error_message
    logic.process_check_route(serial_number)
    app.update_text_widget.assert_called_with(
        app.error_text,
        f"Check Route Failed for {serial_number}: {error_message}",
        "red",
    )
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


def test_process_check_route_with_double_WTR_serial(logic, app, patch_dependencies):
    """
    Test process_check_route when a second WTR serial is send instead
    of a validator or HDD serial number.
    """
    serial_number = "WTR1V234567"
    patch_dependencies["check_route"].return_value = "OK"
    app.current_USN = "WTR2345678"
    logic.process_check_route(serial_number)
    app.update_text_widget.assert_called_with(
        app.error_text,
        f"Please scan a valid Serial or Validator",
        "red",
    )
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


# Test the check_restart method.


def test_check_restart_when_NG(logic, app, patch_dependencies):
    """Test check_restart logic when validate_hdd returns NG."""
    current_SN = "WTRCURRENT123"
    app.current_USN = current_SN
    patch_dependencies["validate_hdd"].return_value = "NG"
    app.counter = 24
    app.quantity = 24
    logic.check_restart()
    app.update_text_widget.assert_called_with(
        app.error_text,
        f"Error: HDD Quantity and Validators Quantity don't match for {app.current_USN}",
        "red",
    )
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


def test_check_restart_mismatch(logic, app, patch_dependencies):
    """Test check_restart logic when validate_hdd returns a mismatch."""
    current_SN = "WTRCURRENT123"
    app.current_USN = current_SN
    patch_dependencies["validate_hdd"].return_value = "48"
    app.counter = 24
    app.quantity = 24
    logic.check_restart()
    app.update_text_widget.assert_called_with(
        app.error_text,
        f"HDD Quantity Mismatch for {current_SN}: Expected 24, Got 48",
        "red",
    )
    patch_dependencies["send_signal"].assert_called_with(
        app.robot_number, app.line, False
    )


def test_check_restart_complete_failure(logic, app, patch_dependencies):
    """Test check_restart logic when send_complete returns an error."""
    current_SN = "WTRCURRENT123"
    app.current_USN = current_SN
    app.counter = 72
    app.quantity = 72
    app.robot_number = 3
    patch_dependencies["send_complete"].return_value = "ERROR"
    patch_dependencies["validate_hdd"].return_value = "72"
    logic.check_restart()
    app.update_text_widget.assert_called_with(
        app.error_text,
        f"Complete Failed for {current_SN}: ERROR",
        "red",
    )
    patch_dependencies["send_complete"].assert_called_with(
        current_SN, app.line, app.workstation, app.employee_id
    )


def test_check_restart_normal_robot(logic, app, patch_dependencies):
    """Test check_restart logic when robot number is different to 3."""
    current_SN = "WTRCURRENT123"
    app.current_USN = current_SN
    patch_dependencies["validate_hdd"].return_value = "24"
    app.counter = 24
    logic.check_restart()
    assert app.counter == 0
    assert app.old_USN == current_SN
    assert app.current_USN is None


def test_check_restart_robot_3(logic, app, patch_dependencies):
    """Test check_restart logic when robot number is 3."""
    current_SN = "WTRCURRENT123"
    app.current_USN = current_SN
    app.counter = 72
    app.quantity = 72
    app.robot_number = 3
    patch_dependencies["send_complete"].return_value = "OK"
    patch_dependencies["validate_hdd"].return_value = "72"
    logic.check_restart()
    app.update_text_widget.assert_called_with(
        app.response_text,
        f"Complete Response for {current_SN}: OK",
        "green",
    )
    patch_dependencies["send_complete"].assert_called_with(
        current_SN, app.line, app.workstation, app.employee_id
    )
    assert app.counter == 0
    assert app.old_USN == current_SN
    assert app.current_USN is None
