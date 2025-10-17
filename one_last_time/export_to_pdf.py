import subprocess
import sys
import os

def install_weasyprint():
    """Install weasyprint for PDF generation"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
        print("✅ WeasyPrint installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install WeasyPrint")
        return False

def convert_html_to_pdf():
    """Convert the HTML report to PDF"""
    try:
        from weasyprint import HTML
        import weasyprint
        
        html_file = 'database_report.html'
        pdf_file = 'database_report.pdf'
        
        if not os.path.exists(html_file):
            print("❌ HTML report not found. Please run generate_db_report.py first.")
            return
        
        print("🔄 Converting HTML to PDF...")
        HTML(filename=html_file).write_pdf(pdf_file)
        
        print(f"✅ PDF report generated: {pdf_file}")
        print(f"📁 Location: {os.path.abspath(pdf_file)}")
        
        # Try to open the PDF
        try:
            os.startfile(pdf_file)
            print("📄 Opening PDF in default viewer...")
        except:
            print("📄 PDF generated successfully. You can find it in the project directory.")
        
        return pdf_file
        
    except ImportError:
        print("📦 Installing WeasyPrint...")
        if install_weasyprint():
            return convert_html_to_pdf()
        else:
            print("❌ Could not install WeasyPrint. PDF conversion failed.")
            return None
    except Exception as e:
        print(f"❌ PDF conversion failed: {e}")
        return None

if __name__ == "__main__":
    convert_html_to_pdf() 