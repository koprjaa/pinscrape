import json
from pathlib import Path
from urllib.parse import parse_qs

from pinscrape.v2 import Pinterest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name):
    return json.loads((FIXTURES / name).read_text())


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.requested_urls = []

    def get(self, url, **kwargs):
        self.requested_urls.append(url)
        return self.response


def _pinterest(tmp_path, monkeypatch):
    # Pinterest() persists data/time_epoch.json into the CWD - isolate it.
    monkeypatch.chdir(tmp_path)
    return Pinterest()


def test_search_builds_request_url_and_parses_results(tmp_path, monkeypatch):
    p = _pinterest(tmp_path, monkeypatch)
    fake = FakeSession(FakeResponse(200, _load("search_response.json")))
    p.session = fake

    urls = p.search("messi", 1)

    assert [str(u) for u in urls] == ["https://i.pinimg.com/originals/aa/bb/cc/test1.jpg"]

    # requested_urls[0] is the warm-up GET, [-1] is the real search request
    request_url = fake.requested_urls[-1]
    query_data = parse_qs(request_url.split("?", 1)[1])["data"][0]
    payload = json.loads(query_data)
    assert payload["options"]["page_size"] == "1"
    assert payload["options"]["query"] == "messi"

    # Pinterest() must isolate its epoch cache to the cwd we chdir'd into
    assert (tmp_path / "data" / "time_epoch.json").exists()


def test_search_returns_empty_list_on_non_200(tmp_path, monkeypatch):
    p = _pinterest(tmp_path, monkeypatch)
    p.session = FakeSession(FakeResponse(404, {}))

    assert p.search("messi", 1) == []


def test_get_pin_details_parses_created_at(tmp_path, monkeypatch):
    p = _pinterest(tmp_path, monkeypatch)
    p.session = FakeSession(FakeResponse(200, _load("board_response.json")))

    created_at = p.get_pin_details(username="canva", board="design-trends")

    assert created_at == "2024-01-01T00:00:00"
