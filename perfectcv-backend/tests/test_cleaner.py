from app.utils import cleaner


def test_clean_full_text_basic():
    raw = """
Jane Doe 😊\n\nExperience:\n- Built API (Jan 2020 - Feb 2022)\n\nSome weird chars and bullets ···\n"""
    cleaned = cleaner.clean_full_text(raw)
    assert '😊' not in cleaned
    assert '\x00' not in cleaned
    assert '-' in cleaned or 'Built API' in cleaned
    assert 'Jan 2020' in cleaned or '2020' in cleaned
