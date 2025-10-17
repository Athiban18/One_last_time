import spacy
import os
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
import re
try:
    import textract
except ImportError:
    textract = None

# Load spaCy English model
nlp = spacy.load('en_core_web_sm')

# Example list of common skills (expand as needed)
COMMON_SKILLS = [
    'python', 'java', 'c++', 'machine learning', 'data analysis', 'sql', 'excel', 'communication',
    'project management', 'deep learning', 'nlp', 'cloud', 'aws', 'azure', 'javascript', 'html', 'css',
    'leadership', 'teamwork', 'problem solving', 'pandas', 'numpy', 'tensorflow', 'keras', 'pytorch'
]
SOFT_SKILLS = [
    'communication', 'leadership', 'teamwork', 'problem solving', 'adaptability', 'creativity',
    'work ethic', 'time management', 'critical thinking', 'collaboration', 'initiative', 'empathy'
]
CERT_KEYWORDS = [
    'certified', 'certification', 'certificate', 'aws certified', 'azure certified', 'google certified',
    'pmp', 'scrum', 'six sigma', 'oracle certified', 'cisco certified', 'microsoft certified', 'udemy', 'coursera', 'edx'
]
EDU_KEYWORDS = ['bachelor', 'master', 'phd', 'b.sc', 'm.sc', 'b.tech', 'm.tech', 'degree', 'university', 'college']
EXP_KEYWORDS = ['intern', 'engineer', 'developer', 'manager', 'analyst', 'consultant', 'assistant', 'lead']
PROJECT_KEYWORDS = ['project', 'developed', 'built', 'created', 'designed']
ACHIEVE_KEYWORDS = ['award', 'achievement', 'won', 'recognized', 'patent', 'published', 'honor']

ROLE_SUGGESTIONS = [
    ('data', ['python', 'data analysis', 'pandas', 'numpy', 'sql', 'machine learning']),
    ('ml', ['machine learning', 'deep learning', 'tensorflow', 'keras', 'pytorch']),
    ('web', ['javascript', 'html', 'css', 'web', 'frontend', 'backend']),
    ('cloud', ['aws', 'azure', 'cloud']),
    ('project', ['project management', 'scrum', 'leadership']),
    ('business', ['business', 'analytics', 'consultant']),
]

ATS_SECTIONS = [
    ('Contact Info', lambda text: bool(re.search(r'@|\bphone\b|\bemail\b', text.lower()))),
    ('Education', lambda text: any(k in text.lower() for k in EDU_KEYWORDS)),
    ('Certifications', lambda text: any(k in text.lower() for k in CERT_KEYWORDS)),
    ('Skills', lambda text: 'skill' in text.lower()),
    ('Projects', lambda text: 'project' in text.lower()),
    ('Achievements', lambda text: any(k in text.lower() for k in ACHIEVE_KEYWORDS)),
    ('LinkedIn', lambda text: 'linkedin.com' in text.lower()),
]


# Helper to extract text from file

def extract_text(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.pdf':
        return extract_pdf_text(file_path)
    elif file_ext in ['.docx', '.doc']:
        doc = Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])
    elif file_ext == '.txt':
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif textract:
        try:
            return textract.process(file_path).decode('utf-8')
        except Exception:
            return ''
    else:
        return ''

def extract_certifications(text):
    certs = []
    for line in text.splitlines():
        for cert in CERT_KEYWORDS:
            if cert in line.lower() and line not in certs:
                certs.append(line.strip())
    return certs

def extract_soft_skills(text):
    found = set()
    for skill in SOFT_SKILLS:
        if skill in text.lower():
            found.add(skill)
    return list(found)

def extract_projects(text):
    projects = []
    for line in text.splitlines():
        if any(k in line.lower() for k in PROJECT_KEYWORDS):
            projects.append(line.strip())
    return projects

def extract_achievements(text):
    achievements = []
    for line in text.splitlines():
        if any(k in line.lower() for k in ACHIEVE_KEYWORDS):
            achievements.append(line.strip())
    return achievements

def extract_linkedin(text):
    match = re.search(r'(https?://[\w\.]*linkedin\.com[\w\-/\?=&#%]*)', text)
    return match.group(1) if match else None

def ats_checklist(text):
    checklist = []
    for section, check in ATS_SECTIONS:
        present = check(text)
        checklist.append({'section': section, 'present': present})
    return checklist

def infer_personality_and_domain(text, skills, experience, education):
    # Infer personality traits from soft skills and summary/objective
    personality = []
    if 'leadership' in skills or 'lead' in text:
        personality.append('Leadership')
    if 'teamwork' in skills or 'team' in text:
        personality.append('Team Player')
    if 'problem solving' in skills or 'problem' in text:
        personality.append('Problem Solver')
    if 'communication' in skills or 'communicat' in text:
        personality.append('Good Communicator')
    if not personality:
        personality.append('Analytical')
    # Infer domain strengths
    domain = []
    for label, keywords in ROLE_SUGGESTIONS:
        if any(k in skills for k in keywords):
            domain.append(label)
    # Infer ideal roles
    ideal_roles = []
    if 'data' in domain:
        ideal_roles.append('Data Analyst')
    if 'ml' in domain:
        ideal_roles.append('ML Engineer')
    if 'web' in domain:
        ideal_roles.append('Web Developer')
    if 'cloud' in domain:
        ideal_roles.append('Cloud Engineer')
    if 'project' in domain:
        ideal_roles.append('Project Manager')
    if 'business' in domain:
        ideal_roles.append('Business Analyst')
    if not ideal_roles:
        ideal_roles.append('Generalist/Entry-level roles')
    return personality, domain, ideal_roles

