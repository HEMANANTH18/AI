import pytest
from app.main import (
    health_check,
    dataset_status,
    list_or_search_schemes,
    get_scheme_detail,
    chat_turn,
    get_supported_languages,
    ChatMessageRequest
)

def test_health_endpoint():
    data = health_check()
    assert data["status"] == "healthy"
    assert data["schemes_loaded"] > 4000
    assert "vector_store_records" in data

def test_dataset_status_endpoint():
    data = dataset_status()
    assert "dataset_profile" in data
    assert "metadata" in data
    assert len(data["metadata"]["states"]) > 10

def test_schemes_search_and_filter():
    data = list_or_search_schemes(state="Tamil Nadu", limit=5, offset=0)
    assert "results" in data
    assert len(data["results"]) <= 5
    assert data["total"] > 0

def test_get_scheme_by_id():
    data = get_scheme_detail("108easuk")
    assert data.id == "108easuk"
    assert data.source_url.startswith("https://")

def test_chat_turn_workflow():
    req = ChatMessageRequest(
        session_id="test-session-api",
        message="I am a 35 year old farmer living in Tamil Nadu with income 180000",
        language="en"
    )
    data = chat_turn(req)
    assert data.session_id == "test-session-api"
    assert data.profile.age == 35
    assert data.profile.state == "Tamil Nadu"
    assert data.profile.occupation == "farmer"
    assert len(data.recommendations) > 0

def test_languages_endpoint():
    langs = get_supported_languages()
    codes = [l["code"] for l in langs]
    assert "en" in codes
    assert "ta" in codes
    assert "hi" in codes
