from job_comparison import find_best_job


def test_find_best_job():
    jobs = [
        {"title": "Python Developer", "score": 86},
        {"title": "Web Developer", "score": 62}
    ]

    result = find_best_job(jobs)

    assert result["title"] == "Python Developer"
    assert result["score"] == 86