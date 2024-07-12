import pytest
import importlib


@pytest.fixture(autouse=True)
def config(mocker):

    # Mock the environment variables.
    mocker.patch.dict(
        "os.environ",
        {
            "MAX_RETRIES": "5",
            "RETRY_DELAY": "10",
            "PLC_3L3": "3L3",
            "PLC_3L6": "3L6",
            "SFCS_SERVER": "http://sfcs.com",
            "STAGE": "PROD",
            "CATEGORY": "A",
            "PLC_DELAY": "0.5",
        },
    )

    # Reload the config module to apply the changes.
    import src.config

    importlib.reload(src.config)
    return src.config


def test_routes(config):
    assert config.ROUTES == {"GC": {1: "24", 2: "48", 3: "72"}}


def test_max_retries(config):
    assert config.MAX_RETRIES == 5


def test_retry_delay(config):
    assert config.RETRY_DELAY == 10


def test_plc_3l3(config):
    assert config.PLC_3L3 == "3L3"


def test_plc_3l6(config):
    assert config.PLC_3L6 == "3L6"


def test_sfcs_server(config):
    assert config.SFCS_SERVER == "http://sfcs.com"


def test_stage(config):
    assert config.STAGE == "PROD"


def test_category(config):
    assert config.CATEGORY == "A"


def test_plc_delay(config):
    assert config.PLC_DELAY == 0.5
