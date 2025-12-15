"""
Text cleaning and normalization utilities.
Fixes common issues in extracted CV text.
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TextCleaner:
    """Clean and normalize extracted CV text."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Fix broken lines (words split across lines)
        text = TextCleaner._fix_broken_lines(text)
        
        # Normalize whitespace
        text = TextCleaner._normalize_whitespace(text)
        
        # Fix common OCR errors
        text = TextCleaner._fix_ocr_errors(text)
        
        # Normalize phone numbers
        text = TextCleaner._normalize_phone_numbers(text)
        
        # Fix bullet points
        text = TextCleaner._fix_bullet_points(text)
        
        # Remove duplicate lines
        text = TextCleaner._remove_duplicate_lines(text)
        
        return text.strip()
    
    @staticmethod
    def _fix_broken_lines(text: str) -> str:
        """
        Fix words that are broken across lines with hyphens.
        Example: 'manage-\nment' -> 'management'
        """
        # Fix hyphenated words across lines
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Join lines that appear to be part of the same sentence
        # (lowercase letter at line end, lowercase letter at next line start)
        lines = text.split('\n')
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if i < len(lines) - 1:
                next_line = lines[i + 1].lstrip()
                # If line doesn't end with punctuation and next line starts with lowercase
                if line and next_line and \
                   line[-1].isalnum() and not line[-1].isupper() and \
                   next_line[0].islower():
                    fixed_lines.append(line + ' ' + next_line)
                    i += 2
                    continue
            fixed_lines.append(line)
            i += 1
        
        return '\n'.join(fixed_lines)
    
    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Normalize whitespace: tabs to spaces, multiple spaces to single."""
        # Convert tabs to spaces
        text = text.replace('\t', ' ')
        
        # Multiple spaces to single space (but preserve line breaks)
        text = re.sub(r' +', ' ', text)
        
        # Remove spaces at line ends
        text = re.sub(r' +\n', '\n', text)
        
        # Remove spaces at line starts
        text = re.sub(r'\n +', '\n', text)
        
        # Limit consecutive line breaks to 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    @staticmethod
    def _fix_ocr_errors(text: str) -> str:
        """Fix common OCR recognition errors."""
        replacements = {
            r'\b0\s+': '0',  # Space after zero
            r'\bl\s+': 'I ',  # lowercase L instead of I
            r'\bO\s+': '0 ',  # O instead of zero in numbers
            r'[|]': 'I',      # Pipe instead of I
            r'~': '-',        # Tilde instead of dash
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    @staticmethod
    def _normalize_phone_numbers(text: str) -> str:
        """
        Normalize phone number formats.
        Formats like +1-234-567-8900, (234) 567-8900, etc.
        """
        # Find phone number patterns
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 (234) 567-8900
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',                    # (234) 567-8900
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',                          # 234-567-8900
        ]
        
        for pattern in phone_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                phone = match.group()
                # Extract only digits
                digits = re.sub(r'\D', '', phone)
                # Format consistently
                if len(digits) == 10:
                    formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                    text = text.replace(phone, formatted, 1)
                elif len(digits) == 11 and digits[0] == '1':
                    formatted = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
                    text = text.replace(phone, formatted, 1)
        
        return text
    
    @staticmethod
    def _fix_bullet_points(text: str) -> str:
        """Normalize bullet point characters."""
        bullet_chars = ['•', '◦', '▪', '▫', '–', '—', '*', '●', '○']
        
        for bullet in bullet_chars:
            text = text.replace(f'\n{bullet} ', '\n• ')
            text = text.replace(f'\n{bullet}', '\n• ')
        
        return text
    
    @staticmethod
    def _remove_duplicate_lines(text: str) -> str:
        """Remove consecutive duplicate lines."""
        lines = text.split('\n')
        deduplicated = []
        prev_line = None
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped != prev_line:
                deduplicated.append(line)
                prev_line = line_stripped
        
        return '\n'.join(deduplicated)
    
    @staticmethod
    def extract_sections(text: str) -> dict:
        """
        Extract major CV sections from text.
        Handles various formats including markdown headers (##), plain text headers, etc.
        
        Returns:
            Dict with section names as keys and content as values
        """
        sections = {}
        
        logger.info(f"Extracting sections from text (length: {len(text)})")
        
        # Common section headers (case-insensitive) - broader patterns
        section_patterns = {
            'summary': r'(professional\s+summary|summary|profile|objective|about\s+me|career\s+summary)',
            'experience': r'(work\s+experience|professional\s+experience|experience|employment\s+history|work\s+history)',
            'education': r'(education|academic\s+background|qualifications|academic\s+qualifications|educational\s+background)',
            'skills': r'(skills|technical\s+skills|core\s+competencies|expertise|competencies|key\s+skills)',
            'certifications': r'(certifications|certificates|licenses|professional\s+certifications)',
            'projects': r'(projects|key\s+projects|project\s+experience)',
            'awards': r'(awards|honors|honours|achievements|accomplishments)',
            'languages': r'(languages|language\s+skills)',
        }
        
        # Find section positions - handle markdown (##), plain headers, and colon-based headers
        section_positions = []
        for section_name, pattern in section_patterns.items():
            # Try markdown headers (## Header)
            for match in re.finditer(
                f'^##\\s*{pattern}\\s*$',
                text,
                flags=re.MULTILINE | re.IGNORECASE,
            ):
                section_positions.append((match.start(), section_name, match.group()))
            
            # Try single # markdown headers
            for match in re.finditer(
                f'^#\\s*{pattern}\\s*$',
                text,
                flags=re.MULTILINE | re.IGNORECASE,
            ):
                # Only add if not already found with ##
                if not any(pos[1] == section_name for pos in section_positions):
                    section_positions.append((match.start(), section_name, match.group()))
            
            # Try plain text headers (uppercase)
            for match in re.finditer(
                f'^{pattern}\\s*:?\\s*$',
                text,
                flags=re.MULTILINE | re.IGNORECASE,
            ):
                # Only add if not already found
                if not any(pos[1] == section_name and abs(pos[0] - match.start()) < 50 for pos in section_positions):
                    section_positions.append((match.start(), section_name, match.group()))
        
        # Sort by position
        section_positions.sort(key=lambda x: x[0])
        
        logger.info(f"Found {len(section_positions)} section headers: {[name for _, name, _ in section_positions]}")
        
        # Extract content between sections
        for i, (pos, name, header) in enumerate(section_positions):
            next_pos = section_positions[i + 1][0] if i + 1 < len(section_positions) else len(text)
            content = text[pos:next_pos].strip()
            # Remove the header from content
            content = content[len(header):].strip()
            
            # Clean up content - remove extra blank lines
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = content.strip()
            
            # Only add non-empty sections
            if content and len(content) > 5:
                sections[name] = content
                logger.info(f"Extracted section '{name}': {len(content)} chars")
        
        logger.info(f"Total sections extracted: {len(sections)}")
        return sections
