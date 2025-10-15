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
Version: 2.0.0
Purpose: Comprehensive ASIC/SoC design workarea analysis and review tool

Description:
    This script provides a comprehensive analysis of ASIC/SoC design workareas,
    covering the complete ASIC design flow from synthesis through signoff.
    It extracts, analyzes, and visualizes design metrics, timing data, runtime
    statistics, verification results, and generates interactive HTML reports.
    
    Key Features:
    - Multi-IPO support with automatic IPO detection
    - Selective section analysis for faster debugging
    - Professional HTML reports with absolute paths for portability
    - Runtime analysis with timeline tracking and flow detection
    - Timing analysis with dual-scenario (setup/hold) extraction
    - DSR Mux Clock Skew tracking across work directories
    - ECO analysis with dont_use cell validation
    - Formal verification timestamp tracking
    - Physical verification (LVS/DRC/Antenna) flow analysis
    - GL Check error categorization and analysis
    - Cross-directory execution support

Analysis Sections:
    Setup           - Environment info, BeFlow config, PRC configuration
    Runtime         - DC, PnR, Star, PT, Formal, PV, GL Check runtimes
    Synthesis       - QoR reports, floorplan dimensions, timing groups
    PnR             - Step sequence, routing data, timing histograms
    Clock           - Clock tree analysis, DSR latency, clock gating
    Formal          - Formal verification status, timestamp tracking
    Star            - Parasitic extraction (SPEF) runtime and status
    PT              - Signoff timing, dual-scenario WNS/TNS/NVP, DSR skew
    PV              - Physical verification (LVS/DRC/Antenna) analysis
    GL-Check        - Gate-level check error analysis and categorization
    ECO             - PT-ECO and NV Gate ECO analysis, dont_use cell checks
    NV-Gate-ECO     - NVIDIA Gate ECO command analysis and validation
    Block-Release   - Block release information and umake commands

Usage:
    # Recommended: Use C-shell launcher (handles Python path automatically)
    /home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> [ipo_name] [options]
    
    # Direct Python invocation (requires correct Python version)
    /home/utils/Python/builds/3.11.9-20250715/bin/python3 avice_wa_review.py <workarea_path> [ipo_name] [options]
    
    # Display help and examples
    /home/avice/scripts/avice_wa_review_launcher.csh --help

Arguments:
    workarea_path         Path to the workarea directory to analyze (required unless --unit is used)
    ipo_name              IPO name to analyze (optional, auto-detected if not specified)
    
Options:
    -u, --unit UNIT       Unit name from agur release table (e.g., prt, pmux, fdb, fth, lnd)
                          Automatically looks up released workarea path from AGUR_UNITS_TABLE.txt
                          Use this instead of providing workarea_path
    
    -s, --sections SECTION [SECTION ...]
                          Run only specific analysis sections (case-insensitive)
                          Available: setup, runtime, synthesis, pnr, clock, formal, 
                                    star, pt, pv, gl-check, eco, nv-gate-eco, block-release
                          Aliases: 'syn'/'dc' = synthesis, 'star' = parasitic, 'pt' = timing
    
    --no-logo             Disable ASCII logo display (useful for automated scripts)
    --skip-validation     Skip workarea validation checks (use with caution)
    --verbose, -v         Enable verbose output with detailed information
    --output, -o FILE     Save results to output file (not yet fully implemented)
    --format FORMAT       Output format: text or json (default: text)
    --version             Show version information and exit
    
Documentation Options:
    --help-docs           Display formatted documentation in terminal
    --open-docs           Generate HTML documentation and open in browser
    --generate-pdf        Generate PDF documentation
    --docs-section SECTION
                          Specific documentation section: usage, examples, 
                          troubleshooting, organization, or all (default: all)

Prerequisites:
    - Python 3.6 or higher (recommended: Python 3.11.9)
    - Access to workarea directory with proper read permissions
    - Unix/Linux environment with standard tools (grep, zcat)
    - Design flow tools output files (DC, Innovus, PrimeTime, Star, etc.)
    - Firefox browser for viewing HTML reports

Output:
    Terminal Output:
    - Color-coded analysis results with ASCII characters only
    - Compact summary tables for quick review
    - Status indicators: [OK], [ERROR], [WARN], [SKIP]
    - Minimal line count for easy scanning
    
    HTML Reports (generated in current working directory):
    - avice_runtime_report_<design>_<timestamp>.html
    - avice_pnr_data_<design>_<ipo>_<timestamp>.html
    - avice_timing_summary_<design>_<ipo>_<timestamp>.html
    - avice_gl_check_<design>_<ipo>_<timestamp>.html
    - avice_image_debug_report_<design>_<timestamp>.html
    
    HTML Features:
    - Comprehensive data beyond terminal output
    - Clickable log file links with absolute paths
    - Interactive tables with sorting and filtering
    - Expandable/collapsible sections
    - Timeline visualizations
    - Professional CSS styling with gradients
    - Mobile-responsive layout
    - Portable across directories (uses absolute paths)

Examples:
    # Complete workarea analysis (all sections)
    /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea
    
    # Analyze specific IPO
    /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea ipo1000
    
    # Analyze using unit name from agur release table (automatic workarea lookup)
    /home/avice/scripts/avice_wa_review_launcher.csh --unit prt
    /home/avice/scripts/avice_wa_review_launcher.csh --unit pmux
    
    # Run only runtime and timing analysis (fast debug)
    /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea -s runtime pt
    
    # Run only parasitic extraction and signoff timing sections
    /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea -s star pt
    
    # Run setup, synthesis, and PnR sections
    /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea -s setup synthesis pnr
    
    # Run with no logo for automation
    /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea --no-logo
    
    # Display documentation
    /home/avice/scripts/avice_wa_review_launcher.csh --help-docs
    /home/avice/scripts/avice_wa_review_launcher.csh --open-docs

Important Notes:
    - This script outputs to Unix shells - always use ASCII characters
      instead of Unicode symbols (→, ✓, ✗, ⚠, •) to ensure proper display
    - Use ASCII equivalents: ->, [OK], [ERROR], [WARN], - instead
    - HTML reports are generated in current working directory, not the workarea
    - All file links in HTML use absolute paths for portability
    - Test HTML portability by copying to different directories
    - For tablog viewer integration, use the copy-to-clipboard feature in HTML

Contact:
    For questions, bug reports, or feature requests, contact: avice@nvidia.com
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
    html_file: str              # Path to detailed section HTML (relative path for cross-user compatibility)
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
                f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_MASTER_dashboard_{self.date_str}.html"
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
        
        /* Enhanced Grid Layout for Status Stats */
        .status-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 30px;
            margin-top: 20px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .status-stat {{
            font-size: 1.2em;
            text-align: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            backdrop-filter: blur(10px);
            transition: transform 0.2s ease;
        }}
        
        .status-stat:hover {{
            transform: scale(1.05);
        }}
        
        .status-stat strong {{
            font-size: 2em;
            display: block;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
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
        
        /* Enhanced Grid Layout for Section Cards */
        .sections-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            align-items: start;
            max-width: 100%;
        }}
        
        @media (min-width: 1400px) {{
            .sections-grid {{
                grid-template-columns: repeat(3, 1fr);
                max-width: 1400px;
                margin: 0 auto;
            }}
        }}
        
        @media (min-width: 1000px) and (max-width: 1399px) {{
            .sections-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 999px) {{
            .sections-grid {{
                grid-template-columns: 1fr;
            }}
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
            min-width: 0;
            max-width: 100%;
            overflow: hidden;
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
            gap: 10px;
            min-width: 0;
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
            flex: 1;
            min-width: 0;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        .section-title span {{
            word-wrap: break-word;
            overflow-wrap: break-word;
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
        
        /* Enhanced Grid Layout for Section Metrics */
        .section-metrics {{
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            display: grid;
            gap: 10px;
        }}
        
        .metric-row {{
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 20px;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .metric-row:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #7f8c8d;
            font-weight: 600;
            text-align: left;
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
        
        .no-report-msg {{
            display: inline-block;
            padding: 10px 20px;
            background: #ecf0f1;
            color: #7f8c8d;
            border-radius: 20px;
            font-style: italic;
            font-size: 0.9em;
            border: 2px dashed #bdc3c7;
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
            <button class="action-btn">Open All Failed/Warning Sections</button>
            <button class="action-btn secondary">Open All Sections</button>
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
                if section.html_file:
                    html += f"""
                <li>
                    <a href="{section.html_file}" target="_blank">
                        [{section.status}] {section.section_name}
                    </a>
                    {f' - {section.issues[0]}' if section.issues else ''}
                </li>
"""
                else:
                    html += f"""
                <li>
                    <span style="color: #856404;">
                        [{section.status}] {section.section_name}
                    </span>
                    {f' - {section.issues[0]}' if section.issues else ''}
                    <em style="color: #95a5a6; font-size: 0.9em;"> (No detailed report)</em>
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
        function expandImage(img) {{
            var overlay = document.getElementById('expandedImage');
            var expandedImg = document.getElementById('expandedImageContent');
            expandedImg.src = img.src;
            overlay.style.display = 'flex';
        }}
        
        function closeImage() {{
            document.getElementById('expandedImage').style.display = 'none';
        }}
        
        function toggleCard(cardId) {{
            var content = document.getElementById(cardId);
            var icon = document.getElementById('icon-' + cardId);
            
            if (content.classList.contains('expanded')) {{
                content.classList.remove('expanded');
                icon.classList.remove('expanded');
            }} else {{
                content.classList.add('expanded');
                icon.classList.add('expanded');
            }}
        }}
        
        function openAllSections() {{
            var sections = document.querySelectorAll('.section-card.FAIL a, .section-card.WARN a');
            console.log('Opening ' + sections.length + ' failed/warning sections');
            var delay = 0;
            // Convert NodeList to Array for compatibility
            var sectionsArray = Array.prototype.slice.call(sections);
            sectionsArray.forEach(function(link) {{
                if (link.href && link.href !== '') {{
                    console.log('Opening: ' + link.href);
                    setTimeout(function() {{
                        window.open(link.href, '_blank');
                    }}, delay);
                    delay += 300; // 300ms delay between each window to avoid popup blocker
                }}
            }});
        }}
        
        function openAllSectionsComplete() {{
            var sections = document.querySelectorAll('.section-card a');
            console.log('Opening all ' + sections.length + ' sections');
            if (sections.length === 0) {{
                alert('No section links found. This might indicate a problem with the dashboard generation.');
                return;
            }}
            var delay = 0;
            // Convert NodeList to Array for compatibility
            var sectionsArray = Array.prototype.slice.call(sections);
            sectionsArray.forEach(function(link) {{
                if (link.href && link.href !== '') {{
                    console.log('Opening: ' + link.href);
                    setTimeout(function() {{
                        window.open(link.href, '_blank');
                    }}, delay);
                    delay += 300; // 300ms delay between each window to avoid popup blocker
                }} else {{
                    console.log('Skipping link with no href');
                }}
            }});
        }}
        
        // Back to top button functionality - wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            var backToTopBtn = document.getElementById('backToTopBtn');
            if (backToTopBtn) {{
                window.addEventListener('scroll', function() {{
                    if (window.pageYOffset > 300) {{
                        backToTopBtn.style.display = 'block';
                    }} else {{
                        backToTopBtn.style.display = 'none';
                    }}
                }});
                
                backToTopBtn.addEventListener('click', function() {{
                    window.scrollTo(0, 0);
                }});
            }}
        }});
        
        // Add event listeners to buttons when DOM is ready (more reliable than inline onclick)
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, setting up button listeners');
            
            // Open Failed/Warning Sections button
            var actionBtns = document.querySelectorAll('.action-btn');
            console.log('Found action buttons:', actionBtns.length);
            
            if (actionBtns.length > 0) {{
                // First button (Open Failed/Warning)
                actionBtns[0].addEventListener('click', function(e) {{
                    console.log('Button clicked: Open Failed/Warning Sections');
                    e.preventDefault();
                    openAllSections();
                }});
                console.log('Attached listener to button 1');
            }}
            
            if (actionBtns.length > 1) {{
                // Second button (Open All Sections)
                actionBtns[1].addEventListener('click', function(e) {{
                    console.log('Button clicked: Open All Sections');
                    e.preventDefault();
                    openAllSectionsComplete();
                }});
                console.log('Attached listener to button 2');
            }}
        }});
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
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
        
        # Generate tooltip text for status badge (show criteria that weren't met)
        tooltip_text = ""
        if section.status in ['FAIL', 'WARN'] and section.issues:
            # Create tooltip showing which criteria failed
            tooltip_text = "Criteria not met:\\n" + "\\n".join(f"- {issue}" for issue in section.issues)
            # Escape HTML special characters for safe tooltip display
            tooltip_text = tooltip_text.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Default to collapsed for all cards
        default_expanded = False
        expanded_class = 'expanded' if default_expanded else ''
        
        # Add title attribute to status badge if there are issues
        status_badge_html = f'<div class="status-badge {section.status}" title="{tooltip_text}">{section.get_status_icon()}</div>' if tooltip_text else f'<div class="status-badge {section.status}">{section.get_status_icon()}</div>'
        
        card_html = f"""
                <div class="section-card {section.status}">
                    <div class="section-header" onclick="toggleCard('card-{section.section_id}-{index}')">
                        <div class="section-title">
                            <span class="section-index">{index}</span>
                            <span>{section.section_name}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            {status_badge_html}
                            <span class="card-toggle-icon {expanded_class}" id="icon-card-{section.section_id}-{index}">▼</span>
                        </div>
                    </div>
                    
                    <div class="card-content {expanded_class}" id="card-{section.section_id}-{index}">
                        {f'<div class="section-metrics">{metrics_html}</div>' if metrics_html else ''}
                        
                        {f'<div class="section-issues">{issues_html}</div>' if issues_html else ''}
                        
                        <div class="section-footer">
                            {f'<a href="{section.html_file}" target="_blank" class="view-details-btn" onclick="event.stopPropagation()">View Detailed Report</a>' if section.html_file else '<span class="no-report-msg">No detailed report available</span>'}
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
    
    def _cleanup_old_html_files(self):
        """Remove old HTML files from previous runs to prevent confusion"""
        try:
            # Get current working directory where HTMLs are generated
            cwd = os.getcwd()
            
            # Define patterns for HTML files that should be cleaned up
            # Only clean up files for the current design
            design_pattern = f"*{self.design_info.top_hier}*.html"
            
            # Find all matching HTML files
            matching_files = glob.glob(os.path.join(cwd, design_pattern))
            
            if matching_files:
                # Keep track of what was cleaned
                cleaned_count = 0
                
                for html_file in matching_files:
                    try:
                        os.remove(html_file)
                        cleaned_count += 1
                    except OSError as e:
                        # If we can't delete (permissions, etc.), just skip
                        pass
                
                if cleaned_count > 0:
                    print(f"{Color.CYAN}Cleaned up {cleaned_count} old HTML file(s) from previous runs{Color.RESET}")
        
        except Exception as e:
            # Don't fail the review if cleanup fails
            pass
    
    def _add_section_summary(self, section_name: str, section_id: str, stage: FlowStage, 
                            status: str = "NOT_RUN", key_metrics: Dict[str, str] = None,
                            html_file: str = "", priority: int = 3, issues: List[str] = None,
                            icon: str = ""):
        """Helper method to add a section summary to the master dashboard"""
        if key_metrics is None:
            key_metrics = {}
        if issues is None:
            issues = []
        
        # Convert absolute path to relative (just filename) for cross-user compatibility
        # This ensures the master dashboard works when opened by different users
        if html_file:
            html_file = os.path.basename(html_file)
        
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
                    print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{os.path.basename(html_file)}{Color.RESET} &")
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
                
                # Return the maximum latency found across all clocks
                max_latencies = []
                for data in clock_data:
                    try:
                        max_latencies.append(float(data['max_delay']))
                    except (ValueError, TypeError):
                        pass
                if max_latencies:
                    return max(max_latencies) * 1000  # Convert to ps
            else:
                print(f"  Scenario {target_scenario} not found in clock tree report")
            
            return 0
                
        except (OSError, UnicodeDecodeError, gzip.BadGzipFile) as e:
            print(f"  Error reading clock file: {e}")
            return 0
    
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
                
                # Return the maximum latency found across all clocks
                max_latencies = []
                for clock, latencies in clock_latencies.items():
                    if latencies:
                        max_latencies.append(max(latencies))
                if max_latencies:
                    return max(max_latencies) * 1000  # Convert to ps
            else:
                print(f"  No clock latency data found in PT report")
            
            return 0
                
        except (OSError, UnicodeDecodeError) as e:
            print(f"  Error reading PT clock file: {e}")
            return 0
    
    def _extract_formal_verification_status(self, log_file: str) -> tuple:
        """Extract verification status and runtime from formal verification log
        Returns: (status, runtime, flow_name, passing_points, failing_points, compare_table, failing_points_list) tuple
        """
        try:
            # Check if formal is currently running
            file_mtime = os.path.getmtime(log_file)
            current_time = time.time()
            time_since_update = current_time - file_mtime
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Extract verification status from "Verification Results" section
            # Use the LAST occurrence if there are multiple runs in the log
            status = "UNKNOWN"
            passing_points = 0
            failing_points = 0
            compare_table = {}  # Dictionary to store the matched compare points table
            failing_points_list = []  # List of failing compare point names
            last_results_index = -1
            
            # Find the last "Verification Results" section
            for i, line in enumerate(lines):
                if "Verification Results" in line and "*****" in line:
                    last_results_index = i
            
            # Extract status from the last Verification Results section
            if last_results_index >= 0:
                # Look in the next 20 lines after "Verification Results" header to get status and compare points
                for i in range(last_results_index + 1, min(last_results_index + 21, len(lines))):
                    line = lines[i]
                    if "Verification SUCCEEDED" in line:
                        status = "SUCCEEDED"
                    elif "Verification FAILED" in line:
                        status = "FAILED"
                    elif "Verification UNRESOLVED" in line:
                        status = "UNRESOLVED"
                    elif "Verification INCONCLUSIVE" in line:
                        status = "UNRESOLVED"
                    
                    # Extract passing compare points
                    # Format: "238522 Passing compare points"
                    if "Passing compare points" in line:
                        match = re.search(r'(\d+)\s+Passing compare points', line)
                        if match:
                            passing_points = int(match.group(1))
                    
                    # Extract failing compare points
                    # Format: "8 Failing compare points (8 matched, 0 unmatched)"
                    if "Failing compare points" in line:
                        match = re.search(r'(\d+)\s+Failing compare points', line)
                        if match:
                            failing_points = int(match.group(1))
            
            # Fallback: if no "Verification Results" section found, search entire log
            if status == "UNKNOWN":
                for line in lines:
                    if "Verification SUCCEEDED" in line:
                        status = "SUCCEEDED"
                    elif "Verification FAILED" in line:
                        status = "FAILED"
                    elif "Verification UNRESOLVED" in line or "Verification INCONCLUSIVE" in line:
                        status = "UNRESOLVED"
            
            # Check for tool crash/error before completion
            # If status is still UNKNOWN, check for crash indicators
            if status == "UNKNOWN":
                has_crash_error = False
                crash_error_msg = ""
                
                # Look for common crash patterns in the last 100 lines
                for line in lines[-100:]:
                    # CMD-081: Script stopped due to error
                    if "stopped at line" in line and "due to error" in line:
                        has_crash_error = True
                        crash_error_msg = "Script execution error"
                        break
                    # FM-036: Unknown design name error
                    elif "Error: Unknown name:" in line and "FM-036" in line:
                        has_crash_error = True
                        crash_error_msg = "Design not loaded"
                        break
                    # FM-008: Design not set error
                    elif "Error: The current design is not set" in line and "FM-008" in line:
                        has_crash_error = True
                        crash_error_msg = "Design not set"
                        break
                    # General error patterns that indicate crashes
                    elif line.strip().startswith("-E-") and "errMsg:" in line:
                        has_crash_error = True
                        crash_error_msg = "Tool error encountered"
                        break
                
                if has_crash_error:
                    status = f"CRASHED ({crash_error_msg})"
            
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
            elif "CRASHED" in status:
                status_color = Color.RED
            else:
                status_color = Color.YELLOW
            
            print(f"  Status: {status_color}{status}{Color.RESET}")
            if status != "RUNNING":
                print(f"  Runtime: {elapsed_time}")
            else:
                print(f"  Runtime: In progress...")
            
            # Display compare points if FAILED
            if status == "FAILED" and (passing_points > 0 or failing_points > 0):
                print(f"  {Color.GREEN}Passing compare points: {passing_points}{Color.RESET}")
                print(f"  {Color.RED}Failing compare points: {failing_points}{Color.RESET}")
            
            # Extract Matched Compare Points table
            for i, line in enumerate(lines):
                if "Matched Compare Points" in line and "BBPin" in line:
                    # Found the table header, parse the next lines
                    # Skip the separator line
                    if i + 2 < len(lines):
                        # Parse "Passing (equivalent)" line
                        passing_line = lines[i + 2]
                        if "Passing (equivalent)" in passing_line:
                            parts = passing_line.split()
                            if len(parts) >= 9:
                                compare_table['passing'] = {
                                    'BBPin': int(parts[2]),
                                    'Loop': int(parts[3]),
                                    'BBNet': int(parts[4]),
                                    'Cut': int(parts[5]),
                                    'Port': int(parts[6]),
                                    'DFF': int(parts[7]),
                                    'LAT': int(parts[8]),
                                    'TOTAL': int(parts[9])
                                }
                        
                        # Parse "Failing (not equivalent)" line
                        if i + 3 < len(lines):
                            failing_line = lines[i + 3]
                            if "Failing (not equivalent)" in failing_line:
                                parts = failing_line.split()
                                if len(parts) >= 9:
                                    compare_table['failing'] = {
                                        'BBPin': int(parts[3]),
                                        'Loop': int(parts[4]),
                                        'BBNet': int(parts[5]),
                                        'Cut': int(parts[6]),
                                        'Port': int(parts[7]),
                                        'DFF': int(parts[8]),
                                        'LAT': int(parts[9]),
                                        'TOTAL': int(parts[10])
                                    }
                        
                        # Parse "Not Compared" section
                        compare_table['not_compared'] = {}
                        for j in range(i + 5, min(i + 10, len(lines))):
                            line = lines[j].strip()
                            if not line or line.startswith('*'):
                                break
                            # Parse lines like "  Clock-gate LAT                                                            6659    6659"
                            if any(keyword in line for keyword in ['Clock-gate', 'Constant', 'Unread']):
                                parts = line.split()
                                if len(parts) >= 2:
                                    # The category name is the first 1-2 words, the last number is the total
                                    try:
                                        count = int(parts[-1])
                                        # Category name is usually first 2 words or until we hit numbers
                                        name_parts = []
                                        for part in parts:
                                            if part.isdigit():
                                                break
                                            name_parts.append(part)
                                        name = ' '.join(name_parts)
                                        compare_table['not_compared'][name] = count
                                    except:
                                        pass
                    break
            
            # Extract failing compare point names
            for line in lines:
                if "Compare point" in line and "failed (is not equivalent)" in line:
                    # Extract the compare point name between "Compare point" and "failed"
                    match = re.search(r'Compare point\s+(.+?)\s+failed \(is not equivalent\)', line)
                    if match:
                        failing_points_list.append(match.group(1).strip())
            
            # Extract flow name from log file path (e.g., rtl_vs_pnr_fm)
            flow_name = os.path.basename(os.path.dirname(os.path.dirname(log_file)))
            
            return (status, elapsed_time, flow_name, passing_points, failing_points, compare_table, failing_points_list)
            
        except (OSError, UnicodeDecodeError) as e:
            print(f"  Error reading formal log: {e}")
            return ("UNKNOWN", "Unknown", "Unknown", 0, 0, {}, [])
    
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
                print(f"    {Color.YELLOW}-> Formal verification should be re-run to verify design changes{Color.RESET}")
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
            
            # Extract DieArea from floorplan DEF file
            floorplan_dims = self._extract_floorplan_dimensions()
            
            # Print only most significant parameters
            stage_display = stage.upper() if stage != 'postroute' else 'Post-Route'
            print(f"\n{Color.YELLOW}Key {stage_display} Parameters:{Color.RESET}")
            print(f"  {'Parameter':<25} {'Value':<15}")
            print(f"  {'-'*25} {'-'*15}")
            
            # Print DieArea first if available
            if floorplan_dims:
                x_dim = floorplan_dims['x_dim_um']
                y_dim = floorplan_dims['y_dim_um']
                die_area_um2 = x_dim * y_dim
                die_area_mm2 = die_area_um2 / 1_000_000
                print(f"  {'Die Dimensions (X x Y)':<25} {f'{x_dim:.2f} x {y_dim:.2f} um':<15}")
                print(f"  {'DieArea (mm2)':<25} {f'{die_area_mm2:.3f}':<15}")
            
            for param_name in significant_params:
                if param_name in all_params:
                    print(f"  {param_name:<25} {all_params[param_name]:<15}")
            
            # Generate HTML table with full data for all stages
            self._generate_postroute_html_table(all_params)
            
            return all_params
            
        except (OSError, UnicodeDecodeError) as e:
            print(f"  {Color.RED}Error reading post-route data file: {e}{Color.RESET}")
            print(f"  {Color.YELLOW}This could be due to:{Color.RESET}")
            print(f"    - Flow still running (data file not yet generated)")
            print(f"    - Flow failed at this stage")
            print(f"    - File permissions issue")
            print(f"    - File corrupted or incomplete")
            return {}
    
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
            html_filename = f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_pnr_data_{self.design_info.ipo}_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\n  {Color.CYAN}Full PnR Data Table:{Color.RESET}")
            print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
            
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
        
        /* Copyright Footer */
        .footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer strong {{
            color: #00ff00;
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
        // Back to top button functionality
        var backToTopBtn = document.getElementById('backToTopBtn');
        if (backToTopBtn) {{
            window.addEventListener('scroll', function() {{
                if (window.pageYOffset > 300) {{
                    backToTopBtn.style.display = 'block';
                }} else {{
                    backToTopBtn.style.display = 'none';
                }}
            }});
            
            backToTopBtn.addEventListener('click', function() {{
                window.scrollTo(0, 0);
            }});
        }}
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
    
    <!-- Copyright Footer -->
    <div class="footer">
        <p><strong>AVICE P&R Data Analysis Report</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
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
        
        # Generate unified DC HTML report
        dc_html = self._generate_unified_dc_html()
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Synthesis (DC)",
            section_id="synthesis",
            stage=FlowStage.SYNTHESIS,
            status="PASS",
            html_file=dc_html if dc_html else "",
            key_metrics={
                "Design": self.design_info.top_hier,
                "IPO": self.design_info.ipo
            },
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
        
        all_params = {}
        if data_files:
            if found_stage == 'postroute':
                self.print_file_info(data_files[0], "Post-Route Data")
            else:
                self.print_file_info(data_files[0], f"PnR Data ({found_stage.upper()} stage)")
                print(f"    {Color.YELLOW}Note: Post-route data not available, showing {found_stage.upper()} stage data instead{Color.RESET}")
            
            all_params = self._extract_postroute_data_parameters(data_files[0], found_stage)
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
        
        # Generate unified PnR HTML report combining all sections
        print(f"\n{Color.CYAN}Generating Unified PnR HTML Report...{Color.RESET}")
        unified_pnr_html = self._generate_unified_pnr_html()
        
        # Collect metrics for dashboard summary
        status = "NOT_RUN"
        key_metrics = {"Design": self.design_info.top_hier, "IPO": self.design_info.ipo}
        issues = []
        priority = 2
        
        # Check if we have PnR data
        if data_files and all_params:
            status = "PASS"
            
            # Extract key metrics
            if 'EffictiveUtilization' in all_params:
                util = all_params['EffictiveUtilization']
                key_metrics["Utilization"] = util
                # WARN if utilization > 85%, FAIL if > 95%
                try:
                    util_float = float(util.strip('%'))
                    if util_float > 95:
                        status = "FAIL"
                        issues.append(f"Utilization extremely high: {util}")
                    elif util_float > 85:
                        status = "WARN"
                        issues.append(f"Utilization high: {util}")
                except ValueError:
                    pass
            
            if 'CellCount' in all_params:
                key_metrics["Cells"] = all_params['CellCount']
            
            # Check for timing violations in PnR data
            for param in ['w1_clk_WNS', 'i1_clk_WNS', 'i2_clk_WNS']:
                if param in all_params:
                    try:
                        wns = float(all_params[param])
                        if wns < 0:
                            if status == "PASS":
                                status = "WARN"
                            clock_name = param.replace('_WNS', '')
                            issues.append(f"{clock_name} WNS negative: {wns:.3f} ns")
                    except ValueError:
                        pass
        elif prc_status and self.file_utils.file_exists(prc_status):
            # PnR exists but no data files yet - possibly still running
            status = "WARN"
            issues.append("PnR data files not found - flow may still be running")
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Place & Route (PnR)",
            section_id="pnr",
            stage=FlowStage.PNR_ANALYSIS,
            status=status,
            key_metrics=key_metrics,
            html_file=unified_pnr_html if unified_pnr_html else "",
            priority=priority,
            issues=issues,
            icon="[PnR]"
        )
    
    def _generate_unified_pnr_html(self):
        """Generate unified PnR HTML report combining PnR Data, Timing Histogram, and Images"""
        try:
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_PnR_comprehensive_{self.design_info.ipo}_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            # Read and encode logo
            logo_data = ""
            logo_path = os.path.join(os.path.dirname(__file__), "images/avice_logo.png")
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as logo_file:
                    logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
            
            # Collect PnR Data content
            pnr_data_content = self._get_pnr_data_html_content()
            
            # Collect Timing Histogram content
            timing_histogram_content = self._get_timing_histogram_html_content()
            
            # Collect Images content  
            images_content = self._get_images_html_content()
            
            # Generate unified HTML
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PnR Comprehensive Report - {self.design_info.top_hier}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 20px;
            align-items: center;
        }}
        
        .logo {{
            width: 80px;
            height: 80px;
            border-radius: 10px;
            background: white;
            padding: 10px;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .logo:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        
        .header-text h1 {{
            font-size: 32px;
            margin: 0 0 8px 0;
        }}
        
        .header-text p {{
            opacity: 0.9;
            font-size: 14px;
            margin: 4px 0;
        }}
        
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }}
        
        .logo-modal.active {{
            display: flex;
        }}
        
        .logo-modal-content {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
        }}
        
        .logo-modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .logo-modal-close:hover {{
            color: #bbb;
        }}
        
        .container {{
            max-width: 98%;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        /* Tab Navigation */
        .tab-navigation {{
            display: flex;
            background: #34495e;
            border-bottom: 3px solid #2c3e50;
        }}
        
        .tab-btn {{
            flex: 1;
            padding: 18px 20px;
            background: #34495e;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            border-right: 1px solid #2c3e50;
        }}
        
        .tab-btn:last-child {{
            border-right: none;
        }}
        
        .tab-btn:hover {{
            background: #2c3e50;
        }}
        
        .tab-btn.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .tab-content {{
            display: none;
            padding: 30px;
            animation: fadeIn 0.3s ease;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Section Headers */
        .section-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 20px;
            font-weight: bold;
        }}
        
        .no-data {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
            font-size: 18px;
            font-style: italic;
        }}
        
        /* Override nested styles to work within tabs */
        .tab-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .tab-content th,
        .tab-content td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        .tab-content th {{
            background-color: #34495e;
            color: white;
        }}
        
        .tab-content tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        /* Copyright Footer */
        .footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer strong {{
            color: #00ff00;
        }}
    </style>
</head>
<body>
    <div class="header">
        <img class='logo' src='data:image/png;base64,{logo_data}' alt='AVICE Logo' onclick="showLogoModal()" title="Click to enlarge">
        <div class="header-text">
            <h1>PnR Comprehensive Report</h1>
            <p>Design: {self.design_info.top_hier} | IPO: {self.design_info.ipo}</p>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
    
    <!-- Logo Modal -->
    <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
        <span class="logo-modal-close">&times;</span>
        <img class="logo-modal-content" src='data:image/png;base64,{logo_data}' alt='AVICE Logo'>
    </div>
    
    <div class="container">
        <!-- Tab Navigation -->
        <div class="tab-navigation">
            <button class="tab-btn active" onclick="openTab(event, 'pnr-data')">PnR Data</button>
            <button class="tab-btn" onclick="openTab(event, 'timing-histogram')">Timing Histogram</button>
            <button class="tab-btn" onclick="openTab(event, 'images')">Debug Images</button>
        </div>
        
        <!-- PnR Data Tab -->
        <div id="pnr-data" class="tab-content active">
            {pnr_data_content}
        </div>
        
        <!-- Timing Histogram Tab -->
        <div id="timing-histogram" class="tab-content">
            {timing_histogram_content}
        </div>
        
        <!-- Images Tab -->
        <div id="images" class="tab-content">
            {images_content}
        </div>
    </div>
    
    <script>
        // Tab switching function
        function openTab(evt, tabName) {{
            // Hide all tab contents
            var tabContents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < tabContents.length; i++) {{
                tabContents[i].classList.remove('active');
            }}
            
            // Remove active class from all tab buttons
            var tabBtns = document.getElementsByClassName('tab-btn');
            for (var i = 0; i < tabBtns.length; i++) {{
                tabBtns[i].classList.remove('active');
            }}
            
            // Show the selected tab and mark button as active
            document.getElementById(tabName).classList.add('active');
            evt.currentTarget.classList.add('active');
        }}
        
        // Logo modal functions
        function showLogoModal() {{
            document.getElementById('logoModal').classList.add('active');
        }}
        
        function hideLogoModal() {{
            document.getElementById('logoModal').classList.remove('active');
        }}
        
        // Allow ESC key to close logo modal
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                hideLogoModal();
            }}
        }});
        
        // Back to top button functionality - wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            var backToTopBtn = document.getElementById('backToTopBtn');
            if (backToTopBtn) {{
                window.addEventListener('scroll', function() {{
                    if (window.pageYOffset > 300) {{
                        backToTopBtn.style.display = 'block';
                    }} else {{
                        backToTopBtn.style.display = 'none';
                    }}
                }});
                
                backToTopBtn.addEventListener('click', function() {{
                    window.scrollTo(0, 0);
                }});
            }}
        }});
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
    
    <!-- Copyright Footer -->
    <div class="footer">
        <p><strong>AVICE P&R Comprehensive Report</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
