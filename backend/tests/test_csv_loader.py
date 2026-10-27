import pytest
from app.data.csv_loader import loader
from app.data.data_quality import assess_data_quality, validate_url

def test_load_schemes_count_and_types():
    schemes = loader.load_schemes()
    assert len(schemes) > 4000
    assert len(schemes) == 4670

    sample = schemes[0]
    assert sample.id is not None
    assert len(sample.id) > 0
    assert sample.name is not None
    assert sample.source_url.startswith("https://")
    assert sample.level in ["Central", "State", "State/ UT", "State / UT"]

def test_url_validation():
    assert validate_url("https://www.myscheme.gov.in/schemes/108easuk") is True
    assert validate_url("http://example.com/test.pdf") is True
    assert validate_url("invalid_url") is False
    assert validate_url("") is False
    assert validate_url(None) is False

def test_data_quality_report():
    schemes = loader.get_all()
    report = assess_data_quality(schemes)
    assert report["status"] == "healthy"
    assert report["total_records"] == 4670
    assert report["unique_schemes"] == 4670
    assert report["valid_source_urls_pct"] == 100.0
