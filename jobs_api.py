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


