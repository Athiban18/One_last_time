import re
from datetime import datetime, timedelta

def get_career_advice(skills, missing_skills=None, education=None):
    advice = []
    if 'machine learning' in skills:
        advice.append('You are suited for Data Scientist or ML Engineer roles.')
    if 'web development' in skills or 'html' in skills or 'css' in skills or 'javascript' in skills:
        advice.append('Consider Frontend or Backend Developer positions.')
    if missing_skills:
        advice.append(f"To improve your job prospects, consider learning: {', '.join(missing_skills)}.")
    if education:
        advice.append(f"Your education background: {', '.join(education)}.")
    if not advice:
        advice.append('Explore more projects and upskill to discover your interests and improve your profile.')
    return ' '.join(advice)

def analyze_career_gaps(text, experience_sections):
    """Analyze career gaps and provide specific advice"""
    gaps = []
    gap_advice = []
    
    # Look for date patterns and gaps
    date_patterns = [
        r'\b(19|20)\d{2}\b',  # Years
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',  # Month Year
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
        r'\b\d{4}-\d{2}-\d{2}\b'  # YYYY-MM-DD
    ]
    
    # Extract all dates from text
    all_dates = []
    for pattern in date_patterns:
        dates = re.findall(pattern, text, re.IGNORECASE)
        all_dates.extend(dates)
    
    # Look for employment gaps
    if experience_sections:
        # Simple gap detection based on experience sections
        if len(experience_sections) < 2:
            gaps.append("Limited work experience detected")
            gap_advice.append("Focus on building projects and gaining practical experience through internships or freelance work.")
    
    # Look for specific gap indicators
    gap_indicators = [
        'gap', 'break', 'sabbatical', 'unemployed', 'job search', 'career change',
        'time off', 'personal reasons', 'health', 'family', 'travel'
    ]
    
    for indicator in gap_indicators:
        if indicator.lower() in text.lower():
            gaps.append(f"Career gap mentioned: {indicator}")
            if indicator in ['health', 'family']:
                gap_advice.append("Focus on your return to work and how you've stayed current with industry trends.")
            elif indicator in ['travel', 'sabbatical']:
                gap_advice.append("Highlight the skills and experiences gained during your time away.")
            else:
                gap_advice.append("Emphasize your readiness to return to work and any upskilling you've done.")
    
    # Check for education gaps
    education_gaps = []
    if 'education' in text.lower():
        # Look for gaps between education and work
        if 'graduated' in text.lower() or 'degree' in text.lower():
            if not any(word in text.lower() for word in ['experience', 'work', 'job', 'employed']):
                education_gaps.append("Gap between education and work experience")
                gap_advice.append("Consider internships, certifications, or freelance work to bridge the gap.")
    
    return {
        'gaps': gaps + education_gaps,
        'advice': gap_advice,
        'has_gaps': len(gaps) > 0 or len(education_gaps) > 0
    }

def generate_gap_specific_advice(gap_analysis):
    """Generate specific advice for career gaps"""
    if not gap_analysis['has_gaps']:
        return {
            'message': "Great! No significant career gaps detected in your resume.",
            'suggestions': [
                "Continue building on your current experience",
                "Focus on skill development and certifications",
                "Network within your industry"
            ]
        }
    
    advice = {
        'message': "Don't worry about career gaps! Here's how to address them positively:",
        'suggestions': [
            "Be honest and positive about your gap in interviews",
            "Focus on what you learned or accomplished during the gap",
            "Show how you've stayed current with industry trends",
            "Emphasize your readiness and enthusiasm to return to work",
            "Consider temporary or contract work to rebuild experience",
            "Update your skills through online courses and certifications",
            "Network actively to find opportunities",
            "Volunteer or freelance to demonstrate current skills"
        ],
        'specific_advice': gap_analysis['advice']
    }
    
    return advice

