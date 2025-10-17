import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import os

class EmailService:
    def __init__(self):
        # Email configuration - you can set these as environment variables
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.sender_email = os.environ.get('SENDER_EMAIL', 'your-email@gmail.com')
        self.sender_password = os.environ.get('SENDER_PASSWORD', 'your-app-password')
        
        # Check if we have valid email credentials
        self.email_enabled = (
            self.sender_email != 'your-email@gmail.com' and 
            self.sender_password != 'your-app-password'
        )
        
        if not self.email_enabled:
            print("⚠️  Email service not configured. Set SENDER_EMAIL and SENDER_PASSWORD environment variables.")
            print("📧 Emails will be printed to console only.")
        
    def send_job_alert(self, user_email, user_name, job, match_percentage, match_reason):
        """Send job alert email to user"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = user_email
            msg['Subject'] = f"🎯 New Job Match: {job.title} at {job.company_name or 'Company'}"
            
            # Create HTML body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                        <h1 style="margin: 0; font-size: 24px;">🎯 New Job Match!</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">We found a perfect job for you!</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h2 style="color: #2c3e50; margin-top: 0;">{job.title}</h2>
                        <p style="color: #7f8c8d; margin: 5px 0;"><strong>Company:</strong> {job.company_name or 'Not specified'}</p>
                        <p style="color: #7f8c8d; margin: 5px 0;"><strong>Location:</strong> {job.location or 'Not specified'}</p>
                        <p style="color: #7f8c8d; margin: 5px 0;"><strong>Type:</strong> {job.job_type or 'Not specified'}</p>
                        <p style="color: #7f8c8d; margin: 5px 0;"><strong>Experience:</strong> {job.experience_level or 'Not specified'}</p>
                        
                        {f'<p style="color: #7f8c8d; margin: 5px 0;"><strong>Salary:</strong> ${job.salary_min:,} - ${job.salary_max:,}</p>' if job.salary_min and job.salary_max else ''}
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #27ae60; margin-top: 0;">🎯 Match Details</h3>
                        <p style="margin: 5px 0;"><strong>Match Percentage:</strong> {match_percentage:.1f}%</p>
                        <p style="margin: 5px 0;"><strong>Why it matches:</strong> {match_reason}</p>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #856404; margin-top: 0;">📝 Job Description</h3>
                        <p style="margin: 0;">{job.description[:200]}{'...' if len(job.description) > 200 else ''}</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://127.0.0.1:5000/job/{job.id}" 
                           style="background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            👀 View Job Details
                        </a>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; font-size: 14px; color: #6c757d;">
                        <p style="margin: 0;"><strong>💡 Tip:</strong> Apply quickly! Jobs with high match percentages often get many applications.</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #6c757d; font-size: 12px;">
                        <p>This email was sent by Job Portal AI</p>
                        <p>To manage your job alerts, visit your dashboard</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Print email for development
            print(f"\n{'='*60}")
            print(f"📧 JOB ALERT EMAIL TO: {user_email}")
            print(f"Subject: {msg['Subject']}")
            print(f"Match: {match_percentage:.1f}%")
            print(f"Job: {job.title} at {job.company_name}")
            print(f"{'='*60}\n")
            
            # Send email if configured
            if self.email_enabled:
                try:
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    text = msg.as_string()
                    server.sendmail(self.sender_email, user_email, text)
                    server.quit()
                    print(f"✅ Email sent successfully to {user_email}")
                    return True
                except Exception as e:
                    print(f"❌ Failed to send email to {user_email}: {e}")
                    return False
            else:
                print(f"📧 [DEV MODE] Email would be sent to: {user_email}")
                return True  # Return True in dev mode so alerts are still created
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_welcome_email(self, user_email, user_name):
        """Send welcome email to new users"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = user_email
            msg['Subject'] = "🎉 Welcome to Job Portal AI!"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                        <h1 style="margin: 0; font-size: 24px;">🎉 Welcome to Job Portal AI!</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Your AI-powered job search journey begins now!</p>
                    </div>
                    
                    <div style="padding: 20px;">
                        <h2 style="color: #2c3e50;">Hi {user_name}!</h2>
                        <p>Welcome to Job Portal AI! We're excited to help you find your perfect job using advanced AI technology.</p>
                        
                        <h3 style="color: #2c3e50;">🚀 What you can do:</h3>
                        <ul>
                            <li>📄 Upload your resume for AI analysis</li>
                            <li>🎯 Get personalized job recommendations</li>
                            <li>📧 Receive job alerts via email</li>
                            <li>📊 Track your application analytics</li>
                            <li>💬 Get career guidance and advice</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://127.0.0.1:5000/upload_resume" 
                               style="background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                                📄 Upload Your Resume
                            </a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            print(f"\n{'='*60}")
            print(f"📧 WELCOME EMAIL TO: {user_email}")
            print(f"Subject: {msg['Subject']}")
            print(f"{'='*60}\n")
            
            # Send email if configured
            if self.email_enabled:
                try:
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    text = msg.as_string()
                    server.sendmail(self.sender_email, user_email, text)
                    server.quit()
                    print(f"✅ Welcome email sent successfully to {user_email}")
                    return True
                except Exception as e:
                    print(f"❌ Failed to send welcome email to {user_email}: {e}")
                    return False
            else:
                print(f"📧 [DEV MODE] Welcome email would be sent to: {user_email}")
                return True  # Return True in dev mode
            
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            return False 