
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import os
import json
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from ai.resume_parser import parse_resume, COMMON_SKILLS
from ai.job_matcher import match_jobs, extract_required_skills, skill_gap, rank_applicants, match_jobs_advanced
from ai.career_counselor import get_career_advice, advanced_career_counseling
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

# Ensure instance and upload folders exist relative to the app directory
instance_dir = os.path.join(app.root_path, 'instance')
os.makedirs(instance_dir, exist_ok=True)

# Use an absolute path for the SQLite DB to avoid CWD issues
db_path = os.path.join(instance_dir, 'jobportal.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# Keep uploads inside the app directory for consistent path resolution
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

# Custom Jinja2 filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

from models import db, User, Job, Application, JobAlert
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return "Test route working!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()  # Remove whitespace
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Input validation
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('register'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('register'))
        
        # Check if username already exists (case-insensitive)
        existing_user = User.query.filter(User.username.ilike(username)).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw, user_type=user_type)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()  # Remove whitespace
        password = request.form['password']
        
        # Input validation
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('login'))
        
        # Try to find user (case-insensitive)
        user = User.query.filter(User.username.ilike(username)).first()
        
        if user and check_password_hash(user.password, password):
            # Update last login time
            user.last_login = datetime.utcnow()
            
            login_user(user)
            # Track login history
            from models import LoginHistory
            login_record = LoginHistory(
                user_id=user.id,
                ip_address=request.remote_addr
            )
            db.session.add(login_record)
            db.session.commit()
            
            flash(f'Welcome back, {user.username}!')
            
            if user.user_type == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'student':
        return redirect(url_for('student_dashboard'))
    elif current_user.user_type == 'employer':
        # Get employer statistics
        from models import EmployerStats, JobView
        
        # Get or create employer stats
        employer_stats = EmployerStats.query.filter_by(employer_id=current_user.id).first()
        if not employer_stats:
            employer_stats = EmployerStats(employer_id=current_user.id)
            db.session.add(employer_stats)
            db.session.commit()
        
        # Calculate recent statistics
        recent_job_views = len([view for view in current_user.job_views 
                               if view.view_time > datetime.utcnow() - timedelta(days=7)])
        
        # Get total applications for employer's jobs
        total_applications = sum(len(job.applications) for job in current_user.jobs)
        recent_applications = sum(len([app for app in job.applications 
                                     if app.applied_at and app.applied_at > datetime.utcnow() - timedelta(days=30)])
                                for job in current_user.jobs)
        
        # Update employer stats
        employer_stats.total_applications_received = total_applications
        employer_stats.total_job_views = sum(job.views for job in current_user.jobs)
        employer_stats.last_updated = datetime.utcnow()
        db.session.commit()
        
        return render_template('dashboard.html',
                             employer_stats=employer_stats,
                             recent_job_views=recent_job_views,
                             recent_applications=recent_applications,
                             total_applications=total_applications)
    return redirect(url_for('index'))

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.user_type != 'student':
        return redirect(url_for('dashboard'))
    
    # Get user statistics
    from models import LoginHistory, ResumeUpload
    
    # Login statistics
    total_logins = len(current_user.login_history)
    recent_logins = len([login for login in current_user.login_history 
                        if login.login_time > datetime.utcnow() - timedelta(days=7)])
    
    # Resume upload statistics
    total_resumes = len(current_user.resume_uploads)
    latest_resume = current_user.resume_uploads[-1] if current_user.resume_uploads else None
    
    # Application statistics
    total_applications = len(current_user.applications)
    recent_applications = len([app for app in current_user.applications 
                             if app.applied_at and app.applied_at > datetime.utcnow() - timedelta(days=30)])
    
    # Calculate average ATS score
    avg_ats_score = 0
    if current_user.resume_uploads:
        ats_scores = [upload.ats_score for upload in current_user.resume_uploads if upload.ats_score]
        avg_ats_score = sum(ats_scores) / len(ats_scores) if ats_scores else 0
    
    # Last activity
    last_activity = None
    if current_user.login_history:
        last_activity = max(login.login_time for login in current_user.login_history)
    
    return render_template('student_dashboard.html',
                         total_logins=total_logins,
                         recent_logins=recent_logins,
                         total_resumes=total_resumes,
                         latest_resume=latest_resume,
                         total_applications=total_applications,
                         recent_applications=recent_applications,
                         avg_ats_score=avg_ats_score,
                         last_activity=last_activity)

