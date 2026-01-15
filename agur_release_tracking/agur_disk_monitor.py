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
    Checks disk usage for all AGUR units, central block release area, and PFNL Unit DB.
    Sends email alerts with two-tier system: 80% warning + 90% daily critical alerts.
    Designed to run daily via cron job.

Features:
    SHARED INFRASTRUCTURE MONITORING (Two-Tier Alerts):
    - Monitors AGUR block release area (/home/agur_backend_blockRelease/)
    - Monitors PFNL Unit DB (/home/PFNL_Unit_DB/)
    - At 80%: ONE-TIME warning email to avice@nvidia.com only
    - At >=90%: DAILY critical alerts to avice + ALL AGUR managers
    - State tracking prevents duplicate 80% warnings
    
    UNIT WORKAREA MONITORING:
    - Checks all 72 AGUR units from AGUR_UNITS_TABLE.csv
    - Groups critical units by owner (one email per owner)
    - Shows disk utilization summary (all user disks)
    - Recommends old workareas for cleanup (>30 days)
    - Clarifies users need to get below 90% to stop daily alerts
    - CC's avice@nvidia.com on all user emails
    - CC's chiplet managers at >=90%
    - CC's project manager at >=100%
    
    RELIABILITY:
    - Continues on email failures, notifies avice
    - Logs all activity to daily log files
    - Can be disabled via .disk_monitor_disabled file

Usage:
    python3 agur_disk_monitor.py                    # Check and send emails
    python3 agur_disk_monitor.py --dry-run          # Check only, no emails
    python3 agur_disk_monitor.py --test-mode        # Send test emails to avice only
    python3 agur_disk_monitor.py --threshold 85     # Custom threshold for units
    python3 agur_disk_monitor.py --units qcorer,pscc  # Specific units only

Arguments:
    --dry-run          Check disk usage but don't send any emails (for testing)
    --test-mode        Send all emails to avice@nvidia.com only (for testing)
    --threshold N      Disk usage threshold percentage for units (default: 90)
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

Alert State Tracking:
    The script maintains a .disk_monitor_warnings.state file to track 80% warnings.
    This ensures one-time warnings are not repeated until usage drops below 80%.
    The state file is automatically managed - no manual intervention needed.

Output:
    - Terminal: Summary of critical units and emails sent
    - Log file: logs/disk_alert_YYYYMMDD.log
    - State file: .disk_monitor_warnings.state (auto-managed)

Examples:
    # Test run (no emails)
    python3 agur_disk_monitor.py --dry-run
    
    # Test mode (emails to avice only)
    python3 agur_disk_monitor.py --test-mode
    
    # Test specific units
    python3 agur_disk_monitor.py --dry-run --units qcorer,pscc
    
    # Production run (sends emails)
    python3 agur_disk_monitor.py
    
    # Custom threshold for units (shared infra always uses 80%/90%)
    python3 agur_disk_monitor.py --threshold 85
    
    # Disable monitor
    touch .disk_monitor_disabled
    
    # Re-enable monitor
    rm .disk_monitor_disabled

Cron Setup:
    # Daily at 8:00 AM
    0 8 * * * cd /home/scratch.avice_vlsi/cursor/avice_wa_review/agur_release_tracking && /home/utils/Python/builds/3.11.9-20250715/bin/python3 agur_disk_monitor.py >> logs/disk_alert_$(date +\%Y\%m\%d).log 2>&1
    
    # Log cleanup (keep 30 days)
    0 9 * * * find /home/scratch.avice_vlsi/cursor/avice_wa_review/agur_release_tracking/logs/disk_alert_*.log -mtime +30 -delete

Author: Alon Vice (avice@nvidia.com)
Date: October 30, 2025
Last Updated: January 1, 2026 (Added PFNL DB monitoring + two-tier alerts)
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
from concurrent.futures import ThreadPoolExecutor, as_completed

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
WARNING_STATE_FILE = '.disk_monitor_warnings.state'
THRESHOLD_DEFAULT = 90
THRESHOLD_WARNING = 80
AGUR_UNITS_CSV = 'AGUR_UNITS_TABLE.csv'
LOGO_PATH = '../assets/images/avice_logo_small.png'
CENTRAL_RELEASE_PATH = '/home/agur_backend_blockRelease/'
PFNL_DB_PATH = '/home/PFNL_Unit_DB/'

# Shared infrastructure paths to monitor
SHARED_INFRA_PATHS = {
    'AGUR Release Area': CENTRAL_RELEASE_PATH,
    'PFNL Unit DB': PFNL_DB_PATH
}

# Chiplet Manager Mapping (CC at >=90%)
CHIPLET_MANAGERS = {
    'CPORT': 'avice@nvidia.com',
    'HPORT': 'avice@nvidia.com',
    'HIOPL': 'avice@nvidia.com',
    'NDQ': 'arot@nvidia.com',
    'QNS': 'ohamama@nvidia.com',
    'TCB': 'ohamama@nvidia.com',
    'TOP_YC': 'arot@nvidia.com',
}

# Project Manager (CC at >=100%)
PROJECT_MANAGER = 'oberkovitz@nvidia.com'

# All managers list (for shared infrastructure alerts at >=90%)
ALL_MANAGERS = list(set(CHIPLET_MANAGERS.values())) + [PROJECT_MANAGER]


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


def load_warning_state() -> Dict[str, bool]:
    """Load warning state from file (tracks if 80% warning was already sent)
    
    Returns:
        Dict mapping path names to whether 80% warning was sent
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    state_file = os.path.join(script_dir, WARNING_STATE_FILE)
    
    state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        state[line] = True
        except:
            pass
    
    return state


def save_warning_state(state: Dict[str, bool]) -> None:
    """Save warning state to file
    
    Args:
        state: Dict mapping path names to whether 80% warning was sent
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    state_file = os.path.join(script_dir, WARNING_STATE_FILE)
    
    try:
        with open(state_file, 'w') as f:
            for path_name in state.keys():
                if state[path_name]:
                    f.write(f"{path_name}\n")
    except Exception as e:
        print(f"[WARN] Failed to save warning state: {e}")


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


