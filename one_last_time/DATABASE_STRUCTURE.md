# Database Structure Documentation

## Overview
This document describes the complete database structure for the AI Job Portal application.

## Database Location
- **File**: `instance/jobportal.db`
- **Type**: SQLite3
- **Path**: `C:\Users\HP\Downloads\one_last_time (1)\one_last_time\instance\jobportal.db`

## Tables Structure

### 1. User Table
**Purpose**: Stores user account information
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(150) NOT NULL,
    user_type VARCHAR(20) NOT NULL,  -- 'student' or 'employer'
    resume VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT 1
);
```

### 2. Job Table
**Purpose**: Stores job postings
```sql
CREATE TABLE job (
    id INTEGER PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    employer_id INTEGER NOT NULL,
    views INTEGER DEFAULT 0,
    FOREIGN KEY (employer_id) REFERENCES user(id)
);
```

### 3. Application Table
**Purpose**: Stores job applications
```sql
CREATE TABLE application (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'applied',
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (job_id) REFERENCES job(id)
);
```

### 4. LoginHistory Table
**Purpose**: Tracks user login activity
```sql
CREATE TABLE login_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 5. ResumeUpload Table
**Purpose**: Tracks resume uploads and ATS scores
```sql
CREATE TABLE resume_upload (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    filename VARCHAR(200) NOT NULL,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    ats_score FLOAT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 6. JobView Table
**Purpose**: Tracks individual job views
```sql
CREATE TABLE job_view (
    id INTEGER PRIMARY KEY,
    job_id INTEGER NOT NULL,
    viewer_id INTEGER NOT NULL,
    view_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (job_id) REFERENCES job(id),
    FOREIGN KEY (viewer_id) REFERENCES user(id)
);
```

### 7. EmployerStats Table
**Purpose**: Tracks employer performance metrics
```sql
CREATE TABLE employer_stats (
    id INTEGER PRIMARY KEY,
    employer_id INTEGER NOT NULL,
    total_jobs_posted INTEGER DEFAULT 0,
    total_applications_received INTEGER DEFAULT 0,
    total_job_views INTEGER DEFAULT 0,
    last_job_posted DATETIME,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES user(id)
);
```

## Database Management Scripts

### 1. Complete Database Setup
```bash
python setup_complete_db.py
```
- Drops all tables and recreates them
- Ensures all columns exist
- Verifies table structure

### 2. Check Existing Users
```bash
python check_users.py
```
- Lists all users in the database
- Shows user IDs, usernames, and types

### 3. Database Migration (for existing data)
```bash
python migrate_db.py
```
- Adds missing columns to existing tables
- Preserves existing user data

## AI/ML Libraries Used

### Resume Analysis
- **spaCy**: Natural language processing for text extraction
- **pdfminer.six**: PDF text extraction
- **python-docx**: DOCX file parsing
- **NLTK**: Natural language processing

### Job Matching
- **scikit-learn**: Machine learning algorithms
- **pandas**: Data manipulation
- **numpy**: Numerical computations

### Text Processing
- **spaCy**: Named entity recognition, part-of-speech tagging
- **NLTK**: Tokenization, stemming, lemmatization

## Security Features

### Password Security
- Passwords are hashed using `werkzeug.security.generate_password_hash()`
- Uses SHA256 with salt for secure storage

### Data Protection
- User passwords are never stored in plain text
- IP addresses are logged for security monitoring
- Session management with Flask-Login

### Input Validation
- Username and password length validation
- Case-insensitive username matching
- SQL injection prevention through SQLAlchemy ORM

## Database Access

### View Database File
```bash
# Using SQLite command line
sqlite3 instance/jobportal.db

# List all tables
.tables

# View table structure
.schema user
.schema job
.schema application
```

### Backup Database
```bash
# Copy the database file
cp instance/jobportal.db backup_jobportal.db
```

### Reset Database
```bash
# Remove database file
rm instance/jobportal.db

# Run setup script
python setup_complete_db.py
```

## Common Issues and Solutions

### 1. "no such column" errors
**Solution**: Run `python setup_complete_db.py` to recreate database with proper structure

### 2. Login issues
**Solution**: Check if user exists with `python check_users.py`

### 3. Missing tables
**Solution**: Ensure all models are imported in `app.py` before running setup

### 4. Permission errors
**Solution**: Ensure write permissions to the `instance/` directory

## Performance Considerations

### Indexes
- Primary keys are automatically indexed
- Foreign keys should be indexed for better performance
- Consider adding indexes on frequently queried columns

### Data Size
- Current database is lightweight (SQLite)
- For production, consider PostgreSQL or MySQL
- Implement data archiving for old records

## Monitoring and Maintenance

### Regular Tasks
1. Monitor database size
2. Check for orphaned records
3. Backup database regularly
4. Monitor login patterns for security

### Health Checks
```bash
# Check database integrity
python -c "from app import app, db; app.app_context().push(); print('Database connection successful')"

# Count records
python -c "from app import app, db; from models import User, Job, Application; app.app_context().push(); print(f'Users: {User.query.count()}, Jobs: {Job.query.count()}, Applications: {Application.query.count()}')"
``` 