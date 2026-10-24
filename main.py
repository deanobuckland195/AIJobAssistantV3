from datetime import datetime
from ai_engine import analyse_job, generate_learning_plan, extract_cv_skills
from openai import APIConnectionError
from skill_matching import calculate_weighted_match
from cv_reader import read_cv
from pypdf.errors import PdfReadError
from jobs_api import search_jobs
from requests.exceptions import RequestException
from job_comparison import find_best_job

def greet_user():
    print("Welcome to the AI Job Assistant!")
    name = input("What is your name? ")
    print(f"\nWelcome, {name}!")

greet_user()

def get_user_skills():
    skills = input("\nEnter your current skills, separated by commas: ")
    skill_list = skills.split(",")
    return skill_list

print("\nHow would you like to provide your skills?")
print("1. Enter skills manually")
print("2. Analyse a PDF CV")
choice = input("Choose option 1 or 2: ")

if choice == "1":
    skill_list = get_user_skills()

elif choice == "2":
    cv_filename = input("\nEnter the filename of your CV: ")
    try:
        cv_text = read_cv(cv_filename)

    except FileNotFoundError:
        print("CV file not found. Please check the filename and try again.")
        raise SystemExit

    except PdfReadError:
        print("This PDF could not be read. Please check the file and try again.")
        raise SystemExit

    skill_list = extract_cv_skills(cv_text)

else:
    print("Invalid choice. Please restart and choose 1 or 2.")
    raise SystemExit

def show_skills(skill_list):
    print("\nYour current skills are:")

    for skill in skill_list:
        print(f"- {skill.strip()}")

show_skills(skill_list)

print("=== AI Job & Apprenticeship Assistant ===")

print("Let's find out which skills you have.")

def check_skills(user_skills, required_skills):
    matching_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill in user_skills:
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)
    return matching_skills, missing_skills

required_skills = [
    "python",
    "git",
    "sql",
    "apis",
    "machine learning",
    "javascript",
    "html",
    "css",
    "excel",
    "data analysis",
    "communication",
    "customer service"
]

skill_aliases = {
    "ml": "machine learning",
    "rest api": "apis",
    "rest api development": "apis",
    "api": "apis",
    "postgresql": "sql",
    "js": "javascript",
    "ms excel": "excel",
    "spreadsheets": "excel",
    "data analytics": "data analysis",
    "customer support": "customer service",
    "customer care": "customer service"
}

skill_weights = {
    "python": 5,
    "machine learning": 5,
    "sql": 4,
    "apis": 4,
    "git": 3,
    "docker": 2
}

user_skills = []

for skill in skill_list:
    clean_skill = skill.strip().lower()
    standard_skill = skill_aliases.get(clean_skill, clean_skill)
    user_skills.append(standard_skill)

matching_skills, missing_skills = check_skills(user_skills, required_skills)

print("\n=== AI Developer Skill Check ===")

print("\nSkills you already have:")
for skill in matching_skills:
    print(f"✓ {skill}")

print("\nSkills you should learn:")
for skill in missing_skills:
    print(f"- {skill}")

def calculate_match(matching_skills, required_skills):
    match_percentage = (len(matching_skills) / len(required_skills)) * 100
    return match_percentage
match_percentage = calculate_match(matching_skills, required_skills)

print(f"\nAI Developer Match Score: {match_percentage:.0f}%")

if match_percentage >= 80:
    print("Excellent match! You are well prepared for this role.")
elif match_percentage >= 60:
    print("Good match! You have a strong foundation.")
elif match_percentage >= 40:
    print("You're making progress. Keep developing your missing skills.")
else:
    print("You're at the beginning. Focus on building the core skills first.")


def match_job_skills(user_skills, detected_skills):
    job_matching_skills = []
    job_missing_skills = []

    for skill in detected_skills:
        if skill in user_skills:
            job_matching_skills.append(skill)
        else:
            job_missing_skills.append(skill)
    return job_matching_skills, job_missing_skills

job_comparisons = []

answer = "yes"

