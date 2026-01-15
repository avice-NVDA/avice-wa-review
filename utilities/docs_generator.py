#!/usr/bin/env python3
#===============================================================================
#      +===+ +--+ +--+ +=+ +===+ +===+
#      |   | |  | |  | | | |     |    
#      |===| |  +-+  | | | |     |=== 
#      |   |  |     |  | | |     |    
#      |   |   +---+   +=+ +===+ +===+                                 
#            ~ Alon Vice Tools ~
# Copyright (c) 2025 Alon Vice (avice)
# All rights reserved.
# This script is the intellectual property of Alon Vice.
# For permissions and licensing, contact: avice@nvidia.com
#===============================================================================

"""
Documentation Generator for Avice Workarea Review Tool

This module provides functionality to generate beautiful HTML and PDF documentation
from markdown files, and display formatted documentation in the terminal.

Author: Alon Vice (avice@nvidia.com)
Version: 1.0.0
"""

import os
import re
import webbrowser
import subprocess
from datetime import datetime
from pathlib import Path


class DocumentationGenerator:
    """Generate and display documentation for the Avice Workarea Review Tool"""
    
    def __init__(self):
        """Initialize the documentation generator"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.main_readme = os.path.join(self.script_dir, "README_avice_wa_review.md")
        self.org_readme = os.path.join(self.script_dir, "README_ORGANIZATION.md")
        self.output_dir = os.getcwd()
        
    def display_terminal_docs(self, section="all"):
        """Display formatted documentation in terminal"""
        print(self._get_logo())
        print(f"{self._get_color('CYAN')}Avice Workarea Review Tool - Documentation{self._get_color('RESET')}")
        print("=" * 80)
        
        if section == "all" or section == "usage":
            self._display_section("Usage", self._read_markdown_section(self.main_readme, "## Usage"))
        
        if section == "all" or section == "examples":
            self._display_section("Examples", self._read_markdown_section(self.main_readme, "## Examples"))
        
        if section == "all" or section == "troubleshooting":
            self._display_section("Troubleshooting", self._read_markdown_section(self.main_readme, "## Troubleshooting"))
        
        if section == "all" or section == "organization":
            self._display_section("Organization", self._read_markdown_section(self.org_readme, "## Directory Structure"))
    
    def generate_html_docs(self):
        """Generate beautiful HTML documentation"""
        html_content = self._generate_html_content()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"avice_wa_review_manual_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"{self._get_color('GREEN')}HTML documentation generated:{self._get_color('RESET')}")
        print(f"  File: {filepath}")
        print(f"  Open with: firefox {filename} &")
        
        return filepath
    
    def generate_and_open_html_docs(self):
        """Generate HTML documentation and open in browser"""
        filepath = self.generate_html_docs()
        try:
            webbrowser.open(f"file://{filepath}")
            print(f"{self._get_color('GREEN')}Opening documentation in browser...{self._get_color('RESET')}")
        except Exception as e:
            print(f"{self._get_color('YELLOW')}Could not open browser automatically: {e}{self._get_color('RESET')}")
            print(f"Please open manually: {filepath}")
    
    def generate_pdf_docs(self):
        """Generate PDF documentation"""
        # First generate HTML
        html_file = self.generate_html_docs()
        
        # Convert HTML to PDF using weasyprint or similar
        try:
            # Add user's local site-packages to path
            import sys
            import os
            user_site = os.path.expanduser("~/.local/lib/python3.11/site-packages")
            if user_site not in sys.path:
                sys.path.insert(0, user_site)
            
            import weasyprint
            pdf_file = html_file.replace('.html', '.pdf')
            weasyprint.HTML(filename=html_file).write_pdf(pdf_file)
            
            print(f"{self._get_color('GREEN')}PDF documentation generated:{self._get_color('RESET')}")
            print(f"  File: {pdf_file}")
            
        except ImportError:
            print(f"{self._get_color('YELLOW')}WeasyPrint not available. Installing...{self._get_color('RESET')}")
            try:
                subprocess.run(["/home/utils/Python/builds/3.11.9-20250715/bin/pip3", "install", "weasyprint"], check=True)
                # Add user's local site-packages to path
                user_site = os.path.expanduser("~/.local/lib/python3.11/site-packages")
                if user_site not in sys.path:
                    sys.path.insert(0, user_site)
                
                import weasyprint
                pdf_file = html_file.replace('.html', '.pdf')
                weasyprint.HTML(filename=html_file).write_pdf(pdf_file)
                print(f"{self._get_color('GREEN')}PDF documentation generated:{self._get_color('RESET')}")
                print(f"  File: {pdf_file}")
            except Exception as e:
                print(f"{self._get_color('RED')}Could not generate PDF: {e}{self._get_color('RESET')}")
                print(f"{self._get_color('YELLOW')}Please install weasyprint manually:{self._get_color('RESET')}")
                print("  pip3 install weasyprint")
    
    def _get_logo(self):
        """Get the ASCII art logo"""
        return """
