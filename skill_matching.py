SKILL_ALIASES = {
    "js": "javascript",
    "javascript": "javascript",
    "py": "python",
    "python": "python",
    "ml": "machine learning",
    "machine learning": "machine learning"
}

def normalise_skill(skill):
    skill = skill.strip().lower()
    return SKILL_ALIASES.get(skill, skill)

def calculate_weighted_match(detected_skills, job_matching_skills, skill_weights):
    detected_skills = set(
        normalise_skill(skill) for skill in detected_skills
    )

    job_matching_skills = set(
        normalise_skill(skill) for skill in job_matching_skills
    )

    skill_weights = {
        normalise_skill(skill): weight
        for skill, weight in skill_weights.items()
    }

    total_weight = sum(
        skill_weights.get(skill, 1)
        for skill in detected_skills
    )

    matched_weight = sum(
        skill_weights.get(skill, 1)
        for skill in job_matching_skills
        if skill in detected_skills
    )

    if total_weight == 0:
        return 0

    return (matched_weight / total_weight) * 100