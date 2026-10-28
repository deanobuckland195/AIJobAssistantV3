import streamlit as st
import json
from ai_engine import analyse_job, analyse_job_requirements, generate_learning_plan, extract_cv_skills
from openai import APIConnectionError, AuthenticationError
from skill_matching import calculate_weighted_match, normalise_skill
from cv_reader import read_cv
from jobs_api import search_jobs, filter_senior_jobs, filter_by_salary, filter_by_work_type, filter_by_experience
from requests.exceptions import RequestException
from job_comparison import find_best_job
from sample_jobs import SAMPLE_JOBS

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

if user_skills.strip():
    current_skills = [
        skill.strip().lower()
        for skill in user_skills.split(",")
        if skill.strip()
    ]
else:
    current_skills = st.session_state.get("cv_skills", [])

if current_skills:
    st.write("Your skills:", current_skills)

demo_mode = st.checkbox(
    "Demo Mode — Use sample jobs for testing",
    value=False
)

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

minimum_salary = st.number_input(
    "Minimum annual salary (£)",
    min_value=0,
    value=0,
    step=1000
)

maximum_salary = st.number_input(
    "Maximum annual salary (£)",
    min_value=0,
    value=0,
    step=1000
)

work_type = st.selectbox(
    "Preferred working arrangement:",
    ["Any", "Remote", "Hybrid", "On-site"]
)

experience_level = st.selectbox(
    "Preferred experience level:",
    ["Any", "Junior", "Graduate", "Apprenticeship"]
)

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

            if minimum_salary > 0 or maximum_salary > 0:
                jobs = filter_by_salary(
                    jobs,
                    minimum_salary,
                    maximum_salary
                )

            jobs = filter_by_work_type(jobs, work_type)
            jobs = filter_by_experience(jobs, experience_level)

            st.session_state["searched_jobs"] = jobs
            st.write(f"Found {len(jobs)} jobs.")

            if not jobs:
                st.info("No suitable entry-level jobs found. Try different keywords or another location.")


selected_job_description = ""