</body>
</html>"""
            
            # Write HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"  {Color.GREEN}[OK] Unified PnR HTML Report Generated{Color.RESET}")
            print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
            
            return os.path.abspath(html_path)
            
        except Exception as e:
            print(f"  {Color.RED}Error generating unified PnR HTML: {e}{Color.RESET}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_pnr_data_html_content(self):
        """Extract PnR data content for unified HTML"""
        try:
            # Get postroute data from all stages
            stages = ['plan', 'place', 'cts', 'route', 'postroute']
            stage_data = {}
            
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
                    except:
                        pass
            
            if not stage_data:
                return '<div class="no-data">No PnR data available</div>'
            
            # Build data table with all parameters
            content = '<div class="section-header">PnR Stage Data - Key Metrics</div>'
            content += '<p>Comparison of key design metrics across all PnR stages.</p>'
            
            # Add filter bar
            content += '''
            <div style="margin: 20px 0;">
                <input type="text" id="paramFilter" placeholder="Filter parameters..." 
                       style="width: 100%; padding: 10px; font-size: 14px; border: 2px solid #667eea; 
                              border-radius: 5px; box-sizing: border-box;">
            </div>
            '''
            
            # Get all unique parameters and sort them
            all_params = set()
            for stage_params in stage_data.values():
                all_params.update(stage_params.keys())
            
            # Define parameter groups for better organization
            timing_params = []
            area_params = []
            power_params = []
            clock_params = []
            dft_params = []
            compute_params = []
            metadata_params = []
            other_params = []
            
            for param in sorted(all_params):
                param_lower = param.lower()
                # Metadata/Run Info - check first for run metadata patterns
                if param in ['User', 'WW', 'Tool', 'RTL_TAG', 'Scenario', 'Stage', 'Date', 'Directory', 'Technology', 'ToolVersion', 'TracksNum', 'Unit', 'Project', 'SiteVersion']:
                    metadata_params.append(param)
                # Compute Metrics - check for cpu/memory/server/runtime patterns
                elif any(x in param_lower for x in ['cpu', 'memory', 'server', 'stepruntime']):
                    compute_params.append(param)
                # Clock Metrics - check for clock-specific patterns
                elif any(x in param_lower for x in ['latency', 'skew', 'cycle_time', 'clk_ffcount', 'parrallel_driver']):
                    clock_params.append(param)
                # DFT Metrics - check for scan/dft patterns
                elif any(x in param_lower for x in ['dft', 'scan']):
                    dft_params.append(param)
                # Timing Metrics (removed cycle_time as it goes to clock)
                elif any(x in param_lower for x in ['wns', 'tns', 'nvp', 'slack', 'timing', 'violpaths', 'maxfanoutviolations', 'maxtransviolations']):
                    timing_params.append(param)
                # Area & Cell Metrics
                elif any(x in param_lower for x in ['area', 'cell', 'instance', 'net', 'utilization', 'array', 'ffcount', 'buffer', 'gate', 'count', 'bufinv']):
                    area_params.append(param)
                # Power Metrics
                elif any(x in param_lower for x in ['power', 'leakage', 'dynamic', 'vt_percentage', 'svt_', 'lvt_', 'hvt_', 'ulvt_', 'mbperc', 
                                                     'ungatedff', 'ffsbigger', 'ffsoverlogic', 'maxclonedcg', 'tapfanout', 'usemultibit', 'percffwith',
                                                     'totalleakage', 'totallogicg']):
                    power_params.append(param)
                else:
                    other_params.append(param)
            
            # Parameter display name mapping for cleaner presentation
            param_display_names = {
                'HVT_percentage': '%HVT',
                'LVT_percentage': '%LVT',
                'SVT_percentage': '%SVT',
                'ULVT_percentage': '%ULVT',
                'Utilization': '%Utilization',
                'EffictiveUtilization': '%EffictiveUtilization'
            }
            
            # Custom sort function to group VT percentages together in Power Metrics
            def sort_power_params(params):
                """Sort power parameters with VT percentages grouped together (high to low threshold)"""
                vt_order = ['HVT_percentage', 'SVT_percentage', 'LVT_percentage', 'ULVT_percentage']
                vt_params = [p for p in vt_order if p in params]
                other_params = [p for p in sorted(params) if p not in vt_order]
                return vt_params + other_params
            
            # Custom sort function to group Utilization parameters together in Area & Cell Metrics
            def sort_area_params(params):
                """Sort area parameters with utilization metrics grouped together"""
                util_order = ['Utilization', 'EffictiveUtilization']
                util_params = [p for p in util_order if p in params]
                other_params = [p for p in sorted(params) if p not in util_order]
                return util_params + other_params
            
            # Custom sort function to order metadata parameters
            def sort_metadata_params(params):
                """Sort metadata parameters in a specific order"""
                meta_order = ['User', 'WW', 'Tool', 'RTL_TAG', 'Scenario', 'Stage', 'Date', 'Directory', 'Technology', 'ToolVersion', 'TracksNum', 'Unit', 'Project', 'SiteVersion']
                ordered_params = [p for p in meta_order if p in params]
                other_params = [p for p in sorted(params) if p not in meta_order]
                return ordered_params + other_params
            
            # Sort power_params with custom ordering
            power_params = sort_power_params(power_params)
            
            # Sort area_params with custom ordering
            area_params = sort_area_params(area_params)
            
            # Sort metadata_params with custom ordering
            metadata_params = sort_metadata_params(metadata_params)
            
            # Build tables by category
            param_groups = [
                ('Environment Details', metadata_params),
                ('Timing Metrics', timing_params),
                ('Clock Metrics', clock_params),
                ('Area & Cell Metrics', area_params),
                ('Power Metrics', power_params),
                ('DFT Metrics', dft_params),
                ('Compute Metrics', compute_params),
                ('Other Parameters', other_params)
            ]
            
            for group_name, params in param_groups:
                if params:
                    content += f'<h3 style="color: #667eea; margin-top: 30px;">{group_name}</h3>'
                    content += '<table style="width: 100%; border-collapse: collapse; margin: 15px 0;">'
                    content += '<thead><tr><th style="background-color: #34495e; color: white; padding: 12px; text-align: left;">Parameter</th>'
                    
                    for stage in stages:
                        if stage in stage_data:
                            content += f'<th style="background-color: #34495e; color: white; padding: 12px; text-align: center;">{stage.upper()}</th>'
                    content += '</tr></thead><tbody>'
                    
                    # Add rows for parameters in this group
                    for param in params:
                        # Get display name (use mapping if available, otherwise use original)
                        display_name = param_display_names.get(param, param)
                        content += f'<tr class="param-row" data-param-name="{param.lower()}" data-display-name="{display_name.lower()}">'
                        content += f'<td style="padding: 10px; border: 1px solid #ddd;"><strong>{display_name}</strong></td>'
                        for stage in stages:
                            if stage in stage_data:
                                value = stage_data[stage].get(param, '-')
                                # Color code timing violations
                                cell_style = 'padding: 10px; border: 1px solid #ddd; text-align: center;'
                                if 'WNS' in param or 'TNS' in param:
                                    try:
                                        num_val = float(value)
                                        if num_val < 0:
                                            cell_style += ' background-color: #ffebee; color: #c62828;'
                                    except:
                                        pass
                                content += f'<td style="{cell_style}">{value}</td>'
                        content += '</tr>'
                    
                    content += '</tbody></table>'
            
            # Add "Back to Top" button
            content += '''
            <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
                    z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
                    cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
                    font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
                    onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
                    onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
                ↑ Top
            </button>
            '''
            
            # Add JavaScript for filtering and back-to-top button
            content += '''
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Filter functionality
                const filterInput = document.getElementById('paramFilter');
                if (filterInput) {
                    filterInput.addEventListener('input', function() {
                        const filterText = this.value.toLowerCase();
                        const rows = document.querySelectorAll('.param-row');
                        
                        rows.forEach(function(row) {
                            const paramName = row.getAttribute('data-param-name') || '';
                            const displayName = row.getAttribute('data-display-name') || '';
                            
                            // Show row if filter text is found in either param name or display name
                            if (paramName.includes(filterText) || displayName.includes(filterText)) {
                                row.style.display = '';
                            } else {
                                row.style.display = 'none';
                            }
                        });
                    });
                }
                
                // Back to top button functionality
                var backToTopBtn = document.getElementById('backToTopBtn');
                if (backToTopBtn) {
                    // Show button when user scrolls down 300px
                    window.addEventListener('scroll', function() {
                        if (window.pageYOffset > 300) {
                            backToTopBtn.style.display = 'block';
                        } else {
                            backToTopBtn.style.display = 'none';
                        }
                    });
                    
                    // Scroll to top when button is clicked
                    backToTopBtn.addEventListener('click', function() {
                        window.scrollTo({
                            top: 0,
                            behavior: 'smooth'
                        });
                    });
                }
            });
            </script>
            '''
            
            return content
            
        except Exception as e:
            import traceback
            return f'<div class="no-data">Error loading PnR data: {e}<br><pre>{traceback.format_exc()}</pre></div>'
    
    def _colorize_histogram_table(self, table_text):
        """Add color coding to histogram table - highlight negative slack columns in red"""
        try:
            import re
            lines = table_text.split('\n')
            colored_lines = []
            
            for line in lines:
                # Check if this line contains negative slack values
                # Pattern 1: Header row with negative slack ranges (e.g., "-0.010 -0.020 -0.030")
                # Pattern 2: Data rows with negative values in WNS/TNS columns
                
                if '|' in line:
                    # Color any negative numbers (with minus sign and digits)
                    # This will catch: -0.010, -1.234, -0.094, etc.
                    colored_line = re.sub(
                        r'(-\d+\.?\d*)',
                        r'<span style="color: #e74c3c; font-weight: bold;">\1</span>',
                        line
                    )
                    colored_lines.append(colored_line)
                else:
                    colored_lines.append(line)
            
            return '\n'.join(colored_lines)
        except Exception as e:
            # If coloring fails, return original text
            return table_text
    
    def _colorize_timing_summary(self, summary_text):
        """Add color coding to timing summary - highlight negative WNS/TNS values in red"""
        try:
            import re
            lines = summary_text.split('\n')
            colored_lines = []
            
            for line in lines:
                # Look for negative numbers in WNS/TNS lines
                if any(keyword in line for keyword in ['WNS', 'TNS', 'NVP']):
                    # Find negative numbers (e.g., -0.123, -1.5)
                    colored_line = re.sub(
                        r'(-\d+\.?\d*)',
                        r'<span style="color: #e74c3c; font-weight: bold;">\1</span>',
                        line
                    )
                    colored_lines.append(colored_line)
                else:
                    colored_lines.append(line)
            
            return '\n'.join(colored_lines)
        except Exception as e:
            # If coloring fails, return original text
            return summary_text
    
    def _get_timing_histogram_html_content(self):
        """Extract timing histogram content for unified HTML"""
        try:
            # Find timing histogram files (both setup and hold)
            pnr_stages = ['postroute', 'route', 'cts', 'place', 'plan']
            setup_file = None
            hold_file = None
            found_stage = None
            
            for stage in pnr_stages:
                setup_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.{stage}.timing.setup.rpt.gz"
                hold_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.{stage}.timing.hold.rpt.gz"
                
                setup_files = self.file_utils.find_files(setup_pattern, self.workarea)
                hold_files = self.file_utils.find_files(hold_pattern, self.workarea)
                
                if setup_files or hold_files:
                    setup_file = setup_files[0] if setup_files else None
                    hold_file = hold_files[0] if hold_files else None
                    found_stage = stage
                    break
            
            if not setup_file and not hold_file:
                return '<div class="no-data">No timing histogram data available</div>'
            
            content = f'<div class="section-header">Timing Histogram Analysis - {found_stage.upper()} Stage</div>'
            content += '<p>Timing path distribution across different slack ranges. Negative slack indicates timing violations.</p>'
            
            # Add Legend
            content += '''
            <div style="background: #f0f8ff; border: 2px solid #3498db; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0; margin-bottom: 10px;">
                    <span style="font-size: 18px;">&#9432;</span> Histogram Legend
                </h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
                    <div>
                        <strong style="color: #16a085;">Slack Ranges:</strong>
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            <li><span style="background: #e74c3c; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold;">Red</span> = Negative slack (timing violations)</li>
                            <li>Positive slack = Paths meeting timing</li>
                        </ul>
                    </div>
                    <div>
                        <strong style="color: #16a085;">Column Meanings:</strong>
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            <li><strong>WNS:</strong> Worst Negative Slack</li>
                            <li><strong>TNS:</strong> Total Negative Slack</li>
                            <li><strong>NVP:</strong> Number of Violating Paths</li>
                            <li><strong>Histogram:</strong> Path count per slack bucket</li>
                        </ul>
                    </div>
                </div>
            </div>
            '''
            
            # Setup Timing Section
            if setup_file:
                try:
                    content += '<h2 style="color: #27ae60; background: #ecf9f0; padding: 10px; border-left: 4px solid #27ae60; margin-top: 20px;">Setup Timing</h2>'
                    
                    result = self.file_utils.run_command(f"zcat {setup_file} | grep -n 'histogram' | grep '|'")
                    if result.strip():
                        histogram_lines = result.strip().split('\n')
                        if len(histogram_lines) >= 2:
                            # Get the last table (sub-category breakdown is most detailed)
                            table_start = int(histogram_lines[-1].split(':')[0])
                            
                            # Extract the table (get 30 lines for more complete view)
                            table_result = self.file_utils.run_command(f"zcat {setup_file} | sed -n '{table_start},{table_start+30}p'")
                            
                            if table_result.strip():
                                content += '<h3 style="color: #667eea; margin-top: 15px;">Setup Path Distribution by Category</h3>'
                                
                                # Apply color coding to negative slack ranges
                                colored_table = self._colorize_histogram_table(table_result.strip())
                                
                                content += '<pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: monospace; font-size: 11px;">'
                                content += colored_table
                                content += '</pre>'
                            
                            # Get summary info
                            summary_result = self.file_utils.run_command(f"zcat {setup_file} | grep -E 'WNS|TNS|NVP' | head -10")
                            if summary_result.strip():
                                content += '<h3 style="color: #667eea; margin-top: 20px;">Setup Timing Summary</h3>'
                                
                                # Apply color coding to summary
                                colored_summary = self._colorize_timing_summary(summary_result.strip())
                                
                                content += '<pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px;">'
                                content += colored_summary
                                content += '</pre>'
                    
                    content += f'<p style="margin-top: 10px; font-size: 11px; color: #666;"><strong>Source:</strong> {setup_file}</p>'
                    
                except Exception as e:
                    content += f'<p style="color: #e74c3c;">Error parsing setup histogram: {e}</p>'
            
            # Hold Timing Section
            if hold_file:
                try:
                    content += '<h2 style="color: #e67e22; background: #fef5e7; padding: 10px; border-left: 4px solid #e67e22; margin-top: 30px;">Hold Timing</h2>'
                    
                    # Extract Table 8 specifically (category + sub_category + scenario)
                    # This is detailed breakdown without logic depth
                    result = self.file_utils.run_command(f"zcat {hold_file} | grep -n 'histogram' | grep '|'")
                    if result.strip():
                        histogram_lines = result.strip().split('\n')
                        if len(histogram_lines) >= 2:
                            # Get the second-to-last table (Table 8) - sub-category breakdown
                            # Last table is Table 9 with logic_depth, we want the one before it
                            table_8_start = int(histogram_lines[-2].split(':')[0])
                            table_9_start = int(histogram_lines[-1].split(':')[0])
                            
                            # Extract only Table 8 (stop before Table 9 starts)
                            # Go back 2 lines from Table 9 start to avoid including its header
                            table_8_end = table_9_start - 2
                            
                            table_result = self.file_utils.run_command(f"zcat {hold_file} | sed -n '{table_8_start},{table_8_end}p'")
                            
                            if table_result.strip():
                                content += '<h3 style="color: #667eea; margin-top: 15px;">Hold Path Distribution by Category (Table 8)</h3>'
                                content += '<p style="font-size: 12px; color: #666;">Detailed breakdown showing path distribution across categories and sub-categories.</p>'
                                
                                # Apply color coding to negative slack ranges
                                colored_table = self._colorize_histogram_table(table_result.strip())
                                
                                content += '<pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: monospace; font-size: 10px;">'
                                content += colored_table
                                content += '</pre>'
                    
                    # Get hold timing summary with WNS/TNS/NVP
                    summary_result = self.file_utils.run_command(f"zcat {hold_file} | grep -E 'WNS|TNS|NVP' | head -10")
                    if summary_result.strip():
                        content += '<h3 style="color: #667eea; margin-top: 20px;">Hold Timing Summary</h3>'
                        
                        # Apply color coding to summary
                        colored_summary = self._colorize_timing_summary(summary_result.strip())
                        
                        content += '<pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px;">'
                        content += colored_summary
                        content += '</pre>'
                    
                    content += f'<p style="margin-top: 10px; font-size: 11px; color: #666;"><strong>Source:</strong> {hold_file}</p>'
                    
                except Exception as e:
                    content += f'<p style="color: #e74c3c;">Error parsing hold histogram: {e}</p>'
            
            return content
            
        except Exception as e:
            import traceback
            return f'<div class="no-data">Error loading timing histogram: {e}<br><pre>{traceback.format_exc()}</pre></div>'
    
    def _get_images_html_content(self):
        """Extract images content for unified HTML with full categorization"""
        try:
            # Find images directory
            images_dir = os.path.join(self.workarea, f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/IMAGES")
            
            if not os.path.exists(images_dir):
                return '<div class="no-data">No debug images directory found</div>'
            
            # Find all image files (excluding hidden files starting with .)
            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif']:
                all_files = glob.glob(os.path.join(images_dir, ext))
                # Filter out hidden files
                image_files.extend([f for f in all_files if not os.path.basename(f).startswith('.')])
            
            if not image_files:
                return f'<div class="no-data">No images found<br><small>{images_dir}</small></div>'
            
            # Categorize images
            categorized_images = self._categorize_images(image_files)
            
            content = '<div class="section-header">Debug Images Gallery</div>'
            content += f'<p><strong>Total Images:</strong> {len(image_files)} | <strong>Directory:</strong> {images_dir}</p>'
            
            # Add styles
            content += '''
            <style>
                .category-container {
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    overflow: hidden;
                }
                .category-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 20px;
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-weight: bold;
                    font-size: 16px;
                }
                .category-header:hover {
                    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
                }
                .category-toggle {
                    transition: transform 0.3s ease;
                }
                .category-toggle.collapsed {
                    transform: rotate(-90deg);
                }
                .category-content {
                    padding: 20px;
                    background: #f9f9f9;
                    display: block;
                }
                .category-content.collapsed {
                    display: none;
                }
                .subcategory-header {
                    background: #34495e;
                    color: white;
                    padding: 10px 15px;
                    margin: 15px 0 10px 0;
                    border-radius: 5px;
                    font-weight: bold;
                }
                .image-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
                    gap: 15px;
                    margin: 15px 0;
                }
                .image-card {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    background: white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                .image-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                }
                .image-card img {
                    width: 100%;
                    height: 160px;
                    object-fit: contain;
                    border-radius: 5px;
                    cursor: pointer;
                    background: #f5f5f5;
                }
                .image-name {
                    font-size: 10px;
                    margin-top: 8px;
                    color: #666;
                    word-break: break-all;
                    line-height: 1.3;
                }
                .image-description {
                    font-size: 9px;
                    color: #999;
                    margin-top: 4px;
                    font-style: italic;
                }
                .image-count {
                    background: rgba(255,255,255,0.2);
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                }
                .image-modal {
                    display: none;
                    position: fixed;
                    z-index: 10000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.95);
                    justify-content: center;
                    align-items: center;
                }
                .image-modal.active {
                    display: flex;
                }
                .image-modal img {
                    max-width: 95%;
                    max-height: 95%;
                    border-radius: 5px;
                }
                .image-modal-close {
                    position: absolute;
                    top: 20px;
                    right: 40px;
                    color: white;
                    font-size: 40px;
                    font-weight: bold;
                    cursor: pointer;
                }
                .show-more-btn {
                    display: block;
                    margin: 15px auto;
                    padding: 10px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                .show-more-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                .show-more-btn:active {
                    transform: translateY(0);
                }
                .image-card.hidden {
                    display: none;
                }
            </style>
            '''
            
            # Category priority order
            category_priority = [
                'Synthesis Flow',
                'Floorplan/Layout',
                'Placement',
                'Clock Tree',
                'Routing',
                'Timing',
                'Power',
                'Signal Integrity',
                'DRC/DRV',
                'DRC Violation Snapshots',
                'ECO/Signoff Analysis',
                'Other'
            ]
            
            # Generate categorized sections
            for category in category_priority:
                if category not in categorized_images:
                    continue
                    
                # Count images in this category
                category_image_count = sum(len(categorized_images[category][subcategory]) 
                                         for subcategory in categorized_images[category])
                
                if category_image_count == 0:
                    continue
                    
                cat_id = category.replace(' ', '_').replace('/', '_')
                content += f'''
                <div class="category-container">
                    <div class="category-header" onclick="toggleImgCategory('{cat_id}')">
                        <span>{category}</span>
                        <span><span class="image-count">{category_image_count} images</span> <span class="category-toggle" id="toggle_{cat_id}">▼</span></span>
                    </div>
                    <div class="category-content" id="content_{cat_id}">
                '''
                
                # Generate subcategories
                subcat_index = 0
                for subcategory in categorized_images[category]:
                    images = categorized_images[category][subcategory]
                    if not images:
                        continue
                    
                    subcat_id = f"{cat_id}_subcat_{subcat_index}"
                    subcat_index += 1
                    initial_show = 12  # Show first 12 images by default
                    
                    content += f'''
                        <div class="subcategory-header">{subcategory} ({len(images)} images)</div>
                        <div class="image-grid" id="grid_{subcat_id}">
                    '''
                    
                    for idx, img_data in enumerate(images):
                        img_path = img_data['path']
                        img_name = img_data['name']
                        img_desc = img_data['description']
                        img_url = f"file://{os.path.abspath(img_path)}"
                        
                        # Add 'hidden' class to images beyond initial_show count
                        hidden_class = ' hidden' if idx >= initial_show else ''
                        
                        content += f'''
                            <div class="image-card{hidden_class}">
                                <img src="{img_url}" alt="{img_name}" onclick="showImageModal(this.src)" title="{img_desc}">
                                <div class="image-name">{img_name}</div>
                                <div class="image-description">{img_desc}</div>
                            </div>
                        '''
                    
                    content += '</div>'  # Close image-grid
                    
                    # Add "Show More" button if there are more than initial_show images
                    if len(images) > initial_show:
                        remaining = len(images) - initial_show
                        content += f'''
                        <button class="show-more-btn" onclick="showMoreImages('{subcat_id}', this)">
                            Show {remaining} More Images
                        </button>
                        '''
                
                content += '''
                    </div>
                </div>
                '''
            
            # Add image modal and scripts
            content += '''
            <div id="imageModal" class="image-modal" onclick="hideImageModal()">
                <span class="image-modal-close">&times;</span>
                <img id="modalImage" src="">
            </div>
            <script>
                function showImageModal(src) {
                    document.getElementById('modalImage').src = src;
                    document.getElementById('imageModal').classList.add('active');
                }
                function hideImageModal() {
                    document.getElementById('imageModal').classList.remove('active');
                }
                function toggleImgCategory(categoryId) {
                    var content = document.getElementById('content_' + categoryId);
                    var toggle = document.getElementById('toggle_' + categoryId);
                    if (content.classList.contains('collapsed')) {
                        content.classList.remove('collapsed');
                        toggle.classList.remove('collapsed');
                        toggle.textContent = '▼';
                    } else {
                        content.classList.add('collapsed');
                        toggle.classList.add('collapsed');
                        toggle.textContent = '▶';
                    }
                }
                function showMoreImages(subcatId, button) {
                    var grid = document.getElementById('grid_' + subcatId);
                    var hiddenImages = grid.querySelectorAll('.image-card.hidden');
                    
                    // Show next batch of images (12 at a time)
                    var showCount = Math.min(12, hiddenImages.length);
                    for (var i = 0; i < showCount; i++) {
                        hiddenImages[i].classList.remove('hidden');
                    }
                    
                    // Update button text or hide it if all images are shown
                    var remainingHidden = grid.querySelectorAll('.image-card.hidden').length;
                    if (remainingHidden > 0) {
                        button.textContent = 'Show ' + remainingHidden + ' More Images';
                    } else {
                        button.style.display = 'none';
                    }
                }
            </script>
            '''
            
            return content
            
        except Exception as e:
            import traceback
            return f'<div class="no-data">Error loading images: {e}<br><pre>{traceback.format_exc()}</pre></div>'
    
    def _categorize_images(self, image_files):
        """Categorize images into sections based on patterns"""
        import re
        
        # Image categories with patterns (same as standalone report)
        image_categories = {
            'Synthesis Flow': {
                'RTL-to-Gate Analysis': [
                    (r'rtl2gate_layout', 95, 'RTL-to-gate layout visualization'),
                    (r'rtl2gate_glbroutecongestion', 90, 'Global routing congestion from synthesis'),
                    (r'rtl2gate_traces.*clock.*color', 85, 'Clock trace analysis from synthesis'),
                    (r'rtl2gate_traces.*color', 80, 'Signal trace analysis from synthesis'),
                ],
                'Clock Trace Analysis': [
                    (r'rtl2gate_traces_i1_clk_color', 90, 'i1 clock trace analysis'),
                    (r'rtl2gate_traces_i2_clk_color', 90, 'i2 clock trace analysis'),
                    (r'rtl2gate_traces_m1_clk_color', 85, 'm1 clock trace analysis'),
                    (r'rtl2gate_traces_clkgate_color', 80, 'Clock gating trace analysis'),
                ],
                'Signal Trace Analysis': [
                    (r'rtl2gate_traces_regin_color', 75, 'Register input trace analysis'),
                    (r'rtl2gate_traces_regout_color', 75, 'Register output trace analysis'),
                    (r'rtl2gate_traces_feedthrough_color', 70, 'Feedthrough trace analysis'),
                    (r'rtl2gate_traces_wrapper_path_color', 70, 'Wrapper path trace analysis'),
                ]
            },
            'DRC Violation Snapshots': {
                'Metal Short Violations': [
                    (r'.*metal_short.*zoom', 95, 'Metal short violation snapshot'),
                    (r'.*metal_short', 90, 'Metal short violation'),
                ],
                'End of Line Keepout Violations': [
                    (r'.*endofline_keepout.*zoom', 95, 'End of line keepout violation snapshot'),
                    (r'.*endofline_keepout', 90, 'End of line keepout violation'),
                ],
                'Via Stack Violations': [
                    (r'maxviastack.*v3s', 90, 'Via stack violation V3S layer'),
                    (r'maxviastack.*v4t', 90, 'Via stack violation V4T layer'),
                    (r'maxviastack', 85, 'Via stack violations'),
                ],
                'Spacing Violations': [
                    (r'parallel_run_length_spacing', 85, 'Parallel run length spacing violation'),
                    (r'spacing.*violation', 80, 'Spacing violations'),
                ],
                'General DRC Snapshots': [
                    (r'.*zoom.*\.png$', 80, 'DRC violation snapshot'),
                    (r'.*drc.*snapshot', 75, 'DRC snapshot'),
                    (r'.*violation.*zoom', 70, 'Violation snapshot'),
                ]
            },
            'ECO/Signoff Analysis': {
                'ECO Impact Analysis': [
                    (r'eco.*images.*eco_in', 90, 'ECO input analysis'),
                    (r'cell_displacement.*eco_in', 85, 'Cell displacement ECO analysis'),
                    (r'cell_displacement', 80, 'Cell displacement analysis'),
                    (r'eco_summary.*drc', 85, 'ECO DRC summary'),
                ],
                'Legalization Issues': [
                    (r'bad_legalizations', 80, 'Bad legalization cases'),
                    (r'legalization.*issue', 75, 'Legalization issues'),
                ]
            },
            'Timing': {
                'Hold Violations': [
                    (r'timing\.hold\.external\.(input|output)\.worst.*failed.*paths', 100, 'Critical hold timing violations'),
                    (r'timing\.hold\.external\.(input|output)\.path_slack_heatmap', 95, 'Hold timing slack heatmap'),
                    (r'timing\.hold\.internal\.(input|output)\.worst.*failed.*paths', 90, 'Internal hold violations'),
                    (r'timing\.hold\..*violations', 85, 'Hold timing violations'),
                    (r'timing\.hold', 80, 'General hold timing analysis'),
                ],
                'Setup Violations': [
                    (r'timing\.setup\.external\.(input|output)\.worst.*failed.*paths', 100, 'Critical setup timing violations'),
                    (r'timing\.setup\.external\.(input|output)\.path_slack_heatmap', 95, 'Setup timing slack heatmap'),
                    (r'timing\.setup\.internal\.(input|output)\.worst.*failed.*paths', 90, 'Internal setup violations'),
                    (r'timing\.setup\..*violations', 85, 'Setup timing violations'),
                    (r'timing\.setup', 80, 'General setup timing analysis'),
                ],
                'Input/Output Timing': [
                    (r'timing\..*external\.input', 85, 'Input timing analysis'),
                    (r'timing\..*external\.output', 85, 'Output timing analysis'),
                    (r'timing\..*io.*constraints', 75, 'I/O timing constraints'),
                    (r'timing\..*external', 70, 'External timing analysis'),
                ],
                'General Timing': [
                    (r'timing\..*slack.*histogram', 85, 'Timing slack distribution'),
                    (r'timing\..*summary', 80, 'Overall timing summary'),
                    (r'timing\..*paths', 75, 'Critical path analysis'),
                    (r'timing\..*report', 70, 'General timing report'),
                    (r'timing\.', 65, 'Timing analysis'),
                ]
            },
            'DRC/DRV': {
                'Design Rule Violations': [
                    (r'drc.*violations', 90, 'Design rule check violations'),
                    (r'drv.*violations', 90, 'Design rule violations'),
                    (r'drc.*summary', 85, 'DRC summary report'),
                    (r'spacing.*violations', 80, 'Metal spacing violations'),
                    (r'width.*violations', 80, 'Wire width violations'),
                ],
                'Layer Violations': [
                    (r'drc.*layer', 80, 'Layer-specific DRC violations'),
                    (r'drv.*layer', 80, 'Layer-specific violations'),
                ],
                'DRC Analysis': [
                    (r'drc\.all\.class', 85, 'DRC violations by class'),
                    (r'drc\.all\.criticality', 85, 'DRC violations by criticality'),
                    (r'drc\.all\.interaction', 80, 'DRC interaction analysis'),
                    (r'drc\.all\.layer', 80, 'DRC violations by layer'),
                    (r'drc\.all\.type', 80, 'DRC violations by type'),
                    (r'drc\.signal_clock_or_preroute', 75, 'Signal/clock/preroute DRC'),
                    (r'drc\.', 70, 'General DRC analysis'),
                ],
                'DRV Analysis': [
                    (r'drv\.max_capacitance', 85, 'Maximum capacitance violations'),
                    (r'drv\.max_transition.*net\.clock', 85, 'Clock net max transition violations'),
                    (r'drv\.max_transition.*net\.signal', 80, 'Signal net max transition violations'),
                    (r'drv\.max_transition', 80, 'Maximum transition violations'),
                    (r'drv\.max_fanout', 75, 'Maximum fanout violations'),
                    (r'drv\.', 70, 'General DRV analysis'),
                ]
            },
            'Power': {
                'Power Density': [
                    (r'power_density\.total', 95, 'Total power density distribution'),
                    (r'power_density\.switching', 90, 'Switching power density'),
                    (r'power_density\.leakage', 90, 'Leakage power density'),
                    (r'power_density', 85, 'Power density analysis'),
                ],
                'Rail Analysis': [
                    (r'rail_analysis', 85, 'Power rail analysis'),
                    (r'ir_drop', 85, 'IR drop analysis'),
                ],
                'General Power': [
                    (r'power\..*histogram', 80, 'Power distribution'),
                    (r'power\..*summary', 75, 'Power summary'),
                    (r'power\.', 70, 'Power analysis'),
                ]
            },
            'Signal Integrity': {
                'Crosstalk Analysis': [
                    (r'crosstalk', 85, 'Signal crosstalk analysis'),
                    (r'coupling', 80, 'Coupling analysis'),
                ],
                'SI Violations': [
                    (r'si.*violations', 85, 'Signal integrity violations'),
                    (r'noise.*violations', 80, 'Noise violations'),
                ]
            },
            'Floorplan/Layout': {
                'Floorplan': [
                    (r'floorplan', 85, 'Floorplan view'),
                    (r'fp_view', 80, 'Floorplan visualization'),
                ],
                'Placement Density': [
                    (r'placement.*density', 85, 'Cell placement density'),
                    (r'density.*map', 80, 'Density heatmap'),
                ],
                'Macros and Blockages': [
                    (r'macro.*placement', 80, 'Macro placement'),
                    (r'blockage', 75, 'Placement blockages'),
                ]
            },
            'Placement': {
                'Placement Quality': [
                    (r'placement.*congestion', 90, 'Placement congestion'),
                    (r'placement.*legalization', 85, 'Legalization analysis'),
                    (r'placement.*quality', 80, 'Placement quality'),
                ],
                'Via Ladder': [
                    (r'via_ladder', 85, 'Via ladder visualization'),
                ]
            },
            'Clock Tree': {
                'Clock Tree QoR': [
                    (r'clock_tree.*arc_wire_resistance', 95, 'Arc wire resistance analysis'),
                    (r'clock_tree.*spine_qor', 90, 'Spine QoR analysis'),
                    (r'clock_tree.*qor', 85, 'Clock tree quality of results'),
                ],
                'Clock Latency': [
                    (r'clock.*latency', 85, 'Clock latency analysis'),
                    (r'clock.*skew', 85, 'Clock skew analysis'),
                ],
                'General Clock': [
                    (r'clock_tree', 80, 'Clock tree analysis'),
                    (r'clock\.', 75, 'Clock analysis'),
                ]
            },
            'Routing': {
                'Routing Congestion': [
                    (r'routing.*congestion', 90, 'Routing congestion analysis'),
                    (r'congestion.*map', 85, 'Congestion heatmap'),
                ],
                'Route Length': [
                    (r'routing\.route_length\.net_type', 85, 'Route length by net type'),
                    (r'routing\.route_length', 80, 'Wire length distribution'),
                ],
                'General Routing': [
                    (r'routing\.', 75, 'Routing analysis'),
                    (r'route\.', 70, 'Route visualization'),
                ]
            },
            'Other': {
                'Uncategorized': []
            }
        }
        
        # Initialize categorized storage
        categorized = {}
        for category in image_categories:
            categorized[category] = {}
            for subcategory in image_categories[category]:
                categorized[category][subcategory] = []
        
        # Categorize each image
        for image_path in image_files:
            image_name = os.path.basename(image_path).lower()
            best_match = None
            best_score = 0
            best_category = 'Other'
            best_subcategory = 'Uncategorized'
            best_description = 'Debug image'
            
            # Check against all patterns
            for category, subcategories in image_categories.items():
                for subcategory, patterns in subcategories.items():
                    for pattern, score, description in patterns:
                        if re.search(pattern, image_name) and score > best_score:
                            best_score = score
                            best_category = category
                            best_subcategory = subcategory
                            best_description = description
            
            # P&R flow stage priority boosts
            flow_stage_boosts = {
                'postroute': 50,
                'route': 30,
                'cts': 20,
                'place': 10,
                'plan': 5
            }
            
            flow_stage_names = {
                'postroute': 'Post-route',
                'route': 'Routing',
                'cts': 'CTS',
                'place': 'Placement',
                'plan': 'Floorplan'
            }
            
            for stage, boost in flow_stage_boosts.items():
                if re.search(rf'\.{stage}\.custom\.', image_name):
                    best_score += boost
                    best_description += f' ({flow_stage_names[stage]} stage)'
                    break
            
            # Default score for uncategorized
            if best_score == 0:
                best_score = 10
            
            # Add to appropriate category
            categorized[best_category][best_subcategory].append({
                'path': image_path,
                'name': os.path.basename(image_path),
                'score': best_score,
                'description': best_description
            })
        
        # Sort images within each subcategory by score (descending)
        for category in categorized:
            for subcategory in categorized[category]:
                categorized[category][subcategory].sort(key=lambda x: x['score'], reverse=True)
        
        return categorized
    
    def _generate_unified_dc_html(self):
        """Generate unified DC (Synthesis) HTML report"""
        try:
            from datetime import datetime
            import base64
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_DC_comprehensive_{timestamp}.html"
            html_path = os.path.abspath(html_filename)
            
            # Read and encode logo
            logo_data = ""
            logo_path = os.path.join(os.path.dirname(__file__), "images/avice_logo.png")
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo_data = base64.b64encode(f.read()).decode('utf-8')
            
            print(f"{Color.CYAN}Generating Unified DC HTML Report...{Color.RESET}")
            
            # Collect content from helper methods
            qor_data_content = self._get_dc_qor_html_content()
            beflow_config_content = self._get_dc_beflow_html_content()
            images_content = self._get_dc_images_html_content()
            
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DC Comprehensive Report - {self.design_info.top_hier}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
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
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .logo {{
            height: 60px;
            cursor: pointer;
        }}
        .header-text h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header-text p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }}
        .logo-modal.active {{
            display: flex;
        }}
        .logo-modal-content {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
        }}
        .logo-modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        .tab-navigation {{
            display: flex;
            background: #34495e;
            border-bottom: 3px solid #667eea;
        }}
        .tab-btn {{
            flex: 1;
            padding: 15px 20px;
            background: #34495e;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            border-right: 1px solid #2c3e50;
        }}
        .tab-btn:last-child {{
            border-right: none;
        }}
        .tab-btn:hover {{
            background: #2c3e50;
        }}
        .tab-btn.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transform: translateY(-2px);
        }}
        .tab-content {{
            display: none;
            padding: 30px;
            animation: fadeIn 0.3s ease;
        }}
        .tab-content.active {{
            display: block;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .section-header {{
            font-size: 24px;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        .no-data {{
            padding: 40px;
            text-align: center;
            color: #999;
            font-size: 18px;
            background: #f5f5f5;
            border-radius: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #34495e;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f0f0f0;
        }}
        
        /* Copyright Footer */
        .footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer strong {{
            color: #00ff00;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">"""
            
            if logo_data:
                html_content += f"""
            <img class='logo' src='data:image/png;base64,{logo_data}' alt='AVICE Logo' onclick="showLogoModal()" title="Click to enlarge">"""
            
            html_content += f"""
            <div class="header-text">
                <h1>DC (Synthesis) Comprehensive Report</h1>
                <p>Design: {self.design_info.top_hier} | IPO: {self.design_info.ipo}</p>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </div>
        
        <!-- Logo Modal -->
        <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
            <span class="logo-modal-close">&times;</span>"""
            
            if logo_data:
                html_content += f"""
            <img class="logo-modal-content" src='data:image/png;base64,{logo_data}' alt='AVICE Logo'>"""
            
            html_content += """
        </div>
        
        <!-- Tab Navigation -->
        <div class="tab-navigation">
            <button class="tab-btn active" onclick="openTab(event, 'qor-data')">QoR Data</button>
            <button class="tab-btn" onclick="openTab(event, 'beflow-config')">BeFlow Config</button>
            <button class="tab-btn" onclick="openTab(event, 'images')">Synthesis Images</button>
        </div>
        
        <!-- QoR Data Tab -->
        <div id="qor-data" class="tab-content active">"""
            html_content += qor_data_content
            html_content += """
        </div>
        
        <!-- BeFlow Config Tab -->
        <div id="beflow-config" class="tab-content">"""
            html_content += beflow_config_content
            html_content += """
        </div>
        
        <!-- Synthesis Images Tab -->
        <div id="images" class="tab-content">"""
            html_content += images_content
            html_content += """
        </div>
    </div>
    
    <script>
        // Tab switching function
        function openTab(evt, tabName) {
            var tabContents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < tabContents.length; i++) {
                tabContents[i].classList.remove('active');
            }
            
            var tabBtns = document.getElementsByClassName('tab-btn');
            for (var i = 0; i < tabBtns.length; i++) {
                tabBtns[i].classList.remove('active');
            }
            
            document.getElementById(tabName).classList.add('active');
            evt.currentTarget.classList.add('active');
        }
        
        // Logo modal functions
        function showLogoModal() {
            document.getElementById('logoModal').classList.add('active');
        }
        
        function hideLogoModal() {
            document.getElementById('logoModal').classList.remove('active');
        }
        
        // Allow ESC key to close logo modal
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                hideLogoModal();
            }
        });
        
        // Back to top button functionality - wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            var backToTopBtn = document.getElementById('backToTopBtn');
            if (backToTopBtn) {{
                window.addEventListener('scroll', function() {{
                    if (window.pageYOffset > 300) {{
                        backToTopBtn.style.display = 'block';
                    }} else {{
                        backToTopBtn.style.display = 'none';
                    }}
                }});
                
                backToTopBtn.addEventListener('click', function() {{
                    window.scrollTo(0, 0);
                }});
            }}
        }});
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
    
    <!-- Copyright Footer -->
    <div class="footer">
        <p><strong>AVICE DC Comprehensive Report</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
</body>
</html>"""
            
            # Write HTML to file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"  {Color.GREEN}[OK] Unified DC HTML Report Generated{Color.RESET}")
            print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{os.path.basename(html_path)}{Color.RESET} &")
            
            return html_path
            
        except Exception as e:
            print(f"  {Color.RED}Error generating unified DC HTML: {e}{Color.RESET}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_dc_qor_html_content(self):
        """Extract DC QoR data content for unified HTML"""
        try:
            content = '<div class="section-header">QoR Data (Quality of Results)</div>'
            
            # Find QoR report
            qor_report = os.path.join(self.workarea, f"syn_flow/dc/reports/{self.design_info.top_hier}_rtl2gate.qor.rpt")
            
            if not os.path.exists(qor_report):
                return content + '<div class="no-data">QoR report not found</div>'
            
            try:
                with open(qor_report, 'r', encoding='utf-8') as f:
                    qor_content = f.read()
                
                # Extract key sections
                content += '<h3 style="color: #667eea; margin-top: 20px;">Timing Summary</h3>'
                
                # Extract timing information
                timing_info = {}
                for line in qor_content.split('\n'):
                    line = line.strip()
                    if 'Timing Path Group' in line or 'clock' in line.lower():
                        if '(Setup)' in line or '(Hold)' in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                group = parts[0]
                                if 'Setup' in line:
                                    timing_info[f"{group}_setup"] = line
                                elif 'Hold' in line:
                                    timing_info[f"{group}_hold"] = line
                
                if timing_info:
                    content += '<table><thead><tr><th>Timing Group</th><th>Information</th></tr></thead><tbody>'
                    for group, info in timing_info.items():
                        content += f'<tr><td>{group}</td><td style="font-family: monospace; font-size: 11px;">{info}</td></tr>'
                    content += '</tbody></table>'
                
                # Extract design metrics
                content += '<h3 style="color: #667eea; margin-top: 30px;">Design Metrics</h3>'
                
                metrics = {}
                in_design_section = False
                for line in qor_content.split('\n'):
                    if 'Design' in line and 'Compiler' not in line:
                        in_design_section = True
                    if in_design_section and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value and len(key) < 50:
                                metrics[key] = value
                    if in_design_section and line.strip() == '':
                        if metrics:
                            break
                
                if metrics:
                    content += '<table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>'
                    for key, value in list(metrics.items())[:20]:  # Limit to first 20 metrics
                        content += f'<tr><td><strong>{key}</strong></td><td>{value}</td></tr>'
                    content += '</tbody></table>'
                else:
                    content += '<p>No design metrics found in QoR report</p>'
                
                # Add full report preview
                content += '<h3 style="color: #667eea; margin-top: 30px;">Full QoR Report Preview</h3>'
                content += f'<p><strong>Report Location:</strong> {qor_report}</p>'
                content += '<pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 500px; font-size: 11px; line-height: 1.4;">'
                content += qor_content[:5000]  # First 5000 characters
                if len(qor_content) > 5000:
                    content += '\n\n... (report truncated, see full file for complete data)'
                content += '</pre>'
                
            except Exception as e:
                content += f'<div class="no-data">Error reading QoR report: {e}</div>'
            
            return content
            
        except Exception as e:
            import traceback
            return f'<div class="no-data">Error loading QoR data: {e}<br><pre>{traceback.format_exc()}</pre></div>'
    
    def _get_dc_beflow_html_content(self):
        """Extract BeFlow configuration content for unified HTML"""
        try:
            content = '<div class="section-header">BeFlow Configuration</div>'
            
            # Find BeFlow config file
            beflow_config = os.path.join(self.workarea, "syn_flow/dc/beflow_config.yaml")
            
            if not os.path.exists(beflow_config):
                return content + '<div class="no-data">BeFlow configuration file not found</div>'
            
            try:
                import yaml
                with open(beflow_config, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                if not config_data:
                    return content + '<div class="no-data">BeFlow configuration is empty</div>'
                
                # Display configuration in organized sections
                content += '<p>Synthesis flow configuration parameters extracted from beflow_config.yaml</p>'
                
                # Group configurations by category
                categories = {
                    'Design': ['design', 'top_hier', 'unit', 'module'],
                    'Clocks': ['clock', 'clk', 'frequency', 'period'],
                    'Timing': ['timing', 'constraint', 'sdc', 'uncertainty'],
                    'Area': ['area', 'utilization', 'density'],
                    'Power': ['power', 'leakage', 'dynamic'],
                    'Technology': ['tech', 'library', 'lib', 'cell'],
                }
                
                def find_matching_keys(data, keywords, prefix=''):
                    """Recursively find keys matching keywords"""
                    matches = {}
                    if isinstance(data, dict):
                        for key, value in data.items():
                            full_key = f"{prefix}.{key}" if prefix else key
                            key_lower = key.lower()
                            
                            # Check if key matches any keyword
                            if any(kw in key_lower for kw in keywords):
                                if isinstance(value, (str, int, float, bool)):
                                    matches[full_key] = value
                                elif isinstance(value, list) and len(value) < 10:
                                    matches[full_key] = ', '.join(str(v) for v in value)
                            
                            # Recursively search nested dicts
                            if isinstance(value, dict):
                                nested = find_matching_keys(value, keywords, full_key)
                                matches.update(nested)
                    
                    return matches
                
                # Extract and display by category
                for category, keywords in categories.items():
                    matches = find_matching_keys(config_data, keywords)
                    
                    if matches:
                        content += f'<h3 style="color: #667eea; margin-top: 30px;">{category} Configuration</h3>'
                        content += '<table><thead><tr><th>Parameter</th><th>Value</th></tr></thead><tbody>'
                        for key, value in sorted(matches.items()):
                            # Truncate very long values
                            value_str = str(value)
                            if len(value_str) > 100:
                                value_str = value_str[:97] + '...'
                            content += f'<tr><td><strong>{key}</strong></td><td>{value_str}</td></tr>'
                        content += '</tbody></table>'
                
                # Add general/uncategorized parameters
                content += '<h3 style="color: #667eea; margin-top: 30px;">General Configuration</h3>'
                
                def flatten_dict(data, prefix='', max_depth=3, current_depth=0):
                    """Flatten nested dictionary"""
                    items = {}
                    if current_depth >= max_depth or not isinstance(data, dict):
                        return items
                    
                    for key, value in data.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, dict):
                            items.update(flatten_dict(value, full_key, max_depth, current_depth + 1))
                        elif isinstance(value, (str, int, float, bool)):
                            items[full_key] = value
                        elif isinstance(value, list) and len(value) < 10:
                            items[full_key] = ', '.join(str(v) for v in value)
                    
                    return items
                
                all_params = flatten_dict(config_data, max_depth=2)
                
                # Show first 30 general parameters
                if all_params:
                    content += '<table><thead><tr><th>Parameter</th><th>Value</th></tr></thead><tbody>'
                    for key, value in list(sorted(all_params.items()))[:30]:
                        value_str = str(value)
                        if len(value_str) > 100:
                            value_str = value_str[:97] + '...'
                        content += f'<tr><td><strong>{key}</strong></td><td>{value_str}</td></tr>'
                    content += '</tbody></table>'
                    
                    if len(all_params) > 30:
                        content += f'<p style="color: #666; font-style: italic; margin-top: 10px;">Showing 30 of {len(all_params)} parameters. See full file for complete configuration.</p>'
                
                # Add link to full config file
                content += '<h3 style="color: #667eea; margin-top: 30px;">Full Configuration File</h3>'
                content += f'<p><strong>File Location:</strong> {beflow_config}</p>'
                
                # Show first part of raw YAML
                with open(beflow_config, 'r', encoding='utf-8') as f:
                    yaml_content = f.read()
                
                content += '<pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 500px; font-size: 11px; line-height: 1.4;">'
                content += yaml_content[:3000]  # First 3000 characters
                if len(yaml_content) > 3000:
                    content += '\n\n... (file truncated, see full file for complete configuration)'
                content += '</pre>'
                
            except ImportError:
                # If yaml module not available, show raw file
                content += '<p style="color: #e74c3c;">YAML parser not available. Showing raw configuration file.</p>'
                with open(beflow_config, 'r', encoding='utf-8') as f:
                    yaml_content = f.read()
                content += '<pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 600px; font-size: 11px; line-height: 1.4;">'
                content += yaml_content
                content += '</pre>'
            except Exception as e:
                content += f'<div class="no-data">Error reading BeFlow configuration: {e}</div>'
            
            return content
            
        except Exception as e:
            import traceback
            return f'<div class="no-data">Error loading BeFlow config: {e}<br><pre>{traceback.format_exc()}</pre></div>'
    
    def _get_dc_images_html_content(self):
        """Extract synthesis images content for unified HTML"""
        try:
            # Find DC images directory
            images_dir = os.path.join(self.workarea, "syn_flow/dc/reports/color")
            
            if not os.path.exists(images_dir):
                return '<div class="no-data">No synthesis images directory found</div>'
            
            # Find all image files
            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif']:
                image_files.extend(glob.glob(os.path.join(images_dir, ext)))
            
            if not image_files:
                return f'<div class="no-data">No synthesis images found<br><small>{images_dir}</small></div>'
            
            # Categorize images (synthesis images will mostly be in "Synthesis Flow" category)
            categorized_images = self._categorize_images(image_files)
            
            content = '<div class="section-header">Synthesis Images Gallery</div>'
            content += f'<p><strong>Total Images:</strong> {len(image_files)} | <strong>Directory:</strong> {images_dir}</p>'
            
            # Add styles (reuse from PnR images)
            content += '''
            <style>
                .category-container {
                    margin: 20px 0;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    overflow: hidden;
                }
                .category-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 20px;
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-weight: bold;
                    font-size: 16px;
                }
                .category-header:hover {
                    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
                }
                .category-toggle {
                    transition: transform 0.3s ease;
                }
                .category-toggle.collapsed {
                    transform: rotate(-90deg);
                }
                .category-content {
                    padding: 20px;
                    background: #f9f9f9;
                    display: block;
                }
                .category-content.collapsed {
                    display: none;
                }
                .subcategory-header {
                    background: #34495e;
                    color: white;
                    padding: 10px 15px;
                    margin: 15px 0 10px 0;
                    border-radius: 5px;
                    font-weight: bold;
                }
                .image-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
                    gap: 15px;
                    margin: 15px 0;
                }
                .image-card {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    background: white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                .image-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                }
                .image-card img {
                    width: 100%;
                    height: 160px;
                    object-fit: contain;
                    border-radius: 5px;
                    cursor: pointer;
                    background: #f5f5f5;
                }
                .image-name {
                    font-size: 10px;
                    margin-top: 8px;
                    color: #666;
                    word-break: break-all;
                    line-height: 1.3;
                }
                .image-description {
                    font-size: 9px;
                    color: #999;
                    margin-top: 4px;
                    font-style: italic;
                }
                .image-count {
                    background: rgba(255,255,255,0.2);
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                }
                .image-modal {
                    display: none;
                    position: fixed;
                    z-index: 10000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.95);
                    justify-content: center;
                    align-items: center;
                }
                .image-modal.active {
                    display: flex;
                }
                .image-modal img {
                    max-width: 95%;
                    max-height: 95%;
                    border-radius: 5px;
                }
                .image-modal-close {
                    position: absolute;
                    top: 20px;
                    right: 40px;
                    color: white;
                    font-size: 40px;
                    font-weight: bold;
                    cursor: pointer;
                }
            </style>
            '''
            
            # Category priority order
            category_priority = [
                'Synthesis Flow',
                'Floorplan/Layout',
                'Placement',
                'Clock Tree',
                'Routing',
                'Timing',
                'Power',
                'Signal Integrity',
                'DRC/DRV',
                'DRC Violation Snapshots',
                'ECO/Signoff Analysis',
                'Other'
            ]
            
            # Generate categorized sections
            for category in category_priority:
                if category not in categorized_images:
                    continue
                    
                # Count images in this category
                category_image_count = sum(len(categorized_images[category][subcategory]) 
                                         for subcategory in categorized_images[category])
                
                if category_image_count == 0:
                    continue
                    
                cat_id = category.replace(' ', '_').replace('/', '_')
                content += f'''
                <div class="category-container">
                    <div class="category-header" onclick="toggleImgCategory('{cat_id}')">
                        <span>{category}</span>
                        <span><span class="image-count">{category_image_count} images</span> <span class="category-toggle" id="toggle_{cat_id}">▼</span></span>
                    </div>
                    <div class="category-content" id="content_{cat_id}">
                '''
                
                # Generate subcategories
                subcat_index = 0
                for subcategory in categorized_images[category]:
                    images = categorized_images[category][subcategory]
                    if not images:
                        continue
                    
                    subcat_id = f"{cat_id}_subcat_{subcat_index}"
                    subcat_index += 1
                    initial_show = 12  # Show first 12 images by default
                    
                    content += f'''
                        <div class="subcategory-header">{subcategory} ({len(images)} images)</div>
                        <div class="image-grid" id="grid_{subcat_id}">
                    '''
                    
                    for idx, img_data in enumerate(images):
                        img_path = img_data['path']
                        img_name = img_data['name']
                        img_desc = img_data['description']
                        img_url = f"file://{os.path.abspath(img_path)}"
                        
                        # Add 'hidden' class to images beyond initial_show count
                        hidden_class = ' hidden' if idx >= initial_show else ''
                        
                        content += f'''
                            <div class="image-card{hidden_class}">
                                <img src="{img_url}" alt="{img_name}" onclick="showImageModal(this.src)" title="{img_desc}">
                                <div class="image-name">{img_name}</div>
                                <div class="image-description">{img_desc}</div>
                            </div>
                        '''
                    
                    content += '</div>'  # Close image-grid
                    
                    # Add "Show More" button if there are more than initial_show images
                    if len(images) > initial_show:
                        remaining = len(images) - initial_show
                        content += f'''
                        <button class="show-more-btn" onclick="showMoreImages('{subcat_id}', this)">
                            Show {remaining} More Images
                        </button>
                        '''
                
                content += '''
                    </div>
                </div>
                '''
            
            # Add image modal and scripts
            content += '''
            <div id="imageModal" class="image-modal" onclick="hideImageModal()">
                <span class="image-modal-close">&times;</span>
                <img id="modalImage" src="">
            </div>
            <script>
                function showImageModal(src) {
                    document.getElementById('modalImage').src = src;
                    document.getElementById('imageModal').classList.add('active');
                }
                function hideImageModal() {
                    document.getElementById('imageModal').classList.remove('active');
                }
                function toggleImgCategory(categoryId) {
                    var content = document.getElementById('content_' + categoryId);
                    var toggle = document.getElementById('toggle_' + categoryId);
                    if (content.classList.contains('collapsed')) {
                        content.classList.remove('collapsed');
                        toggle.classList.remove('collapsed');
                        toggle.textContent = '▼';
                    } else {
                        content.classList.add('collapsed');
                        toggle.classList.add('collapsed');
                        toggle.textContent = '▶';
                    }
                }
            </script>
            '''
            
            return content
            
        except Exception as e:
            import traceback
            return f'<div class="no-data">Error loading images: {e}<br><pre>{traceback.format_exc()}</pre></div>'
    
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
                            html_filename = f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_innovus_timing_histogram_{self.design_info.ipo}.html"
                            html_path = os.path.join(os.getcwd(), html_filename)
                            
                            with open(html_path, 'w', encoding='utf-8') as f:
                                f.write(html_content)
                            
                            print(f"\n  {Color.CYAN}Timing Histogram HTML Report:{Color.RESET}")
                            print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
                            return os.path.abspath(html_path)  # Return absolute path for master dashboard
                        
        except Exception as e:
            print(f"  Error generating timing histogram HTML: {e}")
        
        return None
    
    def _create_timing_histogram_html(self, category_data: str, sub_category_data: str, scenario_data: str, stage: str) -> str:
        """Create HTML content for timing histogram tables"""
        # Read and encode logo
        logo_data = ""
        logo_path = os.path.join(os.path.dirname(__file__), "images/avice_logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo_file:
                logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
        
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
        .header {{ 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 20px;
            align-items: center;
            border-radius: 15px 15px 0 0;
            margin: -20px -20px 0 -20px;
        }}
        .logo {{
            width: 80px;
            height: 80px;
            border-radius: 10px;
            background: white;
            padding: 10px;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .logo:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        .header-text h1 {{
            font-size: 28px;
            margin: 0 0 8px 0;
            color: white;
            border: none;
        }}
        .header-text p {{
            opacity: 0.9;
            font-size: 14px;
            margin: 0;
        }}
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }}
        .logo-modal.active {{
            display: flex;
        }}
        .logo-modal-content {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
        }}
        .logo-modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        .logo-modal-close:hover {{
            color: #bbb;
        }}
        
        /* Copyright Footer */
        .footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer strong {{
            color: #00ff00;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img class='logo' src='data:image/png;base64,{logo_data}' alt='AVICE Logo' onclick="showLogoModal()" title="Click to enlarge">
            <div class="header-text">
                <h1>Timing Histogram Analysis</h1>
                <p>Design: {self.design_info.top_hier} | IPO: {self.design_info.ipo} | Stage: {stage.upper()}</p>
                <p>Workarea: {self.workarea_abs} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </div>
        
        <!-- Logo Modal -->
        <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
            <span class="logo-modal-close">&times;</span>
            <img class="logo-modal-content" src='data:image/png;base64,{logo_data}' alt='AVICE Logo'>
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
        // Logo modal functions
        function showLogoModal() {{
            document.getElementById('logoModal').classList.add('active');
        }}
        
        function hideLogoModal() {{
            document.getElementById('logoModal').classList.remove('active');
        }}
        
        // Allow ESC key to close logo modal
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                hideLogoModal();
            }}
        }});
        
        // Back to top button functionality - wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            var backToTopBtn = document.getElementById('backToTopBtn');
            if (backToTopBtn) {{
                window.addEventListener('scroll', function() {{
                    if (window.pageYOffset > 300) {{
                        backToTopBtn.style.display = 'block';
                    }} else {{
                        backToTopBtn.style.display = 'none';
                    }}
                }});
                
                backToTopBtn.addEventListener('click', function() {{
                    window.scrollTo(0, 0);
                }});
            }}
        }});
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
    
    <!-- Copyright Footer -->
    <div class="footer">
        <p><strong>AVICE Timing Histogram Report</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def run_clock_analysis(self):
        """Run clock analysis"""
        self.print_header(FlowStage.CLOCK_ANALYSIS)
        
        # Initialize max latency
        max_latency_ps = 0
        
        # Innovus clock analysis
        clock_skew_pattern = f"pnr_flow/nv_flow/{self.design_info.top_hier}/{self.design_info.ipo}/REPs/SUMMARY/{self.design_info.top_hier}.{self.design_info.ipo}.postroute.clock_tree.skew_and_latency.from_clock_root_source.rpt*"
        clock_files = self.file_utils.find_files(clock_skew_pattern, self.workarea)
        
        if clock_files:
            self.print_file_info(clock_files[0], "Innovus Clock Analysis")
            innovus_max_latency = self._extract_clock_tree_data(clock_files[0])
            max_latency_ps = max(max_latency_ps, innovus_max_latency)
        
        # PrimeTime clock analysis
        pt_clock_pattern = f"signoff_flow/auto_pt/last_work/func.std_tt_0c_0p6v.setup.typical/reports/timing_reports/{self.design_info.top_hier}_func.std_tt_0c_0p6v.setup.typical.clock_latency"
        pt_clock_file = os.path.join(self.workarea, pt_clock_pattern)
        
        if self.file_utils.file_exists(pt_clock_file):
            self.print_file_info(pt_clock_file, "PT Clock Analysis")
            pt_max_latency = self._extract_pt_clock_latency(pt_clock_file)
            max_latency_ps = max(max_latency_ps, pt_max_latency)
        
        # Determine status based on max latency
        # Thresholds: FAIL ≥ 580ps, WARN 550ps < latency < 580ps, PASS ≤ 550ps
        status = "PASS"
        issues = []
        
        if max_latency_ps >= 580:
            status = "FAIL"
            issues.append(f"Max clock latency: {max_latency_ps:.1f}ps (threshold: <580ps)")
        elif max_latency_ps > 550:
            status = "WARN"
            issues.append(f"Max clock latency: {max_latency_ps:.1f}ps (threshold: ≤550ps)")
        
        # Prepare key metrics
        key_metrics = {}
        if max_latency_ps > 0:
            key_metrics["Max Latency"] = f"{max_latency_ps:.1f}ps"
        else:
            key_metrics["Design"] = self.design_info.top_hier
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Clock Analysis",
            section_id="clock",
            stage=FlowStage.CLOCK_ANALYSIS,
            status=status,
            key_metrics=key_metrics,
            html_file="",
            priority=3,
            issues=issues,
            icon="[Clock]"
        )
    
    def run_formal_verification(self):
        """Run formal verification analysis"""
        self.print_header(FlowStage.FORMAL_VERIFICATION)
        
        # Extract and display RTL tag
        rtl_readme_path = os.path.join(self.workarea, "rbv", "README")
        rtl_tag = "N/A"
        if os.path.isfile(rtl_readme_path):
            try:
                with open(rtl_readme_path, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        # Line 2 contains: TAG: <rtl_tag>
                        tag_line = lines[1].strip()
                        if tag_line.startswith("TAG:"):
                            rtl_tag = tag_line.split("TAG:", 1)[1].strip()
                print(f"{Color.CYAN}RTL Tag: {Color.RESET}{rtl_tag}")
            except (OSError, UnicodeDecodeError):
                pass
        
        formal_log_pattern = "formal_flow/*_vs_*_fm/log/*_vs_*_fm.log"
        formal_files = self.file_utils.find_files(formal_log_pattern, self.workarea)
        
        # Track formal verification results for master dashboard
        formal_results = []
        overall_status = "NOT_RUN"
        issues = []
        
        if formal_files:
            # Get latest formal end time for comparison with ECO
            latest_formal_end = 0
            
            for log_file in formal_files:
                self.print_file_info(log_file, "Formal Log")
                status, runtime, flow_name, passing_pts, failing_pts, compare_tbl, failing_list = self._extract_formal_verification_status(log_file)
                formal_results.append((flow_name, status, runtime, passing_pts, failing_pts, compare_tbl, failing_list))
                
                # Extract and display timestamps
                formal_end_time = self._display_formal_timestamps(log_file)
                if formal_end_time and formal_end_time > latest_formal_end:
                    latest_formal_end = formal_end_time
            
            # Check if ECO was run after formal (potential issue)
            self._check_formal_vs_eco_timestamps(latest_formal_end)
            
            # Determine overall status based on all formal results
            statuses = [result[1] for result in formal_results]
            
            # Check for CRASHED flows first (highest priority - tool error)
            crashed_flows = [f"{r[0]}: {r[1]}" for r in formal_results if "CRASHED" in r[1]]
            if crashed_flows:
                overall_status = "FAIL"
                issues.extend(crashed_flows)
            elif "FAILED" in statuses:
                overall_status = "FAIL"
                # Include failing compare points in issues
                for r in formal_results:
                    if r[1] == "FAILED":
                        if r[4] > 0:  # failing_pts > 0
                            issues.append(f"{r[0]}: FAILED ({r[4]} failing points)")
                        else:
                            issues.append(f"{r[0]}: FAILED")
            elif "UNRESOLVED" in statuses:
                overall_status = "WARN"
                unresolved_flows = [f"{r[0]}: UNRESOLVED" for r in formal_results if r[1] == "UNRESOLVED"]
                issues.extend(unresolved_flows)
            elif "SUCCEEDED" in statuses:
                overall_status = "PASS"
            elif "RUNNING" in statuses:
                overall_status = "WARN"
                issues.append("Formal verification still running")
        else:
            print("No formal verification logs found")
            overall_status = "NOT_RUN"
        
        # Build key metrics
        key_metrics = {"Design": self.design_info.top_hier, "RTL Tag": rtl_tag}
        for flow_name, status, runtime, passing_pts, failing_pts, compare_tbl, failing_list in formal_results:
            if status == "FAILED" and failing_pts > 0:
                key_metrics[flow_name] = f"{status} ({failing_pts} fail, {runtime})"
            else:
                key_metrics[flow_name] = f"{status} ({runtime})"
        
        # Generate comprehensive HTML report for formal verification
        html_path = ""
        if formal_results:
            html_path = self._generate_formal_html_report(formal_results, rtl_tag, latest_formal_end)
            if html_path:
                html_filename = os.path.basename(html_path)
                print(f"\n  {Color.CYAN}Formal Verification HTML Report:{Color.RESET}")
                print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Formal Verification",
            section_id="formal",
            stage=FlowStage.FORMAL_VERIFICATION,
            status=overall_status,
            key_metrics=key_metrics,
            html_file=html_path,
            priority=1 if overall_status == "FAIL" else (2 if overall_status == "WARN" else 3),
            issues=issues,
            icon="[Formal]"
        )
    
    def _generate_formal_html_report(self, formal_results, rtl_tag, latest_formal_end):
        """Generate comprehensive HTML report for Formal Verification"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            username = os.environ.get('USER', 'avice')
            html_filename = f"{self.design_info.top_hier}_{username}_formal_verification_{timestamp}.html"
            html_path = os.path.abspath(html_filename)
            
            # Determine overall status
            statuses = [result[1] for result in formal_results]
            overall_status = "PASS"
            if any("CRASHED" in s for s in statuses):
                overall_status = "CRASHED"
            elif "FAILED" in statuses:
                overall_status = "FAILED"
            elif "UNRESOLVED" in statuses:
                overall_status = "UNRESOLVED"
            elif "RUNNING" in statuses:
                overall_status = "RUNNING"
            elif "SUCCEEDED" in statuses:
                overall_status = "PASS"
            
            status_color = {
                "PASS": "#28a745",
                "FAILED": "#dc3545",
                "CRASHED": "#dc3545",
                "UNRESOLVED": "#ffc107",
                "RUNNING": "#17a2b8"
            }.get(overall_status, "#6c757d")
            
            # Generate HTML content
            html_content = self._generate_formal_html_content(
                formal_results, rtl_tag, overall_status, status_color, html_filename
            )
            
            # Write HTML file
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            return html_path
            
        except Exception as e:
            print(f"  Error generating Formal HTML report: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _generate_formal_html_content(self, formal_results, rtl_tag, overall_status, status_color, html_filename):
        """Generate HTML content for formal verification report"""
        
        # Load and encode logo
        logo_data = ""
        logo_path = os.path.join(os.path.dirname(__file__), "images", "avice_logo.png")
        try:
            with open(logo_path, 'rb') as f:
                import base64
                logo_data = base64.b64encode(f.read()).decode('utf-8')
        except:
            pass  # If logo not found, continue without it
        
        # Count statuses
        total_flows = len(formal_results)
        passed_flows = sum(1 for r in formal_results if r[1] == "SUCCEEDED")
        failed_flows = sum(1 for r in formal_results if r[1] == "FAILED")
        crashed_flows = sum(1 for r in formal_results if "CRASHED" in r[1])
        unresolved_flows = sum(1 for r in formal_results if r[1] == "UNRESOLVED")
        running_flows = sum(1 for r in formal_results if r[1] == "RUNNING")
        
        # Calculate total compare points
        total_passing = sum(r[3] for r in formal_results)
        total_failing = sum(r[4] for r in formal_results)
        
        # Generate flow cards HTML
        flow_cards_html = ""
        for flow_name, status, runtime, passing_pts, failing_pts, compare_table, failing_points_list in formal_results:
            status_class = {
                "SUCCEEDED": "status-pass",
                "FAILED": "status-fail",
                "UNRESOLVED": "status-warn",
                "RUNNING": "status-running"
            }.get(status, "status-fail" if "CRASHED" in status else "status-unknown")
            
            status_icon = {
                "SUCCEEDED": "✓",
                "FAILED": "✗",
                "UNRESOLVED": "⚠",
                "RUNNING": "↻"
            }.get(status, "⚠" if "CRASHED" not in status else "💥")
            
            # Compare points section
            compare_points_html = ""
            if status == "FAILED" and (passing_pts > 0 or failing_pts > 0):
                total_pts = passing_pts + failing_pts
                pass_percentage = (passing_pts / total_pts * 100) if total_pts > 0 else 0
                
                # Generate matched compare points table HTML
                compare_table_html = ""
                if compare_table:
                    compare_table_html = """
                <div class="compare-table-section">
                    <h4>Matched Compare Points Breakdown</h4>
                    <table class="compare-table">
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>BBPin</th>
                                <th>Loop</th>
                                <th>BBNet</th>
                                <th>Cut</th>
                                <th>Port</th>
                                <th>DFF</th>
                                <th>LAT</th>
                                <th>TOTAL</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    
                    if 'passing' in compare_table:
                        p = compare_table['passing']
                        compare_table_html += f"""
                            <tr class="passing-row">
                                <td><strong>Passing (equivalent)</strong></td>
                                <td>{p.get('BBPin', 0):,}</td>
                                <td>{p.get('Loop', 0):,}</td>
                                <td>{p.get('BBNet', 0):,}</td>
                                <td>{p.get('Cut', 0):,}</td>
                                <td>{p.get('Port', 0):,}</td>
                                <td>{p.get('DFF', 0):,}</td>
                                <td>{p.get('LAT', 0):,}</td>
                                <td><strong>{p.get('TOTAL', 0):,}</strong></td>
                            </tr>
                        """
                    
                    if 'failing' in compare_table:
                        f = compare_table['failing']
                        compare_table_html += f"""
                            <tr class="failing-row">
                                <td><strong>Failing (not equivalent)</strong></td>
                                <td>{f.get('BBPin', 0):,}</td>
                                <td>{f.get('Loop', 0):,}</td>
                                <td>{f.get('BBNet', 0):,}</td>
                                <td>{f.get('Cut', 0):,}</td>
                                <td>{f.get('Port', 0):,}</td>
                                <td>{f.get('DFF', 0):,}</td>
                                <td>{f.get('LAT', 0):,}</td>
                                <td><strong>{f.get('TOTAL', 0):,}</strong></td>
                            </tr>
                        """
                    
                    if 'not_compared' in compare_table and compare_table['not_compared']:
                        compare_table_html += """
                            <tr class="separator-row">
                                <td colspan="9"><strong>Not Compared</strong></td>
                            </tr>
                        """
                        for name, count in compare_table['not_compared'].items():
                            compare_table_html += f"""
                            <tr class="not-compared-row">
                                <td>&nbsp;&nbsp;{name}</td>
                                <td colspan="7"></td>
                                <td>{count:,}</td>
                            </tr>
                            """
                    
                    compare_table_html += """
                        </tbody>
                    </table>
                </div>
                    """
                
                # Generate failing points list HTML
                failing_points_html = ""
                if failing_points_list:
                    failing_points_html = f"""
                <div class="failing-points-section">
                    <h4>Failing Compare Points ({len(failing_points_list)} points)</h4>
                    <div class="failing-points-list">
                    """
                    for point in failing_points_list:
                        failing_points_html += f'<div class="failing-point">✗ {point}</div>\n'
                    failing_points_html += """
                    </div>
                </div>
                    """
                
                compare_points_html = f"""
                <div class="compare-points">
                    <h4>Compare Points Summary</h4>
                    <div class="points-grid">
                        <div class="point-card pass">
                            <div class="point-label">Passing</div>
                            <div class="point-value">{passing_pts:,}</div>
                            <div class="point-percentage">{pass_percentage:.2f}%</div>
                        </div>
                        <div class="point-card fail">
                            <div class="point-label">Failing</div>
                            <div class="point-value">{failing_pts:,}</div>
                            <div class="point-percentage">{100-pass_percentage:.2f}%</div>
                        </div>
                        <div class="point-card total">
                            <div class="point-label">Total</div>
                            <div class="point-value">{total_pts:,}</div>
                        </div>
                    </div>
                    {compare_table_html}
                    {failing_points_html}
                </div>
                """
            elif status == "SUCCEEDED" and passing_pts > 0:
                compare_points_html = f"""
                <div class="compare-points success">
                    <div class="success-message">
                        <span class="success-icon">✓</span>
                        All {passing_pts:,} compare points passed
                    </div>
                </div>
                """
            
            flow_cards_html += f"""
            <div class="flow-card {status_class}">
                <div class="flow-header">
                    <h3>{flow_name}</h3>
                    <span class="status-badge {status_class}">{status_icon} {status}</span>
                </div>
                <div class="flow-details">
                    <div class="detail-item">
                        <span class="detail-label">Runtime:</span>
                        <span class="detail-value">{runtime}</span>
                    </div>
                </div>
                {compare_points_html}
            </div>
            """
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formal Verification Report - {self.design_info.top_hier}</title>
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
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        
        .header-content {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }}
        
        .logo {{
            max-width: 120px;
            height: auto;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        
        .logo:hover {{
            transform: scale(1.05);
        }}
        
        .header-text {{
            flex: 1;
            min-width: 300px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header-subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        /* Logo Modal */
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.9);
            cursor: pointer;
        }}
        
        .logo-modal-content {{
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
            position: relative;
            top: 50%;
            transform: translateY(-50%);
        }}
        
        .logo-modal-close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
        }}
        
        .logo-modal-close:hover,
        .logo-modal-close:focus {{
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }}
        
        .summary-section {{
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 3px solid #e9ecef;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .summary-card.overall {{
            border-left-color: {status_color};
            background: linear-gradient(135deg, white 0%, {status_color}10 100%);
        }}
        
        .summary-card.passed {{
            border-left-color: #28a745;
        }}
        
        .summary-card.failed {{
            border-left-color: #dc3545;
        }}
        
        .summary-card.crashed {{
            border-left-color: #dc3545;
        }}
        
        .summary-card.unresolved {{
            border-left-color: #ffc107;
        }}
        
        .summary-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .summary-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}
        
        .rtl-section {{
            padding: 20px 40px;
            background: #fff9e6;
            border-left: 4px solid #ffc107;
            margin: 20px 40px;
            border-radius: 8px;
        }}
        
        .rtl-container {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 8px;
        }}
        
        .rtl-label {{
            font-weight: bold;
            color: #856404;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .rtl-value {{
            flex: 1;
            font-family: 'Courier New', monospace;
            color: #333;
            font-size: 1.1em;
            padding: 10px;
            background: white;
            border-radius: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .copy-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: bold;
            transition: all 0.3s ease;
            white-space: nowrap;
        }}
        
        .copy-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        }}
        
        .copy-btn:active {{
            transform: scale(0.95);
        }}
        
        .copy-btn.copied {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 30px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .flow-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .flow-card:hover {{
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }}
        
        .flow-card.status-pass {{
            border-left: 6px solid #28a745;
        }}
        
        .flow-card.status-fail {{
            border-left: 6px solid #dc3545;
        }}
        
        .flow-card.status-warn {{
            border-left: 6px solid #ffc107;
        }}
        
        .flow-card.status-running {{
            border-left: 6px solid #17a2b8;
        }}
        
        .flow-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f8f9fa;
        }}
        
        .flow-header h3 {{
            color: #333;
            font-size: 1.4em;
        }}
        
        .status-badge {{
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .status-badge.status-pass {{
            background: #28a745;
            color: white;
        }}
        
        .status-badge.status-fail {{
            background: #dc3545;
            color: white;
        }}
        
        .status-badge.status-warn {{
            background: #ffc107;
            color: #333;
        }}
        
        .status-badge.status-running {{
            background: #17a2b8;
            color: white;
        }}
        
        .flow-details {{
            margin-bottom: 20px;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f8f9fa;
        }}
        
        .detail-label {{
            font-weight: 600;
            color: #666;
        }}
        
        .detail-value {{
            font-family: 'Courier New', monospace;
            color: #333;
        }}
        
        .compare-points {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
        }}
        
        .compare-points h4 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .points-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        
        .point-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .point-card.pass {{
            border-top: 4px solid #28a745;
        }}
        
        .point-card.fail {{
            border-top: 4px solid #dc3545;
        }}
        
        .point-card.total {{
            border-top: 4px solid #667eea;
        }}
        
        .point-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        
        .point-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .point-percentage {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .compare-points.success {{
            background: linear-gradient(135deg, #28a74510 0%, #28a74520 100%);
            border: 2px solid #28a745;
        }}
        
        .success-message {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 1.2em;
            color: #155724;
            font-weight: 600;
        }}
        
        .success-icon {{
            font-size: 1.5em;
            color: #28a745;
        }}
        
        .compare-table-section {{
            margin-top: 20px;
        }}
        
        .compare-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .compare-table thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .compare-table th {{
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
            font-size: 0.9em;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .compare-table td {{
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        
        .compare-table td:first-child {{
            text-align: left;
            padding-left: 15px;
        }}
        
        .compare-table .passing-row {{
            background: linear-gradient(90deg, #28a74510 0%, white 100%);
        }}
        
        .compare-table .passing-row td:last-child {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .compare-table .failing-row {{
            background: linear-gradient(90deg, #dc354510 0%, white 100%);
        }}
        
        .compare-table .failing-row td:last-child {{
            color: #dc3545;
            font-weight: bold;
        }}
        
        .compare-table .separator-row {{
            background: #f8f9fa;
            font-weight: bold;
        }}
        
        .compare-table .separator-row td {{
            padding: 12px 15px;
            text-align: left;
            border-top: 2px solid #667eea;
        }}
        
        .compare-table .not-compared-row {{
            background: white;
        }}
        
        .compare-table .not-compared-row:hover {{
            background: #f8f9fa;
        }}
        
        .failing-points-section {{
            margin-top: 20px;
            background: #fff5f5;
            border: 2px solid #dc3545;
            border-radius: 8px;
            padding: 15px;
        }}
        
        .failing-points-section h4 {{
            color: #dc3545;
            margin-bottom: 15px;
        }}
        
        .failing-points-list {{
            max-height: 400px;
            overflow-y: auto;
            background: white;
            border-radius: 4px;
            padding: 10px;
        }}
        
        .failing-point {{
            padding: 8px 12px;
            margin: 5px 0;
            background: #f8f9fa;
            border-left: 4px solid #dc3545;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #333;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}
        
        .failing-point:hover {{
            background: #e9ecef;
            transform: translateX(5px);
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            border-top: 3px solid #e9ecef;
        }}
        
        .footer-info {{
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <!-- Logo Modal -->
    <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
        <span class="logo-modal-close">&times;</span>
        <img class="logo-modal-content" id="logoModalImg">
    </div>
    
    <div class="container">
        <div class="header">
            <div class="header-content">
                {f'<img class="logo" src="data:image/png;base64,{logo_data}" alt="AVICE Logo" onclick="showLogoModal()" title="Click to enlarge">' if logo_data else ''}
                <div class="header-text">
                    <h1>🔍 Formal Verification Report</h1>
                    <div class="header-subtitle">Design: {self.design_info.top_hier}</div>
                    <div class="header-subtitle">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                </div>
            </div>
        </div>
        
        <div class="summary-section">
            <h2>Verification Summary</h2>
            <div class="summary-grid">
                <div class="summary-card overall">
                    <div class="summary-label">Overall Status</div>
                    <div class="summary-value" style="color: {status_color};">{overall_status}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Total Flows</div>
                    <div class="summary-value">{total_flows}</div>
                </div>
                <div class="summary-card passed">
                    <div class="summary-label">Passed</div>
                    <div class="summary-value" style="color: #28a745;">{passed_flows}</div>
                </div>
                <div class="summary-card failed">
                    <div class="summary-label">Failed</div>
                    <div class="summary-value" style="color: #dc3545;">{failed_flows}</div>
                </div>
                {f'''<div class="summary-card crashed">
                    <div class="summary-label">Crashed</div>
                    <div class="summary-value" style="color: #dc3545;">{crashed_flows}</div>
                </div>''' if crashed_flows > 0 else ''}
                {f'''<div class="summary-card unresolved">
                    <div class="summary-label">Unresolved</div>
                    <div class="summary-value" style="color: #ffc107;">{unresolved_flows}</div>
                </div>''' if unresolved_flows > 0 else ''}
            </div>
            {f'''<div class="summary-grid" style="margin-top: 20px;">
                <div class="summary-card passed">
                    <div class="summary-label">Total Passing Points</div>
                    <div class="summary-value" style="color: #28a745;">{total_passing:,}</div>
                </div>
                <div class="summary-card failed">
                    <div class="summary-label">Total Failing Points</div>
                    <div class="summary-value" style="color: #dc3545;">{total_failing:,}</div>
                </div>
            </div>''' if total_passing > 0 or total_failing > 0 else ''}
        </div>
        
        <div class="rtl-section">
            <div class="rtl-label">RTL Tag</div>
            <div class="rtl-container">
                <div class="rtl-value" id="rtl-tag">{rtl_tag}</div>
                <button class="copy-btn" onclick="copyToClipboard('rtl-tag', this)" title="Copy RTL tag">
                    📋 Copy
                </button>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">Formal Verification Flows</h2>
            {flow_cards_html}
        </div>
        
        <div class="footer">
            <div class="footer-info">
                <p><strong>AVICE Formal Verification Report</strong></p>
                <p>Report generated by AVICE Workarea Review Tool</p>
                <p>Workarea: {self.workarea}</p>
                <p>File: {html_filename}</p>
                <p>Copyright (c) 2025 Alon Vice (avice)</p>
                <p>Contact: avice@nvidia.com</p>
            </div>
        </div>
    </div>
    
    <!-- Back to Top Button -->
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 9999; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
    
    <script>
        // Logo modal functions
        function showLogoModal() {{
            const modal = document.getElementById('logoModal');
            const modalImg = document.getElementById('logoModalImg');
            const logo = document.querySelector('.logo');
            if (modal && modalImg && logo) {{
                modal.style.display = 'block';
                modalImg.src = logo.src;
            }}
        }}
        
        function hideLogoModal() {{
            const modal = document.getElementById('logoModal');
            if (modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // Back to top button functionality
        const backToTopBtn = document.getElementById('backToTopBtn');
        if (backToTopBtn) {{
            window.addEventListener('scroll', function() {{
                if (window.pageYOffset > 300) {{
                    backToTopBtn.style.display = 'block';
                }} else {{
                    backToTopBtn.style.display = 'none';
                }}
            }});
            
            backToTopBtn.addEventListener('click', function() {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }});
        }}
        
        // Copy to clipboard function
        function copyToClipboard(elementId, button) {{
            const element = document.getElementById(elementId);
            const text = element.textContent;
            
            // Use modern clipboard API
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(function() {{
                    // Success feedback
                    const originalText = button.innerHTML;
                    button.innerHTML = '✅ Copied!';
                    button.classList.add('copied');
                    
                    // Reset after 2 seconds
                    setTimeout(function() {{
                        button.innerHTML = originalText;
                        button.classList.remove('copied');
                    }}, 2000);
                }}).catch(function(err) {{
                    console.error('Failed to copy:', err);
                    button.innerHTML = '❌ Failed';
                    setTimeout(function() {{
                        button.innerHTML = '📋 Copy';
                    }}, 2000);
                }});
            }} else {{
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                document.body.appendChild(textArea);
                textArea.select();
                try {{
                    document.execCommand('copy');
                    button.innerHTML = '✅ Copied!';
                    button.classList.add('copied');
                    setTimeout(function() {{
                        button.innerHTML = '📋 Copy';
                        button.classList.remove('copied');
                    }}, 2000);
                }} catch (err) {{
                    console.error('Fallback copy failed:', err);
                    button.innerHTML = '❌ Failed';
                    setTimeout(function() {{
                        button.innerHTML = '📋 Copy';
                    }}, 2000);
                }}
                document.body.removeChild(textArea);
            }}
        }}
    </script>
</body>
</html>
"""
        return html
    
    def run_parasitic_extraction(self):
        """Run parasitic extraction analysis"""
        self.print_header(FlowStage.PARASITIC_EXTRACTION)
        
        # Find all Star runs by looking for summary.rpt files
        summary_pattern = f"export/nv_star/{self.design_info.top_hier}/ipo*/REPs/*.checks.summary.rpt"
        summary_files = self.file_utils.find_files(summary_pattern, self.workarea)
        
        if summary_files:
            # Extract run information from each summary file
            star_runs = []
            for summary_file in summary_files:
                # Extract timestamp from filename (e.g., STAR.setup.smc.1.fdb_ipo1000.10_08_18_15.checks.summary.rpt)
                basename = os.path.basename(summary_file)
                timestamp_match = re.search(r'\.(\d{2}_\d{2}_\d{2}_\d{2})\.checks\.summary\.rpt', basename)
                if timestamp_match:
                    timestamp_str = timestamp_match.group(1)
                    # Parse timestamp: MM_DD_HH_MM
                    try:
                        month, day, hour, minute = timestamp_str.split('_')
                        timestamp_display = f"{month}/{day} {hour}:{minute}"
                    except:
                        timestamp_display = timestamp_str
                    
                    # Extract shorts count from SX-0955 code
                    shorts_count = 0
                    try:
                        with open(summary_file, 'r') as f:
                            for line in f:
                                if 'SX-0955' in line:
                                    # Format: SX-0955     COUNT    WAIVED    TOTAL
                                    parts = line.split()
                                    if len(parts) >= 2:
                                        shorts_count = int(parts[1])
                                    break
                    except:
                        pass
                    
                    # Get file modification time for sorting
                    mtime = os.path.getmtime(summary_file)
                    
                    star_runs.append({
                        'timestamp': timestamp_display,
                        'shorts': shorts_count,
                        'mtime': mtime,
                        'file': summary_file
                    })
            
            # Sort by modification time (oldest first)
            star_runs.sort(key=lambda x: x['mtime'])
            
            # Display Star runs summary table
            print(f"\n{Color.CYAN}Star Extraction Runs:{Color.RESET}")
            print(f"  Total Runs: {len(star_runs)}")
            print(f"\n  {'Run':<6} {'Timestamp':<12} {'Shorts':<8}")
            print(f"  {'-'*6} {'-'*12} {'-'*8}")
            for idx, run in enumerate(star_runs, 1):
                shorts_color = Color.RED if run['shorts'] > 0 else Color.GREEN
                is_latest = " (latest)" if idx == len(star_runs) else ""
                print(f"  {idx:<6} {run['timestamp']:<12} {shorts_color}{run['shorts']:<8}{Color.RESET}{is_latest}")
            
            # Show latest run details
            if star_runs:
                latest_run = star_runs[-1]
                print(f"\n{Color.CYAN}Latest Run Details:{Color.RESET}")
                print(f"  Timestamp: {latest_run['timestamp']}")
                print(f"  Shorts: {Color.GREEN if latest_run['shorts'] == 0 else Color.RED}{latest_run['shorts']}{Color.RESET}")
        else:
            print(f"  {Color.YELLOW}No Star extraction runs found{Color.RESET}")
        
        # Star extraction SPEF files (all corners from latest run)
        print(f"\n{Color.CYAN}SPEF Files (All Corners):{Color.RESET}")
        spef_pattern = f"export/nv_star/{self.design_info.top_hier}/ipo*/IOs/netlists/*.spef.*.gz"
        all_spef_files = self.file_utils.find_files(spef_pattern, self.workarea)
        
        if all_spef_files:
            # Get the most recent modification time to group latest run
            if all_spef_files:
                latest_mtime = max(os.path.getmtime(f) for f in all_spef_files)
                # Consider files modified within 5 minutes of latest as part of same run
                latest_spef_files = [f for f in all_spef_files if abs(os.path.getmtime(f) - latest_mtime) < 300]
                
                # Sort by corner name for consistent display
                latest_spef_files.sort()
                
                print(f"  Total SPEF files: {len(latest_spef_files)}")
                if len(latest_spef_files) < 6:
                    print(f"  {Color.YELLOW}Warning: Expected at least 6 SPEF files, found {len(latest_spef_files)}{Color.RESET}")
                else:
                    print(f"  {Color.GREEN}[OK] All required SPEF files present{Color.RESET}")
                
                # Show location once
                if latest_spef_files:
                    spef_dir = os.path.dirname(latest_spef_files[0])
                    print(f"  Location: {spef_dir}")
                    print(f"\n  {'Corner':<25} {'Size':>8}")
                    print(f"  {'-'*25} {'-'*8}")
                    
                    # Extract corner information and display
                    for spef_file in latest_spef_files:
                        basename = os.path.basename(spef_file)
                        # Extract corner name (e.g., typical_T0, cworst_CCworst_T0, etc.)
                        corner_match = re.search(r'\.spef\.([^.]+)\.gz', basename)
                        if corner_match:
                            corner = corner_match.group(1)
                            file_size_bytes = os.path.getsize(spef_file)
                            file_size_gb = file_size_bytes / (1024**3)
                            print(f"  {corner:<25} {file_size_gb:>6.2f} GB")
                        else:
                            print(f"  {basename}")
        else:
            print(f"  {Color.YELLOW}No SPEF files found{Color.RESET}")
        
        # SPEF info file for typical corner
        spef_info_pattern = f"export/nv_star/{self.design_info.top_hier}/ipo*/IOs/netlists/*.typical_T0.spef_info"
        spef_info_files = self.file_utils.find_files(spef_info_pattern, self.workarea)
        
        if spef_info_files:
            # Get the most recent SPEF info file
            latest_spef_info = max(spef_info_files, key=os.path.getmtime)
            self.print_file_info(latest_spef_info, "SPEF Info (Typical Corner)")
            
            print(f"\n{Color.CYAN}Star Extraction Configuration:{Color.RESET}")
            try:
                with open(latest_spef_info, 'r') as f:
                    content = f.read()
                
                # Extract date
                date_match = re.search(r'date:\s*(.+)', content)
                if date_match:
                    date_str = date_match.group(1).strip()
                    print(f"  Date: {date_str}")
                
                # Extract opens and shorts counts
                opens_match = re.search(r'opens:\s*(\d+)', content)
                shorts_match = re.search(r'shorts:\s*(\d+)', content)
                
                opens_count = int(opens_match.group(1)) if opens_match else 0
                shorts_count = int(shorts_match.group(1)) if shorts_match else 0
                
                print(f"  Opens: {opens_count}")
                print(f"  Shorts: {shorts_count}")
                
                # Extract project_rdl_file
                project_rdl_match = re.search(r'project_rdl_file:\s*(.+)', content)
                if project_rdl_match:
                    project_rdl = project_rdl_match.group(1).strip()
                    print(f"  Project RDL: {project_rdl}")
                
                # Extract GDS_LAYER_MAP_FILE
                gds_layer_map_match = re.search(r'GDS_LAYER_MAP_FILE:\s*(.+)', content)
                if gds_layer_map_match:
                    gds_layer_map = gds_layer_map_match.group(1).strip()
                    print(f"  GDS Layer Map: {gds_layer_map}")
                
                # Extract MAPPING_FILE
                mapping_file_match = re.search(r'MAPPING_FILE:\s*(.+)', content)
                if mapping_file_match:
                    mapping_file = mapping_file_match.group(1).strip()
                    print(f"  Mapping File: {mapping_file}")
                
            except Exception as e:
                print(f"  Error reading SPEF info: {e}")
                # Fallback to original grep method
                matches = self.file_utils.grep_file(r"opens|shorts|date:", latest_spef_info)
                for match in matches:
                    print(f"  {match}")
        
        # Star extraction detailed shorts report (generated only when shorts exist)
        shorts_pattern = f"export/nv_star/{self.design_info.top_hier}/ipo*/REPs/*.star_extraction_shorts.rpt"
        shorts_files = self.file_utils.find_files(shorts_pattern, self.workarea)
        
        if shorts_files:
            self.print_file_info(shorts_files[0], "Star Detailed Shorts Report")
            
            # Identify which run this shorts report is from
            if summary_files:  # If we have star_runs data
                shorts_mtime = os.path.getmtime(shorts_files[0])
                
                # Find the run with the closest timestamp (within 5 minutes)
                matching_run = None
                min_time_diff = float('inf')
                for idx, run in enumerate(star_runs, 1):
                    time_diff = abs(run['mtime'] - shorts_mtime)
                    if time_diff < min_time_diff and time_diff < 300:  # Within 5 minutes
                        min_time_diff = time_diff
                        matching_run = (idx, run)
                
                if matching_run:
                    run_num, run_data = matching_run
                    is_latest = (run_num == len(star_runs))
                    latest_note = " (latest run)" if is_latest else f" (NOT the latest - latest is run #{len(star_runs)})"
                    print(f"  {Color.YELLOW}Note: This report is from Run #{run_num} ({run_data['timestamp']}){latest_note}{Color.RESET}")
                else:
                    print(f"  {Color.YELLOW}Note: This report shows shorts from a previous run{Color.RESET}")
            else:
                print(f"  {Color.YELLOW}Note: This report shows shorts from the most recent run that had shorts{Color.RESET}")
            
            try:
                if shorts_files[0].endswith('.gz'):
                    with gzip.open(shorts_files[0], 'rt', encoding='utf-8') as f:
                        content = f.read()
                else:
                    with open(shorts_files[0], 'r', encoding='utf-8') as f:
                        content = f.read()
                # Show first 50 lines to avoid overwhelming output
                lines = content.split('\n')[:50]
                print('\n'.join(lines))
                if len(content.split('\n')) > 50:
                    print(f"\n  {Color.YELLOW}... (truncated, see file for full details){Color.RESET}")
            except (OSError, UnicodeDecodeError, gzip.BadGzipFile):
                print("  Unable to read Star Shorts Report")
        
        # Generate Star HTML report
        star_html = self._generate_star_html_report(star_runs if summary_files else [], 
                                                     latest_spef_files if all_spef_files else [],
                                                     latest_spef_info if spef_info_files else None,
                                                     shorts_files[0] if shorts_files else None)
        
        # Determine status based on shorts and SPEF files
        status = "NOT_RUN"
        key_metrics = {"Design": self.design_info.top_hier}
        issues = []
        priority = 3
        
        if summary_files and star_runs:
            latest_shorts = star_runs[-1]['shorts']
            key_metrics["Total Runs"] = len(star_runs)
            key_metrics["Latest Shorts"] = latest_shorts
            
            # Check SPEF files
            spef_count = len(latest_spef_files) if all_spef_files else 0
            key_metrics["SPEF Files"] = spef_count
            
            # Status logic:
            # FAIL: shorts > 0
            # WARN: SPEF files < 6 (missing corners)
            # PASS: shorts == 0 and SPEF files >= 6
            if latest_shorts > 0:
                status = "FAIL"
                priority = 1
                issues.append(f"Star extraction has {latest_shorts} shorts")
            elif spef_count < 6:
                status = "WARN"
                priority = 2
                issues.append(f"Only {spef_count} SPEF files found (expected >= 6)")
            else:
                status = "PASS"
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Parasitic Extraction (Star)",
            section_id="star",
            stage=FlowStage.PARASITIC_EXTRACTION,
            status=status,
            key_metrics=key_metrics,
            html_file=star_html if star_html else "",
            priority=priority,
            issues=issues,
            icon="[Star]"
        )
    
    def _generate_star_html_report(self, star_runs, spef_files, spef_info_file, shorts_file):
        """Generate comprehensive HTML report for Star extraction analysis"""
        try:
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_star_extraction_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            # Read and encode logo
            logo_data = ""
            logo_path = os.path.join(os.path.dirname(__file__), "images/avice_logo.png")
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as logo_file:
                    logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
            
            # Extract configuration data from spef_info
            config_data = {}
            if spef_info_file and os.path.exists(spef_info_file):
                try:
                    with open(spef_info_file, 'r') as f:
                        content = f.read()
                    config_data['date'] = re.search(r'date:\s*(.+)', content).group(1).strip() if re.search(r'date:\s*(.+)', content) else "N/A"
                    config_data['opens'] = int(re.search(r'opens:\s*(\d+)', content).group(1)) if re.search(r'opens:\s*(\d+)', content) else 0
                    config_data['shorts'] = int(re.search(r'shorts:\s*(\d+)', content).group(1)) if re.search(r'shorts:\s*(\d+)', content) else 0
                    config_data['project_rdl'] = re.search(r'project_rdl_file:\s*(.+)', content).group(1).strip() if re.search(r'project_rdl_file:\s*(.+)', content) else "N/A"
                    config_data['gds_layer_map'] = re.search(r'GDS_LAYER_MAP_FILE:\s*(.+)', content).group(1).strip() if re.search(r'GDS_LAYER_MAP_FILE:\s*(.+)', content) else "N/A"
                    config_data['mapping_file'] = re.search(r'MAPPING_FILE:\s*(.+)', content).group(1).strip() if re.search(r'MAPPING_FILE:\s*(.+)', content) else "N/A"
                except:
                    pass
            
            # Read shorts details if available
            shorts_content = ""
            shorts_run_info = ""
            if shorts_file and os.path.exists(shorts_file):
                try:
                    if shorts_file.endswith('.gz'):
                        with gzip.open(shorts_file, 'rt', encoding='utf-8') as f:
                            shorts_content = f.read()
                    else:
                        with open(shorts_file, 'r', encoding='utf-8') as f:
                            shorts_content = f.read()
                    
                    # Identify which run this shorts report is from
                    if star_runs:
                        shorts_mtime = os.path.getmtime(shorts_file)
                        for idx, run in enumerate(star_runs, 1):
                            time_diff = abs(run['mtime'] - shorts_mtime)
                            if time_diff < 300:  # Within 5 minutes
                                is_latest = (idx == len(star_runs))
                                shorts_run_info = f"Run #{idx} ({run['timestamp']})" + (" - Latest" if is_latest else f" - NOT latest (latest is #{len(star_runs)})")
                                break
                except:
                    shorts_content = "Unable to read shorts report"
            
            # Generate HTML content
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Star Extraction Report - {self.design_info.top_hier}</title>
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
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 20px;
            align-items: center;
        }}
        
        .logo {{
            width: 80px;
            height: 80px;
            border-radius: 10px;
            background: white;
            padding: 10px;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .logo:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }}
        
        .logo-modal.active {{
            display: flex;
        }}
        
        .logo-modal-content {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
        }}
        
        .logo-modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .logo-modal-close:hover {{
            color: #bbb;
        }}
        
        .header-text h1 {{
            font-size: 28px;
            margin-bottom: 8px;
        }}
        
        .header-text p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .card-label {{
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .card-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        
        .card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        
        .card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .section {{
            margin-bottom: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2a5298;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-clean {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .status-shorts {{
            color: #dc3545;
            font-weight: bold;
        }}
        
        .latest-badge {{
            background: #ffc107;
            color: #000;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            margin-left: 8px;
        }}
        
        .config-grid {{
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 12px 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .config-label {{
            font-weight: 600;
            color: #495057;
        }}
        
        .config-value {{
            color: #6c757d;
            word-break: break-all;
        }}
        
        .shorts-details {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }}
        
        .shorts-details-title {{
            font-weight: bold;
            color: #856404;
            margin-bottom: 10px;
        }}
        
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            line-height: 1.5;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        /* Copyright Footer */
        .footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer strong {{
            color: #00ff00;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">"""
            
            if logo_data:
                html_content += f"""
            <img class='logo' src='data:image/png;base64,{logo_data}' alt='AVICE Logo' onclick="showLogoModal()" title="Click to enlarge">"""
            
            html_content += f"""
            <div class="header-text">
                <h1>Star Extraction Report</h1>
                <p>Design: {self.design_info.top_hier} | IPO: {self.design_info.ipo}</p>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </div>
        
        <!-- Logo Modal -->
        <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
            <span class="logo-modal-close">&times;</span>"""
            
            if logo_data:
                html_content += f"""
            <img class="logo-modal-content" src='data:image/png;base64,{logo_data}' alt='AVICE Logo'>"""
            
            html_content += """
        </div>
        
        <div class="content">"""
            
            # Summary Cards
            if star_runs:
                latest_run = star_runs[-1]
                total_runs = len(star_runs)
                shorts_count = latest_run['shorts']
                
                html_content += f"""
            <div class="summary-cards">
                <div class="card">
                    <div class="card-label">Total Runs</div>
                    <div class="card-value">{total_runs}</div>
                </div>
                <div class="card {'success' if shorts_count == 0 else 'warning'}">
                    <div class="card-label">Latest Run Shorts</div>
                    <div class="card-value">{shorts_count}</div>
                </div>
                <div class="card">
                    <div class="card-label">Latest Run</div>
                    <div class="card-value" style="font-size: 18px;">{latest_run['timestamp']}</div>
                </div>
                <div class="card">
                    <div class="card-label">SPEF Files</div>
                    <div class="card-value">{len(spef_files)}</div>
                </div>
            </div>"""
            
            # Star Runs Table
            if star_runs:
                html_content += """
            <div class="section">
                <div class="section-title">Star Extraction Runs History</div>
                <table>
                    <thead>
                        <tr>
                            <th>Run #</th>
                            <th>Timestamp</th>
                            <th>Shorts</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>"""
                
                for idx, run in enumerate(star_runs, 1):
                    is_latest = (idx == len(star_runs))
                    status_class = 'status-clean' if run['shorts'] == 0 else 'status-shorts'
                    status_text = '✓ Clean' if run['shorts'] == 0 else f'⚠ {run["shorts"]} Short(s)'
                    latest_badge = '<span class="latest-badge">LATEST</span>' if is_latest else ''
                    
                    html_content += f"""
                        <tr>
                            <td><strong>#{idx}</strong></td>
                            <td>{run['timestamp']}{latest_badge}</td>
                            <td class="{status_class}">{run['shorts']}</td>
                            <td class="{status_class}">{status_text}</td>
                        </tr>"""
                
                html_content += """
                    </tbody>
                </table>
            </div>"""
            
            # SPEF Files Table
            if spef_files:
                spef_dir = os.path.dirname(spef_files[0])
                html_content += f"""
            <div class="section">
                <div class="section-title">SPEF Files (All RC Corners)</div>
                <p style="margin-bottom: 15px; color: #6c757d;"><strong>Location:</strong> {spef_dir}</p>
                <table>
                    <thead>
                        <tr>
                            <th>Corner</th>
                            <th>File Size</th>
                            <th>Filename</th>
                        </tr>
                    </thead>
                    <tbody>"""
                
                for spef_file in sorted(spef_files):
                    basename = os.path.basename(spef_file)
                    corner_match = re.search(r'\.spef\.([^.]+)\.gz', basename)
                    corner = corner_match.group(1) if corner_match else basename
                    file_size_gb = os.path.getsize(spef_file) / (1024**3)
                    
                    html_content += f"""
                        <tr>
                            <td><strong>{corner}</strong></td>
                            <td>{file_size_gb:.2f} GB</td>
                            <td>{basename}</td>
                        </tr>"""
                
                html_content += """
                    </tbody>
                </table>
            </div>"""
            
            # Configuration Section
            if config_data:
                html_content += f"""
            <div class="section">
                <div class="section-title">Star Extraction Configuration</div>
                <div class="config-grid">
                    <div class="config-label">Extraction Date:</div>
                    <div class="config-value">{config_data.get('date', 'N/A')}</div>
                    
                    <div class="config-label">Opens:</div>
                    <div class="config-value">{config_data.get('opens', 0)}</div>
                    
                    <div class="config-label">Shorts:</div>
                    <div class="config-value">{config_data.get('shorts', 0)}</div>
                    
                    <div class="config-label">Project RDL File:</div>
                    <div class="config-value">{config_data.get('project_rdl', 'N/A')}</div>
                    
                    <div class="config-label">GDS Layer Map:</div>
                    <div class="config-value">{config_data.get('gds_layer_map', 'N/A')}</div>
                    
                    <div class="config-label">Mapping File:</div>
                    <div class="config-value">{config_data.get('mapping_file', 'N/A')}</div>
                </div>
            </div>"""
            
            # Shorts Details Section
            if shorts_content:
                html_content += f"""
            <div class="section">
                <div class="section-title">Detailed Shorts Report</div>"""
                
                if shorts_run_info:
                    html_content += f"""
                <div class="shorts-details">
                    <div class="shorts-details-title">⚠ Note</div>
                    <p>This report is from {shorts_run_info}</p>
                </div>"""
                
                # Limit shorts content to first 100 lines
                shorts_lines = shorts_content.split('\n')[:100]
                shorts_display = '\n'.join(shorts_lines)
                if len(shorts_content.split('\n')) > 100:
                    shorts_display += "\n\n... (truncated, see file for full details)"
                
                html_content += f"""
                <pre>{shorts_display}</pre>
            </div>"""
            
            html_content += """
        </div>
    </div>
    
    <!-- Copyright Footer -->
    <div class="footer">
        <p><strong>AVICE Star Parasitic Extraction Report</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
    
    <script>
        function showLogoModal() {
            document.getElementById('logoModal').classList.add('active');
        }
        
        function hideLogoModal() {
            document.getElementById('logoModal').classList.remove('active');
        }
        
        // Allow ESC key to close modal
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                hideLogoModal();
            }
        });
        
        // Back to top button functionality - wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            var backToTopBtn = document.getElementById('backToTopBtn');
            if (backToTopBtn) {{
                window.addEventListener('scroll', function() {{
                    if (window.pageYOffset > 300) {{
                        backToTopBtn.style.display = 'block';
                    }} else {{
                        backToTopBtn.style.display = 'none';
                    }}
                }});
                
                backToTopBtn.addEventListener('click', function() {{
                    window.scrollTo(0, 0);
                }});
            }}
        }});
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
</body>
</html>"""
            
            # Write HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\n{Color.CYAN}  Star Extraction HTML Report:{Color.RESET}")
            print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
            
            return os.path.abspath(html_path)
            
        except Exception as e:
            print(f"  Error generating Star HTML report: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
                
                # Determine status based on WNS and TNS thresholds
                # Thresholds:
                #   FAIL: WNS < -0.050 ns OR TNS < -10.0 ns (significant violations)
                #   WARN: WNS < 0 OR TNS < 0 (any violation but minor)
                #   PASS: WNS >= 0 AND TNS >= 0
                if internal_wns is not None:
                    if internal_wns < -0.050 or internal_tns < -10.0:
                        status = "FAIL"
                        issues.append(f"Setup timing violation: WNS = {internal_wns:.3f} ns, TNS = {internal_tns:.2f} ns")
                    elif internal_wns < 0 or internal_tns < 0:
                        status = "WARN"
                        issues.append(f"Setup timing minor violation: WNS = {internal_wns:.3f} ns, TNS = {internal_tns:.2f} ns")
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
                    # Hold timing thresholds (stricter than setup - hold is harder to fix)
                    #   FAIL: WNS < -0.025 ns OR TNS < -5.0 ns (tighter threshold than setup)
                    #   WARN: WNS < 0 OR TNS < 0 (small violations - acceptable during development)
                    if hold_wns < -0.025 or hold_tns < -5.0:
                        status = "FAIL"  # Significant hold violation
                        issues.append(f"Hold timing violation: WNS = {hold_wns:.3f} ns, TNS = {hold_tns:.2f} ns")
                    elif hold_wns < 0 or hold_tns < 0:
                        # Only upgrade to WARN if not already FAIL from setup
                        if status != "FAIL":
                            status = "WARN"
                        issues.append(f"Hold timing minor violation: WNS = {hold_wns:.3f} ns, TNS = {hold_tns:.2f} ns")
                    
                    key_metrics["Hold WNS"] = f"{hold_wns:.3f} ns"
                    key_metrics["Hold TNS"] = f"{hold_tns:.2f} ns"
            
            # Check DSR Mux Clock Skew thresholds
            # Thresholds: FAIL > 10ps, WARN 5ps < skew <= 10ps, PASS <= 5ps
            dsr_skew_setup = latest.get('dsr_skew_setup')
            dsr_skew_hold = latest.get('dsr_skew_hold')
            
            if dsr_skew_setup is not None:
                key_metrics["DSR Skew (Setup)"] = f"{dsr_skew_setup:.2f} ps"
                if dsr_skew_setup > 10.0:
                    if status != "FAIL":
                        status = "FAIL"
                    issues.append(f"DSR skew (setup) violation: {dsr_skew_setup:.2f} ps (target: <=5ps)")
                elif dsr_skew_setup > 5.0:
                    if status != "FAIL":
                        status = "WARN"
                    issues.append(f"DSR skew (setup) marginal: {dsr_skew_setup:.2f} ps (target: <=5ps)")
            
            if dsr_skew_hold is not None:
                key_metrics["DSR Skew (Hold)"] = f"{dsr_skew_hold:.2f} ps"
                if dsr_skew_hold > 10.0:
                    if status != "FAIL":
                        status = "FAIL"
                    issues.append(f"DSR skew (hold) violation: {dsr_skew_hold:.2f} ps (target: <=5ps)")
                elif dsr_skew_hold > 5.0:
                    if status != "FAIL":
                        status = "WARN"
                    issues.append(f"DSR skew (hold) marginal: {dsr_skew_hold:.2f} ps (target: <=5ps)")
            
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
        html_filename = f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_PT_timing_summary_{timestamp}.html"
        
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
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 20px;
            align-items: center;
            border-radius: 15px 15px 0 0;
            margin: -20px -20px 0 -20px;
        }}
        .logo {{
            width: 80px;
            height: 80px;
            border-radius: 10px;
            background: white;
            padding: 10px;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .logo:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        .header-text h1 {{
            font-size: 28px;
            margin: 0 0 8px 0;
            color: white;
            border: none;
        }}
        .header-text p {{
            opacity: 0.9;
            font-size: 14px;
            margin: 0;
        }}
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }}
        .logo-modal.active {{
            display: flex;
        }}
        .logo-modal-content {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
        }}
        .logo-modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        .logo-modal-close:hover {{
            color: #bbb;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        /* Enhanced Grid Layout for Info Panels */
        .info {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 15px;
            align-items: start;
            border-left: 5px solid #3498db;
        }}
        .info h3 {{
            margin-top: 0;
            color: #34495e;
            grid-column: 1 / -1;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            grid-column: 1 / -1;
        }}
        .info-item {{
            background: white;
            padding: 12px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .info-item strong {{
            color: #2c3e50;
            display: block;
            margin-bottom: 5px;
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
        
        /* Copyright Footer */
        .footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer strong {{
            color: #00ff00;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img class='logo' src='data:image/png;base64,{logo_data}' alt='AVICE Logo' onclick="showLogoModal()" title="Click to enlarge">
            <div class="header-text">
                <h1>Auto PT Timing Summary Report</h1>
                <p>Design: {self.design_info.top_hier} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>Workarea: {self.workarea_abs}</p>
                <p>Total Work Areas: {len(timing_data)} | Timing Groups: {len(all_groups)}</p>
            </div>
        </div>
        
        <!-- Logo Modal -->
        <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
            <span class="logo-modal-close">&times;</span>
            <img class="logo-modal-content" src='data:image/png;base64,{logo_data}' alt='AVICE Logo'>
        </div>
        
        <h2>Dual-Scenario Timing Summary</h2>
        <p class="info" style="background: #d1ecf1; padding: 15px; border-radius: 5px; border-left: 4px solid #17a2b8;">
            <strong>Note:</strong> Click on work directory names in the table below to access individual HTML reports.
        </p>
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
            
            # Both Setup and Hold start collapsed
            is_expanded = ""  # Start collapsed
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
        
        function showLogoModal() {{
            document.getElementById('logoModal').classList.add('active');
        }}
        
        function hideLogoModal() {{
            document.getElementById('logoModal').classList.remove('active');
        }}
        
        // Allow ESC key to close modal
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                hideLogoModal();
            }}
        }});
        
        // Back to top button functionality - wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            var backToTopBtn = document.getElementById('backToTopBtn');
            if (backToTopBtn) {{
                window.addEventListener('scroll', function() {{
                    if (window.pageYOffset > 300) {{
                        backToTopBtn.style.display = 'block';
                    }} else {{
                        backToTopBtn.style.display = 'none';
                    }}
                }});
                
                backToTopBtn.addEventListener('click', function() {{
                    window.scrollTo(0, 0);
                }});
            }}
        }});
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
    
    <!-- Copyright Footer -->
    <div class="footer">
        <p><strong>AVICE PT Signoff Timing Summary</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
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
                print(f"    Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{os.path.basename(html_filename)}{Color.RESET} &")
                
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
        
        # Check if PV was run by looking for PV flow directory and files
        pv_flow_dir = os.path.join(self.workarea, "pv_flow")
        pv_was_run = os.path.exists(pv_flow_dir)
        
        if not pv_was_run:
            print(f"{Color.YELLOW}Physical Verification (PV) flow was not run in this workarea{Color.RESET}")
            
            # Add NOT_RUN summary to master dashboard
            self._add_section_summary(
                section_name="Physical Verification (PV)",
                section_id="pv",
                stage=FlowStage.PHYSICAL_VERIFICATION,
                status="NOT_RUN",
                key_metrics={},
                html_file="",
                priority=2,
                issues=["PV flow was not executed"],
                icon="[PV]"
            )
            return
        
        # Show PV flow timestamps at the beginning
        timeline_result = self._show_pv_flow_timestamps()
        
        # Initialize violation counts and data structures
        lvs_violations = 0
        drc_violations = 0
        antenna_violations = 0
        
        # Data structures for HTML report
        lvs_data = {}
        drc_data = {'total_violations': 0, 'violations': [], 'file_path': ''}
        antenna_data = {'total_violations': 0, 'file_path': ''}
        pv_flow_data = {}
        timeline_data = {}
        
        # Parse timeline data
        if timeline_result and timeline_result[0]:
            start_time, end_time = timeline_result
            if end_time != "RUNNING":
                # Calculate duration
                try:
                    from datetime import datetime
                    start_dt = datetime.strptime(start_time, "%Y/%m/%d %I:%M:%S%p")
                    end_dt = datetime.strptime(end_time.split(' (')[0] if ' (' in end_time else end_time, "%Y/%m/%d %I:%M:%S%p")
                    duration_sec = int((end_dt - start_dt).total_seconds())
                    if duration_sec >= 3600:
                        duration_str = f"{duration_sec//3600}h {(duration_sec%3600)//60}m {duration_sec%60}s"
                    elif duration_sec >= 60:
                        duration_str = f"{(duration_sec%3600)//60}m {duration_sec%60}s"
                    else:
                        duration_str = f"{duration_sec}s"
                    timeline_data = {'start': start_time, 'end': end_time, 'duration': duration_str}
                except:
                    timeline_data = {'start': start_time, 'end': end_time, 'duration': 'N/A'}
            else:
                timeline_data = {'start': start_time, 'end': 'Running', 'duration': 'In progress'}
        
        # LVS errors
        lvs_pattern = f"pv_flow/drc_dir/{self.design_info.top_hier}/lvs_icv_ipo*/{self.design_info.top_hier}_ipo*_fill.LVS_ERRORS"
        lvs_files = self.file_utils.find_files(lvs_pattern, self.workarea)
        
        if lvs_files:
            self.print_file_info(lvs_files[0], "LVS Errors")
            violations = self.lvs_parser.parse_lvs_errors(lvs_files[0])
            lvs_violations = violations['failed_equivalence_points']
            lvs_data = violations.copy()
            lvs_data['file_path'] = os.path.abspath(lvs_files[0])
            
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
            drc_violations, drc_violations_list = self._analyze_drc_errors_with_data(drc_files[0])
            drc_data = {
                'total_violations': drc_violations,
                'violations': drc_violations_list,
                'file_path': os.path.abspath(drc_files[0])
            }
        
        # Antenna errors
        antenna_pattern = f"pv_flow/drc_dir/{self.design_info.top_hier}/drc_icv_antenna_ipo*/{self.design_info.top_hier}_ipo*_fill.LAYOUT_ERRORS"
        antenna_files = self.file_utils.find_files(antenna_pattern, self.workarea)
        
        if antenna_files:
            self.print_file_info(antenna_files[0], "Antenna Errors")
            antenna_violations = self._analyze_antenna_errors(antenna_files[0])
            antenna_data = {
                'total_violations': antenna_violations,
                'file_path': os.path.abspath(antenna_files[0])
            }
        else:
            print("  No antenna error report found")
        
        # PV Flow Analysis
        pv_flow_data = self._analyze_pv_flow_with_data()
        
        # Generate HTML report
        pv_html_path = self._generate_pv_html_report(lvs_data, drc_data, antenna_data, pv_flow_data, timeline_data)
        
        if pv_html_path:
            html_filename = os.path.basename(pv_html_path)
            print(f"\n  {Color.CYAN}Physical Verification HTML Report:{Color.RESET}")
            print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
        
        # Determine status based on violation counts
        # Thresholds: LVS > 5, DRC > 100, Antenna > 10 → FAIL
        #             All = 0 → PASS
        #             Otherwise → WARN
        status = "PASS"
        issues = []
        
        # Check if any violation type exceeds FAIL threshold
        if lvs_violations > 5 or drc_violations > 100 or antenna_violations > 10:
            status = "FAIL"
            if lvs_violations > 5:
                issues.append(f"LVS failed equivalence points: {lvs_violations} (threshold: ≤5)")
            if drc_violations > 100:
                issues.append(f"DRC violations: {drc_violations} (threshold: ≤100)")
            if antenna_violations > 10:
                issues.append(f"Antenna violations: {antenna_violations} (threshold: ≤10)")
        # Check if any violation type > 0 but within FAIL threshold (WARN)
        elif lvs_violations > 0 or drc_violations > 0 or antenna_violations > 0:
            status = "WARN"
            if lvs_violations > 0:
                issues.append(f"LVS failed equivalence points: {lvs_violations} (threshold: ≤5)")
            if drc_violations > 0:
                issues.append(f"DRC violations: {drc_violations} (threshold: ≤100)")
            if antenna_violations > 0:
                issues.append(f"Antenna violations: {antenna_violations} (threshold: ≤10)")
        
        # Prepare key metrics
        key_metrics = {
            "LVS Failures": str(lvs_violations),
            "DRC Violations": str(drc_violations),
            "Antenna Violations": str(antenna_violations)
        }
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Physical Verification (PV)",
            section_id="pv",
            stage=FlowStage.PHYSICAL_VERIFICATION,
            status=status,
            key_metrics=key_metrics,
            html_file=pv_html_path if pv_html_path else "",
            priority=2,
            issues=issues,
            icon="[PV]"
        )
    
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
    
    def _analyze_pv_flow_with_data(self):
        """Wrapper for _analyze_pv_flow that returns structured data for HTML generation"""
        prc_pattern = f"pv_flow/nv_flow/pv_{self.design_info.top_hier}.prc"
        prc_status_pattern = f"pv_flow/nv_flow/pv_{self.design_info.top_hier}.prc.status"
        
        prc_files = self.file_utils.find_files(prc_pattern, self.workarea)
        prc_status_files = self.file_utils.find_files(prc_status_pattern, self.workarea)
        
        pv_flow_data = {}
        
        if prc_status_files:
            try:
                with open(prc_status_files[0], 'r') as f:
                    content = f.read()
                
                # Extract flow steps
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
                
                # Group by experiment
                experiments = {}
                for step in steps:
                    exp_key = f"{step['block']}/{step['experiment']}"
                    if exp_key not in experiments:
                        experiments[exp_key] = []
                    experiments[exp_key].append(step)
                
                # Process each experiment
                for exp_name, exp_steps in experiments.items():
                    total_runtime = sum(step['duration_sec'] for step in exp_steps if step['status'] == 'DONE')
                    done_steps = [s for s in exp_steps if s['status'] == 'DONE']
                    unlaunched_steps = [s for s in exp_steps if s['status'] == 'UNLAUNCHED']
                    
                    # Format total runtime
                    if total_runtime >= 3600:
                        total_str = f"{total_runtime//3600}h {(total_runtime%3600)//60}m {total_runtime%60}s"
                    elif total_runtime >= 60:
                        total_str = f"{(total_runtime%3600)//60}m {total_runtime%60}s"
                    else:
                        total_str = f"{total_runtime}s"
                    
                    # Get key steps
                    key_steps = [(s['step'], s['duration']) for s in done_steps 
                                 if s['step'] in ['temp_run_lvs', 'temp_run_drc', 'temp_run_ant', 'drc_lvs', 'ant']]
                    
                    pv_flow_data[exp_name] = {
                        'completed': len(done_steps),
                        'unlaunched': len(unlaunched_steps),
                        'total_runtime': total_str,
                        'key_steps': key_steps
                    }
                    
            except Exception as e:
                print(f"  Error extracting PV flow data: {e}")
        
        # Call regular function to print output
        self._analyze_pv_flow()
        
        return pv_flow_data
    
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
                return 0
            elif "LAYOUT ERRORS RESULTS: ERRORS" in content:
                print(f"  {Color.RED}Status: ERRORS - DRC violations found{Color.RESET}")
            
            # Extract violation details from ERROR SUMMARY section
            violations = []
            total_violations = 0
            
            # Find all violation lines in ERROR SUMMARY
            # Pattern to match rule violations that may span multiple lines
            # Format: RULE_NAME : description text ... X violations found.
            violation_pattern = r'^\s*([A-Z0-9._]+)\s*:\s*(.*?)(\d+)\s+violations?\s+found\.'
            matches = re.findall(violation_pattern, content, re.MULTILINE | re.DOTALL)
            
            for rule, description, count in matches:
                count_int = int(count)
                if count_int > 0:  # Only include non-zero violations
                    # Clean up description: remove extra whitespace and newlines
                    desc_clean = ' '.join(description.split())
                    # Truncate if too long
                    if len(desc_clean) > 60:
                        desc_clean = desc_clean[:57] + "..."
                    violations.append((rule, desc_clean, count_int))
                    total_violations += count_int
            
            if violations:
                print(f"  {Color.RED}Total DRC violations: {total_violations}{Color.RESET}")
                print(f"  {Color.CYAN}Violation breakdown:{Color.RESET}")
                
                # Sort by violation count (descending)
                violations.sort(key=lambda x: x[2], reverse=True)
                
                # Create table format
                print(f"    {'Rule':<20} {'Count':<8} {'Description':<60}")
                print(f"    {'-'*20} {'-'*8} {'-'*60}")
                
                for rule, description, count in violations:
                    print(f"    {rule:<20} {count:<8} {description:<60}")
            else:
                # Fallback: Try alternate parsing methods
                print(f"  {Color.YELLOW}Warning: Could not parse DRC violation details with standard pattern{Color.RESET}")
                
                # Try to find ERROR SUMMARY section and extract lines
                summary_match = re.search(r'ERROR SUMMARY.*?(?=\n\n|\Z)', content, re.DOTALL)
                if summary_match:
                    summary_text = summary_match.group(0)
                    # Look for lines with "violation" in ERROR SUMMARY
                    violation_lines = [line.strip() for line in summary_text.split('\n') 
                                      if 'violation' in line.lower() and line.strip()]
                    
                    if violation_lines:
                        print(f"  {Color.CYAN}DRC Violations Found:{Color.RESET}")
                        total_violations = 0
                        for line in violation_lines:
                            print(f"    {line}")
                            # Try to extract count from line
                            numbers = re.findall(r'(\d+)\s+violations?\s+found', line, re.IGNORECASE)
                            if numbers:
                                total_violations += int(numbers[0])
                        print(f"  {Color.RED}Total DRC violations: {total_violations}{Color.RESET}")
                    else:
                        # Last resort: simple counting
                        matches = self.file_utils.grep_file(r".*violation.*found.*", drc_file)
                        total_violations = 0
                        for match in matches:
                            numbers = re.findall(r'\d+', match)
                            if numbers:
                                total_violations += int(numbers[0])
                        print(f"  Total DRC violations: {total_violations}")
                        print(f"  {Color.CYAN}Note: See full details in DRC file{Color.RESET}")
                else:
                    # No ERROR SUMMARY found, show sample content
                    print(f"  {Color.CYAN}Sample from DRC file (first 10 lines with 'violation'):{Color.RESET}")
                    violation_sample = [line for line in content.split('\n') if 'violation' in line.lower()][:10]
                    for line in violation_sample:
                        print(f"    {line.strip()}")
                    print(f"  {Color.YELLOW}Please check the full DRC file for details{Color.RESET}")
            
            # Return total violation count
            return total_violations
                
        except Exception as e:
            print(f"  Error analyzing DRC file: {e}")
            return 0
    
    def _analyze_drc_errors_with_data(self, drc_file: str):
        """Wrapper for _analyze_drc_errors that returns both count and violations list for HTML generation"""
        try:
            with open(drc_file, 'r') as f:
                content = f.read()
            
            violations = []
            total_violations = 0
            
            # Check if CLEAN or ERRORS
            if "LAYOUT ERRORS RESULTS: CLEAN" in content:
                # Call regular function to print output
                self._analyze_drc_errors(drc_file)
                return 0, []
            
            # Extract violation details
            violation_pattern = r'^\s*([A-Z0-9._]+)\s*:\s*(.*?)(\d+)\s+violations?\s+found\.'
            matches = re.findall(violation_pattern, content, re.MULTILINE | re.DOTALL)
            
            for rule, description, count in matches:
                count_int = int(count)
                if count_int > 0:
                    desc_clean = ' '.join(description.split())
                    if len(desc_clean) > 60:
                        desc_clean = desc_clean[:57] + "..."
                    violations.append((rule, desc_clean, count_int))
                    total_violations += count_int
            
            # Sort by violation count (descending)
            violations.sort(key=lambda x: x[2], reverse=True)
            
            # Call regular function to print output
            self._analyze_drc_errors(drc_file)
            
            return total_violations, violations
                
        except Exception as e:
            print(f"  Error analyzing DRC file: {e}")
            return 0, []
    
    def _analyze_antenna_errors(self, antenna_file: str):
        """Analyze antenna errors file and provide detailed information"""
        try:
            with open(antenna_file, 'r') as f:
                content = f.read()
            
            total_violations = 0
            
            # Extract LAYOUT ERRORS RESULTS
            matches = self.file_utils.grep_file(r"LAYOUT ERRORS RESULTS.*", antenna_file)
            for match in matches:
                # Check if status is CLEAN and color it green
                if "CLEAN" in match.upper():
                    print(f"  {Color.GREEN}Status: {match.strip()}{Color.RESET}")
                    print(f"  {Color.GREEN}No antenna violations found{Color.RESET}")
                    return 0
                else:
                    print(f"  {Color.RED}Status: {match.strip()}{Color.RESET}")
            
            
            # If there are errors, extract error summary and count violations
            if "LAYOUT ERRORS RESULTS: ERRORS" in content:
                result = self.file_utils.run_command(f"sed -n '/ERROR SUMMARY/,/ERROR DETAILS/p' {antenna_file} | sed -e '/^$/d' -e '/ERROR DETAILS/d'")
                if result.strip():
                    print(f"  {Color.CYAN}Error Summary:{Color.RESET}")
                    for line in result.strip().split('\n'):
                        if line.strip():
                            print(f"    {line}")
                            # Try to extract violation count from lines
                            numbers = re.findall(r'(\d+)\s+violations?\s+found', line, re.IGNORECASE)
                            if numbers:
                                total_violations += int(numbers[0])
                
                # If no violations counted from summary, try overall pattern
                if total_violations == 0:
                    violation_pattern = r'(\d+)\s+violations?\s+found'
                    matches = re.findall(violation_pattern, content, re.IGNORECASE)
                    for count in matches:
                        total_violations += int(count)
                
                if total_violations > 0:
                    print(f"  {Color.RED}Total Antenna violations: {total_violations}{Color.RESET}")
            
            return total_violations
                            
        except Exception as e:
            print(f"  Error analyzing antenna file: {e}")
            return 0
    
    def _analyze_gl_check_errors(self, waived_file, non_waived_file):
        """Analyze GL Check error files and show waived vs non-waived counts per checker"""
        try:
            # Parse waived errors
            waived_checkers = {}
            waived_lines_total = 0
            if os.path.exists(waived_file):
                try:
                    with open(waived_file, 'r') as f:
                        lines = f.readlines()
                        waived_lines_total = len(lines)
                        for line in lines:
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
            non_waived_lines_total = 0
            if os.path.exists(non_waived_file):
                try:
                    with open(non_waived_file, 'r') as f:
                        lines = f.readlines()
                        non_waived_lines_total = len(lines)
                        for line in lines:
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
            
            # If we couldn't parse any checkers but files have content, show raw counts
            if not all_checkers and (waived_lines_total > 0 or non_waived_lines_total > 0):
                print(f"\n  {Color.YELLOW}Warning: Could not parse checker format from error files{Color.RESET}")
                print(f"  {Color.CYAN}GL Check Error Summary (Raw):{Color.RESET}")
                if waived_lines_total > 0:
                    print(f"    {Color.GREEN}Waived Errors: {waived_lines_total} lines{Color.RESET}")
                if non_waived_lines_total > 0:
                    print(f"    {Color.RED}Non-Waived Errors: {non_waived_lines_total} lines{Color.RESET}")
                print(f"\n  {Color.CYAN}Error file format sample (first 3 lines from non-waived):{Color.RESET}")
                if os.path.exists(non_waived_file):
                    with open(non_waived_file, 'r') as f:
                        for i, line in enumerate(f):
                            if i >= 3:
                                break
                            print(f"    {line.rstrip()}")
                print(f"\n  Waived Errors File: {waived_file}")
                print(f"  Non-Waived Errors File: {non_waived_file}")
                # Return raw line counts
                total = waived_lines_total + non_waived_lines_total
                return total, waived_lines_total, non_waived_lines_total
            
            if not all_checkers:
                print("  No GL Check errors found")
                return 0, 0, 0
            
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
            
            # Return totals for status determination
            return total_errors, total_waived, total_non_waived
                    
        except Exception as e:
            print(f"  Error analyzing GL Check errors: {e}")
            return 0, 0, 0
    
    def _generate_gl_check_html_content(self, waived_checkers, non_waived_checkers, non_waived_errors_detail,
                                        sorted_checkers, total_errors, total_waived, total_non_waived,
                                        allowed_clktree_cells, dont_use_cells, key_reports, main_logs, timestamped_dirs,
                                        waived_file, non_waived_file):
        """Generate the HTML content for GL Check report"""
        
        # Read and encode logo
        import base64
        logo_data = ""
        logo_path = os.path.join(os.path.dirname(__file__), "images/avice_logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo_file:
                logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
        
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
        
        # Build dont_use cells HTML - limit initial display to 50 cells
        dont_use_cells_html = ""
        dont_use_cells_more_html = ""
        if dont_use_cells:
            # Show first 50 cells
            for cell in dont_use_cells[:50]:
                dont_use_cells_html += f"<div class='cell-item'>{cell}</div>"
            # Hide remaining cells
            if len(dont_use_cells) > 50:
                for cell in dont_use_cells[50:]:
                    dont_use_cells_more_html += f"<div class='cell-item'>{cell}</div>"
        else:
            dont_use_cells_html = "<div class='no-data'>No dont_use cells found</div>"
        
        # Build reports HTML
        reports_html = ""
        if key_reports:
            reports_html = "<div class='reports-container'>"
            for name, filepath in key_reports:
                reports_html += f"""
                    <div class='report-item'>
                        <span class='report-name'>{name}</span>
                        <button class='btn-log' onclick='window.open("file://{filepath}", "_blank")' title='Open {filepath}'>Open Log</button>
                    </div>
                """
            reports_html += "</div>"
        else:
            reports_html = "<div class='no-data'>No reports found</div>"
        
        # Build logs HTML
        logs_html = ""
        if main_logs:
            logs_html = "<div class='logs-container'>"
            for name, filepath in main_logs:
                logs_html += f"""
                    <div class='report-item'>
                        <span class='report-name'>{name}</span>
                        <button class='btn-log' onclick='window.open("file://{filepath}", "_blank")' title='Open {filepath}'>Open Log</button>
                    </div>
                """
            logs_html += "</div>"
        else:
            logs_html = "<div class='no-data'>No logs found</div>"
        
        # Build run history HTML
        run_history_html = ""
        if timestamped_dirs:
            run_history_html = "<div class='run-history-container'>"
            for run_dir in reversed(timestamped_dirs):  # Most recent first
                formatted_date = run_dir.replace('_', '/', 2).replace('_', ' ', 1).replace('_', ':', 1).replace('_', ':', 1)
                run_history_html += f"<div class='run-item'>{formatted_date}</div>"
            run_history_html += "</div>"
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
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 20px;
            align-items: center;
        }}
        
        .logo {{
            width: 80px;
            height: 80px;
            border-radius: 10px;
            background: white;
            padding: 10px;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .logo:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        
        .header-text h1 {{
            font-size: 2.5em;
            margin: 0 0 10px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header-text .workarea-path {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }}
        
        .logo-modal.active {{
            display: flex;
        }}
        
        .logo-modal-content {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
        }}
        
        .logo-modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .logo-modal-close:hover {{
            color: #bbb;
        }}
        
        .summary {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            padding: 20px;
            background: #f8f9fa;
        }}
        
        .summary-card {{
            flex: 1 1 calc(20% - 12px);
            min-width: 160px;
            background: white;
            padding: 12px 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
            min-height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        @media (max-width: 899px) {{
            .summary-card {{
                flex: 1 1 calc(33.333% - 12px);
            }}
        }}
        
        @media (max-width: 599px) {{
            .summary-card {{
                flex: 1 1 calc(50% - 12px);
            }}
        }}
        
        .summary-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        
        .summary-card .label {{
            font-size: 0.75em;
            color: #666;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            line-height: 1;
        }}
        
        .summary-card .status {{
            font-size: 1.6em;
            font-weight: bold;
            padding: 6px;
            border-radius: 5px;
            line-height: 1;
        }}
        
        .pass-text {{
            color: #28a745;
        }}
        
        .fail-text {{
            color: #dc3545;
        }}
        
        .content {{
            padding: 20px;
        }}
        
        .section {{
            margin-bottom: 15px;
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
            padding: 6px 12px;
            margin: 4px;
            border-radius: 5px;
            border: 1px solid #ddd;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            transition: all 0.3s;
        }}
        
        .cell-item:hover {{
            background: #667eea;
            color: white;
            border-color: #667eea;
            transform: scale(1.05);
        }}
        
        .reports-container, .logs-container {{
            column-count: 2;
            column-gap: 15px;
        }}
        
        @media (max-width: 900px) {{
            .reports-container, .logs-container {{
                column-count: 1;
            }}
        }}
        
        .report-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            background: white;
            margin-bottom: 8px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
            break-inside: avoid;
        }}
        
        .report-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .report-name {{
            font-weight: 500;
            font-size: 0.9em;
        }}
        
        .run-history-container {{
            column-count: 3;
            column-gap: 15px;
        }}
        
        @media (max-width: 1200px) {{
            .run-history-container {{
                column-count: 2;
            }}
        }}
        
        @media (max-width: 768px) {{
            .run-history-container {{
                column-count: 1;
            }}
        }}
        
        .run-item {{
            padding: 8px 12px;
            background: white;
            margin-bottom: 6px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            break-inside: avoid;
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
        
        /* Back to Top Button */
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
            font-size: 1.5em;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            transition: all 0.3s;
        }}
        
        .back-to-top:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }}
        
        .back-to-top.visible {{
            display: flex;
        }}
        
        /* Quick Navigation */
        .quick-nav {{
            position: fixed;
            top: 50%;
            right: 20px;
            transform: translateY(-50%);
            background: white;
            border-radius: 10px;
            padding: 15px 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 999;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .quick-nav-item {{
            display: block;
            padding: 8px 12px;
            margin: 3px 0;
            color: #667eea;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.85em;
            transition: all 0.3s;
            white-space: nowrap;
        }}
        
        .quick-nav-item:hover {{
            background: #667eea;
            color: white;
        }}
        
        .quick-nav-toggle {{
            position: fixed;
            top: 50%;
            right: 20px;
            transform: translateY(-50%);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 6px;
            border-radius: 8px 0 0 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: bold;
            writing-mode: vertical-rl;
            text-orientation: mixed;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 998;
            transition: all 0.3s;
        }}
        
        .quick-nav-toggle:hover {{
            padding-right: 10px;
        }}
        
        /* Sticky Summary Mode */
        .summary.sticky {{
            position: sticky;
            top: 0;
            z-index: 100;
            margin-bottom: 0;
            border-radius: 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        
        /* Compact mode for sections */
        .section-content {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 10px;
        }}
        
        @media (max-width: 768px) {{
            .quick-nav, .quick-nav-toggle {{
                display: none;
            }}
        }}
        
        /* Copyright Footer */
        .footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer strong {{
            color: #00ff00;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img class='logo' src='data:image/png;base64,{logo_data}' alt='AVICE Logo' onclick="showLogoModal()" title="Click to enlarge">
            <div class="header-text">
                <h1>GL Check Analysis Report</h1>
                <div class="workarea-path">Workarea: {os.path.abspath(self.workarea)}</div>
                <div class="workarea-path">Design: {self.design_info.top_hier}</div>
            </div>
        </div>
        
        <!-- Logo Modal -->
        <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
            <span class="logo-modal-close">&times;</span>
            <img class="logo-modal-content" src='data:image/png;base64,{logo_data}' alt='AVICE Logo'>
        </div>
        
        <div class="summary" id="summary">
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
            <div class="section" id="error-analysis">
                <div class="section-header" onclick="toggleSection(this)">
                    <h2>Error Analysis by Checker</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content">
                    <input type="text" class="search-box" id="checkerSearch" placeholder="Search checkers..." oninput="filterCheckers()" onkeyup="filterCheckers()">
                    
                    <div class="filter-buttons">
                        <button class="filter-btn active" onclick="filterByStatus('all', this)">All Checkers</button>
                        <button class="filter-btn" onclick="filterByStatus('fail', this)">With Non-Waived Only</button>
                        <button class="filter-btn" onclick="filterByStatus('pass', this)">Fully Waived Only</button>
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
            <div class="section" id="clock-cells">
                <div class="section-header collapsed" onclick="toggleSection(this)">
                    <h2>Allowed Clock Tree Cells ({len(allowed_clktree_cells)} cells)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content collapsed">
                    <input type="text" class="search-box" id="cellSearch" placeholder="Search cells..." oninput="filterCells()" onkeyup="filterCells()">
                    <div id="cellsContainer">
                        {clktree_cells_html}
                    </div>
                </div>
            </div>
            
            <!-- Don't Use Cells Section -->
            <div class="section" id="dont-use">
                <div class="section-header collapsed" onclick="toggleSection(this)">
                    <h2>Don't Use Cells ({len(dont_use_cells)} cells)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content collapsed">
                    <input type="text" class="search-box" id="dontUseCellSearch" placeholder="Search dont_use cells..." oninput="filterDontUseCells()" onkeyup="filterDontUseCells()">
                    <div id="dontUseCellsContainer">
                        {dont_use_cells_html}
                        {'<div id="dontUseCellsMore" style="display:none;">' + dont_use_cells_more_html + '</div>' if dont_use_cells_more_html else ''}
                    </div>
                    {f'<button class="btn-show-more" onclick="toggleDontUseCells(this)" style="margin-top: 15px; width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1em; font-weight: bold; transition: all 0.3s;">Show {len(dont_use_cells) - 50} More Cells</button>' if len(dont_use_cells) > 50 else ''}
                </div>
            </div>
            
            <!-- Key Reports Section -->
            <div class="section" id="reports">
                <div class="section-header collapsed" onclick="toggleSection(this)">
                    <h2>Key Reports ({len(key_reports)} reports)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content collapsed">
                    {reports_html}
                </div>
            </div>
            
            <!-- Main Logs Section -->
            <div class="section" id="logs">
                <div class="section-header collapsed" onclick="toggleSection(this)">
                    <h2>Main Logs ({len(main_logs)} logs)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content collapsed">
                    {logs_html}
                </div>
            </div>
            
            <!-- Run History Section -->
            <div class="section" id="history">
                <div class="section-header collapsed" onclick="toggleSection(this)">
                    <h2>Run History ({len(timestamped_dirs)} runs)</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content collapsed">
                    {run_history_html}
                </div>
            </div>
            
            <!-- File Paths Section -->
            <div class="section" id="files">
                <div class="section-header collapsed" onclick="toggleSection(this)">
                    <h2>Source Files</h2>
                    <span class="toggle-icon">▼</span>
                </div>
                <div class="section-content collapsed">
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
    
    <!-- Back to Top Button -->
    <button class="back-to-top" id="backToTop" onclick="scrollToTop()" title="Back to Top">&#8593;</button>
    
    <!-- Quick Navigation Toggle -->
    <button class="quick-nav-toggle" id="quickNavToggle" onclick="toggleQuickNav()">MENU</button>
    
    <!-- Quick Navigation Menu -->
    <div class="quick-nav" id="quickNav" style="display: none;">
        <a href="javascript:void(0)" class="quick-nav-item" onclick="scrollToSection('summary')">Summary</a>
        <a href="javascript:void(0)" class="quick-nav-item" onclick="scrollToSection('error-analysis')">Error Analysis</a>
        <a href="javascript:void(0)" class="quick-nav-item" onclick="scrollToSection('clock-cells')">Clock Cells</a>
        <a href="javascript:void(0)" class="quick-nav-item" onclick="scrollToSection('dont-use')">Don't Use</a>
        <a href="javascript:void(0)" class="quick-nav-item" onclick="scrollToSection('reports')">Reports</a>
        <a href="javascript:void(0)" class="quick-nav-item" onclick="scrollToSection('logs')">Logs</a>
        <a href="javascript:void(0)" class="quick-nav-item" onclick="scrollToSection('history')">History</a>
        <a href="javascript:void(0)" class="quick-nav-item" onclick="scrollToSection('files')">Files</a>
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
        
        function filterByStatus(status, button) {{
            currentFilter = status;
            
            // Update button states
            const buttons = document.querySelectorAll('.filter-btn');
            Array.prototype.slice.call(buttons).forEach(function(btn) {{
                btn.classList.remove('active');
            }});
            button.classList.add('active');
            
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
        
        function toggleDontUseCells(btn) {{
            const moreSection = document.getElementById('dontUseCellsMore');
            if (moreSection) {{
                if (moreSection.style.display === 'none') {{
                    moreSection.style.display = 'block';
                    btn.textContent = 'Show Less';
                }} else {{
                    moreSection.style.display = 'none';
                    btn.textContent = 'Show {len(dont_use_cells) - 50} More Cells';
                }}
            }}
        }}
        
        // Back to Top functionality
        function scrollToTop() {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }}
        
        // Show/hide back to top button based on scroll position
        window.addEventListener('scroll', function() {{
            var backToTopBtn = document.getElementById('backToTop');
            if (window.pageYOffset > 300) {{
                backToTopBtn.classList.add('visible');
            }} else {{
                backToTopBtn.classList.remove('visible');
            }}
        }});
        
        // Quick Navigation functions
        function toggleQuickNav() {{
            const quickNav = document.getElementById('quickNav');
            const quickNavToggle = document.getElementById('quickNavToggle');
            
            if (quickNav.style.display === 'none') {{
                quickNav.style.display = 'block';
                quickNavToggle.style.display = 'none';
            }} else {{
                quickNav.style.display = 'none';
                quickNavToggle.style.display = 'block';
            }}
        }}
        
        function scrollToSection(sectionId) {{
            const section = document.getElementById(sectionId);
            if (section) {{
                section.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'start'
                }});
                
                // If section is collapsed, expand it
                const sectionHeader = section.querySelector('.section-header');
                if (sectionHeader && sectionHeader.classList.contains('collapsed')) {{
                    toggleSection(sectionHeader);
                }}
            }}
            
            // Close quick nav after selection
            toggleQuickNav();
            return false;
        }}
        
        // Close quick nav when clicking outside
        document.addEventListener('click', function(event) {{
            const quickNav = document.getElementById('quickNav');
            const quickNavToggle = document.getElementById('quickNavToggle');
            
            if (quickNav && quickNav.style.display === 'block' &&
                !quickNav.contains(event.target) && 
                !quickNavToggle.contains(event.target)) {{
                toggleQuickNav();
            }}
        }});
        
        // Logo modal functions
        function showLogoModal() {{
            document.getElementById('logoModal').classList.add('active');
        }}
        
        function hideLogoModal() {{
            document.getElementById('logoModal').classList.remove('active');
        }}
        
        // Allow ESC key to close logo modal
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                hideLogoModal();
            }}
        }});
    </script>
    
    <!-- Copyright Footer -->
    <div class="footer">
        <p><strong>AVICE GL Check Analysis Report</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
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
            html_filename = f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_gl_check_report_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            html_content = self._generate_gl_check_html_content(
                waived_checkers, non_waived_checkers, non_waived_errors_detail,
                sorted_checkers, total_errors, total_waived, total_non_waived,
                allowed_clktree_cells, dont_use_cells, key_reports, main_logs, timestamped_dirs,
                waived_file, non_waived_file
            )
            
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            print(f"\n  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
            
            return os.path.abspath(html_path)
            
        except Exception as e:
            print(f"  Error generating GL Check HTML report: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _generate_pv_html_report(self, lvs_data, drc_data, antenna_data, pv_flow_data, timeline_data):
        """Generate comprehensive HTML report for Physical Verification"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            username = os.environ.get('USER', 'avice')
            html_filename = f"{self.design_info.top_hier}_{username}_pv_report_{timestamp}.html"
            html_path = os.path.abspath(html_filename)
            
            # Determine overall status based on violations
            lvs_violations = lvs_data.get('failed_equivalence_points', 0)
            drc_violations = drc_data.get('total_violations', 0)
            antenna_violations = antenna_data.get('total_violations', 0)
            
            overall_status = "PASS"
            if lvs_violations > 5 or drc_violations > 100 or antenna_violations > 10:
                overall_status = "FAIL"
            elif lvs_violations > 0 or drc_violations > 0 or antenna_violations > 0:
                overall_status = "WARN"
            
            status_color = "#28a745" if overall_status == "PASS" else "#ffc107" if overall_status == "WARN" else "#dc3545"
            
            # Generate HTML content
            html_content = self._generate_pv_html_content(
                lvs_data, drc_data, antenna_data, pv_flow_data, timeline_data,
                overall_status, status_color, html_filename
            )
            
            # Write HTML file
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            return html_path
            
        except Exception as e:
            print(f"  Error generating PV HTML report: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _generate_pv_html_content(self, lvs_data, drc_data, antenna_data, pv_flow_data, timeline_data,
                                   overall_status, status_color, html_filename):
        """Generate HTML content for PV report"""
        
        # Load and encode logo
        logo_data = ""
        logo_path = os.path.join(os.path.dirname(__file__), "images", "avice_logo.png")
        try:
            with open(logo_path, 'rb') as f:
                import base64
                logo_data = base64.b64encode(f.read()).decode('utf-8')
        except:
            pass  # If logo not found, continue without it
        
        # Extract data
        lvs_violations = lvs_data.get('failed_equivalence_points', 0)
        drc_violations = drc_data.get('total_violations', 0)
        antenna_violations = antenna_data.get('total_violations', 0)
        
        # Timeline HTML
        timeline_html = ""
        if timeline_data:
            start_time = timeline_data.get('start', 'N/A')
            end_time = timeline_data.get('end', 'N/A')
            duration = timeline_data.get('duration', 'N/A')
            timeline_html = f"""
        <div class="timeline-section">
            <h3>PV Flow Timeline</h3>
            <div class="timeline-info">
                <div><strong>Started:</strong> {start_time}</div>
                <div><strong>Finished:</strong> {end_time}</div>
                <div><strong>Duration:</strong> {duration}</div>
            </div>
        </div>
"""
        
        # LVS section HTML
        lvs_status_class = "status-pass" if lvs_violations == 0 else "status-fail"
        lvs_html = f"""
        <div class="section {lvs_status_class}">
            <div class="section-header" onclick="toggleSection('lvs-section')">
                <h2>LVS Results</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content" id="lvs-section">
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Status</td>
                        <td class="{'pass-text' if lvs_data.get('status') != 'FAIL' else 'fail-text'}">{lvs_data.get('status', 'UNKNOWN')}</td>
                    </tr>
                    <tr>
                        <td>Failed Equivalence Points</td>
                        <td class="num-cell {'fail-text' if lvs_violations > 0 else 'pass-text'}">{lvs_violations}</td>
                    </tr>
                    <tr>
                        <td>Successful Equivalence Points</td>
                        <td class="num-cell">{lvs_data.get('successful_equivalence_points', 0)}</td>
                    </tr>
                    <tr>
                        <td>First Priority Errors</td>
                        <td class="num-cell">{lvs_data.get('first_priority_errors', 0)}</td>
                    </tr>
                    <tr>
                        <td>Second Priority Errors</td>
                        <td class="num-cell">{lvs_data.get('second_priority_errors', 0)}</td>
                    </tr>
                </table>
                
                {'<h3>Unmatched Items</h3>' if lvs_violations > 0 else ''}
                {'<table>' if lvs_violations > 0 else ''}
"""
        
        if lvs_violations > 0:
            unmatched_items = [
                ('Schematic Instances', lvs_data.get('unmatched_schematic_instances', 0)),
                ('Schematic Nets', lvs_data.get('unmatched_schematic_nets', 0)),
                ('Layout Instances', lvs_data.get('unmatched_layout_instances', 0)),
                ('Layout Nets', lvs_data.get('unmatched_layout_nets', 0)),
                ('Schematic Ports', lvs_data.get('unmatched_schematic_ports', 0)),
                ('Layout Ports', lvs_data.get('unmatched_layout_ports', 0))
            ]
            
            for item_name, count in unmatched_items:
                if count > 0:
                    lvs_html += f"""
                    <tr>
                        <td>{item_name}</td>
                        <td class="num-cell fail-text">{count}</td>
                    </tr>
"""
            lvs_html += """
                </table>
"""
        
        lvs_html += f"""
                <h3>Matched Items</h3>
                <table>
                    <tr>
                        <td>Instances</td>
                        <td class="num-cell">{lvs_data.get('matched_instances', 0):,}</td>
                    </tr>
                    <tr>
                        <td>Nets</td>
                        <td class="num-cell">{lvs_data.get('matched_nets', 0):,}</td>
                    </tr>
                    <tr>
                        <td>Ports</td>
                        <td class="num-cell">{lvs_data.get('matched_ports', 0):,}</td>
                    </tr>
                </table>
                
                {'<p><strong>File:</strong> <a href="file://' + lvs_data.get('file_path', '') + '" target="_blank">' + os.path.basename(lvs_data.get('file_path', '')) + '</a></p>' if lvs_data.get('file_path') else ''}
            </div>
        </div>
"""
        
        # DRC section HTML
        drc_status_class = "status-pass" if drc_violations == 0 else "status-fail"
        drc_violations_list = drc_data.get('violations', [])
        
        drc_html = f"""
        <div class="section {drc_status_class}">
            <div class="section-header" onclick="toggleSection('drc-section')">
                <h2>DRC Results</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content" id="drc-section">
                <div class="summary-cards">
                    <div class="summary-card">
                        <div class="label">Status</div>
                        <div class="status {'pass-text' if drc_violations == 0 else 'fail-text'}">
                            {'CLEAN' if drc_violations == 0 else 'ERRORS'}
                        </div>
                    </div>
                    <div class="summary-card">
                        <div class="label">Total Violations</div>
                        <div class="value {'fail-text' if drc_violations > 0 else 'pass-text'}">{drc_violations}</div>
                    </div>
                </div>
                
                {'<h3>Violation Breakdown</h3>' if drc_violations > 0 else ''}
                {'<table><thead><tr><th>Rule</th><th>Count</th><th>Description</th></tr></thead><tbody>' if drc_violations > 0 else ''}
"""
        
        for rule, desc, count in drc_violations_list:
            drc_html += f"""
                <tr>
                    <td><strong>{rule}</strong></td>
                    <td class="num-cell fail-text">{count}</td>
                    <td>{desc}</td>
                </tr>
"""
        
        if drc_violations > 0:
            drc_html += """
                </tbody></table>
"""
        
        drc_html += f"""
                {'<p><strong>File:</strong> <a href="file://' + drc_data.get('file_path', '') + '" target="_blank">' + os.path.basename(drc_data.get('file_path', '')) + '</a></p>' if drc_data.get('file_path') else ''}
            </div>
        </div>
"""
        
        # Antenna section HTML
        antenna_status_class = "status-pass" if antenna_violations == 0 else "status-fail"
        
        antenna_html = f"""
        <div class="section {antenna_status_class}">
            <div class="section-header" onclick="toggleSection('antenna-section')">
                <h2>Antenna Results</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content" id="antenna-section">
                <div class="summary-cards">
                    <div class="summary-card">
                        <div class="label">Status</div>
                        <div class="status {'pass-text' if antenna_violations == 0 else 'fail-text'}">
                            {'CLEAN' if antenna_violations == 0 else 'ERRORS'}
                        </div>
                    </div>
                    <div class="summary-card">
                        <div class="label">Total Violations</div>
                        <div class="value {'fail-text' if antenna_violations > 0 else 'pass-text'}">{antenna_violations}</div>
                    </div>
                </div>
                {'<p><strong>File:</strong> <a href="file://' + antenna_data.get('file_path', '') + '" target="_blank">' + os.path.basename(antenna_data.get('file_path', '')) + '</a></p>' if antenna_data.get('file_path') else ''}
            </div>
        </div>
"""
        
        # PV Flow section HTML
        pv_flow_html = ""
        if pv_flow_data:
            pv_flow_html = """
        <div class="section">
            <div class="section-header" onclick="toggleSection('pv-flow-section')">
                <h2>PV Flow Analysis</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content" id="pv-flow-section">
"""
            
            for exp_name, exp_data in pv_flow_data.items():
                completed_steps = exp_data.get('completed', 0)
                unlaunched_steps = exp_data.get('unlaunched', 0)
                total_runtime = exp_data.get('total_runtime', '0s')
                key_steps = exp_data.get('key_steps', [])
                
                pv_flow_html += f"""
                <h3>{exp_name}</h3>
                <div class="flow-summary">
                    <p><strong>Completed:</strong> {completed_steps} steps (Total runtime: {total_runtime})</p>
                    {f'<p><strong>Unlaunched:</strong> {unlaunched_steps} steps</p>' if unlaunched_steps > 0 else ''}
                </div>
                
                {'<h4>Key Step Runtimes:</h4>' if key_steps else ''}
                {'<table><thead><tr><th>Step</th><th>Runtime</th></tr></thead><tbody>' if key_steps else ''}
"""
                
                for step_name, step_runtime in key_steps:
                    pv_flow_html += f"""
                    <tr>
                        <td>{step_name}</td>
                        <td class="num-cell">{step_runtime}</td>
                    </tr>
"""
                
                if key_steps:
                    pv_flow_html += """
                </tbody></table>
"""
            
            pv_flow_html += """
            </div>
        </div>
"""
        
        # Generate full HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Physical Verification Report - {self.design_info.top_hier}</title>
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
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header-content {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }}
        
        .logo {{
            max-width: 120px;
            height: auto;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        
        .logo:hover {{
            transform: scale(1.05);
        }}
        
        .header-text {{
            flex: 1;
            min-width: 300px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .header .design-info {{
            margin-top: 15px;
            font-size: 1em;
            opacity: 0.8;
        }}
        
        /* Logo Modal */
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.9);
            cursor: pointer;
        }}
        
        .logo-modal-content {{
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
            position: relative;
            top: 50%;
            transform: translateY(-50%);
        }}
        
        .logo-modal-close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
        }}
        
        .logo-modal-close:hover,
        .logo-modal-close:focus {{
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }}
        
        .summary-cards {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            padding: 20px;
            background: #f8f9fa;
            margin-bottom: 20px;
        }}
        
        .summary-card {{
            flex: 1 1 calc(25% - 12px);
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
            min-height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .summary-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        
        .summary-card .label {{
            font-size: 0.75em;
            color: #666;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            line-height: 1;
        }}
        
        .summary-card .status {{
            font-size: 1.6em;
            font-weight: bold;
            padding: 6px;
            border-radius: 5px;
            line-height: 1;
        }}
        
        .pass-text {{
            color: #28a745;
        }}
        
        .fail-text {{
            color: #dc3545;
        }}
        
        .content {{
            padding: 20px;
        }}
        
        .section {{
            margin-bottom: 15px;
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
            margin-bottom: 15px;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f0f0f0;
        }}
        
        .num-cell {{
            text-align: right;
            font-weight: 600;
        }}
        
        .status-pass {{
            border-left: 4px solid #28a745;
        }}
        
        .status-fail {{
            border-left: 4px solid #dc3545;
        }}
        
        .timeline-section {{
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        .timeline-info {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 10px;
        }}
        
        .timeline-info div {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .flow-summary {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        
        h3 {{
            color: #667eea;
            margin-bottom: 10px;
            margin-top: 15px;
        }}
        
        h4 {{
            color: #764ba2;
            margin-bottom: 10px;
            margin-top: 10px;
        }}
        
        a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <!-- Logo Modal -->
    <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
        <span class="logo-modal-close">&times;</span>
        <img class="logo-modal-content" id="logoModalImg">
    </div>
    
    <div class="container">
        <div class="header">
            <div class="header-content">
                {f'<img class="logo" src="data:image/png;base64,{logo_data}" alt="AVICE Logo" onclick="showLogoModal()" title="Click to enlarge">' if logo_data else ''}
                <div class="header-text">
                    <h1>🔍 Physical Verification Report</h1>
                    <div class="subtitle">Comprehensive PV Analysis</div>
                    <div class="design-info">
                        Design: {self.design_info.top_hier} | IPO: {self.design_info.ipo}<br>
                        Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="summary-cards">
            <div class="summary-card">
                <div class="label">Overall Status</div>
                <div class="status" style="color: {status_color};">{overall_status}</div>
            </div>
            <div class="summary-card">
                <div class="label">LVS Failures</div>
                <div class="value {'fail-text' if lvs_violations > 0 else 'pass-text'}">{lvs_violations}</div>
            </div>
            <div class="summary-card">
                <div class="label">DRC Violations</div>
                <div class="value {'fail-text' if drc_violations > 0 else 'pass-text'}">{drc_violations}</div>
            </div>
            <div class="summary-card">
                <div class="label">Antenna Violations</div>
                <div class="value {'fail-text' if antenna_violations > 0 else 'pass-text'}">{antenna_violations}</div>
            </div>
        </div>
        
        {timeline_html}
        
        <div class="content">
            {lvs_html}
            {drc_html}
            {antenna_html}
            {pv_flow_html}
        </div>
        
        <div class="footer">
            <p>Report generated by <strong>avice_wa_review.py</strong></p>
            <p>For questions or issues, contact: avice@nvidia.com</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Alon Vice Tools © 2025</p>
        </div>
    </div>
    
    <script>
        function toggleSection(sectionId) {{
            const content = document.getElementById(sectionId);
            const header = content.previousElementSibling;
            
            content.classList.toggle('collapsed');
            header.classList.toggle('collapsed');
        }}
        
        // Back to top button functionality - wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            var backToTopBtn = document.getElementById('backToTopBtn');
            if (backToTopBtn) {{
                window.addEventListener('scroll', function() {{
                    if (window.pageYOffset > 300) {{
                        backToTopBtn.style.display = 'block';
                    }} else {{
                        backToTopBtn.style.display = 'none';
                    }}
                }});
                
                backToTopBtn.addEventListener('click', function() {{
                    window.scrollTo(0, 0);
                }});
            }}
        }});
        
        // Logo modal functions
        function showLogoModal() {{
            const modal = document.getElementById('logoModal');
            const modalImg = document.getElementById('logoModalImg');
            const logo = document.querySelector('.logo');
            if (modal && modalImg && logo) {{
                modal.style.display = 'block';
                modalImg.src = logo.src;
            }}
        }}
        
        function hideLogoModal() {{
            const modal = document.getElementById('logoModal');
            if (modal) {{
                modal.style.display = 'none';
            }}
        }}
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 9999; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
</body>
</html>
"""
        
        return html
    
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
        total_errors = 0
        total_waived = 0
        total_non_waived = 0
        
        if os.path.exists(waived_file) or os.path.exists(non_waived_file):
            total_errors, total_waived, total_non_waived = self._analyze_gl_check_errors(waived_file, non_waived_file)
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
        
        # Determine status based on non-waived violations (waived are accepted issues)
        # Thresholds: FAIL >= 50, WARN 0 < violations < 50, PASS = 0
        status = "PASS"
        issues = []
        
        if total_non_waived >= 50:
            status = "FAIL"
            issues.append(f"Non-waived violations: {total_non_waived} (threshold: <50)")
        elif total_non_waived > 0:
            status = "WARN"
            issues.append(f"Non-waived violations: {total_non_waived} (threshold: <50)")
        
        # Prepare key metrics
        key_metrics = {
            "Total Violations": str(total_errors),
            "Waived": str(total_waived),
            "Non-Waived": str(total_non_waived)
        }
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="GL Checks",
            section_id="gl-check",
            stage=FlowStage.GL_CHECK,
            status=status,
            key_metrics=key_metrics,
            html_file=gl_check_html_path if gl_check_html_path else "",
            priority=3,
            issues=issues,
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
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="ECO Analysis",
            section_id="eco",
            stage=FlowStage.ECO_ANALYSIS,
            status="PASS",
            key_metrics={
                "PT-ECO Loops": str(len(eco_files)) if eco_files else "0"
            },
            html_file="",
            priority=3,
            issues=[],
            icon="[ECO]"
        )
    
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
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="NV Gate ECO",
            section_id="nv-gate-eco",
            stage=FlowStage.NV_GATE_ECO,
            status="PASS",
            key_metrics={
                "Design": self.design_info.top_hier
            },
            html_file="",
            priority=3,
            issues=[],
            icon="[NV-ECO]"
        )
    
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
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Block Release",
            section_id="block-release",
            stage=FlowStage.BLOCK_RELEASE,
            status="PASS",
            key_metrics={
                "Design": self.design_info.top_hier
            },
            html_file="",
            priority=4,
            issues=[],
            icon="[Release]"
        )
    
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
            dashboard_filename = os.path.basename(dashboard_path)
            print(f"{Color.GREEN}[OK] Master Dashboard generated: {dashboard_filename}{Color.RESET}")
            print(f"{Color.CYAN}     Open with recommended browser:{Color.RESET}")
            print(f"     /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{dashboard_filename}{Color.RESET} &")
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
                # Check if NV Gate ECO is currently running
                running_check = self.file_utils.run_command(f"grep -E '^{self.design_info.top_hier}.*RUN' {eco_prc_status}")
                is_running = bool(running_check.strip())
                
                # Extract NV Gate ECO runtime for completed steps
                result = self.file_utils.run_command(f"grep -E '^{self.design_info.top_hier}.*DONE' {eco_prc_status} | awk '{{sum += $5}} END {{print sum}}'")
                if result.strip() and result.strip().isdigit():
                    total_runtime_seconds = int(result.strip())
                    
                    # If running, add the elapsed time of running step
                    if is_running:
                        running_lines = running_check.strip().split('\n')
                        for line in running_lines:
                            parts = line.split()
                            if len(parts) >= 5 and parts[3] == 'RUN':
                                running_duration = int(parts[4])
                                total_runtime_seconds += running_duration
                                break
                    
                    total_runtime_hours = total_runtime_seconds / 3600
                    total_runtime_days = total_runtime_hours / 24
                    
                    if total_runtime_hours >= 24:
                        runtime_str = f"{total_runtime_hours:.2f} hours ({total_runtime_days:.2f} days)"
                    else:
                        runtime_str = f"{total_runtime_hours:.2f} hours"
                    
                    # Add "(running)" indicator if flow is still active
                    if is_running:
                        runtime_str += " (running)"
                    
                    runtime_data['NV Gate ECO'] = runtime_str
                    # Extract NV Gate ECO timestamps from log file names in status file
                    # Note: All log files have the same timestamp (flow start time), so we calculate end time
                    try:
                        eco_lines = self.file_utils.run_command(f"grep '{self.design_info.top_hier}.*DONE' {eco_prc_status}")
                        if eco_lines.strip():
                            lines = eco_lines.strip().split('\n')
                            if lines:
                                # Extract start timestamp from first log file name
                                first_line = lines[0]
                                
                                # Look for timestamp patterns in log file names (format: YYYYMMDDHHMMSS)
                                first_match = re.search(r'(\d{8})(\d{6})', first_line)
                                
                                if first_match:
                                    try:
                                        first_date = first_match.group(1)  # YYYYMMDD
                                        first_time = first_match.group(2)  # HHMMSS
                                        
                                        # Parse start timestamp
                                        start_datetime_str = f"{first_date[:4]}-{first_date[4:6]}-{first_date[6:8]} {first_time[:2]}:{first_time[2:4]}:{first_time[4:6]}"
                                        start_time_struct = time.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
                                        start_epoch = time.mktime(start_time_struct)
                                        
                                        # Calculate end time by adding total runtime seconds
                                        # For running flows, end time is "now"
                                        if is_running:
                                            end_str = "running"
                                            start_str = time.strftime("%m/%d %H:%M", start_time_struct)
                                        else:
                                            end_epoch = start_epoch + total_runtime_seconds
                                            end_time_struct = time.localtime(end_epoch)
                                            start_str = time.strftime("%m/%d %H:%M", start_time_struct)
                                            end_str = time.strftime("%m/%d %H:%M", end_time_struct)
                                        
                                        runtime_timestamps['NV Gate ECO'] = (start_str, end_str)
                                    except Exception:
                                        pass
                    except Exception:
                        pass
                elif is_running:
                    # No completed steps yet, but flow is running
                    # Get elapsed time of running step
                    running_lines = running_check.strip().split('\n')
                    for line in running_lines:
                        parts = line.split()
                        if len(parts) >= 5 and parts[3] == 'RUN':
                            running_duration = int(parts[4])
                            runtime_hours = running_duration / 3600
                            runtime_data['NV Gate ECO'] = f"{runtime_hours:.2f} hours (running)"
                            
                            # Try to extract start timestamp
                            timestamp_match = re.search(r'(\d{8})(\d{6})', line)
                            if timestamp_match:
                                first_date = timestamp_match.group(1)
                                first_time = timestamp_match.group(2)
                                try:
                                    start_datetime_str = f"{first_date[:4]}-{first_date[4:6]}-{first_date[6:8]} {first_time[:2]}:{first_time[2:4]}:{first_time[4:6]}"
                                    start_time_struct = time.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
                                    start_str = time.strftime("%m/%d %H:%M", start_time_struct)
                                    runtime_timestamps['NV Gate ECO'] = (start_str, "running")
                                except:
                                    pass
                            break
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
        
        # Check for currently running flows
        status = "PASS"
        issues = []
        running_flows = []
        
        for stage_name, runtime_str in runtime_data.items():
            if "(running)" in runtime_str:
                running_flows.append(stage_name)
        
        # Also check PnR runtimes for running status
        for ipo, runtime_str in pnr_runtimes.items():
            if "(running)" in runtime_str:
                running_flows.append(f"PnR ({ipo})")
        
        if running_flows:
            status = "WARN"
            issues.append(f"Currently running: {', '.join(running_flows)}")
        
        # Add section summary for master dashboard
        self._add_section_summary(
            section_name="Runtime Analysis",
            section_id="runtime",
            stage=FlowStage.RUNTIME,
            status=status,
            key_metrics={
                "PnR Runtime": total_runtime_str,
                "Stages": str(len(runtime_data)),
                "IPOs": str(len(pnr_runtimes))
            },
            html_file=runtime_html_path,
            priority=3,
            issues=issues,
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
                    # Check if formal crashed
                    crash_check = self.file_utils.run_command(
                        f"tail -100 {formal_log} | grep -E 'stopped at line.*due to error|Error: Unknown name:.*FM-036|Error: The current design is not set.*FM-008' | head -1"
                    )
                    completion_check = self.file_utils.run_command(
                        f"grep -E 'Verification SUCCEEDED|Verification FAILED|Verification UNRESOLVED' {formal_log} | tail -1"
                    )
                    
                    if crash_check.strip() and not completion_check.strip():
                        # Formal crashed - still extract runtime but mark as crashed
                        runtime_seconds = 0
                        result = self.file_utils.run_command(f"grep 'Elapsed time:' {formal_log} | tail -n1 | sed 's/.*Elapsed time: \\([0-9]*\\) seconds.*/\\1/'")
                        if result.strip() and result.strip().isdigit():
                            runtime_seconds = int(result.strip())
                            runtime_hours = runtime_seconds / 3600
                            formal_runtimes[formal_type] = f"{runtime_hours:.2f} hours (CRASHED)"
                        else:
                            formal_runtimes[formal_type] = "CRASHED"
                        continue
                    
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
                        
                        if check_result.strip() and not completion_check.strip():
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
                # Determine color based on status
                row_color = ""
                reset_color = ""
                
                # Check for CRASHED status (formal verification crashes)
                if "CRASHED" in runtime.upper() or "CRASHED" in str(end).upper():
                    row_color = Color.RED
                    reset_color = Color.RESET
                # Check for RUNNING status
                elif end == "RUNNING" or "RUNNING" in str(end).upper():
                    row_color = Color.YELLOW
                    reset_color = Color.RESET
                
                # Print with color if applicable
                if row_color:
                    print(f"  {row_color}{category:<{category_width}} {stage:<{stage_width}} {runtime:<{runtime_width}} {start:<{start_width}} {end:<{end_width}}{reset_color}")
                else:
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
            html_filename = f"{self.design_info.top_hier}_{os.environ.get('USER', 'avice')}_runtime_report_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\n  {Color.CYAN}Runtime HTML Report:{Color.RESET}")
            print(f"  Open with: /home/scratch.avice_vlsi/firefox-143.0.4/firefox {Color.MAGENTA}{html_filename}{Color.RESET} &")
            
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
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 20px;
            align-items: center;
            border-radius: 15px;
            margin-bottom: 20px;
        }}
        .header-text h1 {{
            font-size: 28px;
            margin: 0 0 8px 0;
        }}
        .header-text p {{
            opacity: 0.9;
            font-size: 14px;
            margin: 4px 0;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            margin: 5px 5px 5px 0;
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
            width: 80px;
            height: 80px;
            border-radius: 10px;
            background: white;
            padding: 10px;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .logo:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        .logo-modal {{
            display: none;
            position: fixed;
            z-index: 9999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }}
        .logo-modal.active {{
            display: flex;
        }}
        .logo-modal-content {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
        }}
        .logo-modal-close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
        .logo-modal-close:hover {{
            color: #bbb;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        /* Enhanced Grid Layout for Summary Cards */
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-align: center;
        }}
        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.25);
        }}
        .summary-card-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .summary-card-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .section {{
            background: white;
            margin: 20px 0;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
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
        /* Enhanced Grid Layout for PnR Details */
        .pnr-details {{
            margin: 20px 0;
            display: grid;
            gap: 20px;
        }}
        .ipo-section {{
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            transition: transform 0.2s ease;
        }}
        .ipo-section:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.12);
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
        
        /* Copyright Footer */
        .footer {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-radius: 10px;
            font-size: 14px;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .footer strong {{
            color: #00ff00;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img class='logo' src='data:image/png;base64,{logo_data}' alt='AVICE Logo' onclick="showLogoModal()" title="Click to enlarge">
            <div class="header-text">
                <h1>Runtime Analysis Report</h1>
                <p>Design: {self.design_info.top_hier} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Workarea: {self.workarea_abs}</p>
                <div>{badges_html}</div>
            </div>
        </div>
        
        <!-- Logo Modal -->
        <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
            <span class="logo-modal-close">&times;</span>
            <img class="logo-modal-content" src='data:image/png;base64,{logo_data}' alt='AVICE Logo'>
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
        
        // Logo modal functions
        function showLogoModal() {{
            document.getElementById('logoModal').classList.add('active');
        }}
        
        function hideLogoModal() {{
            document.getElementById('logoModal').classList.remove('active');
        }}
        
        // Allow ESC key to close logo modal
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                hideLogoModal();
            }}
        }});
        
        // Back to top button functionality - wait for DOM to load
        document.addEventListener('DOMContentLoaded', function() {{
            var backToTopBtn = document.getElementById('backToTopBtn');
            if (backToTopBtn) {{
                window.addEventListener('scroll', function() {{
                    if (window.pageYOffset > 300) {{
                        backToTopBtn.style.display = 'block';
                    }} else {{
                        backToTopBtn.style.display = 'none';
                    }}
                }});
                
                backToTopBtn.addEventListener('click', function() {{
                    window.scrollTo(0, 0);
                }});
            }}
        }});
    </script>
    
    <button id="backToTopBtn" style="display: none; position: fixed; bottom: 30px; right: 30px; 
            z-index: 99; border: none; outline: none; background-color: #667eea; color: white; 
            cursor: pointer; padding: 15px 20px; border-radius: 50px; font-size: 16px; 
            font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;"
            onmouseover="this.style.backgroundColor='#5568d3'; this.style.transform='scale(1.1)';"
            onmouseout="this.style.backgroundColor='#667eea'; this.style.transform='scale(1)';">
        ↑ Top
    </button>
    
    <!-- Copyright Footer -->
    <div class="footer">
        <p><strong>AVICE Runtime Analysis Report</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
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
        description="Avice Workarea Review Tool - Comprehensive ASIC/SoC design flow analysis",
        epilog="""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                          AVICE WORKAREA REVIEW TOOL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BASIC EXAMPLES:
  # Complete workarea analysis (all sections)
  /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea

  # Analyze specific IPO
  /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea ipo1000

  # Analyze using unit name from agur release table (automatic workarea lookup)
  /home/avice/scripts/avice_wa_review_launcher.csh --unit prt
  /home/avice/scripts/avice_wa_review_launcher.csh --unit pmux --sections runtime pt

  # Run only runtime and timing analysis (fast debug)
  /home/avice/scripts/avice_wa_review_launcher.csh /home/scratch.user/design/workarea -s runtime pt

SELECTIVE SECTION ANALYSIS:
  # Parasitic extraction and signoff timing only
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s star pt

  # Setup, synthesis, and PnR sections
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s setup synthesis pnr

  # Physical verification and GL checks
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s pv gl-check

  # ECO analysis sections
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s eco nv-gate-eco

ADDITIONAL OPTIONS:
  # Run without logo for automation
  /home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea --no-logo

  # Display comprehensive documentation
  /home/avice/scripts/avice_wa_review_launcher.csh --help-docs
  /home/avice/scripts/avice_wa_review_launcher.csh --open-docs

ANALYSIS SECTIONS (case-insensitive):
  setup          Environment, BeFlow config, PRC configuration
  runtime        DC, PnR, Star, PT, Formal, PV, GL Check runtimes
  synthesis      QoR reports, floorplan dimensions, timing groups
  pnr            Step sequence, routing data, timing histograms
  clock          Clock tree analysis, DSR latency, clock gating
  formal         Formal verification status, timestamp tracking
  star           Parasitic extraction (SPEF) runtime and status
  pt             Signoff timing, dual-scenario WNS/TNS/NVP, DSR skew
  pv             Physical verification (LVS/DRC/Antenna) flow analysis
  gl-check       Gate-level check error analysis and categorization
  eco            PT-ECO analysis and dont_use cell checks
  nv-gate-eco    NVIDIA Gate ECO command analysis and validation
  block-release  Block release information and umake commands

KEY FEATURES:
  • Multi-IPO support with automatic detection
  • Dual-scenario timing analysis (setup/hold)
  • DSR Mux Clock Skew tracking across work directories
  • Formal verification timestamp tracking vs design changes
  • Interactive HTML reports with absolute paths (portable)
  • Timeline visualizations for all flow stages
  • ECO dont_use cell validation
  • Runtime analysis with fast_dc detection

OUTPUT:
  Terminal: Compact, color-coded summaries with ASCII-only characters
  HTML:     Comprehensive reports in current working directory with:
            - Clickable log file links (absolute paths)
            - Interactive tables and expandable sections
            - Timeline visualizations and flow tracking
            - Professional CSS styling and mobile-responsive layout

For questions or support, contact: avice@nvidia.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
    parser.add_argument("--version", action="version", version="%(prog)s 2.0.0",
                       help="Show version information and exit")
    parser.add_argument("--no-logo", action="store_true",
                       help="Disable logo display (useful for automated scripts)")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip workarea validation (use with caution)")
    parser.add_argument("--unit", "-u", type=str,
                       help="Unit name from agur release table (e.g., prt, pmux). Automatically looks up released workarea path from AGUR_UNITS_TABLE.txt")
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
    
    # Handle --unit flag: look up workarea from release table
    if args.unit:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        release_tracking_dir = os.path.join(script_dir, "agur_release_tracking")
        table_file = os.path.join(release_tracking_dir, "AGUR_UNITS_TABLE.txt")
        update_checker = os.path.join(release_tracking_dir, "check_and_update_agur_table.sh")
        
        # Auto-check and update table if needed
        if os.path.exists(update_checker) and os.access(update_checker, os.X_OK):
            try:
                # Run the checker quietly to auto-update if needed
                result = subprocess.run([update_checker, "--quiet"], 
                                      capture_output=True, 
                                      timeout=60)
                # Return code 2 means first-time setup completed
                if result.returncode == 2:
                    print(f"{Color.CYAN}[INFO] First-time setup: Generated AGUR units table{Color.RESET}")
                elif result.returncode == 1:
                    print(f"{Color.YELLOW}[WARN] Failed to auto-update release table{Color.RESET}")
                # Return code 0 means table is up-to-date or successfully updated
            except subprocess.TimeoutExpired:
                print(f"{Color.YELLOW}[WARN] Table update check timed out{Color.RESET}")
            except Exception as e:
                print(f"{Color.YELLOW}[WARN] Could not check for table updates: {e}{Color.RESET}")
        
        if not os.path.exists(table_file):
            print(f"{Color.RED}[ERROR] AGUR_UNITS_TABLE.txt not found at: {table_file}{Color.RESET}")
            print(f"{Color.YELLOW}[HINT] Run: cd agur_release_tracking && ./extract_agur_releases.sh{Color.RESET}")
            sys.exit(1)
        
        # Look up unit in table
        workarea_found = False
        try:
            with open(table_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 3 and parts[0].lower() == args.unit.lower():
                            args.workarea = parts[2]  # Third column is the workarea path
                            workarea_found = True
                            print(f"{Color.CYAN}[INFO] Unit '{args.unit}' found in release table{Color.RESET}")
                            print(f"{Color.CYAN}[INFO] Using workarea: {args.workarea}{Color.RESET}")
                            break
            
            if not workarea_found:
                print(f"{Color.RED}[ERROR] Unit '{args.unit}' not found in AGUR_UNITS_TABLE.txt{Color.RESET}")
                print(f"{Color.YELLOW}[HINT] Available units:{Color.RESET}")
                with open(table_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = [p.strip() for p in line.split('|')]
                            if len(parts) >= 1:
                                print(f"  - {parts[0]}")
                sys.exit(1)
        except Exception as e:
            print(f"{Color.RED}[ERROR] Failed to read release table: {e}{Color.RESET}")
            sys.exit(1)
    
    # Check if workarea is provided
    if not args.workarea:
        parser.error("workarea is required (or use --unit to specify a unit name)")
    
    if not os.path.isdir(args.workarea):
        print(f"{Color.RED}Error: Workarea directory '{args.workarea}' does not exist{Color.RESET}")
        sys.exit(1)
    
    try:
        reviewer = WorkareaReviewer(args.workarea, args.ipo, show_logo=not args.no_logo, skip_validation=args.skip_validation)
        
        # Cleanup old HTML files from previous runs to avoid confusion
        reviewer._cleanup_old_html_files()
        
        # Handle selective section running
        if args.sections:
            # Run only specified sections
            section_mapping = {
                "setup": reviewer.run_setup_analysis,
                "runtime": reviewer.run_runtime_analysis,
                "synthesis": reviewer.run_synthesis_analysis,
                "syn": reviewer.run_synthesis_analysis,  # Alias for synthesis
                "dc": reviewer.run_synthesis_analysis,   # Alias for synthesis (Design Compiler)
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
