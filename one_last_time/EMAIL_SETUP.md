# Email Setup Guide for Job Portal AI

## Problem
You're not receiving email notifications when recruiters post jobs that match your resume, even though job alerts are working correctly in the UI.

## Solution
The email service needs to be configured with proper SMTP credentials. Currently, it's in development mode and only prints emails to the console.

## Setup Instructions

### Option 1: Using Gmail (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. **Set Environment Variables**:

```bash
# On Windows (Command Prompt)
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=your-16-digit-app-password

# On Windows (PowerShell)
$env:SENDER_EMAIL="your-email@gmail.com"
$env:SENDER_PASSWORD="your-16-digit-app-password"

# On Mac/Linux
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-16-digit-app-password"
```

### Option 2: Using a .env file

Create a `.env` file in your project root:

```env
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Option 3: Other Email Providers

For other providers like Outlook, Yahoo, etc.:

```env
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

## Testing Email Configuration

1. **Check configuration**:
   ```bash
   python email_config.py
   ```

2. **Test email sending**:
   - Start your Flask app
   - Visit: `http://localhost:5000/test_email`
   - Check the console for email details

3. **Test with real job posting**:
   - Post a new job as an employer
   - Check if students with matching resumes receive emails

## Troubleshooting

### Common Issues:

1. **"Authentication failed"**:
   - Make sure you're using an App Password, not your regular password
   - Ensure 2-factor authentication is enabled

2. **"Connection refused"**:
   - Check your internet connection
   - Verify SMTP server and port settings

3. **"Email not configured"**:
   - Make sure environment variables are set correctly
   - Restart your Flask application after setting variables

### Development Mode

If you don't want to set up real email credentials, the system will:
- Print email content to the console
- Still create job alerts in the database
- Show notifications in the UI

## Security Notes

- Never commit email credentials to version control
- Use environment variables or .env files (add .env to .gitignore)
- App passwords are more secure than regular passwords
- Consider using a dedicated email account for sending notifications

## Example Console Output

When emails are sent, you'll see output like:

```
============================================================
📧 JOB ALERT EMAIL TO: student@example.com
Subject: 🎯 New Job Match: Python Developer at TechCorp
Match: 85.5%
Job: Python Developer at TechCorp
============================================================
✅ Email sent successfully to student@example.com
```

This indicates that the email system is working correctly!



