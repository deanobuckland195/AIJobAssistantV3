from pypdf import PdfReader
from ai_engine import extract_cv_skills

def read_cv(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        cv_text = ""

        for page in reader.pages:
            cv_text += page.extract_text() or ""

        return cv_text

    except Exception as error:
        raise ValueError("Unable to read this PDF. Please upload a valid, readable CV.") from error

if __name__ == "__main__":
    cv_text = read_cv("cv.pdf")
    print(cv_text)
    cv_skills = extract_cv_skills(cv_text)
    print(cv_skills)

