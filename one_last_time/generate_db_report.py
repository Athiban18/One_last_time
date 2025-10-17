import sqlite3
import os
from datetime import datetime
import webbrowser

def generate_html_report():
    """Generate a comprehensive HTML report of the database"""
    db_path = 'instance/jobportal.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    # HTML template
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Job Portal - Database Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        h3 {{
            color: #2980b9;
            margin-top: 25px;
        }}
        .info-box {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .table-section {{
            margin: 30px 0;
            border: 1px solid #bdc3c7;
            border-radius: 8px;
            overflow: hidden;
        }}
        .table-header {{
            background: #3498db;
            color: white;
            padding: 15px;
            font-weight: bold;
            font-size: 18px;
        }}
        .table-content {{
            padding: 20px;
        }}
        .column-list {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .column-item {{
            margin: 5px 0;
            padding: 5px 10px;
            background: white;
            border-left: 3px solid #3498db;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .data-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .data-table td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .relationship-diagram {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .relationship-item {{
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #e74c3c;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            margin-top: 30px;
        }}
        .export-btn {{
            background: #27ae60;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }}
        .export-btn:hover {{
            background: #229954;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Job Portal - Database Report</h1>
        
        <div class="info-box">
            <h3>📁 Database Information</h3>
            <p><strong>Location:</strong> {os.path.abspath(db_path)}</p>
            <p><strong>File Size:</strong> {os.path.getsize(db_path)} bytes</p>
            <p><strong>Last Modified:</strong> {datetime.fromtimestamp(os.path.getmtime(db_path))}</p>
        </div>
        
        <h2>📋 Database Tables</h2>
        <p>The database contains the following tables:</p>
        <ul>
"""
    
    # Add table list
    for table in tables:
        html_content += f"            <li><strong>{table[0]}</strong></li>\n"
    
    html_content += """
        </ul>
        
        <h2>📊 Detailed Table Structure</h2>
"""
    
    # Add detailed table information
    for table_name in [table[0] for table in tables]:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        html_content += f"""
        <div class="table-section">
            <div class="table-header">
                📊 Table: {table_name.upper()}
            </div>
            <div class="table-content">
                <h3>📝 Columns ({len(columns)} total)</h3>
                <div class="column-list">
"""
        
        for col in columns:
            col_id, name, data_type, not_null, default_val, pk = col
            pk_mark = " 🔑" if pk else ""
            null_mark = " NOT NULL" if not_null else ""
            default_mark = f" DEFAULT {default_val}" if default_val else ""
            html_content += f"""
                    <div class="column-item">
                        <strong>{name}</strong> ({data_type}){null_mark}{default_mark}{pk_mark}
                    </div>
"""
        
        html_content += f"""
                </div>
                
                <h3>📈 Data Statistics</h3>
                <p><strong>Total Rows:</strong> {row_count}</p>
"""
        
        # Show sample data
        if row_count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_data = cursor.fetchall()
            
            if sample_data:
                html_content += f"""
                <h3>📄 Sample Data (First {len(sample_data)} rows)</h3>
                <table class="data-table">
                    <thead>
                        <tr>
"""
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                col_info = cursor.fetchall()
                for col in col_info:
                    html_content += f"                            <th>{col[1]}</th>\n"
                
                html_content += """
                        </tr>
                    </thead>
                    <tbody>
"""
                
                for row in sample_data:
                    html_content += "                        <tr>\n"
                    for cell in row:
                        html_content += f"                            <td>{str(cell)[:50]}{'...' if len(str(cell)) > 50 else ''}</td>\n"
                    html_content += "                        </tr>\n"
                
                html_content += """
                    </tbody>
                </table>
"""
        
        html_content += """
            </div>
        </div>
"""
    
    # Add relationships
    html_content += """
        <h2>🔗 Database Relationships</h2>
        <div class="relationship-diagram">
"""
    
    relationships = [
        "user → job (employer_id)",
        "user → application (user_id)",
        "user → login_history (user_id)",
        "user → resume_upload (user_id)",
        "user → job_view (viewer_id)",
        "user → employer_stats (employer_id)",
        "job → application (job_id)",
        "job → job_view (job_id)"
    ]
    
    for rel in relationships:
        html_content += f'            <div class="relationship-item">• {rel}</div>\n'
    
    html_content += """
        </div>
        
        <h2>📈 Database Statistics</h2>
        <div class="stats-grid">
"""
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM user")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user WHERE user_type = 'student'")
    student_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user WHERE user_type = 'employer'")
    employer_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM job")
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(views) FROM job")
    total_views = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM application")
    total_applications = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM login_history")
    total_logins = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM resume_upload")
    total_resumes = cursor.fetchone()[0]
    
    stats = [
        ("👥", "Total Users", total_users),
        ("🎓", "Students", student_count),
        ("💼", "Employers", employer_count),
        ("💼", "Total Jobs", total_jobs),
        ("👀", "Job Views", total_views),
        ("📝", "Applications", total_applications),
        ("🔐", "Logins", total_logins),
        ("📄", "Resume Uploads", total_resumes)
    ]
    
    for emoji, label, value in stats:
        html_content += f"""
            <div class="stat-card">
                <div class="stat-number">{value}</div>
                <div class="stat-label">{emoji} {label}</div>
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="timestamp">
            Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="export-btn" onclick="window.print()">🖨️ Print/Save as PDF</button>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    report_file = 'database_report.html'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    conn.close()
    
    print(f"✅ Database report generated: {report_file}")
    print("🌐 Opening report in browser...")
    
    # Open in browser
    webbrowser.open(f'file://{os.path.abspath(report_file)}')
    
    return report_file

if __name__ == "__main__":
    generate_html_report() 