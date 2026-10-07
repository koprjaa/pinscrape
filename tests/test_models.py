import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from pinscrape.models import BoardResponse, SearchResponse

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name):
    return json.loads((FIXTURES / name).read_text())


def test_search_response_parses_image_url():
    data = SearchResponse(**_load("search_response.json"))
    results = data.resource_response.data.results
    urls = [str(r.images["orig"].url) for r in results]
    assert urls == ["https://i.pinimg.com/originals/aa/bb/cc/test1.jpg"]


def test_search_response_allows_unknown_pinterest_fields():
    # Real Pinterest responses carry many fields this schema doesn't model.
    # resource_response.Config.extra = "allow" must keep this from raising.
    data = SearchResponse(**_load("search_response.json"))
    assert data.resource_response.model_extra.get("some_unknown_pinterest_field")


def test_search_response_rejects_invalid_image_url():
    payload = _load("search_response.json")
    payload["resource_response"]["data"]["results"][0]["images"]["orig"]["url"] = "not-a-url"
    with pytest.raises(ValidationError):
        SearchResponse(**payload)


def test_board_response_parses_created_at():
    data = BoardResponse(**_load("board_response.json"))
    assert data.resource_response.data.created_at == "2024-01-01T00:00:00"
