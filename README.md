# AI Job Assistant V3

An AI-powered Python application that helps users explore UK technology jobs, analyse job descriptions, and identify skills they need to develop.

## Features

- Search UK technology jobs using the Adzuna API
- Explore software engineering, AI, cybersecurity, data, cloud and IT careers
- Upload a PDF CV and extract technical skills using OpenAI
- Analyse job descriptions using AI
- Calculate weighted job-match scores
- Identify missing technical skills
- Generate personalised learning plans
- Select a job directly from search results for analysis
- Filter out senior-level vacancies
- Interactive Streamlit web interface
- Automated tests using pytest

## Technologies

Python, Streamlit, OpenAI API, Adzuna API, pytest and Git.

## Installation

Clone the repository and open the project folder:

```bash
git clone https://github.com/deanobuckland195/AIJobAssistantV3.git
cd AIJobAssistantV3
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## API Configuration

This application uses the OpenAI API and Adzuna API.

Set these environment variables before starting the application:

- `OPENAI_API_KEY`
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`

Never commit API keys to GitHub.

## Running the Application

Start the Streamlit interface:

```bash
python -m streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Running Tests

Run the automated tests:

```bash
python -m pytest tests -q
```