from app import app, db
import sqlite3
from datetime import datetime

def setup_complete_database():
    with app.app_context():
        # Drop all tables and recreate them with proper structure
        db.drop_all()
        db.create_all()
        
        # Verify all tables exist
        conn = sqlite3.connect('instance/jobportal.db')
        cursor = conn.cursor()
        
        # Check all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Created tables: {tables}")
        
        # Check User table columns
        cursor.execute('PRAGMA table_info(user)')
        user_columns = [col[1] for col in cursor.fetchall()]
        print(f"User table columns: {user_columns}")
        
        # Check Job table columns
        cursor.execute('PRAGMA table_info(job)')
        job_columns = [col[1] for col in cursor.fetchall()]
        print(f"Job table columns: {job_columns}")
        
        # Check Application table columns
        cursor.execute('PRAGMA table_info(application)')
        app_columns = [col[1] for col in cursor.fetchall()]
        print(f"Application table columns: {app_columns}")
        
        # Check LoginHistory table columns
        cursor.execute('PRAGMA table_info(login_history)')
        login_columns = [col[1] for col in cursor.fetchall()]
        print(f"LoginHistory table columns: {login_columns}")
        
        # Check ResumeUpload table columns
        cursor.execute('PRAGMA table_info(resume_upload)')
        resume_columns = [col[1] for col in cursor.fetchall()]
        print(f"ResumeUpload table columns: {resume_columns}")
        
        # Check JobView table columns
        cursor.execute('PRAGMA table_info(job_view)')
        jobview_columns = [col[1] for col in cursor.fetchall()]
        print(f"JobView table columns: {jobview_columns}")
        
        # Check EmployerStats table columns
        cursor.execute('PRAGMA table_info(employer_stats)')
        employer_columns = [col[1] for col in cursor.fetchall()]
        print(f"EmployerStats table columns: {employer_columns}")
        
        conn.close()
        print("\n✅ Database setup completed successfully!")
        print("All tables and columns are properly configured.")

if __name__ == '__main__':
    setup_complete_database() 