@app.route('/analytics_dashboard')
@login_required
def analytics_dashboard():
    if current_user.user_type != 'student':
        return redirect(url_for('dashboard'))
    
    # --- Analytics Data ---
    from collections import Counter, defaultdict
    resumes = []
    ats_scores = []
    skill_buckets = Counter()
    weekly_submissions = Counter()
    job_category_success = Counter()
    top_skills = Counter()
    high_performing = 0
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # For this demo, treat each resume upload as one resume (could be extended for multiple resumes)
    if current_user.resume:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.resume)
        feedback = parse_resume(filepath)
        # Simulate ATS score (out of 100)
        ats_score = 0
        ats_sections = feedback.get('ats', [])
        if ats_sections:
            ats_score = int(100 * sum(1 for s in ats_sections if s['present']) / len(ats_sections))
        ats_scores.append(ats_score)
        # High performing if ATS > 80
        if ats_score > 80:
            high_performing += 1
        # Skill buckets
        for skill in feedback.get('skills', []):
            if skill in ['python', 'java', 'c++', 'javascript', 'html', 'css']:
                skill_buckets['Programming'] += 1
            elif skill in ['sql', 'database', 'mongodb', 'postgresql']:
                skill_buckets['Database'] += 1
            elif skill in ['aws', 'azure', 'cloud']:
                skill_buckets['Cloud'] += 1
            elif skill in ['project management', 'leadership', 'management']:
                skill_buckets['Management'] += 1
            else:
                skill_buckets['Other'] += 1
            top_skills[skill] += 1
        # Weekly submission (simulate as today)
        weekday = datetime.now().strftime('%A')
        weekly_submissions[weekday] += 1
        # Job category success (simulate)
        job_category_success['Programming'] += ats_score > 80
        job_category_success['Database'] += ats_score > 70 and ats_score <= 80
        job_category_success['Cloud'] += ats_score > 60 and ats_score <= 70
        job_category_success['Management'] += ats_score > 50 and ats_score <= 60
        job_category_success['Other'] += ats_score <= 50
    
    # KPIs
    total_resumes = 1 if current_user.resume else 0
    avg_ats = int(sum(ats_scores)/len(ats_scores)) if ats_scores else 0
    high_performing_count = high_performing
    # Deltas (simulate)
    total_resumes_delta = '+1%' if total_resumes else '0%'
    avg_ats_delta = '+2%' if avg_ats > 80 else '-1%'
    high_perf_delta = '+3%' if high_performing_count else '0%'
    # Skill distribution for bar chart
    skill_dist = [skill_buckets.get(cat, 0) for cat in ['Other', 'Programming', 'Database', 'Cloud', 'Management']]
    # Weekly submission pattern (simulate 7 days)
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    weekly_pattern = [weekly_submissions.get(day, 0) for day in days]
    # Key Insights
    top_cat = max(job_category_success, key=job_category_success.get) if job_category_success else 'N/A'
    top_cat_score = job_category_success[top_cat] if job_category_success else 0
    top_cat_delta = '+5%' if top_cat_score else '0%'
    weekly_trend = '+4%' if avg_ats > 80 else '-2%'
    top_skills_list = top_skills.most_common(3)
    # Success rate by job category (simulate %)
    cat_success = {cat: (job_category_success[cat]*100//total_resumes if total_resumes else 0) for cat in ['Programming','Database','Cloud','Management','Other']}
    
    return render_template('analytics_dashboard.html',
        last_updated=last_updated,
        total_resumes=total_resumes,
        total_resumes_delta=total_resumes_delta,
        avg_ats=avg_ats,
        avg_ats_delta=avg_ats_delta,
        high_performing_count=high_performing_count,
        high_perf_delta=high_perf_delta,
        skill_dist=skill_dist,
        weekly_pattern=weekly_pattern,
        top_cat=top_cat,
        top_cat_score=top_cat_score,
        top_cat_delta=top_cat_delta,
        weekly_trend=weekly_trend,
        top_skills_list=top_skills_list,
        cat_success=cat_success,
        days=days
    )

@app.route('/upload_resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    feedback = None
    job_matches = []
    job_gaps = []
    resume_text = None
    ats = []
    skill_buckets = {}
    chart_data = {}
    if request.method == 'POST':
        file = request.files['resume']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            current_user.resume = filename
            
            # Track resume upload
            from models import ResumeUpload
            file_size = os.path.getsize(filepath)
            
            # Parse resume to get ATS score
            feedback = parse_resume(filepath)
            ats_score = 0
            if feedback and 'ats' in feedback:
                ats_sections = feedback['ats']
                if ats_sections:
                    ats_score = int(100 * sum(1 for s in ats_sections if s['present']) / len(ats_sections))
            
            resume_upload = ResumeUpload(
                user_id=current_user.id,
                filename=filename,
                file_size=file_size,
                ats_score=ats_score
            )
            db.session.add(resume_upload)
            db.session.commit()
            
            resume_text = open(filepath, encoding='utf-8', errors='ignore').read()
    elif current_user.resume:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], current_user.resume)
        feedback = parse_resume(filepath)
        resume_text = open(filepath, encoding='utf-8', errors='ignore').read()
    jobs = Job.query.all()
    if feedback:
        ats = feedback.get('ats', [])
        skill_buckets = feedback.get('skill_buckets', {})
        chart_data = feedback.get('chart_data', {})
        for job in jobs:
            required = extract_required_skills(job.description, COMMON_SKILLS)
            gaps = skill_gap(feedback['skills'], required)
            job_gaps.append({'job': job, 'missing': gaps, 'required': required})
        job_matches = match_jobs_advanced(resume_text, jobs) if resume_text else []
    return render_template('upload_resume.html', feedback=feedback, job_gaps=job_gaps, job_matches=job_matches, ats=ats, skill_buckets=skill_buckets, chart_data=chart_data)

@app.route('/jobs', methods=['GET'])
@login_required
def jobs():
    if current_user.user_type != 'student':
        flash('This page is only for students.')
        return redirect(url_for('dashboard'))
    
    # Get user skills from resume
    user_skills = []
    if current_user.resume:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], current_user.resume)
        feedback = parse_resume(filepath)
        user_skills = feedback['skills']
    
    # Get all jobs
    all_jobs = Job.query.all()
    
    # Filter jobs based on skill match
    matched_jobs = []
    partial_matches = []
    no_matches = []
    
    for job in all_jobs:
        required_skills = extract_required_skills(job.description, COMMON_SKILLS)
        matching_skills = [skill for skill in user_skills if skill in required_skills]
        missing_skills = [skill for skill in required_skills if skill not in user_skills]
        
        # Calculate match percentage
        match_percentage = (len(matching_skills) / len(required_skills) * 100) if required_skills else 0
        
        job_data = {
            'job': job,
            'required_skills': required_skills,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'match_percentage': match_percentage
        }
        
        # Categorize jobs based on match
        if match_percentage >= 70:  # 70% or more skills match
            matched_jobs.append(job_data)
        elif match_percentage >= 30:  # 30-69% skills match
            partial_matches.append(job_data)
        else:
            no_matches.append(job_data)
    
    # Sort by match percentage (highest first)
    matched_jobs.sort(key=lambda x: x['match_percentage'], reverse=True)
    partial_matches.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return render_template('job_list.html', 
                         matched_jobs=matched_jobs,
                         partial_matches=partial_matches,
                         no_matches=no_matches,
                         user_skills=user_skills,
                         has_resume=bool(current_user.resume))