def parse_resume(file_path):
    text = extract_text(file_path)
    doc = nlp(text.lower())
    # Extract skills
    skills = set()
    for token in doc:
        if token.text in COMMON_SKILLS:
            skills.add(token.text)
    # Extract education
    education = [sent.text for sent in doc.sents if any(k in sent.text for k in EDU_KEYWORDS)]
    # Extract experience
    experience = [sent.text for sent in doc.sents if any(k in sent.text for k in EXP_KEYWORDS)]
    # Extract certifications
    certifications = extract_certifications(text)
    # Extract soft skills
    soft_skills = extract_soft_skills(text)
    # Extract projects
    projects = extract_projects(text)
    # Extract achievements
    achievements = extract_achievements(text)
    # Extract LinkedIn
    linkedin = extract_linkedin(text)
    # ATS checklist
    ats = ats_checklist(text)
    # Skill buckets
    have_skills = list(skills)
    gap_skills = [skill for skill in COMMON_SKILLS if skill not in skills]
    suggested_learning = gap_skills[:5]
    # Chart data
    chart_data = {
        'have': len(have_skills),
        'gap': len(gap_skills),
        'suggested': len(suggested_learning)
    }
    # --- AI Feedback Section ---
    feedback = {}
    # Summary
    feedback['summary'] = f"You have strengths in {', '.join(have_skills[:3])}."
    # Strengths
    strengths = []
    if len(skills) > 0:
        strengths.append(f"Good technical skills: {', '.join(skills)}")
    if len(soft_skills) > 0:
        strengths.append(f"Soft skills: {', '.join(soft_skills)}")
    if len(education) > 0:
        strengths.append("Education section found")
    if len(experience) > 0:
        strengths.append("Experience section found")
    if len(certifications) > 0:
        strengths.append(f"Certifications: {', '.join(certifications)}")
    if len(projects) > 0:
        strengths.append(f"Projects: {', '.join(projects[:2])}")
    if len(achievements) > 0:
        strengths.append(f"Achievements: {', '.join(achievements[:2])}")
    feedback['strengths'] = strengths
    # Skill Gaps (compared to common skills)
    feedback['missing_skills'] = gap_skills[:5]
    # Suggestions
    suggestions = []
    if len(skills) < 5:
        suggestions.append("Add more technical or soft skills relevant to your field.")
    if len(education) == 0:
        suggestions.append("Add an education section with your degrees and institutions.")
    if len(experience) == 0:
        suggestions.append("Add an experience section with your work or projects.")
    if len(certifications) == 0:
        suggestions.append("Add certifications or online courses to boost your profile.")
    if len(projects) == 0:
        suggestions.append("Add a Projects section with 2–3 key projects.")
    if len(achievements) == 0:
        suggestions.append("Add an Achievements section and quantify your impact.")
    if not linkedin:
        suggestions.append("Add your LinkedIn profile link.")
    if len(text) < 500:
        suggestions.append("Resume is too short. Add more details about your skills, education, and experience.")
    if not any('@' in line for line in text.splitlines()):
        suggestions.append("Add your email/contact information.")
    feedback['suggestions'] = suggestions
    # Formatting feedback
    formatting = []
    if len(text.splitlines()) > 50:
        formatting.append("Consider shortening your resume to 1-2 pages.")
    if not any(word in text.lower() for word in ['summary', 'objective']):
        formatting.append("Add a summary/objective section at the top.")
    feedback['formatting'] = formatting
    # Career suggestions with gap analysis
    from .career_counselor import advanced_career_counseling, get_personalized_career_plan
    
    # Get personalized career counseling with gap analysis
    career_counseling = advanced_career_counseling(
        skills=list(skills),
        soft_skills=soft_skills,
        education=education,
        experience=experience,
        certifications=certifications,
        resume_text=text
    )
    
    # Get comprehensive career plan
    career_plan = get_personalized_career_plan(
        skills=list(skills),
        soft_skills=soft_skills,
        education=education,
        experience=experience,
        certifications=certifications,
        resume_text=text
    )
    
    feedback['career_suggestions'] = career_counseling
    feedback['career_plan'] = career_plan
    
    return {
        'skills': list(skills),
        'soft_skills': soft_skills,
        'education': education,
        'experience': experience,
        'certifications': certifications,
        'projects': projects,
        'achievements': achievements,
        'linkedin': linkedin,
        'ats': ats,
        'skill_buckets': {
            'have': have_skills,
            'gap': gap_skills,
            'suggested': suggested_learning
        },
        'chart_data': chart_data,
        'feedback': feedback,
        'career_counseling': career_counseling,
        'career_plan': career_plan
    }
