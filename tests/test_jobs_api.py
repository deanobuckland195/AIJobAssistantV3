import pytest
import requests
from jobs_api import search_jobs

from unittest.mock import patch

def test_search_jobs_connection_error(monkeypatch):
    monkeypatch.setenv("ADZUNA_APP_ID", "test-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-key")

    with patch("jobs_api.requests.get", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(requests.exceptions.ConnectionError):
            search_jobs("Python Developer", "London")


def test_search_jobs_success(monkeypatch):
    monkeypatch.setenv("ADZUNA_APP_ID", "test-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test-key")

    fake_jobs = [
        {"title": "Junior Python Developer"},
        {"title": "Cyber Security Apprentice"}
    ]
    with patch("jobs_api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"results": fake_jobs}

        jobs = search_jobs("Python Developer", "London")
        assert jobs == fake_jobs