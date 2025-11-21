import pytest
from app.utils import cv_utils


def test_parse_experience_simple():
    txt = """
Senior Software Engineer at Acme Corp (2020-2023)
- Led development of X
- Improved performance by 30%

Software Engineer at Beta LLC (2018-2020)
- Built API
"""
    jobs = cv_utils.parse_experience_section(txt)
    assert isinstance(jobs, list)
    assert len(jobs) == 2
    assert jobs[0]['title'].lower().startswith('senior') or jobs[0]['company'].lower().startswith('acme')
    assert 'Led development' in jobs[0]['points'][0] or len(jobs[0]['points']) >= 1


def test_parse_education():
    txt = """
BSc Computer Science - Top University (2018)
MSc Data Science - Other University (2020)
"""
    ed = cv_utils.parse_education_section(txt)
    assert len(ed) == 2
    assert ed[0]['degree'].startswith('BSc')
    assert ed[0]['school'].startswith('Top University') or 'Top University' in ed[0]['school'] or ed[0]['year'] == '2018'


def test_convert_to_template_format_minimal():
    sections = {
        'about': 'Jane Doe\njane@example.com',
        'skills': 'Python, SQL',
        'experience': 'Company X\n- did stuff',
        'projects': 'Proj1\n- Built something',
        'education': 'BS CS - Uni (2017)'
    }
    tpl = cv_utils.convert_to_template_format(sections)
    assert tpl['name'] == 'Jane Doe'
    assert 'email' in tpl['contact']
    assert isinstance(tpl['skills'], list) and 'Python' in tpl['skills']
    assert isinstance(tpl['experience'], list)
    assert isinstance(tpl['projects'], list)
    assert isinstance(tpl['education'], list)


def test_build_structured_cv_payload_sections_present():
    raw_cv = """John Doe\njohn@example.com\n+1 555 555 5555\nSoftware Engineer with experience in Python.\n\nSkills\nPython, Flask\n\nWork Experience\nSoftware Engineer at Acme Corp (2020-2023)\n- Built APIs\n\nEducation\nBSc Computer Science - Tech University (2019)\n"""
    structured = cv_utils.build_standardized_sections(raw_cv)
    payload = cv_utils.build_structured_cv_payload(structured)

    required_keys = {
        "Personal Information",
        "Summary / Objective",
        "Skills",
        "Work Experience / Employment History",
        "Projects",
        "Education",
        "Certifications",
        "Achievements / Awards",
        "Languages",
        "Volunteer Experience",
        "Additional Information",
    }

    assert required_keys.issubset(payload.keys())
    # Ensure extracted contact details preserved
    assert payload["Personal Information"]["email"] == "john@example.com"
    # Missing sections should not fabricate content
    assert payload["Projects"] == []


def test_extract_sections_inline_keywords():
    text = """Summary: Passionate engineer who loves data and cloud technologies.\nSkills: Python, SQL, AWS\nWork Experience\nData Engineer at DataCorp (2022-Present)\n- Built ETL pipelines\n"""
    sections = cv_utils.extract_sections(text)
    assert "summary" in sections and "Passionate engineer" in sections["summary"]
    assert "skills" in sections and "Python" in sections["skills"]
    assert "experience" in sections and "Data Engineer" in sections["experience"]


def test_extract_contact_info_labels():
    resume_text = """Name: Jane Appleseed\nDate of Birth: 1995-05-12\nEmail: jane@example.com\nPhone: +1 555 1234 567\nAddress: 123 Mission St, San Francisco, CA\nSummary: Technical Program Manager with 10+ years of experience.\n"""
    contact = cv_utils.extract_contact_info(resume_text)
    assert contact["name"] == "Jane Appleseed"
    assert contact["email"] == "jane@example.com"
    assert "555" in contact["phone"]
    assert "San Francisco" in contact["location"]
    assert contact["date_of_birth"] == "1995-05-12"
    assert "Mission" in contact["address"]