#===============================================================================
#      +===+ +--+ +--+ +=+ +===+ +===+
#      |   | |  | |  | | | |     |    
#      |===| |  +-+  | | | |     |=== 
#      |   |  |     |  | | |     |    
#      |   |   +---+   +=+ +===+ +===+                                 
#            ~ Alon Vice Tools ~
# Copyright (c) 2025 Alon Vice (avice)
# All rights reserved.
# This script is the intellectual property of Alon Vice.
# For permissions and licensing, contact: avice@nvidia.com
#==============================================================================="""
    
    def _get_color(self, color_name):
        """Get color codes for terminal output"""
        colors = {
            'RED': '\033[31m',
            'GREEN': '\033[32m',
            'YELLOW': '\033[33m',
            'BLUE': '\033[34m',
            'MAGENTA': '\033[35m',
            'CYAN': '\033[36m',
            'WHITE': '\033[37m',
            'RESET': '\033[0m'
        }
        return colors.get(color_name, '')
    
    def _display_section(self, title, content):
        """Display a documentation section in terminal"""
        print(f"\n{self._get_color('CYAN')}{title}{self._get_color('RESET')}")
        print("-" * len(title))
        print(content)
        print()
    
    def _read_markdown_section(self, filepath, section_header):
        """Read a specific section from markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the section
            lines = content.split('\n')
            in_section = False
            section_lines = []
            
            for line in lines:
                if line.startswith(section_header):
                    in_section = True
                    continue
                elif in_section and line.startswith('##') and not line.startswith(section_header):
                    break
                elif in_section:
                    section_lines.append(line)
            
            return '\n'.join(section_lines).strip()
        except Exception as e:
            return f"Error reading section: {e}"
    
    def _generate_html_content(self):
        """Generate complete HTML documentation"""
        # Read markdown files
        main_content = self._read_markdown_file(self.main_readme)
        org_content = self._read_markdown_file(self.org_readme)
        
        # Convert markdown to HTML
        main_html = self._markdown_to_html(main_content)
        org_html = self._markdown_to_html(org_content)
        
        # Generate complete HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Avice Workarea Review Tool - Documentation</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo">
                <pre>{self._get_logo()}</pre>
            </div>
            <h1>Avice Workarea Review Tool</h1>
            <p class="subtitle">Comprehensive ASIC/SoC Design Workarea Analysis</p>
            <p class="version">Version 1.0.0 | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>
        
        <nav class="toc">
            <h2>Table of Contents</h2>
            <ul>
                <li><a href="#main-docs">Main Documentation</a></li>
                <li><a href="#organization">Organization Guide</a></li>
            </ul>
        </nav>
        
        <main class="content">
            <section id="main-docs">
                <h2>Main Documentation</h2>
                {main_html}
            </section>
            
            <section id="organization">
                <h2>Organization Guide</h2>
                {org_html}
            </section>
        </main>
        
        <footer class="footer">
            <p>Copyright (c) 2025 Alon Vice (avice@nvidia.com) | All rights reserved</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html_content
    
    def _read_markdown_file(self, filepath):
        """Read markdown file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    
    def _markdown_to_html(self, markdown_content):
        """Convert markdown to HTML (basic implementation)"""
        html = markdown_content
        
        # Headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # Code blocks
        html = re.sub(r'```bash\n(.*?)\n```', r'<pre class="code-bash"><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'```python\n(.*?)\n```', r'<pre class="code-python"><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'```(.*?)\n(.*?)\n```', r'<pre class="code"><code>\2</code></pre>', html, flags=re.DOTALL)
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Lists
        html = re.sub(r'^(\s*)\* (.+)$', r'\1<li>\2</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\s*)- (.+)$', r'\1<li>\2</li>', html, flags=re.MULTILINE)
        
        # Wrap consecutive list items in ul
        html = re.sub(r'(<li>.*</li>\n?)+', lambda m: f'<ul>\n{m.group(0)}</ul>', html, flags=re.DOTALL)
        
        # Line breaks
        html = html.replace('\n', '<br>\n')
        
        return html
    
    def _get_css_styles(self):
        """Get CSS styles for HTML documentation"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .logo pre {
            font-size: 12px;
            margin-bottom: 20px;
            opacity: 0.9;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.2em;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .version {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .toc {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .toc h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        
        .toc ul {
            list-style: none;
        }
        
        .toc li {
            margin: 8px 0;
        }
        
        .toc a {
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }
        
        .toc a:hover {
            color: #2980b9;
            text-decoration: underline;
        }
        
        .content {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        h1, h2, h3, h4 {
            color: #2c3e50;
            margin: 25px 0 15px 0;
        }
        
        h1 {
            font-size: 2.2em;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        
        h2 {
            font-size: 1.8em;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }
        
        h3 {
            font-size: 1.4em;
            color: #34495e;
        }
        
        h4 {
            font-size: 1.2em;
            color: #7f8c8d;
        }
        
        p {
            margin: 15px 0;
            text-align: justify;
        }
        
        code {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 2px 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #e83e8c;
        }
        
        .code-bash, .code-python, .code {
            background-color: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
        
        .code-bash code, .code-python code, .code code {
            background: none;
            border: none;
            padding: 0;
            color: inherit;
            font-size: 0.9em;
        }
        
        ul, ol {
            margin: 15px 0;
            padding-left: 30px;
        }
        
        li {
            margin: 8px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }
        
        th, td {
            border: 1px solid #dee2e6;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .content {
                padding: 20px;
            }
        }
        """


if __name__ == "__main__":
    # Test the documentation generator
    doc_gen = DocumentationGenerator()
    doc_gen.display_terminal_docs("usage")
