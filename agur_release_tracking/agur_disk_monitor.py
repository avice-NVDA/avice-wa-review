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
AGUR Daily Disk Usage Monitor

Purpose:
    Checks disk usage for all AGUR units and central block release area, sends 
    email alerts for critical levels (>=90%). Designed to run daily via cron job.

Features:
    - Checks central AGUR block release area (/home/agur_backend_blockRelease/)
    - Alerts avice@nvidia.com if central area reaches >=90%
    - Checks all 72 AGUR units from AGUR_UNITS_TABLE.csv
    - Groups critical units by owner (one email per owner)
    - Sends individual email if owner has 1 critical unit
    - Sends consolidated email if owner has 2+ critical units
    - Clarifies users need to get below 90% to stop daily alerts
    - CC's avice@nvidia.com on all user emails
    - Continues on email failures, notifies avice
    - Logs all activity to daily log files

Usage:
    python3 agur_disk_monitor.py                    # Check and send emails
    python3 agur_disk_monitor.py --dry-run          # Check only, no emails
    python3 agur_disk_monitor.py --threshold 85     # Custom threshold
    python3 agur_disk_monitor.py --units qcorer,pscc  # Specific units only

Arguments:
    --dry-run          Check disk usage but don't send any emails (for testing)
    --threshold N      Disk usage threshold percentage (default: 90)
    --units U1,U2      Check only specific units (comma-separated)
    --quiet            Minimal output (summary only)
    --help             Show this help message

DISABLE/ENABLE Control:
    To temporarily disable the monitor (e.g., during maintenance):
        touch .disk_monitor_disabled
        
    To re-enable the monitor:
        rm .disk_monitor_disabled
        
    To disable with a reason:
        echo "Maintenance window" > .disk_monitor_disabled
    
    The cron job will still run but exit immediately when disabled.
    Check logs to see disable notifications.

Output:
    - Terminal: Summary of critical units and emails sent
    - Log file: logs/disk_alert_YYYYMMDD.log

Examples:
    # Test run (no emails)
    python3 agur_disk_monitor.py --dry-run
    
    # Test specific units
    python3 agur_disk_monitor.py --dry-run --units qcorer,pscc
    
    # Production run (sends emails)
    python3 agur_disk_monitor.py
    
    # Custom threshold
    python3 agur_disk_monitor.py --threshold 85
    
    # Disable monitor
    touch .disk_monitor_disabled
    
    # Re-enable monitor
    rm .disk_monitor_disabled

Cron Setup:
    # Daily at 8:00 AM
    0 8 * * * cd /home/avice/scripts/avice_wa_review/agur_release_tracking && /home/utils/Python/builds/3.11.9-20250715/bin/python3 agur_disk_monitor.py >> logs/disk_alert_$(date +\%Y\%m\%d).log 2>&1
    
    # Log cleanup (keep 30 days)
    0 9 * * * find /home/avice/scripts/avice_wa_review/agur_release_tracking/logs/disk_alert_*.log -mtime +30 -delete

Author: Alon Vice (avice@nvidia.com)
Date: October 30, 2025
"""

import os
import sys
import csv
import re
import subprocess
import smtplib
import base64
import argparse
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Tuple, Optional

# ANSI Color codes for terminal output
class Color:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Constants
DISABLE_FILE = '.disk_monitor_disabled'
THRESHOLD_DEFAULT = 90
AGUR_UNITS_CSV = 'AGUR_UNITS_TABLE.csv'
LOGO_PATH = '../images/avice_logo.png'
CENTRAL_RELEASE_PATH = '/home/agur_backend_blockRelease/'


def is_monitor_enabled() -> Tuple[bool, Optional[str]]:
    """Check if monitor is enabled (no disable file exists)
    
    Returns:
        (is_enabled, disable_reason)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    disable_file = os.path.join(script_dir, DISABLE_FILE)
    
    if not os.path.exists(disable_file):
        return (True, None)
    
    # Read disable reason if file has content
    reason = None
    try:
        if os.path.getsize(disable_file) > 0:
            with open(disable_file, 'r') as f:
                reason = f.read().strip()
    except:
        pass
    
    return (False, reason)


