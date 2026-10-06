import pytest

from app.config import Settings


@pytest.mark.parametrize(
    ("database_url", "expected"),
    [
        ("postgres://user:pass@db.example/campusloop", "postgresql+psycopg://user:pass@db.example/campusloop"),
        ("postgresql://user:pass@db.example/campusloop", "postgresql+psycopg://user:pass@db.example/campusloop"),
        ("sqlite:///./campusloop.db", "sqlite:///./campusloop.db"),
    ],
)
def test_database_url_normalization(database_url, expected):
    assert Settings(database_url=database_url).database_url == expected