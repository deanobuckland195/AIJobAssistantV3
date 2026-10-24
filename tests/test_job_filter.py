from jobs_api import filter_senior_jobs

def test_senior_job_filter():
    fake_jobs = [
        {"title": "Junior Python Developer"},
        {"title": "Senior Python Engineer"},
        {"title": "Software Developer Apprentice"},
    ]

    filtered_jobs = filter_senior_jobs(fake_jobs)

    assert len(filtered_jobs) == 2
    assert filtered_jobs[0]["title"] == "Junior Python Developer"
    assert filtered_jobs[1]["title"] == "Software Developer Apprentice"
