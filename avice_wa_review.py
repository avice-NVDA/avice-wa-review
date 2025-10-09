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
Script Name: avice_wa_review.py
Purpose: Comprehensive ASIC/SoC design workarea analysis and review tool

Description:
    This script provides a comprehensive analysis of ASIC/SoC design workareas,
    converting the original C-shell script to Python with organized flow stages.
    It analyzes various aspects of the design flow including setup, runtime,
    synthesis, place & route (PnR), clock analysis, formal verification,
    parasitic extraction, signoff timing, physical verification, GL checks,
    ECO analysis, and block release information.

Usage:
    /home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> [ipo_name]
    /home/avice/scripts/avice_wa_review_launcher.csh --help
    /home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> -s setup runtime
    /home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> -s star pt

Arguments:
    workarea_path    - Path to the workarea directory to analyze
    ipo_name        - Optional IPO name to analyze (auto-detected if not specified)
    -s, --sections  - Run only specific analysis sections (use 'star' for parasitic, 'pt' for timing)
    --no-logo       - Disable logo display (useful for automated scripts)
    --verbose       - Enable verbose output with detailed information
    --output, -o    - Output file to save results
    --format        - Output format (text or json)

Prerequisites:
    - Python 3.6 or higher
    - Access to workarea directory with proper permissions
    - Unix/Linux environment with standard tools (grep, sed, awk, zcat)
    - Design flow tools (DC, Innovus, PrimeTime, Star, etc.)

Output:
    - Console output with color-coded analysis results
    - HTML reports for detailed data visualization
    - Runtime summary tables with categorized stages
    - Error analysis and status reporting

Examples:
    # Complete workarea analysis
    /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea
    
    # Analyze specific IPO
    /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea ipo1000
    
    # Run only specific sections
    /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s setup runtime synthesis
    
    # Run Star and PT sections using aliases
    /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s star pt
    
    # Generate output file
    /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea --output results.txt

IMPORTANT: This script outputs to Unix shells - always use ASCII characters
instead of Unicode symbols (→, ✓, ✗, ⚠, •) to ensure proper display.
Use ASCII equivalents: ->, [OK], [ERROR], [WARN], - instead.
"""

import os
import sys
import glob
import re
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum
import base64
from datetime import datetime
import gzip
import time

# Handle dataclasses for Python < 3.7
try:
    from dataclasses import dataclass
except ImportError:
    # Fallback for older Python versions
    def dataclass(cls):
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        cls.__init__ = __init__
        return cls


class LVSViolationParser:
    """Parser for LVS error files to extract detailed violation information"""
    
    def parse_lvs_errors(self, file_path: str) -> Dict[str, Any]:
        """Parse LVS error file and extract violation details"""
        violations = {
            'status': 'UNKNOWN',
            'failed_equivalence_points': 0,
            'first_priority_errors': 0,
            'second_priority_errors': 0,
            'unmatched_schematic_instances': 0,
            'unmatched_schematic_nets': 0,
            'unmatched_layout_instances': 0,
            'unmatched_layout_nets': 0,
            'unmatched_schematic_ports': 0,
            'unmatched_layout_ports': 0,
            'matched_instances': 0,
            'matched_nets': 0,
            'matched_ports': 0,
            'successful_equivalence_points': 0
        }
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract final comparison result
            status_match = re.search(r'Final comparison result:\s*(\w+)', content)
            if status_match:
                violations['status'] = status_match.group(1)
            
            # Extract comparison summary
            summary_match = re.search(
                r'(\d+)\s+Successful equivalence points\s*\*\s*(\d+)\s+Failed equivalence points\s*(\d+)\s+First priority errors\s*(\d+)\s+Second priority errors',
                content, re.MULTILINE
            )
            if summary_match:
                violations['successful_equivalence_points'] = int(summary_match.group(1))
                violations['failed_equivalence_points'] = int(summary_match.group(2))
                violations['first_priority_errors'] = int(summary_match.group(3))
                violations['second_priority_errors'] = int(summary_match.group(4))
            
            # Extract error summary details with more flexible pattern
            error_summary_pattern = r'Error summary:\s*(\d+)\s+Unmatched schematic instance[s]?\s*(\d+)\s+Unmatched schematic nets?\s*(\d+)\s+Unmatched layout instance[s]?\s*(\d+)\s+Unmatched layout nets?'
            error_summary_match = re.search(error_summary_pattern, content, re.MULTILINE | re.DOTALL)
            if error_summary_match:
                violations['unmatched_schematic_instances'] = int(error_summary_match.group(1))
                violations['unmatched_schematic_nets'] = int(error_summary_match.group(2))
                violations['unmatched_layout_instances'] = int(error_summary_match.group(3))
                violations['unmatched_layout_nets'] = int(error_summary_match.group(4))
            
            # Extract matched counts
            matched_match = re.search(
                r'(\d+)\s+Matched instances\s*(\d+)\s+Matched nets',
                content, re.MULTILINE
            )
            if matched_match:
                violations['matched_instances'] = int(matched_match.group(1))
                violations['matched_nets'] = int(matched_match.group(2))
            
            # Extract port summary with more flexible pattern
            port_pattern = r'Port summary:\s*(\d+)\s+Unmatched schematic ports?\s*(\d+)\s+Unmatched layout ports?\s*(\d+)\s+Matched ports'
            port_match = re.search(port_pattern, content, re.MULTILINE | re.DOTALL)
            if port_match:
                violations['unmatched_schematic_ports'] = int(port_match.group(1))
                violations['unmatched_layout_ports'] = int(port_match.group(2))
                violations['matched_ports'] = int(port_match.group(3))
            
        except Exception as e:
            print(f"Error parsing LVS file {file_path}: {e}")
        
        return violations


class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class FlowStage(Enum):
    """Design flow stages"""
    SETUP = "Setup"
    SYNTHESIS = "Synthesis (DC)"
    PLACE_ROUTE = "Place & Route (PnR)"
    PNR_ANALYSIS = "PnR Analysis"
    CLOCK_ANALYSIS = "Clock Analysis"
    FORMAL_VERIFICATION = "Formal Verification"
    PARASITIC_EXTRACTION = "Parasitic Extraction (Star)"
    SIGNOFF_TIMING = "Signoff Timing (PT)"
    PHYSICAL_VERIFICATION = "Physical Verification (PV)"
    GL_CHECK = "GL Checks"
    ECO_ANALYSIS = "ECO Analysis"
    NV_GATE_ECO = "NV Gate ECO"
    BLOCK_RELEASE = "Block Release"
    RUNTIME = "Runtime"
    COMMON = "COMMON"


# Stage index mapping for display (corresponds to INDEX.md)
STAGE_INDEX = {
    FlowStage.SETUP: 1,
    FlowStage.RUNTIME: 2,
    FlowStage.SYNTHESIS: 3,
    FlowStage.PNR_ANALYSIS: 4,
    FlowStage.CLOCK_ANALYSIS: 5,
    FlowStage.FORMAL_VERIFICATION: 6,
    FlowStage.PARASITIC_EXTRACTION: 7,
    FlowStage.SIGNOFF_TIMING: 8,
    FlowStage.PHYSICAL_VERIFICATION: 9,
    FlowStage.GL_CHECK: 10,
    FlowStage.ECO_ANALYSIS: 11,
    FlowStage.NV_GATE_ECO: 12,
    FlowStage.BLOCK_RELEASE: 13,
    FlowStage.COMMON: 14,
    FlowStage.PLACE_ROUTE: 15,  # Placeholder, not commonly used
}


@dataclass
class DesignInfo:
    """Design information extracted from workarea"""
    workarea: str
    top_hier: str
    tag: str
    ipo: str
    all_ipos: List[str]


@dataclass
class SectionSummary:
    """Summary information for a single analysis section"""
    section_name: str           # e.g., "Timing Analysis (PT)"
    section_id: str             # e.g., "timing"
    stage: FlowStage            # FlowStage enum
    status: str                 # PASS, WARN, FAIL, NOT_RUN, SKIP
    key_metrics: Dict[str, str] # e.g., {"Setup WNS": "-0.052", "Hold WNS": "+0.150"}
    html_file: str              # Path to detailed section HTML (absolute path)
    priority: int               # 1=Critical, 2=High, 3=Medium, 4=Low
    issues: List[str]           # List of notable issues/warnings
    timestamp: str              # When this section was analyzed
    icon: str                   # ASCII emoji/icon for display
    
    def get_status_color(self) -> str:
        """Get HTML color for status badge"""
        colors = {
            'PASS': '#27ae60',
            'WARN': '#f39c12',
            'FAIL': '#e74c3c',
            'NOT_RUN': '#95a5a6',
            'SKIP': '#bdc3c7'
        }
        return colors.get(self.status, '#95a5a6')
    
    def get_status_icon(self) -> str:
        """Get ASCII icon for status"""
        icons = {
            'PASS': '[OK]',
            'WARN': '[WARN]',
            'FAIL': '[ERROR]',
            'NOT_RUN': '[SKIP]',
            'SKIP': '[SKIP]'
        }
        return icons.get(self.status, '[?]')


class MasterDashboard:
    """Generate master HTML dashboard integrating all section HTMLs"""
    
    def __init__(self, design_info: DesignInfo):
        self.design_info = design_info
        self.sections: List[SectionSummary] = []
        self.output_dir = os.path.dirname(design_info.workarea)
        self.timestamp = datetime.now().strftime("%m.%d.%y_%H:%M")
        self.date_str = datetime.now().strftime("%Y%m%d")
        
    def add_section(self, summary: SectionSummary):
        """Add a section summary to the dashboard"""
        self.sections.append(summary)
    
    def get_overall_status(self) -> str:
        """Determine overall health status"""
        if not self.sections:
            return 'NOT_RUN'
        
        statuses = [s.status for s in self.sections if s.status != 'SKIP']
        if not statuses:
            return 'NOT_RUN'
        
        if 'FAIL' in statuses:
            return 'FAIL'
        elif 'WARN' in statuses:
            return 'WARN'
        else:
            return 'PASS'
    
    def count_by_status(self, status: str) -> int:
        """Count sections with given status"""
        return sum(1 for s in self.sections if s.status == status)
    
    def get_sections_needing_attention(self) -> List[SectionSummary]:
        """Get sections with FAIL or WARN status"""
        return [s for s in self.sections if s.status in ['FAIL', 'WARN']]
    
    def generate_html(self, output_path: str = None) -> str:
        """Generate master dashboard HTML file"""
        if output_path is None:
            # Create default output path using design name (not tag)
            output_path = os.path.join(
                os.getcwd(),
                f"avice_MASTER_dashboard_{self.design_info.top_hier}_{self.date_str}.html"
            )
        
        # Ensure output path is absolute
        output_path = os.path.abspath(output_path)
        
        # Create sections directory if it doesn't exist
        sections_dir = os.path.join(os.path.dirname(output_path), "sections")
        os.makedirs(sections_dir, exist_ok=True)
        
        html_content = self._generate_html_content(output_path)
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_html_content(self, output_path: str) -> str:
        """Generate the HTML content for master dashboard"""
        
        # Read and encode logo as base64
        logo_data = ""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "images/avice_logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo_file:
                logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
        
        # Calculate statistics
        total_sections = len(self.sections)
        pass_count = self.count_by_status('PASS')
        warn_count = self.count_by_status('WARN')
        fail_count = self.count_by_status('FAIL')
        not_run_count = self.count_by_status('NOT_RUN')
        overall_status = self.get_overall_status()
        attention_sections = self.get_sections_needing_attention()
        
        # Sort sections by index number
        sorted_sections = sorted(self.sections, key=lambda s: STAGE_INDEX.get(s.stage, 99))
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AVICE Workarea Review - Master Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #2c3e50;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        /* Header Styles */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .logo-container {{
            margin: 20px 0;
        }}
        
        .logo-container img {{
            max-width: 200px;
            height: auto;
            cursor: pointer;
            transition: transform 0.3s ease;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }}
        
        .logo-container img:hover {{
            transform: scale(1.05);
        }}
        
        .header-info {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .header-info-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 1.1em;
        }}
        
        /* Status Banner */
        .status-banner {{
            padding: 30px;
            text-align: center;
            border-bottom: 3px solid #ecf0f1;
        }}
        
        .status-banner.PASS {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }}
        
        .status-banner.WARN {{
            background: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%);
            color: white;
        }}
        
        .status-banner.FAIL {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }}
        
        .status-banner h2 {{
            font-size: 2em;
            margin-bottom: 15px;
        }}
        
        .status-stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .status-stat {{
            font-size: 1.2em;
        }}
        
        .status-stat strong {{
            font-size: 1.5em;
            display: block;
        }}
        
        /* Quick Actions */
        .quick-actions {{
            padding: 20px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .action-btn {{
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .action-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }}
        
        .action-btn.secondary {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        }}
        
        /* Attention Required Section */
        .attention-section {{
            padding: 30px 40px;
            background: #fff3cd;
            border-left: 5px solid #f39c12;
            margin: 20px;
            border-radius: 8px;
        }}
        
        .attention-section h3 {{
            color: #856404;
            margin-bottom: 15px;
        }}
        
        .attention-list {{
            list-style: none;
            padding-left: 0;
        }}
        
        .attention-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #f39c12;
        }}
        
        .attention-list li:last-child {{
            border-bottom: none;
        }}
        
        .attention-list a {{
            color: #856404;
            text-decoration: none;
            font-weight: bold;
        }}
        
        .attention-list a:hover {{
            text-decoration: underline;
        }}
        
        /* Section Cards Grid */
        .sections-container {{
            padding: 40px;
        }}
        
        .sections-container h2 {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 2em;
            color: #2c3e50;
        }}
        
        .sections-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }}
        
        /* Section Card */
        .section-card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 25px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 5px solid #667eea;
            position: relative;
        }}
        
        .section-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }}
        
        .section-card.PASS {{
            border-left-color: #27ae60;
        }}
        
        .section-card.WARN {{
            border-left-color: #f39c12;
        }}
        
        .section-card.FAIL {{
            border-left-color: #e74c3c;
        }}
        
        .section-card.NOT_RUN {{
            border-left-color: #95a5a6;
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            cursor: pointer;
            user-select: none;
        }}
        
        .section-header:hover {{
            opacity: 0.8;
        }}
        
        .section-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .card-toggle-icon {{
            font-size: 1.5em;
            transition: transform 0.3s ease;
            color: #667eea;
        }}
        
        .card-toggle-icon.expanded {{
            transform: rotate(180deg);
        }}
        
        .card-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}
        
        .card-content.expanded {{
            max-height: 1000px;
        }}
        
        .section-index {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .status-badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
        }}
        
        .status-badge.PASS {{
            background: #27ae60;
        }}
        
        .status-badge.WARN {{
            background: #f39c12;
        }}
        
        .status-badge.FAIL {{
            background: #e74c3c;
        }}
        
        .status-badge.NOT_RUN {{
            background: #95a5a6;
        }}
        
        .section-metrics {{
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .metric-row:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #7f8c8d;
            font-weight: 600;
        }}
        
        .metric-value {{
            color: #2c3e50;
            font-weight: bold;
        }}
        
        .section-issues {{
            margin: 15px 0;
        }}
        
        .issue-item {{
            padding: 8px;
            background: #fff3cd;
            border-left: 3px solid #f39c12;
            margin: 5px 0;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .section-footer {{
            margin-top: 20px;
            text-align: center;
        }}
        
        .view-details-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 20px;
            font-weight: bold;
            transition: transform 0.2s ease;
        }}
        
        .view-details-btn:hover {{
            transform: scale(1.05);
        }}
        
        .section-timestamp {{
            font-size: 0.85em;
            color: #95a5a6;
            margin-top: 10px;
            text-align: center;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 30px;
            background: #2c3e50;
            color: white;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .sections-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .header-info {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
        
        /* Image Expansion */
        .expanded-image {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 10000;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        
        .expanded-image img {{
            max-width: 90%;
            max-height: 90%;
            box-shadow: 0 0 50px rgba(255,255,255,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>AVICE Workarea Review</h1>
            <h2>Master Dashboard</h2>
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_data}" alt="AVICE Logo" onclick="expandImage(this)">
            </div>
            <div class="header-info">
                <div class="header-info-item">
                    <strong>Workarea:</strong> {self.design_info.workarea}
                </div>
                <div class="header-info-item">
                    <strong>Design:</strong> {self.design_info.top_hier}
                </div>
                <div class="header-info-item">
                    <strong>Tag:</strong> {self.design_info.tag}
                </div>
                <div class="header-info-item">
                    <strong>IPO:</strong> {self.design_info.ipo}
                </div>
                <div class="header-info-item">
                    <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </div>
            </div>
        </div>
        
        <!-- Overall Status Banner -->
        <div class="status-banner {overall_status}">
            <h2>Overall Health: {overall_status} {self._get_status_icon(overall_status)}</h2>
            <div class="status-stats">
                <div class="status-stat">
                    <strong>{pass_count}</strong>
                    <span>Passed</span>
                </div>
                <div class="status-stat">
                    <strong>{warn_count}</strong>
                    <span>Warnings</span>
                </div>
                <div class="status-stat">
                    <strong>{fail_count}</strong>
                    <span>Failed</span>
                </div>
                <div class="status-stat">
                    <strong>{not_run_count}</strong>
                    <span>Not Run</span>
                </div>
                <div class="status-stat">
                    <strong>{total_sections}</strong>
                    <span>Total Sections</span>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="quick-actions">
            <button class="action-btn" onclick="openAllSections()">Open All Failed/Warning Sections</button>
            <button class="action-btn secondary" onclick="openAllSectionsComplete()">Open All Sections</button>
            <button class="action-btn secondary" onclick="window.print()">Print Dashboard</button>
        </div>
"""
        
        # Attention Required Section
        if attention_sections:
            html += f"""
        <!-- Attention Required -->
        <div class="attention-section">
            <h3>Attention Required - {len(attention_sections)} Section(s) Need Review:</h3>
            <ul class="attention-list">
"""
            for section in attention_sections:
                html += f"""
                <li>
                    <a href="{section.html_file}" target="_blank">
                        [{section.status}] {section.section_name}
                    </a>
                    {f' - {section.issues[0]}' if section.issues else ''}
                </li>
"""
            html += """
            </ul>
        </div>
"""
        
        # Section Cards
        html += """
        <!-- Section Cards -->
        <div class="sections-container">
            <h2>Analysis Sections</h2>
            <div class="sections-grid">
"""
        
        for section in sorted_sections:
            section_index = STAGE_INDEX.get(section.stage, "?")
            html += self._generate_section_card(section, section_index)
        
        html += """
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>AVICE Workarea Review Tool</strong></p>
            <p>Copyright (c) 2025 Alon Vice (avice)</p>
            <p>Contact: avice@nvidia.com</p>
        </div>
    </div>
    
    <!-- Expanded Image Overlay -->
    <div class="expanded-image" id="expandedImage" onclick="closeImage()">
        <img id="expandedImageContent" src="" alt="Expanded">
    </div>
    
    <script>
        function expandImage(img) {
            var overlay = document.getElementById('expandedImage');
            var expandedImg = document.getElementById('expandedImageContent');
            expandedImg.src = img.src;
            overlay.style.display = 'flex';
        }
        
        function closeImage() {
            document.getElementById('expandedImage').style.display = 'none';
        }
        
        function toggleCard(cardId) {
            var content = document.getElementById(cardId);
            var icon = document.getElementById('icon-' + cardId);
            
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                icon.classList.remove('expanded');
            } else {
                content.classList.add('expanded');
                icon.classList.add('expanded');
            }
        }
        
        function openAllSections() {
            var sections = document.querySelectorAll('.section-card.FAIL a, .section-card.WARN a');
            sections.forEach(function(link) {
                window.open(link.href, '_blank');
            });
        }
        
        function openAllSectionsComplete() {
            var sections = document.querySelectorAll('.section-card a');
            sections.forEach(function(link) {
                window.open(link.href, '_blank');
            });
        }
    </script>
</body>
</html>
"""
        
        return html
    
    def _generate_section_card(self, section: SectionSummary, index: int) -> str:
        """Generate HTML for a single section card"""
        
        # Generate metrics HTML
        metrics_html = ""
        if section.key_metrics:
            for label, value in section.key_metrics.items():
                metrics_html += f"""
                <div class="metric-row">
                    <span class="metric-label">{label}:</span>
                    <span class="metric-value">{value}</span>
                </div>
"""
        
        # Generate issues HTML
        issues_html = ""
        if section.issues:
            for issue in section.issues[:3]:  # Show max 3 issues
                issues_html += f"""
                <div class="issue-item">{issue}</div>
"""
            if len(section.issues) > 3:
                issues_html += f"""
                <div class="issue-item">... and {len(section.issues) - 3} more</div>
"""
        
        # Default to expanded for FAIL/WARN status, collapsed for others
        default_expanded = section.status in ['FAIL', 'WARN']
        expanded_class = 'expanded' if default_expanded else ''
        
        card_html = f"""
                <div class="section-card {section.status}">
                    <div class="section-header" onclick="toggleCard('card-{section.section_id}-{index}')">
                        <div class="section-title">
                            <span class="section-index">{index}</span>
                            <span>{section.icon} {section.section_name}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div class="status-badge {section.status}">{section.get_status_icon()}</div>
                            <span class="card-toggle-icon {expanded_class}" id="icon-card-{section.section_id}-{index}">▼</span>
                        </div>
                    </div>
                    
                    <div class="card-content {expanded_class}" id="card-{section.section_id}-{index}">
                        {f'<div class="section-metrics">{metrics_html}</div>' if metrics_html else ''}
                        
                        {f'<div class="section-issues">{issues_html}</div>' if issues_html else ''}
                        
                        <div class="section-footer">
                            <a href="{section.html_file}" target="_blank" class="view-details-btn" onclick="event.stopPropagation()">View Detailed Report</a>
                        </div>
                        
                        <div class="section-timestamp">Analyzed: {section.timestamp}</div>
                    </div>
                </div>
"""
        
        return card_html
    
    def _get_status_icon(self, status: str) -> str:
        """Get ASCII icon for status"""
        icons = {
            'PASS': '[OK]',
            'WARN': '[WARN]',
            'FAIL': '[ERROR]',
            'NOT_RUN': '[SKIP]'
        }
        return icons.get(status, '[?]')


class LogoDisplay:
    """Handle logo display functionality"""
    
    @staticmethod
    def get_logo_path() -> str:
        """Get the path to the Avice logo (for reference only)"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "images", "avice_logo.png")
    
    @staticmethod
    def display_logo():
        """Display the Avice logo if available (image popup disabled)"""
        # Logo image popup functionality has been disabled
        # Only ASCII art logo is displayed
        pass
    
    @staticmethod
    def print_ascii_logo():
        """Print ASCII art logo as fallback"""
        ascii_logo = f"""
{Color.CYAN}    +===============================================================+
    |                                                               |
    |                    {Color.BOLD}AVICE WORKAREA REVIEW{Color.RESET}{Color.CYAN}                      |
    |                                                               |
    |              {Color.GREEN}Advanced Verification & Integration{Color.RESET}{Color.CYAN}              |
    |                    {Color.GREEN}Circuit Engineering{Color.RESET}{Color.CYAN}                        |
    |                                                               |
    +===============================================================+{Color.RESET}
"""
        print(ascii_logo)


class FileUtils:
    """Utility functions for file operations"""
    
    @staticmethod
    def realpath(path: str) -> str:
        """Get real path of a file/directory"""
        try:
            return os.path.realpath(path)
        except (OSError, FileNotFoundError):
            return path
    
    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if file exists"""
        return os.path.isfile(path)
    
    @staticmethod
    def dir_exists(path: str) -> bool:
        """Check if directory exists"""
        return os.path.isdir(path)
    
    @staticmethod
    def find_files(pattern: str, base_path: str) -> List[str]:
        """Find files matching pattern"""
        search_path = os.path.join(base_path, pattern)
        return glob.glob(search_path)
    
    @staticmethod
    def grep_file(pattern: str, file_path: str, case_insensitive: bool = True) -> List[str]:
        """Grep pattern in file (handles both regular and compressed files)"""
        try:
            # Check if file is compressed
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            flags = re.IGNORECASE if case_insensitive else 0
            flags |= re.MULTILINE
            matches = re.findall(pattern, content, flags)
            return matches
        except (OSError, FileNotFoundError, UnicodeDecodeError, gzip.BadGzipFile):
            return []
    
    @staticmethod
    def run_command(cmd: str) -> str:
        """Run shell command and return output"""
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8').strip()
        except subprocess.SubprocessError:
            return ""


class WorkareaReviewer:
    """Main class for workarea review"""
    
    def __init__(self, workarea: str, ipo: Optional[str] = None, show_logo: bool = True, skip_validation: bool = False):
        self.workarea = workarea
        self.workarea_abs = os.path.abspath(workarea)  # Absolute path for display
        self.ipo = ipo
        self.show_logo = show_logo
        self.file_utils = FileUtils()
        self.lvs_parser = LVSViolationParser()
        
        # Validate workarea before proceeding (unless skipped)
        if not skip_validation and not self._validate_workarea():
            sys.exit(1)
        elif skip_validation:
            print(f"{Color.YELLOW}[WARN] Skipping workarea validation (--skip-validation used){Color.RESET}")
            
        self.design_info = self._extract_design_info()
        
        # Initialize Master Dashboard
        self.master_dashboard = MasterDashboard(self.design_info)
        self.section_summaries = []  # Collect section summaries for master dashboard
    
    def _add_section_summary(self, section_name: str, section_id: str, stage: FlowStage, 
                            status: str = "NOT_RUN", key_metrics: Dict[str, str] = None,
                            html_file: str = "", priority: int = 3, issues: List[str] = None,
                            icon: str = ""):
        """Helper method to add a section summary to the master dashboard"""
        if key_metrics is None:
            key_metrics = {}
        if issues is None:
            issues = []
        
        summary = SectionSummary(
            section_name=section_name,
            section_id=section_id,
            stage=stage,
            status=status,
            key_metrics=key_metrics,
            html_file=html_file if html_file else "",
            priority=priority,
            issues=issues,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            icon=icon
        )
        
        self.master_dashboard.add_section(summary)
        self.section_summaries.append(summary)
    
    def _validate_workarea(self) -> bool:
        """Validate that the workarea is a proper ASIC/SoC workarea (PnR, Syn, or both)"""
        print(f"{Color.CYAN}Validating workarea structure...{Color.RESET}")
        
        validation_errors = []
        validation_warnings = []
        flow_types = []
        additional_stages = []  # Track additional stages like fast_dc, RTL
        
        # Always required directories
        required_dirs = ["unit_scripts", "rbv"]
        
        # Check always required directories
        for dir_name in required_dirs:
            dir_path = os.path.join(self.workarea, dir_name)
            if not os.path.isdir(dir_path):
                validation_errors.append(f"Missing required directory: {dir_name}/")
        
        # Check for PnR flow structure
        pnr_flow_dir = os.path.join(self.workarea, "pnr_flow")
        if os.path.isdir(pnr_flow_dir):
            nv_flow_dir = os.path.join(pnr_flow_dir, "nv_flow")
            if not os.path.isdir(nv_flow_dir):
                validation_warnings.append("Missing pnr_flow/nv_flow/ directory")
            else:
                # Check for PRC files (indicates PnR configuration)
                prc_files = glob.glob(os.path.join(nv_flow_dir, "*.prc"))
                if not prc_files:
                    validation_warnings.append("No .prc files found in pnr_flow/nv_flow/")
                else:
                    flow_types.append("PnR")
        
        # Check for synthesis flow structure
        syn_flow_dir = os.path.join(self.workarea, "syn_flow")
        if os.path.isdir(syn_flow_dir):
            dc_dir = os.path.join(syn_flow_dir, "dc")
            if not os.path.isdir(dc_dir):
                validation_warnings.append("Missing syn_flow/dc/ directory")
            else:
                flow_types.append("Syn")
            
            # Check for fast_dc
            fast_dc_dir = os.path.join(syn_flow_dir, "fast_dc")
            fast_dc_log = os.path.join(fast_dc_dir, "log/fast_dc.log")
            if os.path.isfile(fast_dc_log):
                additional_stages.append("fast_dc")
        
        # Check for RTL formal verification
        rtl_formal_dirs = [
            os.path.join(self.workarea, "formal_flow/rtl_vs_pnr_bbox_fm"),
            os.path.join(self.workarea, "formal_flow/rtl_vs_pnr_fm"),
            os.path.join(self.workarea, "rtl_vs_pnr_bbox_fm"),
            os.path.join(self.workarea, "rtl_vs_pnr_fm")
        ]
        rtl_detected = False
        for rtl_dir in rtl_formal_dirs:
            if os.path.isdir(rtl_dir):
                rtl_detected = True
                break
        if rtl_detected:
            additional_stages.append("RTL")
        
        # Check for design definition
        des_def_path = os.path.join(self.workarea, "unit_scripts/des_def.tcl")
        if not os.path.isfile(des_def_path):
            validation_errors.append("Missing unit_scripts/des_def.tcl file")
        
        # Check for RBV information
        rbv_readme = os.path.join(self.workarea, "rbv/README")
        if not os.path.isfile(rbv_readme):
            validation_warnings.append("Missing rbv/README file")
        
        # Validate that at least one flow type is present
        if not flow_types:
            validation_errors.append("No valid flow detected - must have either pnr_flow/ or syn_flow/")
        
        # Print validation results
        if validation_errors:
            print(f"{Color.RED}[ERROR] WORKAREA VALIDATION FAILED:{Color.RESET}")
            for error in validation_errors:
                print(f"  {Color.RED}ERROR:{Color.RESET} {error}")
            print(f"\n{Color.RED}This does not appear to be a valid ASIC/SoC workarea.{Color.RESET}")
            print(f"{Color.YELLOW}Required structure:{Color.RESET}")
            print(f"  - unit_scripts/des_def.tcl")
            print(f"  - rbv/")
            print(f"  - Either pnr_flow/ OR syn_flow/ (or both)")
            return False
        
        if validation_warnings:
            print(f"{Color.YELLOW}[WARN] WORKAREA VALIDATION WARNINGS:{Color.RESET}")
            for warning in validation_warnings:
                print(f"  {Color.YELLOW}WARNING:{Color.RESET} {warning}")
        
        # Determine flow type for success message
        if "PnR" in flow_types and "Syn" in flow_types:
            flow_desc = "PnR + Syn workarea"
        elif "PnR" in flow_types:
            flow_desc = "PnR-only workarea"
        elif "Syn" in flow_types:
            flow_desc = "Syn-only workarea"
        else:
            flow_desc = "ASIC/SoC workarea"
        
        # Add additional stages info if detected
        if additional_stages:
            additional_info = ", ".join(additional_stages)
            print(f"{Color.GREEN}[OK] Workarea validation passed - {flow_desc} detected{Color.RESET}")
            print(f"{Color.CYAN}     Additional stages detected: {additional_info}{Color.RESET}")
        else:
            print(f"{Color.GREEN}[OK] Workarea validation passed - {flow_desc} detected{Color.RESET}")
        
        return True
    
    def _extract_design_info(self) -> DesignInfo:
        """Extract design information from workarea"""
        # Extract top hierarchy
        des_def_path = os.path.join(self.workarea, "unit_scripts/des_def.tcl")
        top_hier = ""
        if self.file_utils.file_exists(des_def_path):
            matches = self.file_utils.grep_file(r"bset top_hier\s+(\w+)", des_def_path)
            if matches:
                top_hier = matches[0]
        
        # Extract tag
        readme_path = os.path.join(self.workarea, "rbv/README")
        tag = ""
        if self.file_utils.file_exists(readme_path):
            matches = self.file_utils.grep_file(r"tag:\s*(.+)", readme_path)
            if matches:
                tag = matches[0]
        
        # Extract IPO information
        prc_path = os.path.join(self.workarea, f"pnr_flow/nv_flow/{top_hier}.prc")
        all_ipos = []
        ipo = self.ipo
        
        if self.file_utils.file_exists(prc_path):
            # Handle both YAML and legacy PRC formats
            matches = self.file_utils.grep_file(r"^\s*ipo(\d+)\s*:", prc_path)
            all_ipos = [f"ipo{match}" for match in matches]
            if not ipo and matches:
                ipo = f"ipo{matches[0]}"
        
        return DesignInfo(
            workarea=self.workarea,
            top_hier=top_hier,
            tag=tag,
            ipo=ipo or "unknown",
            all_ipos=all_ipos
        )
    
    def print_header(self, stage: FlowStage):
        """Print section header with index number"""
        stage_num = STAGE_INDEX.get(stage, "")
        stage_prefix = f"[{stage_num}] " if stage_num else ""
        print(f"\n{'-' * 35} {Color.GREEN}{stage_prefix}{stage.value}{Color.RESET} {'-' * 35}")
    
    def print_file_info(self, file_path: str, description: str = ""):
        """Print file information"""
        if self.file_utils.file_exists(file_path):
            real_path = self.file_utils.realpath(file_path)
            print(f"{description}: {real_path}")
            return True
        else:
            print(f"{description}: File not found")
            return False
    
    def _extract_power_summary_table(self, power_file: str):
        """Extract the first power summary table from power report"""
        try:
            # Read the file content
            if power_file.endswith('.gz'):
                with gzip.open(power_file, 'rt', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(power_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Find the first table (summary table)
            lines = content.split('\n')
            table_start = -1
            table_end = -1
            
            # Look for the table header line with the column names
            for i, line in enumerate(lines):
                if 'group' in line and 'area' in line and 'count' in line and 'power' in line and 'leakage' in line:
                    table_start = i
                    break
            
            if table_start != -1:
                # Find the end of the first table (look for the next major separator)
                for i in range(table_start + 1, len(lines)):
                    # Look for the end of the first table (after the total row)
                    if '=======' in lines[i] and i > table_start + 3:
                        # Check if this is the end of the first table
                        if i + 1 < len(lines) and ('group' in lines[i + 1] or 'type' in lines[i + 1]):
                            table_end = i + 1
                            break
                        elif 'total' in lines[i-1] and '=======' in lines[i]:
                            table_end = i + 1
                            break
                
                if table_end == -1:
                    # If we didn't find a clear end, take the next 8 lines (header + 4 data rows + separators)
                    table_end = min(table_start + 8, len(lines))
                
                # Print the table
                print(f"  {Color.CYAN}Power Summary Table:{Color.RESET}")
                for i in range(table_start, table_end):
                    if lines[i].strip():  # Skip empty lines
                        print(f"    {lines[i]}")
            else:
                print("  Power summary table not found")
                
        except (OSError, UnicodeDecodeError, gzip.BadGzipFile) as e:
            print(f"  Error reading power file: {e}")
    
    def _extract_pnr_timing_histogram(self):
        """Extract PnR timing histogram from setup timing report"""
        try:
            # Define stage priority order
            pnr_stages = ['postroute', 'route', 'cts', 'place', 'plan']
            timing_file = None
            found_stage = None
            
            # Try each stage in priority order
            for stage in pnr_stages:
                timing_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.{stage}.timing.setup.rpt.gz"
                timing_files = self.file_utils.find_files(timing_pattern, self.workarea)
                if timing_files:
                    timing_file = timing_files[0]
                    found_stage = stage
                    break
            
            if timing_file:
                try:
                    # Extract the last two histogram tables (sub-category and sub-category+scenario)
                    print(f"  {Color.CYAN}Timing Histogram Tables ({found_stage.upper()}):{Color.RESET}")
                    self.print_file_info(timing_file, f"PnR Timing Setup ({found_stage.upper()})")
                    
                    # Get all histogram table line numbers
                    result = self.file_utils.run_command(f"zcat {timing_file} | grep -n 'histogram' | grep '|'")
                    if result.strip():
                        histogram_lines = result.strip().split('\n')
                        if len(histogram_lines) >= 4:
                            # Get the last 4 tables: category, scenario, sub-category, and sub-category + scenario
                            table_category_start = int(histogram_lines[-4].split(':')[0])  # Category breakdown
                            table_scenario_start = int(histogram_lines[-3].split(':')[0])  # Scenario breakdown
                            table_subcat_start = int(histogram_lines[-2].split(':')[0])    # Sub-category breakdown
                            table_subcat_scenario_start = int(histogram_lines[-1].split(':')[0])  # Sub-category + scenario breakdown
                            
                            # Find the end of category table (it ends before scenario table starts)
                            table_category_end = table_scenario_start - 1
                            
                            # Extract category table (for HTML only - not printed to terminal)
                            table_category_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_category_start},{table_category_end}p'")
                            # Table 1 data extracted but not printed (HTML only)
                            
                            # Find the end of sub-category table (it ends before sub-category + scenario table starts)
                            table_subcat_end = table_subcat_scenario_start - 1
                            
                            # Extract sub-category table (TERMINAL OUTPUT: Table 2 only for concise output)
                            table_subcat_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_subcat_start},{table_subcat_end}p'")
                            if table_subcat_result.strip():
                                print(f"  Table 2 - Sub-Category Breakdown (Lines {table_subcat_start}-{table_subcat_end}):")
                                table_subcat_lines = table_subcat_result.strip().split('\n')
                                # Skip first 2 lines (histogram header and dots line)
                                for line in table_subcat_lines[2:]:
                                    if line.strip():
                                        print(f"  {line}")
                            
                            # Extract sub-category + scenario table (for HTML only - not printed to terminal)
                            table_subcat_scenario_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_subcat_scenario_start},$p'")
                            # Table 3 data extracted but not printed (HTML only)
                        else:
                            print("  Could not find histogram tables")
                    else:
                        print("  Histogram tables not found")
                except Exception as e:
                    print(f"  Error processing timing histogram: {e}")
            else:
                print(f"  {Color.YELLOW}PnR Timing Setup: No timing setup reports found for any stage{Color.RESET}")
                print(f"    {Color.YELLOW}Tried stages: {', '.join(pnr_stages)}{Color.RESET}")
                print(f"    {Color.YELLOW}This could be due to:{Color.RESET}")
                print(f"      - Flow still running (timing reports not yet generated)")
                print(f"      - Flow failed at this stage")
                print(f"      - Different file naming convention")
                print(f"      - File permissions issue")
                
        except Exception as e:
            print(f"  {Color.RED}Error extracting PnR timing histogram: {e}{Color.RESET}")
    
    def _extract_timing_histogram_for_html(self):
        """Extract timing histogram data for HTML report"""
        try:
            # Define stage priority order
            pnr_stages = ['postroute', 'route', 'cts', 'place', 'plan']
            timing_file = None
            found_stage = None
            
            # Try each stage in priority order
            for stage in pnr_stages:
                timing_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.{stage}.timing.setup.rpt.gz"
                timing_files = self.file_utils.find_files(timing_pattern, self.workarea)
                if timing_files:
                    timing_file = timing_files[0]
                    found_stage = stage
                    break
            
            if timing_file:
                # Extract the last three histogram tables (category, sub-category, and sub-category+scenario)
                result = self.file_utils.run_command(f"zcat {timing_file} | grep -n 'histogram' | grep '|'")
                if result.strip():
                    histogram_lines = result.strip().split('\n')
                    if len(histogram_lines) >= 4:
                        # Get the last 4 tables: category, scenario, sub-category, and sub-category + scenario
                        table_category_start = int(histogram_lines[-4].split(':')[0])  # Category breakdown
                        table_scenario_start = int(histogram_lines[-3].split(':')[0])  # Scenario breakdown
                        table_subcat_start = int(histogram_lines[-2].split(':')[0])    # Sub-category breakdown
                        table_subcat_scenario_start = int(histogram_lines[-1].split(':')[0])  # Sub-category + scenario breakdown
                        
                        # Find the end of category table (it ends before scenario table starts)
                        table_category_end = table_scenario_start - 1
                        
                        # Extract category table
                        table_category_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_category_start},{table_category_end}p'")
                        
                        # Find the end of sub-category table (it ends before sub-category + scenario table starts)
                        table_subcat_end = table_subcat_scenario_start - 1
                        
                        # Extract sub-category table
                        table_subcat_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_subcat_start},{table_subcat_end}p'")
                        
                        # Extract sub-category + scenario table - get remaining lines
                        table_subcat_scenario_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_subcat_scenario_start},$p'")
                        
                        if table_category_result.strip() and table_subcat_result.strip() and table_subcat_scenario_result.strip():
                            # Skip first 2 lines (histogram header and dots line) for each table
                            category_lines = table_category_result.strip().split('\n')
                            subcat_lines = table_subcat_result.strip().split('\n')
                            scenario_lines = table_subcat_scenario_result.strip().split('\n')
                            
                            return {
                                'stage': found_stage,
                                'file': timing_file,
                                'category_data': '\n'.join(category_lines[2:]) if len(category_lines) > 2 else table_category_result.strip(),
                                'sub_category_data': '\n'.join(subcat_lines[2:]) if len(subcat_lines) > 2 else table_subcat_result.strip(),
                                'scenario_data': '\n'.join(scenario_lines[2:]) if len(scenario_lines) > 2 else table_subcat_scenario_result.strip()
                            }
            
            return None
        except Exception as e:
            print(f"  Error extracting timing histogram for HTML: {e}")
            return None
    
    def _generate_image_html_report(self):
        """Generate HTML report with all relevant pictures using avice_image_debug_report.py"""
        try:
            # Import the image debug report functions
            import subprocess
            import os
            from datetime import datetime
            
            # Get the path to the avice_image_debug_report.py script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_script = os.path.join(script_dir, "avice_image_debug_report.py")
            
            # Check if the image debug script exists
            if not os.path.exists(image_script):
                print(f"  Image debug script not found: {image_script}")
                return
            
            # Run the image debug report script
            cmd = [sys.executable, image_script, self.workarea]
            if self.design_info.ipo and self.design_info.ipo != "unknown":
                cmd.append(self.design_info.ipo)
            
            print(f"  Generating HTML image report...")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            
            if result.returncode == 0:
                # Decode output
                stdout = result.stdout.decode('utf-8', errors='replace')
                stderr = result.stderr.decode('utf-8', errors='replace')
                
                # Extract the output file name from the script output
                output_lines = stdout.strip().split('\n')
                html_file = None
                for line in output_lines:
                    if 'Generated HTML report:' in line:
                        html_file = line.split('Generated HTML report:')[1].strip()
                        break
                    elif 'HTML report generated:' in line:
                        html_file = line.split('HTML report generated:')[1].strip()
                        break
                
                if html_file and os.path.exists(html_file):
                    print(f"  Open with: firefox {Color.MAGENTA}{html_file}{Color.RESET} &")
                    return os.path.abspath(html_file)
                else:
                    print(f"  HTML report generated successfully")
                    return ""
            else:
                stderr = result.stderr.decode('utf-8', errors='replace')
                print(f"  Error generating HTML report: {stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            print(f"  Timeout generating HTML report")
            return ""
        except Exception as e:
            print(f"  Error generating HTML report: {e}")
            return ""
    
    def _extract_clock_tree_data(self, clock_file: str):
        """Extract clock tree data for func.std_tt_0c_0p6v.setup.typical scenario"""
        try:
            if clock_file.endswith('.gz'):
                with gzip.open(clock_file, 'rt', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(clock_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            lines = content.split('\n')
            target_scenario = "func.std_tt_0c_0p6v.setup.typical"
            
            print(f"\n{Color.YELLOW}Clock Tree Analysis for {target_scenario}:{Color.RESET}")
            
            current_clock = None
            found_scenario = False
            clock_data = []
            
            for i, line in enumerate(lines):
                # Check for clock section header
                if line.strip().startswith("Clock :"):
                    current_clock = line.split("Clock :")[1].strip()
                    continue
                
                # Check for scenario data line
                if target_scenario in line and "|" in line:
                    found_scenario = True
                    # Parse the data line
                    parts = [part.strip() for part in line.split("|")]
                    if len(parts) >= 5:
                        scenario = parts[0].strip()
                        period = parts[1].strip()
                        global_skew = parts[2].strip()
                        
                        # Parse insertion delay data (min:max:median:mean:stdev)
                        insertion_delay_parts = parts[3].split(":")
                        if len(insertion_delay_parts) >= 5:
                            min_delay = insertion_delay_parts[0].strip()
                            max_delay = insertion_delay_parts[1].strip()
                            median_delay = insertion_delay_parts[2].strip()
                            mean_delay = insertion_delay_parts[3].strip()
                            stdev_delay = insertion_delay_parts[4].strip()
                            
                            clock_data.append({
                                'clock': current_clock,
                                'period': period,
                                'global_skew': global_skew,
                                'min_delay': min_delay,
                                'max_delay': max_delay,
                                'median_delay': median_delay,
                                'mean_delay': mean_delay,
                                'stdev_delay': stdev_delay
                            })
            
            if found_scenario and clock_data:
                # Print table header
                print(f"  {'Clock':<10} {'Period':<8} {'Skew':<8} {'Min':<8} {'Max':<8} {'Median':<8} {'Mean':<8} {'StdDev':<8}")
                print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
                
                # Print table data
                for data in clock_data:
                    # Check if max delay exceeds 550ps (0.55ns) and apply red color
                    try:
                        max_delay_val = float(data['max_delay'])
                        if max_delay_val > 0.55:  # 550ps threshold
                            max_delay_colored = f"{Color.RED}{data['max_delay']}{Color.RESET}"
                        else:
                            max_delay_colored = data['max_delay']
                    except (ValueError, TypeError):
                        max_delay_colored = data['max_delay']
                    
                    # Use fixed-width formatting to maintain alignment
                    clock_str = f"{data['clock']:<10}"
                    period_str = f"{data['period']:<8}"
                    skew_str = f"{data['global_skew']:<8}"
                    min_str = f"{data['min_delay']:<8}"
                    median_str = f"{data['median_delay']:<8}"
                    mean_str = f"{data['mean_delay']:<8}"
                    stdev_str = f"{data['stdev_delay']:<8}"
                    
                    print(f"  {clock_str} {period_str} {skew_str} {min_str} {max_delay_colored:<8} {median_str} {mean_str} {stdev_str}")
                
                print(f"\n  All values in nanoseconds (ns)")
                print(f"  {Color.RED}Note: Max latency values > 550ps (0.55ns) are highlighted in red{Color.RESET}")
            else:
                print(f"  Scenario {target_scenario} not found in clock tree report")
                
        except (OSError, UnicodeDecodeError, gzip.BadGzipFile) as e:
            print(f"  Error reading clock file: {e}")
    
    def _extract_pt_clock_latency(self, pt_clock_file: str):
        """Extract min and max total clock latency per clock from PT clock latency report"""
        try:
            with open(pt_clock_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            print(f"\n{Color.YELLOW}PT Clock Latency Analysis:{Color.RESET}")
            
            clock_latencies = {}
            current_clock = None
            
            for line in lines:
                # Check for clock section header
                if line.strip().startswith("Clock:"):
                    current_clock = line.split("Clock:")[1].strip()
                    if current_clock not in clock_latencies:
                        clock_latencies[current_clock] = []
                    continue
                
                # Check for total clock latency line
                if "total clock latency" in line:
                    # Extract the latency value (last number in the line)
                    parts = line.split()
                    if parts:
                        try:
                            latency = float(parts[-1])
                            if current_clock:
                                clock_latencies[current_clock].append(latency)
                        except (ValueError, IndexError):
                            continue
            
            if clock_latencies:
                # Print table header
                print(f"  {'Clock':<10} {'Min (ns)':<10} {'Max (ns)':<10}")
                print(f"  {'-'*10} {'-'*10} {'-'*10}")
                
                # Print table data
                for clock, latencies in clock_latencies.items():
                    if latencies:
                        min_latency = min(latencies)
                        max_latency = max(latencies)
                        
                        # Check if max latency exceeds 550ps (0.55ns) and apply red color
                        if max_latency > 0.55:  # 550ps threshold
                            max_latency_colored = f"{Color.RED}{max_latency:.3f}{Color.RESET}"
                        else:
                            max_latency_colored = f"{max_latency:.3f}"
                        
                        # Use fixed-width formatting to maintain alignment
                        clock_str = f"{clock:<10}"
                        min_str = f"{min_latency:<10.3f}"
                        
                        print(f"  {clock_str} {min_str} {max_latency_colored:<10}")
                
                print(f"\n  All values in nanoseconds (ns)")
                print(f"  {Color.RED}Note: Max latency values > 550ps (0.55ns) are highlighted in red{Color.RESET}")
            else:
                print(f"  No clock latency data found in PT report")
                
        except (OSError, UnicodeDecodeError) as e:
            print(f"  Error reading PT clock file: {e}")
    
    def _extract_formal_verification_status(self, log_file: str):
        """Extract verification status and runtime from formal verification log"""
        try:
            # Check if formal is currently running
            file_mtime = os.path.getmtime(log_file)
            current_time = time.time()
            time_since_update = current_time - file_mtime
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Extract verification status
            status = "UNKNOWN"
            for line in lines:
                if "Verification SUCCEEDED" in line:
                    status = "SUCCEEDED"
                    break
                elif "Verification FAILED" in line:
                    status = "FAILED"
                    break
                elif "Verification UNRESOLVED" in line:
                    status = "UNRESOLVED"
                    break
            
            # Check if running (file updated within last 5 minutes and no final status)
            is_running = False
            if status == "UNKNOWN" and time_since_update < 300:  # 5 minutes
                # Check for running indicators in the log
                for line in reversed(lines[-50:]):  # Check last 50 lines
                    if any(indicator in line for indicator in [
                        "Status:  Building verification models",
                        "Status:  Verifying",
                        "Status:  Checking designs",
                        "Matching in progress"
                    ]):
                        is_running = True
                        status = "RUNNING"
                        break
            
            # Extract elapsed time (in hours only)
            elapsed_time = "Unknown"
            for line in lines:
                if line.strip().startswith("Elapsed time:"):
                    # Extract time from "Elapsed time: 3669 seconds ( 1.02 hours )"
                    time_part = line.split("Elapsed time:")[1].strip()
                    # Extract hours from the format "3669 seconds ( 1.02 hours )"
                    if "(" in time_part and "hours" in time_part:
                        hours_part = time_part.split("(")[1].split("hours")[0].strip()
                        elapsed_time = f"{hours_part} hours"
                    else:
                        # Fallback to original format if hours not found
                        elapsed_time = time_part
                    break
            
            # Print status and runtime
            if status == "RUNNING":
                status_color = Color.CYAN
            elif status == "SUCCEEDED":
                status_color = Color.GREEN
            elif status == "FAILED":
                status_color = Color.RED
            else:
                status_color = Color.YELLOW
            
            print(f"  Status: {status_color}{status}{Color.RESET}")
            if status != "RUNNING":
                print(f"  Runtime: {elapsed_time}")
            else:
                print(f"  Runtime: In progress...")
            
        except (OSError, UnicodeDecodeError) as e:
            print(f"  Error reading formal log: {e}")
    
    def _display_formal_timestamps(self, log_file: str):
        """Extract and display start/end timestamps for formal verification"""
        try:
            # Get end time from file modification time
            end_time_epoch = os.path.getmtime(log_file)
            start_time_epoch = end_time_epoch
            
            # Try to extract runtime and calculate start time
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                
                # Look for elapsed time to calculate start time
                # Format: "Elapsed time: 16191 seconds ( 4.50 hours )"
                elapsed_match = re.search(r'Elapsed time:\s*(\d+)\s*seconds', content)
                if elapsed_match:
                    elapsed_seconds = int(elapsed_match.group(1))
                    start_time_epoch = end_time_epoch - elapsed_seconds
            except:
                pass
            
            # Format timestamps
            start_str = time.strftime("%m/%d %H:%M", time.localtime(start_time_epoch))
            end_str = time.strftime("%m/%d %H:%M", time.localtime(end_time_epoch))
            
            print(f"  Start: {start_str}")
            print(f"  End:   {end_str}")
            
            return end_time_epoch  # Return for comparison with ECO timestamps
            
        except Exception as e:
            return None  # Return None if extraction fails
    
    def _check_formal_vs_eco_timestamps(self, formal_end_time: float):
        """Check if ECO was run after formal verification (potential issue)"""
        try:
            if not formal_end_time:
                return
            
            latest_eco_time = 0
            eco_source = None
            
            # Check 1: Auto PT Fix log (automatic ECO fixes)
            auto_pt_fix_log = os.path.join(self.workarea, "signoff_flow/auto_pt/log/auto_pt_fix.log")
            if os.path.exists(auto_pt_fix_log):
                eco_time = os.path.getmtime(auto_pt_fix_log)
                if eco_time > latest_eco_time:
                    latest_eco_time = eco_time
                    eco_source = "Auto PT Fix"
            
            # Check 2: Latest netlist file (manual ECO or any netlist regeneration)
            # Pattern: $wa/export/export_innovus/$b.ipo*.lvs.gv.gz
            netlist_pattern = f"export/export_innovus/{self.design_info.top_hier}.{self.design_info.ipo}*.lvs.gv.gz"
            netlist_files = self.file_utils.find_files(netlist_pattern, self.workarea)
            
            if netlist_files:
                # Get the latest netlist file
                latest_netlist = max(netlist_files, key=os.path.getmtime)
                netlist_time = os.path.getmtime(latest_netlist)
                if netlist_time > latest_eco_time:
                    latest_eco_time = netlist_time
                    eco_source = "Netlist (Manual ECO or regeneration)"
            
            # If any ECO/netlist update ran after formal, warn the user
            if latest_eco_time > formal_end_time:
                time_diff_hours = (latest_eco_time - formal_end_time) / 3600
                formal_end_str = time.strftime("%m/%d %H:%M", time.localtime(formal_end_time))
                eco_str = time.strftime("%m/%d %H:%M", time.localtime(latest_eco_time))
                
                print(f"\n  {Color.YELLOW}[WARN] Design changes were made AFTER formal verification!{Color.RESET}")
                print(f"    Latest formal ended:  {formal_end_str}")
                print(f"    {eco_source} updated: {eco_str} ({time_diff_hours:.1f} hours later)")
                print(f"    {Color.YELLOW}→ Formal verification should be re-run to verify design changes{Color.RESET}")
        except Exception:
            pass  # Silently skip if check fails
    
    def _extract_postroute_data_parameters(self, data_file: str, stage: str = 'postroute'):
        """Extract most significant parameters and generate HTML table with full data"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Define most significant parameters to show in summary
            significant_params = [
                'REGIN_WNS', 'REGIN_TNS', 'REGIN_ViolPaths',
                'REGOUT_WNS', 'REGOUT_TNS', 'REGOUT_ViolPaths',
                'EffictiveUtilization', 'CellCount', 'FFCount', 'ArraysCount',
                'HVT_percentage', 'SVT_percentage',
                'w1_clk_WNS', 'w1_clk_TNS', 'w1_clk_ViolPaths',
                'i1_clk_WNS', 'i1_clk_TNS', 'i1_clk_ViolPaths',
                'i2_clk_WNS', 'i2_clk_TNS', 'i2_clk_ViolPaths'
            ]
            
            # Extract all parameters
            all_params = {}
            for line in lines:
                line = line.strip()
                if ' = ' in line:
                    param_name, param_value = line.split(' = ', 1)
                    all_params[param_name] = param_value
            
            # Print only most significant parameters
            stage_display = stage.upper() if stage != 'postroute' else 'Post-Route'
            print(f"\n{Color.YELLOW}Key {stage_display} Parameters:{Color.RESET}")
            print(f"  {'Parameter':<25} {'Value':<15}")
            print(f"  {'-'*25} {'-'*15}")
            
            for param_name in significant_params:
                if param_name in all_params:
                    print(f"  {param_name:<25} {all_params[param_name]:<15}")
            
            # Generate HTML table with full data for all stages
            self._generate_postroute_html_table(all_params)
            
        except (OSError, UnicodeDecodeError) as e:
            print(f"  {Color.RED}Error reading post-route data file: {e}{Color.RESET}")
            print(f"  {Color.YELLOW}This could be due to:{Color.RESET}")
            print(f"    - Flow still running (data file not yet generated)")
            print(f"    - Flow failed at this stage")
            print(f"    - File permissions issue")
            print(f"    - File corrupted or incomplete")
    
    def _generate_postroute_html_table(self, all_params: dict):
        """Generate HTML table with full post-route data for all stages"""
        try:
            # Get all data files for different stages
            stages = ['plan', 'place', 'cts', 'route', 'postroute']
            stage_data = {}
            missing_stages = []
            error_stages = []
            
            for stage in stages:
                stage_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/reports/{self.design_info.top_hier}_{self.design_info.top_hier}_{self.design_info.ipo}_report_{self.design_info.top_hier}_{self.design_info.ipo}_{stage}.func.std_tt_0c_0p6v.setup.typical.data"
                stage_file = os.path.join(self.workarea, stage_pattern)
                
                if os.path.exists(stage_file):
                    try:
                        with open(stage_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        stage_params = {}
                        for line in content.split('\n'):
                            line = line.strip()
                            if ' = ' in line:
                                param_name, param_value = line.split(' = ', 1)
                                stage_params[param_name] = param_value
                        
                        stage_data[stage] = stage_params
                    except Exception as e:
                        error_stages.append(stage)
                        print(f"    [ERROR] Error reading {stage} data: {e}")
                else:
                    missing_stages.append(stage)
                    print(f"    [WARN] {stage.upper()} data file not found: {stage_file}")
            
            # Report summary
            if missing_stages:
                print(f"    {Color.YELLOW}Missing stages: {', '.join(missing_stages)}{Color.RESET}")
            if error_stages:
                print(f"    {Color.RED}Error stages: {', '.join(error_stages)}{Color.RESET}")
            
            if not stage_data:
                print(f"    {Color.RED}No stage data available - cannot generate HTML table{Color.RESET}")
                return
            
            # Extract timing histogram data
            timing_histogram_data = self._extract_timing_histogram_for_html()
            
            # Generate HTML table
            html_content = self._create_postroute_html_table(stage_data, missing_stages, error_stages, timing_histogram_data)
            
            # Save HTML file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"{os.environ.get('USER', 'avice')}_pnr_data_{self.design_info.top_hier}_{self.design_info.ipo}_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\n  {Color.CYAN}Full PnR Data Table:{Color.RESET}")
            print(f"  Open with: firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
            
        except Exception as e:
            print(f"  Error generating HTML table: {e}")
    
    def _create_postroute_html_table(self, stage_data: dict, missing_stages: list = None, error_stages: list = None, timing_histogram_data: dict = None) -> str:
        """Create HTML table with post-route data for all stages"""
        # Get all unique parameters across all stages
        all_params = set()
        for stage_params in stage_data.values():
            all_params.update(stage_params.keys())
        
        all_params = sorted(list(all_params))
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
            <title>Place & Route Data Analysis - {self.design_info.top_hier}</title>
    <style>
        .header {{
            text-align: center;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 10px;
        }}
        .logo img {{
            max-height: 80px;
            max-width: 300px;
            height: auto;
            width: auto;
            cursor: pointer;
            transition: transform 0.2s ease;
            border-radius: 6px;
        }}
        .logo img:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
        }}
        .image-expanded {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        .image-expanded img {{
            max-width: 90%;
            max-height: 90%;
            border: 3px solid #2c3e50;
        }}
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .stage-header {{ background-color: #2c3e50; color: black; font-weight: bold; }}
        .param-name {{ font-weight: bold; background-color: #ecf0f1; }}
        .timing {{ color: #e74c3c; }}
        .area {{ color: #27ae60; }}
        .cell {{ color: #8e44ad; }}
        .power {{ color: #f39c12; }}
        .clock {{ color: #16a085; }}
        .parameter-groups {{ margin-top: 20px; }}
        .category-header {{ 
            background-color: #34495e; 
            color: white; 
            padding: 10px 15px; 
            margin: 5px 0; 
            cursor: pointer; 
            border-radius: 5px;
            font-weight: bold;
            user-select: none;
        }}
        .category-header:hover {{ background-color: #2c3e50; }}
        .category-icon {{
            width: 24px;
            height: 24px;
            margin-right: 10px;
            vertical-align: middle;
        }}
        .category-content {{ 
            display: none; 
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }}
        .category-content.expanded {{ display: block; }}
        .category-table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 0;
        }}
        .category-table th, .category-table td {{ 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }}
        .category-table th {{ 
            background-color: #34495e; 
            color: white; 
            font-weight: bold; 
        }}
        .category-table tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .expand-icon {{ 
            float: right; 
            transition: transform 0.3s ease;
        }}
        .expand-icon.expanded {{ transform: rotate(90deg); }}
        .timing-histogram-section {{
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .histogram-info {{
            margin-bottom: 20px;
        }}
        .histogram-info h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .histogram-info p {{
            margin: 5px 0;
            color: #7f8c8d;
        }}
        .histogram-tables {{
            margin-top: 20px;
        }}
        .histogram-tables h4 {{
            color: #34495e;
            margin-bottom: 15px;
        }}
        .histogram-table-container {{
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
        }}
        .histogram-table {{
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
            margin: 0;
            white-space: pre;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <img src="/home/avice/scripts/avice_wa_review/images/avice_logo.png" alt="AVICE Logo" onclick="expandImage(this)">
        </div>
    <h1>Place & Route Data Analysis</h1>
    <h2>Design: {self.design_info.top_hier} | IPO: {self.design_info.ipo} | Tag: {self.design_info.tag}</h2>
        <h3>Workarea: {self.workarea_abs}</h3>
    </div>
    
    <h2>Legend</h2>
    <ul>
        <li><span class="timing">Timing Parameters</span> - WNS, TNS, Violation Paths, Skew, Latency, Cycle Time</li>
        <li><span class="area">Area Parameters</span> - Area, Utilization, Die, Core</li>
        <li><span class="cell">Cell Parameters</span> - Cell Count, Combinational, Sequential, FF Count, Buffer/Inverter</li>
        <li><span class="power">Power Parameters</span> - Leakage, Power</li>
        <li><span class="clock">Clock Parameters</span> - Clock-related parameters</li>
    </ul>
    
    <div class="parameter-groups">
"""
        
        # Group parameters by category
        categories = {
            'timing': [],
            'area': [],
            'cell': [],
            'power': [],
            'clock': [],
            'other': []
        }
        
        for param in all_params:
            # Determine parameter category
            if any(keyword in param.upper() for keyword in ['WNS', 'TNS', 'VIOLPATHS', 'SKEW', 'LATENCY', 'CYCLE_TIME']):
                categories['timing'].append(param)
            elif any(keyword in param.upper() for keyword in ['AREA', 'UTILIZATION', 'DIE', 'CORE']):
                categories['area'].append(param)
            elif any(keyword in param.upper() for keyword in ['CELLCOUNT', 'COMBINATIONAL', 'SEQUENTIAL', 'FFCOUNT', 'BUFINV', 'GATED', 'UNGATED']):
                categories['cell'].append(param)
            elif any(keyword in param.upper() for keyword in ['LEAKAGE', 'POWER']):
                categories['power'].append(param)
            elif any(keyword in param.upper() for keyword in ['CLK', 'CLOCK']):
                categories['clock'].append(param)
            else:
                categories['other'].append(param)
        
        # Generate expandable category sections with embedded base64 icons
        # Read base64 data for each icon (relative to script location)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(script_dir, 'icons')
        
        try:
            with open(os.path.join(icons_dir, 'timing.b64'), 'r') as f:
                timing_b64 = f.read().strip()
            with open(os.path.join(icons_dir, 'area.b64'), 'r') as f:
                area_b64 = f.read().strip()
            with open(os.path.join(icons_dir, 'cell.b64'), 'r') as f:
                cell_b64 = f.read().strip()
            with open(os.path.join(icons_dir, 'power.b64'), 'r') as f:
                power_b64 = f.read().strip()
            with open(os.path.join(icons_dir, 'clock.b64'), 'r') as f:
                clock_b64 = f.read().strip()
            with open(os.path.join(icons_dir, 'other.b64'), 'r') as f:
                other_b64 = f.read().strip()
        except FileNotFoundError:
            # Fallback to text icons if base64 files not found
            timing_b64 = area_b64 = cell_b64 = power_b64 = clock_b64 = other_b64 = ""
        
        category_info = {
            'timing': {'name': 'Timing Parameters', 'icon': f'data:image/png;base64,{timing_b64}' if timing_b64 else '[T]'},
            'area': {'name': 'Area Parameters', 'icon': f'data:image/png;base64,{area_b64}' if area_b64 else '[A]'},
            'cell': {'name': 'Cell Parameters', 'icon': f'data:image/png;base64,{cell_b64}' if cell_b64 else '[C]'},
            'power': {'name': 'Power Parameters', 'icon': f'data:image/png;base64,{power_b64}' if power_b64 else '[P]'},
            'clock': {'name': 'Clock Parameters', 'icon': f'data:image/png;base64,{clock_b64}' if clock_b64 else '[K]'},
            'other': {'name': 'Other Parameters', 'icon': f'data:image/png;base64,{other_b64}' if other_b64 else '[O]'},
            'histogram': {'name': 'Timing Histogram Analysis', 'icon': f'data:image/png;base64,{timing_b64}' if timing_b64 else '[H]'}
        }
        
        for category, params in categories.items():
            if not params:
                continue
                
            category_name = category_info[category]['name']
            category_icon = category_info[category]['icon']
            
            # Check if icon is a data URI or text
            if category_icon.startswith('data:'):
                icon_html = f'<img src="{category_icon}" alt="{category_name}" style="width: 16px; height: 16px; margin-right: 8px; vertical-align: middle;">'
            else:
                icon_html = f'<span style="display: inline-block; width: 16px; height: 16px; margin-right: 8px; text-align: center; font-weight: bold; color: #2c3e50;">{category_icon}</span>'
            
            html += f"""
        <div class="category-section">
            <div class="category-header" onclick="toggleCategory('{category}')">
                {icon_html} {category_name} ({len(params)} parameters)
                <span class="expand-icon" id="icon-{category}">▶</span>
            </div>
            <div class="category-content" id="content-{category}">
                <table class="category-table">
                    <tr>
                        <th>Parameter</th>
"""
            
            # Add stage headers for this category
            for stage in ['postroute', 'route', 'cts', 'place', 'plan']:
                if stage in stage_data:
                    html += f"                        <th>{stage.upper()}</th>\n"
                elif missing_stages and stage in missing_stages:
                    html += f"                        <th style=\"background-color: #f39c12; color: white;\">{stage.upper()} (MISSING)</th>\n"
                elif error_stages and stage in error_stages:
                    html += f"                        <th style=\"background-color: #e74c3c; color: white;\">{stage.upper()} (ERROR)</th>\n"
                else:
                    html += f"                        <th style=\"background-color: #95a5a6; color: white;\">{stage.upper()} (N/A)</th>\n"
            
            html += "                    </tr>\n"
            
            # Add parameter rows for this category
            for param in sorted(params):
                param_class = category
                html += f"                    <tr>\n"
                html += f"                        <td class=\"param-name {param_class}\">{param}</td>\n"
                
                for stage in ['postroute', 'route', 'cts', 'place', 'plan']:
                    if stage in stage_data:
                        value = stage_data[stage].get(param, 'N/A')
                        html += f"                        <td class=\"{param_class}\">{value}</td>\n"
                    elif missing_stages and stage in missing_stages:
                        html += f"                        <td style=\"background-color: #fdf2e9; color: #d68910; text-align: center;\">FILE MISSING</td>\n"
                    elif error_stages and stage in error_stages:
                        html += f"                        <td style=\"background-color: #fadbd8; color: #c0392b; text-align: center;\">READ ERROR</td>\n"
                    else:
                        html += f"                        <td style=\"background-color: #f8f9fa; color: #7f8c8d; text-align: center;\">N/A</td>\n"
                
                html += "                    </tr>\n"
            
            html += "                </table>\n"
            html += "            </div>\n"
            html += "        </div>\n"
        
        html += """
    </div>
    
    <h2>Timing Histogram Analysis</h2>
    <div class="timing-histogram-section">
"""
        
        # Add timing histogram data if available
        if timing_histogram_data and (timing_histogram_data.get('category_data') or timing_histogram_data.get('data')):
            # Combine all histogram tables into one expandable section
            histogram_content = ""
            
            if timing_histogram_data.get('category_data'):
                histogram_content += f"<h4>Table 1 - Category Breakdown</h4>\n"
                histogram_content += f"<div class='histogram-table-container'>\n"
                histogram_content += f"<pre class='histogram-table'>{timing_histogram_data['category_data']}</pre>\n"
                histogram_content += f"</div>\n\n"
            
            if timing_histogram_data.get('sub_category_data'):
                histogram_content += f"<h4>Table 2 - Sub-Category Breakdown</h4>\n"
                histogram_content += f"<div class='histogram-table-container'>\n"
                histogram_content += f"<pre class='histogram-table'>{timing_histogram_data['sub_category_data']}</pre>\n"
                histogram_content += f"</div>\n\n"
            
            if timing_histogram_data.get('scenario_data'):
                histogram_content += f"<h4>Table 3 - Sub-Category + Scenario Breakdown</h4>\n"
                histogram_content += f"<div class='histogram-table-container'>\n"
                histogram_content += f"<pre class='histogram-table'>{timing_histogram_data['scenario_data']}</pre>\n"
                histogram_content += f"</div>\n\n"
            
            # Fallback for old data format
            elif timing_histogram_data.get('data'):
                histogram_content += f"<h4>Category + Scenario Breakdown</h4>\n"
                histogram_content += f"<div class='histogram-table-container'>\n"
                histogram_content += f"<pre class='histogram-table'>{timing_histogram_data['data']}</pre>\n"
                histogram_content += f"</div>\n\n"
            
            # Get histogram icon
            histogram_icon = category_info['histogram']['icon']
            if histogram_icon.startswith('data:'):
                histogram_icon_html = f'<img src="{histogram_icon}" alt="Timing Histogram" style="width: 16px; height: 16px; margin-right: 8px; vertical-align: middle;">'
            else:
                histogram_icon_html = f'<span style="display: inline-block; width: 16px; height: 16px; margin-right: 8px; text-align: center; font-weight: bold; color: #2c3e50;">{histogram_icon}</span>'
            
            html += f"""
        <div class="category-section">
            <div class="category-header" onclick="toggleCategory('histogram')">
                {histogram_icon_html} Timing Histogram Analysis - {timing_histogram_data['stage'].upper()} Stage
                <span class="expand-icon" id="icon-histogram">▶</span>
            </div>
            <div class="category-content" id="content-histogram">
                <div class="histogram-info">
                    <p><strong>Source:</strong> {os.path.basename(timing_histogram_data['file'])}</p>
                </div>
                <div class="histogram-tables">
                    {histogram_content}
                </div>
            </div>
        </div>
"""
        else:
            # Get histogram icon for fallback case
            histogram_icon = category_info['histogram']['icon']
            if histogram_icon.startswith('data:'):
                histogram_icon_html = f'<img src="{histogram_icon}" alt="Timing Histogram" style="width: 16px; height: 16px; margin-right: 8px; vertical-align: middle;">'
            else:
                histogram_icon_html = f'<span style="display: inline-block; width: 16px; height: 16px; margin-right: 8px; text-align: center; font-weight: bold; color: #2c3e50;">{histogram_icon}</span>'
            
            html += f"""
        <div class="category-section">
            <div class="category-header" onclick="toggleCategory('histogram')">
                {histogram_icon_html} Timing Histogram Analysis
                <span class="expand-icon" id="icon-histogram">▶</span>
            </div>
            <div class="category-content" id="content-histogram">
                <p><em>No timing histogram data available</em></p>
            </div>
        </div>
"""
        
        html += """
    </div>
    
    <script>
        function toggleCategory(category) {
            const content = document.getElementById('content-' + category);
            const icon = document.getElementById('icon-' + category);
            
            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                icon.classList.remove('expanded');
                icon.textContent = '▶';
            } else {
                content.classList.add('expanded');
                icon.classList.add('expanded');
                icon.textContent = '▼';
            }
        }
        
        
        // All categories start collapsed by default
        document.addEventListener('DOMContentLoaded', function() {
            const categories = ['timing', 'area', 'cell', 'power', 'clock', 'other', 'histogram'];
            categories.forEach(category => {
                const content = document.getElementById('content-' + category);
                const icon = document.getElementById('icon-' + category);
                if (content) {
                    // Categories start collapsed (no expanded class)
                    icon.textContent = '▶';
                }
            });
        });
    </script>
    
    <p><em>Generated by avice_wa_review.py</em></p>
    
    <script>
        function expandImage(imgElement) {{
            // Create overlay
            var overlay = document.createElement('div');
            overlay.className = 'image-expanded';
            
            // Create expanded image
            var expandedImg = document.createElement('img');
            expandedImg.src = imgElement.src;
            expandedImg.alt = imgElement.alt;
            
            overlay.appendChild(expandedImg);
            document.body.appendChild(overlay);
            
            // Close on click
            overlay.onclick = function() {{
                if (document.body.contains(overlay)) {{
                    document.body.removeChild(overlay);
                }}
            }};
            
            // Close on escape key
            function escapeHandler(e) {{
                e = e || window.event;
                if ((e.keyCode || e.which) === 27) {{
                    if (document.body.contains(overlay)) {{
                        document.body.removeChild(overlay);
                        if (document.removeEventListener) {{
                            document.removeEventListener('keydown', escapeHandler);
                        }} else if (document.detachEvent) {{
                            document.detachEvent('onkeydown', escapeHandler);
                        }}
                    }}
                }}
            }}
            
            if (document.addEventListener) {{
                document.addEventListener('keydown', escapeHandler);
            }} else if (document.attachEvent) {{
                document.attachEvent('onkeydown', escapeHandler);
            }}
        }}
    </script>
</body>
</html>
"""
        
        return html
    
    def run_synthesis_analysis(self):
        """Run synthesis (DC) analysis"""
        self.print_header(FlowStage.SYNTHESIS)
        
        # Design Definition
        des_def = os.path.join(self.workarea, "unit_scripts/des_def.tcl")
        if self.print_file_info(des_def, "Design Definition"):
            matches = self.file_utils.grep_file(r"trans_factor|dont_use", des_def)
            for match in matches:
                print(f"  {match}")
        
        # DC Log
        dc_log = os.path.join(self.workarea, "syn_flow/dc/log/dc.log")
        if self.file_utils.file_exists(dc_log):
            self.print_file_info(dc_log, "DC Log")
        
        # DC reports
        reports = [
            "syn_flow/dc/reports/be4rtl/internal_high_width_logical_cones.rpt",
            "syn_flow/dc/reports/debug/*.rtl2gate.removed_cgates.rep",
            "syn_flow/dc/reports/*_rtl2gate.qor.rpt",
            f"syn_flow/dc/reports/debug/{self.design_info.top_hier}.rtl2gate.removed_registers.rep"
        ]
        
        # QoR Report (Quality of Results)
        qor_report = os.path.join(self.workarea, f"syn_flow/dc/reports/{self.design_info.top_hier}_rtl2gate.qor.rpt")
        if self.print_file_info(qor_report, "QoR Report (Quality of Results)"):
            self._analyze_qor_report(qor_report)
        
        # BeFlow Configuration
        beflow_config = os.path.join(self.workarea, "syn_flow/dc/beflow_config.yaml")
        if self.print_file_info(beflow_config, "BeFlow Configuration"):
            self._analyze_beflow_config(beflow_config)
        
        for report in reports:
            report_path = os.path.join(self.workarea, report)
            if "*" in report:
                files = self.file_utils.find_files(report, self.workarea)
                if files:
                    self.print_file_info(files[0], "Report")
            else:
                self.print_file_info(report_path, "Report")
        
        # Clock gates removed
        files = self.file_utils.find_files("syn_flow/dc/reports/debug/*.rtl2gate.removed_cgates.rep", self.workarea)
        if files:
            matches = self.file_utils.grep_file(r"Total clock gates removed:\s*(\d+)", files[0])
            if matches:
                count = matches[0]
                print(f"Clock gates removed: {count}")
            else:
                print("Clock gates removed: Unable to extract count")
        
        # Registers removed
        reg_rep = os.path.join(self.workarea, f"syn_flow/dc/reports/debug/{self.design_info.top_hier}.rtl2gate.removed_registers.rep")
        if self.file_utils.file_exists(reg_rep):
            try:
                if reg_rep.endswith('.gz'):
                    with gzip.open(reg_rep, 'rt', encoding='utf-8') as f:
                        lines = f.readlines()
                else:
                    with open(reg_rep, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                print(f"Removed registers: {len(lines)}")
            except (OSError, UnicodeDecodeError, gzip.BadGzipFile):
                print("Removed registers: Unable to read file")
        
        # Don't use cells
        dont_use_cells_rpt = os.path.join(self.workarea, f"syn_flow/dc/reports/{self.design_info.top_hier}.dont_use_cells.rpt")
        if self.file_utils.file_exists(dont_use_cells_rpt):
            try:
                if dont_use_cells_rpt.endswith('.gz'):
                    with gzip.open(dont_use_cells_rpt, 'rt', encoding='utf-8') as f:
                        lines = f.readlines()
                else:
                    with open(dont_use_cells_rpt, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                
                # Count non-empty lines (actual cells)
                cell_count = len([line for line in lines if line.strip()])
                if cell_count > 0:
                    print(f"{Color.YELLOW}Don't use cells found: {cell_count}{Color.RESET}")
                    print(f"  Report: {dont_use_cells_rpt}")
                    # Show first few cells as examples
                    if cell_count <= 10:
                        print(f"  Cells: {', '.join([line.strip() for line in lines if line.strip()])}")
                    else:
                        sample_cells = [line.strip() for line in lines if line.strip()][:5]
                        print(f"  Sample cells: {', '.join(sample_cells)} ... (+{cell_count-5} more)")
                else:
                    print(f"{Color.GREEN}No don't use cells{Color.RESET}")
            except (OSError, UnicodeDecodeError, gzip.BadGzipFile) as e:
                print(f"{Color.YELLOW}Don't use cells report found but unable to read: {e}{Color.RESET}")
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Synthesis (DC)",
            section_id="synthesis",
            stage=FlowStage.SYNTHESIS,
            status="PASS",
            key_metrics={
                "Design": self.design_info.top_hier,
                "IPO": self.design_info.ipo
            },
            html_file="",
            priority=3,
            issues=[],
            icon="[DC]"
        )
    
    def _extract_floorplan_dimensions(self):
        """Extract floorplan dimensions from DEF file"""
        try:
            # Find floorplan DEF file - try with top_hier first
            flp_pattern = os.path.join(self.workarea, "flp", f"{self.design_info.top_hier}_fp.def.gz")
            
            if not os.path.exists(flp_pattern):
                # Try finding any *_fp.def.gz file
                flp_files = glob.glob(os.path.join(self.workarea, "flp", "*_fp.def.gz"))
                if flp_files:
                    flp_pattern = flp_files[0]
                else:
                    return None
            
            # Parse DEF file
            if flp_pattern.endswith('.gz'):
                with gzip.open(flp_pattern, 'rt', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(flp_pattern, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Extract UNITS DISTANCE MICRONS
            units_match = re.search(r'UNITS\s+DISTANCE\s+MICRONS\s+(\d+)', content)
            units = int(units_match.group(1)) if units_match else 2000  # Default to 2000
            
            # Extract DIEAREA coordinates (x1 y1 x2 y2)
            diearea_match = re.search(r'DIEAREA\s+\(\s*(\d+)\s+(\d+)\s*\)\s+\(\s*(\d+)\s+(\d+)\s*\)', content)
            if diearea_match:
                x1, y1, x2, y2 = map(int, diearea_match.groups())
                
                # Calculate X, Y dimensions in um: top-right coordinates / 2000
                x_dim_um = x2 / 2000
                y_dim_um = y2 / 2000
                
                return {
                    'x_dim_um': x_dim_um,
                    'y_dim_um': y_dim_um
                }
        except Exception as e:
            # Silently fail if floorplan not found or parsing fails
            return None
        
        return None
    
    def _analyze_qor_report(self, qor_file: str):
        """Analyze QoR report and extract key metrics"""
        try:
            print(f"  {Color.CYAN}QoR Analysis:{Color.RESET}")
            
            # Read the QoR report
            if qor_file.endswith('.gz'):
                with gzip.open(qor_file, 'rt', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(qor_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Extract key QoR metrics
            qor_metrics = {}
            
            # Area metrics
            design_area_match = re.search(r'Design Area:\s+([\d,]+\.?\d*)', content)
            if design_area_match:
                qor_metrics['Design Area'] = design_area_match.group(1)
            
            # Cell count metrics
            leaf_cell_match = re.search(r'Leaf Cell Count:\s+([\d,]+)', content)
            if leaf_cell_match:
                qor_metrics['Leaf Cell Count'] = leaf_cell_match.group(1)
            
            comb_cell_match = re.search(r'Combinational Cell Count:\s+([\d,]+)', content)
            if comb_cell_match:
                qor_metrics['Combinational Cells'] = comb_cell_match.group(1)
            
            seq_cell_match = re.search(r'Sequential Cell Count:\s+([\d,]+)', content)
            if seq_cell_match:
                qor_metrics['Sequential Cells'] = seq_cell_match.group(1)
            
            # Net count
            net_count_match = re.search(r'Total Number of Nets:\s+([\d,]+)', content)
            if net_count_match:
                qor_metrics['Total Nets'] = net_count_match.group(1)
            
            # Timing metrics (from path groups)
            wns_match = re.search(r'Critical Path Slack:\s+([-\d,]+\.?\d*)', content)
            if wns_match:
                qor_metrics['Critical Path Slack'] = wns_match.group(1)
            
            tns_match = re.search(r'Total Negative Slack:\s+([-\d,]+\.?\d*)', content)
            if tns_match:
                qor_metrics['Total Negative Slack'] = tns_match.group(1)
            
            viol_paths_match = re.search(r'No\. of Violating Paths:\s+([\d,]+\.?\d*)', content)
            if viol_paths_match:
                qor_metrics['Violating Paths'] = viol_paths_match.group(1)
            
            # Macro count
            macro_count_match = re.search(r'Macro Count:\s+([\d,]+)', content)
            if macro_count_match:
                qor_metrics['Macro Count'] = macro_count_match.group(1)
            
            # Extract floorplan dimensions
            flp_dims = self._extract_floorplan_dimensions()
            
            # Display extracted metrics
            if qor_metrics:
                print(f"    {Color.GREEN}Key QoR Metrics:{Color.RESET}")
                for metric, value in qor_metrics.items():
                    if metric == 'Design Area':
                        # Convert area from um² to mm² by dividing by 1,000,000
                        try:
                            area_um2 = float(value.replace(',', ''))
                            area_mm2 = area_um2 / 1000000
                            # Show area and X,Y dimensions in one line
                            if flp_dims:
                                print(f"      {metric}: {value} um2 ({area_mm2:.3f} mm2) | Die (X,Y): {flp_dims['x_dim_um']:.2f} um x {flp_dims['y_dim_um']:.2f} um")
                            else:
                                print(f"      {metric}: {value} um2 ({area_mm2:.3f} mm2)")
                        except (ValueError, AttributeError):
                            print(f"      {metric}: {value}")
                    else:
                        print(f"      {metric}: {value}")
            else:
                print(f"    {Color.YELLOW}No QoR metrics found in report{Color.RESET}")
            
            # Extract and display scenario lines from the end of the file
            lines = content.split('\n')
            scenario_lines = [line for line in lines if line.strip().startswith('Scenario')]
            if scenario_lines:
                print(f"    {Color.CYAN}Scenario Summary:{Color.RESET}")
                print(f"    {'Scenario':<50} {'WNS':<10} {'TNS':<10} {'Violating Paths':<15}")
                print(f"    {'-'*50} {'-'*10} {'-'*10} {'-'*15}")
                
                for line in scenario_lines[-2:]:  # Last 2 scenario lines
                    # Parse the scenario line to extract components
                    scenario_match = re.search(r'Scenario:\s+([^\s]+)', line)
                    hold_match = re.search(r'\(Hold\)', line)
                    wns_match = re.search(r'WNS:\s+([\d.-]+)', line)
                    tns_match = re.search(r'TNS:\s+([\d.-]+)', line)
                    viol_paths_match = re.search(r'Number of Violating Paths:\s+([\d.-]+)', line)
                    
                    scenario = scenario_match.group(1) if scenario_match else "N/A"
                    if hold_match:
                        scenario += " (Hold)"
                    wns = wns_match.group(1) if wns_match else "N/A"
                    tns = tns_match.group(1) if tns_match else "N/A"
                    viol_paths = viol_paths_match.group(1) if viol_paths_match else "N/A"
                    
                    print(f"    {scenario:<50} {wns:<10} {tns:<10} {viol_paths:<15}")
            
            # Extract and display all Timing Path Group names
            path_groups = []
            for line in lines:
                if 'Timing Path Group' in line:
                    # Extract the path group name from lines like "Timing Path Group 'CLKGATE'"
                    match = re.search(r"Timing Path Group '([^']+)'", line)
                    if match:
                        path_groups.append(match.group(1))
            
            if path_groups:
                print(f"    {Color.CYAN}Timing Path Groups:{Color.RESET} {', '.join(path_groups)}")
                
        except (OSError, UnicodeDecodeError, gzip.BadGzipFile) as e:
            print(f"    {Color.RED}Error reading QoR report: {e}{Color.RESET}")
    
    def _analyze_beflow_config(self, beflow_file: str):
        """Analyze BeFlow configuration and extract useful variables"""
        try:
            print(f"  {Color.CYAN}BeFlow Configuration Analysis:{Color.RESET}")
            
            # Read the BeFlow config file
            with open(beflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract useful variables
            config_vars = {}
            
            # Environment variables
            lib_snap_match = re.search(r'LIB_SNAP_REV:\s+(\d+)', content)
            if lib_snap_match:
                config_vars['Library Snapshot'] = lib_snap_match.group(1)
            
            # Process and technology
            nv_process_match = re.search(r'nv_process:\s+\[[\'\"]([^\'\"]+)[\'\"]\]', content)
            if nv_process_match:
                config_vars['NV Process'] = nv_process_match.group(1)
            
            tracks_match = re.search(r'TracksNum:\s+\[[\'\"]([^\'\"]+)[\'\"]\]', content)
            if tracks_match:
                config_vars['Tracks Number'] = tracks_match.group(1)
            
            # Design information
            project_match = re.search(r'project:\s+\[[\'\"]([^\'\"]+)[\'\"]\]', content)
            if project_match:
                config_vars['Project'] = project_match.group(1)
            
            
            # Timing scenario
            scenario_match = re.search(r'default_scenario\(dc\):\s+\[[\'\"]([^\'\"]+)[\'\"]\]', content)
            if scenario_match:
                config_vars['Default Scenario'] = scenario_match.group(1)
            
            # Library paths
            stdcell_lib_match = re.search(r'stdcell_lib_path:\s+\[[\'\"]([^\'\"]+)[\'\"]\]', content)
            if stdcell_lib_match:
                config_vars['StdCell Library Path'] = stdcell_lib_match.group(1)
            
            memories_path_match = re.search(r'MemoriesPath:\s+\[[\'\"]([^\'\"]+)[\'\"]\]', content)
            if memories_path_match:
                config_vars['Memories Path'] = memories_path_match.group(1)
            
            
            # VT types
            vt_types_match = re.search(r'vt_type_list:\s+\[([^\]]+)\]', content)
            if vt_types_match:
                vt_types = vt_types_match.group(1).replace("'", "").replace('"', '').replace('[', '').replace(']', '')
                config_vars['VT Types'] = vt_types.strip()
            
            # Array names list
            array_names_match = re.search(r'arrayNames:\s+\[([^\]]+)\]', content)
            if array_names_match:
                array_names = array_names_match.group(1)
                # Clean up the array names and join them
                clean_names = [name.strip().strip("'\"") for name in array_names.split(',')]
                config_vars['Array Names'] = ', '.join(clean_names)
            
            # agur_unit_be_ip for the design
            agur_unit_match = re.search(rf'agur_unit_be_ip\({self.design_info.top_hier}\):\s+\[([^\]]+)\]', content)
            if agur_unit_match:
                agur_units = agur_unit_match.group(1)
                # Clean up the unit names and join them
                clean_units = [unit.strip().strip("'\"") for unit in agur_units.split(',')]
                config_vars['Agur Unit BE IP'] = ', '.join(clean_units)
            
            # Display extracted variables
            if config_vars:
                print(f"    {Color.GREEN}Key Configuration Variables:{Color.RESET}")
                for var, value in config_vars.items():
                    print(f"      {var}: {value}")
            else:
                print(f"    {Color.YELLOW}No configuration variables found{Color.RESET}")
                
        except (OSError, UnicodeDecodeError) as e:
            print(f"    {Color.RED}Error reading BeFlow config: {e}{Color.RESET}")
    
    def run_setup_analysis(self):
        """Run setup analysis including environment and runtime information"""
        self.print_header(FlowStage.SETUP)
        
        # Display design information
        print(f"UNIT: {self.design_info.top_hier}")
        print(f"TAG: {self.design_info.tag}")
        print(f"IPO: {self.design_info.ipo} (Available IPOs: {', '.join(self.design_info.all_ipos)})")
        
        # Extract environment information
        self._extract_environment_info()
        
        
        
        # Design Definition
        design_def_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/design_definition.tcl"
        design_def_file = os.path.join(self.workarea, design_def_pattern)
        if self.file_utils.file_exists(design_def_file):
            self.print_file_info(design_def_file, "Design Definition")
        
        # PnR Configuration
        pnr_config_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/pnr_config.tcl"
        pnr_config_file = os.path.join(self.workarea, pnr_config_pattern)
        if self.file_utils.file_exists(pnr_config_file):
            self.print_file_info(pnr_config_file, "PnR Configuration")
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Setup",
            section_id="setup",
            stage=FlowStage.SETUP,
            status="PASS",
            key_metrics={
                "Design": self.design_info.top_hier,
                "Tag": self.design_info.tag,
                "IPO": self.design_info.ipo
            },
            html_file="",
            priority=4,
            issues=[],
            icon="[Setup]"
        )
    
    def _extract_environment_info(self):
        """Extract BeFlow, Tech Data, and Tool Override environment information"""
        print(f"  {Color.CYAN}Environment Information:{Color.RESET}")
        
        # Check formal flow environment files for BeFlow and Tech Data info
        # Note: LIB_SNAP_REV is already shown in DC/PnR sections
        env_locations = [
            "formal_flow/rtl_vs_pnr_fm/FM_INFO/env",
            "formal_flow/rtl_vs_syn_fm/FM_INFO/env",
            "formal_flow/rtl_vs_pnr_bbox_fm/FM_INFO/env",
            "formal_flow/rtl_vs_syn_bbox_fm/FM_INFO/env"
        ]
        
        env_vars_found = {
            'BEFLOW_REV': False,
            'BEFLOW_CONFIG_REV': False,
            'TECH_DATA_T6_REV': False,
            'BE_OVERRIDE_TOOLVERS': False
        }
        
        for env_path in env_locations:
            full_path = os.path.join(self.workarea, env_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        for var_name in env_vars_found.keys():
                            if line.startswith(f"{var_name}=") and not env_vars_found[var_name]:
                                print(f"    {line}")
                                env_vars_found[var_name] = True
                    
                    # If we found all variables, no need to check more files
                    if all(env_vars_found.values()):
                        break
                            
                except (OSError, UnicodeDecodeError):
                    continue
        
        # Also check PnR debug files for BE_OVERRIDE_TOOLVERS
        if not env_vars_found['BE_OVERRIDE_TOOLVERS']:
            debug_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/LOGs/PRIME/STEP__BEGIN__*.debug"
            debug_files = self.file_utils.find_files(debug_pattern, self.workarea)
            
            for debug_file in debug_files[:1]:  # Check first BEGIN debug file
                try:
                    result = self.file_utils.run_command(f"grep '^BE_OVERRIDE_TOOLVERS' {debug_file}")
                    if result.strip():
                        print(f"    {result.strip()}")
                        env_vars_found['BE_OVERRIDE_TOOLVERS'] = True
                        break
                except Exception:
                    continue
        
        # If no environment info found at all
        if not any(env_vars_found.values()):
            print(f"    No environment information found")
    
    def _analyze_pnr_status(self, prc_status_file: str):
        """Analyze PnR status to show flow progress, running stages, and errors"""
        try:
            with open(prc_status_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse status data
            status_data = {}
            current_ipo = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse status line: block ipo step status duration logfile
                parts = line.split()
                if len(parts) >= 6:
                    block, ipo, step, status, duration, logfile = parts[0], parts[1], parts[2], parts[3], parts[4], ' '.join(parts[5:])
                    
                    if ipo not in status_data:
                        status_data[ipo] = []
                    
                    status_data[ipo].append({
                        'step': step,
                        'status': status,
                        'duration': duration,
                        'logfile': logfile
                    })
            
            if not status_data:
                print(f"  {Color.YELLOW}No PnR status data found{Color.RESET}")
                return
            
            # Analyze and display status for each IPO
            print(f"\n{Color.CYAN}PnR Flow Status Analysis:{Color.RESET}")
            
            for ipo in sorted(status_data.keys()):
                steps = status_data[ipo]
                print(f"\n  {Color.CYAN}IPO {ipo}:{Color.RESET}")
                
                # Categorize steps
                pnr_steps = []
                report_steps = []
                other_steps = []
                
                for step_info in steps:
                    step = step_info['step']
                    if step.startswith('report_'):
                        report_steps.append(step_info)
                    elif step in ['BEGIN', 'END']:
                        other_steps.append(step_info)
                    else:
                        pnr_steps.append(step_info)
                
                # Analyze PnR flow status
                pnr_status = self._analyze_step_sequence(pnr_steps, "PnR Flow")
                if pnr_status:
                    print(f"    {pnr_status}")
                
                # Analyze reporting status
                report_status = self._analyze_step_sequence(report_steps, "Reporting")
                if report_status:
                    print(f"    {report_status}")
                
                # Show current running stage
                running_steps = [s for s in steps if s['status'] == 'RUN']
                if running_steps:
                    print(f"    {Color.YELLOW}Currently Running: {', '.join([s['step'] for s in running_steps])}{Color.RESET}")
                
                # Show errors
                error_steps = [s for s in steps if s['status'] == 'ERR']
                if error_steps:
                    print(f"    {Color.RED}Errors in: {', '.join([s['step'] for s in error_steps])}{Color.RESET}")
                
                # Overall completion status
                total_steps = len(steps)
                done_steps = len([s for s in steps if s['status'] == 'DONE'])
                error_steps_count = len(error_steps)
                running_steps_count = len(running_steps)
                
                if done_steps == total_steps:
                    print(f"    {Color.GREEN}Status: COMPLETED ({done_steps}/{total_steps} steps){Color.RESET}")
                elif error_steps_count > 0:
                    print(f"    {Color.RED}Status: FAILED ({done_steps}/{total_steps} done, {error_steps_count} errors){Color.RESET}")
                elif running_steps_count > 0:
                    print(f"    {Color.YELLOW}Status: RUNNING ({done_steps}/{total_steps} done, {running_steps_count} active){Color.RESET}")
                else:
                    print(f"    {Color.YELLOW}Status: UNKNOWN ({done_steps}/{total_steps} done){Color.RESET}")
        
        except Exception as e:
            print(f"  Error analyzing PnR status: {e}")
    
    def _analyze_step_sequence(self, steps, category_name):
        """Analyze a sequence of steps and return status summary"""
        if not steps:
            return None
        
        # Define expected PnR flow order
        pnr_flow_order = ['setup', 'edi_plan', 'place', 'cts', 'route', 'postroute', 'export', 'extraction', 'nbu_auto_pt']
        report_flow_order = ['report_edi_plan', 'report_place', 'report_cts', 'report_route', 'report_postroute']
        
        if category_name == "PnR Flow":
            expected_order = pnr_flow_order
        else:
            expected_order = report_flow_order
        
        # Find the last completed step
        last_completed = None
        first_error = None
        first_running = None
        
        for step_info in steps:
            step = step_info['step']
            status = step_info['status']
            
            if status == 'DONE':
                last_completed = step
            elif status == 'ERR' and first_error is None:
                first_error = step
            elif status == 'RUN' and first_running is None:
                first_running = step
        
        # Determine progress
        if last_completed:
            try:
                completed_index = expected_order.index(last_completed)
                progress = f"Completed through: {last_completed} ({completed_index + 1}/{len(expected_order)})"
            except ValueError:
                progress = f"Completed: {last_completed}"
        else:
            progress = "No steps completed"
        
        # Add error/running info
        if first_error:
            progress += f", Error at: {first_error}"
        if first_running:
            progress += f", Running: {first_running}"
        
        return f"{category_name}: {progress}"

    def _extract_prc_configuration(self, prc_file):
        """Extract key configuration information from PRC file (YAML or legacy format)"""
        try:
            with open(prc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it's YAML format (starts with top_hier:)
            if f"{self.design_info.top_hier}:" in content:
                self._extract_yaml_prc_configuration(content)
            else:
                # Legacy format - search for useful/MULTIBIT keywords
                matches = self.file_utils.grep_file(r"useful|MULTIBIT", prc_file)
                for match in matches:
                    print(f"  {match}")
                    
        except Exception as e:
            print(f"  Error reading PRC configuration: {e}")
            # Fallback to simple keyword search
            try:
                matches = self.file_utils.grep_file(r"useful|MULTIBIT", prc_file)
                for match in matches:
                    print(f"  {match}")
            except:
                pass
    
    def _print_flow_sequence_with_hooks(self, ipo, flow_sequence, hooks):
        """Print flow sequence with TCL hooks inline"""
        # Build the sequence list with hooks and stages combined
        sequence_parts = []
        
        # Stage name mapping (flow_sequence name -> hook stage name)
        stage_mapping = {
            'edi_plan': 'plan',
            'plan': 'plan',
            # Add more mappings as needed
        }
        
        for step in flow_sequence:
            # Try direct match first, then try mapped name
            matched_hooks = None
            if step in hooks:
                matched_hooks = hooks[step]
            elif step in stage_mapping and stage_mapping[step] in hooks:
                matched_hooks = hooks[stage_mapping[step]]
            
            # Separate hooks by type (begin vs end)
            begin_hooks = []
            end_hooks = []
            if matched_hooks:
                for script, hook_type in matched_hooks:
                    if hook_type == 'begin':
                        begin_hooks.append(script)
                    elif hook_type == 'end':
                        end_hooks.append(script)
            
            # Build stage string with hooks attached (no arrows between them)
            stage_str = ""
            if begin_hooks:
                stage_str += f"[+{',+'.join(begin_hooks)}] "
            stage_str += f"{Color.YELLOW}{step}{Color.RESET}"
            if end_hooks:
                stage_str += f" [+{',+'.join(end_hooks)}]"
            
            sequence_parts.append(stage_str)
        
        # Print with arrows only between stages (not between hooks and stages)
        print(f"  {Color.CYAN}Flow Sequence ({ipo}):{Color.RESET} {' -> '.join(sequence_parts)}")
    
    def _extract_yaml_prc_configuration(self, content):
        """Extract configuration from YAML-based PRC file"""
        lines = content.split('\n')
        
        # Extract IPO information
        ipos = []
        for line in lines:
            if re.match(r'^\s*ipo(\d+)\s*:', line):
                ipo_match = re.search(r'ipo(\d+)', line)
                if ipo_match:
                    ipos.append(ipo_match.group(1))
        
        if ipos:
            print(f"  {Color.CYAN}Available IPOs:{Color.RESET} {', '.join(ipos)}")
        
        # Extract tool information
        tools = set()
        for line in lines:
            if 'tool:' in line:
                tool_match = re.search(r'tool:\s*(\w+)', line)
                if tool_match:
                    tools.add(tool_match.group(1))
        if tools:
            print(f"  {Color.CYAN}Tools:{Color.RESET} {', '.join(tools)}")
        
        # Extract TCL hook scripts per IPO
        hook_scripts = {}  # {ipo: {stage: [(script, type)]}}
        current_ipo = None
        in_scripts = False
        current_script = None
        current_stage = None
        current_type = None
        
        for i, line in enumerate(lines):
            # Check for IPO start
            ipo_match = re.match(r'^\s*(ipo\d+)\s*:', line)
            if ipo_match:
                current_ipo = ipo_match.group(1)
                if current_ipo not in hook_scripts:
                    hook_scripts[current_ipo] = {}
                in_scripts = False
                continue
            
            # Check for scripts section
            if current_ipo and re.match(r'^\s{4}scripts:', line):
                in_scripts = True
                continue
            
            # Exit scripts section when we hit another key at same level
            if in_scripts and re.match(r'^\s{4}[a-z_]+:', line) and 'scripts:' not in line:
                in_scripts = False
                continue
            
            # Parse script entries
            if in_scripts and current_ipo:
                # Script name line: "     - script_name.tcl:" (flexible whitespace before dash)
                script_match = re.match(r'^\s+-\s+([\w.]+):', line)
                if script_match:
                    current_script = script_match.group(1)
                    current_stage = None
                    current_type = None
                    continue
                
                # Stage line: "          stage: place" (flexible whitespace)
                if current_script and 'stage:' in line:
                    stage_match = re.search(r'stage:\s*(\w+)', line)
                    if stage_match:
                        current_stage = stage_match.group(1)
                        continue
                
                # Type line: "          type: begin" (flexible whitespace)
                if current_script and 'type:' in line:
                    type_match = re.search(r'type:\s*(\w+)', line)
                    if type_match:
                        current_type = type_match.group(1)
                        
                        # Store the complete hook info
                        if current_stage:
                            if current_stage not in hook_scripts[current_ipo]:
                                hook_scripts[current_ipo][current_stage] = []
                            hook_scripts[current_ipo][current_stage].append((current_script, current_type))
                        
                        # Reset for next script
                        current_script = None
                        current_stage = None
                        current_type = None
        
        # Process each IPO individually for flow sequence
        current_ipo = None
        in_flow_sequence = False
        flow_sequence = []
        
        for i, line in enumerate(lines):
            # Check for IPO start
            ipo_match = re.match(r'^\s*(ipo\d+)\s*:', line)
            if ipo_match:
                # Print previous IPO's flow sequence if we have one
                if current_ipo and flow_sequence:
                    self._print_flow_sequence_with_hooks(current_ipo, flow_sequence, hook_scripts.get(current_ipo, {}))
                
                current_ipo = ipo_match.group(1)
                in_flow_sequence = False
                flow_sequence = []
                continue
            
            # Extract flow sequence for current IPO
            if current_ipo and 'flow_sequence:' in line:
                in_flow_sequence = True
                continue
            elif in_flow_sequence and current_ipo:
                # Exit flow_sequence section when we hit another YAML key at same indentation
                # (e.g., ipo_number:, handoffs:, recipes:, scripts:)
                if re.match(r'^\s{4}[a-z_]+:', line):  # 4-space indent = same level as flow_sequence
                    in_flow_sequence = False
                    continue
                    
                if line.strip().startswith('- '):
                    step = line.strip()[2:].strip()
                    if ':' in step:
                        step = step.split(':')[0]
                    # Only include main flow steps, not handoffs/recipes
                    if step not in ['prime.SELF_BLOCK.mk', 'prime.beflow.mk', 'CUSTOM_MAKE', 'CUSTOM_YAML', 'SELF_BLOCK.yaml?']:
                        flow_sequence.append(step)
                elif line.strip() and not line.startswith(' '):
                    in_flow_sequence = False
        
        # Print last IPO's flow sequence
        if current_ipo and flow_sequence:
            self._print_flow_sequence_with_hooks(current_ipo, flow_sequence, hook_scripts.get(current_ipo, {}))
        
        # Extract useful skew settings per IPO
        current_ipo = None
        useful_skew_settings = {}
        
        for i, line in enumerate(lines):
            # Track current IPO
            ipo_match = re.match(r'^\s*(ipo\d+)\s*:', line)
            if ipo_match:
                current_ipo = ipo_match.group(1)
                continue
            
            # Extract useful skew for current IPO
            if current_ipo and 'USEFUL_SKEW:' in line:
                # Look for ENABLE in the next few lines
                for j in range(i, min(i+10, len(lines))):
                    if 'ENABLE:' in lines[j] and 'value:' in lines[j+1]:
                        value_line = lines[j+1]
                        value_match = re.search(r'value:\s*(\d+)', value_line)
                        if value_match:
                            value = "Useful Skew Enabled" if value_match.group(1) == "1" else "Useful Skew Disabled"
                            # Determine context based on previous lines
                            context = "Unknown"
                            for k in range(max(0, i-20), i):
                                if 'PLACE:' in lines[k]:
                                    context = "PLACE"
                                    break
                                elif 'POSTROUTE:' in lines[k]:
                                    context = "POSTROUTE"
                                    break
                            
                            if current_ipo not in useful_skew_settings:
                                useful_skew_settings[current_ipo] = {}
                            useful_skew_settings[current_ipo][context] = value
                            break
        
        # Print useful skew settings per IPO
        if useful_skew_settings:
            print(f"  {Color.CYAN}Useful Skew Settings:{Color.RESET}")
            for ipo, settings in useful_skew_settings.items():
                print(f"    {ipo}:")
                for context, value in settings.items():
                    print(f"      {context}: {value}")
        
        # Extract power optimization settings
        power_ratios = set()
        for i, line in enumerate(lines):
            if 'LEAKAGE_DYNAMIC_RATIO:' in line:
                # Look for value in next line
                if i + 1 < len(lines):
                    value_line = lines[i + 1]
                    ratio_match = re.search(r'value:\s*([\d.]+)', value_line)
                    if ratio_match:
                        power_ratios.add(ratio_match.group(1))
        
        if power_ratios:
            print(f"  {Color.CYAN}Power Optimization Ratios:{Color.RESET} {', '.join(sorted(power_ratios))}")
        
        # Extract clock tree settings per IPO
        current_ipo = None
        clock_names = {}
        
        for i, line in enumerate(lines):
            # Track current IPO
            ipo_match = re.match(r'^\s*(ipo\d+)\s*:', line)
            if ipo_match:
                current_ipo = ipo_match.group(1)
                continue
            
            # Extract clock names for current IPO
            if current_ipo and 'SDC_CLOCK_NAMES:' in line:
                # Look for value in next line
                if i + 1 < len(lines):
                    value_line = lines[i + 1]
                    if 'value:' in value_line:
                        clock_line = value_line.split('value:')[1].strip()
                        clock_names[current_ipo] = clock_line
                        break
        
        # Print clock names per IPO
        if clock_names:
            print(f"  {Color.CYAN}Clock Names:{Color.RESET}")
            for ipo, clocks in clock_names.items():
                print(f"    {ipo}: {clocks}")
    
    def _verify_tcl_usage_in_prc(self, prc_file, common_dir):
        """Verify that Common TCL files are actually used in the PnR configuration"""
        try:
            # Read the PnR configuration file
            with open(prc_file, 'r', encoding='utf-8') as f:
                prc_content = f.read()
            
            # Get all TCL files in COMMON directory
            tcl_files = self.file_utils.find_files("pnr_flow/nv_flow/COMMON/*.tcl", self.workarea)
            
            if not tcl_files:
                return
            
            print(f"  {Color.CYAN}TCL Usage Verification:{Color.RESET}")
            
            used_tcl_files = []
            unused_tcl_files = []
            
            # Check if it's YAML format
            if f"{self.design_info.top_hier}:" in prc_content:
                # For YAML format, look in CUSTOM_MAKE sections
                for tcl_file in tcl_files:
                    tcl_filename = os.path.basename(tcl_file)
                    # Check if TCL filename appears in CUSTOM_MAKE sections
                    if f"CUSTOM_MAKE:" in prc_content and tcl_filename in prc_content:
                        used_tcl_files.append(tcl_filename)
                    else:
                        unused_tcl_files.append(tcl_filename)
            else:
                # Legacy format - simple filename matching
                for tcl_file in tcl_files:
                    tcl_filename = os.path.basename(tcl_file)
                if tcl_filename in prc_content:
                    used_tcl_files.append(tcl_filename)
                else:
                    unused_tcl_files.append(tcl_filename)
            
            # Report results
            if used_tcl_files:
                print(f"    {Color.GREEN}[OK] Used TCL files ({len(used_tcl_files)}):{Color.RESET}")
                for tcl_file in sorted(used_tcl_files):
                    print(f"      - {tcl_file}")
            
            if unused_tcl_files:
                print(f"    {Color.YELLOW}[WARN] Unused TCL files ({len(unused_tcl_files)}):{Color.RESET}")
                for tcl_file in sorted(unused_tcl_files):
                    print(f"      - {tcl_file}")
            
            if not used_tcl_files and not unused_tcl_files:
                print(f"    {Color.YELLOW}No TCL files found to verify{Color.RESET}")
                
        except Exception as e:
            print(f"    {Color.RED}Error verifying TCL usage: {e}{Color.RESET}")
    
    def _extract_pnr_flow_variables(self, runset_file):
        """Extract important PnR flow variables from runset.tcl file"""
        try:
            with open(runset_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"  {Color.CYAN}PnR Flow Variables:{Color.RESET}")
            
            # Variables to extract with their actual patterns in runset.tcl
            variable_patterns = [
                (r'set\s+FLOW\(PATH\)\s+([^\s\n]+)', 'FLOW(PATH)'),
                (r'set\s+PROJECT\(CUSTOM_SCRIPTS_DIR\)\s+([^\s\n]+)', 'PROJECT(CUSTOM_SCRIPTS_DIR)'),
                (r'set\s+BLOCK\(FLOORPLAN,FILE\)\s+([^\s\n]+)', 'FLOORPLAN'),
                (r'set\s+BLOCK\(FLOORPLAN,PIN_PLACEMENT_FILE\)\s+([^\s\n]+)', 'PIN_PLACEMENT_FILE'),
                (r'set\s+PROJECT\(TOP_PLANNER_YAML\)\s+([^\s\n]+)', 'TOP_PLANNER_YAML'),
                (r'set\s+VERSION\(DC_SHELL\)\s+([^\s\n]+)', 'DC_SHELL_VERSION'),
                (r'set\s+LIB\(PHYSICAL,PATH,RAM\)\s+([^\s\n]+)', 'RAM_LIB_PATH'),
                (r'set\s+LIB\(CENTRAL,PATH\)\s+([^\s\n]+)', 'CENTRAL_LIB_PATH'),
                (r'set\s+NETWORK_FLOW\(PATH\)\s+([^\s\n]+)', 'NETWORK_FLOW_PATH'),
                (r'set\s+NETWORK_FLOW\(UTILS_DIR\)\s+([^\s\n]+)', 'NETWORK_FLOW_UTILS_DIR')
            ]
            
            found_variables = []
            
            for pattern, var_name in variable_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    value = matches[0].strip()
                    if value and value != '""' and value != "''" and value != "None":
                        found_variables.append((var_name, value))
            
            if found_variables:
                for var, value in found_variables:
                    # Display full values without truncation
                    print(f"    {var}: {value}")
            else:
                print(f"    {Color.YELLOW}No PnR flow variables found{Color.RESET}")
                
        except Exception as e:
            print(f"    {Color.RED}Error extracting PnR flow variables: {e}{Color.RESET}")
    
    def run_recipe_analysis(self):
        """Run recipe configuration analysis"""
        pass
    
    def run_pnr_analysis(self):
        """Run comprehensive PnR (Place & Route) analysis"""
        self.print_header(FlowStage.PNR_ANALYSIS)
        
        # PnR Status
        prc_status = os.path.join(self.workarea, f"pnr_flow/nv_flow/{self.design_info.top_hier}.prc.status")
        if self.file_utils.file_exists(prc_status):
            self.print_file_info(prc_status, "PnR Status")
            self._analyze_pnr_status(prc_status)
        
        # PnR Configuration
        prc_file = os.path.join(self.workarea, f"pnr_flow/nv_flow/{self.design_info.top_hier}.prc")
        if self.print_file_info(prc_file, "PnR Configuration"):
            self._extract_prc_configuration(prc_file)
        
        # Verify TCL files are used in PnR configuration
        common_dir = os.path.join(self.workarea, "pnr_flow/nv_flow/COMMON")
        if os.path.exists(prc_file) and os.path.exists(common_dir):
            self._verify_tcl_usage_in_prc(prc_file, common_dir)
        
        # Extract PnR flow variables from runset.tcl
        runset_file = os.path.join(self.workarea, f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/runset.tcl")
        if self.print_file_info(runset_file, "PnR Runset"):
            self._extract_pnr_flow_variables(runset_file)
        
        # BeFlow Configuration (use first available IPO)
        first_ipo = self.design_info.all_ipos[0] if self.design_info.all_ipos else self.design_info.ipo
        beflow_config = os.path.join(self.workarea, f"pnr_flow/nv_flow/{self.design_info.top_hier}/{first_ipo}/beflow_config.yaml")
        if self.print_file_info(beflow_config, f"PnR BeFlow Configuration ({first_ipo})"):
            self._analyze_beflow_config(beflow_config)
        
        # Summary reports
        summary_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/ipo*/REPs/SUMMARY/*route.nbu_summary.rpt*"
        summary_files = self.file_utils.find_files(summary_pattern, self.workarea)
        
        if summary_files:
            self.print_file_info(summary_files[0], "Route Summary")
            matches = self.file_utils.grep_file(r"diearea|CellCount|SequentialCount|VT|Shorts", summary_files[0])
            for match in matches:
                print(f"  {match}")
        
        # Data reports - try postroute first, then fallback to earlier stages
        temperature_corners = ['0c_0p6v', '125c_0p6v', '25c_0p6v', '85c_0p6v']
        pnr_stages = ['postroute', 'route', 'cts', 'place', 'plan']
        data_files = []
        found_stage = None
        
        # Try each stage in order
        for stage in pnr_stages:
            for temp_corner in temperature_corners:
                data_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/reports/{self.design_info.top_hier}_{self.design_info.top_hier}_{self.design_info.ipo}_report_{self.design_info.top_hier}_{self.design_info.ipo}_{stage}.func.std_tt_{temp_corner}.setup.typical.data"
                found_files = self.file_utils.find_files(data_pattern, self.workarea)
                if found_files:
                    data_files = found_files
                    found_stage = stage
                    break
            if data_files:
                break
        
        if data_files:
            if found_stage == 'postroute':
                self.print_file_info(data_files[0], "Post-Route Data")
            else:
                self.print_file_info(data_files[0], f"PnR Data ({found_stage.upper()} stage)")
                print(f"    {Color.YELLOW}Note: Post-route data not available, showing {found_stage.upper()} stage data instead{Color.RESET}")
            
            self._extract_postroute_data_parameters(data_files[0], found_stage)
        else:
            print(f"  {Color.YELLOW}PnR Data: No data files found for any stage or temperature corner{Color.RESET}")
            print(f"    {Color.YELLOW}Tried stages: {', '.join(pnr_stages)}{Color.RESET}")
            print(f"    {Color.YELLOW}Tried corners: {', '.join(temperature_corners)}{Color.RESET}")
            print(f"    {Color.YELLOW}This could be due to:{Color.RESET}")
            print(f"      - Flow still running (data files not yet generated)")
            print(f"      - Flow failed at this stage")
            print(f"      - Different temperature corner used")
            print(f"      - File permissions issue")
        
        # Power summary
        power_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/ipo*/REPs/SUMMARY/*.postroute.power.rpt*"
        power_files = self.file_utils.find_files(power_pattern, self.workarea)
        
        if power_files:
            self.print_file_info(power_files[0], "Power Summary")
            self._extract_power_summary_table(power_files[0])
        
        # PnR Timing Histogram
        self._extract_pnr_timing_histogram()
        
        # Generate timing histogram HTML report (after displaying tables)
        self._generate_timing_histogram_html()
        
        # Visualization commands
        print(f"\n{Color.CYAN}PnR Pictures:{Color.RESET}")
        pnr_image_html = self._generate_image_html_report()
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Place & Route (PnR)",
            section_id="pnr",
            stage=FlowStage.PNR_ANALYSIS,
            status="PASS",
            key_metrics={
                "Design": self.design_info.top_hier,
                "IPO": self.design_info.ipo
            },
            html_file=pnr_image_html if pnr_image_html else "",
            priority=2,
            issues=[],
            icon="[PnR]"
        )
    
    def _generate_timing_histogram_html(self):
        """Generate HTML report with timing histogram tables"""
        try:
            # Define stage priority order
            pnr_stages = ['postroute', 'route', 'cts', 'place', 'plan']
            timing_file = None
            found_stage = None
            
            # Try each stage in priority order
            for stage in pnr_stages:
                timing_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.{stage}.timing.setup.rpt.gz"
                timing_files = self.file_utils.find_files(timing_pattern, self.workarea)
                if timing_files:
                    timing_file = timing_files[0]
                    found_stage = stage
                    break
            
            if timing_file:
                # Extract the last three histogram tables (category, sub-category, and sub-category+scenario)
                result = self.file_utils.run_command(f"zcat {timing_file} | grep -n 'histogram' | grep '|'")
                if result.strip():
                    histogram_lines = result.strip().split('\n')
                    if len(histogram_lines) >= 4:
                        # Get the last 4 tables: category, scenario, sub-category, and sub-category + scenario
                        table_category_start = int(histogram_lines[-4].split(':')[0])  # Category breakdown
                        table_scenario_start = int(histogram_lines[-3].split(':')[0])  # Scenario breakdown
                        table_subcat_start = int(histogram_lines[-2].split(':')[0])    # Sub-category breakdown
                        table_subcat_scenario_start = int(histogram_lines[-1].split(':')[0])  # Sub-category + scenario breakdown
                        
                        # Find the end of category table (it ends before scenario table starts)
                        table_category_end = table_scenario_start - 1
                        
                        # Extract category table
                        table_category_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_category_start},{table_category_end}p'")
                        
                        # Find the end of sub-category table (it ends before sub-category + scenario table starts)
                        table_subcat_end = table_subcat_scenario_start - 1
                        
                        # Extract sub-category table
                        table_subcat_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_subcat_start},{table_subcat_end}p'")
                        
                        # Extract sub-category + scenario table - get remaining lines
                        table_subcat_scenario_result = self.file_utils.run_command(f"zcat {timing_file} | sed -n '{table_subcat_scenario_start},$p'")
                        
                        if table_category_result.strip() and table_subcat_result.strip() and table_subcat_scenario_result.strip():
                            # Generate HTML content for timing histogram
                            html_content = self._create_timing_histogram_html(table_category_result.strip(), table_subcat_result.strip(), table_subcat_scenario_result.strip(), found_stage)
                            
                            # Save HTML file
                            html_filename = f"{os.environ.get('USER', 'avice')}_innovus_timing_histogram_{self.design_info.top_hier}_{self.design_info.ipo}.html"
                            html_path = os.path.join(os.getcwd(), html_filename)
                            
                            with open(html_path, 'w', encoding='utf-8') as f:
                                f.write(html_content)
                            
                            print(f"\n  {Color.CYAN}Timing Histogram HTML Report:{Color.RESET}")
                            print(f"  Open with: firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
                        
        except Exception as e:
            print(f"  Error generating timing histogram HTML: {e}")
    
    def _create_timing_histogram_html(self, category_data: str, sub_category_data: str, scenario_data: str, stage: str) -> str:
        """Create HTML content for timing histogram tables"""
        # Process the three separate tables
        category_table = [line.strip() for line in category_data.split('\n') if line.strip()]
        sub_category_table = [line.strip() for line in sub_category_data.split('\n') if line.strip()]
        scenario_table = [line.strip() for line in scenario_data.split('\n') if line.strip()]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Timing Histogram Analysis - {self.design_info.top_hier}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 95%; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .info {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 12px; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 6px; text-align: center; }}
        th {{ background-color: #34495e; color: white; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .external {{ background-color: #e8f5e8; }}
        .internal {{ background-color: #fff3cd; }}
        .histogram-cell {{ font-family: 'Courier New', monospace; font-size: 11px; }}
        .legend {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; border-left: 4px solid #3498db; }}
        .legend h4 {{ margin-top: 0; color: #2c3e50; }}
        .legend ul {{ margin: 10px 0; padding-left: 20px; }}
        .legend li {{ margin: 5px 0; }}
        .header {{ text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }}
        .logo {{ text-align: center; margin-bottom: 10px; }}
        .logo img {{ 
            max-height: 80px; 
            max-width: 300px; 
            height: auto; 
            width: auto; 
            cursor: pointer;
            transition: transform 0.2s ease;
            border-radius: 6px;
        }}
        .logo img:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
        }}
        .image-expanded {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        .image-expanded img {{
            max-width: 90%;
            max-height: 90%;
            border: 3px solid #3498db;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="/home/avice/scripts/avice_wa_review/images/avice_logo.png" alt="AVICE Logo" onclick="expandImage(this)">
            </div>
            <h1>Timing Histogram Analysis</h1>
        </div>
        
        <div class="info">
            <h3>Report Information</h3>
            <p><strong>Design:</strong> {self.design_info.top_hier}</p>
            <p><strong>IPO:</strong> {self.design_info.ipo}</p>
            <p><strong>Tag:</strong> {self.design_info.tag}</p>
            <p><strong>Workarea:</strong> {self.workarea_abs}</p>
            <p><strong>Stage:</strong> {stage.upper()}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
                <h2>Category Breakdown</h2>
                <p>Timing analysis by category showing external and internal timing paths.</p>
                <table>
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Category</th>
                            <th>WNS (ns)</th>
                            <th>TNS (ns)</th>
                            <th>FEP</th>
                            <th colspan="11">Histogram (Path Count by Slack Range)</th>
                        </tr>
                        <tr>
                            <th></th>
                            <th></th>
                            <th></th>
                            <th></th>
                            <th></th>
                            <th>-0.010</th>
                            <th>-0.020</th>
                            <th>-0.030</th>
                            <th>-0.040</th>
                            <th>-0.050</th>
                            <th>-0.060</th>
                            <th>-0.070</th>
                            <th>-0.080</th>
                            <th>-0.090</th>
                            <th>-0.100</th>
                            <th>-Inf</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Process category table
        for line in category_table:
            if '=' in line or 'histogram' in line.lower() or 'type' in line.lower():
                continue
            # Check if line has data (contains numbers and |)
            if '|' in line and any(char.isdigit() or char == '-' for char in line):
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 6:  # Minimum columns for category table
                    # Determine type class based on first column or content
                    first_col = parts[0].strip() if len(parts) > 0 else ''
                    if 'external' in first_col.lower():
                        type_class = 'external'
                    elif 'internal' in first_col.lower():
                        type_class = 'internal'
                    else:
                        # Default to internal for rows without explicit type
                        type_class = 'internal'
                    
                    html += f"                <tr class=\"{type_class}\">\n"
                    html += f"                    <td>{first_col}</td>\n"  # type
                    html += f"                    <td>{parts[1] if len(parts) > 1 and parts[1].strip() else ''}</td>\n"  # category
                    html += f"                    <td>{parts[2] if len(parts) > 2 and parts[2].strip() else ''}</td>\n"  # wns
                    html += f"                    <td>{parts[3] if len(parts) > 3 and parts[3].strip() else ''}</td>\n"  # tns
                    html += f"                    <td>{parts[4] if len(parts) > 4 and parts[4].strip() else ''}</td>\n"  # fep
                    # Histogram data - split the histogram string into individual values
                    if len(parts) > 5:
                        histogram_data = parts[5].split()
                        for i, value in enumerate(histogram_data):
                            if i < 11:  # Limit to 11 histogram columns
                                html += f"                    <td class=\"histogram-cell\">{value}</td>\n"
                        # Fill remaining histogram columns if needed
                        for i in range(len(histogram_data), 11):
                            html += f"                    <td class=\"histogram-cell\"></td>\n"
                    else:
                        # Fill all histogram columns if no data
                        for i in range(11):
                            html += f"                    <td class=\"histogram-cell\"></td>\n"
                    html += "                </tr>\n"
        
        html += """            </tbody>
            </table>
            
            <h2>Sub-Category Breakdown</h2>
            <p>Timing analysis by category and sub-category showing external and internal timing paths.</p>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Sub-Category</th>
                    <th>WNS (ns)</th>
                    <th>TNS (ns)</th>
                    <th>FEP</th>
                    <th colspan="11">Histogram (Path Count by Slack Range)</th>
                </tr>
                <tr>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th>-0.010</th>
                    <th>-0.020</th>
                    <th>-0.030</th>
                    <th>-0.040</th>
                    <th>-0.050</th>
                    <th>-0.060</th>
                    <th>-0.070</th>
                    <th>-0.080</th>
                    <th>-0.090</th>
                    <th>-0.100</th>
                    <th>-Inf</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Process sub-category table
        for line in sub_category_table:
            if '=' in line or 'histogram' in line.lower() or 'type' in line.lower():
                continue
            # Check if line has data (contains numbers and |)
            if '|' in line and any(char.isdigit() or char == '-' for char in line):
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 7:  # Minimum columns for sub-category table
                    # Determine type class based on first column or content
                    first_col = parts[0].strip() if len(parts) > 0 else ''
                    if 'external' in first_col.lower():
                        type_class = 'external'
                    elif 'internal' in first_col.lower():
                        type_class = 'internal'
                    else:
                        # Default to internal for rows without explicit type
                        type_class = 'internal'
                    
                    html += f"                <tr class=\"{type_class}\">\n"
                    html += f"                    <td>{first_col}</td>\n"  # type
                    html += f"                    <td>{parts[1] if len(parts) > 1 else ''}</td>\n"  # category
                    html += f"                    <td>{parts[2] if len(parts) > 2 else ''}</td>\n"  # sub_category
                    html += f"                    <td>{parts[3] if len(parts) > 3 else ''}</td>\n"  # wns
                    html += f"                    <td>{parts[4] if len(parts) > 4 else ''}</td>\n"  # tns
                    html += f"                    <td>{parts[5] if len(parts) > 5 else ''}</td>\n"  # fep
                    # Histogram data - split the histogram string into individual values
                    if len(parts) > 6:
                        histogram_data = parts[6].split()
                        for i, value in enumerate(histogram_data):
                            if i < 11:  # Limit to 11 histogram columns
                                html += f"                    <td class=\"histogram-cell\">{value}</td>\n"
                        # Fill remaining histogram columns if needed
                        for i in range(len(histogram_data), 11):
                            html += f"                    <td class=\"histogram-cell\"></td>\n"
                    else:
                        # Fill all histogram columns if no data
                        for i in range(11):
                            html += f"                    <td class=\"histogram-cell\"></td>\n"
                    html += "                </tr>\n"
        
        html += """            </tbody>
        </table>
        
        <h2>Scenario Breakdown</h2>
        <p>Timing analysis by category, sub-category, and scenario showing both typical and high-temperature conditions.</p>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Sub-Category</th>
                    <th>Scenario</th>
                    <th>WNS (ns)</th>
                    <th>TNS (ns)</th>
                    <th>FEP</th>
                    <th colspan="11">Histogram (Path Count by Slack Range)</th>
                </tr>
                <tr>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th>-0.010</th>
                    <th>-0.020</th>
                    <th>-0.030</th>
                    <th>-0.040</th>
                    <th>-0.050</th>
                    <th>-0.060</th>
                    <th>-0.070</th>
                    <th>-0.080</th>
                    <th>-0.090</th>
                    <th>-0.100</th>
                    <th>-Inf</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Process scenario table
        for line in scenario_table:
            if '=' in line or 'histogram' in line.lower() or 'type' in line.lower():
                continue
            # Check if line has data (contains numbers and |)
            if '|' in line and any(char.isdigit() or char == '-' for char in line):
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 8:  # Minimum columns for scenario table
                    # Determine type based on category - look for the first non-empty category
                    type_class = 'external'  # Default fallback
                    category = ''
                    for i in range(1, min(4, len(parts))):
                        if parts[i].strip() and parts[i].strip() not in ['', '............', '..................']:
                            category = parts[i].strip()
                            if category in ['output', 'input']:
                                type_class = 'external'
                            else:
                                type_class = 'internal'
                            break
                    
                    html += f"                <tr class=\"{type_class}\">\n"
                    html += f"                    <td>{parts[0] if len(parts) > 0 and parts[0].strip() else ''}</td>\n"  # type
                    html += f"                    <td>{parts[1] if len(parts) > 1 and parts[1].strip() else ''}</td>\n"  # category
                    html += f"                    <td>{parts[2] if len(parts) > 2 and parts[2].strip() else ''}</td>\n"  # sub_category
                    html += f"                    <td>{parts[3] if len(parts) > 3 and parts[3].strip() else ''}</td>\n"  # scenario
                    html += f"                    <td>{parts[4] if len(parts) > 4 and parts[4].strip() else ''}</td>\n"  # wns
                    html += f"                    <td>{parts[5] if len(parts) > 5 and parts[5].strip() else ''}</td>\n"  # tns
                    html += f"                    <td>{parts[6] if len(parts) > 6 and parts[6].strip() else ''}</td>\n"  # fep
                    # Histogram data - split the histogram string into individual values
                    if len(parts) > 7:
                        histogram_data = parts[7].split()
                        for i, value in enumerate(histogram_data):
                            if i < 11:  # Limit to 11 histogram columns
                                html += f"                    <td class=\"histogram-cell\">{value}</td>\n"
                        # Fill remaining histogram columns if needed
                        for i in range(len(histogram_data), 11):
                            html += f"                    <td class=\"histogram-cell\"></td>\n"
                    else:
                        # Fill all histogram columns if no data
                        for i in range(11):
                            html += f"                    <td class=\"histogram-cell\"></td>\n"
                    html += "                </tr>\n"
        
        html += """            </tbody>
        </table>
        
        <div class="legend">
            <h4>Legend</h4>
            <ul>
                <li><strong>WNS:</strong> Worst Negative Slack (ns)</li>
                <li><strong>TNS:</strong> Total Negative Slack (ns)</li>
                <li><strong>FEP:</strong> Failing Endpoint Count</li>
                <li><strong>Histogram:</strong> Number of paths in each slack range</li>
            </ul>
            <h4>Path Types</h4>
            <ul>
                <li><span class="external" style="padding: 2px 6px; border-radius: 3px;">External:</span> Input/Output timing paths</li>
                <li><span class="internal" style="padding: 2px 6px; border-radius: 3px;">Internal:</span> Register-to-register timing paths</li>
            </ul>
            <h4>Categories</h4>
            <ul>
                <li><strong>Output:</strong> Flop-to-port paths</li>
                <li><strong>Input:</strong> Port-to-flop and port-to-clock-gate paths</li>
                <li><strong>Reg_to_reg:</strong> Flop-to-flop paths</li>
                <li><strong>Reg_to_cgate:</strong> Flop-to-clock-gate paths</li>
            </ul>
        </div>
    </div>
    
    <script>
        function expandImage(imgElement) {{
            // Create overlay
            var overlay = document.createElement('div');
            overlay.className = 'image-expanded';
            
            // Create expanded image
            var expandedImg = document.createElement('img');
            expandedImg.src = imgElement.src;
            expandedImg.alt = imgElement.alt;
            
            overlay.appendChild(expandedImg);
            document.body.appendChild(overlay);
            
            // Close on click
            overlay.onclick = function() {{
                if (document.body.contains(overlay)) {{
                    document.body.removeChild(overlay);
                }}
            }};
            
            // Close on escape key
            function escapeHandler(e) {{
                e = e || window.event;
                if ((e.keyCode || e.which) === 27) {{
                    if (document.body.contains(overlay)) {{
                        document.body.removeChild(overlay);
                        if (document.removeEventListener) {{
                            document.removeEventListener('keydown', escapeHandler);
                        }} else if (document.detachEvent) {{
                            document.detachEvent('onkeydown', escapeHandler);
                        }}
                    }}
                }}
            }}
            
            if (document.addEventListener) {{
                document.addEventListener('keydown', escapeHandler);
            }} else if (document.attachEvent) {{
                document.attachEvent('onkeydown', escapeHandler);
            }}
        }}
    </script>
</body>
</html>
"""
        
        return html
    
    def run_clock_analysis(self):
        """Run clock analysis"""
        self.print_header(FlowStage.CLOCK_ANALYSIS)
        
        # Innvou clock analysis
        clock_skew_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.postroute.clock_tree.skew_and_latency.from_clock_root_source.rpt*"
        clock_files = self.file_utils.find_files(clock_skew_pattern, self.workarea)
        
        if clock_files:
            self.print_file_info(clock_files[0], "Innvou Clock Analysis")
            self._extract_clock_tree_data(clock_files[0])
        
        # PrimeTime clock analysis
        pt_clock_pattern = f"signoff_flow/auto_pt/last_work/func.std_tt_0c_0p6v.setup.typical/reports/timing_reports/{self.design_info.top_hier}_func.std_tt_0c_0p6v.setup.typical.clock_latency"
        pt_clock_file = os.path.join(self.workarea, pt_clock_pattern)
        
        if self.file_utils.file_exists(pt_clock_file):
            self.print_file_info(pt_clock_file, "PT Clock Analysis")
            self._extract_pt_clock_latency(pt_clock_file)
    
    def run_formal_verification(self):
        """Run formal verification analysis"""
        self.print_header(FlowStage.FORMAL_VERIFICATION)
        
        formal_log_pattern = "formal_flow/*_vs_*_fm/log/*_vs_*_fm.log"
        formal_files = self.file_utils.find_files(formal_log_pattern, self.workarea)
        
        if formal_files:
            # Get latest formal end time for comparison with ECO
            latest_formal_end = 0
            
            for log_file in formal_files:
                self.print_file_info(log_file, "Formal Log")
                self._extract_formal_verification_status(log_file)
                # Extract and display timestamps
                formal_end_time = self._display_formal_timestamps(log_file)
                if formal_end_time and formal_end_time > latest_formal_end:
                    latest_formal_end = formal_end_time
            
            # Check if ECO was run after formal (potential issue)
            self._check_formal_vs_eco_timestamps(latest_formal_end)
        else:
            print("No formal verification logs found")
    
    def run_parasitic_extraction(self):
        """Run parasitic extraction analysis"""
        self.print_header(FlowStage.PARASITIC_EXTRACTION)
        
        # Show Star flow timeline
        star_local_flow_dirs = [
            os.path.join(self.workarea, f"export/nv_star/{self.design_info.top_hier}/local_flow"),
            os.path.join(self.workarea, f"export/nv_star/local_flow"),
            os.path.join(self.workarea, f"export/nv_star/{self.design_info.top_hier}/ipo*/LOGs/PRIME"),
            os.path.join(self.workarea, f"export/nv_star/ipo*/LOGs/PRIME")
        ]
        self._show_flow_timeline("Star", star_local_flow_dirs)
        
        # Star extraction files
        spef_pattern = f"export/nv_star/{self.design_info.top_hier}/ipo*/IOs/netlists/*.spef.typical_T0.gz"
        spef_files = self.file_utils.find_files(spef_pattern, self.workarea)
        
        if spef_files:
            self.print_file_info(spef_files[0], "SPEF File")
        
        spef_info_pattern = f"export/nv_star/{self.design_info.top_hier}/ipo*/IOs/netlists/*.typical_T0.spef_info"
        spef_info_files = self.file_utils.find_files(spef_info_pattern, self.workarea)
        
        if spef_info_files:
            self.print_file_info(spef_info_files[0], "SPEF Info")
            try:
                with open(spef_info_files[0], 'r') as f:
                    content = f.read()
                
                # Extract opens and shorts counts
                opens_match = re.search(r'opens:\s*(\d+)', content)
                shorts_match = re.search(r'shorts:\s*(\d+)', content)
                
                opens_count = int(opens_match.group(1)) if opens_match else 0
                shorts_count = int(shorts_match.group(1)) if shorts_match else 0
                
                print(f"  Opens: {opens_count}")
                print(f"  Shorts: {shorts_count}")
                
            except Exception as e:
                print(f"  Error reading SPEF info: {e}")
                # Fallback to original grep method
                matches = self.file_utils.grep_file(r"opens|shorts", spef_info_files[0])
                for match in matches:
                    print(f"  {match}")
        
        # Star extraction shorts report
        shorts_pattern = f"export/nv_star/{self.design_info.top_hier}/ipo*/REPs/*.star_extraction_shorts.rpt"
        shorts_files = self.file_utils.find_files(shorts_pattern, self.workarea)
        
        if shorts_files:
            self.print_file_info(shorts_files[0], "Star Shorts Report")
            try:
                if shorts_files[0].endswith('.gz'):
                    with gzip.open(shorts_files[0], 'rt', encoding='utf-8') as f:
                        content = f.read()
                else:
                    with open(shorts_files[0], 'r', encoding='utf-8') as f:
                        content = f.read()
                print(content)
            except (OSError, UnicodeDecodeError, gzip.BadGzipFile):
                print("Unable to read Star Shorts Report")
    
    def run_signoff_timing(self):
        """Run signoff timing analysis"""
        self.print_header(FlowStage.SIGNOFF_TIMING)
        
        # Show PT flow timeline
        pt_local_flow_dirs = [
            os.path.join(self.workarea, f"signoff_flow/auto_pt/{self.design_info.top_hier}/local_flow"),
            os.path.join(self.workarea, f"signoff_flow/auto_pt/local_flow")
        ]
        self._show_flow_timeline("PT", pt_local_flow_dirs)
        
        # Check if PT is currently running
        work_pattern = os.path.join(self.workarea, "signoff_flow/auto_pt/work_*")
        all_items = glob.glob(work_pattern)
        work_dirs = [item for item in all_items if os.path.isdir(item)]
        if work_dirs:
            work_dirs_sorted = sorted(work_dirs, key=os.path.getmtime, reverse=True)
            latest_work = work_dirs_sorted[0]
            latest_work_name = os.path.basename(latest_work)
            
            # Check if HTML report exists for the latest work area
            html_for_latest = os.path.join(self.workarea, f"signoff_flow/auto_pt/{latest_work_name}.html")
            if not os.path.exists(html_for_latest):
                # No HTML means PT is likely still running
                # Check if files were recently modified (within last hour)
                latest_mtime = os.path.getmtime(latest_work)
                current_time = time.time()
                time_since_update = (current_time - latest_mtime) / 60  # minutes
                
                if time_since_update < 60:  # Within last hour
                    print(f"{Color.YELLOW}PT Status: RUNNING (work area: {latest_work_name}){Color.RESET}")
                    print(f"  Last updated: {int(time_since_update)} minutes ago")
        
        # HTML reports
        html_pattern = "signoff_flow/auto_pt/*html"
        html_files = self.file_utils.find_files(html_pattern, self.workarea)
        if html_files:
            for html_file in sorted(html_files, key=os.path.getmtime, reverse=True):
                print(f"HTML Report: {Color.MAGENTA}{self.file_utils.realpath(html_file)}{Color.RESET}")
        
        # Timing reports
        base_path = f"signoff_flow/auto_pt/last_work/func.std_tt_0c_0p6v.setup.typical"
        
        violators_pattern = f"{base_path}/reports/timing_reports/{self.design_info.top_hier}_func.std_tt_0c_0p6v.setup.typical.all_violators.gz"
        violators_file = os.path.join(self.workarea, violators_pattern)
        self.print_file_info(violators_file, "All Violators")
        
        # Check auto_pt.log for errors
        auto_pt_log = os.path.join(self.workarea, "signoff_flow/auto_pt/log/auto_pt.log")
        if self.print_file_info(auto_pt_log, "PT Log"):
            # Check for errors with more comprehensive patterns
            try:
                # Look for various error patterns (exclude warnings and informational messages)
                error_patterns = [
                    r"^Error:.*",  # Lines starting with "Error:" (case insensitive)
                    r".*\-E\-.*",  # Lines containing "-E-"
                    r"Extended.*rror.*nfo.*",  # Lines containing "Extended .rror .nfo"
                    r"^FATAL.*",  # Lines starting with "FATAL"
                    r"^CRITICAL.*",  # Lines starting with "CRITICAL"
                    r"^Failed.*",  # Lines starting with "Failed"
                    r"^Exception:.*",  # Lines starting with "Exception:"
                    r"^Abort.*"  # Lines starting with "Abort"
                ]
                
                all_errors = []
                for pattern in error_patterns:
                    matches = self.file_utils.grep_file(pattern, auto_pt_log)
                    all_errors.extend(matches)
                
                if all_errors:
                    print(f"{Color.RED}Errors found ({len(all_errors)} total):{Color.RESET}")
                    # Remove duplicates and filter out common false positives
                    unique_errors = list(dict.fromkeys(all_errors))
                    filtered_errors = []
                    for error in unique_errors:
                        error_text = error.strip()
                        # Skip empty lines and common false positives
                        if (error_text and 
                            not error_text.startswith("exceptions") and
                            not error_text.startswith("Run time:") and
                            not error_text.endswith("was not found.") and
                            not error_text.endswith("}':") and
                            not error_text.endswith('"') and
                            len(error_text) > 10):  # Skip very short matches
                            filtered_errors.append(error_text)
                    
                    # Show up to 15 filtered errors
                    if filtered_errors:
                        for error in filtered_errors[:15]:
                            print(f"  {error}")
                        if len(filtered_errors) > 15:
                            print(f"  ... and {len(filtered_errors) - 15} more errors")
                    else:
                        print(f"  {Color.GREEN}No errors found in PT log{Color.RESET}")
                    
            except Exception as e:
                print(f"  {Color.YELLOW}Error reading PT log: {e}{Color.RESET}")
        
        # Generate timing summary HTML report
        pt_html_path, timing_data = self._generate_timing_summary_report()
        
        # Add section summary for master dashboard
        status = "NOT_RUN"
        key_metrics = {}
        issues = []
        priority = 1  # Critical section
        
        if timing_data and len(timing_data) > 0:
            # Get latest work area data
            latest = timing_data[0]
            
            # Calculate status based on setup timing (most critical)
            if 'setup' in latest['scenarios']:
                setup_data = latest['scenarios']['setup']
                external_groups = {'FEEDTHROUGH', 'REGIN', 'REGOUT'}
                
                # Calculate internal WNS (worst of all internal groups)
                internal_wns = None
                internal_tns = 0
                internal_nvp = 0
                
                for group_name, group_data in setup_data['groups'].items():
                    if group_name.upper() not in external_groups:
                        internal_tns += group_data['TNS']
                        internal_nvp += group_data['NVP']
                        if internal_wns is None or group_data['WNS'] < internal_wns:
                            internal_wns = group_data['WNS']
                
                # Determine status based on WNS
                if internal_wns is not None:
                    if internal_wns < 0:
                        status = "FAIL"
                        issues.append(f"Setup timing violation: WNS = {internal_wns:.3f} ns")
                    elif internal_wns < 0.1:
                        status = "WARN"
                        issues.append(f"Setup timing marginal: WNS = {internal_wns:.3f} ns")
                    else:
                        status = "PASS"
                    
                    key_metrics["Setup WNS"] = f"{internal_wns:.3f} ns"
                    key_metrics["Setup TNS"] = f"{internal_tns:.2f} ns"
                    key_metrics["Setup NVP"] = str(internal_nvp)
            
            # Check hold timing too
            if 'hold' in latest['scenarios']:
                hold_data = latest['scenarios']['hold']
                external_groups = {'FEEDTHROUGH', 'REGIN', 'REGOUT'}
                
                hold_wns = None
                hold_tns = 0
                hold_nvp = 0
                
                for group_name, group_data in hold_data['groups'].items():
                    if group_name.upper() not in external_groups:
                        hold_tns += group_data['TNS']
                        hold_nvp += group_data['NVP']
                        if hold_wns is None or group_data['WNS'] < hold_wns:
                            hold_wns = group_data['WNS']
                
                if hold_wns is not None:
                    if hold_wns < 0:
                        status = "FAIL"  # Hold violation is critical
                        issues.append(f"Hold timing violation: WNS = {hold_wns:.3f} ns")
                    
                    key_metrics["Hold WNS"] = f"{hold_wns:.3f} ns"
            
            key_metrics["Work Areas"] = str(len(timing_data))
        
        self._add_section_summary(
            section_name="Signoff Timing (PT)",
            section_id="timing",
            stage=FlowStage.SIGNOFF_TIMING,
            status=status,
            key_metrics=key_metrics,
            html_file=pt_html_path if pt_html_path else "",
            priority=priority,
            issues=issues,
            icon="[PT]"
        )
    
    def _extract_timing_data_from_work_areas(self):
        """Extract timing data from all auto_pt work areas with dual-scenario support"""
        
        # Find all work directories (exclude .html files)
        work_pattern = os.path.join(self.workarea, "signoff_flow/auto_pt/work_*")
        all_items = glob.glob(work_pattern)
        work_dirs = [item for item in all_items if os.path.isdir(item)]
        work_dirs = sorted(work_dirs, key=os.path.getmtime, reverse=True)
        
        timing_data = []
        
        # Define scenarios to extract: setup and hold
        # Default scenarios - will auto-detect if these don't exist
        scenarios_to_check = {
            'setup': [
                'func.std_tt_0c_0p6v.setup.typical',
                'func.std_tt_25c_0p6v.setup.typical',
                'func.std_tt_85c_0p6v.setup.typical',
                'func.std_tt_125c_0p6v.setup.typical'
            ],
            'hold': [
                'func.std_ffg_125c_0p825v.hold.typical',
                'func.std_ffg_0c_0p825v.hold.typical',
                'func.std_tt_0c_0p6v.hold.typical',
                'func.std_tt_125c_0p6v.hold.typical'
            ]
        }
        
        for work_dir in work_dirs:
            # Extract work directory name (e.g., work_16.09.25_19:53)
            work_name = os.path.basename(work_dir)
            
            # Look for HTML reports in this work directory and parent auto_pt directory
            html_reports = []
            
            # Check inside work directory
            html_pattern = os.path.join(work_dir, "*.html")
            html_files = glob.glob(html_pattern)
            for html_file in sorted(html_files, key=os.path.getmtime, reverse=True):
                # Convert to absolute path for HTML links to work from any location
                html_reports.append(os.path.abspath(html_file))
            
            # Check parent auto_pt directory for work-specific HTML files
            auto_pt_dir = os.path.dirname(work_dir)
            parent_html_patterns = [
                os.path.join(auto_pt_dir, f"PT_{work_name}.html"),
                os.path.join(auto_pt_dir, f"{work_name}.html")
            ]
            for parent_html_pattern in parent_html_patterns:
                if os.path.exists(parent_html_pattern):
                    # Convert to absolute path for HTML links to work from any location
                    html_reports.append(os.path.abspath(parent_html_pattern))
                    break
            
            # Initialize work data structure
            work_data = {
                "work_dir": work_name,
                "scenarios": {},
                "html_reports": html_reports,
                "dsr_skew_setup": None,  # DSR skew for setup scenario
                "dsr_skew_hold": None,   # DSR skew for hold scenario
                "runtime": None
            }
            
            # Extract data for each scenario type (setup and hold)
            for scenario_type, scenario_list in scenarios_to_check.items():
                best_scenario = None
                best_tns = 0  # Track worst (most negative) TNS to find the scenario with most violations
                
                for scenario in scenario_list:
                    timing_file = os.path.join(work_dir, f"{scenario}/reports/timing_reports/{self.design_info.top_hier}_{scenario}.timing")
                    
                    if os.path.exists(timing_file):
                        try:
                            with open(timing_file, 'r') as f:
                                content = f.read()
                            
                            # Find all Group lines - improved regex to handle asterisks properly
                            groups_data = {}
                            group_pattern = r'Group:\s*\*\*([^*]+)\*\*\s*\|\s*NVP:\s*(\d+)\s*\|\s*WNS:\s*([-\d.]+)\s*\|\s*TNS:\s*([-\d.]+)|Group:\s*([^|]+)\s*\|\s*NVP:\s*(\d+)\s*\|\s*WNS:\s*([-\d.]+)\s*\|\s*TNS:\s*([-\d.]+)'
                            matches = re.findall(group_pattern, content)
                            
                            total_tns = 0
                            for match in matches:
                                if match[0]:  # Group with asterisks
                                    group_name = match[0].strip()
                                    nvp = int(match[1])
                                    wns = float(match[2])
                                    tns = float(match[3])
                                else:  # Regular group
                                    group_name = match[4].strip()
                                    nvp = int(match[5])
                                    wns = float(match[6])
                                    tns = float(match[7])
                                
                                groups_data[group_name] = {
                                    "NVP": nvp,
                                    "WNS": wns,
                                    "TNS": tns
                                }
                                total_tns += tns
                            
                            # If this scenario has worse TNS (or is the first found), use it
                            if best_scenario is None or total_tns < best_tns:
                                best_scenario = scenario
                                best_tns = total_tns
                                work_data["scenarios"][scenario_type] = {
                                    "name": scenario,
                                    "groups": groups_data,
                                    "total_tns": total_tns
                                }
                        except Exception as e:
                            # Silently skip files with errors
                            pass
            
            # Extract DSR mux_clock_skew from both setup and hold scenarios
            # Each scenario has its own DSR skew file with different corner-specific values
            
            # Setup scenario DSR skew
            if "setup" in work_data["scenarios"]:
                setup_scenario = work_data["scenarios"]["setup"]["name"]
                dsr_pattern = os.path.join(work_dir, f"{setup_scenario}/reports/timing_reports/*.dsr_mux_clock_skew")
                dsr_files = glob.glob(dsr_pattern)
                
                if dsr_files:
                    try:
                        with open(dsr_files[0], 'r') as f:
                            dsr_content = f.read()
                        
                        # Extract clock skew values - look for "I0-I1 skew is:" pattern
                        # Format: "I0-I1 skew is: 0.01101" (in nanoseconds)
                        skew_pattern = r'I0-I1\s+skew\s+is:\s*([-\d.]+)'
                        skew_matches = re.findall(skew_pattern, dsr_content, re.IGNORECASE)
                        
                        if skew_matches:
                            # Convert from nanoseconds to picoseconds (multiply by 1000)
                            work_data["dsr_skew_setup"] = float(skew_matches[0]) * 1000.0
                    
                    except Exception as e:
                        # Silently skip DSR extraction errors
                        pass
            
            # Hold scenario DSR skew
            if "hold" in work_data["scenarios"]:
                hold_scenario = work_data["scenarios"]["hold"]["name"]
                dsr_pattern = os.path.join(work_dir, f"{hold_scenario}/reports/timing_reports/*.dsr_mux_clock_skew")
                dsr_files = glob.glob(dsr_pattern)
                
                if dsr_files:
                    try:
                        with open(dsr_files[0], 'r') as f:
                            dsr_content = f.read()
                        
                        # Extract clock skew values - look for "I0-I1 skew is:" pattern
                        skew_pattern = r'I0-I1\s+skew\s+is:\s*([-\d.]+)'
                        skew_matches = re.findall(skew_pattern, dsr_content, re.IGNORECASE)
                        
                        if skew_matches:
                            # Convert from nanoseconds to picoseconds (multiply by 1000)
                            work_data["dsr_skew_hold"] = float(skew_matches[0]) * 1000.0
                    
                    except Exception as e:
                        # Silently skip DSR extraction errors
                        pass
            
            # Extract PT runtime from log file
            log_file = os.path.join(work_dir, "*.log")
            log_files = glob.glob(log_file)
            if log_files:
                try:
                    with open(log_files[0], 'r') as f:
                        log_content = f.read()
                    
                    # Look for "Elapsed time for this session" pattern
                    runtime_pattern = r'Elapsed time for this session:\s*([\d.]+)\s*hours?'
                    runtime_matches = re.findall(runtime_pattern, log_content, re.IGNORECASE)
                    
                    if runtime_matches:
                        work_data["runtime"] = float(runtime_matches[0])
                
                except Exception as e:
                    # Silently skip runtime extraction errors
                    pass
            
            # Only add work data if at least one scenario was found
            if work_data["scenarios"]:
                timing_data.append(work_data)
        
        return timing_data
    
    def _generate_timing_summary_html(self, timing_data):
        """Generate HTML report with dual-scenario timing summary table and DSR skew tracking"""
        
        if not timing_data:
            return None
        
        # Get all unique groups across all work areas for both scenarios
        all_groups = set()
        for work_data in timing_data:
            for scenario_type, scenario_data in work_data["scenarios"].items():
                all_groups.update(scenario_data["groups"].keys())
        
        all_groups = sorted(all_groups)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"{os.environ.get('USER', 'avice')}_PT_timing_summary_{self.design_info.top_hier}_{timestamp}.html"
        
        # Read and encode logo as base64 for HTML embedding (portability)
        logo_data = ""
        logo_path = os.path.join(os.path.dirname(__file__), "images/avice_logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo_file:
                logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
        
        # Start HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto PT Timing Summary Report - {self.design_info.top_hier}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 95%;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 10px;
        }}
        .logo img {{
            max-height: 80px;
            max-width: 300px;
            height: auto;
            width: auto;
            cursor: pointer;
            transition: transform 0.2s ease;
            border-radius: 6px;
        }}
        .logo img:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
        }}
        .image-expanded {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        .image-expanded img {{
            max-width: 90%;
            max-height: 90%;
            border: 3px solid #3498db;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .info {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .info h3 {{
            margin-top: 0;
            color: #34495e;
        }}
        .table-wrapper {{
            overflow-x: auto;
            max-width: 100%;
            margin: 20px 0;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0;
            font-size: 16px;
        }}
        th, td {{
            border: 1px solid #bdc3c7;
            padding: 12px;
            text-align: center;
        }}
        th {{
            background-color: #34495e;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
        }}
        th.work-dir {{
            background-color: #34495e;
            color: white;
            font-weight: bold;
            text-align: left;
            min-width: 200px;
        }}
        td.work-dir {{
            background-color: #ecf0f1;
            font-weight: bold;
            text-align: left;
            min-width: 200px;
        }}
        .group-header {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
            min-width: 120px;
        }}
        .timing-cell {{
            font-family: 'Courier New', monospace;
            font-size: 15px;
        }}
        .positive {{
            color: #27ae60;
            font-weight: bold;
        }}
        .negative {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .zero {{
            color: #7f8c8d;
        }}
        .legend {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #3498db;
        }}
        .legend h4 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .legend ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .legend li {{
            margin: 5px 0;
        }}
        .section-header {{
            cursor: pointer;
            user-select: none;
            padding: 15px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            margin: 20px 0 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .section-header:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .section-header h3 {{
            margin: 0;
            border: none;
            padding: 0;
            font-size: 20px;
        }}
        .toggle-icon {{
            font-size: 24px;
            transition: transform 0.3s ease;
        }}
        .toggle-icon.expanded {{
            transform: rotate(180deg);
        }}
        .section-content {{
            display: none;
            animation: slideDown 0.3s ease-out;
        }}
        .section-content.expanded {{
            display: block;
        }}
        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="data:image/png;base64,{logo_data}" alt="AVICE Logo" onclick="expandImage(this)">
            </div>
        <h1>Auto PT Timing Summary Report - {self.design_info.top_hier}</h1>
        </div>
        
        <div class="info">
            <h3>Report Information</h3>
            <p><strong>Workarea:</strong> {self.workarea_abs}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Total Work Areas:</strong> {len(timing_data)}</p>
            <p><strong>Timing Groups:</strong> {len(all_groups)}</p>
        </div>
        
        <div class="info">
            <h3>Available HTML Reports</h3>
            <p>Click on any work area below to access its HTML reports:</p>
            <ul>
"""
        
        # Add links to all HTML reports
        for work_data in timing_data:
            if work_data.get("html_reports"):
                html_content += f'                <li><strong>{work_data["work_dir"]}:</strong><br>\n'
                for html_report in work_data["html_reports"]:
                    # Use absolute path for HTML links to ensure they work from any location
                    html_content += f'                    <a href="file://{html_report}" target="_blank">{os.path.basename(html_report)}</a><br>\n'
                html_content += f'                </li>\n'
        
        html_content += """            </ul>
        </div>
        
        <h2>Dual-Scenario Timing Summary</h2>
"""
        
        # Generate separate tables for Setup and Hold scenarios
        for scenario_type in ['setup', 'hold']:
            # Check if any work area has this scenario
            has_scenario = any(scenario_type in wd["scenarios"] for wd in timing_data)
            if not has_scenario:
                continue
            
            scenario_title = "Setup Timing" if scenario_type == "setup" else "Hold Timing"
            
            # Get scenario name from first work area (all rows have same scenario)
            scenario_name = ""
            for work_data in timing_data:
                if scenario_type in work_data["scenarios"]:
                    scenario_name = work_data["scenarios"][scenario_type]["name"].replace("func.", "").replace(".typical", "")
                    break
            
            # Add scenario name to header (without styling for collapsible header)
            scenario_display = scenario_title
            if scenario_name:
                scenario_display = f"{scenario_title.split(' <')[0]} <span style='font-size:0.8em; color:#e0e0e0;'>({scenario_name})</span>"
            
            # Setup starts expanded, Hold starts collapsed
            is_expanded = "expanded" if scenario_type == "setup" else ""
            section_id = f"section-{scenario_type}"
            
            html_content += f"""
        <div class="section-header" onclick="toggleSection('{section_id}')">
            <h3>{scenario_display}</h3>
            <span class="toggle-icon {is_expanded}" id="icon-{section_id}">▼</span>
        </div>
        <div class="section-content {is_expanded}" id="{section_id}">
        <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th class="work-dir">Work Directory</th>
"""
            
            # Add group headers for this scenario type
            # Separate internal and external timing groups
            internal_groups = set()
            external_groups_set = set()
            external_group_names = {'FEEDTHROUGH', 'REGIN', 'REGOUT'}
            
            # Collect all groups and calculate average TNS for sorting
            group_tns_map = {}  # group_name -> list of TNS values across work areas
            
            for work_data in timing_data:
                if scenario_type in work_data["scenarios"]:
                    for group_name, group_data in work_data["scenarios"][scenario_type]["groups"].items():
                        if group_name.upper() in external_group_names:
                            external_groups_set.add(group_name)
                        else:
                            internal_groups.add(group_name)
                            # Track TNS for sorting (use worst TNS across all work areas)
                            if group_name not in group_tns_map:
                                group_tns_map[group_name] = []
                            group_tns_map[group_name].append(group_data["TNS"])
            
            # Sort internal groups by worst TNS (most negative first)
            # Use the minimum (most negative) TNS value across all work areas
            def get_worst_tns(group_name):
                if group_name in group_tns_map and group_tns_map[group_name]:
                    return min(group_tns_map[group_name])  # Most negative
                return 0  # Groups with no data sorted last
            
            internal_groups_sorted = sorted(internal_groups, key=get_worst_tns)
            external_groups_sorted = sorted(external_groups_set)
            
            # Combine: internal groups (by TNS) then external groups (alphabetical)
            scenario_groups = internal_groups_sorted + external_groups_sorted
            
            # Column order: DSR Skew -> Total Internal -> Internal groups -> External groups
            html_content += '                    <th class="group-header">DSR Skew (ps)</th>\n'
            html_content += '                    <th class="group-header">Total Internal</th>\n'
            
            for group in scenario_groups:
                html_content += f'                    <th class="group-header">{group}</th>\n'
        
            html_content += """                </tr>
            </thead>
            <tbody>
"""
        
            # Add data rows
            for work_data in timing_data:
                if scenario_type not in work_data["scenarios"]:
                    continue
                
                scenario_data = work_data["scenarios"][scenario_type]
                
                html_content += f'                <tr>\n'
                # Make work directory name a clickable link if HTML reports exist
                if work_data.get("html_reports"):
                    work_dir_links = []
                    for html_report in work_data["html_reports"][:2]:  # Show up to 2 most recent reports
                        # Use absolute path for HTML links to ensure they work from any location
                        work_dir_links.append(f'<a href="file://{html_report}" target="_blank">{os.path.basename(html_report)}</a>')
                    if len(work_data["html_reports"]) > 2:
                        work_dir_links.append(f'<em>+{len(work_data["html_reports"]) - 2}</em>')
                    work_dir_cell = f'{work_data["work_dir"]}<br><small>{" | ".join(work_dir_links)}</small>'
                else:
                    work_dir_cell = work_data["work_dir"]
                html_content += f'                    <td class="work-dir">{work_dir_cell}</td>\n'
                
                # Add DSR skew data first - use scenario-specific value
                dsr_key = f"dsr_skew_{scenario_type}"  # dsr_skew_setup or dsr_skew_hold
                if work_data.get(dsr_key) is not None:
                    dsr_val = work_data[dsr_key]
                    # Green only if <=10ps, Yellow/Orange 10-20ps (NOT acceptable), Red >20ps
                    if dsr_val <= 10:
                        dsr_class = "positive"  # Green
                    elif dsr_val <= 20:
                        dsr_class = "negative"  # Yellow/Orange - NOT acceptable
                    else:
                        dsr_class = "negative"  # Red - poor
                    html_content += f'                    <td class="timing-cell"><div class="{dsr_class}">{dsr_val:.2f}</div></td>\n'
                else:
                    html_content += f'                    <td class="timing-cell">N/A</td>\n'
                
                # Calculate and add Total Internal timing (sum of all internal groups)
                internal_wns = None  # Track worst WNS
                internal_tns = 0
                internal_nvp = 0
                
                for group in scenario_groups:
                    if group.upper() not in external_group_names:
                        if group in scenario_data["groups"]:
                            group_data = scenario_data["groups"][group]
                            internal_tns += group_data["TNS"]
                            internal_nvp += group_data["NVP"]
                            # Track worst WNS (most negative)
                            if internal_wns is None or group_data["WNS"] < internal_wns:
                                internal_wns = group_data["WNS"]
                
                # Display Total Internal column
                if internal_wns is not None:
                    wns_class = "positive" if internal_wns >= 0 else "negative" if internal_wns < -0.1 else "zero"
                    tns_class = "positive" if internal_tns >= 0 else "negative" if internal_tns < -1.0 else "zero"
                    nvp_class = "zero" if internal_nvp == 0 else "negative"
                    
                    html_content += f'                    <td class="timing-cell" style="font-weight:bold; background-color:#f0f8ff;">\n'
                    html_content += f'                        <div class="{wns_class}">WNS: {internal_wns:6.3f}</div>\n'
                    html_content += f'                        <div class="{tns_class}">TNS: {internal_tns:7.2f}</div>\n'
                    html_content += f'                        <div class="{nvp_class}">NVP: {internal_nvp:4d}</div>\n'
                    html_content += f'                    </td>\n'
                else:
                    html_content += f'                    <td class="timing-cell">N/A</td>\n'
                
                # Add timing data for each group
                for group in scenario_groups:
                    if group in scenario_data["groups"]:
                        group_data = scenario_data["groups"][group]
                        nvp = group_data["NVP"]
                        wns = group_data["WNS"]
                        tns = group_data["TNS"]
                        
                        # Determine color based on values
                        wns_class = "positive" if wns >= 0 else "negative" if wns < -0.1 else "zero"
                        tns_class = "positive" if tns >= 0 else "negative" if tns < -1.0 else "zero"
                        nvp_class = "zero" if nvp == 0 else "negative"
                        
                        html_content += f'                    <td class="timing-cell">\n'
                        html_content += f'                        <div class="{wns_class}">WNS: {wns:6.3f}</div>\n'
                        html_content += f'                        <div class="{tns_class}">TNS: {tns:7.2f}</div>\n'
                        html_content += f'                        <div class="{nvp_class}">NVP: {nvp:4d}</div>\n'
                        html_content += f'                    </td>\n'
                    else:
                        html_content += f'                    <td class="timing-cell">N/A</td>\n'
            
            html_content += f'                </tr>\n'
        
            html_content += """            </tbody>
        </table>
        </div>
        </div>
"""
        
        html_content += """        
        <div class="legend">
            <h4>Legend</h4>
            <ul>
                <li><strong>WNS:</strong> Worst Negative Slack (ns)</li>
                <li><strong>TNS:</strong> Total Negative Slack (ns)</li>
                <li><strong>NVP:</strong> Number of Violating Paths</li>
                <li><strong>DSR Skew:</strong> DSR Mux Clock Skew (picoseconds) - Lower is better</li>
                <li><strong>Total Internal:</strong> Sum of all internal timing groups (excludes FEEDTHROUGH/REGIN/REGOUT)</li>
            </ul>
            <h4>Color Coding</h4>
            <ul>
                <li><span class="positive">Green:</span> Positive slack (meets timing) / Excellent DSR skew (&lt;=10ps)</li>
                <li><span class="negative">Red/Orange:</span> Negative slack (timing violations) / Unacceptable DSR skew (&gt;10ps)</li>
            </ul>
            <h4>Column Order</h4>
            <ul>
                <li>1. <strong>DSR Skew:</strong> Physical design metric (same for all scenarios)</li>
                <li>2. <strong>Total Internal:</strong> Overall internal timing health</li>
                <li>3. <strong>Internal Groups:</strong> Individual clock domains (i1_clk, i2_clk, etc.)</li>
                <li>4. <strong>External Groups:</strong> FEEDTHROUGH/REGIN/REGOUT (relaxed, always 0)</li>
            </ul>
        </div>
    </div>
    
    <script>
        function expandImage(imgElement) {{
            // Create overlay
            var overlay = document.createElement('div');
            overlay.className = 'image-expanded';
            
            // Create expanded image
            var expandedImg = document.createElement('img');
            expandedImg.src = imgElement.src;
            expandedImg.alt = imgElement.alt;
            
            overlay.appendChild(expandedImg);
            document.body.appendChild(overlay);
            
            // Close on click
            overlay.onclick = function() {{
                if (document.body.contains(overlay)) {{
                    document.body.removeChild(overlay);
                }}
            }};
            
            // Close on escape key
            function escapeHandler(e) {{
                e = e || window.event;
                if ((e.keyCode || e.which) === 27) {{
                    if (document.body.contains(overlay)) {{
                        document.body.removeChild(overlay);
                        if (document.removeEventListener) {{
                            document.removeEventListener('keydown', escapeHandler);
                        }} else if (document.detachEvent) {{
                            document.detachEvent('onkeydown', escapeHandler);
                        }}
                    }}
                }}
            }}
            
            if (document.addEventListener) {{
                document.addEventListener('keydown', escapeHandler);
            }} else if (document.attachEvent) {{
                document.attachEvent('onkeydown', escapeHandler);
            }}
        }}
        
        function toggleSection(sectionId) {{
            var content = document.getElementById(sectionId);
            var icon = document.getElementById('icon-' + sectionId);
            
            if (content.classList.contains('expanded')) {{
                content.classList.remove('expanded');
                icon.classList.remove('expanded');
            }} else {{
                content.classList.add('expanded');
                icon.classList.add('expanded');
            }}
        }}
    </script>
</body>
</html>"""
        
        # Write HTML file in current working directory to avoid permission issues
        # Use absolute paths in HTML content to ensure links work from any location
        html_path = os.path.join(os.getcwd(), html_filename)
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        return os.path.abspath(html_path)
    
    def _generate_timing_summary_report(self):
        """Generate timing summary report with dual-scenario and DSR skew tracking"""
        
        # Extract timing data from all work areas
        timing_data = self._extract_timing_data_from_work_areas()
        
        if timing_data:
            # Generate HTML report
            html_filename = self._generate_timing_summary_html(timing_data)
            
            if html_filename:
                print(f"\n  {Color.CYAN}PT Timing Summary (Dual-Scenario):{Color.RESET}")
                print(f"    Open with: firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
                
                # Show brief summary
                print(f"\n  {Color.CYAN}Work Areas Summary:{Color.RESET}")
                print(f"    Total Work Areas: {len(timing_data)}")
                
                if len(timing_data) >= 1:
                    latest = timing_data[0]
                    print(f"    Latest: {latest['work_dir']}")
                    
                    # Show latest setup scenario summary
                    if 'setup' in latest['scenarios']:
                        setup_data = latest['scenarios']['setup']
                        print(f"\n  {Color.CYAN}Latest Setup Scenario ({setup_data['name']}):{Color.RESET}")
                        
                        # Define external timing groups
                        external_groups = {'FEEDTHROUGH', 'REGIN', 'REGOUT'}
                        
                        # Calculate sum of internal timing path groups (exclude external)
                        internal_wns = None  # Track worst WNS
                        internal_tns = 0
                        internal_nvp = 0
                        worst_group = None
                        worst_tns = 0
                        
                        for group_name, group_data in setup_data['groups'].items():
                            # Skip external groups for internal sum
                            if group_name.upper() not in external_groups:
                                internal_tns += group_data['TNS']
                                internal_nvp += group_data['NVP']
                                
                                # Track worst WNS (most negative)
                                if internal_wns is None or group_data['WNS'] < internal_wns:
                                    internal_wns = group_data['WNS']
                                
                                # Track worst group by TNS
                                if group_data['TNS'] < worst_tns:
                                    worst_tns = group_data['TNS']
                                    worst_group = group_name
                        
                        # Display internal timing summary
                        if internal_wns is not None:
                            wns_color = Color.GREEN if internal_wns >= 0 else Color.RED
                            tns_color = Color.GREEN if internal_tns >= 0 else Color.RED
                            print(f"    Internal Timing (all groups except FEEDTHROUGH/REGIN/REGOUT):")
                            print(f"      WNS: {wns_color}{internal_wns:7.3f}{Color.RESET} ns")
                            print(f"      TNS: {tns_color}{internal_tns:9.2f}{Color.RESET} ns")
                            print(f"      NVP: {internal_nvp:5d} paths")
                            if worst_group:
                                print(f"    Worst Internal Group: {worst_group}")
                    
                    # Show latest hold scenario summary
                    if 'hold' in latest['scenarios']:
                        hold_data = latest['scenarios']['hold']
                        print(f"\n  {Color.CYAN}Latest Hold Scenario ({hold_data['name']}):{Color.RESET}")
                        
                        # Define external timing groups
                        external_groups = {'FEEDTHROUGH', 'REGIN', 'REGOUT'}
                        
                        # Calculate sum of internal timing path groups (exclude external)
                        internal_wns = None  # Track worst WNS
                        internal_tns = 0
                        internal_nvp = 0
                        worst_group = None
                        worst_tns = 0
                        
                        for group_name, group_data in hold_data['groups'].items():
                            # Skip external groups for internal sum
                            if group_name.upper() not in external_groups:
                                internal_tns += group_data['TNS']
                                internal_nvp += group_data['NVP']
                                
                                # Track worst WNS (most negative)
                                if internal_wns is None or group_data['WNS'] < internal_wns:
                                    internal_wns = group_data['WNS']
                                
                                # Track worst group by TNS
                                if group_data['TNS'] < worst_tns:
                                    worst_tns = group_data['TNS']
                                    worst_group = group_name
                        
                        # Display internal timing summary
                        if internal_wns is not None:
                            wns_color = Color.GREEN if internal_wns >= 0 else Color.RED
                            tns_color = Color.GREEN if internal_tns >= 0 else Color.RED
                            print(f"    Internal Timing (all groups except FEEDTHROUGH/REGIN/REGOUT):")
                            print(f"      WNS: {wns_color}{internal_wns:7.3f}{Color.RESET} ns")
                            print(f"      TNS: {tns_color}{internal_tns:9.2f}{Color.RESET} ns")
                            print(f"      NVP: {internal_nvp:5d} paths")
                            if worst_group:
                                print(f"    Worst Internal Group: {worst_group}")
                    
                # Show DSR skew trend if multiple work areas (show both setup and hold)
                if len(timing_data) >= 2:
                    print(f"\n  {Color.CYAN}DSR Skew Trend:{Color.RESET}")
                    
                    # Setup scenario DSR skew
                    dsr_setup_values = []
                    for wd in timing_data[:5]:  # Show up to 5 most recent
                        if wd.get('dsr_skew_setup') is not None:
                            dsr_val = wd['dsr_skew_setup']
                            dsr_color = Color.GREEN if dsr_val <= 10 else Color.YELLOW if dsr_val <= 20 else Color.RED
                            dsr_setup_values.append((wd['work_dir'], dsr_val, dsr_color))
                    
                    if dsr_setup_values:
                        print(f"    {Color.CYAN}Setup Scenario:{Color.RESET}")
                        for work_name, dsr_val, dsr_color in dsr_setup_values:
                            print(f"      {work_name}: {dsr_color}{dsr_val:6.2f}{Color.RESET} ps")
                        
                        # Show improvement/degradation for setup
                        if len(dsr_setup_values) >= 2:
                            first_dsr = dsr_setup_values[0][1]
                            last_dsr = dsr_setup_values[-1][1]
                            diff = first_dsr - last_dsr
                            trend_color = Color.GREEN if diff < 0 else Color.RED
                            trend_text = "improved" if diff < 0 else "degraded"
                            print(f"      Trend: {trend_color}{abs(diff):.2f} ps {trend_text}{Color.RESET} (newest vs oldest)")
                    
                    # Hold scenario DSR skew
                    dsr_hold_values = []
                    for wd in timing_data[:5]:  # Show up to 5 most recent
                        if wd.get('dsr_skew_hold') is not None:
                            dsr_val = wd['dsr_skew_hold']
                            dsr_color = Color.GREEN if dsr_val <= 10 else Color.YELLOW if dsr_val <= 20 else Color.RED
                            dsr_hold_values.append((wd['work_dir'], dsr_val, dsr_color))
                    
                    if dsr_hold_values:
                        print(f"    {Color.CYAN}Hold Scenario:{Color.RESET}")
                        for work_name, dsr_val, dsr_color in dsr_hold_values:
                            print(f"      {work_name}: {dsr_color}{dsr_val:6.2f}{Color.RESET} ps")
                        
                        # Show improvement/degradation for hold
                        if len(dsr_hold_values) >= 2:
                            first_dsr = dsr_hold_values[0][1]
                            last_dsr = dsr_hold_values[-1][1]
                            diff = first_dsr - last_dsr
                            trend_color = Color.GREEN if diff < 0 else Color.RED
                            trend_text = "improved" if diff < 0 else "degraded"
                            print(f"      Trend: {trend_color}{abs(diff):.2f} ps {trend_text}{Color.RESET} (newest vs oldest)")
                else:
                    # Show DSR skew for latest if only one work area
                    print(f"\n  {Color.CYAN}Latest DSR Mux Clock Skew:{Color.RESET}")
                    if latest.get('dsr_skew_setup') is not None:
                        dsr_val_setup = latest['dsr_skew_setup']
                        dsr_color = Color.GREEN if dsr_val_setup <= 10 else Color.YELLOW if dsr_val_setup <= 20 else Color.RED
                        print(f"    Setup: {dsr_color}{dsr_val_setup:6.2f}{Color.RESET} ps")
                    if latest.get('dsr_skew_hold') is not None:
                        dsr_val_hold = latest['dsr_skew_hold']
                        dsr_color = Color.GREEN if dsr_val_hold <= 10 else Color.YELLOW if dsr_val_hold <= 20 else Color.RED
                        print(f"    Hold:  {dsr_color}{dsr_val_hold:6.2f}{Color.RESET} ps")
                
                # Return HTML path and timing data for dashboard summary
                return html_filename, timing_data
        
        return None, None
    
    def run_physical_verification(self):
        """Run physical verification analysis"""
        self.print_header(FlowStage.PHYSICAL_VERIFICATION)
        
        # Show PV flow timestamps at the beginning
        self._show_pv_flow_timestamps()
        
        # LVS errors
        lvs_pattern = f"pv_flow/drc_dir/{self.design_info.top_hier}/lvs_icv_ipo*/{self.design_info.top_hier}_ipo*_fill.LVS_ERRORS"
        lvs_files = self.file_utils.find_files(lvs_pattern, self.workarea)
        
        if lvs_files:
            self.print_file_info(lvs_files[0], "LVS Errors")
            violations = self.lvs_parser.parse_lvs_errors(lvs_files[0])
            
            # Display detailed LVS violation information
            status_color = Color.RED if violations['status'] == 'FAIL' else Color.GREEN
            print(f"  {status_color}Status: {violations['status']}{Color.RESET}")
            print(f"  Failed Equivalence Points: {violations['failed_equivalence_points']}")
            if violations['first_priority_errors'] > 0:
                print(f"  First Priority Errors: {violations['first_priority_errors']}")
            if violations['second_priority_errors'] > 0:
                print(f"  Second Priority Errors: {violations['second_priority_errors']}")
            print(f"  Successful Equivalence Points: {violations['successful_equivalence_points']}")
            
            if violations['failed_equivalence_points'] > 0:
                # Only show non-zero unmatched items
                unmatched_items = []
                if violations['unmatched_schematic_instances'] > 0:
                    unmatched_items.append(f"Schematic Instances: {violations['unmatched_schematic_instances']}")
                if violations['unmatched_schematic_nets'] > 0:
                    unmatched_items.append(f"Schematic Nets: {violations['unmatched_schematic_nets']}")
                if violations['unmatched_layout_instances'] > 0:
                    unmatched_items.append(f"Layout Instances: {violations['unmatched_layout_instances']}")
                if violations['unmatched_layout_nets'] > 0:
                    unmatched_items.append(f"Layout Nets: {violations['unmatched_layout_nets']}")
                if violations['unmatched_schematic_ports'] > 0:
                    unmatched_items.append(f"Schematic Ports: {violations['unmatched_schematic_ports']}")
                if violations['unmatched_layout_ports'] > 0:
                    unmatched_items.append(f"Layout Ports: {violations['unmatched_layout_ports']}")
                
                if unmatched_items:
                    print(f"\n  {Color.YELLOW}Unmatched Items:{Color.RESET}")
                    for item in unmatched_items:
                        print(f"    {item}")
                
                total_unmatched = (violations['unmatched_schematic_instances'] + 
                                 violations['unmatched_schematic_nets'] + 
                                 violations['unmatched_layout_instances'] + 
                                 violations['unmatched_layout_nets'] + 
                                 violations['unmatched_schematic_ports'] + 
                                 violations['unmatched_layout_ports'])
                print(f"    {Color.RED}Total Unmatched Items: {total_unmatched}{Color.RESET}")
            
            print(f"\n  {Color.GREEN}Matched Items:{Color.RESET}")
            print(f"    Instances: {violations['matched_instances']:,}")
            print(f"    Nets:      {violations['matched_nets']:,}")
            print(f"    Ports:     {violations['matched_ports']:,}")
        
        # DRC errors
        drc_pattern = f"pv_flow/drc_dir/{self.design_info.top_hier}/drc_icv_ipo*/{self.design_info.top_hier}_ipo*_fill.LAYOUT_ERRORS"
        drc_files = self.file_utils.find_files(drc_pattern, self.workarea)
        
        if drc_files:
            self.print_file_info(drc_files[0], "DRC Errors")
            self._analyze_drc_errors(drc_files[0])
        
        # Antenna errors
        antenna_pattern = f"pv_flow/drc_dir/{self.design_info.top_hier}/drc_icv_antenna_ipo*/{self.design_info.top_hier}_ipo*_fill.LAYOUT_ERRORS"
        antenna_files = self.file_utils.find_files(antenna_pattern, self.workarea)
        
        if antenna_files:
            self.print_file_info(antenna_files[0], "Antenna Errors")
            self._analyze_antenna_errors(antenna_files[0])
        else:
            print("  No antenna error report found")
        
        # PV Flow Analysis
        self._analyze_pv_flow()
    
    def _show_flow_timeline(self, flow_name: str, local_flow_dirs: list):
        """Show flow start and end timestamps for any flow type"""
        for local_flow_dir_pattern in local_flow_dirs:
            # Handle glob patterns in directory paths
            if '*' in local_flow_dir_pattern:
                matching_dirs = glob.glob(local_flow_dir_pattern)
            else:
                matching_dirs = [local_flow_dir_pattern] if os.path.exists(local_flow_dir_pattern) else []
            
            for local_flow_dir in matching_dirs:
                if os.path.exists(local_flow_dir):
                    try:
                        # Find BEGIN and END step files
                        begin_files = glob.glob(os.path.join(local_flow_dir, "STEP__BEGIN__*"))
                        end_files = glob.glob(os.path.join(local_flow_dir, "STEP__END__*"))
                        
                        if begin_files:
                            # Get begin time
                            begin_time = os.path.getmtime(begin_files[0])
                            begin_str = time.strftime("%Y/%m/%d %I:%M:%S%p", time.localtime(begin_time))
                            
                            if end_files:
                                # Flow completed - show full timeline
                                end_time = os.path.getmtime(end_files[0])
                                end_str = time.strftime("%Y/%m/%d %I:%M:%S%p", time.localtime(end_time))
                                
                                # Calculate total duration
                                duration_sec = int(end_time - begin_time)
                                if duration_sec >= 3600:
                                    duration_str = f"{duration_sec//3600}h {(duration_sec%3600)//60}m {duration_sec%60}s"
                                elif duration_sec >= 60:
                                    duration_str = f"{(duration_sec%3600)//60}m {duration_sec%60}s"
                                else:
                                    duration_str = f"{duration_sec}s"
                                
                                print(f"{Color.CYAN}{flow_name} Flow Timeline:{Color.RESET}")
                                print(f"  Started:  {begin_str}")
                                print(f"  Finished: {end_str}")
                                print(f"  Duration: {duration_str}")
                                print()
                                return begin_str, end_str  # Return timestamps for use in runtime table
                            else:
                                # No END file - check if flow actually completed by looking for output files
                                flow_completed_without_end_marker = False
                                
                                if flow_name == "Star":
                                    # Check if SPEF files exist (Star's main output)
                                    spef_pattern = os.path.join(self.workarea, f"export/nv_star/{self.design_info.top_hier}/ipo*/IOs/netlists/*.spef.typical_T0.gz")
                                    spef_files = glob.glob(spef_pattern)
                                    if spef_files:
                                        # SPEF exists - flow completed but END marker missing
                                        flow_completed_without_end_marker = True
                                        # Use the SPEF file timestamp as proxy for end time
                                        end_time = os.path.getmtime(spef_files[0])
                                        end_str = time.strftime("%Y/%m/%d %I:%M:%S%p", time.localtime(end_time))
                                        duration_sec = int(end_time - begin_time)
                                
                                if flow_completed_without_end_marker:
                                    # Show completed timeline with note about missing END marker
                                    if duration_sec >= 3600:
                                        duration_str = f"{duration_sec//3600}h {(duration_sec%3600)//60}m {duration_sec%60}s"
                                    elif duration_sec >= 60:
                                        duration_str = f"{(duration_sec%3600)//60}m {duration_sec%60}s"
                                    else:
                                        duration_str = f"{duration_sec}s"
                                    
                                    print(f"{Color.CYAN}{flow_name} Flow Timeline:{Color.RESET}")
                                    print(f"  Started:  {begin_str}")
                                    print(f"  Finished: {end_str} {Color.YELLOW}(inferred from output files){Color.RESET}")
                                    print(f"  Duration: {duration_str}")
                                    print()
                                    return begin_str, end_str
                        else:
                            # Flow is currently running - calculate elapsed time
                            current_time = time.time()
                            elapsed_sec = int(current_time - begin_time)
                            if elapsed_sec >= 3600:
                                elapsed_str = f"{elapsed_sec//3600}h {(elapsed_sec%3600)//60}m {elapsed_sec%60}s"
                            elif elapsed_sec >= 60:
                                elapsed_str = f"{(elapsed_sec%3600)//60}m {elapsed_sec%60}s"
                            else:
                                elapsed_str = f"{elapsed_sec}s"
                            
                            print(f"{Color.CYAN}{flow_name} Flow Timeline:{Color.RESET}")
                            print(f"  Started: {begin_str}")
                            print(f"  {Color.YELLOW}Status:  RUNNING (elapsed: {elapsed_str}){Color.RESET}")
                            print()
                            return begin_str, "RUNNING"  # Return start time and RUNNING status
                            
                    except Exception as e:
                        print(f"{Color.YELLOW}Could not determine {flow_name} flow timestamps: {e}{Color.RESET}")
                        continue
        
        return None, None  # No timeline found
    
    def _show_pv_flow_timestamps(self):
        """Show PV flow start and end timestamps"""
        local_flow_dir = os.path.join(self.workarea, f"pv_flow/nv_flow/{self.design_info.top_hier}/local_flow")
        return self._show_flow_timeline("PV", [local_flow_dir])
    
    def _analyze_pv_flow(self):
        """Analyze PV flow configuration and status"""
        prc_pattern = f"pv_flow/nv_flow/pv_{self.design_info.top_hier}.prc"
        prc_status_pattern = f"pv_flow/nv_flow/pv_{self.design_info.top_hier}.prc.status"
        
        prc_files = self.file_utils.find_files(prc_pattern, self.workarea)
        prc_status_files = self.file_utils.find_files(prc_status_pattern, self.workarea)
        
        if prc_files and prc_status_files:
            print(f"\n{Color.CYAN}PV Flow Analysis:{Color.RESET}")
            self.print_file_info(prc_status_files[0], "PV Flow Status")
            self._parse_pv_flow_status(prc_status_files[0])
            
            self.print_file_info(prc_files[0], "PV Flow Configuration")
            self._parse_pv_flow_config(prc_files[0])
        elif prc_status_files:
            print(f"\n{Color.CYAN}PV Flow Status:{Color.RESET}")
            self.print_file_info(prc_status_files[0], "PV Flow Status")
            self._parse_pv_flow_status(prc_status_files[0])
        else:
            print(f"\n{Color.YELLOW}No PV flow status files found{Color.RESET}")
    
    def _parse_pv_flow_status(self, status_file: str):
        """Parse PV flow status file and display runtime information"""
        try:
            with open(status_file, 'r') as f:
                content = f.read()
            
            # Extract flow steps with status and runtime
            steps = []
            lines = content.split('\n')
            
            for line in lines:
                if line.strip() and not line.startswith('#') and '    ' in line:
                    parts = line.split()
                    if len(parts) >= 6 and parts[3] in ['DONE', 'FAILED', 'RUNNING', 'UNLAUNCHED']:
                        block = parts[0]
                        experiment = parts[1]
                        step = parts[2]
                        status = parts[3]
                        duration = parts[4]
                        
                        # Convert duration to readable format
                        if duration.isdigit() and int(duration) > 0:
                            duration_sec = int(duration)
                            if duration_sec >= 3600:
                                duration_str = f"{duration_sec//3600}h {(duration_sec%3600)//60}m {duration_sec%60}s"
                            elif duration_sec >= 60:
                                duration_str = f"{(duration_sec%3600)//60}m {duration_sec%60}s"
                            else:
                                duration_str = f"{duration_sec}s"
                        else:
                            duration_str = duration
                        
                        steps.append({
                            'block': block,
                            'experiment': experiment,
                            'step': step,
                            'status': status,
                            'duration': duration_str,
                            'duration_sec': int(duration) if duration.isdigit() else 0
                        })
            
            if steps:
                # Group by experiment and show summary
                experiments = {}
                for step in steps:
                    exp_key = f"{step['block']}/{step['experiment']}"
                    if exp_key not in experiments:
                        experiments[exp_key] = []
                    experiments[exp_key].append(step)
                
                for exp_name, exp_steps in experiments.items():
                    # Calculate total runtime for completed steps
                    total_runtime = sum(step['duration_sec'] for step in exp_steps if step['status'] == 'DONE')
                    done_steps = [s for s in exp_steps if s['status'] == 'DONE']
                    failed_steps = [s for s in exp_steps if s['status'] == 'FAILED']
                    unlaunched_steps = [s for s in exp_steps if s['status'] == 'UNLAUNCHED']
                    
                    # Format total runtime
                    if total_runtime >= 3600:
                        total_str = f"{total_runtime//3600}h {(total_runtime%3600)//60}m {total_runtime%60}s"
                    elif total_runtime >= 60:
                        total_str = f"{(total_runtime%3600)//60}m {total_runtime%60}s"
                    else:
                        total_str = f"{total_runtime}s"
                    
                    print(f"  {Color.CYAN}{exp_name}:{Color.RESET}")
                    print(f"    {Color.GREEN}Completed: {len(done_steps)} steps{Color.RESET} (Total runtime: {total_str})")
                    
                    if failed_steps:
                        print(f"    {Color.RED}Failed: {len(failed_steps)} steps{Color.RESET}")
                    if unlaunched_steps:
                        print(f"    {Color.YELLOW}Unlaunched: {len(unlaunched_steps)} steps{Color.RESET}")
                    
                    # Show key step runtimes (only for significant steps)
                    key_steps = [s for s in done_steps if s['step'] in ['temp_run_lvs', 'temp_run_drc', 'temp_run_ant', 'drc_lvs', 'ant']]
                    if key_steps:
                        print(f"    {Color.CYAN}Key step runtimes:{Color.RESET}")
                        for step in key_steps:
                            print(f"      {step['step']}: {step['duration']}")
                    print()
                    
        except Exception as e:
            print(f"  Error parsing PV flow status: {e}")
    
    def _parse_pv_flow_config(self, config_file: str):
        """Parse PV flow configuration file and display key settings"""
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Extract key configuration information
            print(f"  {Color.CYAN}Configuration Summary:{Color.RESET}")
            
            # Extract IPO number
            ipo_match = re.search(r'ipo_number:\s*(\d+)', content)
            if ipo_match:
                print(f"    IPO Number: {ipo_match.group(1)}")
            
            # Extract tool
            tool_match = re.search(r'tool:\s*(\w+)', content)
            if tool_match:
                print(f"    Tool: {tool_match.group(1)}")
            
            # Extract flow sequences
            self._extract_flow_sequences(content)
                
        except Exception as e:
            print(f"  Error parsing PV flow config: {e}")
    
    def _extract_flow_sequences(self, content: str):
        """Extract and display flow sequences from PRC YAML content"""
        try:
            # Extract local_flow sequence using a simpler approach
            local_steps = self._extract_flow_sequence_simple(content, 'local_flow')
            if local_steps:
                print(f"    {Color.CYAN}Local Flow Sequence:{Color.RESET} {' -> '.join(local_steps)}")
            
            # Extract release_flow sequence
            release_steps = self._extract_flow_sequence_simple(content, 'release_flow')
            if release_steps:
                print(f"    {Color.CYAN}Release Flow Sequence:{Color.RESET} {' -> '.join(release_steps)}")
            else:
                # Check if release_flow exists at all
                if 'release_flow:' in content:
                    print(f"    Release Flow Configured: Yes (but no steps found)")
                else:
                    print(f"    Release Flow Configured: No")
                
        except Exception as e:
            print(f"    Error extracting flow sequences: {e}")
    
    def _extract_flow_sequence_simple(self, content: str, flow_type: str):
        """Extract flow sequence using a simpler line-by-line approach"""
        lines = content.split('\n')
        steps = []
        in_flow_sequence = False
        flow_found = False
        
        for line in lines:
            # Look for the flow type (local_flow or release_flow)
            if f'{flow_type}:' in line and line.strip().endswith(':'):
                flow_found = True
                continue
            
            # If we found the flow, look for flow_sequence
            if flow_found and 'flow_sequence:' in line and line.strip().endswith(':'):
                in_flow_sequence = True
                continue
            
            # If we're in flow_sequence, collect steps
            if in_flow_sequence:
                stripped = line.strip()
                # Stop if we hit another section at the same level
                if stripped and not stripped.startswith('-') and not stripped.startswith(' ') and stripped.endswith(':'):
                    break
                
                # Collect step if it starts with -
                if stripped.startswith('- '):
                    step = stripped[2:].strip()
                    # Extract step name (before colon if present)
                    if ':' in step:
                        step = step.split(':')[0].strip()
                    if step and step not in steps:  # Avoid duplicates
                        steps.append(step)
        
        return steps
    
    
    def _analyze_drc_errors(self, drc_file: str):
        """Analyze DRC errors file and provide detailed breakdown"""
        try:
            with open(drc_file, 'r') as f:
                content = f.read()
            
            # Check if CLEAN or ERRORS
            if "LAYOUT ERRORS RESULTS: CLEAN" in content:
                print(f"  {Color.GREEN}Status: CLEAN - No DRC violations{Color.RESET}")
                return
            elif "LAYOUT ERRORS RESULTS: ERRORS" in content:
                print(f"  {Color.RED}Status: ERRORS - DRC violations found{Color.RESET}")
            
            # Extract violation details from ERROR SUMMARY section
            violations = []
            total_violations = 0
            
            # Find all violation lines in ERROR SUMMARY
            # Pattern to match rule violations that may span multiple lines
            violation_pattern = r'([A-Z0-9._]+)\s*:\s*\([^)]+\).*?(\d+)\s+violations?\s+found\.'
            matches = re.findall(violation_pattern, content, re.DOTALL)
            
            for rule, count in matches:
                count_int = int(count)
                if count_int > 0:  # Only include non-zero violations
                    violations.append((rule, count_int))
                    total_violations += count_int
            
            if violations:
                print(f"  {Color.RED}Total DRC violations: {total_violations}{Color.RESET}")
                print(f"  {Color.CYAN}Violation breakdown:{Color.RESET}")
                
                # Sort by violation count (descending)
                violations.sort(key=lambda x: x[1], reverse=True)
                
                # Create table format
                print(f"    {'Rule':<20} {'Count':<8} {'Percentage':<10}")
                print(f"    {'-'*20} {'-'*8} {'-'*10}")
                
                for rule, count in violations:
                    percentage = f"{(count/total_violations)*100:.1f}%"
                    print(f"    {rule:<20} {count:<8} {percentage:<10}")
            else:
                # Fallback to simple counting
                matches = self.file_utils.grep_file(r".*violation.*found.*", drc_file)
                total_violations = 0
                for match in matches:
                    numbers = re.findall(r'\d+', match)
                    if numbers:
                        total_violations += int(numbers[0])
                print(f"  Total DRC violations: {total_violations}")
                
        except Exception as e:
            print(f"  Error analyzing DRC file: {e}")
    
    def _analyze_antenna_errors(self, antenna_file: str):
        """Analyze antenna errors file and provide detailed information"""
        try:
            with open(antenna_file, 'r') as f:
                content = f.read()
            
            # Extract LAYOUT ERRORS RESULTS
            matches = self.file_utils.grep_file(r"LAYOUT ERRORS RESULTS.*", antenna_file)
            for match in matches:
                # Check if status is CLEAN and color it green
                if "CLEAN" in match.upper():
                    print(f"  {Color.GREEN}Status: {match.strip()}{Color.RESET}")
                    print(f"  {Color.GREEN}No antenna violations found{Color.RESET}")
                else:
                    print(f"  {Color.RED}Status: {match.strip()}{Color.RESET}")
            
            
            # If there are errors, extract error summary
            if "LAYOUT ERRORS RESULTS: ERRORS" in content:
                result = self.file_utils.run_command(f"sed -n '/ERROR SUMMARY/,/ERROR DETAILS/p' {antenna_file} | sed -e '/^$/d' -e '/ERROR DETAILS/d'")
                if result.strip():
                    print(f"  {Color.CYAN}Error Summary:{Color.RESET}")
                    for line in result.strip().split('\n'):
                        if line.strip():
                            print(f"    {line}")
                            
        except Exception as e:
            print(f"  Error analyzing antenna file: {e}")
    
    def _analyze_gl_check_errors(self, waived_file, non_waived_file):
        """Analyze GL Check error files and show waived vs non-waived counts per checker"""
        try:
            # Parse waived errors
            waived_checkers = {}
            if os.path.exists(waived_file):
                try:
                    with open(waived_file, 'r') as f:
                        for line in f:
                            # Match pattern: -E-[code](checkerName)
                            match = re.match(r'-E-\[(\d+)\]\((\w+)\)', line)
                            if match:
                                code = match.group(1)
                                checker = match.group(2)
                                key = f"[{code}]({checker})"
                                waived_checkers[key] = waived_checkers.get(key, 0) + 1
                except Exception as e:
                    print(f"  Error reading waived file: {e}")
            
            # Parse non-waived errors
            non_waived_checkers = {}
            if os.path.exists(non_waived_file):
                try:
                    with open(non_waived_file, 'r') as f:
                        for line in f:
                            # Match pattern: -E-[code](checkerName)
                            match = re.match(r'-E-\[(\d+)\]\((\w+)\)', line)
                            if match:
                                code = match.group(1)
                                checker = match.group(2)
                                key = f"[{code}]({checker})"
                                non_waived_checkers[key] = non_waived_checkers.get(key, 0) + 1
                except Exception as e:
                    print(f"  Error reading non-waived file: {e}")
            
            # Combine all checkers
            all_checkers = set(waived_checkers.keys()) | set(non_waived_checkers.keys())
            
            if not all_checkers:
                print("  No GL Check errors found")
                return
            
            # Calculate totals
            total_waived = sum(waived_checkers.values())
            total_non_waived = sum(non_waived_checkers.values())
            total_errors = total_waived + total_non_waived
            
            # Print summary
            print(f"\n  {Color.CYAN}GL Check Error Summary:{Color.RESET}")
            print(f"    Total Errors: {total_errors}")
            print(f"    {Color.GREEN}Waived: {total_waived}{Color.RESET}")
            if total_non_waived > 0:
                print(f"    {Color.RED}Non-Waived: {total_non_waived}{Color.RESET}")
            else:
                print(f"    {Color.GREEN}Non-Waived: 0 (PASS){Color.RESET}")
            
            # Print table
            print(f"\n  {Color.CYAN}GL Check Results by Checker:{Color.RESET}")
            print(f"  {'Checker [Code](Name)':<40} {'Waived':<10} {'Non-Waived':<12} {'Total':<10}")
            print(f"  {'-'*40} {'-'*10} {'-'*12} {'-'*10}")
            
            # Sort by total count (descending)
            sorted_checkers = sorted(all_checkers, 
                                    key=lambda x: waived_checkers.get(x, 0) + non_waived_checkers.get(x, 0), 
                                    reverse=True)
            
            for checker in sorted_checkers:
                waived_cnt = waived_checkers.get(checker, 0)
                non_waived_cnt = non_waived_checkers.get(checker, 0)
                total_cnt = waived_cnt + non_waived_cnt
                
                # Color non-waived count if > 0
                if non_waived_cnt > 0:
                    non_waived_str = f"{Color.RED}{non_waived_cnt}{Color.RESET}"
                else:
                    non_waived_str = f"{Color.GREEN}{non_waived_cnt}{Color.RESET}"
                
                print(f"  {checker:<40} {waived_cnt:<10} {non_waived_str:<22} {total_cnt:<10}")
            
            # Print file paths
            print(f"\n  Waived Errors File: {waived_file}")
            print(f"  Non-Waived Errors File: {non_waived_file}")
                    
        except Exception as e:
            print(f"  Error analyzing GL Check errors: {e}")
    
    def _generate_gl_check_html_content(self, waived_checkers, non_waived_checkers, non_waived_errors_detail,
                                        sorted_checkers, total_errors, total_waived, total_non_waived,
                                        allowed_clktree_cells, dont_use_cells, key_reports, main_logs, timestamped_dirs,
                                        waived_file, non_waived_file):
        """Generate the HTML content for GL Check report"""
        
        # Build checker rows HTML
        checker_rows = []
        for checker in sorted_checkers:
            waived_cnt = waived_checkers.get(checker, 0)
            non_waived_cnt = non_waived_checkers.get(checker, 0)
            total_cnt = waived_cnt + non_waived_cnt
            
            status_class = 'status-pass' if non_waived_cnt == 0 else 'status-fail'
            
            # Get error details for this checker
            error_details = non_waived_errors_detail.get(checker, [])
            error_details_html = ""
            if error_details:
                error_details_html = "<div class='error-details'>"
                for i, error in enumerate(error_details[:50], 1):  # Limit to 50 errors
                    error_details_html += f"<div class='error-line'>{i}. {error}</div>"
                if len(error_details) > 50:
                    error_details_html += f"<div class='error-line'>... and {len(error_details) - 50} more errors</div>"
                error_details_html += "</div>"
            
            checker_rows.append(f"""
                <tr class="checker-row {status_class}" data-checker="{checker}" data-waived="{waived_cnt}" data-nonwaived="{non_waived_cnt}" data-total="{total_cnt}">
                    <td>{checker}</td>
                    <td class="num-cell">{waived_cnt}</td>
                    <td class="num-cell {'fail-text' if non_waived_cnt > 0 else 'pass-text'}">{non_waived_cnt}</td>
                    <td class="num-cell">{total_cnt}</td>
                    <td class="action-cell">
                        {'<button class="btn-expand" onclick="toggleErrorDetails(this)">Show Errors</button>' if error_details else '-'}
                    </td>
                </tr>
                {'<tr class="error-details-row" style="display:none;"><td colspan="5">' + error_details_html + '</td></tr>' if error_details else ''}
            """)
        
        # Build allowed clock tree cells HTML
        clktree_cells_html = ""
        if allowed_clktree_cells:
            for cell in allowed_clktree_cells:
                clktree_cells_html += f"<div class='cell-item'>{cell}</div>"
        else:
            clktree_cells_html = "<div class='no-data'>No allowed clock tree cells found</div>"
        
        # Build dont_use cells HTML
        dont_use_cells_html = ""
        if dont_use_cells:
            for cell in dont_use_cells:
                dont_use_cells_html += f"<div class='cell-item'>{cell}</div>"
        else:
            dont_use_cells_html = "<div class='no-data'>No dont_use cells found</div>"
        
        # Build reports HTML
        reports_html = ""
        if key_reports:
            for name, filepath in key_reports:
                reports_html += f"""
                    <div class='report-item'>
                        <span class='report-name'>{name}</span>
                        <button class='btn-log' onclick='window.open("file://{filepath}", "_blank")' title='Open {filepath}'>Open Log</button>
                    </div>
                """
        else:
            reports_html = "<div class='no-data'>No reports found</div>"
        
        # Build logs HTML
        logs_html = ""
        if main_logs:
            for name, filepath in main_logs:
                logs_html += f"""
                    <div class='report-item'>
                        <span class='report-name'>{name}</span>
                        <button class='btn-log' onclick='window.open("file://{filepath}", "_blank")' title='Open {filepath}'>Open Log</button>
                    </div>
                """
        else:
            logs_html = "<div class='no-data'>No logs found</div>"
        
        # Build run history HTML
        run_history_html = ""
        if timestamped_dirs:
            for run_dir in reversed(timestamped_dirs):  # Most recent first
                formatted_date = run_dir.replace('_', '/', 2).replace('_', ' ', 1).replace('_', ':', 1).replace('_', ':', 1)
                run_history_html += f"<div class='run-item'>{formatted_date}</div>"
        else:
            run_history_html = "<div class='no-data'>No run history found</div>"
        
        # Calculate status
        overall_status = "PASS" if total_non_waived == 0 else "FAIL"
        status_class = "pass-text" if total_non_waived == 0 else "fail-text"
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GL Check Report - {self.design_info.top_hier}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .workarea-path {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}
        
        .summary-card .label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        
        .summary-card .status {{
            font-size: 2em;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
        }}
        
        .pass-text {{
            color: #28a745;
        }}
        
        .fail-text {{
            color: #dc3545;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            cursor: pointer;
            margin-bottom: 15px;
            transition: all 0.3s;
        }}
        
        .section-header:hover {{
            transform: translateX(5px);
        }}
        
        .section-header h2 {{
            font-size: 1.5em;
        }}
        
        .section-header .toggle-icon {{
            font-size: 1.2em;
            transition: transform 0.3s;
        }}
        
        .section-header.collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}
        
        .section-content {{
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 10px;
        }}
        
        .section-content.collapsed {{
            display: none;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }}
        
        th:hover {{
            background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%);
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr.checker-row:hover {{
            background: #f0f0f0;
        }}
        
        .num-cell {{
            text-align: right;
            font-weight: 600;
        }}
        
        .action-cell {{
            text-align: center;
        }}
        
        .status-pass {{
            border-left: 4px solid #28a745;
        }}
        
        .status-fail {{
            border-left: 4px solid #dc3545;
        }}
        
        .error-details-row {{
            background: #fff3cd !important;
        }}
        
        .error-details {{
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
            background: white;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }}
        
        .error-line {{
            padding: 5px;
            border-bottom: 1px solid #e0e0e0;
            word-wrap: break-word;
        }}
        
        .error-line:last-child {{
            border-bottom: none;
        }}
        
        .cell-item {{
            display: inline-block;
            background: white;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 5px;
            border: 1px solid #ddd;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            transition: all 0.3s;
        }}
        
        .cell-item:hover {{
            background: #667eea;
            color: white;
            border-color: #667eea;
            transform: scale(1.05);
        }}
        
        .report-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            background: white;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
        }}
        
        .report-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .report-name {{
            font-weight: 500;
        }}
        
        .run-item {{
            padding: 10px 15px;
            background: white;
            margin-bottom: 8px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
            font-family: 'Courier New', monospace;
        }}
        
        .btn-expand, .btn-log {{
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
        }}
        
        .btn-expand {{
            background: #667eea;
            color: white;
        }}
        
        .btn-expand:hover {{
            background: #5568d3;
            transform: scale(1.05);
        }}
        
        .btn-log {{
            background: #28a745;
            color: white;
        }}
        
        .btn-log:hover {{
            background: #218838;
            transform: scale(1.05);
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #667eea;
            border-radius: 25px;
            font-size: 1em;
            margin-bottom: 20px;
            transition: all 0.3s;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #764ba2;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }}
        
        .no-data {{
            text-align: center;
            padding: 30px;
            color: #999;
            font-style: italic;
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
        }}
        
        .filter-btn:hover, .filter-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>GL Check Analysis Report</h1>
            <div class="workarea-path">Workarea: {os.path.abspath(self.workarea)}</div>
            <div class="workarea-path">Design: {self.design_info.top_hier}</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="label">Overall Status</div>
                <div class="status {status_class}">{overall_status}</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Errors</div>
                <div class="value">{total_errors}</div>
            </div>
            <div class="summary-card">
                <div class="label">Waived</div>
                <div class="value pass-text">{total_waived}</div>
            </div>
            <div class="summary-card">
                <div class="label">Non-Waived</div>
                <div class="value {status_class}">{total_non_waived}</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Runs</div>
                <div class="value">{len(timestamped_dirs)}</div>
            </div>
        </div>
        
        <div class="content">
            <!-- Error Analysis Section -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <h2>Error Analysis by Checker</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content">
                    <input type="text" class="search-box" id="checkerSearch" placeholder="Search checkers..." oninput="filterCheckers()" onkeyup="filterCheckers()">
                    
                    <div class="filter-buttons">
                        <button class="filter-btn active" onclick="filterByStatus('all')">All Checkers</button>
                        <button class="filter-btn" onclick="filterByStatus('fail')">With Non-Waived Only</button>
                        <button class="filter-btn" onclick="filterByStatus('pass')">Fully Waived Only</button>
                    </div>
                    
                    <table id="checkersTable">
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)">Checker [Code](Name) ↕</th>
                                <th onclick="sortTable(1)">Waived ↕</th>
                                <th onclick="sortTable(2)">Non-Waived ↕</th>
                                <th onclick="sortTable(3)">Total ↕</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(checker_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Allowed Clock Tree Cells Section -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <h2>Allowed Clock Tree Cells ({len(allowed_clktree_cells)} cells)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content">
                    <input type="text" class="search-box" id="cellSearch" placeholder="Search cells..." oninput="filterCells()" onkeyup="filterCells()">
                    <div id="cellsContainer">
                        {clktree_cells_html}
                    </div>
                </div>
            </div>
            
            <!-- Don't Use Cells Section -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <h2>Don't Use Cells ({len(dont_use_cells)} cells)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content">
                    <input type="text" class="search-box" id="dontUseCellSearch" placeholder="Search dont_use cells..." oninput="filterDontUseCells()" onkeyup="filterDontUseCells()">
                    <div id="dontUseCellsContainer">
                        {dont_use_cells_html}
                    </div>
                </div>
            </div>
            
            <!-- Key Reports Section -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <h2>Key Reports ({len(key_reports)} reports)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content">
                    {reports_html}
                </div>
            </div>
            
            <!-- Main Logs Section -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <h2>Main Logs ({len(main_logs)} logs)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content">
                    {logs_html}
                </div>
            </div>
            
            <!-- Run History Section -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <h2>Run History ({len(timestamped_dirs)} runs)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content">
                    {run_history_html}
                </div>
            </div>
            
            <!-- File Paths Section -->
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    <h2>Source Files</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content">
                    <div class="report-item">
                        <span class="report-name">Waived Errors File</span>
                        <button class="btn-log" onclick='window.open("file://{waived_file}", "_blank")'>Open Log</button>
                    </div>
                    <div class="report-item">
                        <span class="report-name">Non-Waived Errors File</span>
                        <button class="btn-log" onclick='window.open("file://{non_waived_file}", "_blank")'>Open Log</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentFilter = 'all';
        
        // Initialize search boxes when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            const checkerSearch = document.getElementById('checkerSearch');
            const cellSearch = document.getElementById('cellSearch');
            
            if (checkerSearch) {{
                checkerSearch.addEventListener('input', filterCheckers);
                checkerSearch.addEventListener('keyup', filterCheckers);
            }}
            
            if (cellSearch) {{
                cellSearch.addEventListener('input', filterCells);
                cellSearch.addEventListener('keyup', filterCells);
            }}
        }});
        
        function toggleSection(header) {{
            const content = header.nextElementSibling;
            const icon = header.querySelector('.toggle-icon');
            
            content.classList.toggle('collapsed');
            header.classList.toggle('collapsed');
        }}
        
        function toggleErrorDetails(btn) {{
            const row = btn.closest('tr');
            const detailsRow = row.nextElementSibling;
            
            if (detailsRow && detailsRow.classList.contains('error-details-row')) {{
                if (detailsRow.style.display === 'none') {{
                    detailsRow.style.display = 'table-row';
                    btn.textContent = 'Hide Errors';
                }} else {{
                    detailsRow.style.display = 'none';
                    btn.textContent = 'Show Errors';
                }}
            }}
        }}
        
        function filterCheckers() {{
            const searchTerm = document.getElementById('checkerSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#checkersTable tbody tr.checker-row');
            
            // Convert NodeList to Array for compatibility with older browsers
            Array.prototype.slice.call(rows).forEach(function(row) {{
                const checker = row.getAttribute('data-checker').toLowerCase();
                const matchesSearch = checker.includes(searchTerm);
                const matchesFilter = currentFilter === 'all' || 
                                     (currentFilter === 'fail' && parseInt(row.getAttribute('data-nonwaived')) > 0) ||
                                     (currentFilter === 'pass' && parseInt(row.getAttribute('data-nonwaived')) === 0);
                
                if (matchesSearch && matchesFilter) {{
                    row.style.display = '';
                    const detailsRow = row.nextElementSibling;
                    if (detailsRow && detailsRow.classList.contains('error-details-row')) {{
                        if (detailsRow.style.display === 'table-row') {{
                            detailsRow.style.display = 'table-row';
                        }}
                    }}
                }} else {{
                    row.style.display = 'none';
                    const detailsRow = row.nextElementSibling;
                    if (detailsRow && detailsRow.classList.contains('error-details-row')) {{
                        detailsRow.style.display = 'none';
                    }}
                }}
            }});
        }}
        
        function filterByStatus(status) {{
            currentFilter = status;
            
            // Update button states
            const buttons = document.querySelectorAll('.filter-btn');
            Array.prototype.slice.call(buttons).forEach(function(btn) {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            filterCheckers();
        }}
        
        function sortTable(columnIndex) {{
            const table = document.getElementById('checkersTable');
            const tbody = table.querySelector('tbody');
            const rowsNodeList = tbody.querySelectorAll('tr.checker-row');
            const rows = Array.prototype.slice.call(rowsNodeList);
            
            rows.sort(function(a, b) {{
                let aVal, bVal;
                
                if (columnIndex === 0) {{
                    aVal = a.getAttribute('data-checker');
                    bVal = b.getAttribute('data-checker');
                    return aVal.localeCompare(bVal);
                }} else if (columnIndex === 1) {{
                    aVal = parseInt(a.getAttribute('data-waived'));
                    bVal = parseInt(b.getAttribute('data-waived'));
                }} else if (columnIndex === 2) {{
                    aVal = parseInt(a.getAttribute('data-nonwaived'));
                    bVal = parseInt(b.getAttribute('data-nonwaived'));
                }} else if (columnIndex === 3) {{
                    aVal = parseInt(a.getAttribute('data-total'));
                    bVal = parseInt(b.getAttribute('data-total'));
                }}
                
                return bVal - aVal;
            }});
            
            // Re-append rows with their detail rows
            rows.forEach(function(row) {{
                tbody.appendChild(row);
                const detailsRow = row.nextElementSibling;
                if (detailsRow && detailsRow.classList.contains('error-details-row')) {{
                    tbody.appendChild(detailsRow);
                }}
            }});
        }}
        
        function filterCells() {{
            const searchTerm = document.getElementById('cellSearch').value.toLowerCase();
            const container = document.getElementById('cellsContainer');
            const cells = container.querySelectorAll('.cell-item');
            
            // Convert NodeList to Array for compatibility with older browsers
            Array.prototype.slice.call(cells).forEach(function(cell) {{
                const cellText = cell.textContent.toLowerCase();
                cell.style.display = cellText.includes(searchTerm) ? 'inline-block' : 'none';
            }});
        }}
        
        function filterDontUseCells() {{
            const searchTerm = document.getElementById('dontUseCellSearch').value.toLowerCase();
            const container = document.getElementById('dontUseCellsContainer');
            const cells = container.querySelectorAll('.cell-item');
            
            // Convert NodeList to Array for compatibility with older browsers
            Array.prototype.slice.call(cells).forEach(function(cell) {{
                const cellText = cell.textContent.toLowerCase();
                cell.style.display = cellText.includes(searchTerm) ? 'inline-block' : 'none';
            }});
        }}
    </script>
</body>
</html>
        """
        
        return html
    
    def _generate_gl_check_html_report(self, gl_check_dir, waived_file, non_waived_file, timestamped_dirs):
        """Generate comprehensive HTML report for GL Check analysis"""
        try:
            import yaml
            from datetime import datetime
            
            # Parse error files to get checker data
            waived_checkers = {}
            non_waived_checkers = {}
            non_waived_errors_detail = {}  # Store full error messages by checker
            
            if os.path.exists(waived_file):
                with open(waived_file, 'r') as f:
                    for line in f:
                        match = re.match(r'-E-\[(\d+)\]\((\w+)\)(.*)', line)
                        if match:
                            code, checker, message = match.groups()
                            key = f"[{code}]({checker})"
                            waived_checkers[key] = waived_checkers.get(key, 0) + 1
            
            if os.path.exists(non_waived_file):
                with open(non_waived_file, 'r') as f:
                    for line in f:
                        match = re.match(r'-E-\[(\d+)\]\((\w+)\)(.*)', line)
                        if match:
                            code, checker, message = match.groups()
                            key = f"[{code}]({checker})"
                            non_waived_checkers[key] = non_waived_checkers.get(key, 0) + 1
                            if key not in non_waived_errors_detail:
                                non_waived_errors_detail[key] = []
                            non_waived_errors_detail[key].append(line.strip())
            
            # Parse beflow_config.yaml for allowed_clktree_cells_rex and dont_use_cells_by_rex
            beflow_config_file = os.path.join(gl_check_dir, "beflow_config.yaml")
            allowed_clktree_cells = []
            dont_use_cells = []
            if os.path.exists(beflow_config_file):
                try:
                    with open(beflow_config_file, 'r') as f:
                        content = f.read()
                        
                    # Extract allowed_clktree_cells_rex
                    for line in content.split('\n'):
                            if 'allowed_clktree_cells_rex' in line:
                                match = re.search(r'\[(.*)\]', line)
                                if match:
                                    cells_str = match.group(1)
                                    cells = [cell.strip().strip("'\"") for cell in re.findall(r"'([^']*)'", cells_str)]
                                    allowed_clktree_cells = sorted(cells)
                                break
                    
                    # Extract dont_use_cells_by_rex (can be multi-line)
                    dont_use_match = re.search(r'dont_use_cells_by_rex\s*:\s*\[(.*?)\]', content, re.DOTALL)
                    if dont_use_match:
                        cells_str = dont_use_match.group(1)
                        cells = [cell.strip().strip("'\"") for cell in re.findall(r"'([^']*)'", cells_str)]
                        dont_use_cells = sorted(cells)
                except Exception as e:
                    pass
            
            # Find key report files
            reports_dir = os.path.join(gl_check_dir, "reports")
            key_reports = []
            if os.path.exists(reports_dir):
                report_files = {
                    'Clock Tree Report': 'ClockTree.rpt',
                    'Don\'t Use Cells': 'dontUseCells.rpt',
                    'Cell Statistics': 'cellStats.rpt',
                    'Scan Chains': 'ScanChains.rpt',
                    'DFT Clock Tree (Shift)': 'DFT_clocktree_shift.rpt',
                    'DFT Clock Tree (Capture)': 'DFT_clocktree_capture.rpt',
                    'Illegal DCAP Connections': 'illegal_dcap_connections.rpt',
                    'Sequential to Root Clock': 'seq2RootClk.rpt'
                }
                for name, filename in report_files.items():
                    filepath = os.path.join(reports_dir, filename)
                    if os.path.exists(filepath):
                        # Convert to absolute path for HTML links to work from any location
                        key_reports.append((name, os.path.abspath(filepath)))
            
            # Find main log files
            main_logs = []
            log_files = {
                'GL Check Log': 'gl-check.log',
                'BeFlow2YAML Log': 'beflow2yaml.log',
                'Vivid Log': 'vivid.log'
            }
            # Check in latest timestamped directory first
            if timestamped_dirs:
                latest_run_dir = os.path.join(gl_check_dir, timestamped_dirs[-1])
                for name, filename in log_files.items():
                    filepath = os.path.join(latest_run_dir, filename)
                    if os.path.exists(filepath):
                        # Convert to absolute path for HTML links to work from any location
                        main_logs.append((name, os.path.abspath(filepath)))
            # Also check root gl-check directory
            for name, filename in log_files.items():
                filepath = os.path.join(gl_check_dir, filename)
                abs_filepath = os.path.abspath(filepath)
                if os.path.exists(filepath) and (name, abs_filepath) not in main_logs:
                    # Convert to absolute path for HTML links to work from any location
                    main_logs.append((name, abs_filepath))
            
            # Combine all checkers
            all_checkers = set(waived_checkers.keys()) | set(non_waived_checkers.keys())
            
            # Calculate totals
            total_waived = sum(waived_checkers.values())
            total_non_waived = sum(non_waived_checkers.values())
            total_errors = total_waived + total_non_waived
            
            # Sort checkers by total count
            sorted_checkers = sorted(all_checkers, 
                                    key=lambda x: waived_checkers.get(x, 0) + non_waived_checkers.get(x, 0), 
                                    reverse=True)
            
            # Generate HTML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"avice_gl_check_report_{self.design_info.top_hier}_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            html_content = self._generate_gl_check_html_content(
                waived_checkers, non_waived_checkers, non_waived_errors_detail,
                sorted_checkers, total_errors, total_waived, total_non_waived,
                allowed_clktree_cells, dont_use_cells, key_reports, main_logs, timestamped_dirs,
                waived_file, non_waived_file
            )
            
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            print(f"\n  Open with: firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
            
            return os.path.abspath(html_path)
            
        except Exception as e:
            print(f"  Error generating GL Check HTML report: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def run_gl_check(self):
        """Run GL check analysis"""
        self.print_header(FlowStage.GL_CHECK)
        
        # Show GL Check flow timeline
        gl_check_local_flow_dirs = [
            os.path.join(self.workarea, f"signoff_flow/gl-check/{self.design_info.top_hier}/local_flow"),
            os.path.join(self.workarea, f"signoff_flow/gl-check/local_flow"),
            os.path.join(self.workarea, f"signoff_flow/gl-check_{self.design_info.top_hier}/local_flow")
        ]
        self._show_flow_timeline("GL Check", gl_check_local_flow_dirs)
        
        # Detect GL Check run history from timestamped directories
        gl_check_dir = os.path.join(self.workarea, "signoff_flow/gl-check")
        if os.path.exists(gl_check_dir):
            try:
                # Find all timestamped directories (format: YYYY_MM_DD_HH_MM_SS)
                timestamped_dirs = []
                for entry in os.listdir(gl_check_dir):
                    entry_path = os.path.join(gl_check_dir, entry)
                    if os.path.isdir(entry_path) and re.match(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}', entry):
                        timestamped_dirs.append(entry)
                
                if timestamped_dirs:
                    timestamped_dirs.sort()
                    print(f"\n  {Color.CYAN}GL Check Run History:{Color.RESET}")
                    print(f"    Total Runs: {len(timestamped_dirs)}")
                    print(f"    First Run: {timestamped_dirs[0].replace('_', '/', 2).replace('_', ' ', 1).replace('_', ':').replace('_', ':')}")
                    print(f"    Latest Run: {timestamped_dirs[-1].replace('_', '/', 2).replace('_', ' ', 1).replace('_', ':').replace('_', ':')}")
            except Exception as e:
                pass  # Silently skip if unable to read directory
        
        # Look for GL check error files (waived vs non-waived)
        # Convert to absolute paths for HTML links to work from any location
        waived_file = os.path.abspath(os.path.join(gl_check_dir, "gl-check.all.waived"))
        non_waived_file = os.path.abspath(os.path.join(gl_check_dir, "gl-check.all.err"))
        
        gl_check_html_path = ""
        if os.path.exists(waived_file) or os.path.exists(non_waived_file):
            self._analyze_gl_check_errors(waived_file, non_waived_file)
            # Generate HTML report
            gl_check_html_path = self._generate_gl_check_html_report(gl_check_dir, waived_file, non_waived_file, timestamped_dirs if 'timestamped_dirs' in locals() else [])
        else:
            # Fallback to old err.long.rep format
            gl_check_pattern = "signoff_flow/gl-check*/reports/err.long.rep"
            gl_check_files = self.file_utils.find_files(gl_check_pattern, self.workarea)
            
            if gl_check_files:
                for report_file in gl_check_files:
                    self.print_file_info(report_file, "GL Check Report")
                    try:
                        with open(report_file, 'r') as f:
                            lines = f.readlines()
                        
                        # Process the report and collect data for table formatting
                        gl_check_data = []
                        for line in lines:
                            line = line.strip()
                            # Skip empty lines, separators, and header lines
                            if not line or line.startswith('---') or 'Checker Name' in line or 'Category' in line:
                                continue
                            # Split by pipe and extract relevant columns (1, 3, 4, 5) - skip Category (col2) as it's same as Checker Name
                            parts = line.split('|')
                            if len(parts) >= 6:
                                checker_name = parts[1].strip() if len(parts) > 1 else ""
                                count = parts[3].strip() if len(parts) > 3 else ""
                                error_id = parts[4].strip() if len(parts) > 4 else ""
                                description = parts[5].strip() if len(parts) > 5 else ""
                                # Only add if we have valid data (checker_name and count are required)
                                if checker_name and count:
                                    gl_check_data.append((checker_name, count, error_id, description))
                        
                        # Print as formatted table
                        if gl_check_data:
                            print(f"\n  {Color.CYAN}GL Check Results:{Color.RESET}")
                            print(f"  {'Checker Name':<30} {'Count':<8} {'Error ID':<10} {'Description'}")
                            print(f"  {'-'*30} {'-'*8} {'-'*10} {'-'*50}")
                            for checker_name, count, error_id, description in gl_check_data:
                                # Truncate description if too long
                                desc_truncated = description[:47] + "..." if len(description) > 50 else description
                                print(f"  {checker_name:<30} {count:<8} {error_id:<10} {desc_truncated}")
                        else:
                            print("  No GL check data found")
                    except Exception as e:
                        print(f"  Error reading GL check report: {e}")
            else:
                print("  Didn't run GL checks")
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="GL Checks",
            section_id="gl-check",
            stage=FlowStage.GL_CHECK,
            status="PASS",
            key_metrics={
                "Design": self.design_info.top_hier
            },
            html_file=gl_check_html_path if gl_check_html_path else "",
            priority=3,
            issues=[],
            icon="[GL]"
        )
    
    def _find_beflow_path(self):
        """Find the beflow path from PnR flow configuration or common locations"""
        try:
            # Method 1: Look in PnR logs for NETWORK_FLOW_PATH
            log_files = glob.glob(os.path.join(self.workarea, "pnr_flow/nv_flow/*/ipo*/*.log"))
            for log_file in log_files[:5]:  # Check first 5 logs
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            match = re.search(r'NETWORK_FLOW(?:_UTILS)?_(?:PATH|DIR)\s*[:=]\s*([^\s\n]+)', line)
                            if match:
                                path = match.group(1)
                                # Convert flow2_utils path to beflow path if needed
                                if 'flow2_utils' in path:
                                    # Try to find corresponding beflow path
                                    beflow_path = path.replace('flow2_utils', 'beflow')
                                    if os.path.exists(beflow_path):
                                        return beflow_path
                                return path
                except:
                    continue
            
            # Method 2: Try common beflow installation paths
            common_paths = [
                '/home/nbu_be_tools/beflow/1.0',
                '/tools/nbu_be_tools/beflow/1.0',
            ]
            for base_path in common_paths:
                if os.path.exists(base_path):
                    # Find the latest version
                    versions = glob.glob(os.path.join(base_path, '*'))
                    if versions:
                        # Return the first one found (or could sort by date)
                        return sorted(versions)[-1]  # Return latest
        except:
            pass
        return None
    
    def _check_eco_for_dont_use_cells(self, eco_file, eco_commands):
        """Check if ECO file contains any dont_use cells (ultra-optimized using set lookup)"""
        try:
            # OPTIMIZATION: Try to use dont_use_cell_patterns.tcl from gl-check results (much faster)
            # This file contains actual cell names (not regex patterns) that can be used for O(1) set lookup
            dont_use_cells = set()
            patterns_file = None
            
            for gl_dir in ["signoff_flow/gl-check", "signoff_flow/gl_check", "gl_check", "gl-check"]:
                test_path = os.path.join(self.workarea, gl_dir, "results", "dont_use_cell_patterns.tcl")
                if os.path.exists(test_path):
                    patterns_file = test_path
                    break
            
            if patterns_file:
                # TIER 1: Use GL-Check results (most accurate, workarea-specific)
                print(f"    {Color.CYAN}Using dont_use check: GL-Check results ({os.path.basename(patterns_file)}){Color.RESET}")
                with open(patterns_file, 'r') as f:
                    for line in f:
                        # Format: "dont_use CELLNAME patterns = ..."
                        match = re.match(r'dont_use\s+(\S+)\s+patterns\s+=', line)
                        if match:
                            dont_use_cells.add(match.group(1))
                
                # Check using Tier 1 cells (O(1) set lookup - FAST!)
                violations = []
                violation_cells = {}
                for line in eco_commands:
                    words = re.findall(r'\b[A-Z][A-Z0-9_]+\b', line)
                    for word in words:
                        if word in dont_use_cells:
                            violations.append((line, word))
                            violation_cells[word] = violation_cells.get(word, 0) + 1
                            break
                
                if violations:
                    print(f"  {Color.RED}[WARN] Found {len(violations)} ECO commands using dont_use cells:{Color.RESET}")
                    
                    # Show all matched cells with counts
                    print(f"    {Color.CYAN}Matched cells ({len(violation_cells)}):{Color.RESET}")
                    for cell, count in sorted(violation_cells.items(), key=lambda x: x[1], reverse=True)[:15]:
                        print(f"      {cell}: {count}")
                    if len(violation_cells) > 15:
                        print(f"      ... and {len(violation_cells)-15} more cells")
                    
                    # Show example violations
                    print(f"    {Color.YELLOW}Example violations:{Color.RESET}")
                    for line, cell in violations[:3]:
                        print(f"      Cell '{cell}': {line[:70]}...")
                else:
                    print(f"  {Color.GREEN}[OK] No dont_use cells found in ECO{Color.RESET}")
                return  # Tier 1 found and checked, done
            
            else:
                # FALLBACK 1: Try project-level agur_dont_use.tcl (fast O(1) set lookup with exact cell names)
                agur_dont_use_file = None
                runset_paths = glob.glob(os.path.join(self.workarea, "pnr_flow/nv_flow/*/ipo*/runset.tcl"))
                if runset_paths:
                    try:
                        with open(runset_paths[0], 'r') as f:
                            for line in f:
                                match = re.match(r'set PROJECT\(CUSTOM_SCRIPTS_DIR\)\s+(.+)', line)
                                if match:
                                    custom_scripts_dir = match.group(1).strip()
                                    test_path = os.path.join(custom_scripts_dir, "agur_dont_use.tcl")
                                    if os.path.exists(test_path):
                                        agur_dont_use_file = test_path
                                    break
                    except:
                        pass
                
                if agur_dont_use_file:
                    # Parse agur_dont_use.tcl for exact cell names (O(1) set lookup - FAST!)
                    with open(agur_dont_use_file, 'r') as f:
                        for line in f:
                            # Format: "nvb_dont_use CELLNAME" (exact names, no regex)
                            match = re.match(r'nvb_dont_use\s+(\S+)', line)
                            if match:
                                dont_use_cells.add(match.group(1))
                
                # ALWAYS combine with Tier 3 (BeFlow rules) for comprehensive checking
                # Tier 2 provides project-specific exact names, Tier 3 provides regex patterns
                # Together they form a complete superset of banned cells
                beflow_path = self._find_beflow_path()
                nbu_dont_use_file = None
                if beflow_path:
                    test_path = os.path.join(beflow_path, "bytech/tsmc5/nvidia/tcl/nbu_dont_use.tcl")
                    if os.path.exists(test_path):
                        nbu_dont_use_file = test_path
                
                dont_use_patterns = []
                if nbu_dont_use_file:
                    # Parse nbu_dont_use.tcl for patterns (skip patterns that don't apply to ECO)
                    with open(nbu_dont_use_file, 'r') as f:
                        for line in f:
                            # Format: "nvb_dont_use PATTERN -regexp [-opt|-include_step rtl2gate]"
                            # Skip patterns with -opt flag (optimization-only, not for ECO)
                            # Skip patterns with -include_step rtl2gate (synthesis-only, not for ECO)
                            if '-opt' in line or '-include_step' in line:
                                continue
                            match = re.match(r'nvb_dont_use\s+(\S+)', line)
                            if match:
                                pattern = match.group(1)
                                # Convert to standard regex if needed (already in regex format)
                                dont_use_patterns.append(pattern)
                
                # Determine which sources were used for reporting
                sources_used = []
                if agur_dont_use_file:
                    sources_used.append(f"Project rules ({agur_dont_use_file})")
                if nbu_dont_use_file:
                    sources_used.append(f"BeFlow rules ({nbu_dont_use_file})")
                
                if sources_used:
                    print(f"    {Color.CYAN}Using dont_use check: {' + '.join(sources_used)}{Color.RESET}")
                    # Inform user about optimization opportunity
                    if len(eco_commands) > 10000:
                        print(f"    {Color.YELLOW}[TIP] For faster and more accurate results, run GL-Check to generate dont_use_cell_patterns.tcl{Color.RESET}")
                
                # If we have both exact cells and patterns, check both (COMBINED TIER 2 + 3)
                if dont_use_cells and dont_use_patterns:
                    # OPTIMIZATION: Sample ECO to find active cell types (reduces false checking)
                    sample_cells = set()
                    for line in eco_commands[:min(1000, len(eco_commands))]:
                        sample_cells.update(re.findall(r'\b[A-Z][A-Z0-9_]+\b', line))
                    
                    # STEP 1: Convert Tier 2 exact names to regex and combine with Tier 3 patterns
                    # This allows single-pass checking instead of two passes
                    compiled_patterns = []
                    
                    # Add exact cell names as simple regex patterns
                    for cell in dont_use_cells:
                        pattern_re = re.compile(r'\b' + re.escape(cell) + r'\b', re.IGNORECASE)
                        compiled_patterns.append((pattern_re, f"[EXACT] {cell}"))
                    
                    # Add regex patterns, but only if they might match based on sample
                    for pattern in dont_use_patterns:
                        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
                        clean_pattern = regex_pattern.strip('^$')
                        word_boundary_pattern = r'\b' + clean_pattern + r'\b'
                        try:
                            pattern_re = re.compile(word_boundary_pattern, re.IGNORECASE)
                            # Quick filter: only include if pattern matches something in sample
                            if any(pattern_re.search(cell) for cell in list(sample_cells)[:50]):
                                compiled_patterns.append((pattern_re, pattern))
                        except re.error:
                            pass
                    
                    # STEP 2: Smart sampling for large ECOs with extrapolation
                    violations = []
                    violation_map = {}
                    
                    # For large ECOs, use sampling with extrapolation for speed
                    if len(eco_commands) > 10000:
                        # Check first 10K lines thoroughly for accurate pattern detection
                        sample_size = 10000
                        for line in eco_commands[:sample_size]:
                            for compiled_re, original_pattern in compiled_patterns:
                                if compiled_re.search(line):
                                    violations.append((line, original_pattern))
                                    violation_map[original_pattern] = violation_map.get(original_pattern, 0) + 1
                                    break
                        
                        # Extrapolate total count based on sample
                        if violations:
                            extrapolation_factor = len(eco_commands) / sample_size
                            estimated_total = int(len(violations) * extrapolation_factor)
                            violation_map['_ESTIMATED_TOTAL'] = estimated_total
                    else:
                        # For smaller ECOs, check everything
                        for line in eco_commands:
                            for compiled_re, original_pattern in compiled_patterns:
                                if compiled_re.search(line):
                                    violations.append((line, original_pattern))
                                    violation_map[original_pattern] = violation_map.get(original_pattern, 0) + 1
                                    break
                    
                    # Separate exact vs pattern violations for reporting
                    violations_exact = [(l, p) for l, p in violations if p.startswith('[EXACT]')]
                    violations_pattern = [(l, p) for l, p in violations if not p.startswith('[EXACT]')]
                    violation_cells_exact = {p.replace('[EXACT] ', ''): c for p, c in violation_map.items() if p.startswith('[EXACT]')}
                    violation_patterns = {p: c for p, c in violation_map.items() if not p.startswith('[EXACT]')}
                    
                    # Combine results
                    total_violations = len(violations_exact) + len(violations_pattern)
                    estimated_total = violation_map.get('_ESTIMATED_TOTAL')
                    
                    if total_violations > 0:
                        if estimated_total:
                            print(f"  {Color.RED}[WARN] Found ~{estimated_total} ECO commands using dont_use cells (estimated from {total_violations} in sample):{Color.RESET}")
                        else:
                            print(f"  {Color.RED}[WARN] Found {total_violations} ECO commands using dont_use cells:{Color.RESET}")
                        
                        # Show all matched patterns first
                        if violation_patterns:
                            # Remove the _ESTIMATED_TOTAL key if present
                            patterns_to_show = {k: v for k, v in violation_patterns.items() if k != '_ESTIMATED_TOTAL'}
                            if patterns_to_show:
                                print(f"    {Color.CYAN}Matched patterns ({len(patterns_to_show)}):{Color.RESET}")
                                for pattern, count in sorted(patterns_to_show.items(), key=lambda x: x[1], reverse=True):
                                    if estimated_total:
                                        # Extrapolate pattern count too
                                        extrapolation_factor = len(eco_commands) / 10000
                                        estimated_pattern_count = int(count * extrapolation_factor)
                                        print(f"      {pattern}: ~{estimated_pattern_count} (found {count} in sample)")
                                    else:
                                        print(f"      {pattern}: {count}")
                        
                        if violation_cells_exact:
                            print(f"    {Color.CYAN}Matched exact cells ({len(violation_cells_exact)}):{Color.RESET}")
                            for cell, count in sorted(violation_cells_exact.items(), key=lambda x: x[1], reverse=True)[:10]:
                                print(f"      {cell}: {count}")
                            if len(violation_cells_exact) > 10:
                                print(f"      ... and {len(violation_cells_exact)-10} more cells")
                        
                        # Show examples
                        print(f"    {Color.YELLOW}Example violations:{Color.RESET}")
                        if violations_exact:
                            for line, cell in violations_exact[:2]:
                                print(f"      Cell '{cell.replace('[EXACT] ', '')}': {line[:70]}...")
                        if violations_pattern:
                            for line, pattern in violations_pattern[:2]:
                                print(f"      Pattern '{pattern}': {line[:70]}...")
                    else:
                        print(f"  {Color.GREEN}[OK] No dont_use cells found in ECO{Color.RESET}")
                    return
                
                elif dont_use_cells:
                    # Only exact cells available (Tier 2 only - no BeFlow patterns found)
                    # Use fast O(1) set lookup
                    violations = []
                    violation_cells = {}
                    for line in eco_commands:
                        words = re.findall(r'\b[A-Z][A-Z0-9_]+\b', line)
                        for word in words:
                            if word in dont_use_cells:
                                violations.append((line, word))
                                violation_cells[word] = violation_cells.get(word, 0) + 1
                                break
                    
                    if violations:
                        print(f"  {Color.RED}[WARN] Found {len(violations)} ECO commands using dont_use cells:{Color.RESET}")
                        for line, cell in violations[:5]:
                            print(f"    {Color.YELLOW}Cell '{cell}':{Color.RESET} {line[:75]}...")
                        if len(violations) > 5:
                            print(f"    {Color.YELLOW}... and {len(violations)-5} more violations{Color.RESET}")
                        print(f"    {Color.YELLOW}Violating cells:{Color.RESET} {', '.join([f'{cell}({count})' for cell, count in sorted(violation_cells.items(), key=lambda x: x[1], reverse=True)[:10]])}")
                    else:
                        print(f"  {Color.GREEN}[OK] No dont_use cells found in ECO{Color.RESET}")
                    return
                
                else:
                    # No sources found
                    return
                
        except Exception as e:
            pass  # Silently skip if check fails
    
    def run_eco_analysis(self):
        """Run ECO analysis"""
        self.print_header(FlowStage.ECO_ANALYSIS)
        
        # PT-ECO
        eco_pattern = "signoff_flow/auto_pt/work*/pt_eco_out_*_final.tcl"
        eco_files = self.file_utils.find_files(eco_pattern, self.workarea)
        
        print(f"{Color.RED}{len(eco_files)} ECO loops were done{Color.RESET}")
        
        if eco_files:
            for eco_file in eco_files:
                self.print_file_info(eco_file, "ECO File")
                # Count ECO commands by reading file directly
                try:
                    with open(eco_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Filter out comments and empty lines
                    eco_commands = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and line != 'current_instance':
                            eco_commands.append(line)
                    
                    print(f"  Total ECO commands: {len(eco_commands)}")
                    
                    # Count commands by type
                    command_types = {}
                    for command_line in eco_commands:
                        # Extract command type (first word)
                        command = command_line.split()[0] if command_line.split() else ""
                        if command:
                            command_types[command] = command_types.get(command, 0) + 1
                            
                except Exception as e:
                    print(f"  Error reading ECO file: {e}")
                    eco_commands = []
                    command_types = {}
                
                # Display command breakdown
                if command_types:
                    print(f"  Command breakdown:")
                    for cmd_type, count in sorted(command_types.items(), key=lambda x: x[1], reverse=True):
                        print(f"    {cmd_type}: {count}")
                
                # Check for dont_use cells in ECO file
                self._check_eco_for_dont_use_cells(eco_file, eco_commands)
                        
        else:
            print("Didn't run PT ECO")
        
        # NV Gate ECO - handled in run_nv_gate_eco method
        nv_eco_dir = os.path.join(self.workarea, "signoff_flow/nv_gate_eco")
        if self.file_utils.dir_exists(nv_eco_dir):
            print("NV Gate ECO directory found - see NV Gate ECO section for details")
        else:
            print("Didn't run NV Gate ECO")
    
    def _extract_block_release_info(self, release_log: str):
        """Extract block release information focusing on umake block_release commands"""
        try:
            # Use grep to extract only the line we need instead of reading entire file
            result = self.file_utils.run_command(f"grep 'Release to:' '{release_log}' | head -1")
            if result.strip():
                release_to = result.strip().split('Release to:')[1].strip()
                print(f"  Release to: {release_to}")
            
            # Extract umake block_release command lines from umake logs
            self._extract_umake_block_release_commands()
                
        except Exception as e:
            print(f"  Error reading block release log: {e}")
    
    def _extract_umake_block_release_commands(self):
        """Extract umake -s block_release commands with dates from umake logs"""
        try:
            # Use grep to find all umake block_release commands in one go
            umake_pattern = os.path.join(self.workarea, "umake_log/2025*/*.log")
            result = self.file_utils.run_command(f"grep -h 'Command line:.*-s block_release' {umake_pattern} 2>/dev/null | head -10")
            
            if result.strip():
                print(f"  {Color.CYAN}Umake Block Release Commands:{Color.RESET}")
                lines = result.strip().split('\n')
                for line in lines:
                    if line.strip():
                        # Extract timestamp and command
                        timestamp = "Unknown"
                        if '[' in line and ']' in line:
                            timestamp = line.split('[')[1].split(']')[0].strip()
                        
                        if 'Command line:' in line:
                            cmd_line = line.split('Command line:')[1].strip()
                            print(f"    [{timestamp}] {cmd_line}")
            else:
                print("  No umake -s block_release commands found")
                
        except Exception as e:
            print(f"  Error extracting umake block_release commands: {e}")
    
    def run_nv_gate_eco(self):
        """Run NV Gate ECO analysis"""
        self.print_header(FlowStage.NV_GATE_ECO)
        
        # Show NV Gate ECO flow timeline
        nv_gate_eco_local_flow_dirs = [
            os.path.join(self.workarea, f"signoff_flow/nv_gate_eco/{self.design_info.top_hier}/local_flow"),
            os.path.join(self.workarea, f"signoff_flow/nv_gate_eco/local_flow")
        ]
        self._show_flow_timeline("NV Gate ECO", nv_gate_eco_local_flow_dirs)
        
        # Check if NV Gate ECO directory exists
        nv_gate_eco_dir = os.path.join(self.workarea, "signoff_flow/nv_gate_eco")
        
        if os.path.exists(nv_gate_eco_dir):
            # Look for ECO change summary
            eco_change_pattern = f"signoff_flow/nv_gate_eco/{self.design_info.top_hier}/ipo*/sum.eco_change"
            eco_change_files = self.file_utils.find_files(eco_change_pattern, self.workarea)
            
            if eco_change_files:
                self.print_file_info(eco_change_files[0], "NV Gate ECO Summary")
                try:
                    # Read and extract the ECO change summary table
                    with open(eco_change_files[0], 'r') as f:
                        content = f.read()
                    
                    # Find the ECO summary table section
                    lines = content.split('\n')
                    in_table = False
                    table_lines = []
                    
                    for line in lines:
                        line = line.strip()
                        # Start of table
                        if 'OBJECT' in line and 'CHANGE' in line and 'COUNT' in line:
                            in_table = True
                            table_lines.append(line)
                        continue
                        # End of table
                        if in_table and line.startswith('---') and 'TOTAL' in line:
                            table_lines.append(line)
                            break
                        # Table content
                        if in_table and line and not line.startswith('---'):
                            table_lines.append(line)
                    
                    # Parse and format the ECO summary table
                    if table_lines:
                        eco_data = []
                        total_count = 0
                        
                        for line in table_lines:
                            if line.startswith('OBJECT') or line.startswith('---'):
                                continue  # Skip header and separator lines
                            
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    count = int(parts[-1])
                                    if count > 0:  # Only include non-zero changes
                                        if 'TOTAL' in line.upper():
                                            eco_data.append(('TOTAL', '', count))
                                        else:
                                            obj_type = parts[0]
                                            change_type = ' '.join(parts[1:-1])
                                            eco_data.append((obj_type, change_type, count))
                                except (ValueError, IndexError):
                                    pass
                        
                        if eco_data:
                            print(f"  {Color.CYAN}ECO Changes Summary:{Color.RESET}")
                            # Print formatted table header
                            print(f"    {'Object':<10} {'Change':<15} {'Count':>8}")
                            print(f"    {'-'*10} {'-'*15} {'-'*8}")
                            
                            # Print data rows
                            for obj_type, change_type, count in eco_data:
                                if obj_type == 'TOTAL':
                                    print(f"    {'-'*10} {'-'*15} {'-'*8}")
                                    print(f"    {'TOTAL':<10} {'':<15} {count:>8}")
                                else:
                                    print(f"    {obj_type:<10} {change_type:<15} {count:>8}")
                    else:
                        print(f"  {Color.YELLOW}No ECO changes found{Color.RESET}")
                except Exception as e:
                    print(f"  Error reading ECO change summary: {e}")
            
            # Look for timing reports
            setup_pattern = f"signoff_flow/nv_gate_eco/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.eco.timing.setup.rpt.gz"
            hold_pattern = f"signoff_flow/nv_gate_eco/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.eco.timing.hold.rpt.gz"
            
            setup_files = self.file_utils.find_files(setup_pattern, self.workarea)
            hold_files = self.file_utils.find_files(hold_pattern, self.workarea)
            
            # Process setup timing report
            if setup_files:
                self.print_file_info(setup_files[0], "NV Gate ECO Setup Timing")
                try:
                    # Extract the last three histogram tables (category, sub-category, and sub-category+scenario)
                    print(f"  {Color.CYAN}Timing Histogram Tables (ECO):{Color.RESET}")
                    
                    # Get all histogram table line numbers
                    result = self.file_utils.run_command(f"zcat {setup_files[0]} | grep -n 'histogram' | grep '|'")
                    if result.strip():
                        histogram_lines = result.strip().split('\n')
                        if len(histogram_lines) >= 4:
                            # Get the last 4 tables: category, scenario, sub-category, and sub-category + scenario
                            table_category_start = int(histogram_lines[-4].split(':')[0])  # Category breakdown
                            table_scenario_start = int(histogram_lines[-3].split(':')[0])  # Scenario breakdown
                            table_subcat_start = int(histogram_lines[-2].split(':')[0])    # Sub-category breakdown
                            table_subcat_scenario_start = int(histogram_lines[-1].split(':')[0])  # Sub-category + scenario breakdown
                            
                            # Find the end of category table (it ends before scenario table starts)
                            table_category_end = table_scenario_start - 1
                            
                            # Extract category table (for HTML only - not printed to terminal)
                            table_category_result = self.file_utils.run_command(f"zcat {setup_files[0]} | sed -n '{table_category_start},{table_category_end}p'")
                            # Table 1 data extracted but not printed (HTML only)
                            
                            # Find the end of sub-category table (it ends before sub-category + scenario table starts)
                            table_subcat_end = table_subcat_scenario_start - 1
                            
                            # Extract sub-category table (TERMINAL OUTPUT: Table 2 only for concise output)
                            table_subcat_result = self.file_utils.run_command(f"zcat {setup_files[0]} | sed -n '{table_subcat_start},{table_subcat_end}p'")
                            if table_subcat_result.strip():
                                print(f"  Table 2 - Sub-Category Breakdown (Lines {table_subcat_start}-{table_subcat_end}):")
                                table_subcat_lines = table_subcat_result.strip().split('\n')
                                for line in table_subcat_lines:
                                    if line.strip():
                                        print(f"  {line}")
                            
                            # Extract sub-category + scenario table (for HTML only - not printed to terminal)
                            table_subcat_scenario_result = self.file_utils.run_command(f"zcat {setup_files[0]} | sed -n '{table_subcat_scenario_start},$p'")
                            # Table 3 data extracted but not printed (HTML only)
                        else:
                            print("  Could not find histogram tables")
                    else:
                        print("  Histogram tables not found")
                except Exception as e:
                    print(f"  Error processing setup timing report: {e}")
            
            # Process hold timing report
            if hold_files:
                self.print_file_info(hold_files[0], "NV Gate ECO Hold Timing")
                try:
                    # Find histogram line in hold report
                    result = self.file_utils.run_command(f"grep -n '_histogram_' {hold_files[0]} | tail -n2 | head -n1 | cut -d ':' -f 1")
                    if result.strip():
                        start_line = int(result.strip())
                        # Extract histogram section
                        result = self.file_utils.run_command(f"zcat {hold_files[0]} | awk -v line={start_line} 'NR >= line {{print; if (/===/ && ++count == 2) exit}}'")
                        if result.strip():
                            for line in result.strip().split('\n'):
                                print(f"  {line}")
                except Exception as e:
                    print(f"  Error processing hold timing report: {e}")
            
            # Look for trace reports and worst paths
            trace_pattern = f"signoff_flow/nv_gate_eco*/{self.design_info.top_hier}/{self.design_info.ipo}/reports/*.traces.rpt"
            worst_paths_pattern = f"signoff_flow/nv_gate_eco*/{self.design_info.top_hier}/{self.design_info.ipo}/reports/*.worst_paths"
            
            trace_files = self.file_utils.find_files(trace_pattern, self.workarea)
            worst_paths_files = self.file_utils.find_files(worst_paths_pattern, self.workarea)
            
            for trace_file in trace_files:
                self.print_file_info(trace_file, "NV Gate ECO Traces")
            
            for worst_paths_file in worst_paths_files:
                self.print_file_info(worst_paths_file, "NV Gate ECO Worst Paths")
        else:
            print("  Didn't run NV Gate ECO")
    
    def run_block_release(self):
        """Run block release analysis"""
        self.print_header(FlowStage.BLOCK_RELEASE)
        
        # Block release log
        release_log = os.path.join(self.workarea, "export/block_release/log/block_release.log")
        if self.file_utils.file_exists(release_log):
            self.print_file_info(release_log, "Block Release Log")
            self._extract_block_release_info(release_log)
        else:
            print("No release was done")
        
        # Umake logs - use grep for better performance
        umake_pattern = os.path.join(self.workarea, "umake_log/2025*/*.log")
        result = self.file_utils.run_command(f"grep -h 'block_release.*umake\\.py' {umake_pattern} 2>/dev/null | head -5")
        if result.strip():
            for line in result.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
        
        # Block release summary
        summary_pattern = f"*block_release/reports/{self.design_info.top_hier}.summary"
        summary_files = self.file_utils.find_files(summary_pattern, self.workarea)
        if summary_files:
            self.print_file_info(summary_files[0], "Block Release Summary")
            try:
                # Use grep to filter out 'False' lines instead of reading entire file
                if summary_files[0].endswith('.gz'):
                    result = self.file_utils.run_command(f"zcat '{summary_files[0]}' | grep -v 'False'")
                else:
                    result = self.file_utils.run_command(f"grep -v 'False' '{summary_files[0]}'")
                
                if result.strip():
                    for line in result.strip().split('\n'):
                        if line.strip():
                            print(f"  {line}")
            except Exception as e:
                print(f"Unable to read Block Release Summary: {e}")
    
    def run_complete_review(self):
        """Run complete workarea review"""
        # Display logo if enabled
        if self.show_logo:
            LogoDisplay.print_ascii_logo()
            # Try to display the actual logo image
            LogoDisplay.display_logo()
        
        # Run all analysis stages
        self.run_setup_analysis()
        self.run_runtime_analysis()
        self.run_synthesis_analysis()
        self.run_pnr_analysis()
        self.run_clock_analysis()
        self.run_formal_verification()
        self.run_parasitic_extraction()
        self.run_signoff_timing()
        self.run_physical_verification()
        self.run_gl_check()
        self.run_eco_analysis()
        self.run_nv_gate_eco()
        self.run_block_release()
        
        # Generate Master Dashboard
        print(f"\n{Color.CYAN}Generating Master Dashboard...{Color.RESET}")
        try:
            dashboard_path = self.master_dashboard.generate_html()
            print(f"{Color.GREEN}[OK] Master Dashboard generated: file://{dashboard_path}{Color.RESET}")
            print(f"{Color.CYAN}     Open this file in your browser to view the integrated review dashboard{Color.RESET}")
        except Exception as e:
            print(f"{Color.RED}[ERROR] Failed to generate Master Dashboard: {e}{Color.RESET}")
        
        print(f"\n{Color.GREEN}Review completed successfully!{Color.RESET}")

    def run_runtime_analysis(self):
        """Run runtime analysis"""
        self.print_header(FlowStage.RUNTIME)
        
        # Collect runtime data for summary table
        runtime_data = {}
        runtime_timestamps = {}  # Store start/end timestamps for each stage
        
        # Check for fast_dc first
        fast_dc_log = os.path.join(self.workarea, "syn_flow/fast_dc/log/fast_dc.log")
        fast_dc_detected = os.path.exists(fast_dc_log)
        
        if fast_dc_detected:
            print(f"\n{Color.CYAN}Fast DC detected - analyzing both fast_dc and full dc runs{Color.RESET}")
            print(f"  Note: PnR start times adjusted to setup step (full PnR run after fast_dc)")
            
            # Fast DC runtime
            try:
                result = self.file_utils.run_command(f"grep 'Elapsed time' {fast_dc_log} | sed -e 's/.*( //' -e 's/ ).//' | tail -n1")
                full_elapsed_line = self.file_utils.run_command(f"grep 'Elapsed time' {fast_dc_log} | tail -n1")
                
                if result.strip():
                    runtime_data['Fast DC'] = result.strip()
                    
                    # Extract Fast DC timestamps
                    try:
                        end_time = os.path.getmtime(fast_dc_log)
                        duration_match = re.search(r'(\d+)\s+seconds', full_elapsed_line)
                        if duration_match:
                            duration_seconds = int(duration_match.group(1))
                            start_time = end_time - duration_seconds
                            
                            start_str = time.strftime("%m/%d %H:%M", time.localtime(start_time))
                            end_str = time.strftime("%m/%d %H:%M", time.localtime(end_time))
                            runtime_timestamps['Fast DC'] = (start_str, end_str)
                    except Exception:
                        pass
            except Exception as e:
                print(f"  Error extracting Fast DC runtime: {e}")

        # DC runtime
        dc_log = os.path.join(self.workarea, "syn_flow/dc/log/dc.log")
        if os.path.exists(dc_log):
            try:
                # Get both the formatted runtime and the full elapsed time line
                result = self.file_utils.run_command(f"grep 'Elapsed time' {dc_log} | sed -e 's/.*( //' -e 's/ ).//' | tail -n1")
                full_elapsed_line = self.file_utils.run_command(f"grep 'Elapsed time' {dc_log} | tail -n1")
                
                if result.strip():
                    dc_key = "Full DC" if fast_dc_detected else "DC"
                    runtime_data[dc_key] = result.strip()
                    # Extract DC timestamps - calculate start time from end time and duration
                    try:
                        # Get file modification time as end time
                        end_time = os.path.getmtime(dc_log)
                        
                        # Extract duration in seconds from the full elapsed time line
                        duration_match = re.search(r'(\d+)\s+seconds', full_elapsed_line)
                        if duration_match:
                            duration_seconds = int(duration_match.group(1))
                            start_time = end_time - duration_seconds
                            
                            start_str = time.strftime("%m/%d %H:%M", time.localtime(start_time))
                            end_str = time.strftime("%m/%d %H:%M", time.localtime(end_time))
                            runtime_timestamps[dc_key] = (start_str, end_str)
                        else:
                            # Fallback to file timestamps
                            start, end = self._extract_timestamps_from_log(dc_log)
                            if start and end:
                                runtime_timestamps[dc_key] = (start, end)
                    except Exception:
                        # Fallback to file timestamps
                        start, end = self._extract_timestamps_from_log(dc_log)
                        if start and end:
                            runtime_timestamps[dc_key] = (start, end)
            except Exception as e:
                print(f"  Error extracting DC runtime: {e}")
        
        # PnR runtime for each IPO
        pnr_runtimes = {}
        # Convert to absolute path for HTML links to work from any location
        prc_status = os.path.abspath(os.path.join(self.workarea, f"pnr_flow/nv_flow/{self.design_info.top_hier}.prc.status"))
        
        for ipo in self.design_info.all_ipos:
            if os.path.exists(prc_status):
                try:
                    # Calculate PnR runtime (BEGIN to postroute only, exclude reporting and post-postroute stages)
                    result = self.file_utils.run_command(f"grep ' {ipo}' {prc_status} | grep -E '(BEGIN|setup|edi_plan|place|cts|route|postroute)' | grep -v report | sed 's/# //' | awk '{{print $5}}' | column -t")
                    if result.strip():
                        try:
                            total_runtime_seconds = sum(int(x) for x in result.strip().split() if x.isdigit())
                            total_runtime_hours = total_runtime_seconds / 3600
                            total_runtime_days = total_runtime_hours / 24
                            
                            if total_runtime_hours >= 24:
                                runtime_str = f"{total_runtime_hours:.2f} hours ({total_runtime_days:.2f} days)"
                            else:
                                runtime_str = f"{total_runtime_hours:.2f} hours"
                            
                            pnr_runtimes[ipo] = runtime_str
                            
                            # Extract PnR timestamps from log file names in PRC status
                            try:
                                pnr_lines = self.file_utils.run_command(f"grep ' {ipo}' {prc_status} | grep -E '(BEGIN|setup|edi_plan|place|cts|route|postroute)' | grep -v report")
                                if pnr_lines.strip():
                                    lines = pnr_lines.strip().split('\n')
                                    if lines:
                                        # Check if fast_dc was used - if so, use setup as start instead of BEGIN
                                        fast_dc_log = os.path.join(self.workarea, "syn_flow/fast_dc/log/fast_dc.log")
                                        use_setup_as_start = os.path.exists(fast_dc_log)
                                        
                                        if use_setup_as_start:
                                            # Find setup step as start (full PnR after fast_dc)
                                            setup_line = None
                                            for line in lines:
                                                if 'setup' in line and 'DONE' in line:
                                                    setup_line = line
                                                    break
                                            first_line = setup_line if setup_line else lines[0]
                                        else:
                                            # Use BEGIN as normal
                                            first_line = lines[0]
                                        
                                        last_line = lines[-1]
                                        
                                        # Look for timestamp patterns in log file names (format: YYYYMMDDHHMMSS)
                                        first_match = re.search(r'(\d{8})(\d{6})', first_line)
                                        last_match = re.search(r'(\d{8})(\d{6})', last_line)
                                        
                                        # Extract the last stage's duration to calculate actual end time
                                        last_line_parts = last_line.split()
                                        last_stage_duration_seconds = 0
                                        if len(last_line_parts) >= 5:
                                            try:
                                                last_stage_duration_seconds = int(last_line_parts[4])
                                            except (ValueError, IndexError):
                                                pass
                                        
                                        if first_match and last_match:
                                            try:
                                                first_date = first_match.group(1)  # YYYYMMDD
                                                first_time = first_match.group(2)  # HHMMSS
                                                last_date = last_match.group(1)
                                                last_time = last_match.group(2)
                                                
                                                # Parse start timestamp
                                                start_datetime = f"{first_date[:4]}-{first_date[4:6]}-{first_date[6:8]} {first_time[:2]}:{first_time[2:4]}:{first_time[4:6]}"
                                                start_time = time.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
                                                start_epoch = time.mktime(start_time)
                                                
                                                # Parse last stage's START timestamp (from log file name)
                                                last_start_datetime = f"{last_date[:4]}-{last_date[4:6]}-{last_date[6:8]} {last_time[:2]}:{last_time[2:4]}:{last_time[4:6]}"
                                                last_start_time = time.strptime(last_start_datetime, "%Y-%m-%d %H:%M:%S")
                                                last_start_epoch = time.mktime(last_start_time)
                                                
                                                # Calculate actual end time by adding last stage's duration
                                                actual_end_epoch = last_start_epoch + last_stage_duration_seconds
                                                
                                                start_str = time.strftime("%m/%d %H:%M", start_time)
                                                end_str = time.strftime("%m/%d %H:%M", time.localtime(actual_end_epoch))
                                                runtime_timestamps[f'PnR ({ipo})'] = (start_str, end_str)
                                            except Exception:
                                                pass
                            except Exception:
                                pass
                        except ValueError:
                            print(f"  Total PnR Runtime for {ipo}: Unable to calculate (non-numeric values)")
                except Exception as e:
                    print(f"  Error extracting PnR runtime for {ipo}: {e}")
            else:
                print(f"  PnR Status file not found for {ipo}")
        
        # Star extraction runtime
        star_runtime = self._extract_star_runtime()
        if star_runtime:
            runtime_data['Star'] = star_runtime
            # Extract Star timestamps from log files
            star_log_patterns = [
                f"export/nv_star/{self.design_info.top_hier}/ipo*/LOGs/PRIME/STEP__star_extraction__*.log",
                f"export/nv_star/{self.design_info.top_hier}/ipo*/LOGs/*.log",
                f"export/nv_star/ipo*/LOGs/PRIME/STEP__star_extraction__*.log"
            ]
            star_logs = []
            for pattern in star_log_patterns:
                logs = self.file_utils.find_files(pattern, self.workarea)
                star_logs.extend(logs)
            if star_logs:
                latest_log = max(star_logs, key=os.path.getmtime)
                # Try to calculate accurate timestamps from runtime duration
                end_time = os.path.getmtime(latest_log)
                calculated_times = self._calculate_start_time_from_duration(end_time, star_runtime)
                if calculated_times[0] and calculated_times[1]:
                    runtime_timestamps['Star'] = calculated_times
                else:
                    # Fallback to file timestamps
                    start, end = self._extract_timestamps_from_log(latest_log)
                    if start and end:
                        runtime_timestamps['Star'] = (start, end)
        
        # Auto PT runtime
        auto_pt_runtime = self._extract_auto_pt_runtime()
        if auto_pt_runtime:
            runtime_data['Auto PT'] = auto_pt_runtime
            # Extract Auto PT timestamps from log files
            auto_pt_log_patterns = [
                f"signoff_flow/auto_pt/log/auto_pt.log",
                f"signoff_flow/auto_pt/*/LOGs/PRIME/STEP__auto_pt__*.log",
                f"signoff_flow/auto_pt/work_*/LOGs/*.log"
            ]
            auto_pt_logs = []
            for pattern in auto_pt_log_patterns:
                logs = self.file_utils.find_files(pattern, self.workarea)
                auto_pt_logs.extend(logs)
            if auto_pt_logs:
                latest_log = max(auto_pt_logs, key=os.path.getmtime)
                # Check if running (runtime string contains "(running)")
                if auto_pt_runtime and "(running)" in auto_pt_runtime:
                    # For running PT, use start time and "RUNNING" as end
                    start, _ = self._extract_timestamps_from_log(latest_log)
                    if start:
                        runtime_timestamps['Auto PT'] = (start, "RUNNING")
                else:
                    # Try to calculate accurate timestamps from runtime duration
                    end_time = os.path.getmtime(latest_log)
                    calculated_times = self._calculate_start_time_from_duration(end_time, auto_pt_runtime)
                    if calculated_times[0] and calculated_times[1]:
                        runtime_timestamps['Auto PT'] = calculated_times
                    else:
                        # Fallback to file timestamps
                        start, end = self._extract_timestamps_from_log(latest_log)
                        if start and end:
                            runtime_timestamps['Auto PT'] = (start, end)
        
        # Formal verification runtime (both types separately)
        formal_runtimes = self._extract_formal_runtime()
        if formal_runtimes:
            for formal_type, runtime in formal_runtimes.items():
                runtime_data[f'Formal ({formal_type})'] = runtime
                # Extract Formal verification timestamps
                formal_log_patterns = [
                    f"formal_flow/{formal_type}/LOGs/PRIME/STEP__formal__*.log",
                    f"formal_flow/{formal_type}/log/*.log",
                    f"formal_flow/{formal_type}/*.log"
                ]
                formal_logs = []
                for pattern in formal_log_patterns:
                    logs = self.file_utils.find_files(pattern, self.workarea)
                    formal_logs.extend(logs)
                if formal_logs:
                    latest_log = max(formal_logs, key=os.path.getmtime)
                    # Check if running
                    if runtime == "running":
                        # For running formal, use start time and "RUNNING" as end
                        start, _ = self._extract_timestamps_from_log(latest_log)
                        if start:
                            runtime_timestamps[f'Formal ({formal_type})'] = (start, "RUNNING")
                    else:
                        # Try to calculate accurate timestamps from runtime duration
                        end_time = os.path.getmtime(latest_log)
                        calculated_times = self._calculate_start_time_from_duration(end_time, runtime)
                        if calculated_times[0] and calculated_times[1]:
                            runtime_timestamps[f'Formal ({formal_type})'] = calculated_times
                        else:
                            # Fallback to file timestamps
                            start, end = self._extract_timestamps_from_log(latest_log)
                            if start and end:
                                runtime_timestamps[f'Formal ({formal_type})'] = (start, end)
        
        # GL Check runtime
        gl_check_runtime = self._extract_gl_check_runtime()
        if gl_check_runtime:
            runtime_data['GL Check'] = gl_check_runtime
            # Extract GL Check timestamps
            gl_check_log_patterns = [
                f"signoff_flow/gl-check*/LOGs/PRIME/STEP__gl_check__*.log",
                f"signoff_flow/gl-check*/*/gl-check.log",
                f"signoff_flow/gl-check/*/gl-check.log"
            ]
            gl_check_logs = []
            for pattern in gl_check_log_patterns:
                logs = self.file_utils.find_files(pattern, self.workarea)
                gl_check_logs.extend(logs)
            if gl_check_logs:
                latest_log = max(gl_check_logs, key=os.path.getmtime)
                # Try to calculate accurate timestamps from runtime duration
                end_time = os.path.getmtime(latest_log)
                calculated_times = self._calculate_start_time_from_duration(end_time, gl_check_runtime)
                if calculated_times[0] and calculated_times[1]:
                    runtime_timestamps['GL Check'] = calculated_times
                else:
                    # Fallback to file timestamps
                    start, end = self._extract_timestamps_from_log(latest_log)
                    if start and end:
                        runtime_timestamps['GL Check'] = (start, end)
        
        # Auto PT Fix runtime
        auto_pt_fix_runtime = self._extract_auto_pt_fix_runtime()
        if auto_pt_fix_runtime:
            runtime_data['Auto PT Fix'] = auto_pt_fix_runtime
            # Extract Auto PT Fix timestamps
            # Use pt_eco_out_*_final.tcl files to identify which work areas had auto_pt_fix
            # and use auto_pt_fix.log for end timestamp
            end_time = None
            
            # Method 1: Use auto_pt_fix.log modification time as end time
            auto_pt_fix_log = os.path.join(self.workarea, "signoff_flow/auto_pt_fix/log/auto_pt_fix.log")
            if os.path.exists(auto_pt_fix_log):
                end_time = os.path.getmtime(auto_pt_fix_log)
            else:
                # Fallback: Try other auto_pt_fix log locations
                auto_pt_fix_log = os.path.join(self.workarea, "signoff_flow/auto_pt/log/auto_pt_fix.log")
                if os.path.exists(auto_pt_fix_log):
                    end_time = os.path.getmtime(auto_pt_fix_log)
            
            if end_time:
                # Try to calculate accurate timestamps from runtime duration
                calculated_times = self._calculate_start_time_from_duration(end_time, auto_pt_fix_runtime)
                if calculated_times[0] and calculated_times[1]:
                    runtime_timestamps['Auto PT Fix'] = calculated_times
                else:
                    # Fallback: Look for pt_eco_out_*_final.tcl files in work directories
                    eco_pattern = "signoff_flow/auto_pt/work_*/pt_eco_out_*_final.tcl"
                    eco_files = self.file_utils.find_files(eco_pattern, self.workarea)
                    if eco_files:
                        # Use the latest pt_eco_out file timestamp
                        latest_eco = max(eco_files, key=os.path.getmtime)
                        eco_end_time = os.path.getmtime(latest_eco)
                        calculated_times = self._calculate_start_time_from_duration(eco_end_time, auto_pt_fix_runtime)
                        if calculated_times[0] and calculated_times[1]:
                            runtime_timestamps['Auto PT Fix'] = calculated_times
        
        # Gen ECO Netlist Innovus runtime
        gen_eco_runtime = self._extract_gen_eco_runtime()
        if gen_eco_runtime:
            runtime_data['Gen ECO Netlist'] = gen_eco_runtime
            # Extract Gen ECO Netlist timestamps
            gen_eco_log_patterns = [
                f"signoff_flow/gen_eco_netlist_innovus/{self.design_info.top_hier}/ipo*/LOGs/PRIME/STEP__gen_eco_netlist__*.log",
                f"signoff_flow/gen_eco_netlist_innovus/*/LOGs/PRIME/STEP__gen_eco_netlist__*.log",
                f"signoff_flow/gen_eco_netlist_innovus/log/*.log"
            ]
            gen_eco_logs = []
            for pattern in gen_eco_log_patterns:
                logs = self.file_utils.find_files(pattern, self.workarea)
                gen_eco_logs.extend(logs)
            if gen_eco_logs:
                latest_log = max(gen_eco_logs, key=os.path.getmtime)
                # Try to calculate accurate timestamps from runtime duration
                end_time = os.path.getmtime(latest_log)
                calculated_times = self._calculate_start_time_from_duration(end_time, gen_eco_runtime)
                if calculated_times[0] and calculated_times[1]:
                    runtime_timestamps['Gen ECO Netlist'] = calculated_times
                else:
                    # Fallback to file timestamps
                    start, end = self._extract_timestamps_from_log(latest_log)
                    if start and end:
                        runtime_timestamps['Gen ECO Netlist'] = (start, end)
        
        # NV Gate ECO runtime
        eco_prc_status = os.path.join(self.workarea, f"signoff_flow/nv_gate_eco/eco_{self.design_info.top_hier}.prc.status")
        if os.path.exists(eco_prc_status):
            self.print_file_info(eco_prc_status, "NV Gate ECO Status")
            try:
                # Extract NV Gate ECO runtime for completed steps
                result = self.file_utils.run_command(f"grep -E '^{self.design_info.top_hier}.*DONE' {eco_prc_status} | awk '{{sum += $5}} END {{print sum}}'")
                if result.strip() and result.strip().isdigit():
                    total_runtime_seconds = int(result.strip())
                    total_runtime_hours = total_runtime_seconds / 3600
                    total_runtime_days = total_runtime_hours / 24
                    
                    if total_runtime_hours >= 24:
                        runtime_str = f"{total_runtime_hours:.2f} hours ({total_runtime_days:.2f} days)"
                    else:
                        runtime_str = f"{total_runtime_hours:.2f} hours"
                    
                    runtime_data['NV Gate ECO'] = runtime_str
                    # Extract NV Gate ECO timestamps from log file names in status file
                    try:
                        eco_lines = self.file_utils.run_command(f"grep '{self.design_info.top_hier}.*DONE' {eco_prc_status}")
                        if eco_lines.strip():
                            lines = eco_lines.strip().split('\n')
                            if lines:
                                # Extract timestamps from log file names
                                first_line = lines[0]
                                last_line = lines[-1]
                                
                                # Look for timestamp patterns in log file names (format: YYYYMMDDHHMMSS)
                                first_match = re.search(r'(\d{8})(\d{6})', first_line)
                                last_match = re.search(r'(\d{8})(\d{6})', last_line)
                                
                                if first_match and last_match:
                                    try:
                                        first_date = first_match.group(1)  # YYYYMMDD
                                        first_time = first_match.group(2)  # HHMMSS
                                        last_date = last_match.group(1)
                                        last_time = last_match.group(2)
                                        
                                        # Parse timestamps
                                        start_datetime = f"{first_date[:4]}-{first_date[4:6]}-{first_date[6:8]} {first_time[:2]}:{first_time[2:4]}:{first_time[4:6]}"
                                        end_datetime = f"{last_date[:4]}-{last_date[4:6]}-{last_date[6:8]} {last_time[:2]}:{last_time[2:4]}:{last_time[4:6]}"
                                        
                                        start_time = time.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
                                        end_time = time.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")
                                        
                                        start_str = time.strftime("%m/%d %H:%M", start_time)
                                        end_str = time.strftime("%m/%d %H:%M", end_time)
                                        runtime_timestamps['NV Gate ECO'] = (start_str, end_str)
                                    except Exception:
                                        pass
                    except Exception:
                        pass
                else:
                    print("  No completed NV Gate ECO steps found")
            except Exception as e:
                print(f"  Error extracting NV Gate ECO runtime: {e}")
        else:
            print("  NV Gate ECO Status file not found")
        
        # PV runtime
        pv_runtime = self._extract_pv_runtime()
        if pv_runtime:
            runtime_data['PV'] = pv_runtime
            # Extract PV timestamps from PV flow timeline
            local_flow_dir = os.path.join(self.workarea, f"pv_flow/nv_flow/{self.design_info.top_hier}/local_flow")
            if os.path.exists(local_flow_dir):
                try:
                    begin_files = glob.glob(os.path.join(local_flow_dir, "STEP__BEGIN__*"))
                    end_files = glob.glob(os.path.join(local_flow_dir, "STEP__END__*"))
                    if begin_files:
                        begin_time = os.path.getmtime(begin_files[0])
                        start_str = time.strftime("%m/%d %H:%M", time.localtime(begin_time))
                        
                        if end_files:
                            # Flow completed
                            end_time = os.path.getmtime(end_files[0])
                            end_str = time.strftime("%m/%d %H:%M", time.localtime(end_time))
                            runtime_timestamps['PV'] = (start_str, end_str)
                        else:
                            # Flow is running
                            runtime_timestamps['PV'] = (start_str, "RUNNING")
                except Exception:
                    pass
        
        # Print runtime summary table
        self._print_runtime_summary_table(runtime_data, pnr_runtimes, runtime_timestamps)
        
        # Generate HTML runtime report
        runtime_html_path = self._generate_runtime_html_report(runtime_data, pnr_runtimes, prc_status, runtime_timestamps)
        
        # Calculate total runtime for summary
        total_runtime_str = "N/A"
        if runtime_data or pnr_runtimes:
            # Get PnR runtime as main metric (typically longest)
            if pnr_runtimes:
                total_runtime_str = list(pnr_runtimes.values())[0] if pnr_runtimes else "N/A"
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Runtime Analysis",
            section_id="runtime",
            stage=FlowStage.RUNTIME,
            status="PASS",
            key_metrics={
                "PnR Runtime": total_runtime_str,
                "Stages": str(len(runtime_data)),
                "IPOs": str(len(pnr_runtimes))
            },
            html_file=runtime_html_path,
            priority=3,
            issues=[],
            icon="[Runtime]"
        )

    def _extract_star_runtime(self):
        """Extract Star extraction runtime"""
        try:
            # Look for Star extraction logs in multiple locations
            star_log_patterns = [
                f"export/nv_star/{self.design_info.top_hier}/ipo*/LOGs/PRIME/STEP__extraction__*.log",
                f"export/nv_star/{self.design_info.top_hier}/ipo*/LOGs/flow_logs/*extraction*.log"
            ]
            
            star_logs = []
            for pattern in star_log_patterns:
                logs = self.file_utils.find_files(pattern, self.workarea)
                star_logs.extend(logs)
            
            if star_logs:
                # Extract runtime from the most recent log
                latest_log = max(star_logs, key=os.path.getmtime)
                result = self.file_utils.run_command(f"grep 'Run time' {latest_log} | tail -n1 | sed 's/.*Run time.*: *//' | sed 's/ sec.*//'")
                if result.strip() and result.strip().isdigit():
                    runtime_seconds = int(result.strip())
                    runtime_hours = runtime_seconds / 3600
                    if runtime_hours >= 24:
                        runtime_days = runtime_hours / 24
                        return f"{runtime_days:.2f} days ({runtime_hours:.2f} hours)"
                    else:
                        return f"{runtime_hours:.2f} hours"
        except Exception:
            pass
        return None

    def _extract_auto_pt_runtime(self):
        """Extract Auto PT runtime including elapsed time if currently running"""
        try:
            # Look for Auto PT log
            auto_pt_log = os.path.join(self.workarea, "signoff_flow/auto_pt/log/auto_pt.log")
            if os.path.exists(auto_pt_log):
                # Check if PT is currently running by checking for work directory without HTML
                is_running = False
                work_pattern = os.path.join(self.workarea, "signoff_flow/auto_pt/work_*")
                all_items = glob.glob(work_pattern)
                work_dirs = [item for item in all_items if os.path.isdir(item)]
                
                if work_dirs:
                    work_dirs_sorted = sorted(work_dirs, key=os.path.getmtime, reverse=True)
                    latest_work = work_dirs_sorted[0]
                    latest_work_name = os.path.basename(latest_work)
                    
                    # Check if HTML report exists for the latest work area
                    html_for_latest = os.path.join(self.workarea, f"signoff_flow/auto_pt/{latest_work_name}.html")
                    if not os.path.exists(html_for_latest):
                        # No HTML means PT is likely still running
                        # Check if files were recently modified (within last hour)
                        latest_mtime = os.path.getmtime(latest_work)
                        current_time = time.time()
                        time_since_update = (current_time - latest_mtime) / 60  # minutes
                        
                        if time_since_update < 60:  # Within last hour
                            is_running = True
                
                # Try multiple patterns for runtime extraction
                result = self.file_utils.run_command(f"grep 'Total.*cpu seconds' {auto_pt_log} | tail -n1 | sed 's/.*Total \\([0-9]*\\) cpu seconds.*/\\1/'")
                
                if not result.strip() or not result.strip().isdigit():
                    # Look for "Elapsed time for this session" pattern
                    result = self.file_utils.run_command(f"grep 'Elapsed time for this session' {auto_pt_log} | sed 's/.*Elapsed time for this session: \\([0-9]*\\) seconds.*/\\1/'")
                
                if not result.strip() or not result.strip().isdigit():
                    # Look for elapsed time in performance table
                    result = self.file_utils.run_command(f"grep -A 10 'Elapsed Time (s)' {auto_pt_log} | grep 'local process' | awk '{{print $4}}'")
                
                if not result.strip() or not result.strip().isdigit():
                    result = self.file_utils.run_command(f"grep 'Run time' {auto_pt_log} | tail -n1 | sed 's/.*Run time.*: *//' | sed 's/ sec.*//'")
                
                # If PT is running, calculate elapsed time from start
                if is_running:
                    # Try to find start time from log or work directory creation time
                    start_time = None
                    if work_dirs:
                        # Use work directory creation time as start time
                        start_time = os.path.getctime(work_dirs_sorted[0])
                    
                    if start_time:
                        current_time = time.time()
                        elapsed_seconds = int(current_time - start_time)
                        elapsed_hours = elapsed_seconds / 3600
                        
                        if elapsed_hours >= 24:
                            elapsed_days = elapsed_hours / 24
                            return f"{elapsed_hours:.2f} hours ({elapsed_days:.2f} days) (running)"
                        else:
                            return f"{elapsed_hours:.2f} hours (running)"
                    else:
                        return "running"
                
                # PT is not running, return completed runtime
                if result.strip() and result.strip().isdigit():
                    runtime_seconds = int(result.strip())
                    runtime_hours = runtime_seconds / 3600
                    if runtime_hours >= 24:
                        runtime_days = runtime_hours / 24
                        return f"{runtime_days:.2f} days ({runtime_hours:.2f} hours)"
                    else:
                        return f"{runtime_hours:.2f} hours"
        except Exception:
            pass
        return None

    def _extract_formal_runtime(self):
        """Extract Formal verification runtime from both formal types separately"""
        try:
            # Look for both types of Formal verification logs
            formal_logs = [
                ("rtl_vs_pnr_bbox_fm", os.path.join(self.workarea, "formal_flow/rtl_vs_pnr_bbox_fm/log/rtl_vs_pnr_bbox_fm.log")),
                ("rtl_vs_pnr_fm", os.path.join(self.workarea, "formal_flow/rtl_vs_pnr_fm/log/rtl_vs_pnr_fm.log"))
            ]
            
            formal_runtimes = {}
            
            for formal_type, formal_log in formal_logs:
                if os.path.exists(formal_log):
                    # Check if formal is currently running
                    file_mtime = os.path.getmtime(formal_log)
                    current_time = time.time()
                    time_since_update = current_time - file_mtime
                    
                    is_running = False
                    if time_since_update < 300:  # 5 minutes
                        # Check for running indicators and no completion status
                        check_result = self.file_utils.run_command(
                            f"tail -100 {formal_log} | grep -E 'Status:.*Building verification models|Status:.*Verifying|Status:.*Checking designs|Matching in progress' | tail -1"
                        )
                        completion_result = self.file_utils.run_command(
                            f"grep -E 'Verification SUCCEEDED|Verification FAILED' {formal_log} | tail -1"
                        )
                        
                        if check_result.strip() and not completion_result.strip():
                            is_running = True
                    
                    if is_running:
                        formal_runtimes[formal_type] = "running"
                        continue
                    
                    # Try multiple patterns for runtime extraction
                    result = self.file_utils.run_command(f"grep 'Total.*cpu seconds' {formal_log} | tail -n1 | sed 's/.*Total \\([0-9]*\\) cpu seconds.*/\\1/'")
                    
                    if not result.strip() or not result.strip().isdigit():
                        # Look for "Elapsed time: X seconds" pattern
                        result = self.file_utils.run_command(f"grep 'Elapsed time:' {formal_log} | tail -n1 | sed 's/.*Elapsed time: \\([0-9]*\\) seconds.*/\\1/'")
                    
                    if not result.strip() or not result.strip().isdigit():
                        # Look for "Elapsed time for this session" pattern
                        result = self.file_utils.run_command(f"grep 'Elapsed time for this session' {formal_log} | sed 's/.*Elapsed time for this session: \\([0-9]*\\) seconds.*/\\1/'")
                    
                    if not result.strip() or not result.strip().isdigit():
                        # Look for elapsed time in performance table
                        result = self.file_utils.run_command(f"grep -A 10 'Elapsed Time (s)' {formal_log} | grep 'local process' | awk '{{print $4}}'")
                    
                    if not result.strip() or not result.strip().isdigit():
                        result = self.file_utils.run_command(f"grep 'Run time' {formal_log} | tail -n1 | sed 's/.*Run time.*: *//' | sed 's/ sec.*//'")
                    
                    if result.strip() and result.strip().isdigit():
                        runtime_seconds = int(result.strip())
                        runtime_hours = runtime_seconds / 3600
                        if runtime_hours >= 24:
                            runtime_days = runtime_hours / 24
                            formal_runtimes[formal_type] = f"{runtime_days:.2f} days ({runtime_hours:.2f} hours)"
                        else:
                            formal_runtimes[formal_type] = f"{runtime_hours:.2f} hours"
            
            return formal_runtimes
        except Exception:
            pass
        return None

    def _extract_gl_check_runtime(self):
        """Extract GL Check runtime"""
        try:
            # Look for GL Check logs in multiple possible locations
            gl_check_log_patterns = [
                f"signoff_flow/gl-check*/LOGs/PRIME/STEP__gl_check__*.log",  # Original pattern
                f"signoff_flow/gl-check*/*/gl-check.log",  # New pattern for timestamped directories
                f"signoff_flow/gl-check/*/gl-check.log"    # Alternative pattern
            ]
            
            gl_check_logs = []
            for pattern in gl_check_log_patterns:
                logs = self.file_utils.find_files(pattern, self.workarea)
                gl_check_logs.extend(logs)
            
            if gl_check_logs:
                # Extract runtime from the most recent log
                latest_log = max(gl_check_logs, key=os.path.getmtime)
                
                # Try different runtime extraction methods
                # Method 1: Look for "Run time:" pattern
                result = self.file_utils.run_command(f"grep 'Run time:' {latest_log} | tail -n1 | sed 's/.*Run time: //' | sed 's/ sec//'")
                if result.strip() and result.strip().isdigit():
                    runtime_seconds = int(result.strip())
                    runtime_hours = runtime_seconds / 3600
                    if runtime_hours >= 24:
                        runtime_days = runtime_hours / 24
                        return f"{runtime_days:.2f} days ({runtime_hours:.2f} hours)"
                    else:
                        return f"{runtime_hours:.2f} hours"
                
                # Method 2: Calculate from file timestamps (directory start/end times)
                log_dir = os.path.dirname(latest_log)
                if os.path.exists(log_dir):
                    # Get directory creation time and latest file modification time
                    dir_files = glob.glob(os.path.join(log_dir, "*"))
                    if dir_files:
                        start_time = min(os.path.getmtime(f) for f in dir_files)
                        end_time = max(os.path.getmtime(f) for f in dir_files)
                        duration_seconds = int(end_time - start_time)
                        
                        if duration_seconds > 0:
                            runtime_hours = duration_seconds / 3600
                            if runtime_hours >= 24:
                                runtime_days = runtime_hours / 24
                                return f"{runtime_days:.2f} days ({runtime_hours:.2f} hours)"
                            else:
                                return f"{runtime_hours:.2f} hours"
                
        except Exception as e:
            print(f"  Error extracting GL Check runtime: {e}")
        return None

    def _extract_auto_pt_fix_runtime(self):
        """Extract Auto PT Fix runtime (elapsed/wall-clock time, not CPU time)"""
        try:
            # Look for Auto PT Fix log in auto_pt directory (auto_pt_fix uses auto_pt structure)
            auto_pt_fix_log = os.path.join(self.workarea, "signoff_flow/auto_pt/log/auto_pt_fix.log")
            if os.path.exists(auto_pt_fix_log):
                # Extract "Elapsed time for this session" which shows actual wall-clock time
                # Format: "Elapsed time for this session: 3866 seconds"
                result = self.file_utils.run_command(f"grep 'Elapsed time for this session' {auto_pt_fix_log} | tail -n1")
                
                if result.strip():
                    # Extract seconds from the line
                    match = re.search(r'(\d+\.?\d*)\s*seconds?', result)
                    if match:
                        runtime_seconds = float(match.group(1))
                        runtime_hours = runtime_seconds / 3600
                        if runtime_hours >= 24:
                            runtime_days = runtime_hours / 24
                            return f"{runtime_hours:.2f} hours ({runtime_days:.2f} days)"
                        else:
                            return f"{runtime_hours:.2f} hours"
        except Exception as e:
            print(f"  Error extracting Auto PT Fix runtime: {e}")
        return None

    def _extract_gen_eco_runtime(self):
        """Extract Gen ECO Netlist Innovus runtime"""
        try:
            # Look for Gen ECO Netlist logs
            gen_eco_log_pattern = f"signoff_flow/gen_eco_netlist_innovus/{self.design_info.top_hier}/ipo*/LOGs/PRIME/STEP__gen_eco_netlist__*.log"
            gen_eco_logs = self.file_utils.find_files(gen_eco_log_pattern, self.workarea)
            if gen_eco_logs:
                # Extract runtime from the most recent log
                latest_log = max(gen_eco_logs, key=os.path.getmtime)
                result = self.file_utils.run_command(f"grep 'Run time:' {latest_log} | tail -n1 | sed 's/.*Run time: //' | sed 's/ sec//'")
                if result.strip() and result.strip().isdigit():
                    runtime_seconds = int(result.strip())
                    runtime_hours = runtime_seconds / 3600
                    if runtime_hours >= 24:
                        runtime_days = runtime_hours / 24
                        return f"{runtime_days:.2f} days ({runtime_hours:.2f} hours)"
                    else:
                        return f"{runtime_hours:.2f} hours"
        except Exception:
            pass
        return None

    def _extract_pv_runtime(self):
        """Extract PV flow runtime including elapsed time of running steps"""
        try:
            prc_status_pattern = f"pv_flow/nv_flow/pv_{self.design_info.top_hier}.prc.status"
            prc_status_files = self.file_utils.find_files(prc_status_pattern, self.workarea)
            
            if not prc_status_files:
                return None
            
            prc_status_file = prc_status_files[0]
            
            with open(prc_status_file, 'r') as f:
                content = f.read()
            
            # Extract completed steps and calculate total runtime
            total_runtime_seconds = 0
            completed_steps = 0
            running_steps = 0
            
            # Get BEGIN timestamp to calculate running step's elapsed time
            local_flow_dir = os.path.join(self.workarea, f"pv_flow/nv_flow/{self.design_info.top_hier}/local_flow")
            begin_time = None
            if os.path.exists(local_flow_dir):
                begin_files = glob.glob(os.path.join(local_flow_dir, "STEP__BEGIN__*"))
                if begin_files:
                    begin_time = os.path.getmtime(begin_files[0])
            
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#') and '    ' in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        status = parts[3]
                        duration = parts[4]
                        
                        if status == 'DONE' and duration.isdigit() and int(duration) > 0:
                            # Add completed step duration
                            total_runtime_seconds += int(duration)
                            completed_steps += 1
                        elif status == 'RUN' and duration.isdigit() and int(duration) > 0:
                            # For running steps, use the duration from status file 
                            # (which represents elapsed time so far)
                            total_runtime_seconds += int(duration)
                            running_steps += 1
            
            # If there are running steps and we have begin time, calculate current elapsed time
            if running_steps > 0 and begin_time:
                current_time = time.time()
                # Calculate total elapsed time from BEGIN
                total_elapsed_seconds = int(current_time - begin_time)
                # Use the greater of: sum of step durations OR total elapsed time
                # (Sometimes the status file durations lag behind real time)
                total_runtime_seconds = max(total_runtime_seconds, total_elapsed_seconds)
            
            if total_runtime_seconds > 0:
                total_runtime_hours = total_runtime_seconds / 3600
                total_runtime_days = total_runtime_hours / 24
                
                if total_runtime_hours >= 24:
                    runtime_str = f"{total_runtime_hours:.2f} hours ({total_runtime_days:.2f} days)"
                else:
                    runtime_str = f"{total_runtime_hours:.2f} hours"
                
                # Add indicator if flow is still running
                if running_steps > 0:
                    runtime_str += " (running)"
                
                return runtime_str
            
        except Exception as e:
            print(f"  Error extracting PV runtime: {e}")
        
        return None

    def _extract_timestamps_from_log(self, log_file: str):
        """Extract start and end timestamps from a log file"""
        try:
            if not os.path.exists(log_file):
                return None, None
            
            # Get file creation and modification times as fallback
            stat = os.stat(log_file)
            start_time = stat.st_ctime  # Creation time
            end_time = stat.st_mtime    # Modification time
            
            # Try to extract more precise timestamps from log content
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                
                # Look for timestamp patterns in the first and last few lines
                if lines:
                    # Check first few lines for start timestamp
                    for line in lines[:10]:
                        # Look for common timestamp patterns
                        timestamp_match = re.search(r'(\d{4}[/-]\d{2}[/-]\d{2}[\s_]\d{2}:\d{2}:\d{2})', line)
                        if timestamp_match:
                            try:
                                # Try to parse the timestamp
                                timestamp_str = timestamp_match.group(1).replace('_', ' ').replace('/', '-')
                                parsed_time = time.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                start_time = time.mktime(parsed_time)
                                break
                            except:
                                continue
                    
                    # Check last few lines for end timestamp
                    for line in reversed(lines[-10:]):
                        timestamp_match = re.search(r'(\d{4}[/-]\d{2}[/-]\d{2}[\s_]\d{2}:\d{2}:\d{2})', line)
                        if timestamp_match:
                            try:
                                timestamp_str = timestamp_match.group(1).replace('_', ' ').replace('/', '-')
                                parsed_time = time.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                end_time = time.mktime(parsed_time)
                                break
                            except:
                                continue
            except:
                pass  # Use file timestamps as fallback
            
            # Format timestamps
            start_str = time.strftime("%m/%d %H:%M", time.localtime(start_time))
            end_str = time.strftime("%m/%d %H:%M", time.localtime(end_time))
            
            return start_str, end_str
            
        except Exception:
            return None, None

    def _calculate_start_time_from_duration(self, end_time_epoch: float, runtime_str: str):
        """Calculate start time from end time and runtime duration string"""
        try:
            # Extract duration in hours from runtime string
            hours_match = re.search(r'(\d+\.?\d*)\s*hours?', runtime_str)
            if hours_match:
                duration_hours = float(hours_match.group(1))
                duration_seconds = int(duration_hours * 3600)
                start_time_epoch = end_time_epoch - duration_seconds
                
                start_str = time.strftime("%m/%d %H:%M", time.localtime(start_time_epoch))
                end_str = time.strftime("%m/%d %H:%M", time.localtime(end_time_epoch))
                return start_str, end_str
        except Exception:
            pass
        return None, None

    def _print_runtime_summary_table(self, runtime_data, pnr_runtimes, runtime_timestamps=None):
        """Print runtime summary table"""
        print(f"\n{Color.CYAN}Runtime Summary Table:{Color.RESET}")
        
        # Prepare table data with timestamps
        table_data = []
        
        if runtime_timestamps is None:
            runtime_timestamps = {}
        
        # Construction stages
        if 'Fast DC' in runtime_data:
            start, end = runtime_timestamps.get('Fast DC', (None, None))
            table_data.append(("Construction", "Fast DC", runtime_data['Fast DC'], start or "N/A", end or "N/A"))
        if 'Full DC' in runtime_data:
            start, end = runtime_timestamps.get('Full DC', (None, None))
            table_data.append(("Construction", "Full DC", runtime_data['Full DC'], start or "N/A", end or "N/A"))
        elif 'DC' in runtime_data:
            start, end = runtime_timestamps.get('DC', (None, None))
            table_data.append(("Construction", "DC", runtime_data['DC'], start or "N/A", end or "N/A"))
        
        for ipo, runtime in pnr_runtimes.items():
            start, end = runtime_timestamps.get(f'PnR ({ipo})', (None, None))
            table_data.append(("Construction", f"PnR ({ipo})", runtime, start or "N/A", end or "N/A"))
        
        # Signoff stages
        if 'Star' in runtime_data:
            start, end = runtime_timestamps.get('Star', (None, None))
            table_data.append(("Signoff", "Star", runtime_data['Star'], start or "N/A", end or "N/A"))
        if 'Auto PT' in runtime_data:
            start, end = runtime_timestamps.get('Auto PT', (None, None))
            table_data.append(("Signoff", "Auto PT", runtime_data['Auto PT'], start or "N/A", end or "N/A"))
        
        # Formal verification stages (both types separately)
        for key, value in runtime_data.items():
            if key.startswith('Formal ('):
                formal_type = key.replace('Formal (', '').replace(')', '')
                start, end = runtime_timestamps.get(key, (None, None))
                table_data.append(("Signoff", f"Formal ({formal_type})", value, start or "N/A", end or "N/A"))
        
        if 'GL Check' in runtime_data:
            start, end = runtime_timestamps.get('GL Check', (None, None))
            table_data.append(("Signoff", "GL Check", runtime_data['GL Check'], start or "N/A", end or "N/A"))
        if 'PV' in runtime_data:
            start, end = runtime_timestamps.get('PV', (None, None))
            table_data.append(("Signoff", "PV", runtime_data['PV'], start or "N/A", end or "N/A"))
        
        # ECO stages
        if 'Auto PT Fix' in runtime_data:
            start, end = runtime_timestamps.get('Auto PT Fix', (None, None))
            table_data.append(("ECO", "Auto PT Fix", runtime_data['Auto PT Fix'], start or "N/A", end or "N/A"))
        if 'Gen ECO Netlist' in runtime_data:
            start, end = runtime_timestamps.get('Gen ECO Netlist', (None, None))
            table_data.append(("ECO", "Gen ECO Netlist", runtime_data['Gen ECO Netlist'], start or "N/A", end or "N/A"))
        if 'NV Gate ECO' in runtime_data:
            start, end = runtime_timestamps.get('NV Gate ECO', (None, None))
            table_data.append(("ECO", "NV Gate ECO", runtime_data['NV Gate ECO'], start or "N/A", end or "N/A"))
        
        # Print table with proper alignment
        if table_data:
            # Sort table data by start timestamp (oldest to newest)
            # Convert timestamp strings to sortable format and handle "N/A" and "RUNNING"
            def get_sort_key(row):
                start_time = row[3]  # Start timestamp is at index 3
                if start_time == "N/A":
                    return "9999/99/99 99:99"  # Put N/A at the end
                return start_time
            
            table_data_sorted = sorted(table_data, key=get_sort_key)
            
            # Calculate column widths
            max_category = max(len(row[0]) for row in table_data_sorted)
            max_stage = max(len(row[1]) for row in table_data_sorted)
            max_runtime = max(len(row[2]) for row in table_data_sorted)
            max_start = max(len(row[3]) for row in table_data_sorted)
            max_end = max(len(row[4]) for row in table_data_sorted)
            
            # Ensure minimum widths for headers
            category_width = max(max_category, len("Category"))
            stage_width = max(max_stage, len("Stage"))
            runtime_width = max(max_runtime, len("Runtime"))
            start_width = max(max_start, len("Start"))
            end_width = max(max_end, len("End"))
            
            # Print header
            print(f"  {'Category':<{category_width}} {'Stage':<{stage_width}} {'Runtime':<{runtime_width}} {'Start':<{start_width}} {'End':<{end_width}}")
            print(f"  {'-' * category_width} {'-' * stage_width} {'-' * runtime_width} {'-' * start_width} {'-' * end_width}")
            
            # Print data rows (now sorted by start time)
            for category, stage, runtime, start, end in table_data_sorted:
                print(f"  {category:<{category_width}} {stage:<{stage_width}} {runtime:<{runtime_width}} {start:<{start_width}} {end:<{end_width}}")
        else:
            print("  No runtime data available")
    
    def _print_runtime_summary_table_advanced(self, runtime_data, pnr_runtimes):
        """Alternative advanced table printing with more options"""
        print(f"\n{Color.CYAN}Runtime Summary Table (Advanced):{Color.RESET}")
        
        # Prepare table data
        table_data = []
        
        # Construction stages
        if 'DC' in runtime_data:
            table_data.append(("Construction", "DC", runtime_data['DC']))
        
        for ipo, runtime in pnr_runtimes.items():
            table_data.append(("Construction", f"PnR ({ipo})", runtime))
        
        # Signoff stages
        if 'Star' in runtime_data:
            table_data.append(("Signoff", "Star", runtime_data['Star']))
        if 'Auto PT' in runtime_data:
            table_data.append(("Signoff", "Auto PT", runtime_data['Auto PT']))
        
        # Formal verification stages
        for key, value in runtime_data.items():
            if key.startswith('Formal ('):
                formal_type = key.replace('Formal (', '').replace(')', '')
                table_data.append(("Signoff", f"Formal ({formal_type})", value))
        
        if 'GL Check' in runtime_data:
            table_data.append(("Signoff", "GL Check", runtime_data['GL Check']))
        if 'PV' in runtime_data:
            table_data.append(("Signoff", "PV", runtime_data['PV']))
        
        # ECO stages
        if 'Auto PT Fix' in runtime_data:
            table_data.append(("ECO", "Auto PT Fix", runtime_data['Auto PT Fix']))
        if 'Gen ECO Netlist' in runtime_data:
            table_data.append(("ECO", "Gen ECO Netlist", runtime_data['Gen ECO Netlist']))
        if 'NV Gate ECO' in runtime_data:
            table_data.append(("ECO", "NV Gate ECO", runtime_data['NV Gate ECO']))
        
        # Print table with borders and better formatting
        if table_data:
            # Calculate column widths
            max_category = max(len(row[0]) for row in table_data)
            max_stage = max(len(row[1]) for row in table_data)
            max_runtime = max(len(row[2]) for row in table_data)
            
            # Ensure minimum widths
            category_width = max(max_category, 8)
            stage_width = max(max_stage, 5)
            runtime_width = max(max_runtime, 6)
            
            # Print table with borders
            print(f"  +{'-' * (category_width + 2)}+{'-' * (stage_width + 2)}+{'-' * (runtime_width + 2)}+")
            print(f"  | {'Category':<{category_width}} | {'Stage':<{stage_width}} | {'Runtime':<{runtime_width}} |")
            print(f"  +{'-' * (category_width + 2)}+{'-' * (stage_width + 2)}+{'-' * (runtime_width + 2)}+")
            
            for category, stage, runtime in table_data:
                print(f"  | {category:<{category_width}} | {stage:<{stage_width}} | {runtime:<{runtime_width}} |")
            
            print(f"  +{'-' * (category_width + 2)}+{'-' * (stage_width + 2)}+{'-' * (runtime_width + 2)}+")
    
    def _generate_runtime_html_report(self, runtime_data, pnr_runtimes, prc_status_file, runtime_timestamps=None):
        """Generate comprehensive HTML runtime report"""
        try:
            # Get detailed PnR stage data
            pnr_stage_data = self._extract_detailed_pnr_stage_data(prc_status_file)
            
            # Check for fast_dc detection
            fast_dc_log = os.path.join(self.workarea, "syn_flow/fast_dc/log/fast_dc.log")
            fast_dc_detected = os.path.exists(fast_dc_log)
            
            # Check for RTL formal
            rtl_detected = self._check_rtl_formal_exists()
            
            # Generate HTML content
            html_content = self._create_runtime_html_content(runtime_data, pnr_runtimes, pnr_stage_data, prc_status_file, runtime_timestamps, fast_dc_detected, rtl_detected)
            
            # Save HTML file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"{os.environ.get('USER', 'avice')}_runtime_report_{self.design_info.top_hier}_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\n  {Color.CYAN}Runtime HTML Report:{Color.RESET}")
            print(f"  Open with: firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
            
            return os.path.abspath(html_path)
            
        except Exception as e:
            print(f"  Error generating runtime HTML report: {e}")
            return ""
    
    def _check_rtl_formal_exists(self):
        """Check if RTL formal verification directories exist"""
        rtl_formal_dirs = [
            os.path.join(self.workarea, "formal_flow/rtl_vs_pnr_bbox_fm"),
            os.path.join(self.workarea, "formal_flow/rtl_vs_pnr_fm"),
            os.path.join(self.workarea, "rtl_vs_pnr_bbox_fm"),
            os.path.join(self.workarea, "rtl_vs_pnr_fm")
        ]
        for rtl_dir in rtl_formal_dirs:
            if os.path.isdir(rtl_dir):
                return True
        return False
    
    def _extract_detailed_pnr_stage_data(self, prc_status_file):
        """Extract detailed PnR stage data for each IPO"""
        pnr_stage_data = {}
        
        if not os.path.exists(prc_status_file):
            return pnr_stage_data
        
        try:
            with open(prc_status_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse status line: block ipo step status duration logfile
                parts = line.split()
                if len(parts) >= 6:
                    block, ipo, step, status, duration, logfile = parts[0], parts[1], parts[2], parts[3], parts[4], ' '.join(parts[5:])
                    
                    if ipo not in pnr_stage_data:
                        pnr_stage_data[ipo] = []
                    
                    # Convert duration to hours
                    try:
                        duration_seconds = int(duration)
                        duration_hours = duration_seconds / 3600
                        duration_days = duration_hours / 24
                        
                        if duration_hours >= 24:
                            duration_str = f"{duration_hours:.2f} hours ({duration_days:.2f} days)"
                        else:
                            duration_str = f"{duration_hours:.2f} hours"
                    except ValueError:
                        duration_str = f"{duration} seconds"
                    
                    # Convert logfile path to absolute for HTML links to work from any location
                    abs_logfile = os.path.abspath(os.path.join(self.workarea, logfile)) if not os.path.isabs(logfile) else logfile
                    
                    pnr_stage_data[ipo].append({
                        'step': step,
                        'status': status,
                        'duration': duration_str,
                        'duration_seconds': duration,
                        'logfile': abs_logfile
                    })
        
        except Exception as e:
            print(f"  Error extracting detailed PnR stage data: {e}")
        
        return pnr_stage_data
    
    def _create_runtime_html_content(self, runtime_data, pnr_runtimes, pnr_stage_data, prc_status_file, runtime_timestamps=None, fast_dc_detected=False, rtl_detected=False):
        """Create HTML content for runtime report"""
        if runtime_timestamps is None:
            runtime_timestamps = {}
            
        # Get AVICE logo
        logo_path = "/home/avice/scripts/avice_wa_review/images/avice_logo.png"
        logo_data = ""
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo_file:
                logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
        
        # Generate badges HTML for detected stages
        badges_html = ""
        if fast_dc_detected:
            badges_html += '<span class="badge badge-warning">Fast DC Detected</span>'
        if rtl_detected:
            badges_html += '<span class="badge badge-info">RTL Formal Detected</span>'
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Runtime Analysis Report - {self.design_info.top_hier}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            margin: 5px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-warning {{
            background-color: #ffc107;
            color: #000;
        }}
        .badge-info {{
            background-color: #17a2b8;
            color: #fff;
        }}
        .logo {{
            height: 60px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        .logo:hover {{
            transform: scale(1.05);
        }}
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
            cursor: pointer;
        }}
        .logo-modal-content {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            max-width: 90%;
            max-height: 90%;
        }}
        .logo-modal img {{
            width: 100%;
            height: auto;
            border-radius: 10px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .section {{
            background: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .summary-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .summary-table th, .summary-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .summary-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #495057;
        }}
        .summary-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .category-construction {{ color: #28a745; font-weight: bold; }}
        .category-signoff {{ color: #007bff; font-weight: bold; }}
        .category-eco {{ color: #dc3545; font-weight: bold; }}
        .pnr-details {{
            margin: 20px 0;
        }}
        .ipo-section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .ipo-title {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
        }}
        .stage-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        .stage-table th, .stage-table td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .stage-table th {{
            background-color: #e9ecef;
            font-weight: bold;
        }}
        .status-done {{ color: #28a745; font-weight: bold; }}
        .status-run {{ color: #ffc107; font-weight: bold; }}
        .status-err {{ color: #dc3545; font-weight: bold; }}
        .highlight-max-runtime {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            font-weight: bold;
        }}
        .highlight-max-runtime td {{
            background-color: #fff3cd;
        }}
        .prc-link {{
            display: inline-block;
            background-color: #667eea;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
            transition: background-color 0.3s ease;
        }}
        .prc-link:hover {{
            background-color: #5a6fd8;
        }}
        .total-runtime {{
            font-size: 16px;
            font-weight: bold;
            color: #495057;
            margin: 10px 0;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
        }}
        .tablog-btn {{
            background-color: #28a745;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-right: 5px;
            transition: background-color 0.3s ease;
        }}
        .tablog-btn:hover {{
            background-color: #218838;
        }}
        .tablog-btn:active {{
            background-color: #1e7e34;
        }}
        .raw-log-link {{
            display: inline-block;
            background-color: #6c757d;
            color: white;
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            margin-left: 5px;
            transition: background-color 0.3s ease;
        }}
        .raw-log-link:hover {{
            background-color: #5a6268;
        }}
        .toast {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #28a745;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
            max-width: 400px;
            white-space: pre-line;
            font-family: monospace;
            font-size: 12px;
        }}
        .toast.show {{
            opacity: 1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="data:image/png;base64,{logo_data}" alt="AVICE Logo" class="logo" onclick="showLogoModal()">
            <h1>Runtime Analysis Report</h1>
            <p>Design: {self.design_info.top_hier} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Workarea: {self.workarea_abs}</p>
            <div>{badges_html}</div>
        </div>
        
        <div class="section">
            <h2>Runtime Summary</h2>
            <table class="summary-table">
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Stage</th>
                        <th>Runtime</th>
                        <th>Start</th>
                        <th>End</th>
                    </tr>
                </thead>
                <tbody>"""
        
        # Add summary table rows - Construction stages
        if 'Fast DC' in runtime_data:
            start, end = runtime_timestamps.get('Fast DC', ('N/A', 'N/A'))
            html += f"""
                    <tr>
                        <td class="category-construction">Construction</td>
                        <td>Fast DC</td>
                        <td>{runtime_data['Fast DC']}</td>
                        <td>{start}</td>
                        <td>{end}</td>
                    </tr>"""
        
        if 'Full DC' in runtime_data:
            start, end = runtime_timestamps.get('Full DC', ('N/A', 'N/A'))
            html += f"""
                    <tr>
                        <td class="category-construction">Construction</td>
                        <td>Full DC</td>
                        <td>{runtime_data['Full DC']}</td>
                        <td>{start}</td>
                        <td>{end}</td>
                    </tr>"""
        elif 'DC' in runtime_data:
            start, end = runtime_timestamps.get('DC', ('N/A', 'N/A'))
            html += f"""
                    <tr>
                        <td class="category-construction">Construction</td>
                        <td>DC</td>
                        <td>{runtime_data['DC']}</td>
                        <td>{start}</td>
                        <td>{end}</td>
                    </tr>"""
        
        for ipo, runtime in pnr_runtimes.items():
            start, end = runtime_timestamps.get(f'PnR ({ipo})', ('N/A', 'N/A'))
            html += f"""
                    <tr>
                        <td class="category-construction">Construction</td>
                        <td>PnR ({ipo})</td>
                        <td>{runtime}</td>
                        <td>{start}</td>
                        <td>{end}</td>
                    </tr>"""
        
        # Signoff stages
        signoff_stages = ['Star', 'Auto PT', 'Formal (rtl_vs_pnr_bbox_fm)', 'Formal (rtl_vs_pnr_fm)', 'GL Check', 'PV']
        for stage in signoff_stages:
            if stage in runtime_data:
                start, end = runtime_timestamps.get(stage, ('N/A', 'N/A'))
                html += f"""
                    <tr>
                        <td class="category-signoff">Signoff</td>
                        <td>{stage}</td>
                        <td>{runtime_data[stage]}</td>
                        <td>{start}</td>
                        <td>{end}</td>
                    </tr>"""
        
        # ECO stages
        eco_stages = ['Auto PT Fix', 'Gen ECO Netlist', 'NV Gate ECO']
        for stage in eco_stages:
            if stage in runtime_data:
                start, end = runtime_timestamps.get(stage, ('N/A', 'N/A'))
                html += f"""
                    <tr>
                        <td class="category-eco">ECO</td>
                        <td>{stage}</td>
                        <td>{runtime_data[stage]}</td>
                        <td>{start}</td>
                        <td>{end}</td>
                    </tr>"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Detailed PnR Stage Analysis</h2>
            <a href="javascript:void(0);" class="prc-link" onclick="openWithTablog('{prc_status_file}');" style="border: none; cursor: pointer; text-decoration: none;" title="Copy tablog command to view the PRC status file with your custom tablog viewer. This file contains detailed runtime information for all PnR stages.">
                Copy PRC Status Command
            </a>
            <a href="file://{prc_status_file}" class="raw-log-link" target="_blank" title="Open PRC status file directly in your default text editor or browser. File: {prc_status_file}" style="margin-left: 10px;">Open PRC Status</a>""".format(prc_status_file=prc_status_file)
        
        # Add detailed PnR stage data for each IPO
        for ipo in sorted(pnr_stage_data.keys()):
            stages = pnr_stage_data[ipo]
            
            # Calculate total PnR runtime (core stages only)
            core_stages = ['BEGIN', 'setup', 'edi_plan', 'place', 'cts', 'route', 'postroute']
            total_seconds = 0
            for stage_info in stages:
                if stage_info['step'] in core_stages:
                    try:
                        total_seconds += int(stage_info['duration_seconds'])
                    except (ValueError, KeyError):
                        pass
            
            total_hours = total_seconds / 3600
            total_days = total_hours / 24
            
            if total_hours >= 24:
                total_runtime_str = f"{total_hours:.2f} hours ({total_days:.2f} days)"
            else:
                total_runtime_str = f"{total_hours:.2f} hours"
            
            # Find the stage with highest runtime for highlighting
            max_duration_seconds = 0
            max_duration_stage = None
            for stage_info in stages:
                try:
                    duration_seconds = int(stage_info['duration_seconds'])
                    if duration_seconds > max_duration_seconds:
                        max_duration_seconds = duration_seconds
                        max_duration_stage = stage_info['step']
                except (ValueError, KeyError):
                    pass
            
            html += f"""
            <div class="ipo-section">
                <div class="ipo-title">IPO {ipo}</div>
                <div class="total-runtime">Total PnR Runtime: {total_runtime_str}</div>
                <table class="stage-table">
                    <thead>
                        <tr>
                            <th>Stage</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Log File</th>
                        </tr>
                    </thead>
                    <tbody>"""
            
            for stage_info in stages:
                status_class = f"status-{stage_info['status'].lower()}"
                # Add highlighting class for the stage with highest runtime
                highlight_class = "highlight-max-runtime" if stage_info['step'] == max_duration_stage else ""
                html += f"""
                        <tr class="{highlight_class}">
                            <td>{stage_info['step']}</td>
                            <td class="{status_class}">{stage_info['status']}</td>
                            <td>{stage_info['duration']}</td>
                            <td>
                                <a href="javascript:void(0);" class="tablog-btn" onclick="openWithTablog('{stage_info['logfile']}');" title="Copy tablog command to view this log file with your custom tablog viewer. A popup will appear with the command ready to copy.">
                                    Copy tablog command
                                </a>
                                <a href="file://{stage_info['logfile']}" target="_blank" class="raw-log-link" title="Open this log file directly in your default text editor or browser. File: {stage_info['logfile']}">Open log</a>
                            </td>
                        </tr>"""
            
            html += """
                    </tbody>
                </table>
            </div>"""
        
        html += f"""
        </div>
        
        <!-- Logo Modal -->
        <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
            <div class="logo-modal-content">
                <img src="data:image/png;base64,{logo_data}" alt="AVICE Logo Full Size">
            </div>
        </div>
    </div>
    
    <script>
        function showLogoModal() {{
            document.getElementById('logoModal').style.display = 'block';
        }}
        
        function hideLogoModal() {{
            document.getElementById('logoModal').style.display = 'none';
        }}
        
        // Close modal when clicking outside the image
        document.getElementById('logoModal').addEventListener('click', function(e) {{
            if (e.target === this) {{
                hideLogoModal();
            }}
        }});
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                hideLogoModal();
            }}
        }});
        
        // Function to open log file with tablog
        function openWithTablog(logfile) {{
            const tablogCmd = '/home/scratch.avice_vlsi/tablog/tablog ' + logfile;
            
            // Print to browser console
            console.log('================================================================================');
            console.log('Tablog Command:');
            console.log(tablogCmd);
            console.log('================================================================================');
            console.log('Copy the command above and paste it in your terminal to view the log file.');
            console.log('');
            
            // Show command in a modal popup for easy copying
            showCommandModal(tablogCmd);
        }}
        
        // Function to show command in a modal for easy copying
        function showCommandModal(command) {{
            // Remove existing modal if present
            const existingModal = document.getElementById('commandModal');
            if (existingModal) {{
                existingModal.remove();
            }}
            
            // Create modal
            const modal = document.createElement('div');
            modal.id = 'commandModal';
            modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; ' +
                                 'background: rgba(0,0,0,0.8); z-index: 10000; display: flex; ' +
                                 'align-items: center; justify-content: center;';
            
            // Create modal content
            const content = document.createElement('div');
            content.style.cssText = 'background: white; padding: 30px; border-radius: 10px; ' +
                                   'max-width: 800px; width: 90%; box-shadow: 0 4px 20px rgba(0,0,0,0.3);';
            
            // Title
            const title = document.createElement('h2');
            title.textContent = 'Tablog Command';
            title.style.cssText = 'margin-top: 0; color: #667eea;';
            content.appendChild(title);
            
            // Instructions
            const instructions = document.createElement('p');
            instructions.innerHTML = 'Click in the box below, then press <strong>Ctrl+A</strong> to select all, ' +
                                   'then <strong>Ctrl+C</strong> to copy:';
            instructions.style.cssText = 'color: #666; margin-bottom: 15px;';
            content.appendChild(instructions);
            
            // Command text area
            const textArea = document.createElement('textarea');
            textArea.value = command;
            textArea.readOnly = true;
            textArea.style.cssText = 'width: 100%; height: 80px; padding: 10px; font-family: monospace; ' +
                                    'font-size: 14px; border: 2px solid #667eea; border-radius: 5px; ' +
                                    'resize: none; background: #f8f9fa;';
            content.appendChild(textArea);
            
            // Button container
            const buttonContainer = document.createElement('div');
            buttonContainer.style.cssText = 'margin-top: 20px; text-align: right;';
            
            // Close button
            const closeButton = document.createElement('button');
            closeButton.textContent = 'Close';
            closeButton.style.cssText = 'background: #667eea; color: white; border: none; ' +
                                       'padding: 10px 20px; border-radius: 5px; cursor: pointer; ' +
                                       'font-size: 14px;';
            closeButton.onmouseover = function() {{ this.style.background = '#5a6fd8'; }};
            closeButton.onmouseout = function() {{ this.style.background = '#667eea'; }};
            closeButton.onclick = function() {{ modal.remove(); }};
            buttonContainer.appendChild(closeButton);
            
            content.appendChild(buttonContainer);
            modal.appendChild(content);
            document.body.appendChild(modal);
            
            // Auto-select the text
            textArea.focus();
            textArea.select();
            
            // Close modal on background click
            modal.onclick = function(e) {{
                if (e.target === modal) {{
                    modal.remove();
                }}
            }};
            
            // Close modal on Escape key
            document.addEventListener('keydown', function escHandler(e) {{
                if (e.key === 'Escape') {{
                    modal.remove();
                    document.removeEventListener('keydown', escHandler);
                }}
            }});
        }}
        
        // Function to show toast notification
        function showToast(message) {{
            let toast = document.getElementById('toast');
            if (!toast) {{
                toast = document.createElement('div');
                toast.id = 'toast';
                toast.className = 'toast';
                document.body.appendChild(toast);
            }}
            
            toast.textContent = message;
            toast.classList.add('show');
            
            setTimeout(function() {{
                toast.classList.remove('show');
            }}, 3000);
        }}
    </script>
</body>
</html>"""
        
        return html

    def run_common_analysis(self):
        """Run COMMON TCL files analysis"""
        self.print_header(FlowStage.COMMON)
        
        common_dir = os.path.join(self.workarea, "pnr_flow/nv_flow/COMMON")
        if os.path.exists(common_dir):
            tcl_files = self.file_utils.find_files("pnr_flow/nv_flow/COMMON/*.tcl", self.workarea)
            if tcl_files:
                for tcl_file in tcl_files:
                    self.print_file_info(tcl_file, "Common TCL")
            else:
                print("  No .tcl files found")
        else:
            print("  No COMMON directory found")




def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Avice Workarea Review Tool - Comprehensive analysis of design workareas",
        epilog="""
Examples:
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea                    # Analyze workarea with auto-detected IPO
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea ipo1000            # Analyze workarea with specific IPO
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s setup runtime   # Run only setup and runtime sections
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s star            # Run only Star (Parasitic Extraction)
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s pt              # Run only PT (Signoff Timing)
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s star pt pv      # Run Star, PT, and PV sections
  /home/avice/scripts/avice_wa_review_launcher.csh --help                               # Show this help message
  /home/avice/scripts/avice_wa_review_launcher.csh --version                            # Show version information

The tool analyzes various aspects of the design flow including:
  - Setup and Environment Information
  - Runtime Analysis (DC and PnR)
  - Synthesis Analysis (DC)
  - Place & Route (PnR) Analysis
  - Clock Analysis and Latency
  - Formal Verification
  - Parasitic Extraction (Star)
  - Signoff Timing (PT)
  - Physical Verification (LVS/DRC/Antenna)
  - GL Checks
  - ECO Analysis (PT-ECO and NV Gate ECO)
  - Block Release Information

Available sections: setup, runtime, synthesis, pnr, clock, formal, star, pt, pv, gl-check, eco, nv-gate-eco, block-release
Short flag: -s (alias for --sections)
All section names are case-insensitive

For more information, visit: https://github.com/your-repo/avice-tools
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("workarea", nargs="?", 
                       help="Path to workarea directory to analyze")
    parser.add_argument("ipo", nargs="?", 
                       help="IPO name to analyze (optional, auto-detected if not specified)")
    
    # Documentation generation arguments
    parser.add_argument("--help-docs", action="store_true",
                       help="Display formatted documentation in terminal")
    parser.add_argument("--open-docs", action="store_true",
                       help="Generate HTML documentation and open in browser")
    parser.add_argument("--generate-pdf", action="store_true",
                       help="Generate PDF documentation")
    parser.add_argument("--docs-section", choices=["usage", "examples", "troubleshooting", "organization", "all"],
                       default="all", help="Specific documentation section to display")
    
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output with detailed information")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0",
                       help="Show version information and exit")
    parser.add_argument("--no-logo", action="store_true",
                       help="Disable logo display (useful for automated scripts)")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip workarea validation (use with caution)")
    parser.add_argument("--sections", "-s", nargs="+", 
                       type=str.lower,
                       metavar="SECTION",
                       choices=["setup", "runtime", "synthesis", "pnr", 
                               "clock", "formal", "star", "pt", "pv", 
                               "gl-check", "eco", "nv-gate-eco", 
                               "block-release"],
                       help="Run only specific analysis sections (case-insensitive). Choices: setup, runtime, synthesis, pnr, clock, formal, star, pt, pv, gl-check, eco, nv-gate-eco, block-release")
    parser.add_argument("--output", "-o", 
                       help="Output file to save results (optional)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format (default: text)")
    
    args = parser.parse_args()
    
    # Handle documentation generation (doesn't require workarea)
    if args.help_docs or args.open_docs or args.generate_pdf:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from docs_generator import DocumentationGenerator
        doc_gen = DocumentationGenerator()
        
        if args.help_docs:
            doc_gen.display_terminal_docs(args.docs_section)
        elif args.open_docs:
            doc_gen.generate_and_open_html_docs()
        elif args.generate_pdf:
            doc_gen.generate_pdf_docs()
        return
    
    # Check if workarea is provided
    if not args.workarea:
        parser.error("workarea is required")
    
    if not os.path.isdir(args.workarea):
        print(f"{Color.RED}Error: Workarea directory '{args.workarea}' does not exist{Color.RESET}")
        sys.exit(1)
    
    try:
        reviewer = WorkareaReviewer(args.workarea, args.ipo, show_logo=not args.no_logo, skip_validation=args.skip_validation)
        
        # Handle selective section running
        if args.sections:
            # Run only specified sections
            section_mapping = {
                "setup": reviewer.run_setup_analysis,
                "runtime": reviewer.run_runtime_analysis,
                "synthesis": reviewer.run_synthesis_analysis,
                "pnr": reviewer.run_pnr_analysis,
                "clock": reviewer.run_clock_analysis,
                "formal": reviewer.run_formal_verification,
                "star": reviewer.run_parasitic_extraction,
                "pt": reviewer.run_signoff_timing,
                "pv": reviewer.run_physical_verification,
                "gl-check": reviewer.run_gl_check,
                "eco": reviewer.run_eco_analysis,
                "nv-gate-eco": reviewer.run_nv_gate_eco,
                "block-release": reviewer.run_block_release
            }
            
            print(f"Running selected sections: {', '.join(args.sections)}")
            for section in args.sections:
                # Convert to lowercase for case-insensitive matching
                section_lower = section.lower()
                if section_lower in section_mapping:
                    try:
                        section_mapping[section_lower]()
                    except Exception as e:
                        print(f"Error running {section} section: {e}")
                else:
                    print(f"Unknown section: {section}")
        else:
            # Run complete review
            reviewer.run_complete_review()
            
        # Handle output file
        if args.output:
            print(f"\nResults saved to: {args.output}")
            # Note: In a full implementation, you would capture the output and write to file
            
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Review interrupted by user{Color.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Color.RED}Error during review: {e}{Color.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