@app.route('/advanced_search', methods=['GET'])
@login_required
def advanced_search():
    if current_user.user_type != 'student':
        flash('This page is only for students.')
        return redirect(url_for('dashboard'))
    
    # Get filter parameters
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    remote_work = request.args.get('remote_work', '')
    experience_level = request.args.get('experience_level', '')
    industry = request.args.get('industry', '')
    salary_min = request.args.get('salary_min', '')
    salary_max = request.args.get('salary_max', '')
    sort_by = request.args.get('sort_by', 'relevance')
    min_match = request.args.get('min_match', '0')
    
    # Build query
    query = Job.query.filter(Job.is_active == True)
    
    # Apply filters
    if keyword:
        query = query.filter(
            db.or_(
                Job.title.ilike(f'%{keyword}%'),
                Job.description.ilike(f'%{keyword}%'),
                Job.company_name.ilike(f'%{keyword}%'),
                Job.requirements.ilike(f'%{keyword}%')
            )
        )
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    if remote_work:
        query = query.filter(Job.remote_work == remote_work)
    
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    
    if industry:
        query = query.filter(Job.industry == industry)
    
    if salary_min:
        query = query.filter(Job.salary_max >= int(salary_min))
    
    if salary_max:
        query = query.filter(Job.salary_min <= int(salary_max))
    
    # Apply sorting
    if sort_by == 'date':
        query = query.order_by(Job.posted_date.desc())
    elif sort_by == 'salary':
        query = query.order_by(Job.salary_max.desc())
    else:  # relevance or match
        query = query.order_by(Job.posted_date.desc())
    
    # Get filtered jobs
    filtered_jobs = query.all()
    
    # Get user skills for matching
    user_skills = []
    if current_user.resume:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], current_user.resume)
        feedback = parse_resume(filepath)
        user_skills = feedback['skills']
    
    # Calculate match percentages and filter by minimum match
    jobs_with_match = []
    for job in filtered_jobs:
        required_skills = extract_required_skills(job.description, COMMON_SKILLS)
        matching_skills = [skill for skill in user_skills if skill in required_skills]
        
        # Calculate match percentage
        match_percentage = (len(matching_skills) / len(required_skills) * 100) if required_skills else 0
        
        # Filter by minimum match if specified
        if not min_match or match_percentage >= int(min_match):
            jobs_with_match.append({
                'job': job,
                'match_percentage': match_percentage,
                'matching_skills': matching_skills,
                'required_skills': required_skills
            })
    
    # Sort by match percentage if sorting by match
    if sort_by == 'match':
        jobs_with_match.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return render_template('advanced_job_search.html', 
                         jobs=[item['job'] for item in jobs_with_match],
                         user_skills=user_skills,
                         has_resume=bool(current_user.resume))

