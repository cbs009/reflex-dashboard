
import os
from fpdf import FPDF
import datetime

# --- Configuration ---
PROJECT_ROOT = "/Users/chandrabhushansingh/AI/reflex_dashboard"
ARTIFACTS_DIR = "/Users/chandrabhushansingh/.gemini/antigravity/brain/c4565fa8-d87f-4460-bd04-5ed1de2a7cb7"
OUTPUT_FILENAME = "Reflex_Dashboard_Manual.pdf"

# Screenshot mapping (Title -> Filename)
SCREENSHOTS = {
    "Dashboard Overview": "uploaded_image_1767292251004.png", # Large full view
    "KPI Cards": "uploaded_image_0_1767289428641.png",       # KPI section
    "Sales Data Tab": "uploaded_image_1767291520721.png"     # Data view
}

class PDF(FPDF):
    def header(self):
        # Header Color
        self.set_fill_color(44, 62, 80) # Dark Blue
        self.rect(0, 0, 210, 20, 'F')
        
        self.set_font('Arial', 'B', 15)
        self.set_text_color(255, 255, 255) # White text
        self.cell(0, 10, 'Reflex Dashboard Comprehensive Manual', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, num, label):
        self.add_page()
        self.set_font('Arial', 'B', 14)
        self.set_text_color(41, 128, 185) # Nice Blue
        self.cell(0, 10, f'Chapter {num} : {label}', 0, 1, 'L')
        self.line(10, 30, 200, 30) # Horizontal line
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Times', '', 12)
        self.set_text_color(0, 0, 0)
        # Sanitize body
        body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, body)
        self.ln()
    
    def section_header(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(230, 126, 34) # Orange
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)

    def add_code_module(self, module_name, filepath, description=None):
        self.section_header(f"File: {module_name}")
        
        if description:
            self.set_font('Arial', 'I', 10)
            self.set_text_color(50, 50, 50)
            # Sanitize description
            description = description.encode('latin-1', 'replace').decode('latin-1')
            self.multi_cell(0, 5, description)
            self.ln(2)
        
        self.set_font('Courier', '', 7) # Smaller font for full code
        self.set_text_color(0, 0, 0) # Black code
        self.set_fill_color(245, 245, 245) # Light Gray bg
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
                # Sanitize
                code = code.encode('latin-1', 'replace').decode('latin-1')
                code = code.replace('\t', '    ')
                
                # We want ALL code now, no truncation
                self.multi_cell(0, 4, code, 1, 'L', True)
        except Exception as e:
            self.multi_cell(0, 4, f"Could not read file: {e}", 1, 'L', True)
        self.ln(8)

    def add_image_output(self, title, image_filename):
        image_path = os.path.join(ARTIFACTS_DIR, image_filename)
        if os.path.exists(image_path):
            self.section_header(f"Visual Output: {title}")
            # Center image
            # Width = 150mm
            try:
                self.image(image_path, x=15, w=180) 
            except Exception as e:
                self.set_text_color(255, 0, 0)
                self.cell(0, 10, f"Error embedding image: {e}", 0, 1)
            self.ln(10)

def create_manual():
    pdf = PDF()
    pdf.alias_nb_pages()
    
    # --- 1. Project Overview ---
    pdf.chapter_title(1, 'Project Overview')
    pdf.chapter_body(
        "Introduction:\n"
        "The Enterprise Intelligence Suite is a Reflex-based web application enabling "
        "Sales and Logistics data analysis. This manual contains the COMPLETE source code "
        "of the project, organized by module."
    )
    
    # --- 2. Visual Gallery ---
    pdf.chapter_title(2, 'Visual Gallery')
    pdf.add_image_output("Dashboard Overview", SCREENSHOTS["Dashboard Overview"])
    pdf.add_image_output("Key Performance Indicators", SCREENSHOTS["KPI Cards"])

    # --- 3. Full Codebase ---
    pdf.chapter_title(3, 'Full Project Codebase')
    pdf.chapter_body(
        "The following pages contain the source code for every Python module in the project."
    )
    
    # Define directories to scan
    target_dir = os.path.join(PROJECT_ROOT, "reflex_dashboard")
    
    # Walk through the directory
    for root, dirs, files in os.walk(target_dir):
        # Sort for consistent order
        files.sort()
        dirs.sort()
        
        for filename in files:
            if filename.endswith(".py") and "__init__" not in filename and "test_" not in filename:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, PROJECT_ROOT)
                
                # Determine description based on path
                desc = "Source code module."
                if "state" in rel_path:
                    desc = "State Management Module: Handles data logic and events."
                elif "components" in rel_path:
                    desc = "UI Component Module: specific aspect of the dashboard interface."
                elif "reflex_dashboard.py" in filename:
                    desc = "Application Entry Point: Configuration and main routing."
                
                pdf.add_code_module(rel_path, filepath, desc)
                
                # Inject relevant screenshot if applicable
                if "overview.py" in filename:
                     pdf.add_image_output("Overview Tab Layout", SCREENSHOTS["KPI Cards"])

    
    pdf.output(OUTPUT_FILENAME)
    print(f"Manual successfully generated: {OUTPUT_FILENAME}")

if __name__ == '__main__':
    create_manual()
