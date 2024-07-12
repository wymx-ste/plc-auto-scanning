import pytest
from xml.etree.ElementTree import fromstring
from src.sfcs import sfcs_lib

# Sample XML response content for mocking.
sample_response_content = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <DynamicDBFunctionResponse xmlns="http://localhost/Tester.WebService/WebService">
            <DynamicDBFunctionResult>OK</DynamicDBFunctionResult>
        </DynamicDBFunctionResponse>
    </soap:Body>
</soap:Envelope>"""


@pytest.fixture
def mock_response(mocker):
    """Mock the response object."""
    response = mocker.Mock()
    response.content = sample_response_content
    return response


@pytest.fixture
def mock_post_request(mocker):
    """Mock the post_request function."""
    return mocker.patch("src.sfcs.sfcs_lib.post_request")


@pytest.fixture
def mock_find_xml_value(mocker):
    """Mock the find_xml_value function."""
    return mocker.patch("src.sfcs.sfcs_lib.find_xml_value")


def test_find_xml_value():

    # Convert the XML content to an ElementTree object.
    tree = fromstring(sample_response_content)

    # Test the function without splitting.
    result = sfcs_lib.find_xml_value(tree, ".//a:DynamicDBFunctionResult")
    assert result == "OK"

    # Test the function with splitting.
    sample_response_content_split = sample_response_content.replace("OK", "OK.123")
    tree = fromstring(sample_response_content_split)
    result = sfcs_lib.find_xml_value(tree, ".//a:DynamicDBFunctionResult", split=True)
    assert result == "OK"

    # Test the function with an invalid path.
    result = sfcs_lib.find_xml_value(tree, ".//a:InvalidPath")
    assert result is None


def test_post_request(mocker, mock_response):
    mock_post = mocker.patch("requests.post", return_value=mock_response)
    body = "<test>test</test>"
    endpoint = "test_endpoint"
    response_tree = sfcs_lib.post_request(body, endpoint)
    assert response_tree is not None
    assert (
        sfcs_lib.find_xml_value(response_tree, ".//a:DynamicDBFunctionResult") == "OK"
    )
    mock_post.assert_called_once_with(
        f"http://{sfcs_lib.SFCS_SERVER}/{endpoint}", data=body, headers=sfcs_lib.HEADERS
    )


def test_generate_soap_body():
    # Test the function with a sample query and parameters.
    query = """
        <CheckRoute xmlns="http://localhost/Tester.WebService/WebService">
            <UnitSerialNumber>{usn}</UnitSerialNumber>
            <StageCode>{stage}</StageCode>
        </CheckRoute>
    """

    params = {"usn": "12345", "stage": "AO"}

    expected_body = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
        <CheckRoute xmlns="http://localhost/Tester.WebService/WebService">
            <UnitSerialNumber>12345</UnitSerialNumber>
            <StageCode>AO</StageCode>
        </CheckRoute>

        </soap:Body>
    </soap:Envelope>
    """

    body = sfcs_lib.generate_soap_body(query, **params)

    # Normalize withe space for comparison.
    normalized_body = " ".join(body.split())
    normalized_expected_body = " ".join(expected_body.split())
    assert normalized_body == normalized_expected_body


def test_check_route(mock_post_request, mock_find_xml_value):
    usn = "12345"
    stage = "AO"
    mock_tree = fromstring(sample_response_content)
    mock_post_request.return_value = mock_tree
    mock_find_xml_value.return_value = "OK"

    result = sfcs_lib.check_route(usn, stage)
    assert result == "OK"


def test_upload_USN_item_with_barcode_validation(
    mock_post_request, mock_find_xml_value
):
    usn = "12345"
    csn = "54321"
    line = "1"
    workstation = "1"
    employee_id = "1"
    stage = "AO"
    mock_tree = fromstring(sample_response_content)
    mock_post_request.return_value = mock_tree
    mock_find_xml_value.return_value = "OK"

    result = sfcs_lib.upload_USN_item_with_barcode_validation(
        usn, csn, line, workstation, employee_id, stage
    )
    assert result == "OK"


def test_send_complete_to_sfcs(mock_post_request, mock_find_xml_value):
    usn = "12345"
    stage = "AO"
    station = "2"
    username = "test_user"
    mock_tree = fromstring(sample_response_content)
    mock_post_request.return_value = mock_tree
    mock_find_xml_value.return_value = "OK"

    result = sfcs_lib.send_complete(usn, station, station, username, stage)
    assert result == "OK"


def test_validate_hdd(mock_post_request, mock_find_xml_value):
    usn = "12345"
    mock_tree = fromstring(sample_response_content)
    mock_post_request.return_value = mock_tree
    mock_find_xml_value.return_value = "24"

    result = sfcs_lib.validate_hdd(usn)
    assert result == "24"
