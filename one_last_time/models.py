from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'student' or 'employer'
    resume = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Notification settings
    email = db.Column(db.String(120), nullable=True)
    email_notifications = db.Column(db.Boolean, default=True)
    job_alert_frequency = db.Column(db.String(20), default='daily')  # 'immediate', 'daily', 'weekly'
    preferred_job_types = db.Column(db.Text, nullable=True)  # JSON string of job types
    preferred_locations = db.Column(db.Text, nullable=True)  # JSON string of locations
    salary_range_min = db.Column(db.Integer, nullable=True)
    salary_range_max = db.Column(db.Integer, nullable=True)
    
    applications = db.relationship('Application', backref='user', lazy=True)
    login_history = db.relationship('LoginHistory', backref='user', lazy=True)
    resume_uploads = db.relationship('ResumeUpload', backref='user', lazy=True)
    jobs = db.relationship('Job', backref='employer', lazy=True)
    job_views = db.relationship('JobView', backref='viewer', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    applications = db.relationship('Application', backref='job', lazy=True)
    views = db.Column(db.Integer, default=0)
    
    # Advanced job fields
    location = db.Column(db.String(100), nullable=True)
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    salary_currency = db.Column(db.String(10), default='USD')
    job_type = db.Column(db.String(50), nullable=True)  # Full-time, Part-time, Contract, Internship
    remote_work = db.Column(db.String(20), nullable=True)  # Remote, Hybrid, On-site
    experience_level = db.Column(db.String(50), nullable=True)  # Entry, Mid, Senior, Executive
    industry = db.Column(db.String(100), nullable=True)
    company_name = db.Column(db.String(100), nullable=True)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    application_deadline = db.Column(db.DateTime, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default='applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # IPv6 compatible

class ResumeUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)  # Size in bytes
    ats_score = db.Column(db.Float)  # ATS compatibility score

class JobView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    viewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    view_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # IPv6 compatible

class EmployerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_jobs_posted = db.Column(db.Integer, default=0)
    total_applications_received = db.Column(db.Integer, default=0)
    total_job_views = db.Column(db.Integer, default=0)
    last_job_posted = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class JobAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    alert_type = db.Column(db.String(50), default='email')  # 'email', 'sms'
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    match_percentage = db.Column(db.Float, nullable=True)
    match_reason = db.Column(db.Text, nullable=True)  # Why this job matched
    
    # Relationships
    user = db.relationship('User', backref='job_alerts', lazy=True)
    job = db.relationship('Job', backref='job_alerts', lazy=True)
