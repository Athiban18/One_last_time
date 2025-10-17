from app import app, db
import sqlite3
from datetime import datetime

def migrate_database():
    with app.app_context():
        # Connect to the database
        conn = sqlite3.connect('instance/jobportal.db')
        cursor = conn.cursor()
        
        # Get existing columns in the job table
        cursor.execute("PRAGMA table_info(job)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Define new columns to add
        new_columns = [
            ('location', 'TEXT'),
            ('salary_min', 'INTEGER'),
            ('salary_max', 'INTEGER'),
            ('salary_currency', 'TEXT'),
            ('job_type', 'TEXT'),
            ('remote_work', 'TEXT'),
            ('experience_level', 'TEXT'),
            ('industry', 'TEXT'),
            ('company_name', 'TEXT'),
            ('posted_date', 'DATETIME'),
            ('application_deadline', 'DATETIME'),
            ('benefits', 'TEXT'),
            ('requirements', 'TEXT'),
            ('is_active', 'BOOLEAN')
        ]
        
        # Add user notification columns
        cursor.execute("PRAGMA table_info(user)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        user_new_columns = [
            ('email', 'TEXT'),
            ('email_notifications', 'BOOLEAN'),
            ('job_alert_frequency', 'TEXT'),
            ('preferred_job_types', 'TEXT'),
            ('preferred_locations', 'TEXT'),
            ('salary_range_min', 'INTEGER'),
            ('salary_range_max', 'INTEGER')
        ]
        
        for column_name, column_type in user_new_columns:
            if column_name not in user_columns:
                try:
                    cursor.execute(f"ALTER TABLE user ADD COLUMN {column_name} {column_type}")
                    print(f"Added user column: {column_name}")
                except Exception as e:
                    print(f"Error adding user column {column_name}: {e}")
        
        # Create job_alert table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_alert (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                job_id INTEGER,
                alert_type TEXT,
                sent_at DATETIME,
                is_read BOOLEAN,
                match_percentage REAL,
                match_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (job_id) REFERENCES job (id)
            )
        """)
        print("Created job_alert table")
        
        # Add missing columns
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE job ADD COLUMN {column_name} {column_type}")
                    print(f"Added column: {column_name}")
                except Exception as e:
                    print(f"Error adding column {column_name}: {e}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("Database migration completed!")

if __name__ == "__main__":
    migrate_database() 