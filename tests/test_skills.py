from skill_matching import calculate_weighted_match

def test_simple_addition():
    result = 2 + 2
    assert result == 4

def test_weighted_skill_match():
    detected_skills = ["python", "sql", "docker"]
    matching_skills = ["python", "sql"]
    skill_weights = {"python": 5, "sql": 4, "docker": 2}

    result = calculate_weighted_match(
        detected_skills,
        matching_skills,
        skill_weights
    )

    assert round(result, 2) == 81.82