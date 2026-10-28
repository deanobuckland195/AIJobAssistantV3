from jobs_api import filter_senior_jobs, filter_by_salary, filter_by_work_type, filter_by_experience

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


def test_filter_by_salary():
    jobs = [
        {"title": "Junior Developer", "salary_min": 28000},
        {"title": "IT Support", "salary_min": 22000},
        {"title": "Software Apprentice"}
    ]

    result = filter_by_salary(jobs, 25000)

    assert len(result) == 1
    assert result[0]["title"] == "Junior Developer"


def test_filter_by_work_type():
    jobs = [
        {
            "title": "Remote Python Developer",
            "description": "This is a fully remote position."
        },
        {
            "title": "Hybrid Software Developer",
            "description": "Hybrid working, three days in the office."
        },
        {
            "title": "On-site IT Support",
            "description": "This role is fully on-site."
        },
        {
            "title": "Junior Data Analyst",
            "description": "Experience with Python and SQL required."
        }
    ]

    result = filter_by_work_type(jobs, "Remote")

    assert len(result) == 1
    assert result[0]["title"] == "Remote Python Developer"


def test_hybrid_and_onsite_filters():
    jobs = [
        {
            "title": "Hybrid Developer",
            "description": "Hybrid working, two days in the office."
        },
        {
            "title": "On-site IT Support",
            "description": "This is a fully on-site position."
        },
        {
            "title": "Remote Developer",
            "description": "Fully remote working."
        }
    ]

    hybrid_jobs = filter_by_work_type(jobs, "Hybrid")
    onsite_jobs = filter_by_work_type(jobs, "On-site")

    assert len(hybrid_jobs) == 1
    assert hybrid_jobs[0]["title"] == "Hybrid Developer"

    assert len(onsite_jobs) == 1
    assert onsite_jobs[0]["title"] == "On-site IT Support"


def test_remote_filter_excludes_negated_remote_work():
    jobs = [
        {
            "title": "Office Developer",
            "description": "Remote working is not available. This is an office-based role."
        },
        {
            "title": "Remote Python Developer",
            "description": "This position is fully remote."
        }
    ]

    result = filter_by_work_type(jobs, "Remote")

    assert len(result) == 1
    assert result[0]["title"] == "Remote Python Developer"

def test_filter_by_experience():
    jobs = [
        {"title": "Junior Python Developer"},
        {"title": "Graduate Software Engineer"},
        {"title": "Software Developer Apprentice"},
        {"title": "Senior Software Engineer"}
    ]

    junior_jobs = filter_by_experience(jobs, "Junior")
    graduate_jobs = filter_by_experience(jobs, "Graduate")
    apprenticeship_jobs = filter_by_experience(jobs, "Apprenticeship")

    assert len(junior_jobs) == 1
    assert junior_jobs[0]["title"] == "Junior Python Developer"

    assert len(graduate_jobs) == 1
    assert graduate_jobs[0]["title"] == "Graduate Software Engineer"

    assert len(apprenticeship_jobs) == 1
    assert apprenticeship_jobs[0]["title"] == "Software Developer Apprentice"
