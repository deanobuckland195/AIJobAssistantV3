import os
import requests
from requests.exceptions import RequestException


BASE_URL = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

def search_jobs(keywords, location):
    """Search for UK job vacancies by keywords and location."""
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise ValueError("Adzuna API credentials are missing.")

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": keywords,
        "where": location,
        "results_per_page": 10
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    return response.json().get("results", [])

if __name__ == "__main__":
    keywords = input("What type of technology job are you looking for? ")
    location = input("Where would you like to work? ")

    try:
        jobs = search_jobs(keywords, location)
    except RequestException:
        print("Unable to retrieve jobs. Please check your connection and try again.")
        raise SystemExit
    
    if not jobs:
        print("No jobs found. Try different keywords or another location.")

    for job in jobs:
        print(job["title"])
        print("Company:", job.get("company", {}).get("display_name", "Unknown"))
        print("Location:", job.get("location", {}).get("display_name", "Unknown"))
        print("Apply here:", job.get("redirect_url", "Not available"))
        print("-" * 50)


def filter_senior_jobs(jobs):
    return [
        job for job in jobs
        if not any(
            word in job.get("title", "").lower()
            for word in ["senior", "lead", "principal", "director"]
        )
    ]

def filter_by_salary(jobs, minimum_salary=0, maximum_salary=0):
    filtered_jobs = []

    for job in jobs:
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        if minimum_salary > 0:
            if salary_min is None or salary_min < minimum_salary:
                continue

        if maximum_salary > 0:
            if salary_max is None or salary_max > maximum_salary:
                continue

        filtered_jobs.append(job)

    return filtered_jobs

def filter_by_work_type(jobs, work_type):
    if work_type == "Any":
        return jobs

    filtered_jobs = []

    for job in jobs:
        text = (
            job.get("title", "") + " " +
            job.get("description", "")
        ).lower()

        if work_type == "Remote":
            remote_exclusions = (
                "remote working is not available",
                "no remote working",
                "remote work is not available",
                "not a remote role",
                "no remote option"
            )

            if (
                "remote" in text
                and "hybrid" not in text
                and not any(phrase in text for phrase in remote_exclusions)
            ):
                filtered_jobs.append(job)

        elif work_type == "Hybrid":
            if "hybrid" in text:
                filtered_jobs.append(job)

        elif work_type == "On-site":
            if "on-site" in text or "onsite" in text:
                filtered_jobs.append(job)

    return filtered_jobs


def filter_by_experience(jobs, experience_level):
    if experience_level == "Any":
        return jobs

    experience_keywords = {
        "Junior": ("junior", "entry level", "entry-level"),
        "Graduate": ("graduate",),
        "Apprenticeship": ("apprentice", "apprenticeship")
    }

    keywords = experience_keywords.get(experience_level, ())

    return [
        job for job in jobs
        if any(
            keyword in job.get("title", "").lower()
            for keyword in keywords
        )
    ]


