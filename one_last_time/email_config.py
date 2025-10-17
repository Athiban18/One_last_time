"""
Email Configuration for Job Portal AI

To enable email notifications, you need to set up SMTP credentials.
Follow these steps:

1. For Gmail:
   - Go to your Google Account settings
   - Enable 2-factor authentication
   - Generate an App Password (not your regular password)
   - Use your Gmail address and the App Password

2. Set environment variables:
   - SENDER_EMAIL: your-email@gmail.com
   - SENDER_PASSWORD: your-app-password
   - SMTP_SERVER: smtp.gmail.com (default)
   - SMTP_PORT: 587 (default)

3. For other email providers:
   - SENDER_EMAIL: your-email@domain.com
   - SENDER_PASSWORD: your-password-or-app-password
   - SMTP_SERVER: smtp.your-provider.com
   - SMTP_PORT: 587 (or 465 for SSL)

Example setup:
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"

Or create a .env file:
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
"""

import os

def check_email_config():
    """Check if email configuration is properly set up"""
    email = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('SENDER_PASSWORD')
    
    if not email or email == 'your-email@gmail.com':
        print("❌ SENDER_EMAIL not configured")
        return False
    
    if not password or password == 'your-app-password':
        print("❌ SENDER_PASSWORD not configured")
        return False
    
    print("✅ Email configuration found")
    print(f"📧 Sender: {email}")
    print(f"🔐 Password: {'*' * len(password)}")
    return True

if __name__ == "__main__":
    check_email_config()