if demo_mode or "searched_jobs" in st.session_state:
    saved_jobs = st.session_state.get("searched_jobs", [])
    st.subheader("Your Saved Job Search Results")

    for job in saved_jobs:
        st.write(job.get("title", "Unknown job"))

        st.write("Company:", job.get("company", {}).get("display_name", "Unknown"))

        st.write("Location:", job.get("location", {}).get("display_name", "Unknown"))

        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")

        if salary_min is not None and salary_max is not None:
            st.write(f"Salary: £{salary_min:,.0f} - £{salary_max:,.0f}")
        elif salary_min is not None:
            st.write(f"Salary: From £{salary_min:,.0f}")
        elif salary_max is not None:
            st.write(f"Salary: Up to £{salary_max:,.0f}")
        else:
            st.write("Salary: Not advertised")

        st.write("Apply here:", job.get("redirect_url", "No link available"))

        st.divider()

    st.subheader("Compare Jobs")

    comparison_job_options = SAMPLE_JOBS if demo_mode else saved_jobs
    selected_comparison_jobs = st.multiselect(
        "Select jobs to compare:",
        comparison_job_options,
        format_func=lambda job: (
            f"{job.get('title', 'Unknown job')} - "
            f"{job.get('company', {}).get('display_name', 'Unknown')} - "
            f"£{job.get('salary_min', 0):,.0f}"
        ),
        max_selections=3
    )

    if selected_comparison_jobs:
        st.session_state["comparison_jobs"] = selected_comparison_jobs
        st.success(f"{len(selected_comparison_jobs)} job(s) selected for comparison!")

        comparison_data = []

        for job in selected_comparison_jobs:
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")

            if salary_min is not None and salary_max is not None:
                if salary_min == salary_max:
                    salary = f"£{salary_min:,.0f}"
                else:
                    salary = f"£{salary_min:,.0f} - £{salary_max:,.0f}"
            elif salary_min is not None:
                salary = f"From £{salary_min:,.0f}"
            elif salary_max is not None:
                salary = f"Up to £{salary_max:,.0f}"
            else:
                salary = "Not advertised"

            comparison_data.append({
                "Job Title": job.get("title", "Unknown job"),
                "Company": job.get("company", {}).get("display_name", "Unknown"),
                "Location": job.get("location", {}).get("display_name", "Unknown"),
                "Salary": salary
            })

        st.subheader("Job Comparison Results")
        st.dataframe(comparison_data, hide_index=True, width="stretch")

        if st.button("Analyse Selected Jobs", disabled=not selected_comparison_jobs):
            st.session_state["comparison_results"] = []

            st.session_state["comparison_inputs"] = (
                tuple(sorted(normalise_skill(skill) for skill in current_skills)),
                demo_mode,
                tuple(sorted(str(job.get("id")) for job in selected_comparison_jobs))
            )

        if not current_skills:
            st.warning("Please enter your skills or extract skills from your CV first.")
            st.stop()

        st.write("Skills being used for comparison:", current_skills)

        for job in selected_comparison_jobs:
            job_description = job.get("description", "")
            st.write("Checking job description for:", job.get("title", "Unknown job"))
            st.write("Description length:", len(job_description))

            if len(job_description) == 500:
                st.info(
                    "This job description may be shortened by Adzuna. "
                    "The AI match score will only reflect the available information."
                )

            with st.expander("View job description"):
                st.write(job_description)

            if not job_description.strip():
                st.warning(
                    f"No description available for {job.get('title', 'Unknown job')}."
                )
                continue

            try:
                with st.spinner(
                    f"Analysing {job.get('title', 'Unknown job')}..."
                ):
                    requirements = analyse_job_requirements(job_description)

                    essential_skills = {
                        normalise_skill(skill)
                        for skill in requirements["essential_skills"]
                    }

                    desirable_skills = {
                        normalise_skill(skill)
                        for skill in requirements["desirable_skills"]
                    }

                    detected_skills = sorted(essential_skills | desirable_skills)

            except (APIConnectionError, AuthenticationError, json.JSONDecodeError, ValueError):
                st.error(
                    f"Unable to analyse {job.get('title', 'Unknown job')}."
                )
                continue

            required_skills = {
                normalise_skill(skill)
                for skill in detected_skills
            }

            user_skill_set = {
                normalise_skill(skill)
                for skill in current_skills
            }

            matching_skills = sorted(required_skills & user_skill_set)

            missing_skills = sorted(required_skills - user_skill_set)

            if required_skills:
                skill_weights = {
                    skill: 3 if skill in essential_skills else 1
                    for skill in required_skills
                }

                match_score = calculate_weighted_match(
                    required_skills,
                    matching_skills,
                    skill_weights
                )
            else:
                match_score = None

            st.session_state["comparison_results"].append({
                "job": job,
                "detected_skills": detected_skills,
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "score": match_score
            })

        st.success("Job comparison analysis finished!")

    comparison_inputs = (
        tuple(sorted(normalise_skill(skill) for skill in current_skills)),
        demo_mode,
        tuple(sorted(str(job.get("id")) for job in selected_comparison_jobs))
    )

    if st.session_state.get("comparison_inputs") != comparison_inputs:
        st.session_state["comparison_results"] = []

    st.subheader("Skills Comparison Summary")

    summary_data = []

    for result in st.session_state["comparison_results"]:
        job = result["job"]
        summary_data.append({

            "Job Title": job.get("title", "Unknown job"),

            "Salary Range": (
                f"£{job['salary_min']:,.0f} - £{job['salary_max']:,.0f}"
                if job.get("salary_min") is not None
                   and job.get("salary_max") is not None
                else "Not fully advertised"
            ),

            "Match Score": (
                f"{result['score']:.0f}%"
                if result["score"] is not None
                else "N/A"
            ),
            "Missing Skills": ", ".join(result["missing_skills"]) or "None"
        })

    st.dataframe(summary_data, hide_index=True, width="stretch")

    if st.session_state.get("comparison_results"):
        st.subheader("AI Skills Detected for Each Job")

        for result in st.session_state["comparison_results"]:
            job = result["job"]
            detected_skills = result["detected_skills"]
            matching_skills = result["matching_skills"]
            missing_skills = result["missing_skills"]
            match_score = result["score"]

            st.write(
                f"**{job.get('title', 'Unknown job')} - "
                f"{job.get('company', {}).get('display_name', 'Unknown')}**"
            )

            if match_score is not None:
                st.write(f"Job Match Score: {match_score:.0f}%")
                st.write("Matching skills:", matching_skills)
                st.write("Missing skills:", missing_skills)


            if detected_skills:
                st.write("Required technical skills:", detected_skills)
            else:
                st.warning(
                    "No explicit technical skills detected. "
                    "A reliable job match score cannot be calculated."
                )

            st.divider()

        valid_results = [
            result
            for result in st.session_state["comparison_results"]
            if result["score"] is not None
        ]

        if valid_results:
            best_job = find_best_job(valid_results)

            st.subheader("Best Matching Job")

            st.success(
                f"{best_job['job'].get('title', 'Unknown job')} - "
                f"{best_job['job'].get('company', {}).get('display_name', 'Unknown')} "
                f"({best_job['score']:.0f}% match)"
            )
        else:
            st.info("No reliable job match scores are available.")

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

        except (json.JSONDecodeError, ValueError):
            st.error("The AI returned an invalid response. Please try analysing the job again.")

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

