import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# month name mapping to short form
_MONTH_MAP = {
    'january': 'Jan', 'february': 'Feb', 'march': 'Mar', 'april': 'Apr', 'may': 'May', 'june': 'Jun',
    'july': 'Jul', 'august': 'Aug', 'september': 'Sep', 'october': 'Oct', 'november': 'Nov', 'december': 'Dec'
}


def remove_control_chars(text: str) -> str:
    # remove non-printable control chars
    return re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]', '', text)


def remove_unwanted_symbols(text: str) -> str:
    # remove emojis and many rare unicode symbols (keep basic punctuation)
    # allow letters, numbers, common punctuation, bullet chars
    text = re.sub(r'[\u2600-\u26FF\u2700-\u27BF\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF]', '', text)
    # remove sequences of weird punctuation
    text = re.sub(r'[◦•▪·▲■◆▶►]+', '-', text)
    return text


def normalize_whitespace(text: str) -> str:
    # Normalize newlines and spaces
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # collapse more than 2 newlines to two
    text = re.sub(r'\n{3,}', '\n\n', text)
    # remove trailing spaces on lines
    text = '\n'.join([ln.rstrip() for ln in text.split('\n')])
    # collapse multiple spaces
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def normalize_bullets(text: str) -> str:
    lines = []
    for raw in text.split('\n'):
        line = raw.strip()
        if not line:
            lines.append('')
            continue
        # common bullet markers
        if re.match(r'^[\-\*\u2022\u00B7\u2219\u25E6\•\·\▪\•]\s*', line):
            content = re.sub(r'^[\-\*\u2022\u00B7\u2219\u25E6\•\·\▪\•]\s*', '', line)
            lines.append(f"- {content}")
            continue
        # bullets using digits or parenthesis
        if re.match(r'^\d+[\).]\s+', line):
            content = re.sub(r'^\d+[\).]\s+', '', line)
            lines.append(f"- {content}")
            continue
        lines.append(line)
    return '\n'.join(lines)


def _shorten_month_name(m: str) -> str:
    key = m.strip().lower()
    return _MONTH_MAP.get(key, m[:3].title())


def normalize_dates(text: str) -> str:
    # Normalize common date patterns to 'Mon YYYY' and ranges to 'Mon YYYY – Present'
    # e.g., January 2020 -> Jan 2020 ; 2020-2022 -> Jan 2020 – Dec 2022 (best-effort)

    # normalize full month names
    def repl_month(match):
        mon = match.group('mon')
        year = match.group('yr')
        short = _shorten_month_name(mon)
        return f"{short} {year}"

    text = re.sub(r'(?P<mon>January|February|March|April|May|June|July|August|September|October|November|December)\s+(?P<yr>\d{4})', repl_month, text, flags=re.IGNORECASE)

    # numeric month patterns mm/yyyy or mm-yyyy -> try to convert to Mon YYYY
    def repl_num_month(match):
        m = int(match.group('m'))
        y = match.group('y')
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        mon = months[m-1] if 1 <= m <= 12 else f"M{m}"
        return f"{mon} {y}"

    text = re.sub(r'(?P<m>0?[1-9]|1[0-2])[/-](?P<y>\d{4})', repl_num_month, text)

    # ranges like "2020 - Present" or "Jan 2020 - Feb 2022"
    text = re.sub(r'\b(Present|present|current)\b', 'Present', text)
    text = re.sub(r'\s+[–—-]+\s+', ' – ', text)

    return text


def clean_full_text(text: str) -> str:
    try:
        t = text
        t = remove_control_chars(t)
        t = remove_unwanted_symbols(t)
        t = normalize_whitespace(t)
        t = normalize_bullets(t)
        t = normalize_dates(t)
        # final collapse of repeated blank lines
        t = re.sub(r'\n{3,}', '\n\n', t)
        return t.strip()
    except Exception as e:
        logger.exception("Cleaning failed: %s", e)
        return text


def split_to_paragraphs(text: str) -> List[str]:
    # Split by double-newline as paragraph boundary
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return paras