def extract_disk_path(workarea_path: str) -> str:
    """Extract base disk path from workarea path
    
    Examples:
        /home/scratch.avice_vlsi/agur/fth/... -> /home/scratch.avice_vlsi
        /home/scratch.avice_vlsi_1/ioplc/... -> /home/scratch.avice_vlsi_1
    
    Args:
        workarea_path: Full workarea path
        
    Returns:
        Base disk path
    """
    if 'scratch.' in workarea_path:
        match = re.search(r'(/home/scratch\.[^/]+(?:_vlsi(?:_\d+)?)?)', workarea_path)
        if match:
            return match.group(1)
    elif 'sunbird_' in workarea_path:
        match = re.search(r'(/home/sunbird_[^/]+)', workarea_path)
        if match:
            return match.group(1)
    elif 'starling_' in workarea_path:
        match = re.search(r'(/home/starling_[^/]+)', workarea_path)
        if match:
            return match.group(1)
    return workarea_path.split('/')[0:3]  # Fallback: /home/something


def get_chiplet_manager(chiplet: str) -> Optional[str]:
    """Get manager email for a chiplet
    
    Args:
        chiplet: Chiplet name (e.g., 'CPORT', 'NDQ')
        
    Returns:
        Manager email or None if not found
    """
    return CHIPLET_MANAGERS.get(chiplet)


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
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                universal_newlines=True, 
                                timeout=5)
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


def parse_size_to_bytes(size_str: str) -> int:
    """Convert human-readable size to bytes for sorting
    
    Args:
        size_str: Size string like "2.5T", "500G", "100M"
        
    Returns:
        Size in bytes (int)
    """
    size_str = size_str.strip().upper()
    multipliers = {
        'K': 1024,
        'M': 1024**2,
        'G': 1024**3,
        'T': 1024**4,
        'P': 1024**5
    }
    
    try:
        # Extract number and unit
        match = re.match(r'^([\d.]+)([KMGTP]?)$', size_str)
        if match:
            num, unit = match.groups()
            multiplier = multipliers.get(unit, 1)
            return int(float(num) * multiplier)
    except Exception:
        pass
    
    return 0  # Default for unparseable sizes


