import os
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")

import pytest
from unittest.mock import patch
from ai_engine import analyse_job, generate_learning_plan, analyse_job_requirements
from openai import APIConnectionError

def test_analyse_job_connection_error():
    with patch("ai_engine.client.responses.create") as mock_create:
        mock_create.side_effect = APIConnectionError(request=None)

        with pytest.raises(APIConnectionError):
            analyse_job("Junior Python Developer")


def test_learning_plan_connection_error():
    with patch("ai_engine.client.responses.create") as mock_create:
        mock_create.side_effect = APIConnectionError(request=None)
        with pytest.raises(APIConnectionError):
            generate_learning_plan("Docker")

def test_analyse_job_removes_duplicate_skills():
    from unittest.mock import Mock

    fake_response = Mock()
    fake_response.output_text = '{"skills": ["Python", "SQL", "python", " Git "]}'

    with patch("ai_engine.client.responses.create", return_value=fake_response):
        result = analyse_job("Required skills: Python, SQL and Git.")

    assert result == ["python", "sql", "git"]

def test_analyse_job_invalid_json():
    from unittest.mock import Mock
    import json

    fake_response = Mock()
    fake_response.output_text = "This is not valid JSON"

    with patch("ai_engine.client.responses.create", return_value=fake_response):
        with pytest.raises(json.JSONDecodeError):
            analyse_job("Required skills: Python and SQL.")

def test_analyse_job_rejects_invalid_skills_type():
    from unittest.mock import Mock

    fake_response = Mock()
    fake_response.output_text = '{"skills": "Python, SQL"}'

    with patch("ai_engine.client.responses.create", return_value=fake_response):
        with pytest.raises(ValueError):
            analyse_job("Required skills: Python and SQL.")

def test_analyse_job_skill_categories():
    from unittest.mock import Mock

    fake_response = Mock()
    fake_response.output_text = (
        '{"essential_skills": ["Python", "SQL"], '
        '"desirable_skills": ["Docker"]}'
    )

    with patch("ai_engine.client.responses.create", return_value=fake_response):
        result = analyse_job_requirements(
            "Essential skills: Python and SQL. "
            "Desirable skills: Docker."
        )

    assert result == {
        "essential_skills": ["python", "sql"],
        "desirable_skills": ["docker"]
    }