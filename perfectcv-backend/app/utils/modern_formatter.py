"""
Modern CV Presentation System
Uses Rich library for beautiful, styled text formatting
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    logger.warning("Rich library not available - install with: pip install rich")


class ModernCVFormatter:
    """
    State-of-the-art CV formatting with Rich library
    Creates beautiful, color-coded, and well-structured presentations
    """
    
    def __init__(self):
        if RICH_AVAILABLE:
            self.console = Console(record=True, width=100)
        else:
            self.console = None
    
    def format_cv_rich(self, cv_data: Dict[str, Any]) -> str:
        """
        Format CV with Rich library for beautiful terminal/HTML output
        
        Args:
            cv_data: Structured CV data
            
        Returns:
            Rich-formatted text (can be exported to HTML/ANSI/Plain)
        """
        if not RICH_AVAILABLE or not self.console:
            return self._format_cv_fallback(cv_data)
        
        self.console.clear()
        
        # Header with name
        self._add_header(cv_data)
        
        # Contact information
        self._add_contact_section(cv_data)
        
        # Professional summary
        self._add_summary_section(cv_data)
        
        # Skills
        self._add_skills_section(cv_data)
        
        # Experience
        self._add_experience_section(cv_data)
        
        # Projects
        self._add_projects_section(cv_data)
        
        # Education
        self._add_education_section(cv_data)
        
        # Certifications
        self._add_certifications_section(cv_data)
        
        # Export as text
        return self.console.export_text()
    
    def format_cv_html(self, cv_data: Dict[str, Any]) -> str:
        """
        Format CV as HTML with Rich styling
        
        Returns:
            HTML string with embedded CSS
        """
        if not RICH_AVAILABLE:
            return self._format_cv_fallback(cv_data)
        
        try:
            # Use Markdown format and convert to HTML with basic styling
            markdown_content = self.format_cv_markdown(cv_data)
            
            # Simple HTML wrapper with modern styling
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV - {cv_data.get('name', 'Resume')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8f9fa;
            color: #2d3748;
        }}
        .cv-container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #3b82f6;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 15px;
        }}
        h2 {{
            color: #3b82f6;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #3b82f6;
        }}
        h3 {{
            color: #1f2937;
            font-size: 1.2em;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .contact-info {{
            text-align: center;
            margin: 20px 0;
            font-size: 1.1em;
            color: #4a5568;
        }}
        .contact-info a {{
            color: #3b82f6;
            text-decoration: none;
            margin: 0 10px;
        }}
        .contact-info a:hover {{
            text-decoration: underline;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        li {{
            margin: 5px 0;
        }}
        strong {{
            color: #1f2937;
        }}
        em {{
            color: #6b7280;
        }}
        .section {{
            margin: 25px 0;
        }}
        code {{
            background: #eff6ff;
            padding: 2px 6px;
            border-radius: 3px;
            color: #3b82f6;
            font-size: 0.95em;
        }}
        pre {{
            background: #f7fafc;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #3b82f6;
            overflow-x: auto;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .cv-container {{
                box-shadow: none;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="cv-container">
        <h1>{cv_data.get('name', 'Your Name')}</h1>
        <div class="contact-info">
"""
            
            # Contact info
            contact = cv_data.get('contact_info', {})
            contact_parts = []
            if contact.get('email'):
                contact_parts.append(f'📧 <a href="mailto:{contact["email"]}">{contact["email"]}</a>')
            if contact.get('phone'):
                contact_parts.append(f'📱 {contact["phone"]}')
            if contact.get('linkedin'):
                url = contact['linkedin'] if contact['linkedin'].startswith('http') else f"https://{contact['linkedin']}"
                contact_parts.append(f'🔗 <a href="{url}" target="_blank">{contact["linkedin"]}</a>')
            if contact.get('github'):
                url = contact['github'] if contact['github'].startswith('http') else f"https://{contact['github']}"
                contact_parts.append(f'💻 <a href="{url}" target="_blank">{contact["github"]}</a>')
            
            html += ' • '.join(contact_parts)
            html += """
        </div>
        <div class="cv-content">
"""
            
            # Add sections
            if cv_data.get('professional_summary'):
                html += f"""
            <div class="section">
                <h2>💼 Professional Summary</h2>
                <p>{cv_data['professional_summary']}</p>
            </div>
"""
            
            # Skills
            skills = cv_data.get('skills', {})
            if skills:
                html += """
            <div class="section">
                <h2>🔧 Skills</h2>
                <ul>
"""
                for category, skill_list in skills.items():
                    if isinstance(skill_list, list):
                        skills_str = ', '.join([f'<code>{s}</code>' for s in skill_list])
                        html += f"                    <li><strong>{category}:</strong> {skills_str}</li>\n"
                html += "                </ul>\n            </div>\n"
            
            # Experience
            experience = cv_data.get('work_experience', [])
            if experience:
                html += """
            <div class="section">
                <h2>💼 Work Experience</h2>
"""
                for exp in experience:
                    title = exp.get('title', exp.get('role', 'Position'))
                    company = exp.get('company', '')
                    location = exp.get('location', '')
                    start = exp.get('start_date', '')
                    end = exp.get('end_date', '')
                    
                    html += f"                <h3>{title}</h3>\n"
                    html += f"                <p><strong>{company}</strong>"
                    if location:
                        html += f" • {location}"
                    if start or end:
                        html += f" • <em>{start} - {end}</em>"
                    html += "</p>\n"
                    
                    responsibilities = exp.get('responsibilities', [])
                    if responsibilities:
                        html += "                <ul>\n"
                        for resp in responsibilities:
                            html += f"                    <li>{resp}</li>\n"
                        html += "                </ul>\n"
                
                html += "            </div>\n"
            
            # Projects
            projects = cv_data.get('projects', [])
            if projects:
                html += """
            <div class="section">
                <h2>🚀 Projects</h2>
"""
                for proj in projects:
                    name = proj.get('name', '')
                    desc = proj.get('description', '')
                    tech = proj.get('technologies', [])
                    
                    html += f"                <h3>{name}</h3>\n"
                    if desc:
                        html += f"                <p>{desc}</p>\n"
                    if tech:
                        tech_str = ', '.join([f'<code>{t}</code>' for t in tech])
                        html += f"                <p><strong>Tech Stack:</strong> {tech_str}</p>\n"
                
                html += "            </div>\n"
            
            # Education
            education = cv_data.get('education', [])
            if education:
                html += """
            <div class="section">
                <h2>🎓 Education</h2>
"""
                for edu in education:
                    degree = edu.get('degree', '')
                    institution = edu.get('institution', '')
                    grad_date = edu.get('graduation_date', '')
                    gpa = edu.get('gpa', '')
                    
                    html += f"                <h3>{degree}</h3>\n"
                    html += f"                <p><strong>{institution}</strong>"
                    if grad_date:
                        html += f" • {grad_date}"
                    if gpa:
                        html += f" • GPA: {gpa}"
                    html += "</p>\n"
                
                html += "            </div>\n"
            
            # Certifications
            certifications = cv_data.get('certifications', [])
            if certifications:
                html += """
            <div class="section">
                <h2>📜 Certifications</h2>
                <ul>
"""
                for cert in certifications:
                    if isinstance(cert, dict):
                        name = cert.get('name', '')
                        issuer = cert.get('issuer', '')
                        date = cert.get('date', '')
                        html += f"                    <li><strong>{name}</strong>"
                        if issuer:
                            html += f" • {issuer}"
                        if date:
                            html += f" • {date}"
                        html += "</li>\n"
                    else:
                        html += f"                    <li>{cert}</li>\n"
                
                html += "                </ul>\n            </div>\n"
            
            html += """
        </div>
    </div>
</body>
</html>
"""
            
            return html
        
        except Exception as e:
            print(f"HTML export error: {e}")
            return self._format_cv_fallback(cv_data)
    
    def format_cv_markdown(self, cv_data: Dict[str, Any]) -> str:
        """
        Format CV as clean Markdown
        
        Returns:
            Markdown string
        """
        md_parts = []
        
        # Header
        name = cv_data.get('name', 'Your Name')
        md_parts.append(f"# {name}\n")
        
        # Contact
        contact = cv_data.get('contact_info', {})
        contact_parts = []
        if contact.get('email'):
            contact_parts.append(f"📧 {contact['email']}")
        if contact.get('phone'):
            contact_parts.append(f"📱 {contact['phone']}")
        if contact.get('linkedin'):
            contact_parts.append(f"[LinkedIn]({contact['linkedin']})")
        if contact.get('github'):
            contact_parts.append(f"[GitHub]({contact['github']})")
        
        if contact_parts:
            md_parts.append(" | ".join(contact_parts) + "\n")
        
        md_parts.append("---\n")
        
        # Professional Summary
        summary = cv_data.get('professional_summary', '')
        if summary:
            md_parts.append("## 💼 Professional Summary\n")
            md_parts.append(f"{summary}\n")
        
        # Skills
        skills = cv_data.get('skills', {})
        if skills:
            md_parts.append("## 🔧 Skills\n")
            
            if skills.get('technical'):
                md_parts.append("Technical Skills:\n")
                for skill in skills['technical']:
                    md_parts.append(f"- {skill}\n")
                md_parts.append("\n")
            
            if skills.get('soft'):
                md_parts.append("Soft Skills:\n")
                for skill in skills['soft']:
                    md_parts.append(f"- {skill}\n")
                md_parts.append("\n")
        
        # Experience
        experience = cv_data.get('work_experience', [])
        if experience:
            md_parts.append("## 💼 Work Experience\n")
            for exp in experience:
                role = exp.get('role', '')
                company = exp.get('company', '')
                years = exp.get('years', '')
                description = exp.get('description', '')
                
                md_parts.append(f"### {role}\n")
                md_parts.append(f"**{company}** | *{years}*\n\n")
                if description:
                    md_parts.append(f"{description}\n\n")
        
        # Projects
        projects = cv_data.get('projects', [])
        if projects:
            md_parts.append("## 🚀 Projects\n")
            for proj in projects:
                name = proj.get('name', '')
                desc = proj.get('description', '')
                tech = proj.get('technologies', [])
                
                md_parts.append(f"### {name}\n")
                if desc:
                    md_parts.append(f"{desc}\n\n")
                if tech:
                    md_parts.append(f"**Technologies:** {', '.join(tech)}\n\n")
        
        # Education
        education = cv_data.get('education', [])
        if education:
            md_parts.append("## 🎓 Education\n")
            for edu in education:
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                year = edu.get('year', '')
                
                md_parts.append(f"### {degree}\n")
                md_parts.append(f"**{institution}** | {year}\n\n")
        
        # Certifications
        certifications = cv_data.get('certifications', [])
        if certifications:
            md_parts.append("## 📜 Certifications\n")
            for cert in certifications:
                md_parts.append(f"- {cert}\n")
        
        return "".join(md_parts)
    
    def _add_header(self, cv_data: Dict[str, Any]):
        """Add styled header with name"""
        name = cv_data.get('name', 'Your Name')
        
        header = Text(name.upper(), style="bold magenta", justify="center")
        panel = Panel(
            header,
            box=box.DOUBLE,
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def _add_contact_section(self, cv_data: Dict[str, Any]):
        """Add contact information"""
        contact = cv_data.get('contact_info', {})
        if not contact:
            return
        
        contact_items = []
        if contact.get('email'):
            contact_items.append(f"📧 [cyan]{contact['email']}[/cyan]")
        if contact.get('phone'):
            contact_items.append(f"📱 [cyan]{contact['phone']}[/cyan]")
        if contact.get('linkedin'):
            contact_items.append(f"🔗 [cyan]{contact['linkedin']}[/cyan]")
        if contact.get('github'):
            contact_items.append(f"💻 [cyan]{contact['github']}[/cyan]")
        
        if contact_items:
            contact_text = "  •  ".join(contact_items)
            self.console.print(contact_text, justify="center")
            self.console.print()
    
    def _add_summary_section(self, cv_data: Dict[str, Any]):
        """Add professional summary"""
        summary = cv_data.get('professional_summary', '')
        if not summary:
            return
        
        self.console.print("[bold bright_blue]💼 PROFESSIONAL SUMMARY[/bold bright_blue]")
        self.console.print("─" * 80, style="dim")
        self.console.print()
        self.console.print(summary, style="white", justify="full")
        self.console.print()
    
    def _add_skills_section(self, cv_data: Dict[str, Any]):
        """Add skills in a table format"""
        skills = cv_data.get('skills', {})
        if not skills:
            return
        
        self.console.print("[bold bright_blue]🔧 SKILLS[/bold bright_blue]")
        self.console.print("─" * 80, style="dim")
        self.console.print()
        
        # Create skills table
        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        table.add_column("Category", style="bright_yellow", width=20)
        table.add_column("Skills", style="white")
        
        if skills.get('technical'):
            table.add_row("Technical", ", ".join(skills['technical']))
        
        if skills.get('soft'):
            table.add_row("Soft Skills", ", ".join(skills['soft']))
        
        if skills.get('languages_skills'):
            table.add_row("Programming", ", ".join(skills['languages_skills']))
        
        self.console.print(table)
        self.console.print()
    
    def _add_experience_section(self, cv_data: Dict[str, Any]):
        """Add work experience"""
        experience = cv_data.get('work_experience', [])
        if not experience:
            return
        
        self.console.print("[bold bright_blue]💼 WORK EXPERIENCE[/bold bright_blue]")
        self.console.print("─" * 80, style="dim")
        self.console.print()
        
        for exp in experience:
            role = exp.get('role', 'Position')
            company = exp.get('company', 'Company')
            years = exp.get('years', '')
            description = exp.get('description', '')
            
            self.console.print(f"[bold bright_white]{role}[/bold bright_white]")
            self.console.print(f"[italic cyan]{company}[/italic cyan]  •  [dim]{years}[/dim]")
            
            if description:
                # Split description into bullet points if not already
                if '•' in description or '▪' in description:
                    for line in description.split('\n'):
                        if line.strip():
                            self.console.print(f"  {line.strip()}", style="white")
                else:
                    self.console.print(f"  {description}", style="white")
            
            self.console.print()
    
    def _add_projects_section(self, cv_data: Dict[str, Any]):
        """Add projects"""
        projects = cv_data.get('projects', [])
        if not projects:
            return
        
        self.console.print("[bold bright_blue]🚀 PROJECTS[/bold bright_blue]")
        self.console.print("─" * 80, style="dim")
        self.console.print()
        
        for proj in projects:
            name = proj.get('name', 'Project')
            description = proj.get('description', '')
            tech = proj.get('technologies', [])
            
            self.console.print(f"[bold bright_white]{name}[/bold bright_white]")
            
            if description:
                self.console.print(f"  {description}", style="white")
            
            if tech:
                tech_str = ", ".join(tech)
                self.console.print(f"  [dim]Tech Stack:[/dim] [cyan]{tech_str}[/cyan]")
            
            self.console.print()
    
    def _add_education_section(self, cv_data: Dict[str, Any]):
        """Add education"""
        education = cv_data.get('education', [])
        if not education:
            return
        
        self.console.print("[bold bright_blue]🎓 EDUCATION[/bold bright_blue]")
        self.console.print("─" * 80, style="dim")
        self.console.print()
        
        for edu in education:
            degree = edu.get('degree', 'Degree')
            institution = edu.get('institution', 'Institution')
            year = edu.get('year', '')
            details = edu.get('details', '')
            
            self.console.print(f"[bold bright_white]{degree}[/bold bright_white]")
            self.console.print(f"[italic cyan]{institution}[/italic cyan]  •  [dim]{year}[/dim]")
            
            if details:
                self.console.print(f"  {details}", style="white")
            
            self.console.print()
    
    def _add_certifications_section(self, cv_data: Dict[str, Any]):
        """Add certifications"""
        certifications = cv_data.get('certifications', [])
        if not certifications:
            return
        
        self.console.print("[bold bright_blue]📜 CERTIFICATIONS[/bold bright_blue]")
        self.console.print("─" * 80, style="dim")
        self.console.print()
        
        for cert in certifications:
            self.console.print(f"  ✓ [bright_white]{cert}[/bright_white]")
        
        self.console.print()
    
    def _format_cv_fallback(self, cv_data: Dict[str, Any]) -> str:
        """Fallback formatting without Rich library"""
        from app.utils.cv_utils import format_extracted_text_with_sections
        
        # Use existing formatter if Rich not available
        structured = cv_data.get('structured_data', cv_data)
        result = format_extracted_text_with_sections("")
        return result.get('formatted_text', '')


# Global formatter instance
_formatter = None

def get_formatter() -> ModernCVFormatter:
    """Get singleton formatter instance"""
    global _formatter
    if _formatter is None:
        _formatter = ModernCVFormatter()
    return _formatter


def format_cv_modern(cv_data: Dict[str, Any], format_type: str = "text") -> str:
    """
    Modern CV formatting with multiple output formats
    
    Args:
        cv_data: Structured CV data
        format_type: "text", "html", or "markdown"
        
    Returns:
        Formatted CV string
    """
    formatter = get_formatter()
    
    if format_type == "html":
        return formatter.format_cv_html(cv_data)
    elif format_type == "markdown":
        return formatter.format_cv_markdown(cv_data)
    else:
        return formatter.format_cv_rich(cv_data)
