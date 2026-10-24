import os
import runpy
from unittest.mock import patch
from pathlib import Path
from openai import APIConnectionError

os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")

def test_main_job_analysis_connection_error(capsys):
    user_inputs = [
        "Test User",
        "1",
        "python, sql, git",
        "1",
        "First job description",
        "END",
        "1",
        "Second job description",
        "END",
        "no"
    ]

    with patch("builtins.input", side_effect=user_inputs):
        with patch("ai_engine.analyse_job", side_effect=[
            APIConnectionError(request=None),
            ["python", "sql", "git"]
        ]):
            runpy.run_path(
                str(Path(__file__).resolve().parents[1] / "main.py"),
                run_name="__main__"
            )
            captured = capsys.readouterr()
            assert "Job analysis failed. Please try again." in captured.out
            assert "Job Match Score: 100%" in captured.out

def test_main_learning_plan_connection_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    user_inputs = [
        "Test User",
        "1",
        "python, sql, git",
        "1",
        "Junior AI Developer job",
        "END",
        "yes",
        "no"
    ]
    with patch("builtins.input", side_effect=user_inputs):
        with patch("ai_engine.analyse_job", return_value=["python", "sql", "git", "docker"]):
            with patch(
                    "ai_engine.generate_learning_plan",
                    side_effect=APIConnectionError(request=None)
            ):
                runpy.run_path(
                    str(Path(__file__).resolve().parents[1] / "main.py"),
                    run_name="__main__"
                )
                report = (tmp_path / "job_analysis.txt").read_text(encoding="utf-8")
                assert "Learning plan unavailable. Please check your connection and try again." in report

def test_main_report_saving_error(capsys):
    user_inputs = [
        "Test User",
        "1",
        "python, sql, git",
        "1",
        "Junior AI Developer job",
        "END",
        "no"
    ]

    real_open = open



    def fake_open(file, mode="r", *args, **kwargs):
        if str(file) == "job_analysis.txt" and mode == "a":
            raise OSError("Simulated file-saving failure")

        return real_open(file, mode, *args, **kwargs)

    with patch("builtins.input", side_effect=user_inputs):
        with patch("ai_engine.analyse_job", return_value=["python", "sql", "git"]):
            with patch("builtins.open", side_effect=fake_open):
                runpy.run_path(
                    str(Path(__file__).resolve().parents[1] / "main.py"),
                    run_name="__main__"
                )

    captured = capsys.readouterr()

    assert "Unable to save your job analysis." in captured.out
    assert "Your job analysis has been saved!" not in captured.out