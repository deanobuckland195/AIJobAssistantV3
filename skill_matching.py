def calculate_weighted_match(detected_skills, job_matching_skills, skill_weights):
    total_weight = sum(skill_weights.get(skill, 1) for skill in detected_skills)
    matched_weight = sum(skill_weights.get(skill, 1) for skill in job_matching_skills)

    if total_weight > 0:
        return (matched_weight / total_weight) * 100
    else:
        return 0