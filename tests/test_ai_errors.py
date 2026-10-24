import os
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")

import pytest
from unittest.mock import patch
from ai_engine import analyse_job, generate_learning_plan
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