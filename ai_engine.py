from openai import OpenAI, APIConnectionError

client = OpenAI()


def analyse_job(job_description):
    if not job_description.strip():
        return []

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Extract only technical skills explicitly required "
                        "in the supplied job description. "
                        "Do not invent skills or provide explanations. "
                        "If no technical skills are explicitly stated, "
                        "return an empty skills list."
                    )
                },
                {
                    "role": "user",
                    "content": job_description
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "job_skills",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "skills": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["skills"],
                        "additionalProperties": False
                    }
                }
            }
        )

    except APIConnectionError:
        print("Unable to connect to OpenAI.")
        raise

    import json

    data = json.loads(response.output_text)

    if (
        not isinstance(data, dict)
        or not isinstance(data.get("skills"), list)
        or not all(isinstance(skill, str) for skill in data["skills"])
    ):
        raise ValueError("Invalid AI response: skills must be a list of strings.")

    skills = [
        skill.strip().lower()
        for skill in data["skills"]
        if skill.strip()
    ]

    return list(dict.fromkeys(skills))


def analyse_job_requirements(job_description):
    import json

    if not job_description.strip():
        return {
            "essential_skills": [],
            "desirable_skills": []
        }

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "Extract only technical skills explicitly mentioned "
                    "in the job description. "
                    "Put required or essential skills in essential_skills. "
                    "Put preferred, desirable or nice-to-have skills "
                    "in desirable_skills. "
                    "Do not invent skills. "
                    "Return empty lists when no skills qualify."
                )
            },
            {
                "role": "user",
                "content": job_description
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "job_requirements",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "essential_skills": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "desirable_skills": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": [
                        "essential_skills",
                        "desirable_skills"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    data = json.loads(response.output_text)

    if (
        not isinstance(data, dict)
        or not isinstance(data.get("essential_skills"), list)
        or not isinstance(data.get("desirable_skills"), list)
        or not all(
            isinstance(skill, str)
            for category in ("essential_skills", "desirable_skills")
            for skill in data[category]
        )
    ):
        raise ValueError("Invalid AI response: expected two lists of skills.")

    essential = list(dict.fromkeys(
        skill.strip().lower()
        for skill in data["essential_skills"]
        if skill.strip()
    ))

    desirable = list(dict.fromkeys(
        skill.strip().lower()
        for skill in data["desirable_skills"]
        if skill.strip()
    ))

    desirable = [
        skill for skill in desirable
        if skill not in essential
    ]

    return {
        "essential_skills": essential,
        "desirable_skills": desirable
    }


def generate_learning_plan(skill):
    try:
        response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Create a beginner-friendly, 5-step learning plan for {skill}. Keep each step short and practical."
    )
    except APIConnectionError:
        print("Unable to connect to OpenAI while generating the learning plan.")
        raise
    learning_plan = response.output_text.replace("**", "")
    return learning_plan

def extract_cv_skills(cv_text):
    try:
        response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"List only the technical skills found in this CV, separated by commas. Do not add explanations or numbering:\n\n{cv_text}"
        )
    except APIConnectionError:
        print("Unable to connect to OpenAI while generating the cv skills.")
        raise

    skills = [
        skill.strip().lower()
        for skill in response.output_text.split(",")
        if skill.strip().lower() not in ("", "none", "n/a", "no skills")
    ]

    return list(dict.fromkeys(skills))
