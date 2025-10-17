import json
from datetime import datetime, timedelta
from email_service import EmailService
from models import User, Job, JobAlert, db
from ai.resume_parser import parse_resume
from ai.job_matcher import extract_required_skills
import os

class JobAlertService:
    def __init__(self):
        self.email_service = EmailService()
        self.COMMON_SKILLS = [
            'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'docker', 'kubernetes',
            'machine learning', 'ai', 'data science', 'analytics', 'excel', 'powerbi', 'tableau',
            'html', 'css', 'git', 'agile', 'scrum', 'project management', 'leadership',
            'marketing', 'sales', 'customer service', 'communication', 'teamwork'
        ]
    
    def check_job_matches(self, job):
        """Check if a new job matches any users and send alerts"""
        try:
            # Get all students with email notifications enabled
            students = User.query.filter_by(
                user_type='student',
                email_notifications=True
            ).all()
            
            matches_found = 0
            
            for student in students:
                if not student.email:
                    continue
                
                # Check if student has resume
                if not student.resume:
                    continue
                
                # Calculate match percentage
                match_result = self.calculate_job_match(student, job)
                
                if match_result['match_percentage'] >= 50:  # Only alert if 50%+ match
                    # Send email alert
                    success = self.email_service.send_job_alert(
                        student.email,
                        student.username,
                        job,
                        match_result['match_percentage'],
                        match_result['match_reason']
                    )
                    
                    if success:
                        # Create job alert record
                        job_alert = JobAlert(
                            user_id=student.id,
                            job_id=job.id,
                            match_percentage=match_result['match_percentage'],
                            match_reason=match_result['match_reason']
                        )
                        db.session.add(job_alert)
                        matches_found += 1
            
            db.session.commit()
            print(f"📧 Sent {matches_found} job alerts for job: {job.title}")
            return matches_found
            
        except Exception as e:
            print(f"Error checking job matches: {e}")
            return 0
    
    def calculate_job_match(self, user, job):
        """Calculate how well a job matches a user's profile"""
        try:
            # Get user skills from resume
            filepath = os.path.join('uploads', user.resume)
            if not os.path.exists(filepath):
                return {'match_percentage': 0, 'match_reason': 'No resume uploaded'}
            
            feedback = parse_resume(filepath)
            user_skills = feedback.get('skills', [])
            
            # Extract required skills from job description
            required_skills = extract_required_skills(job.description, self.COMMON_SKILLS)
            
            if not required_skills:
                return {'match_percentage': 0, 'match_reason': 'No specific skills required'}
            
            # Calculate matching skills
            matching_skills = [skill for skill in user_skills if skill.lower() in [req.lower() for req in required_skills]]
            
            # Calculate match percentage
            match_percentage = (len(matching_skills) / len(required_skills)) * 100 if required_skills else 0
            
            # Create match reason
            if matching_skills:
                match_reason = f"Your skills match: {', '.join(matching_skills[:3])}"
                if len(matching_skills) > 3:
                    match_reason += f" and {len(matching_skills) - 3} more"
            else:
                match_reason = "Job matches your profile based on other criteria"
            
            # Apply preference filters
            match_percentage = self.apply_preference_filters(user, job, match_percentage)
            
            return {
                'match_percentage': match_percentage,
                'match_reason': match_reason,
                'matching_skills': matching_skills,
                'required_skills': required_skills
            }
            
        except Exception as e:
            print(f"Error calculating job match: {e}")
            return {'match_percentage': 0, 'match_reason': 'Error calculating match'}
    
    def apply_preference_filters(self, user, job, base_match):
        """Apply user preferences to adjust match percentage"""
        adjusted_match = base_match
        
        # Check job type preferences
        if user.preferred_job_types:
            try:
                preferred_types = json.loads(user.preferred_job_types)
                if job.job_type and job.job_type not in preferred_types:
                    adjusted_match *= 0.8  # Reduce match if job type doesn't match preference
            except:
                pass
        
        # Check location preferences
        if user.preferred_locations:
            try:
                preferred_locations = json.loads(user.preferred_locations)
                if job.location:
                    location_match = any(pref.lower() in job.location.lower() for pref in preferred_locations)
                    if not location_match:
                        adjusted_match *= 0.9  # Slight reduction for location mismatch
            except:
                pass
        
        # Check salary preferences
        if user.salary_range_min and job.salary_max:
            if job.salary_max < user.salary_range_min:
                adjusted_match *= 0.7  # Significant reduction if salary is too low
        
        if user.salary_range_max and job.salary_min:
            if job.salary_min > user.salary_range_max:
                adjusted_match *= 0.8  # Reduction if salary is too high
        
        return min(adjusted_match, 100)  # Cap at 100%
    
    def send_welcome_email(self, user):
        """Send welcome email to new users"""
        if user.email and user.email_notifications:
            return self.email_service.send_welcome_email(user.email, user.username)
        return False
    
    def get_user_alerts(self, user_id, limit=10):
        """Get recent job alerts for a user"""
        return JobAlert.query.filter_by(user_id=user_id).order_by(
            JobAlert.sent_at.desc()
        ).limit(limit).all()
    
    def mark_alert_read(self, alert_id, user_id):
        """Mark a job alert as read"""
        alert = JobAlert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            alert.is_read = True
            db.session.commit()
            return True
        return False
    
    def delete_alert(self, alert_id, user_id):
        """Delete a job alert"""
        alert = JobAlert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            db.session.delete(alert)
            db.session.commit()
            return True
        return False 