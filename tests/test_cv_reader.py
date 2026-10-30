import os
os.environ.setdefault("OPENAI_API_KEY", "test-key")

from pathlib import Path

import pytest
from pypdf.errors import PdfReadError

from cv_reader import read_cv

def test_read_cv_missing_file():
    with pytest.raises(ValueError):
        read_cv("nonexistent_cv.pdf")

def test_read_cv_damaged_pdf():
    pdf_path = Path(__file__).resolve().parents[1] / "broken_cv.pdf"

    with pytest.raises(ValueError):
        read_cv(pdf_path)

def test_read_cv_valid_pdf():
    pdf_path = Path(__file__).resolve().parents[1] / "cv.pdf"

    cv_text = read_cv(pdf_path)
    assert "Python" in cv_text

