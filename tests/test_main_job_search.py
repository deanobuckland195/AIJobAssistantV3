import os
import runpy
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

def test_main_job_search(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    fake_jobs = [
        {
            "title": "Junior Python Developer",
            "description": "Required skills: Python, SQL, Git and Docker."
        },
        {
            "title": "Senior Python Engineer",
            "description": "Required skills: Python, AWS and Kubernetes."
        }
    ]

    user_inputs = [
        "Test User",
        "1",
        "python, sql, git",
        "2",
        "Junior Python Developer",
        "London",
        "1",
        "yes",
        "no"
    ]

    with patch("builtins.input", side_effect=user_inputs):
        with patch("jobs_api.search_jobs", return_value=fake_jobs):
            with patch("ai_engine.analyse_job", return_value=["python", "sql", "git", "docker"]):
                with patch("ai_engine.generate_learning_plan", return_value="Learn Docker basics."):
                    runpy.run_path(
                        str(Path(__file__).resolve().parents[1] / "main.py"),
                        run_name="__main__"
                    )
    captured = capsys.readouterr()

    assert "Junior Python Developer" in captured.out
    assert "Required skills: Python, SQL, Git and Docker." in captured.out
    assert "Recommendation: Excellent match" in captured.out
    assert "Senior Python Engineer" not in captured.out


def test_main_job_search_limited_skills(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    fake_jobs = [
        {
            "title": "Junior Python Developer",
            "description": "Required skills: Python, SQL, Git and Docker."
        }
    ]

    user_inputs = [
        "Test User",
        "1",
        "python, sql, git",
        "2",
        "Python Developer",
        "London",
        "1",
        "no",
        "no"
    ]

    with patch("builtins.input", side_effect=user_inputs):
        with patch("jobs_api.search_jobs", return_value=fake_jobs):
            with patch("ai_engine.analyse_job", return_value=["python"]):
                with patch("ai_engine.generate_learning_plan", return_value="Learn Docker basics."):
                    runpy.run_path(
                        str(Path(__file__).resolve().parents[1] / "main.py"),
                        run_name="__main__"
                    )
    captured = capsys.readouterr()

    assert "Junior Python Developer" in captured.out
    assert "Required skills: Python, SQL, Git and Docker." in captured.out
    assert "Recommendation: Limited information" in captured.out


def test_main_skip_learning_plans(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    fake_jobs = [
        {
            "title": "Junior Python Developer",
            "description": "Required skills: Python, SQL, Git and Docker."
        }
    ]

    user_inputs = [
        "Test User",
        "1",
        "python, sql, git",
        "2",
        "Junior Python Developer",
        "London",
        "1",
        "no",
        "no"
    ]

    with patch("builtins.input", side_effect=user_inputs):
        with patch("jobs_api.search_jobs", return_value=fake_jobs):
            with patch("ai_engine.analyse_job", return_value=["python", "sql", "git", "docker"]):
                runpy.run_path(
                    str(Path(__file__).resolve().parents[1] / "main.py"),
                    run_name="__main__"
                )
    report = (tmp_path / "job_analysis.txt").read_text(encoding="utf-8")

    assert "Learning plan skipped by user." in report
    assert "docker" in report.lower()


def test_main_job_comparison(capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    user_inputs = [
        "Test User",
        "1",
        "python, sql, git",
        "1",
        "Junior Python Developer. Required skills: Python, SQL, Git, Docker.",
        "END",
        "no",
        "yes",
        "1",
        "Junior Web Developer. Required skills: Python, JavaScript, HTML, CSS.",
        "END",
        "no",
        "no"
    ]

    fake_ai_skills = [
        ["python", "sql", "git", "docker"],
        ["python", "javascript", "html", "css"]
    ]

    with patch("builtins.input", side_effect=user_inputs):
        with patch("ai_engine.analyse_job", side_effect=fake_ai_skills):
            runpy.run_path(
                str(Path(__file__).resolve().parents[1] / "main.py"),
                run_name="__main__"
            )
    captured = capsys.readouterr()

    assert "Junior Python Developer - 86%" in captured.out
    assert "Junior Web Developer - 62%" in captured.out
    assert "Best match: Junior Python Developer (86%)" in captured.out