def extract_owner_from_path(workarea_path: str) -> str:
    """Extract username from workarea path (handles _vlsi_1, _vlsi_2, etc.)
    
    Examples:
        /home/scratch.thadad_vlsi_1/... -> thadad
        /home/scratch.arcohen_vlsi/... -> arcohen
        /home/scratch.ronil/... -> ronil
    
    Args:
        workarea_path: Full workarea path
        
    Returns:
        Username string (e.g., 'thadad')
    """
    if 'scratch.' in workarea_path:
        match = re.search(r'/scratch\.([^/]+?)(?:_vlsi(?:_\d+)?)?/', workarea_path)
        if match:
            return match.group(1)
    return 'unknown'


def check_disk_usage(workarea_path: str) -> Tuple[Optional[int], str, str, str, str, str]:
    """Check disk usage for given workarea path using df -h
    
    Args:
        workarea_path: Path to check
        
    Returns:
        (usage_pct, mount, size, used, avail, filesystem)
        Returns (None, ...) if check fails
    """
    try:
        result = subprocess.run(['df', '-h', workarea_path], 
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 5:
                    usage_pct = int(parts[4].rstrip('%'))
                    filesystem = parts[0]
                    size = parts[1]
                    used = parts[2]
                    avail = parts[3]
                    mount = parts[5] if len(parts) > 5 else parts[0]
                    return (usage_pct, mount, size, used, avail, filesystem)
    except Exception:
        pass
    return (None, '', '', '', '', '')


def load_logo() -> str:
    """Load and base64 encode the Avice logo
    
    Returns:
        Base64 encoded logo string
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, LOGO_PATH)
    
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except:
            pass
    return ''


def send_single_unit_email(owner: str, unit_info: Dict, logo_data: str, dry_run: bool = False, test_mode: bool = False) -> bool:
    """Send email for single critical unit (uses unified format with consolidated email)
    
    Args:
        owner: Username (e.g., 'thadad')
        unit_info: Dict with unit data
        logo_data: Base64 encoded logo
        dry_run: If True, print email details but don't send
        test_mode: If True, send to avice@nvidia.com only (for testing)
        
    Returns:
        True if email sent successfully (or dry run), False otherwise
    """
    # Use the same consolidated format for consistency (just with 1 unit)
    return send_consolidated_email(owner, [unit_info], logo_data, dry_run, test_mode)


def send_consolidated_email(owner: str, units: List[Dict], logo_data: str, dry_run: bool = False, test_mode: bool = False) -> bool:
    """Send email for multiple critical units owned by same person
    
    Args:
        owner: Username (e.g., 'siddharthasa')
        units: List of unit_info dicts (2+ units)
        logo_data: Base64 encoded logo
        dry_run: If True, print email details but don't send
        test_mode: If True, send to avice@nvidia.com only (for testing)
        
    Returns:
        True if email sent successfully (or dry run), False otherwise
    """
    if dry_run:
        unit_names = ', '.join([u['unit'] for u in units])
        print(f"[DRY RUN] Would send to {owner}@nvidia.com ({len(units)} units: {unit_names})")
        return True
    
    try:
        # Format display name
        display_name = owner.replace('_', ' ').title()
        
        # Email addresses
        from_email = f"{os.environ.get('USER', 'avice')}@nvidia.com"
        if test_mode:
            to_email = "avice@nvidia.com"  # TEST MODE: All emails to avice
            cc_email = None
            subject_prefix = "[TEST] "
        else:
            to_email = f"{owner}@nvidia.com"
            cc_email = "avice@nvidia.com"
            subject_prefix = ""
        
        # Calculate worst (max) usage percentage
        max_usage = max(unit['usage_pct'] for unit in units)
        
        # Subject
        unit_word = "unit" if len(units) == 1 else "units"
        subject = f"{subject_prefix}[CRITICAL] Disk Usage Alert: {len(units)} AGUR {unit_word} at >=90%"
        
        # Build units table HTML
        units_rows = ''
        for unit in sorted(units, key=lambda x: x['usage_pct'], reverse=True):
            units_rows += f"""
                <tr>
                    <td><span style="font-size: 14px !important;">{unit['unit']}</span></td>
                    <td><span style="font-size: 14px !important;">{unit['chiplet']}</span></td>
                    <td><span style="color: #e74c3c !important; font-weight: bold !important; font-size: 26px !important;">{unit['usage_pct']}%</span></td>
                    <td><span style="font-size: 14px !important;">{unit['size']}</span></td>
                    <td><span style="color: #e74c3c !important; font-weight: bold !important; font-size: 18px !important;">{unit['avail']}</span></td>
                    <td><span style="word-break: break-all; font-size: 11px !important;">{unit['workarea']}</span></td>
                </tr>"""
        
        # HTML body
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 0 15px 10px 15px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            font-size: 24px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .greeting {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px 15px;
            margin: 15px;
        }}
        .section {{
            padding: 15px;
        }}
        .section h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin-top: 0;
        }}
        .units-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        .units-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-size: 14px;
        }}
        .units-table td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .cleanup-list {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 15px;
        }}
        .cleanup-list ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .cleanup-list li {{
            margin: 8px 0;
            color: #2e7d32;
        }}
        .footer {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 12px;
        }}
        .footer a {{
            color: #a8ff78;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CRITICAL DISK USAGE ALERT</h1>
            <p style="margin: 3px 0 3px 0; font-size: 14px;">{"Immediate Action Required" if len(units) == 1 else "Multiple Units Require Immediate Action"}</p>
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0;">
                <tr>
                    <td width="54" style="padding-right: 10px; vertical-align: middle;">
                        <img src="data:image/png;base64,{logo_data}" alt="Avice Logo" width="54" height="54" style="display: block; border-radius: 6px;">
                    </td>
                    <td style="padding-left: 10px; vertical-align: middle;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #c0392b; border: 2px solid #fff; border-radius: 6px; height: 50px;">
                            <tr>
                                <td style="text-align: center; vertical-align: middle; width: 50%;">
                                    <div style="font-size: 28px; font-weight: bold; color: #fff; line-height: 1; margin: 0;">{max_usage}%</div>
                                    <div style="font-size: 9px; color: #fff; margin-top: 2px; letter-spacing: 0.5px;">MAX DISK USAGE</div>
                                </td>
                                <td style="text-align: center; vertical-align: middle; width: 50%; border-left: 1px solid rgba(255,255,255,0.3);">
                                    <div style="font-size: 28px; font-weight: bold; color: #fff; line-height: 1; margin: 0;">{len(units)}</div>
                                    <div style="font-size: 9px; color: #fff; margin-top: 2px; letter-spacing: 0.5px;">{"UNIT" if len(units) == 1 else "UNITS"}</div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </div>
        
        <div class="greeting">
            <p>Hello <strong>{display_name}</strong>,</p>
            <p style="margin-top: 3px;">{"Your workarea storage is critically low and may cause flow failures!" if len(units) == 1 else f"You have {len(units)} AGUR units with critical disk usage (>=90%). Multiple workareas require immediate attention!"}</p>
        </div>
        
        <div style="background: #fff3cd; border-left: 4px solid #ff9800; padding: 12px 15px; margin: 15px;">
            <p style="margin: 0; font-weight: bold; color: #e65100;">⚠ Daily Alert Notice</p>
            <p style="margin: 5px 0 0 0; color: #e65100;">You will continue to receive this email <strong>daily at 8:00 AM</strong> until your disk usage drops <strong>below 90%</strong>. Please take action to free up disk space to stop these alerts.</p>
        </div>
        
        <div class="section">
            <h3>Critical Units</h3>
            <table class="units-table">
                <tr>
                    <th>Unit</th>
                    <th>Chiplet</th>
                    <th>Usage</th>
                    <th>Total Size</th>
                    <th>Available</th>
                    <th>Workarea Path</th>
                </tr>
                {units_rows}
            </table>
        </div>
        
        <div class="cleanup-list">
            <h3 style="color: #2e7d32; margin-top: 0;">Recommended Cleanup Actions</h3>
            <ol>
                <li>Remove old PnR work directories (pnr_flow/*/work_*)</li>
                <li>Delete old PT timing sessions (signoff_flow/auto_pt/work_*)</li>
                <li>Clean up old Star SPEF files (signoff_flow/star/work_*/spef/)</li>
                <li>Archive completed runs to long-term storage</li>
            </ol>
            <p style="color: #2e7d32; margin: 10px 0 0 0;"><strong>Note:</strong> Apply these actions to all listed workareas to free up space.</p>
        </div>
        
        <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 15px;">
            <h3 style="color: #1565c0; margin-top: 0;">Quick Disk Analysis Commands</h3>
            <p style="margin: 5px 0; color: #1565c0;">Copy-paste these commands to analyze disk usage (cd to workarea first):</p>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find top 10 largest directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">du -sh */ 2>/dev/null | sort -rh | head -10</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Count and size of PnR work directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find pnr_flow/*/work_* -maxdepth 0 -type d 2>/dev/null | wc -l
du -sh pnr_flow/*/work_* 2>/dev/null | sort -rh | head -5</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Count and size of PT timing sessions:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find signoff_flow/auto_pt/work_* -maxdepth 0 -type d 2>/dev/null | wc -l
du -sh signoff_flow/auto_pt/work_* 2>/dev/null | sort -rh | head -5</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find large log files (>100MB):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find . -name "*.log" -size +100M -exec ls -lh {{}} \; 2>/dev/null | sort -k5 -rh | head -10</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find old work directories (>30 days):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find pnr_flow/*/work_* signoff_flow/*/work_* -maxdepth 0 -type d -mtime +30 2>/dev/null</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Star SPEF files disk usage:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">du -sh signoff_flow/star/work_*/spef 2>/dev/null | sort -rh</pre>
            </div>
            
            <p style="margin: 10px 0 0 0; color: #1565c0; font-size: 12px;"><strong>Tip:</strong> Review oldest work directories first. Keep only the latest 2-3 runs unless specifically needed.</p>
        </div>
        
        <div class="footer">
            <strong>AGUR Disk Monitor</strong><br>
            Copyright (c) 2025 Alon Vice (avice)<br>
            Contact: <a href="mailto:avice@nvidia.com">avice@nvidia.com</a>
        </div>
    </div>
</body>
</html>"""
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        if cc_email:
            msg['Cc'] = cc_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send via SMTP
        all_recipients = [to_email]
        if cc_email:
            all_recipients.append(cc_email)
        with smtplib.SMTP('smtp.nvidia.com', 25, timeout=30) as server:
            server.sendmail(from_email, all_recipients, msg.as_string())
        
        return True
    except Exception as e:
        raise Exception(f"Email send failed: {str(e)}")


def send_central_release_alert(usage_pct: int, mount: str, size: str, used: str, avail: str, 
                               filesystem: str, logo_data: str, dry_run: bool = False, 
                               test_mode: bool = False) -> bool:
    """Send email alert for critical central block release area
    
    Args:
        usage_pct: Disk usage percentage
        mount: Mount point
        size: Total size
        used: Used space
        avail: Available space
        filesystem: Filesystem name
        logo_data: Base64 encoded logo
        dry_run: If True, print email details but don't send
        test_mode: If True, add [TEST] prefix to subject
        
    Returns:
        True if email sent successfully (or dry run), False otherwise
    """
    if dry_run:
        print(f"[DRY RUN] Would send central release alert to avice@nvidia.com ({usage_pct}%)")
        return True
    
    try:
        from_email = f"{os.environ.get('USER', 'avice')}@nvidia.com"
        to_email = "avice@nvidia.com"
        subject_prefix = "[TEST] " if test_mode else ""
        subject = f"{subject_prefix}[CRITICAL] Central Block Release Disk Usage: {usage_pct}%"
        
        # HTML body
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 0 15px 10px 15px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            font-size: 24px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .alert-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px;
        }}
        .section {{
            padding: 15px;
        }}
        .disk-info {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin: 10px 0;
        }}
        .disk-info table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .disk-info td {{
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
        }}
        .disk-info td:first-child {{
            font-weight: bold;
            width: 40%;
            color: #495057;
        }}
        .disk-info td:last-child {{
            color: #212529;
        }}
        .usage-critical {{
            color: #e74c3c;
            font-weight: bold;
            font-size: 24px;
        }}
        .footer {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 12px;
        }}
        .footer a {{
            color: #a8ff78;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CRITICAL: Central Block Release Area</h1>
            <p style="margin: 3px 0 3px 0; font-size: 14px;">Shared Infrastructure Alert</p>
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0;">
                <tr>
                    <td width="54" style="padding-right: 10px; vertical-align: middle;">
                        <img src="data:image/png;base64,{logo_data}" alt="Avice Logo" width="54" height="54" style="display: block; border-radius: 6px;">
                    </td>
                    <td style="padding-left: 10px; vertical-align: middle;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #c0392b; border: 2px solid #fff; border-radius: 6px; height: 50px;">
                            <tr>
                                <td style="text-align: center; vertical-align: middle;">
                                    <div style="font-size: 32px; font-weight: bold; color: #fff; line-height: 1; margin: 0;">{usage_pct}%</div>
                                    <div style="font-size: 10px; color: #fff; margin-top: 2px; letter-spacing: 0.5px;">DISK USAGE</div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </div>
        
        <div class="alert-box">
            <p style="margin: 0; font-weight: bold; color: #856404;">IMMEDIATE ACTION REQUIRED</p>
            <p style="margin: 5px 0 0 0; color: #856404;">The central AGUR block release area has reached critical disk usage. If this disk fills up, designers will be unable to release their blocks to the central release area, blocking the entire AGUR project workflow.</p>
        </div>
        
        <div class="section">
            <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">Disk Information</h3>
            <div class="disk-info">
                <table>
                    <tr>
                        <td>Path:</td>
                        <td><code>{CENTRAL_RELEASE_PATH}</code></td>
                    </tr>
                    <tr>
                        <td>Disk Usage:</td>
                        <td><span class="usage-critical">{usage_pct}%</span></td>
                    </tr>
                    <tr>
                        <td>Filesystem:</td>
                        <td>{filesystem}</td>
                    </tr>
                    <tr>
                        <td>Mount Point:</td>
                        <td>{mount}</td>
                    </tr>
                    <tr>
                        <td>Total Size:</td>
                        <td>{size}</td>
                    </tr>
                    <tr>
                        <td>Used:</td>
                        <td>{used}</td>
                    </tr>
                    <tr>
                        <td>Available:</td>
                        <td style="color: #e74c3c; font-weight: bold; font-size: 18px;">{avail}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 15px;">
            <h3 style="color: #2e7d32; margin-top: 0;">Recommended Actions</h3>
            <ol style="margin: 10px 0; padding-left: 20px; color: #2e7d32;">
                <li>Check for old release versions that can be archived</li>
                <li>Identify large files/directories consuming space</li>
                <li>Coordinate with AGUR team for cleanup strategy</li>
                <li>Consider moving old releases to archive storage</li>
                <li>Review release retention policy</li>
            </ol>
        </div>
        
        <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 15px;">
            <h3 style="color: #1565c0; margin-top: 0;">Quick Analysis Commands</h3>
            <p style="margin: 5px 0; color: #1565c0;">Run these commands to analyze the central release area:</p>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Top 10 largest directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">du -sh {CENTRAL_RELEASE_PATH}*/ 2>/dev/null | sort -rh | head -10</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">List all release directories with sizes:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">ls -lhd {CENTRAL_RELEASE_PATH}*/ 2>/dev/null</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find old directories (>60 days):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find {CENTRAL_RELEASE_PATH} -maxdepth 1 -type d -mtime +60 2>/dev/null</pre>
            </div>
        </div>
        
        <div class="footer">
            <strong>AGUR Disk Monitor</strong><br>
            Copyright (c) 2025 Alon Vice (avice)<br>
            Contact: <a href="mailto:avice@nvidia.com">avice@nvidia.com</a>
        </div>
    </div>
</body>
</html>"""
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send via SMTP
        with smtplib.SMTP('smtp.nvidia.com', 25, timeout=30) as server:
            server.sendmail(from_email, [to_email], msg.as_string())
        
        return True
    except Exception as e:
        raise Exception(f"Email send failed: {str(e)}")


def send_failure_notification(failures: List[str]) -> None:
    """Send email to avice@nvidia.com about email send failures
    
    Args:
        failures: List of error messages
    """
    try:
        from_email = f"{os.environ.get('USER', 'avice')}@nvidia.com"
        to_email = "avice@nvidia.com"
        subject = f"[AGUR Disk Monitor] Email Failure Alert - {len(failures)} failed"
        
        body = f"""AGUR Disk Monitor - Email Failure Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The following emails failed to send:

"""
        for failure in failures:
            body += f"  - {failure}\n"
        
        body += """

Please investigate and retry manually if needed.

Log file: agur_release_tracking/logs/disk_alert_{date}.log

-- 
Alon Vice Tools
avice@nvidia.com
"""
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send via SMTP
        with smtplib.SMTP('smtp.nvidia.com', 25, timeout=30) as server:
            server.sendmail(from_email, [to_email], msg.as_string())
    except Exception as e:
        print(f"[ERROR] Failed to send failure notification: {e}")


def read_agur_units(filter_units: Optional[str] = None) -> List[Dict]:
    """Read AGUR units from CSV file
    
    Args:
        filter_units: Comma-separated list of units to filter (or None for all)
        
    Returns:
        List of unit dictionaries
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, AGUR_UNITS_CSV)
    
    if not os.path.exists(csv_path):
        print(f"[ERROR] AGUR units CSV not found: {csv_path}")
        sys.exit(1)
    
    units = []
    filter_set = set(filter_units.split(',')) if filter_units else None
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            unit_name = row['UNIT']
            if filter_set is None or unit_name in filter_set:
                units.append({
                    'unit': unit_name,
                    'chiplet': row['CHIPLET'],
                    'workarea': row['RELEASED_WA_PATH']
                })
    
    return units


def print_colored_help():
    """Print color-coded help message"""
    help_text = f"""
{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}
{Color.BOLD}{Color.GREEN}AGUR Daily Disk Usage Monitor{Color.END}
{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}

{Color.BOLD}{Color.YELLOW}DESCRIPTION:{Color.END}
  Checks disk usage for all AGUR units and central block release area.
  Sends email alerts for critical levels (>=90%). Designed for daily cron job.

{Color.BOLD}{Color.YELLOW}USAGE:{Color.END}
  {Color.CYAN}python3 agur_disk_monitor.py [OPTIONS]{Color.END}

{Color.BOLD}{Color.YELLOW}OPTIONS:{Color.END}
  {Color.GREEN}--dry-run{Color.END}              Check disk usage but don't send emails (for testing)
  {Color.GREEN}--test-mode{Color.END}            Send all emails to avice@nvidia.com only (for testing)
  {Color.GREEN}--threshold N{Color.END}          Disk usage threshold percentage (default: 90)
  {Color.GREEN}--units U1,U2{Color.END}          Check specific units only (comma-separated)
  {Color.GREEN}--quiet{Color.END}                Minimal output (summary only)
  {Color.GREEN}--help{Color.END}                 Show this help message

{Color.BOLD}{Color.YELLOW}FEATURES:{Color.END}
  - Checks central AGUR block release area ({Color.CYAN}/home/agur_backend_blockRelease/{Color.END})
  - Alerts {Color.CYAN}avice@nvidia.com{Color.END} if central area reaches >=90%
  - Checks all 72 AGUR units from {Color.CYAN}AGUR_UNITS_TABLE.csv{Color.END}
  - Groups critical units by owner (one email per owner)
  - Clarifies users need to get below 90% to stop daily alerts
  - CC's avice@nvidia.com on all user emails
  - Logs all activity to daily log files

{Color.BOLD}{Color.YELLOW}EXAMPLES:{Color.END}
  {Color.CYAN}# Test run without sending emails{Color.END}
  python3 agur_disk_monitor.py --dry-run
  
  {Color.CYAN}# Test specific units only{Color.END}
  python3 agur_disk_monitor.py --dry-run --units qcorer,pscc
  
  {Color.CYAN}# Custom threshold (85%){Color.END}
  python3 agur_disk_monitor.py --threshold 85
  
  {Color.CYAN}# Production run (sends emails){Color.END}
  python3 agur_disk_monitor.py

{Color.BOLD}{Color.YELLOW}DISABLE/ENABLE CONTROL:{Color.END}
  {Color.CYAN}# Temporarily disable the monitor{Color.END}
  touch .disk_monitor_disabled
  
  {Color.CYAN}# Re-enable the monitor{Color.END}
  rm .disk_monitor_disabled
  
  {Color.CYAN}# Disable with a reason{Color.END}
  echo "Maintenance window" > .disk_monitor_disabled
  
  {Color.MAGENTA}Note:{Color.END} The cron job will still run but exit immediately when disabled.

{Color.BOLD}{Color.YELLOW}CRON SETUP:{Color.END}
  {Color.CYAN}# Daily at 8:00 AM{Color.END}
  0 8 * * * cd /home/avice/scripts/avice_wa_review/agur_release_tracking && \\
    /home/utils/Python/builds/3.11.9-20250715/bin/python3 agur_disk_monitor.py \\
    >> logs/disk_alert_$(date +\\%Y\\%m\\%d).log 2>&1

{Color.BOLD}{Color.YELLOW}AUTHOR:{Color.END}
  Alon Vice ({Color.CYAN}avice@nvidia.com{Color.END})

{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}
"""
    print(help_text)


def main():
    # Check for --help flag manually to show colored help
    if '--help' in sys.argv or '-h' in sys.argv:
        print_colored_help()
        return 0
    
    # Build help epilog with disable control info (for errors only)
    epilog = """
DISABLE/ENABLE CONTROL:
  To temporarily disable the monitor (e.g., during maintenance):
    touch .disk_monitor_disabled
    
  To re-enable the monitor:
    rm .disk_monitor_disabled
    
  To disable with a reason:
    echo "Maintenance window" > .disk_monitor_disabled
  
  The cron job will still run but exit immediately when disabled.
  Check logs to see disable notifications.

EXAMPLES:
  python3 agur_disk_monitor.py --dry-run
    Test run without sending emails
    
  python3 agur_disk_monitor.py --dry-run --units qcorer,pscc
    Test specific units only
    
  python3 agur_disk_monitor.py --threshold 85
    Check with custom threshold (85%)
    
  python3 agur_disk_monitor.py
    Production run (sends emails)

AUTHOR:
  Alon Vice (avice@nvidia.com)
"""
    
    parser = argparse.ArgumentParser(
        description='AGUR Daily Disk Usage Monitor - Check disk usage and send email alerts',
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # Disable default help to use our colored version
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Check disk usage but don\'t send emails (for testing)')
    parser.add_argument('--test-mode', action='store_true',
                        help='TEST MODE: Send all emails to avice@nvidia.com only (for testing before going live)')
    parser.add_argument('--threshold', type=int, default=THRESHOLD_DEFAULT,
                        help=f'Disk usage threshold percentage (default: {THRESHOLD_DEFAULT})')
    parser.add_argument('--units', type=str, default=None,
                        help='Check specific units only (comma-separated)')
    parser.add_argument('--quiet', action='store_true',
                        help='Minimal output (summary only)')
    args = parser.parse_args()
    
    # Record start time
    start_time = time.time()
    
    # Check if monitor is enabled
    is_enabled, disable_reason = is_monitor_enabled()
    if not is_enabled:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        disable_file = os.path.join(script_dir, DISABLE_FILE)
        
        print(f"{'='*80}")
        print(f"AGUR Disk Monitor - DISABLED")
        print(f"{'='*80}")
        print(f"Monitor is currently disabled.")
        print(f"Disable file: {disable_file}")
        
        if disable_reason:
            print(f"Reason: {disable_reason}")
        
        print(f"\nTo re-enable the monitor, run:")
        print(f"  rm {disable_file}")
        print(f"{'='*80}")
        return 0
    
    # Print header
    print(f"{'='*80}")
    print(f"AGUR Disk Usage Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.dry_run:
        print(f"{'='*80}")
        print(f"[DRY RUN MODE] No emails will be sent")
    elif args.test_mode:
        print(f"{'='*80}")
        print(f"[TEST MODE] All emails will be sent to avice@nvidia.com only!")
        print(f"[TEST MODE] Subjects will have [TEST] prefix")
    print(f"{'='*80}")
    
    # Check central block release area first
    print(f"Checking central block release area: {CENTRAL_RELEASE_PATH}")
    central_usage_pct, central_mount, central_size, central_used, central_avail, central_filesystem = check_disk_usage(CENTRAL_RELEASE_PATH)
    central_alert_sent = False
    
    if central_usage_pct is not None:
        if central_usage_pct >= args.threshold:
            print(f"[CRITICAL] Central block release area: {central_usage_pct}% used")
            # Load logo for email
            logo_data = load_logo()
            try:
                send_central_release_alert(central_usage_pct, central_mount, central_size, 
                                          central_used, central_avail, central_filesystem, 
                                          logo_data, args.dry_run, args.test_mode)
                if args.dry_run:
                    print(f"[DRY RUN] Would send central release alert to avice@nvidia.com")
                elif args.test_mode:
                    print(f"[TEST] Central release alert sent to avice@nvidia.com")
                else:
                    print(f"[EMAIL] Central release alert sent to avice@nvidia.com")
                central_alert_sent = True
            except Exception as e:
                print(f"[ERROR] Failed to send central release alert: {e}")
        else:
            print(f"[OK] Central block release area: {central_usage_pct}% used (below threshold)")
    else:
        print(f"[WARN] Could not check central block release area disk usage")
    
    print()  # Blank line for readability
    
    # Read AGUR units
    units = read_agur_units(args.units)
    print(f"Checking {len(units)} units...\n")
    
    # Check disk usage
    critical_units = []
    for unit in units:
        usage_pct, mount, size, used, avail, filesystem = check_disk_usage(unit['workarea'])
        
        if usage_pct is not None and usage_pct >= args.threshold:
            unit['usage_pct'] = usage_pct
            unit['mount'] = mount
            unit['size'] = size
            unit['used'] = used
            unit['avail'] = avail
            unit['filesystem'] = filesystem
            unit['owner'] = extract_owner_from_path(unit['workarea'])
            critical_units.append(unit)
            
            if not args.quiet:
                print(f"[CRITICAL] {unit['unit']:15s} ({unit['chiplet']:10s}) - {usage_pct}% used | Owner: {unit['owner']}")
    
    if not critical_units and not central_alert_sent:
        print(f"\n[OK] No critical units found (threshold: {args.threshold}%)")
        print(f"{'='*80}")
        return 0
    
    # Group by owner
    units_by_owner = {}
    for unit in critical_units:
        owner = unit['owner']
        if owner not in units_by_owner:
            units_by_owner[owner] = []
        units_by_owner[owner].append(unit)
    
    print(f"\nGrouping by owner...")
    for owner, owner_units in units_by_owner.items():
        print(f"  {owner}: {len(owner_units)} unit(s)")
    
    # Load logo
    logo_data = load_logo()
    
    # Send emails
    print(f"\nSending emails...")
    email_failures = []
    emails_sent = 0
    
    for owner, owner_units in units_by_owner.items():
        try:
            if len(owner_units) == 1:
                send_single_unit_email(owner, owner_units[0], logo_data, args.dry_run, args.test_mode)
            else:
                send_consolidated_email(owner, owner_units, logo_data, args.dry_run, args.test_mode)
            
            if args.dry_run:
                print(f"[DRY RUN] Would send to {owner}@nvidia.com ({len(owner_units)} unit(s))")
            elif args.test_mode:
                print(f"[TEST] Sent to avice@nvidia.com (originally for {owner}@nvidia.com, {len(owner_units)} unit(s))")
                emails_sent += 1
            else:
                print(f"[EMAIL] Sent to {owner}@nvidia.com ({len(owner_units)} unit(s))")
                emails_sent += 1
        except Exception as e:
            error_msg = f"Failed to send email to {owner}@nvidia.com: {str(e)}"
            print(f"[ERROR] {error_msg}")
            email_failures.append(error_msg)
    
    # Notify avice of failures
    if email_failures and not args.dry_run:
        send_failure_notification(email_failures)
        print(f"[EMAIL] Failure notification sent to avice@nvidia.com")
    
    # Calculate execution time
    elapsed = time.time() - start_time
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"  Central block release: {central_usage_pct}% used" + (f" [ALERT SENT]" if central_alert_sent else " [OK]") if central_usage_pct is not None else "  Central block release: [CHECK FAILED]")
    print(f"  Total units checked: {len(units)}")
    print(f"  Critical units (>={args.threshold}%): {len(critical_units)}")
    if critical_units:
        print(f"  Unique owners: {len(units_by_owner)}")
    if args.dry_run:
        total_emails = len(units_by_owner) + (1 if central_usage_pct and central_usage_pct >= args.threshold else 0)
        print(f"  Emails (dry run): {total_emails} would be sent")
    elif args.test_mode:
        total_emails = emails_sent + (1 if central_alert_sent else 0)
        print(f"  Emails sent (TEST MODE): {total_emails} to avice@nvidia.com, {len(email_failures)} failed")
    else:
        total_emails = emails_sent + (1 if central_alert_sent else 0)
        print(f"  Emails sent: {total_emails} successful, {len(email_failures)} failed")
    print(f"  Execution time: {elapsed:.1f} seconds")
    print(f"{'='*80}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