@app.route('/job/<int:job_id>')
@login_required
def job_details(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Track job view
    from models import JobView
    job_view = JobView(
        job_id=job_id,
        viewer_id=current_user.id,
        ip_address=request.remote_addr
    )
    db.session.add(job_view)
    
    # Increment the view count
    job.views = (job.views or 0) + 1
    db.session.commit()
    
    # Get user skills from resume
    user_skills = []
    if current_user.resume:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], current_user.resume)
        feedback = parse_resume(filepath)
        user_skills = feedback['skills']
    # Extract required skills from job description
    required_skills = extract_required_skills(job.description, COMMON_SKILLS)
    # Find matching and missing skills
    matching_skills = [skill for skill in user_skills if skill in required_skills]
    missing_skills = [skill for skill in required_skills if skill not in user_skills]
    return jsonify({
        'job': {
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'company_name': job.company_name,
            'location': job.location,
            'job_type': job.job_type,
            'remote_work': job.remote_work,
            'experience_level': job.experience_level,
            'industry': job.industry,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'requirements': job.requirements,
            'benefits': job.benefits,
            'views': job.views
        },
        'required_skills': required_skills,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills
    })

@app.route('/check_application/<int:job_id>')
@login_required
def check_application(job_id):
    """Check if the current user has already applied to a job"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Check if already applied
    existing_application = Application.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    
    return jsonify({
        'has_applied': existing_application is not None,
        'application_date': existing_application.applied_at.isoformat() if existing_application else None
    })

@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'})
    
    # Check if already applied
    existing_application = Application.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    if existing_application:
        return jsonify({
            'success': False, 
            'message': 'Already applied to this job',
            'has_applied': True,
            'application_date': existing_application.applied_at.isoformat()
        })
    
    # Create new application
    app_obj = Application(user_id=current_user.id, job_id=job_id)
    db.session.add(app_obj)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Application submitted successfully!',
        'has_applied': True,
        'application_date': app_obj.applied_at.isoformat()
    })

@app.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.user_type != 'employer':
        flash('Only employers can post jobs')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        description = request.form['description']
        company_name = request.form.get('company_name', '')
        location = request.form.get('location', '')
        job_type = request.form.get('job_type', '')
        remote_work = request.form.get('remote_work', '')
        experience_level = request.form.get('experience_level', '')
        industry = request.form.get('industry', '')
        requirements = request.form.get('requirements', '')
        benefits = request.form.get('benefits', '')
        
        # Handle salary fields
        salary_min = request.form.get('salary_min')
        salary_max = request.form.get('salary_max')
        if salary_min:
            salary_min = int(salary_min)
        if salary_max:
            salary_max = int(salary_max)
        
        # Handle deadline
        application_deadline = request.form.get('application_deadline')
        if application_deadline:
            application_deadline = datetime.strptime(application_deadline, '%Y-%m-%d')
        
        # Create job object
        job = Job(
            title=title,
            description=description,
            employer_id=current_user.id,
            company_name=company_name,
            location=location,
            job_type=job_type,
            remote_work=remote_work,
            experience_level=experience_level,
            industry=industry,
            salary_min=salary_min,
            salary_max=salary_max,
            requirements=requirements,
            benefits=benefits,
            application_deadline=application_deadline
        )
        db.session.add(job)
        
        # Update employer statistics
        from models import EmployerStats
        
        employer_stats = EmployerStats.query.filter_by(employer_id=current_user.id).first()
        if not employer_stats:
            employer_stats = EmployerStats(employer_id=current_user.id)
            db.session.add(employer_stats)
        
        employer_stats.total_jobs_posted += 1
        employer_stats.last_job_posted = datetime.utcnow()
        employer_stats.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        # Send job alerts to matching users
        from job_alert_service import JobAlertService
        alert_service = JobAlertService()
        alerts_sent = alert_service.check_job_matches(job)
        
        if alerts_sent > 0:
            flash(f'Job posted successfully! {alerts_sent} matching candidates notified.')
        else:
            flash('Job posted successfully!')
        
        return redirect(url_for('dashboard'))
    return render_template('post_job.html')

@app.route('/applicants')
@login_required
def applicants():
    if current_user.user_type != 'employer':
        flash('Only employers can view applicants')
        return redirect(url_for('dashboard'))
    
    jobs = Job.query.filter_by(employer_id=current_user.id).all()
    job_ids = [job.id for job in jobs]
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all()
    
    # Enhanced applicant analysis for each job
    job_applicants = {}
    for job in jobs:
        job_apps = [app for app in applications if app.job_id == job.id]
        applicants_data = []
        
        for app_obj in job_apps:
            user = User.query.get(app_obj.user_id)
            skills = []
            match_percentage = 0
            matching_skills = []
            missing_skills = []
            
            if user.resume:
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], user.resume)
                feedback = parse_resume(filepath)
                skills = feedback['skills']
                
                # Calculate skill match for this specific job
                required_skills = extract_required_skills(job.description, COMMON_SKILLS)
                matching_skills = [skill for skill in skills if skill in required_skills]
                missing_skills = [skill for skill in required_skills if skill not in skills]
                
                # Calculate match percentage
                match_percentage = (len(matching_skills) / len(required_skills) * 100) if required_skills else 0
            
            applicants_data.append({
                'user': user, 
                'skills': skills, 
                'app': app_obj,
                'match_percentage': match_percentage,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'required_skills': extract_required_skills(job.description, COMMON_SKILLS)
            })
        
        # Sort applicants by match percentage (highest first)
        applicants_data.sort(key=lambda x: x['match_percentage'], reverse=True)
        job_applicants[job.id] = applicants_data
    
    return render_template('applicants.html', 
                         jobs=jobs, 
                         job_applicants=job_applicants)

@app.route('/shortlist/<int:job_id>')
@login_required
def shortlist_applicants(job_id):
    """AI-powered resume shortlisting for a specific job"""
    if current_user.user_type != 'employer':
        flash('Only employers can access shortlisting')
        return redirect(url_for('dashboard'))
    
    job = Job.query.get(job_id)
    if not job or job.employer_id != current_user.id:
        flash('Job not found or access denied')
        return redirect(url_for('applicants'))
    
    # Get all applications for this job
    applications = Application.query.filter_by(job_id=job_id).all()
    
    # AI-powered shortlisting analysis
    shortlisted_applicants = []
    rejected_applicants = []
    
    for app_obj in applications:
        user = User.query.get(app_obj.user_id)
        
        # Initialize analysis data
        analysis = {
            'user': user,
            'application': app_obj,
            'has_resume': bool(user.resume),
            'skills': [],
            'match_percentage': 0,
            'ats_score': 0,
            'experience_level': 'Unknown',
            'shortlist_reason': '',
            'overall_score': 0
        }
        
        if user.resume:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.resume)
            feedback = parse_resume(filepath)
            
            # Extract skills and calculate match
            skills = feedback['skills']
            required_skills = extract_required_skills(job.description, COMMON_SKILLS)
            matching_skills = [skill for skill in skills if skill in required_skills]
            
            # Calculate match percentage
            match_percentage = (len(matching_skills) / len(required_skills) * 100) if required_skills else 0
            
            # Get ATS score
            ats_score = 0
            if 'ats' in feedback and feedback['ats']:
                ats_sections = feedback['ats']
                ats_score = int(100 * sum(1 for s in ats_sections if s['present']) / len(ats_sections)) if ats_sections else 0
            
            # Determine experience level based on skills and resume content
            experience_level = 'Entry Level'
            if len(skills) > 8:
                experience_level = 'Senior'
            elif len(skills) > 5:
                experience_level = 'Mid Level'
            
            # Calculate overall score (weighted combination)
            overall_score = (match_percentage * 0.6) + (ats_score * 0.3) + (len(skills) * 2)
            
            # Determine shortlist reason
            shortlist_reason = []
            if match_percentage >= 80:
                shortlist_reason.append("Excellent skill match")
            elif match_percentage >= 60:
                shortlist_reason.append("Good skill match")
            
            if ats_score >= 80:
                shortlist_reason.append("High ATS compatibility")
            elif ats_score >= 60:
                shortlist_reason.append("Good ATS compatibility")
            
            if len(skills) >= 8:
                shortlist_reason.append("Strong technical background")
            
            analysis.update({
                'skills': skills,
                'match_percentage': match_percentage,
                'ats_score': ats_score,
                'experience_level': experience_level,
                'shortlist_reason': ', '.join(shortlist_reason) if shortlist_reason else 'Manual review needed',
                'overall_score': overall_score,
                'matching_skills': matching_skills,
                'missing_skills': [skill for skill in required_skills if skill not in skills]
            })
        else:
            analysis['shortlist_reason'] = 'No resume uploaded'
            analysis['overall_score'] = 0
        
        # Categorize based on overall score
        if analysis['overall_score'] >= 70:
            shortlisted_applicants.append(analysis)
        else:
            rejected_applicants.append(analysis)
    
    # Sort shortlisted applicants by overall score (highest first)
    shortlisted_applicants.sort(key=lambda x: x['overall_score'], reverse=True)
    rejected_applicants.sort(key=lambda x: x['overall_score'], reverse=True)
    
    # Calculate statistics
    total_applicants = len(applications)
    shortlisted_count = len(shortlisted_applicants)
    rejected_count = len(rejected_applicants)
    avg_match_percentage = sum(app['match_percentage'] for app in shortlisted_applicants) / shortlisted_count if shortlisted_count > 0 else 0
    avg_ats_score = sum(app['ats_score'] for app in shortlisted_applicants) / shortlisted_count if shortlisted_count > 0 else 0
    
    return render_template('shortlist.html',
                         job=job,
                         shortlisted_applicants=shortlisted_applicants,
                         rejected_applicants=rejected_applicants,
                         total_applicants=total_applicants,
                         shortlisted_count=shortlisted_count,
                         rejected_count=rejected_count,
                         avg_match_percentage=avg_match_percentage,
                         avg_ats_score=avg_ats_score)

@app.route('/counseling')
@login_required
def counseling():
    advice = None
    missing_skills = []
    education = []
    strengths = []
    attitude = []
    career_advice = []
    resume_feedback = []
    improvements = []
    gap_analysis = None
    gap_advice = None
    career_plan = None
    
    if current_user.resume:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], current_user.resume)
        feedback = parse_resume(filepath)
        # Skill gap for all jobs
        jobs = Job.query.all()
        all_missing = set()
        for job in jobs:
            required = extract_required_skills(job.description, COMMON_SKILLS)
            gaps = skill_gap(feedback['skills'], required)
            all_missing.update(gaps)
        missing_skills = list(all_missing)
        education = feedback['education']
        
        # Get career counseling with gap analysis
        if 'career_counseling' in feedback:
            counseling_result = feedback['career_counseling']
            strengths = counseling_result['strengths']
            attitude = counseling_result['attitude']
            career_advice = counseling_result['career_advice']
            resume_feedback = counseling_result['resume_feedback']
            improvements = counseling_result['improvements']
            gap_analysis = counseling_result.get('gap_analysis')
            gap_advice = counseling_result.get('gap_advice')
        
        # Get comprehensive career plan
        if 'career_plan' in feedback:
            career_plan = feedback['career_plan']
    
    return render_template('counseling.html', 
                         advice=advice, 
                         missing_skills=missing_skills, 
                         strengths=strengths, 
                         attitude=attitude, 
                         career_advice=career_advice, 
                         resume_feedback=resume_feedback, 
                         improvements=improvements,
                         gap_analysis=gap_analysis,
                         gap_advice=gap_advice,
                         career_plan=career_plan)

@app.route('/my_applications')
@login_required
def my_applications():
    """Student route to track their application status"""
    if current_user.user_type != 'student':
        flash('This page is only for students.')
        return redirect(url_for('dashboard'))
    
    # Get all applications by the current user
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.applied_at.desc()).all()
    
    # Get job details for each application
    application_data = []
    for app in applications:
        job = Job.query.get(app.job_id)
        employer = User.query.get(job.employer_id) if job else None
        
        # Calculate days since application
        days_since_applied = (datetime.utcnow() - app.applied_at).days
        
        application_data.append({
            'application': app,
            'job': job,
            'employer': employer,
            'days_since_applied': days_since_applied
        })
    
    # Application statistics
    total_applications = len(applications)
    pending_applications = len([app for app in applications if app.status == 'applied'])
    recent_applications = len([app for app in applications if app.applied_at > datetime.utcnow() - timedelta(days=7)])
    
    return render_template('my_applications.html', 
                         applications=application_data,
                         total_applications=total_applications,
                         pending_applications=pending_applications,
                         recent_applications=recent_applications)

@app.route('/notification_settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    if current_user.user_type != 'student':
        flash('This page is only for students.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Update notification settings
        current_user.email = request.form.get('email', '')
        current_user.email_notifications = 'email_notifications' in request.form
        current_user.job_alert_frequency = request.form.get('job_alert_frequency', 'daily')
        
        # Handle preferred job types
        preferred_types = request.form.getlist('preferred_job_types')
        current_user.preferred_job_types = json.dumps(preferred_types) if preferred_types else None
        
        # Handle preferred locations
        preferred_locations = request.form.get('preferred_locations', '').strip()
        current_user.preferred_locations = preferred_locations if preferred_locations else None
        
        # Handle salary range
        salary_min = request.form.get('salary_range_min')
        salary_max = request.form.get('salary_range_max')
        current_user.salary_range_min = int(salary_min) if salary_min else None
        current_user.salary_range_max = int(salary_max) if salary_max else None
        
        db.session.commit()
        flash('Notification settings updated successfully!')
        return redirect(url_for('notification_settings'))
    
    # Get recent alerts
    from job_alert_service import JobAlertService
    alert_service = JobAlertService()
    recent_alerts = alert_service.get_user_alerts(current_user.id, 5)
    
    return render_template('notification_settings.html', recent_alerts=recent_alerts)

@app.route('/job_alerts')
@login_required
def job_alerts():
    if current_user.user_type != 'student':
        flash('This page is only for students.')
        return redirect(url_for('dashboard'))
    
    from job_alert_service import JobAlertService
    alert_service = JobAlertService()
    alerts = alert_service.get_user_alerts(current_user.id, 50)
    
    return render_template('job_alerts.html', alerts=alerts)

@app.route('/mark_alert_read/<int:alert_id>')
@login_required
def mark_alert_read(alert_id):
    from job_alert_service import JobAlertService
    alert_service = JobAlertService()
    
    if alert_service.mark_alert_read(alert_id, current_user.id):
        flash('Alert marked as read.')
    else:
        flash('Alert not found.')
    
    return redirect(request.referrer or url_for('notification_settings'))

@app.route('/delete_alert/<int:alert_id>')
@login_required
def delete_alert(alert_id):
    from job_alert_service import JobAlertService
    alert_service = JobAlertService()
    
    if alert_service.delete_alert(alert_id, current_user.id):
        flash('Alert deleted successfully.')
    else:
        flash('Alert not found.')
    
    return redirect(request.referrer or url_for('notification_settings'))

@app.route('/create_test_job')
def create_test_job():
    # Create sample jobs for demonstration
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'description': 'We are seeking a senior Python developer with experience in Django, Flask, and AWS. Must have 5+ years of experience in web development and database design.',
            'company_name': 'TechCorp Inc.',
            'location': 'San Francisco, CA',
            'job_type': 'Full-time',
            'remote_work': 'Hybrid',
            'experience_level': 'Senior',
            'industry': 'Technology',
            'salary_min': 120000,
            'salary_max': 180000,
            'requirements': 'Python, Django, Flask, AWS, PostgreSQL, 5+ years experience',
            'benefits': 'Health insurance, 401k, flexible PTO, remote work options'
        },
        {
            'title': 'Data Scientist',
            'description': 'Join our data science team to build machine learning models and analyze large datasets. Experience with Python, R, and SQL required.',
            'company_name': 'DataFlow Analytics',
            'location': 'New York, NY',
            'job_type': 'Full-time',
            'remote_work': 'Remote',
            'experience_level': 'Mid',
            'industry': 'Technology',
            'salary_min': 90000,
            'salary_max': 140000,
            'requirements': 'Python, R, SQL, Machine Learning, Statistics, 3+ years experience',
            'benefits': 'Competitive salary, health benefits, learning budget'
        },
        {
            'title': 'Frontend Developer',
            'description': 'Create beautiful and responsive user interfaces using React, JavaScript, and CSS. Experience with modern frontend frameworks required.',
            'company_name': 'WebSolutions',
            'location': 'Austin, TX',
            'job_type': 'Full-time',
            'remote_work': 'On-site',
            'experience_level': 'Entry',
            'industry': 'Technology',
            'salary_min': 60000,
            'salary_max': 85000,
            'requirements': 'React, JavaScript, HTML, CSS, 1+ years experience',
            'benefits': 'Health insurance, gym membership, team events'
        },
        {
            'title': 'Marketing Manager',
            'description': 'Lead our marketing initiatives including digital campaigns, social media, and content creation. Experience with marketing automation tools preferred.',
            'company_name': 'Growth Marketing Co.',
            'location': 'Chicago, IL',
            'job_type': 'Full-time',
            'remote_work': 'Hybrid',
            'experience_level': 'Mid',
            'industry': 'Marketing',
            'salary_min': 70000,
            'salary_max': 100000,
            'requirements': 'Marketing, Digital Campaigns, Social Media, 3+ years experience',
            'benefits': 'Health benefits, performance bonuses, professional development'
        },
        {
            'title': 'UX/UI Designer',
            'description': 'Design user-centered digital experiences using Figma, Sketch, and other design tools. Portfolio required.',
            'company_name': 'Design Studio',
            'location': 'Los Angeles, CA',
            'job_type': 'Contract',
            'remote_work': 'Remote',
            'experience_level': 'Senior',
            'industry': 'Design',
            'salary_min': 80000,
            'salary_max': 120000,
            'requirements': 'Figma, Sketch, User Research, 5+ years experience',
            'benefits': 'Flexible schedule, project-based bonuses'
        }
    ]
    
    for job_data in sample_jobs:
        job = Job(
            title=job_data['title'],
            description=job_data['description'],
            employer_id=1,  # Assuming employer with ID 1 exists
            company_name=job_data['company_name'],
            location=job_data['location'],
            job_type=job_data['job_type'],
            remote_work=job_data['remote_work'],
            experience_level=job_data['experience_level'],
            industry=job_data['industry'],
            salary_min=job_data['salary_min'],
            salary_max=job_data['salary_max'],
            requirements=job_data['requirements'],
            benefits=job_data['benefits']
        )
        db.session.add(job)
    
    db.session.commit()
    flash('Sample jobs created successfully!')
    return redirect(url_for('jobs'))

@app.route('/employer/jobs')
@login_required
def employer_jobs():
    """Get all jobs posted by the current employer"""
    if current_user.user_type != 'employer':
        return jsonify({'error': 'Access denied'}), 403
    
    jobs = Job.query.filter_by(employer_id=current_user.id).order_by(Job.posted_date.desc()).all()
    
    jobs_data = []
    for job in jobs:
        jobs_data.append({
            'id': job.id,
            'title': job.title,
            'company_name': job.company_name or 'Not specified',
            'location': job.location or 'Not specified',
            'job_type': job.job_type or 'Not specified',
            'experience_level': job.experience_level or 'Not specified',
            'salary_min': job.salary_min or 0,
            'salary_max': job.salary_max or 0,
            'views': job.views or 0,
            'applications_count': len(job.applications),
            'posted_date': job.posted_date.strftime('%B %d, %Y') if job.posted_date else 'Recently',
            'is_active': job.is_active,
            'description': job.description[:100] + '...' if len(job.description) > 100 else job.description
        })
    
    return jsonify({'jobs': jobs_data})

@app.route('/test_email')
def test_email():
    """Test email functionality"""
    from email_service import EmailService
    from email_config import check_email_config
    
    # Check if email is configured
    if not check_email_config():
        return jsonify({
            'success': False,
            'message': 'Email not configured. Set SENDER_EMAIL and SENDER_PASSWORD environment variables.'
        })
    
    # Test email service
    email_service = EmailService()
    
    # Create a test job
    from models import Job
    test_job = Job(
        title="Test Job",
        description="This is a test job to verify email functionality",
        company_name="Test Company",
        location="Test Location",
        job_type="Full-time"
    )
    
    # Try to send test email
    success = email_service.send_job_alert(
        user_email="test@example.com",
        user_name="Test User",
        job=test_job,
        match_percentage=85.5,
        match_reason="Test match reason"
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Test email sent successfully! Check your console for details.'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to send test email. Check console for errors.'
        })

@app.route('/admin/stats')
def admin_stats():
    # Comprehensive admin statistics
    from models import User, Job, Application, LoginHistory, ResumeUpload, JobView, EmployerStats
    
    # User statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(user_type='student').count()
    total_employers = User.query.filter_by(user_type='employer').count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Recent registrations (last 30 days)
    recent_users = User.query.filter(
        User.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # Job statistics
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    total_job_views = sum(job.views for job in Job.query.all())
    
    # Resume upload statistics
    total_resume_uploads = ResumeUpload.query.count()
    avg_ats_score = db.session.query(db.func.avg(ResumeUpload.ats_score)).scalar() or 0
    
    # Login statistics
    total_logins = LoginHistory.query.count()
    recent_logins = LoginHistory.query.filter(
        LoginHistory.login_time >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Top performing employers
    top_employers = db.session.query(
        User.username,
        db.func.count(Job.id).label('jobs_posted'),
        db.func.sum(Job.views).label('total_views')
    ).join(Job).filter(User.user_type == 'employer').group_by(User.id).order_by(
        db.func.sum(Job.views).desc()
    ).limit(5).all()
    
    # Most active students
    active_students = db.session.query(
        User.username,
        db.func.count(Application.id).label('applications'),
        db.func.count(ResumeUpload.id).label('resumes_uploaded')
    ).outerjoin(Application).outerjoin(ResumeUpload).filter(User.user_type == 'student').group_by(User.id).order_by(
        db.func.count(Application.id).desc()
    ).limit(5).all()
    
    # Recent activity (last 7 days)
    recent_applications = Application.query.filter(
        Application.applied_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    recent_job_views = JobView.query.filter(
        JobView.view_time >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    recent_resume_uploads = ResumeUpload.query.filter(
        ResumeUpload.upload_time >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    return render_template('admin_stats.html',
                         total_users=total_users,
                         total_students=total_students,
                         total_employers=total_employers,
                         active_users=active_users,
                         recent_users=recent_users,
                         total_jobs=total_jobs,
                         total_applications=total_applications,
                         total_job_views=total_job_views,
                         total_resume_uploads=total_resume_uploads,
                         avg_ats_score=round(avg_ats_score, 2),
                         total_logins=total_logins,
                         recent_logins=recent_logins,
                         top_employers=top_employers,
                         active_students=active_students,
                         recent_applications=recent_applications,
                         recent_job_views=recent_job_views,
                         recent_resume_uploads=recent_resume_uploads)
    """Admin route to view system statistics (no sensitive data)"""
    from models import User, LoginHistory, ResumeUpload, Job, Application
    
    # Get basic statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(user_type='student').count()
    total_employers = User.query.filter_by(user_type='employer').count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_logins = LoginHistory.query.filter(LoginHistory.login_time >= week_ago).count()
    recent_resumes = ResumeUpload.query.filter(ResumeUpload.upload_time >= week_ago).count()
    recent_applications = Application.query.filter(Application.applied_at >= week_ago).count()
    
    return jsonify({
        'total_users': total_users,
        'total_students': total_students,
        'total_employers': total_employers,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'recent_activity': {
            'logins_7_days': recent_logins,
            'resumes_7_days': recent_resumes,
            'applications_7_days': recent_applications
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
