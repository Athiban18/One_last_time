from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
try:
    from sentence_transformers import SentenceTransformer, util
    st_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    st_model = None

def extract_required_skills(job_description, common_skills):
    # Simple extraction: match common skills in job description
    desc = job_description.lower()
    return [skill for skill in common_skills if skill in desc]

def skill_gap(user_skills, required_skills):
    # Return skills required by job but missing in user
    return [skill for skill in required_skills if skill not in user_skills]

def match_jobs(user_skills, jobs, common_skills=None):
    # Rank jobs by number of matching skills
    ranked = []
    for job in jobs:
        required = extract_required_skills(job.description, common_skills) if common_skills else []
        score = len(set(user_skills).intersection(set(required)))
        ranked.append((job, score))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return [job for job, score in ranked]

def rank_applicants(applicants, job, common_skills):
    # Rank applicants by skill match to job requirements
    required = extract_required_skills(job.description, common_skills)
    ranked = []
    for app in applicants:
        user_skills = app['skills']
        score = len(set(user_skills).intersection(set(required)))
        ranked.append((app, score))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

def match_jobs_advanced(resume_text, jobs):
    # Use semantic similarity if available, else fallback to cosine similarity
    results = []
    if st_model:
        resume_emb = st_model.encode(resume_text, convert_to_tensor=True)
        for job in jobs:
            job_emb = st_model.encode(job.description, convert_to_tensor=True)
            score = float(util.pytorch_cos_sim(resume_emb, job_emb).item())
            percent = int(score * 100)
            explanation = ""
            if percent > 80:
                explanation = "Excellent match: Your skills and experience closely align with the job requirements."
            elif percent > 60:
                explanation = "Good match: You meet most requirements, but could improve by adding more relevant skills or experience."
            elif percent > 40:
                explanation = "Partial match: Some important skills or experience are missing."
            else:
                explanation = "Low match: Resume and job description have little overlap. Consider tailoring your resume."
            results.append({
                'job': job,
                'score': percent,
                'explanation': explanation
            })
    else:
        texts = [resume_text] + [job.description for job in jobs]
        vectorizer = CountVectorizer().fit_transform(texts)
        vectors = vectorizer.toarray()
        resume_vec = vectors[0]
        for i, job in enumerate(jobs):
            job_vec = vectors[i+1]
            score = cosine_similarity([resume_vec], [job_vec])[0][0]
            percent = int(score * 100)
            explanation = ""
            if percent > 80:
                explanation = "Excellent match: Your skills and experience closely align with the job requirements."
            elif percent > 60:
                explanation = "Good match: You meet most requirements, but could improve by adding more relevant skills or experience."
            elif percent > 40:
                explanation = "Partial match: Some important skills or experience are missing."
            else:
                explanation = "Low match: Resume and job description have little overlap. Consider tailoring your resume."
            results.append({
                'job': job,
                'score': percent,
                'explanation': explanation
            })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