def calculate_dir_size(dir_path: str, timeout_sec: int = 180) -> Tuple[str, int]:
    """Calculate size of a directory with increased timeout for large workareas
    
    Args:
        dir_path: Directory path to measure
        timeout_sec: Timeout in seconds (default: 180s = 3 minutes for large workareas)
    
    Returns:
        Tuple of (size_string, size_bytes)
        Returns (">100G", 100GB) if timeout
    """
    try:
        # Use du -sh to get total size (including all subdirectories)
        # Increased timeout to 180s (3 minutes) for very large workareas (hundreds of GB)
        du_result = subprocess.run(['du', '-sh', dir_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True,
                                  timeout=timeout_sec)
        if du_result.returncode == 0:
            size_str = du_result.stdout.split()[0]
            size_bytes = parse_size_to_bytes(size_str)
            return (size_str, size_bytes)
    except subprocess.TimeoutExpired:
        # If du times out after 3 minutes, workarea is HUGE (>500GB likely)
        # Return conservative estimate
        return ('>500G', 500 * 1024**3)
    except Exception:
        pass
    
    return ('>100G', 100 * 1024**3)


def find_old_large_workareas(disk_path: str, age_days: int = 30, top_n: int = 3, timeout_sec: int = 60) -> Optional[List[Dict]]:
    """Find top N oldest workareas on a disk using depth-based scanning with parallel size calculation
    
    Strategy:
    1. Scan directories at depth 2-5 from disk root
    2. Exclude PnR/signoff subdirectories (they're inside workareas)
    3. Filter by age > age_days
    4. Get size for each IN PARALLEL (using ThreadPoolExecutor)
    5. Sort by size descending, return top N
    
    Args:
        disk_path: Base disk path (e.g., /home/scratch.avice_vlsi_1)
        age_days: Minimum age in days (default: 30)
        top_n: Number of results to return (default: 3)
        timeout_sec: Find command timeout in seconds (default: 60)
        
    Returns:
        List of dicts: [{'size': '2.5T', 'path': '...', 'age_days': 90, 'last_modified': 'Oct 15, 2024'}, ...]
        None if timeout
        [] if error or no results
    """
    try:
        # Build find command with exclusions
        # Strategy: Find workarea directories at typical depths (3-5 levels from disk root)
        # Most workareas are at depth 3-5: disk_root/project/unit/workarea_name
        # or disk_root/agur/1NL/unit/workarea_name
        # We filter the results to exclude known subdirectories
        cmd = f"""find {disk_path}/ -mindepth 3 -maxdepth 5 -type d -mtime +{age_days} \
            2>/dev/null | head -200"""
        
        # Execute with timeout to get list of directories
        result = subprocess.run(cmd, shell=True, 
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True,
                               timeout=timeout_sec)
        
        if result.returncode == 0 and result.stdout:
            # Path segments that indicate this is NOT a workarea root (check full path)
            excluded_path_segments = [
                '/COMMON/', '/common/', '/old/', '/backup/', '/samples/', 
                '/scripts/', '/sources/', '/reports/', '/logs/', '/temp/',
                '/my_backup/', '/.git/', '/hooks/', '/tmp/'
            ]
            
            # Common subdirectory names to exclude (check basename only)
            excluded_subdirs = {
                'pnr_flow', 'signoff_flow', 'export', 'nbu_signoff', 'syn_flow', 
                'formal_flow', 'pv_flow', 'fe_reports', 'fe_results', 'rbv', 'flp',
                'fsub_scratchDir', 'logs', 'log', 'reports', 'scripts', 'src', 'temp',
                'cmd_log', 'last_run', '.git', 'task_scripts', 'umake_log', 'unit_scripts',
                'nv_gen_runset', 'fe_logs', 'hooks', 'tmp', 'run_logs', 'out', 'sources',
                'my_backup', 'backup', 'common_scripts', 'samples', 'COMMON', 'old',
                'fe_logs', 'data', 'cache'
            }
            
            # Patterns that indicate subdirectories (not workarea roots) - check basename
            subdir_patterns = [
                r'_scripts$',      # any_scripts
                r'_backup$',       # any_backup
                r'_samples$',      # any_samples
                r'_common$',       # any_common
                r'_inputs?$',      # any_input/any_inputs
                r'_flow$',         # any_flow
                r'_results?$',     # any_result/any_results
                r'_logs?$',        # any_log/any_logs
                r'_reports?$',     # any_report/any_reports
                r'^fe_',           # fe_*
                r'^nv_',           # nv_*
                r'_fix_',          # fix directories
            ]
            
            entries = []
            dir_paths = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
            
            # Filter to find workarea root directories
            filtered_paths = []
            for dir_path in dir_paths:
                # Skip if path contains excluded segments (e.g., /COMMON/, /old/, /backup/)
                skip_path = False
                for segment in excluded_path_segments:
                    if segment in dir_path:
                        skip_path = True
                        break
                
                if skip_path:
                    continue
                
                dir_basename = os.path.basename(dir_path)
                
                # Skip if directory name matches excluded subdirs
                if dir_basename.lower() in excluded_subdirs:
                    continue
                
                # Skip if starts with '.' or 'work_'
                if dir_basename.startswith('.') or dir_basename.startswith('work_'):
                    continue
                
                # Skip if matches ipo pattern
                if re.match(r'ipo\d+', dir_basename):
                    continue
                
                # Skip if matches any subdirectory pattern
                is_subdir = False
                for pattern in subdir_patterns:
                    if re.search(pattern, dir_basename, re.IGNORECASE):
                        is_subdir = True
                        break
                
                if is_subdir:
                    continue
                
                # Include directories that contain '_rbv_' (typical workarea naming)
                if '_rbv_' in dir_basename:
                    filtered_paths.append(dir_path)
            
            # Process directories in PARALLEL for faster execution
            # Helper function to process a single directory
            def process_directory(dir_path):
                """Process a single directory: calculate size and get mtime"""
                try:
                    # Get mtime first (fast operation)
                    stat_result = subprocess.run(['stat', '-c', '%Y', dir_path],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                universal_newlines=True,
                                                timeout=2)
                    if stat_result.returncode != 0:
                        return None
                    
                    mtime_epoch = int(stat_result.stdout.strip())
                    age_days_calc = int((time.time() - mtime_epoch) / 86400)
                    last_modified = datetime.fromtimestamp(mtime_epoch).strftime('%b %d, %Y')
                    
                    # Calculate size (slow operation, 180s timeout for large workareas)
                    size_str, size_bytes = calculate_dir_size(dir_path, timeout_sec=180)
                    
                    return {
                        'size': size_str,
                        'size_bytes': size_bytes,
                        'path': dir_path,
                        'age_days': age_days_calc,
                        'last_modified': last_modified
                    }
                except Exception:
                    return None
            
            # Use ThreadPoolExecutor for parallel processing (max 5 concurrent threads)
            # This speeds up size calculation significantly (5x faster for 5 workareas)
            entries = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all directory processing tasks
                future_to_path = {executor.submit(process_directory, path): path 
                                 for path in filtered_paths[:50]}
                
                # Collect results as they complete
                for future in as_completed(future_to_path):
                    result = future.result()
                    if result:
                        entries.append(result)
            
            # Sort by size (largest first)
            entries.sort(key=lambda x: x['size_bytes'], reverse=True)
            return entries[:top_n]
            
    except subprocess.TimeoutExpired:
        return None  # Indicate timeout
    except Exception:
        return []
    
    return []


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


def send_single_unit_email(owner: str, unit_info: Dict, logo_data: str, dry_run: bool = False, 
                           test_mode: bool = False, disk_summary: Optional[Dict] = None, 
                           old_workareas: Optional[Dict] = None) -> bool:
    """Send email for single critical unit (uses unified format with consolidated email)
    
    Args:
        owner: Username (e.g., 'thadad')
        unit_info: Dict with unit data
        logo_data: Base64 encoded logo
        dry_run: If True, print email details but don't send
        test_mode: If True, send to avice@nvidia.com only (for testing)
        disk_summary: Optional dict of disk paths to usage info
        old_workareas: Optional dict of disk paths to old workarea list
        
    Returns:
        True if email sent successfully (or dry run), False otherwise
    """
    # Use the same consolidated format for consistency (just with 1 unit)
    return send_consolidated_email(owner, [unit_info], logo_data, dry_run, test_mode, disk_summary, old_workareas)


def send_consolidated_email(owner: str, units: List[Dict], logo_data: str, dry_run: bool = False, 
                           test_mode: bool = False, disk_summary: Optional[Dict] = None,
                           old_workareas: Optional[Dict] = None) -> bool:
    """Send email for multiple critical units owned by same person
    
    Args:
        owner: Username (e.g., 'siddharthasa')
        units: List of unit_info dicts (2+ units)
        logo_data: Base64 encoded logo
        dry_run: If True, print email details but don't send
        test_mode: If True, send to avice@nvidia.com only (for testing)
        disk_summary: Optional dict of disk paths to usage info
        old_workareas: Optional dict of disk paths to old workarea list
        
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
        
        # Calculate worst (max) usage percentage from BOTH units and disk summary
        max_usage = max(unit['usage_pct'] for unit in units)
        
        # Also check disk summary for higher usage (important for multi-disk users)
        if disk_summary:
            disk_max = max(disk['usage_pct'] for disk in disk_summary.values())
            max_usage = max(max_usage, disk_max)
        
        # Collect unique chiplets and their managers
        chiplet_managers = set()
        for unit in units:
            manager = get_chiplet_manager(unit['chiplet'])
            if manager:
                chiplet_managers.add(manager)
        
        # Build CC list
        cc_list = ["avice@nvidia.com"]  # Always CC avice
        
        # Add chiplet managers (>=90%)
        if max_usage >= 90:
            cc_list.extend(chiplet_managers)
        
        # Add project manager (>=100%)
        if max_usage >= 100:
            cc_list.append(PROJECT_MANAGER)
        
        # Remove duplicates while preserving order
        cc_list = list(dict.fromkeys(cc_list))
        
        # Email addresses
        from_email = f"{os.environ.get('USER', 'avice')}@nvidia.com"
        if test_mode:
            to_email = "avice@nvidia.com"  # TEST MODE: All emails to avice
            cc_emails = None
            subject_prefix = "[TEST] "
        else:
            to_email = f"{owner}@nvidia.com"
            cc_emails = cc_list
            subject_prefix = ""
        
        # Subject
        unit_word = "unit" if len(units) == 1 else "units"
        subject = f"{subject_prefix}[CRITICAL] Disk Usage Alert: {len(units)} AGUR {unit_word} at >=90%"
        
        # Build disk summary section (show disk info for all users)
        disk_summary_html = ''
        if disk_summary and len(disk_summary) >= 1:
            disk_rows = ''
            disks_sorted = sorted(disk_summary.items(), key=lambda x: x[1]['usage_pct'], reverse=True)
            min_usage = min(d[1]['usage_pct'] for d in disks_sorted)
            max_usage_disk = max(d[1]['usage_pct'] for d in disks_sorted)
            
            for disk_path, disk_info in disks_sorted:
                status_color = '#e74c3c' if disk_info['usage_pct'] >= 90 else '#f39c12' if disk_info['usage_pct'] >= 80 else '#27ae60'
                status_text = '[CRITICAL]' if disk_info['usage_pct'] >= 90 else '[WARNING]' if disk_info['usage_pct'] >= 80 else '[OK]'
                disk_rows += f"""
                <tr>
                    <td style="font-size: 16px;">{disk_path}</td>
                    <td style="color: {status_color}; font-weight: bold; font-size: 22px;">{disk_info['usage_pct']}%</td>
                    <td style="font-size: 16px;">{disk_info['size']}</td>
                    <td style="color: {status_color}; font-weight: bold; font-size: 16px;">{disk_info['avail']}</td>
                    <td style="color: {status_color}; font-size: 13px;">{status_text}</td>
                </tr>"""
            
            # Check if balancing recommended (only for multiple disks)
            balance_notice = ''
            if len(disk_summary) > 1 and max_usage_disk - min_usage >= 20:
                balance_notice = f"""
                <div style="background: #fff3cd; border-left: 4px solid #ff9800; padding: 12px; margin: 10px 0;">
                    <p style="margin: 0; font-weight: bold; color: #e65100;">⚖️ Storage Balancing Recommended</p>
                    <p style="margin: 5px 0 0 0; color: #e65100;">Your disks are unbalanced. Consider moving data from high-usage disks to lower-usage disks to optimize storage.</p>
                </div>"""
            
            disk_word = "disk" if len(disk_summary) == 1 else "disks"
            levels_text = "" if len(disk_summary) == 1 else " with varying usage levels"
            disk_summary_html = f"""
        <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 15px;">
            <h3 style="color: #1565c0; margin-top: 0;">📊 Your Disk Utilization Summary</h3>
            <p style="margin: 5px 0; color: #1565c0;">You have {len(disk_summary)} scratch {disk_word}{levels_text}:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <tr style="background: #1565c0; color: white;">
                    <th style="padding: 10px; text-align: left;">Disk Path</th>
                    <th style="padding: 10px; text-align: left;">Usage</th>
                    <th style="padding: 10px; text-align: left;">Total Size</th>
                    <th style="padding: 10px; text-align: left;">Available</th>
                    <th style="padding: 10px; text-align: left;">Status</th>
                </tr>
                {disk_rows}
            </table>
            {balance_notice}
        </div>"""
        
        # Build escalation notice (if managers are CC'd)
        escalation_notice = ''
        if cc_emails and len(cc_emails) > 1:  # More than just avice
            manager_names = []
            if max_usage >= 90:
                for unit in units:
                    manager = get_chiplet_manager(unit['chiplet'])
                    if manager and manager not in manager_names:
                        chiplet_name = unit['chiplet']
                        manager_names.append(f"{chiplet_name} manager")
            if max_usage >= 100:
                manager_names.append("project manager")
            
            if manager_names:
                escalation_notice = f"""
        <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 12px 15px; margin: 15px;">
            <p style="margin: 0; font-weight: bold; color: #c62828;">🚨 Management Escalation Notice</p>
            <p style="margin: 5px 0 0 0; color: #c62828;">Due to {"critical (>=100%)" if max_usage >= 100 else "high (>=90%)"} disk usage, your {' and '.join(manager_names)} {'has' if len(manager_names) == 1 else 'have'} been notified (CC'd) to assist with storage management and prioritization.</p>
        </div>"""
        
        # Build old workareas section (for disks at >=90%)
        old_workareas_html = ''
        if old_workareas:
            for disk_path, workareas in old_workareas.items():
                if workareas is None:
                    # Timeout occurred
                    old_workareas_html += f"""
        <div style="background: #fff3cd; border-left: 4px solid #ff9800; padding: 15px; margin: 15px;">
            <h3 style="color: #e65100; margin-top: 0;">💾 {disk_path}</h3>
            <p style="margin: 5px 0; color: #e65100;"><strong>Note:</strong> Automatic scan timed out (disk too large). Run manual commands below to find cleanup candidates.</p>
        </div>"""
                elif workareas:
                    # Found old workareas
                    workarea_rows = ''
                    for i, wa in enumerate(workareas, 1):
                        workarea_rows += f"""
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; margin: 8px 0;">
                    <div style="font-weight: bold; color: #c62828; font-size: 16px;">{i}. {wa['size']} - {wa['path']}</div>
                    <div style="color: #666; font-size: 13px; margin-top: 3px;">Last modified: {wa['last_modified']} ({wa['age_days']} days ago)</div>
                </div>"""
                    
                    old_workareas_html += f"""
        <div style="background: #fff3e1; border-left: 4px solid #ff9800; padding: 15px; margin: 15px;">
            <h3 style="color: #e65100; margin-top: 0;">💾 {disk_path} - Top Cleanup Candidates</h3>
            <p style="margin: 5px 0; color: #e65100;">These workareas are <strong>>30 days old</strong> and consuming significant space:</p>
            {workarea_rows}
            <p style="margin: 10px 0 0 0; color: #e65100; font-size: 13px;"><strong>Tip:</strong> Consider archiving or removing these old workareas to free up space.</p>
        </div>"""
        
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
        
        # Build logo image (only if exists and reasonable size) - tall version for header
        logo_cell = ''
        if logo_data and len(logo_data) < 500000:
            logo_cell = f'''
                            <td style="width: 100px; text-align: center; vertical-align: middle; border-right: 2px solid rgba(255,255,255,0.3); padding: 0 10px;">
                                <img src="data:image/png;base64,{logo_data}" alt="" width="80" height="80" style="display: block; margin: 0 auto; border-radius: 6px;">
                            </td>'''
        
        # HTML body - Single row compact header
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px;">
    <div style="max-width: 900px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
        
        <!-- Single Row Compact Header -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #dc3545;">
            <tr>{logo_cell}
                <td style="padding: 12px 15px; vertical-align: middle;">
                    <span style="color: white; font-size: 28px; font-weight: bold; display: block;">Hello {display_name}</span>
                    <span style="color: white; font-size: 18px;">⚠ Critical disk usage! Daily alerts at 8:00 AM until &lt; 90%</span>
                </td>
                <td style="width: 600px; text-align: right; vertical-align: middle; padding: 10px 15px;">
                    <table cellpadding="0" cellspacing="0" border="0" align="right">
                        <tr>
                            <td style="background-color: #fff; border: 3px solid #fff; border-radius: 6px; padding: 14px 35px; text-align: center;">
                                <span style="color: #dc3545; font-size: 42px; font-weight: bold; display: block; line-height: 1;">{max_usage}%</span>
                                <span style="color: #666; font-size: 14px; display: block; margin-top: 3px; white-space: nowrap;">MAX DISK USAGE</span>
                            </td>
                            <td style="width: 18px;"></td>
                            <td style="background-color: #fff; border: 3px solid #fff; border-radius: 6px; padding: 14px 35px; text-align: center;">
                                <span style="color: #dc3545; font-size: 42px; font-weight: bold; display: block; line-height: 1;">{len(units)}</span>
                                <span style="color: #666; font-size: 14px; display: block; margin-top: 3px; white-space: nowrap;">{"UNIT" if len(units) == 1 else "UNITS"}</span>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        {escalation_notice}
        
        {disk_summary_html}
        
        {old_workareas_html}
        
        <!-- Critical Units Table -->
        <div style="padding: 15px;">
            <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-top: 0;">Critical Units</h3>
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
            <p style="color: #2e7d32; margin: 5px 0;">Apply these cleanup strategies to <strong>each workarea listed above</strong> (especially the old ones shown in cleanup candidates):</p>
            <ol style="margin: 10px 0; padding-left: 20px;">
                <li style="margin: 12px 0; color: #2e7d32;">
                    <strong>Remove old PnR work directories:</strong>
                    <pre style="background: #263238; color: #aed581; padding: 8px; border-radius: 4px; margin: 5px 0; font-size: 11px;">cd [workarea_path]/pnr_flow
ls -ltd */work_* | tail -n +3   # Show all except latest 2
rm -rf [old_work_dirs]          # Delete after review</pre>
                </li>
                <li style="margin: 12px 0; color: #2e7d32;">
                    <strong>Delete old PT timing sessions:</strong>
                    <pre style="background: #263238; color: #aed581; padding: 8px; border-radius: 4px; margin: 5px 0; font-size: 11px;">cd [workarea_path]/signoff_flow/auto_pt
ls -ltd work_* | tail -n +4     # Show all except latest 3
rm -rf [old_work_dirs]          # Delete after review</pre>
                </li>
                <li style="margin: 12px 0; color: #2e7d32;">
                    <strong>Clean up old Star SPEF files:</strong>
                    <pre style="background: #263238; color: #aed581; padding: 8px; border-radius: 4px; margin: 5px 0; font-size: 11px;">cd [workarea_path]/signoff_flow/star
du -sh work_*/spef              # Check sizes
rm -rf work_*/spef/*.gz         # Delete old SPEFs</pre>
                </li>
                <li style="margin: 12px 0; color: #2e7d32;">
                    <strong>Archive or remove entire old workareas:</strong>
                    <pre style="background: #263238; color: #aed581; padding: 8px; border-radius: 4px; margin: 5px 0; font-size: 11px;"># Focus on workareas shown in "Top Cleanup Candidates" above
# These are >30 days old and consuming significant space
tar -czf [workarea_name].tar.gz [workarea_path]  # Archive
# OR
rm -rf [workarea_path]          # Delete (after backup!)</pre>
                </li>
            </ol>
            <div style="background: #ffebee; border: 1px solid #ef5350; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <p style="margin: 0; font-weight: bold; color: #c62828;">⚠ Safety Warning:</p>
                <p style="margin: 5px 0 0 0; color: #c62828;">Always verify with <code>ls</code> before running <code>rm -rf</code>! Consider archiving important data to tape first.</p>
            </div>
            <p style="color: #2e7d32; margin: 10px 0 0 0;"><strong>Note:</strong> Replace <code>[workarea_path]</code> with actual paths from the workareas listed in this email.</p>
        </div>
        
        <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 15px;">
            <h3 style="color: #1565c0; margin-top: 0;">Quick Disk Analysis Commands (CSH/TCSH Compatible)</h3>
            <p style="margin: 5px 0; color: #1565c0;">Copy-paste these commands to analyze disk usage. Run from workarea root directory.</p>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find top 10 largest directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">du -sk * |& grep -v '^du:' | sort -rn | head -10</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">Shows size in KB for each directory, sorted largest first</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Count and size of PnR work directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find pnr_flow/*/work_* -maxdepth 0 -type d |& wc -l
find pnr_flow/*/work_* -maxdepth 0 -type d -exec du -sk {{}} \; |& sort -rn | head -5</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">First line: total count. Second line: top 5 largest work dirs</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Count and size of PT timing sessions:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find signoff_flow/auto_pt/work_* -maxdepth 0 -type d |& wc -l
find signoff_flow/auto_pt/work_* -maxdepth 0 -type d -exec du -sk {{}} \; |& sort -rn | head -5</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">First line: total count. Second line: top 5 largest PT sessions</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find large log files (>100MB):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find . -name "*.log" -type f -size +102400 -exec ls -lh {{}} \; |& awk '{{print $5, $9}}' | head -10</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">Shows file size and path for logs >100MB (102400 blocks = 100MB)</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find old work directories (>60 days):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find pnr_flow/*/work_* signoff_flow/*/work_* -maxdepth 0 -type d -mtime +60 |& grep -v '^find:'</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">Lists all work directories older than 60 days (prime cleanup candidates)</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Star SPEF files disk usage:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find signoff_flow/star/work_*/spef -type f -name "*.spef.gz" -exec du -sk {{}} \; |& sort -rn | head -10</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">Shows largest SPEF files in KB (old corners can often be deleted)</p>
            </div>
            
            <div style="background: #fff3e1; border: 1px solid #ff9800; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <p style="margin: 0; font-weight: bold; color: #e65100;">💡 Pro Tips:</p>
                <ul style="margin: 5px 0; padding-left: 20px; color: #e65100;">
                    <li><code>|&</code> redirects both stdout and stderr (csh/tcsh syntax)</li>
                    <li><code>grep -v '^find:'</code> filters error messages</li>
                    <li>All commands use relative paths from workarea root</li>
                    <li><code>sort -rn</code> = reverse numeric sort (largest first)</li>
                </ul>
            </div>
            
            <p style="margin: 10px 0 0 0; color: #1565c0; font-size: 12px;"><strong>Tip:</strong> <code>cd</code> to each workarea listed above, then run these commands to identify cleanup targets.</p>
        </div>
        
        <!-- Footer -->
        <table width="100%" cellpadding="15" cellspacing="0" border="0" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">
            <tr>
                <td style="font-size: 12px;">
                    <strong>AGUR Disk Monitor</strong><br>
                    Copyright (c) 2025 Alon Vice (avice)<br>
                    Contact: <a href="mailto:avice@nvidia.com" style="color: #a8ff78; text-decoration: none;">avice@nvidia.com</a>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>"""
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send via SMTP
        all_recipients = [to_email]
        if cc_emails:
            all_recipients.extend(cc_emails)
        with smtplib.SMTP('smtp.nvidia.com', 25, timeout=30) as server:
            server.sendmail(from_email, all_recipients, msg.as_string())
        
        return True
    except Exception as e:
        raise Exception(f"Email send failed: {str(e)}")


def send_shared_infra_alert(path_name: str, path: str, usage_pct: int, mount: str, size: str, 
                           used: str, avail: str, filesystem: str, logo_data: str, 
                           is_warning: bool = False, dry_run: bool = False, 
                           test_mode: bool = False) -> bool:
    """Send email alert for critical shared infrastructure (AGUR release area or PFNL DB)
    
    Args:
        path_name: Friendly name (e.g., 'AGUR Release Area', 'PFNL Unit DB')
        path: Actual path being monitored
        usage_pct: Disk usage percentage
        mount: Mount point
        size: Total size
        used: Used space
        avail: Available space
        filesystem: Filesystem name
        logo_data: Base64 encoded logo
        is_warning: If True, this is an 80% warning (not daily alert)
        dry_run: If True, print email details but don't send
        test_mode: If True, add [TEST] prefix to subject
        
    Returns:
        True if email sent successfully (or dry run), False otherwise
    """
    if dry_run:
        alert_type = "80% WARNING" if is_warning else f"{usage_pct}% ALERT"
        print(f"[DRY RUN] Would send {path_name} {alert_type} to avice@nvidia.com" + 
              (f" and {len(ALL_MANAGERS)} managers" if not is_warning and usage_pct >= 90 else ""))
        return True
    
    try:
        from_email = f"{os.environ.get('USER', 'avice')}@nvidia.com"
        to_email = "avice@nvidia.com"
        
        # Build CC list
        cc_list = []
        if not is_warning and usage_pct >= 90:
            # At >=90%, CC all managers (daily alerts)
            cc_list = [mgr for mgr in ALL_MANAGERS if mgr != to_email]
        
        subject_prefix = "[TEST] " if test_mode else ""
        
        if is_warning:
            # 80% Initial warning
            subject = f"{subject_prefix}[WARNING] {path_name} Disk Usage: {usage_pct}% (First Alert)"
            alert_level = "WARNING"
            alert_color = "#ff9800"
            alert_bg = "#fff3cd"
        else:
            # >=90% Critical alert
            subject = f"{subject_prefix}[CRITICAL] {path_name} Disk Usage: {usage_pct}%"
            alert_level = "CRITICAL"
            alert_color = "#e74c3c"
            alert_bg = "#ffebee"
        
        # Build escalation notice for >=90%
        escalation_notice = ''
        if not is_warning and usage_pct >= 90 and cc_list:
            escalation_notice = f"""
        <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 12px 15px; margin: 15px;">
            <p style="margin: 0; font-weight: bold; color: #c62828;">🚨 Management Escalation</p>
            <p style="margin: 5px 0 0 0; color: #c62828;">Due to critical disk usage (>=90%), all AGUR managers have been notified (CC'd): {', '.join(set(cc_list))}</p>
            <p style="margin: 5px 0 0 0; color: #c62828;">You will receive <strong>daily alerts at 8:00 AM</strong> until usage drops below 90%.</p>
        </div>"""
        
        # Build alert notice based on type
        if is_warning:
            alert_notice = f"""
        <div style="background: {alert_bg}; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px;">
            <p style="margin: 0; font-weight: bold; color: #856404;">⚠ INITIAL WARNING - 80% THRESHOLD REACHED</p>
            <p style="margin: 5px 0 0 0; color: #856404;">The {path_name} has reached 80% disk usage. This is a <strong>one-time warning</strong> to alert you of increasing disk consumption.</p>
            <p style="margin: 5px 0 0 0; color: #856404;"><strong>Action required:</strong> Please plan cleanup activities. If usage reaches 90%, you will receive <strong>daily alerts</strong> and all AGUR managers will be notified.</p>
        </div>"""
        else:
            alert_notice = f"""
        <div style="background: {alert_bg}; border-left: 4px solid {alert_color}; padding: 15px; margin: 15px;">
            <p style="margin: 0; font-weight: bold; color: #c62828;">🚨 CRITICAL - IMMEDIATE ACTION REQUIRED</p>
            <p style="margin: 5px 0 0 0; color: #c62828;">The {path_name} has reached critical disk usage (>= 90%). {'Designers will be unable to release their blocks if this disk fills up, blocking the entire AGUR project workflow.' if 'AGUR' in path_name else 'PFNL database operations will be impacted if this disk fills up.'}</p>
            <p style="margin: 5px 0 0 0; color: #c62828;"><strong>You will continue to receive this email daily at 8:00 AM until disk usage drops below 90%.</strong></p>
        </div>"""
        
        # Cleanup recommendations based on path type
        if 'AGUR' in path_name:
            cleanup_section = f"""
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
            <p style="margin: 5px 0; color: #1565c0;">Run these commands to analyze the area:</p>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Top 10 largest directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">du -sh {path}*/ 2>/dev/null | sort -rh | head -10</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">List all directories with sizes:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">ls -lhd {path}*/ 2>/dev/null</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find old directories (>60 days):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find {path} -maxdepth 1 -type d -mtime +60 2>/dev/null</pre>
            </div>
        </div>"""
        else:  # PFNL
            cleanup_section = f"""
        <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 15px;">
            <h3 style="color: #2e7d32; margin-top: 0;">Recommended Actions</h3>
            <ol style="margin: 10px 0; padding-left: 20px; color: #2e7d32;">
                <li>Check for old unit database versions that can be removed</li>
                <li>Identify large files/directories consuming space</li>
                <li>Coordinate with PFNL team for cleanup strategy</li>
                <li>Review database retention policy</li>
                <li>Consider archiving old unit data</li>
            </ol>
        </div>
        
        <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 15px;">
            <h3 style="color: #1565c0; margin-top: 0;">Quick Analysis Commands</h3>
            <p style="margin: 5px 0; color: #1565c0;">Run these commands to analyze the database area:</p>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Top 10 largest directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">du -sh {path}*/ 2>/dev/null | sort -rh | head -10</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">List all directories with sizes:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">ls -lhd {path}*/ 2>/dev/null</pre>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find old directories (>60 days):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find {path} -maxdepth 1 -type d -mtime +60 2>/dev/null</pre>
            </div>
        </div>"""
        
        # Build logo cell (only if exists and reasonable size)
        logo_cell = ''
        if logo_data and len(logo_data) < 500000:
            logo_cell = f'''
                            <td style="width: 100px; text-align: center; vertical-align: middle; border-right: 2px solid rgba(255,255,255,0.3); padding: 0 10px;">
                                <img src="data:image/png;base64,{logo_data}" alt="" width="80" height="80" style="display: block; margin: 0 auto; border-radius: 6px;">
                            </td>'''
        
        # Choose color based on alert level
        header_color = '#ff9800' if is_warning else '#dc3545'
        
        # HTML body - Single row compact header
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px;">
    <div style="max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
        
        <!-- Single Row Compact Header -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: {header_color};">
            <tr>{logo_cell}
                <td style="padding: 12px 15px; vertical-align: middle;">
                    <span style="color: white; font-size: 22px; font-weight: bold; display: block;">[{alert_level}] {path_name}</span>
                    <span style="color: white; font-size: 18px;">{"⚠ One-time warning - Plan cleanup to avoid daily alerts at 90%" if is_warning else "🚨 Critical! Daily alerts until usage drops below 90%"}</span>
                </td>
                <td style="width: 350px; text-align: right; vertical-align: middle; padding: 10px 15px;">
                    <table cellpadding="0" cellspacing="0" border="0" align="right">
                        <tr>
                            <td style="background-color: #fff; border: 3px solid #fff; border-radius: 6px; padding: 16px 38px; text-align: center;">
                                <span style="color: {header_color}; font-size: 46px; font-weight: bold; display: block; line-height: 1;">{usage_pct}%</span>
                                <span style="color: #666; font-size: 14px; display: block; margin-top: 3px; white-space: nowrap;">DISK USAGE</span>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        {alert_notice}
        
        {escalation_notice}
        
        <!-- Disk Information -->
        <div style="padding: 15px;">
            <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">Disk Information</h3>
            <div class="disk-info">
                <table>
                    <tr>
                        <td>Path:</td>
                        <td><code>{path}</code></td>
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
                        <td style="color: {alert_color}; font-weight: bold; font-size: 18px;">{avail}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        {cleanup_section}
        
        <!-- Footer -->
        <table width="100%" cellpadding="15" cellspacing="0" border="0" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">
            <tr>
                <td style="font-size: 12px;">
                    <strong>AGUR Disk Monitor</strong><br>
                    Copyright (c) 2025 Alon Vice (avice)<br>
                    Contact: <a href="mailto:avice@nvidia.com" style="color: #a8ff78; text-decoration: none;">avice@nvidia.com</a>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>"""
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        if cc_list:
            msg['Cc'] = ', '.join(cc_list)
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send via SMTP
        all_recipients = [to_email]
        if cc_list:
            all_recipients.extend(cc_list)
        with smtplib.SMTP('smtp.nvidia.com', 25, timeout=30) as server:
            server.sendmail(from_email, all_recipients, msg.as_string())
        
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
  - Checks shared infrastructure with two-tier alerts:
    * AGUR block release area ({Color.CYAN}/home/agur_backend_blockRelease/{Color.END})
    * PFNL Unit DB ({Color.CYAN}/home/PFNL_Unit_DB/{Color.END})
    * At 80%: ONE-TIME warning to avice only
    * At >=90%: DAILY alerts to avice + ALL managers
  - Checks all 72 AGUR units from {Color.CYAN}AGUR_UNITS_TABLE.csv{Color.END}
  - Groups critical units by owner (one email per owner)
  - Shows disk utilization summaries and cleanup recommendations
  - Clarifies users need to get below 90% to stop daily alerts
  - CC's avice@nvidia.com on all user emails
  - CC's chiplet managers at >=90%, project manager at >=100%
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
  0 8 * * * cd /home/scratch.avice_vlsi/cursor/avice_wa_review/agur_release_tracking && \\
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
    
    # Load warning state (tracks if 80% warning was already sent)
    warning_state = load_warning_state()
    
    # Load logo for emails
    logo_data = load_logo()
    
    # Check shared infrastructure paths (AGUR release area + PFNL DB)
    print(f"Checking shared infrastructure paths...")
    infra_alerts_sent = 0
    infra_results = {}
    
    for path_name, path in SHARED_INFRA_PATHS.items():
        print(f"  {path_name}: {path}")
        usage_pct, mount, size, used, avail, filesystem = check_disk_usage(path)
        
        if usage_pct is not None:
            infra_results[path_name] = {
                'usage_pct': usage_pct,
                'mount': mount,
                'size': size,
                'used': used,
                'avail': avail,
                'filesystem': filesystem,
                'path': path
            }
            
            # Two-tier alert system:
            # 1. At 80%: Send ONE-TIME warning to avice only
            # 2. At >=90%: Send DAILY alerts to avice + all managers
            
            if usage_pct >= 90:
                # Critical: Daily alert to avice + all managers
                print(f"    [CRITICAL] {usage_pct}% used (>=90% - daily alert)")
                try:
                    send_shared_infra_alert(path_name, path, usage_pct, mount, size, 
                                          used, avail, filesystem, logo_data,
                                          is_warning=False, dry_run=args.dry_run, 
                                          test_mode=args.test_mode)
                    if args.dry_run:
                        print(f"    [DRY RUN] Would send daily alert to avice + all managers")
                    elif args.test_mode:
                        print(f"    [TEST] Daily alert sent (all managers CC'd)")
                    else:
                        print(f"    [EMAIL] Daily alert sent to avice + all managers")
                    infra_alerts_sent += 1
                    # Mark that warning was sent (for state tracking)
                    warning_state[path_name] = True
                except Exception as e:
                    print(f"    [ERROR] Failed to send alert: {e}")
                    
            elif usage_pct >= 80:
                # Warning: One-time alert to avice only (if not already sent)
                if path_name not in warning_state:
                    print(f"    [WARNING] {usage_pct}% used (>=80% - first warning)")
                    try:
                        send_shared_infra_alert(path_name, path, usage_pct, mount, size, 
                                              used, avail, filesystem, logo_data,
                                              is_warning=True, dry_run=args.dry_run, 
                                              test_mode=args.test_mode)
                        if args.dry_run:
                            print(f"    [DRY RUN] Would send 80% warning to avice")
                        elif args.test_mode:
                            print(f"    [TEST] 80% warning sent to avice")
                        else:
                            print(f"    [EMAIL] 80% warning sent to avice")
                        infra_alerts_sent += 1
                        # Mark that warning was sent
                        warning_state[path_name] = True
                    except Exception as e:
                        print(f"    [ERROR] Failed to send warning: {e}")
                else:
                    print(f"    [WARNING] {usage_pct}% used (80% warning already sent, waiting for 90%)")
            else:
                print(f"    [OK] {usage_pct}% used (below 80%)")
                # Clear warning state if usage drops below 80%
                if path_name in warning_state:
                    del warning_state[path_name]
        else:
            print(f"    [WARN] Could not check disk usage")
    
    # Save updated warning state
    save_warning_state(warning_state)
    
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
    
    if not critical_units and infra_alerts_sent == 0:
        print(f"\n[OK] No critical units found (threshold: {args.threshold}%)")
        print(f"[OK] All shared infrastructure below thresholds")
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
    
    # Build disk summaries and scan for old workareas per owner
    print(f"\nBuilding disk summaries and scanning for old workareas...")
    owner_disk_summaries = {}
    owner_old_workareas = {}
    
    for owner, owner_units in units_by_owner.items():
        # Extract ALL unique disks for this owner by:
        # 1. Checking units in CSV
        # 2. Auto-discovering other _vlsi disks (_vlsi, _vlsi_1, _vlsi_2, etc.)
        disk_paths = set()
        
        # Method 1: Check all units in the CSV for this owner to find their disks
        for unit in units:
            unit_owner = extract_owner_from_path(unit['workarea'])
            if unit_owner == owner:
                disk_path = extract_disk_path(unit['workarea'])
                disk_paths.add(disk_path)
        
        # Method 2: Auto-discover additional disks for this owner
        # Check for common patterns: scratch.{user}_vlsi, scratch.{user}_vlsi_1, scratch.{user}_vlsi_2
        base_patterns = [
            f'/home/scratch.{owner}_vlsi',
            f'/home/scratch.{owner}_vlsi_1', 
            f'/home/scratch.{owner}_vlsi_2',
            f'/home/scratch.{owner}_vlsi_3',
            f'/home/scratch.{owner}'  # Some users might not have _vlsi suffix
        ]
        for pattern in base_patterns:
            if os.path.exists(pattern) and os.path.isdir(pattern):
                disk_paths.add(pattern)
        
        # Check disk usage for ALL disks this owner has
        disk_summary = {}
        for disk_path in sorted(disk_paths):  # Sort for consistent ordering
            usage_pct, mount, size, used, avail, filesystem = check_disk_usage(disk_path)
            if usage_pct is not None:
                disk_summary[disk_path] = {
                    'usage_pct': usage_pct,
                    'mount': mount,
                    'size': size,
                    'used': used,
                    'avail': avail,
                    'filesystem': filesystem
                }
        # Always show disk summary (even for single disk) so user can see all their storage
        owner_disk_summaries[owner] = disk_summary if len(disk_summary) > 0 else None
        
        # Scan for old workareas on critical disks (>=90%)
        old_workareas = {}
        for unit in owner_units:
            if unit['usage_pct'] >= 90:
                disk_path = extract_disk_path(unit['workarea'])
                if disk_path not in old_workareas:
                    if not args.quiet:
                        print(f"  Scanning {disk_path} for old workareas...")
                    result = find_old_large_workareas(disk_path, age_days=30, top_n=3, timeout_sec=60)
                    old_workareas[disk_path] = result
                    # Log scan results
                    if not args.quiet:
                        if result is None:
                            print(f"    -> Scan timed out (disk too large)")
                        elif result:
                            print(f"    -> Found {len(result)} old workarea(s): {', '.join([wa['size'] for wa in result])}")
                        else:
                            print(f"    -> No old workareas found (>30 days)")
        owner_old_workareas[owner] = old_workareas if old_workareas else None
    
    # Send emails
    print(f"\nSending emails...")
    email_failures = []
    emails_sent = 0
    
    for owner, owner_units in units_by_owner.items():
        try:
            disk_summary = owner_disk_summaries.get(owner)
            old_workareas = owner_old_workareas.get(owner)
            
            if len(owner_units) == 1:
                send_single_unit_email(owner, owner_units[0], logo_data, args.dry_run, 
                                     args.test_mode, disk_summary, old_workareas)
            else:
                send_consolidated_email(owner, owner_units, logo_data, args.dry_run, 
                                      args.test_mode, disk_summary, old_workareas)
            
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
    
    # Shared infrastructure summary
    print(f"  Shared Infrastructure:")
    for path_name, result in infra_results.items():
        usage = result['usage_pct']
        if usage >= 90:
            status = "[CRITICAL - DAILY ALERTS]"
        elif usage >= 80:
            if path_name in warning_state:
                status = "[WARNING SENT]"
            else:
                status = "[OK]"
        else:
            status = "[OK]"
        print(f"    {path_name}: {usage}% {status}")
    
    # Unit check summary
    print(f"  Total units checked: {len(units)}")
    print(f"  Critical units (>={args.threshold}%): {len(critical_units)}")
    if critical_units:
        print(f"  Unique owners: {len(units_by_owner)}")
    
    # Email summary
    if args.dry_run:
        total_emails = len(units_by_owner) + infra_alerts_sent
        print(f"  Emails (dry run): {total_emails} would be sent")
    elif args.test_mode:
        total_emails = emails_sent + infra_alerts_sent
        print(f"  Emails sent (TEST MODE): {total_emails} to avice@nvidia.com, {len(email_failures)} failed")
    else:
        total_emails = emails_sent + infra_alerts_sent
        print(f"  Emails sent: {total_emails} successful, {len(email_failures)} failed")
    print(f"  Execution time: {elapsed:.1f} seconds")
    print(f"{'='*80}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

