import requests
from xml.etree.ElementTree import fromstring
from config import SFCS_SERVER, STAGE, CATEGORY


HEADERS = {"content-type": "text/xml"}
NAMESPACES = {
    "soap": "http://schemas.xmlsoap.org/soap/envelope/",
    "a": "http://localhost/Tester.WebService/WebService",
    "b": "http://localhost/Basic.WebService/WebService",
}


def main():
    pass


def post_request(body, endpoint):
    url = f"http://{SFCS_SERVER}/{endpoint}"
    response = requests.post(url, data=body, headers=HEADERS)
    return fromstring(response.content)


def find_xml_value(tree, path, split=False):
    result = tree.findall(path, NAMESPACES)
    try:
        return [i.text.split(".")[0] if split else i.text for i in result][0]
    except IndexError:
        return


def generate_soap_body(query, **params):
    body_template = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>{}
        </soap:Body>
    </soap:Envelope>
    """
    return body_template.format(query.format(**params))


def check_route(usn, stage=STAGE):
    body = generate_soap_body(
        """
        <CheckRoute xmlns="http://localhost/Tester.WebService/WebService">
            <UnitSerialNumber>{usn}</UnitSerialNumber>
            <StageCode>{stage}</StageCode>
        </CheckRoute>
        """,
        usn=usn,
        stage=stage,
    )
    tree = post_request(body, "Tester.WebService/WebService.asmx")
    return find_xml_value(tree, ".//a:CheckRouteResult")


def upload_USN_item_with_barcode_validation(
    usn,
    csn,
    line,
    workstation,
    employee_id,
    stage=STAGE,
    assembly="true",
    category=CATEGORY,
):
    body = generate_soap_body(
        """
        <UploadUSNItemWithBarcodeValidation xmlns="http://localhost/Tester.WebService/WebService">
            <UnitSerialNumber>{usn}</UnitSerialNumber>
            <StageCode>{stage}</StageCode>
            <ComponentSerialNumber>{csn}</ComponentSerialNumber>
            <Assembly>{assembly}</Assembly>
            <CheckUsedCategory>{category}</CheckUsedCategory>
            <Line>{line}</Line>
            <Workstation>{workstation}</Workstation>
            <UserID>{employee_id}</UserID>
        </UploadUSNItemWithBarcodeValidation>
        """,
        usn=usn,
        stage=stage,
        csn=csn,
        assembly=assembly,
        category=category,
        line=line,
        workstation=workstation,
        employee_id=employee_id,
    )
    tree = post_request(body, "Tester.WebService/WebService.asmx")
    return find_xml_value(tree, ".//a:UploadUSNItemWithBarcodeValidationResult")


def send_complete(serial_number, line, station, username, stage=STAGE):
    body = generate_soap_body(
        """
    <Complete xmlns="http://localhost/Tester.WebService/WebService">
        <UnitSerialNumber>{serial_number}</UnitSerialNumber>
        <Line>{line}</Line>
        <StageCode>{stage}</StageCode>
        <StationName>{station}</StationName>
        <EmployeeID>{username}</EmployeeID>
        <Pass>1</Pass>
        <TrnDatas>
            <TrnData></TrnData>
        </TrnDatas>
    </Complete>
    """,
        serial_number=serial_number,
        line=line,
        stage=stage,
        station=station,
        username=username,
    )
    tree = post_request(body, "Tester.WebService/WebService.asmx")
    return find_xml_value(tree, ".//a:CompleteResult")


def validate_hdd(usn):
    body = generate_soap_body(
        """
    <DynamicDBFunction xmlns="http://localhost/Tester.WebService/WebService">
      <FunctionName>FUNC_VALIDATEHDD</FunctionName>
      <Stage>AO</Stage>
      <DynamicParameters>
        <DynamicParameter>
          <strParam>P_USN</strParam>
          <strValue>{usn}</strValue>
        </DynamicParameter>
      </DynamicParameters>
    </DynamicDBFunction>

    """,
        usn=usn,
    )
    tree = post_request(body, "Tester.WebService/WebService.asmx")
    return find_xml_value(
        tree, "./soap:Body" "/a:DynamicDBFunctionResponse" "/a:DynamicDBFunctionResult"
    )


if __name__ == "__main__":
    main()
