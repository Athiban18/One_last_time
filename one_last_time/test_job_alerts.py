#!/usr/bin/env python3
"""
Test script for job alert system
"""

from app import app, db
from models import User, Job, JobAlert
from job_alert_service import JobAlertService
import json

def test_job_alerts():
    with app.app_context():
        # Create test student
        student = User(
            username='teststudent',
            password='hashed_password',
            user_type='student',
            email='teststudent@example.com',
            email_notifications=True,
            resume='Athiban_K_Final_Resume.pdf'  # Use existing resume
        )
        db.session.add(student)
        
        # Create test employer
        employer = User(
            username='testemployer',
            password='hashed_password',
            user_type='employer'
        )
        db.session.add(employer)
        db.session.commit()
        
        # Create test job that should match the resume
        job = Job(
            title='Python Developer',
            description='We are looking for a Python developer with experience in Django, Flask, and web development. Skills required: Python, Django, Flask, SQL, HTML, CSS.',
            employer_id=employer.id,
            company_name='Test Company',
            location='Remote',
            job_type='Full-time',
            salary_min=60000,
            salary_max=80000
        )
        db.session.add(job)
        db.session.commit()
        
        print(f"✅ Created test student: {student.username}")
        print(f"✅ Created test employer: {employer.username}")
        print(f"✅ Created test job: {job.title}")
        
        # Test job alert service
        alert_service = JobAlertService()
        alerts_sent = alert_service.check_job_matches(job)
        
        print(f"📧 Job alerts sent: {alerts_sent}")
        
        # Check if alert was created
        alerts = JobAlert.query.filter_by(user_id=student.id, job_id=job.id).all()
        print(f"📋 Alerts in database: {len(alerts)}")
        
        for alert in alerts:
            print(f"   - Match: {alert.match_percentage}%")
            print(f"   - Reason: {alert.match_reason}")

if __name__ == '__main__':
    test_job_alerts() 