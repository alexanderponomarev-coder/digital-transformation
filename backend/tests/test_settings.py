from __future__ import annotations

from app.core.settings import Settings


def test_cors_origin_list_parses():
    s = Settings(cors_origins="http://a.com, http://b.com")
    assert s.cors_origin_list == ["http://a.com", "http://b.com"]


def test_cors_star():
    s = Settings(cors_origins="*")
    assert s.cors_origin_list == ["*"]
