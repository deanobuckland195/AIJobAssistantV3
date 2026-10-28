
from skill_matching import calculate_weighted_match, normalise_skill

user_skills = ["python", "sql", "git"]

jobs = [
    {
        "title": "Python Developer",
        "required_skills": ["python", "sql", "docker"]
    },
    {
        "title": "Cloud Developer",
        "required_skills": ["python", "git", "aws"]
    }
]

for job in jobs:
    required_skills = {
        normalise_skill(skill)
        for skill in job["required_skills"]
    }

    user_skill_set = {
        normalise_skill(skill)
        for skill in user_skills
    }

    matching_skills = sorted(required_skills & user_skill_set)
    missing_skills = sorted(required_skills - user_skill_set)

    skill_weights = {skill: 1 for skill in required_skills}

    score = calculate_weighted_match(
        required_skills,
        matching_skills,
        skill_weights
    )

    print("\nJob:", job["title"])
    print(f"Match score: {score:.0f}%")
    print("Matching skills:", matching_skills)
    print("Missing skills:", missing_skills)