def advanced_career_counseling(skills, soft_skills, education, experience, certifications, summary_text=None, resume_text=""):
    # 1. Analyze strengths, interests, and potential
    strengths = []
    interests = []
    if 'python' in skills or 'data analysis' in skills:
        strengths.append('Analytical thinking and technical skills')
        interests.append('Data, analytics, or technology')
    if 'machine learning' in skills:
        strengths.append('Curiosity for AI/ML and research')
        interests.append('AI, research, or innovation')
    if 'leadership' in soft_skills:
        strengths.append('Leadership and initiative')
    if 'communication' in soft_skills:
        strengths.append('Communication and teamwork')
    if certifications:
        strengths.append('Commitment to continuous learning')
    if not strengths:
        strengths.append('Eager to learn and adaptable')
    
    # 2. Infer soft skills, attitude, and work style
    attitude = []
    if 'teamwork' in soft_skills:
        attitude.append('Collaborative')
    if 'problem solving' in soft_skills:
        attitude.append('Solution-oriented')
    if 'adaptability' in soft_skills:
        attitude.append('Flexible and open to change')
    if not attitude:
        attitude.append('Motivated and diligent')
    
    # 3. Career gap analysis
    gap_analysis = analyze_career_gaps(resume_text, experience)
    gap_advice = generate_gap_specific_advice(gap_analysis)
    
    # 4. Recommend 2–3 ideal career paths
    career_paths = []
    explanations = []
    learnings = []
    industries = []
    
    if 'python' in skills and 'data analysis' in skills:
        career_paths.append('Data Analyst')
        explanations.append('Strong analytical and programming skills make you a great fit for data roles.')
        learnings.append('Deepen SQL and data visualization skills (Tableau, Power BI).')
        industries.append('Tech, finance, analytics teams in large companies.')
    
    if 'machine learning' in skills:
        career_paths.append('Machine Learning Engineer')
        explanations.append('Your ML exposure and technical foundation are ideal for ML engineering.')
        learnings.append('Build end-to-end ML projects, learn cloud deployment, contribute to open-source.')
        industries.append('AI startups, research labs, innovation teams.')
    
    if 'web development' in skills or 'javascript' in skills or 'html' in skills:
        career_paths.append('Web Developer')
        explanations.append('Your web development skills are in high demand.')
        learnings.append('Learn modern frameworks (React, Vue, Angular) and backend technologies.')
        industries.append('Tech companies, agencies, startups.')
    
    if 'project management' in skills or 'leadership' in soft_skills:
        career_paths.append('Project Manager')
        explanations.append('Leadership and organization skills suit project management roles.')
        learnings.append('Get certified (PMP/Scrum), improve stakeholder communication.')
        industries.append('Consulting, IT, enterprise project teams.')
    
    if 'cloud' in skills or 'aws' in skills or 'azure' in skills:
        career_paths.append('Cloud Engineer')
        explanations.append('Cloud skills are highly valued in today\'s market.')
        learnings.append('Get cloud certifications (AWS, Azure, GCP) and learn DevOps practices.')
        industries.append('Tech companies, consulting firms, enterprises.')
    
    if not career_paths:
        career_paths.append('Entry-level Analyst or Developer')
        explanations.append('Your profile is versatile; start in analyst or developer roles to build experience.')
        learnings.append('Focus on building a portfolio and gaining practical experience.')
        industries.append('Tech, business, or consulting firms.')
    
    # 5. For each path, explain why, what to learn, and best-fit industries
    career_advice = []
    for i, path in enumerate(career_paths):
        career_advice.append({
            'role': path,
            'why': explanations[i],
            'learn': learnings[i],
            'industry': industries[i]
        })
    
    # 6. Resume feedback with gap considerations
    feedback = []
    if not certifications:
        feedback.append('Add certifications or online courses to boost your profile.')
    if not education:
        feedback.append('Add an education section with your degrees and institutions.')
    if not experience:
        feedback.append('Add an experience section with your work or projects.')
    if len(skills) < 5:
        feedback.append('Add more technical or soft skills relevant to your field.')
    if summary_text and len(summary_text) < 30:
        feedback.append('Add a summary/objective at the top to quickly convey your career goals.')
    
    # Add gap-specific feedback
    if gap_analysis['has_gaps']:
        feedback.append('Address career gaps positively in your resume and interviews.')
        feedback.append('Show how you\'ve stayed current during any gaps.')
    
    improvements = [
        'Use more action verbs and quantify achievements (e.g., "Improved process efficiency by 20%").',
        'Add more detail about your impact and responsibilities in work experience.',
        'Format your resume for clarity and easy reading.'
    ]
    
    # Add gap-specific improvements
    if gap_analysis['has_gaps']:
        improvements.append('Include a brief, positive explanation of any career gaps.')
        improvements.append('Highlight any learning or personal development during gaps.')
    
    return {
        'strengths': strengths,
        'attitude': attitude,
        'career_advice': career_advice,
        'resume_feedback': feedback,
        'improvements': improvements,
        'gap_analysis': gap_analysis,
        'gap_advice': gap_advice
    }

def get_personalized_career_plan(skills, soft_skills, education, experience, certifications, resume_text=""):
    """Generate a comprehensive personalized career plan"""
    
    # Get advanced counseling
    counseling = advanced_career_counseling(skills, soft_skills, education, experience, certifications, None, resume_text)
    
    # Create personalized plan
    plan = {
        'current_assessment': {
            'strengths': counseling['strengths'],
            'attitude': counseling['attitude'],
            'skill_level': 'Beginner' if len(skills) < 3 else 'Intermediate' if len(skills) < 6 else 'Advanced'
        },
        'career_paths': counseling['career_advice'],
        'gap_analysis': counseling['gap_analysis'],
        'gap_advice': counseling['gap_advice'],
        'action_items': [
            'Update your resume with the suggested improvements',
            'Start working on the recommended certifications',
            'Build projects to demonstrate your skills',
            'Network actively in your target industry',
            'Practice explaining any career gaps positively'
        ],
        'timeline': {
            'immediate': ['Update resume', 'Start skill development'],
            'short_term': ['Get certifications', 'Build portfolio'],
            'long_term': ['Apply for target roles', 'Continue learning']
        }
    }
    
    return plan
