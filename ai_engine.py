from openai import OpenAI, APIConnectionError

client = OpenAI()

def analyse_job(job_description):
    try:
        response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Extract every technical skill explicitly required in this job description. Include programming languages, tools, frameworks, databases and APIs. Return only skill names separated by commas. Do not include explanations, examples, parentheses or numbering. Do not invent skills:\n\n{job_description}"
    )
    except APIConnectionError:
        print("Unable to connect to OpenAI. Please check your internet connection.")
        raise

    skills = [skill.strip().lower() for skill in response.output_text.split(",")]
    return skills

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

    skills = [skill.strip().lower() for skill in response.output_text.split(",")]
    return skills