while answer == "yes":

    job_title = "Pasted job description"

    print("\n=== AI Job Description Analyser ===")

    print("\nHow would you like to find a job?")
    print("1. Paste a job description")
    print("2. Search real UK job vacancies")

    job_choice = input("Choose option 1 or 2: ")

    if job_choice == "1":
        job_lines = []
        print("\nPaste your job description below. Type END on a new line when finished:")

        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            job_lines.append(line)

        job_description = "\n".join(job_lines)
        if job_lines:
            job_title = job_lines[0].split(".")[0].strip()

    elif job_choice == "2":
        keywords = input("What type of technology job are you looking for? ")
        location = input("Where would you like to work? ")

        try:
            jobs = search_jobs(keywords, location)
        except RequestException:
            print("Unable to retrieve jobs. Please check your connection and try again.")
            continue

        if not jobs:
            print("No jobs found. Try different keywords or another location.")
            continue

        entry_level_terms = ("junior", "graduate", "apprentice", "trainee", "entry level")

        if any(term in keywords.lower() for term in entry_level_terms):
            jobs = [
                job for job in jobs
                if not any(
                    term in job.get("title", "").lower()
                    for term in ("senior", "principal", "director", "head of")
                )
            ]
        if not jobs:
            print("No suitable entry-level jobs found. Try different keywords or another location.")
            continue

        print("\n=== Available UK Jobs ===")

        for number, job in enumerate(jobs, start=1):
            print(f"{number}. {job.get('title', 'Unknown job')}")
            print("   Company:", job.get("company", {}).get("display_name", "Unknown"))
            print("   Location:", job.get("location", {}).get("display_name", "Unknown"))

        selected_job = input("\nEnter the number of the job you want to analyse: ")

        if not selected_job.isdigit() or not 1 <= int(selected_job) <= len(jobs):
            print("Invalid job number. Please choose a number from the list.")
            continue

        job = jobs[int(selected_job) - 1]
        job_title = job.get("title", "Unknown job")
        job_description = (
            f"Job title: {job.get('title', 'Unknown')}\n"
            f"{job.get('description', '')}"
        )
        application_link = job.get("redirect_url", "Not available")
        print("\n=== Selected Job ===")
        print("Job:", job.get("title", "Unknown"))
        print("Company:", job.get("company", {}).get("display_name", "Unknown"))
        print("Location:", job.get("location", {}).get("display_name", "Unknown"))
        print("Apply here:", application_link)

    else:
        print("Invalid choice. Please choose option 1 or 2.")
        continue

    if not job_description.strip():
        print("Please enter a job description before continuing.")
        continue

    print("\nJob description received:")
    print(job_description)
    print("\n=== AI Job Analysis ===")
    try:
        ai_skills = analyse_job(job_description)
    except APIConnectionError:
        print("Job analysis failed. Please try again.")
        continue

    detected_skills = []

    for skill in ai_skills:
        clean_skill = skill.strip().lower()
        standard_skill = skill_aliases.get(clean_skill, clean_skill)
        detected_skills.append(standard_skill)

    print("\n=== Skills Detected in Job Description ===")


    for skill in detected_skills:
        print(f"- {skill}")

    job_matching_skills, job_missing_skills = match_job_skills(user_skills, detected_skills)

    print("\n=== Your Match Against This Job ===")

    print("\nSkills you match:")
    for skill in job_matching_skills:
        print(f"✓ {skill}")

    print("\nSkills you're missing:")

    if len(job_missing_skills) > 0:
        for skill in job_missing_skills:
            print(f"- {skill}")
    else:
        print("No missing skills!")

    job_match_percentage = calculate_weighted_match(
        detected_skills,
        job_matching_skills,
        skill_weights
    )

    job_result = {
        "title": job_title,
        "score": job_match_percentage,
        "matching_skills": job_matching_skills,
        "missing_skills": job_missing_skills
    }

    job_comparisons.append(job_result)

    print(f"\nJob Match Score: {job_match_percentage:.0f}%")

    if len(detected_skills) == 0:
        print("Recommendation: No technical skills detected - unable to assess this job reliably.")
    elif len(detected_skills) == 1:
        print("Recommendation: Limited information - only one technical skill was detected.")
    elif job_match_percentage >= 80:
        print("Recommendation: Excellent match - you should apply!")
    elif job_match_percentage >= 60:
        print("Recommendation: Good match - definitely consider applying.")
    elif job_match_percentage >= 40:
        print("Recommendation: Possible match - work on the missing skills.")
    else:
        print("Recommendation: Low match - build more of the required skills first.")

    print("\n=== Your Personalised Learning Roadmap ===")

    ai_learning_plans = {}

    if len(detected_skills) == 0:
        print("No recognised technical skills were found in this job description.")
    elif len(job_missing_skills) == 0:
        print("Congratulations! You already have all the detected skills for this job!")

    else:
        generate_plans = input("Would you like learning plans for your missing skills? (yes/no): ").strip().lower()

        if generate_plans == "yes":
            for skill in job_missing_skills:
                print(f"\n{skill.upper()} Learning Plan:")

                try:
                    learning_plan = generate_learning_plan(skill)
                except APIConnectionError:
                    learning_plan = "Learning plan unavailable. Please check your connection and try again."

                ai_learning_plans[skill] = learning_plan
                print(learning_plan)

    analysis_time = datetime.now()

    try:
        with open("job_analysis.txt", "r", encoding="utf-8") as file:
            report_count = file.read().count("AI Job Assistant - Job Analysis Report")
    except FileNotFoundError:
        report_count = 0

    report_number = report_count + 1

    try:
        with open("job_analysis.txt", "a", encoding="utf-8") as file:
            file.write("\n" + "=" * 50 + "\n")
            file.write(f"AI Job Assistant - Job Analysis Report #{report_number}\n")
            file.write(f"Date: {analysis_time.strftime('%d %B %Y')}\n")
            file.write(f"Time: {analysis_time.strftime('%H:%M')}\n")
            file.write(f"Job Match Score: {job_match_percentage:.0f}%\n")

            file.write("\nMatching Skills:\n")
            for skill in job_matching_skills:
                file.write(f"- {skill}\n")

            file.write("\nMissing Skills:\n")
            for skill in job_missing_skills:
                file.write(f"- {skill}\n")

            file.write("\n=== Personalised Learning Roadmap ===\n")

            if not detected_skills:
                file.write("No recognised technical skills were found in this job description.\n")

            elif not job_missing_skills:
                file.write("You already have all the detected skills!\n")

            else:
                for skill in job_missing_skills:
                    file.write(f"\n{skill.upper()} Learning Plan:\n")
                    file.write(ai_learning_plans.get(skill, "Learning plan skipped by user.") + "\n")

    except OSError:
        print("Unable to save your job analysis. Please check the file location or permissions.")

    else:
        print("Your job analysis has been saved!")

    answer = input("\nWould you like to analyse another job? (yes/no): ").strip().lower()

if job_comparisons:
    print("\n=== Job Comparison Results ===")

    for number, job in enumerate(job_comparisons, start=1):
        print(f"{number}. {job['title']} - {job['score']:.0f}%")

    best_job = find_best_job(job_comparisons)
    
    print(f"\nBest match: {best_job['title']} ({best_job['score']:.0f}%)")












