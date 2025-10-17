import sqlite3
import os
from datetime import datetime

def view_database_details():
    """View complete database details"""
    db_path = 'instance/jobportal.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    print("🔍 DATABASE DETAILS")
    print("=" * 50)
    print(f"📁 Database Location: {os.path.abspath(db_path)}")
    print(f"📏 File Size: {os.path.getsize(db_path)} bytes")
    print(f"🕒 Last Modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    print()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("📋 TABLES IN DATABASE")
    print("=" * 30)
    for table in tables:
        print(f"• {table[0]}")
    print()
    
    # Show detailed structure for each table
    for table_name in [table[0] for table in tables]:
        print(f"📊 TABLE: {table_name.upper()}")
        print("-" * 40)
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("📝 COLUMNS:")
        for col in columns:
            col_id, name, data_type, not_null, default_val, pk = col
            pk_mark = " 🔑" if pk else ""
            null_mark = " NOT NULL" if not_null else ""
            default_mark = f" DEFAULT {default_val}" if default_val else ""
            print(f"  • {name} ({data_type}){null_mark}{default_mark}{pk_mark}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"📊 Total Rows: {row_count}")
        
        # Show sample data (first 3 rows)
        if row_count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = cursor.fetchall()
            
            print("📄 SAMPLE DATA:")
            for i, row in enumerate(sample_data, 1):
                print(f"  Row {i}: {row}")
        
        print()
    
    # Show relationships
    print("🔗 DATABASE RELATIONSHIPS")
    print("=" * 30)
    print("• user → job (employer_id)")
    print("• user → application (user_id)")
    print("• user → login_history (user_id)")
    print("• user → resume_upload (user_id)")
    print("• user → job_view (viewer_id)")
    print("• user → employer_stats (employer_id)")
    print("• job → application (job_id)")
    print("• job → job_view (job_id)")
    print()
    
    # Show statistics
    print("📈 DATABASE STATISTICS")
    print("=" * 30)
    
    # User statistics
    cursor.execute("SELECT COUNT(*) FROM user")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM user WHERE user_type = 'student'")
    student_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM user WHERE user_type = 'employer'")
    employer_count = cursor.fetchone()[0]
    
    print(f"👥 Total Users: {total_users}")
    print(f"🎓 Students: {student_count}")
    print(f"💼 Employers: {employer_count}")
    
    # Job statistics
    cursor.execute("SELECT COUNT(*) FROM job")
    total_jobs = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(views) FROM job")
    total_views = cursor.fetchone()[0] or 0
    
    print(f"💼 Total Jobs: {total_jobs}")
    print(f"👀 Total Job Views: {total_views}")
    
    # Application statistics
    cursor.execute("SELECT COUNT(*) FROM application")
    total_applications = cursor.fetchone()[0]
    
    print(f"📝 Total Applications: {total_applications}")
    
    # Activity statistics
    cursor.execute("SELECT COUNT(*) FROM login_history")
    total_logins = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM resume_upload")
    total_resumes = cursor.fetchone()[0]
    
    print(f"🔐 Total Logins: {total_logins}")
    print(f"📄 Total Resume Uploads: {total_resumes}")
    
    conn.close()
    print()
    print("✅ Database details retrieved successfully!")

if __name__ == "__main__":
    view_database_details() 