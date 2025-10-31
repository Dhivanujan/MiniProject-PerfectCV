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
