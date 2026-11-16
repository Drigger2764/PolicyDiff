from app.api.v1.endpoints.health import health_check
from app.main import root_health


def test_root_health():
    res = root_health()
    assert res["status"] == "ok"
    assert res["service"] == "PolicyDiff"
    assert res["version"] == "0.1.0"


def test_api_v1_health():
    res = health_check()
    assert res["status"] == "ok"
    assert res["service"] == "PolicyDiff"
    assert res["environment"] == "development"
