import streamlit as st
from ai_engine import analyse_job, generate_learning_plan, extract_cv_skills
from openai import APIConnectionError, AuthenticationError
from skill_matching import calculate_weighted_match
from cv_reader import read_cv
from jobs_api import search_jobs, filter_senior_jobs
from requests.exceptions import RequestException

st.title("AI Job Assistant V3")
st.write("Welcome to your AI-powered career assistant!")

st.subheader("Upload Your CV")
uploaded_cv = st.file_uploader(
    "Choose your CV (PDF only)",
    type=["pdf"]
)

if uploaded_cv is not None:
    st.success("CV uploaded successfully!")
    cv_text = read_cv(uploaded_cv)
    st.write("CV text extracted successfully!")
    if st.button("Extract Skills from CV"):
        if cv_text.strip():
            with st.spinner("AI is reading your CV..."):
                cv_skills = extract_cv_skills(cv_text)
                st.session_state["cv_skills"] = cv_skills

            st.success("CV skills extracted!")
            st.write("Skills found in your CV:", cv_skills)
        else:
            st.warning("No readable text found in this CV.")

user_skills = st.text_input(
    "Enter your technical skills (separated by commas):"
)

if user_skills:
    skill_list = [skill.strip().lower() for skill in user_skills.split(",")]
    st.write("Your skills:", skill_list)

st.subheader("Search UK Tech Jobs")
job_category = st.selectbox(
    "Choose a technology career:",
    [
        "Software Developer",
        "AI Engineer",
        "Machine Learning Engineer",
        "Data Analyst",
        "Cyber Security",
        "Cloud Engineer",
        "IT Support",
        "Software Tester",
        "Software Apprentice",
        "Other"
    ]
)

if job_category == "Other":
    job_keywords = st.text_input("Enter your own tech job:")
else:
    job_keywords = job_category

job_location = st.text_input("Where would you like to work?")
if st.button("Search Jobs"):
    if not job_keywords.strip() or not job_location.strip():
        st.warning("Please enter both job keywords and a location.")
    else:
        st.write("Searching for UK tech jobs...")
        try:
            jobs = search_jobs(job_keywords, job_location)

        except RequestException:
            st.error("Unable to retrieve jobs. Please check your connection.")

        except ValueError:
            st.error("Job search is unavailable. Please check your Adzuna API settings.")

        else:
            jobs = filter_senior_jobs(jobs)
            st.session_state["searched_jobs"] = jobs
            st.write(f"Found {len(jobs)} jobs.")

            if not jobs:
                st.info("No suitable entry-level jobs found. Try different keywords or another location.")


selected_job_description = ""


if "searched_jobs" in st.session_state:
    saved_jobs = st.session_state["searched_jobs"]
    st.subheader("Your Saved Job Search Results")

    for job in saved_jobs:
        st.write(job.get("title", "Unknown job"))
        st.write("Company:", job.get("company", {}).get("display_name", "Unknown"))
        st.write("Location:", job.get("location", {}).get("display_name", "Unknown"))
        st.write("Apply here:", job.get("redirect_url", "No link available"))
        st.divider()

    selected_job = st.selectbox(
        "Choose a job to analyse:",
        saved_jobs,
        format_func=lambda job: job.get("title", "Unknown job"),
        index=None,
        placeholder="Select a job"
    )

    if selected_job is not None:
        selected_job_description = selected_job.get("description", "")

        if not selected_job_description:
            st.warning("This job has no description available to analyse.")

st.subheader("Job Description Analyser")

job_description = st.text_area(
    "Paste a job description here:",
    value=selected_job_description
)

if st.button("Analyse Job"):
    if job_description.strip():
        try:
            with st.spinner("AI is analysing the job..."):
                detected_skills = analyse_job(job_description)
                st.session_state["detected_skills"] = detected_skills

        except APIConnectionError:
            st.error("Unable to connect to OpenAI. Please check your connection.")
        except AuthenticationError:
            st.error("OpenAI authentication failed. Please check your API key.")

        else:
            st.success("Job analysis complete!")
            st.write("Skills detected:", detected_skills)
            skill_weights = {
                "python": 5,
                "machine learning": 5,
                "sql": 4,
                "apis": 4,
                "git": 3,
                "docker": 2
            }

            if user_skills.strip():
                skills_to_use = user_skills.split(",")
            else:
                skills_to_use = st.session_state.get("cv_skills", [])

            current_skills = [
                skill.strip().lower()
                for skill in skills_to_use
                if skill.strip()
            ]

            matching_skills = [
                skill for skill in detected_skills
                if skill in current_skills
            ]

            missing_skills = [
                skill for skill in detected_skills
                if skill not in current_skills
            ]

            match_score = calculate_weighted_match(
                detected_skills,
                matching_skills,
                skill_weights
            )

            st.write(f"Job Match Score: {match_score:.0f}%")
            st.write("✅ Matching skills:", matching_skills)
            st.write("📚 Missing skills:", missing_skills)
            st.session_state["missing_skills"] = missing_skills
            st.session_state["job_result"] = {
                "detected_skills": detected_skills,
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "score": match_score
            }

            if len(detected_skills) == 0:
                st.warning("No technical skills detected. Unable to assess this job reliably.")
            elif len(detected_skills) == 1:
                st.warning("Limited information: only one technical skill detected.")
            elif match_score >= 80:
                st.success("Excellent match - you should consider applying!")
            elif match_score >= 60:
                st.info("Good match - definitely consider applying.")
            elif match_score >= 40:
                st.info("Possible match - work on your missing skills.")
            else:
                st.warning("Low match - build more of the required skills first.")

    else:
        st.warning("Please paste a job description first.")

if st.session_state.get("missing_skills"):
    generate_plans = st.checkbox("Generate learning plans for missing skills")

    if generate_plans:
        if st.button("Create Learning Plans"):
            for skill in st.session_state["missing_skills"]:
                try:
                    with st.spinner(f"Creating a learning plan for {skill}..."):
                        plan = generate_learning_plan(skill)
                        st.session_state.setdefault("learning_plans", {})[skill] = plan

                except APIConnectionError:
                    st.error(f"Unable to generate a learning plan for {skill}.")

    for skill, plan in st.session_state.get("learning_plans", {}).items():
        st.subheader(f"{skill.title()} Learning Plan")
        st.write(plan)


if "job_result" in st.session_state:
    saved_result = st.session_state["job_result"]
    st.subheader("Your Saved Job Analysis")
    st.write("Skills detected:", saved_result["detected_skills"])
    st.write("✅ Matching skills:", saved_result["matching_skills"])
    st.write("📚 Missing skills:", saved_result["missing_skills"])
    st.write(f"Job Match Score: {saved_result['score']:.0f}%")

