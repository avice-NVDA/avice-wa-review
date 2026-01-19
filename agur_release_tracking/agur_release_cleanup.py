#!/home/utils/Python/builds/3.11.9-20250715/bin/python3
#===============================================================================
#      +===+ +--+ +--+ +=+ +===+ +===+
#      |   | |  | |  | | | |     |    
#      |===| |  +-+  | | | |     |=== 
#      |   |  |     |  | | |     |    
#      |   |   +---+   +=+ +===+ +===+                                 
#            ~ Alon Vice Tools ~
# Copyright (c) 2026 Alon Vice (avice)
# All rights reserved.
# This script is the intellectual property of Alon Vice.
# For permissions and licensing, contact: avice@nvidia.com
#===============================================================================
"""
AGUR Block Release Area Cleanup Utility

Purpose:
    Analyzes the AGUR block release area (/home/agur_backend_blockRelease/) to identify
    old releases (>3 months by default) and provides cleanup recommendations to unit owners.
    Handles multi-user coordination when symlinks are created by fullchip STA/PV/PI users.

Features:
    - Interactive web dashboard for easy review and approval (DEFAULT MODE)
    - Scans all 73 AGUR units across 7 chiplets
    - Identifies releases older than configurable threshold (default: 90 days)
    - Detects symlinks and their owners via file ownership
    - Calculates reclaimable disk space using parallel du commands
    - Generates detailed CSV and HTML reports
    - Sends coordination emails to release owners, symlink owners, and chiplet managers
    - Tracks email history (remembers which releases were emailed)
    - Never deletes anything - ANALYSIS ONLY (dry-run by design)

Safety:
    - Read-only utility - never deletes files or modifies symlinks
    - Detects symlink dependencies for coordination
    - Provides safe deletion commands with verification steps
    - Requires manual user action for all deletions

Usage:
    python3 agur_release_cleanup.py                    # Interactive dashboard (DEFAULT)
    python3 agur_release_cleanup.py -c CPORT           # Interactive dashboard for specific chiplet
    python3 agur_release_cleanup.py --test-mode        # Interactive with test emails to current user
    python3 agur_release_cleanup.py --batch            # Batch mode (no interactive dashboard)
    python3 agur_release_cleanup.py --age-threshold 60 # Custom age threshold (days)
    python3 agur_release_cleanup.py --units prt,fdb    # Specific units only

Arguments:
    --age-threshold DAYS    Age threshold in days (default: 90)
    -c, --chiplet NAME      Chiplet name (CPORT, HPORT, HIOPL, NDQ, QNS, TCB, TOP_YC, ALL)
    --units U1,U2          Check only specific units (comma-separated)
    --test-mode            Send all emails to current user only (for testing)
    --batch                Disable interactive mode (for automated runs)
    --dry-run              Analysis only, no emails or reports
    --send-emails          Send emails in batch mode
    --parallel N           Number of parallel du processes (default: 10)
    --output-dir DIR       Output directory for reports (default: ./cleanup_reports)
    --quiet                Minimal output (summary only)
    --help                 Show this help message

Output:
    - Interactive Dashboard: http://localhost:5000 (default mode)
    - HTML Report: cleanup_reports/cleanup_unit_summary_YYYYMMDD_HHMMSS.html
    - CSV Report: cleanup_reports/cleanup_report_YYYYMMDD_HHMMSS.csv
    - Emails: To unit owners with CC to symlink owners and chiplet managers
    - Approval State: cleanup_reports/approval_state_YYYYMMDD_HHMMSS.json
    - Log file: logs/release_cleanup_YYYYMMDD.log

Examples:
    # Interactive dashboard (default)
    python3 agur_release_cleanup.py -c CPORT
    
    # Test mode (emails to current user only)
    python3 agur_release_cleanup.py -c CPORT --test-mode
    
    # Batch mode for automation (no dashboard)
    python3 agur_release_cleanup.py --batch --send-emails
    
    # Custom threshold (60 days)
    python3 agur_release_cleanup.py -c CPORT --age-threshold 60
    
    # Specific units only
    python3 agur_release_cleanup.py --units prt,fdb,pmux

Author: Alon Vice (avice@nvidia.com)
Date: January 18, 2026
"""

import os
import sys
import re
import csv
import base64
import smtplib
import subprocess
import argparse
import getpass
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import json
import webbrowser
import time
from threading import Thread
from flask import Flask, request, jsonify
from flask_cors import CORS

# Chiplet to units mapping
CHIPLET_UNITS = {
    'HIOPL': ['ioplca', 'ioplcb', 'ioplcc', 'ioplcd'],
    'CPORT': ['fdb', 'fth', 'lnd', 'pmux', 'prt'],
    'HPORT': ['ccorea', 'ccoreb', 'ccorec', 'ccored', 'ccoree', 'ccoref'],
    'NDQ': ['clr', 'clt', 'cscore', 'dcmp', 'fdbm', 'fdbs', 'fthm', 'ftos', 'fwam', 'fwas', 
            'glc', 'iopl', 'ioplm', 'iopx', 'ir', 'lndm', 'nvrisc', 'pmuxm', 'prtm', 
            'psca', 'pscb', 'pscc', 'pscd', 'px', 'riba', 'ribs', 'sma', 'yu'],
    'QNS': ['dqaa', 'dqaci', 'dqaco', 'dqai', 'dqamci', 'dqamco', 'dqamdi', 'dqamdo', 
            'dqap', 'dqavi', 'dqavo', 'dqax', 'dql', 'dqs', 'eds', 'qcorel', 'qcorer', 
            'tecorel', 'tecorer', 'tds'],
    'TCB': ['alm', 'bta', 'eri', 'hib'],
    'TOP_YC': ['top_yc_clock', 'top_yc_gpio', 'yc_clock_macro', 'yc_fuse', 'yc_fuse_macro', 'yu_mng']
}

# Constants
SCRIPT_DIR = Path(__file__).resolve().parent
RELEASE_BASE_PATH = '/home/agur_backend_blockRelease/block/'
UNITS_TABLE_FILE = SCRIPT_DIR / 'AGUR_UNITS_TABLE.csv'
DEFAULT_AGE_THRESHOLD = 90  # days
DEFAULT_PARALLEL_PROCESSES = 10
LOGO_PATH = SCRIPT_DIR.parent / 'assets/images/avice_logo_small.png'

# Chiplet managers mapping
CHIPLET_MANAGERS = {
    'HIOPL': 'avice@nvidia.com',
    'CPORT': 'avice@nvidia.com',
    'HPORT': 'avice@nvidia.com',
    'NDQ': 'arot@nvidia.com',
    'TOP_YC': 'arot@nvidia.com',
    'QNS': 'ohamama@nvidia.com',
    'TCB': 'ohamama@nvidia.com'
}
PROJECT_MANAGER = 'oberkovitz@nvidia.com'
ALWAYS_CC = 'avice@nvidia.com'  # Always CC on all emails

def get_test_mode_recipient() -> str:
    """Resolve test-mode recipient to the current user."""
    username = (os.environ.get('SUDO_USER') or
                os.environ.get('USER') or
                os.environ.get('LOGNAME') or
                getpass.getuser())
    if not username:
        return ALWAYS_CC
    if '@' in username:
        return username
    return f"{username}@nvidia.com"

# Data structures
@dataclass
class SymlinkInfo:
    """Information about a symlink pointing to a release"""
    symlink_name: str
    symlink_owner: str  # Username from ls -l
    symlink_path: str
    target_release: str
    
@dataclass
class ReleaseInfo:
    """Information about a single release directory"""
    unit: str
    chiplet: str
    release_dir: str
    full_path: str
    age_days: int
    size_bytes: int
    size_human: str
    owner: str
    release_timestamp: datetime
    has_symlinks: bool
    symlink_infos: List[SymlinkInfo] = field(default_factory=list)
    is_protected: bool = False  # True if pointed to by any symlink
    requires_coordination: bool = False  # True if symlinks created by other users
    log_file_path: str = ''
    folder_owner: str = ''  # Current owner from filesystem (ls -l)
    log_owner: str = ''  # Original release creator from logs/block_release.log

@dataclass
class OwnerRecommendation:
    """Cleanup recommendations for a specific owner"""
    owner_email: str
    releases: List[ReleaseInfo]
    total_size_bytes: int
    total_size_human: str
    unit_count: int
    release_count: int
    chiplet_manager: str
    all_symlink_owners: Set[str] = field(default_factory=set)
    cc_log_owners: Set[str] = field(default_factory=set)  # Previous owners from logs for CC

# Global state
logger = None

def get_actual_disk_usage(path: str) -> Tuple[int, float, float, float]:
    """Get actual disk usage from df command
    
    Args:
        path: Path to check disk usage for
        
    Returns:
        Tuple of (usage_pct, total_capacity_tb, used_tb, available_tb)
        Returns default fallback values if query fails
    """
    try:
        result = subprocess.run(['df', '-h', path], 
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
                    # Parse sizes (e.g., "120T" -> 120.0)
                    size_str = parts[1]  # Total
                    used_str = parts[2]  # Used
                    avail_str = parts[3] # Available
                    
                    # Simple conversion (handles T, G, M suffixes)
                    def parse_size_tb(s):
                        s = s.upper()
                        if s.endswith('T'):
                            return float(s[:-1])
                        elif s.endswith('G'):
                            return float(s[:-1]) / 1024
                        elif s.endswith('M'):
                            return float(s[:-1]) / (1024 * 1024)
                        return 0.0
                    
                    total_tb = parse_size_tb(size_str)
                    used_tb = parse_size_tb(used_str)
                    avail_tb = parse_size_tb(avail_str)
                    
                    return (usage_pct, total_tb, used_tb, avail_tb)
    except Exception as e:
        if logger:
            logger.warning(f"Failed to get disk usage for {path}: {e}")
    
    # Fallback to hardcoded values if query fails
    return (90, 120.0, 108.0, 12.0)

def setup_logging(quiet: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"release_cleanup_{datetime.now().strftime('%Y%m%d')}.log"
    
    logger = logging.getLogger('agur_release_cleanup')
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)
    
    # Console handler
    if not quiet:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(ch)
    
    return logger

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='AGUR Block Release Area Cleanup Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--age-threshold', type=int, default=DEFAULT_AGE_THRESHOLD,
                        help=f'Age threshold in days (default: {DEFAULT_AGE_THRESHOLD})')
    parser.add_argument('--dry-run', action='store_true',
                        help='Analysis only, no emails or reports')
    parser.add_argument('--send-emails', action='store_true',
                        help='Send emails to owners (default: reports only, no emails)')
    parser.add_argument('--email-only', action='store_true',
                        help='Send emails only, no reports')
    parser.add_argument('--units', type=str,
                        help='Comma-separated list of units to check')
    parser.add_argument('-c', '--chiplet', type=str,
                        help='Chiplet name(s) - comma-separated, case-insensitive (CPORT, HPORT, HIOPL, NDQ, QNS, TCB, TOP_YC, ALL)')
    parser.add_argument('--parallel', type=int, default=DEFAULT_PARALLEL_PROCESSES,
                        help=f'Number of parallel du processes (default: {DEFAULT_PARALLEL_PROCESSES})')
    parser.add_argument('--output-dir', type=str, default='cleanup_reports',
                        help='Output directory for reports (default: cleanup_reports)')
    parser.add_argument('--test-mode', action='store_true',
                        help='Send all emails to current user only (implies --send-emails)')
    parser.add_argument('--quiet', action='store_true',
                        help='Minimal output (summary only)')
    parser.add_argument('--interactive', action='store_true', default=True,
                        help='Start interactive approval server (DEFAULT, opens dashboard in browser)')
    parser.add_argument('--batch', action='store_true',
                        help='Disable interactive mode (for automated/batch processing)')
    
    args = parser.parse_args()
    
    # If --batch is specified, disable interactive mode
    if args.batch:
        args.interactive = False
    
    return args

def load_units_table() -> Dict[str, Dict]:
    """Load unit information from AGUR_UNITS_TABLE.csv"""
    units = {}
    units_table_path = Path(UNITS_TABLE_FILE)
    
    if not units_table_path.exists():
        logger.error(f"Units table not found: {units_table_path}")
        sys.exit(1)
    
    with open(units_table_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            units[row['UNIT']] = {
                'chiplet': row['CHIPLET'],
                'owner': row['RELEASE_USER']
            }
    
    logger.info(f"Loaded {len(units)} units from {units_table_path}")
    return units

def parse_release_timestamp(release_dir: str) -> Optional[datetime]:
    """
    Parse timestamp from release directory name.
    
    Formats:
    - {unit}_rbv_*__YYYY_M_D_H_M_S
    - nbu_signoff_*_YYYY_M_D_H_M_S
    """
    # Try to extract timestamp from end of directory name
    # Format: __YYYY_M_D_H_M_S or _YYYY_M_D_H_M_S
    patterns = [
        r'__(\d{4})_(\d{1,2})_(\d{1,2})_(\d{1,2})_(\d{1,2})_(\d{1,2})$',
        r'_(\d{4})_(\d{1,2})_(\d{1,2})_(\d{1,2})_(\d{1,2})_(\d{1,2})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, release_dir)
        if match:
            year, month, day, hour, minute, second = map(int, match.groups())
            try:
                return datetime(year, month, day, hour, minute, second)
            except ValueError:
                continue
    
    return None

def is_release_directory(path: Path) -> bool:
    """Check if a directory looks like a release directory"""
    name = path.name
    
    # Must be a directory
    if not path.is_dir():
        return False
    
    # Skip symlinks
    if path.is_symlink():
        return False
    
    # Must contain logs/block_release.log or match naming pattern
    has_log = (path / 'logs' / 'block_release.log').exists()
    
    # Match typical release patterns
    matches_pattern = bool(re.match(r'^.*_rbv_.*__\d{4}_\d{1,2}_\d{1,2}_\d{1,2}_\d{1,2}_\d{1,2}$', name) or
                           re.match(r'^nbu_signoff_.*_\d{4}_\d{1,2}_\d{1,2}_\d{1,2}_\d{1,2}_\d{1,2}$', name))
    
    return has_log or matches_pattern

def scan_unit_releases(unit: str, unit_info: Dict, age_threshold_days: int) -> List[ReleaseInfo]:
    """
    Scan a single unit directory for old releases.
    
    Args:
        unit: Unit name
        unit_info: Dict with 'chiplet' and 'owner' keys
        age_threshold_days: Age threshold in days
        
    Returns:
        List of ReleaseInfo objects for old releases
    """
    unit_path = Path(RELEASE_BASE_PATH) / unit
    
    if not unit_path.exists():
        logger.warning(f"Unit directory not found: {unit_path}")
        return []
    
    old_releases = []
    threshold_date = datetime.now() - timedelta(days=age_threshold_days)
    
    logger.debug(f"Scanning {unit} ({unit_info['chiplet']})...")
    
    logger.debug(f"  [DEBUG] Unit path: {unit_path}")
    logger.debug(f"  [DEBUG] Age threshold: {age_threshold_days} days")
    logger.debug(f"  [DEBUG] Threshold date: {threshold_date}")
    
    try:
        # Find all symlinks in the unit directory
        for item in unit_path.iterdir():
            logger.debug(f"  [DEBUG] Checking item: {item.name}")
            
            if not is_release_directory(item):
                logger.debug(f"    [DEBUG] Skipped - Not a release directory")
                continue
            
            logger.debug(f"    [DEBUG] Is release directory: YES")
            
            # Parse timestamp
            release_timestamp = parse_release_timestamp(item.name)
            if not release_timestamp:
                logger.debug(f"    [DEBUG] Skipped - Couldn't parse timestamp from: {item.name}")
                continue
            
            # Check age
            age_days = (datetime.now() - release_timestamp).days
            logger.debug(f"    [DEBUG] Release timestamp: {release_timestamp}")
            logger.debug(f"    [DEBUG] Age: {age_days} days (threshold: {age_threshold_days})")
            
            if age_days < age_threshold_days:
                logger.debug(f"    [DEBUG] Skipped - Too young ({age_days} < {age_threshold_days})")
                continue
            
            logger.debug(f"    [DEBUG] ✓ INCLUDED - Old enough ({age_days} >= {age_threshold_days})")
            
            # Create ReleaseInfo (size and symlinks will be filled later)
            # Use resolve() to get canonical path for symlink matching
            release_info = ReleaseInfo(
                unit=unit,
                chiplet=unit_info['chiplet'],
                release_dir=item.name,
                full_path=str(item.resolve()),
                age_days=age_days,
                size_bytes=0,
                size_human='',
                owner=unit_info['owner'],
                release_timestamp=release_timestamp,
                has_symlinks=False,
                log_file_path=str(item / 'logs' / 'block_release.log'),
                folder_owner='',
                log_owner=''
            )
            
            # Get folder owner (current owner from filesystem)
            release_info.folder_owner = get_directory_owner(item)
            logger.debug(f"    [DEBUG] Folder owner: {release_info.folder_owner}")
            
            logger.debug(f"    [DEBUG] Created ReleaseInfo with full_path: {release_info.full_path}")
            
            old_releases.append(release_info)
            logger.debug(f"  Found old release: {item.name} ({age_days} days old)")
    
    except PermissionError as e:
        logger.error(f"Permission denied accessing {unit_path}: {e}")
    except Exception as e:
        logger.error(f"Error scanning {unit_path}: {e}")
    
    return old_releases

def get_symlink_owner(symlink_path: Path) -> str:
    """
    Get the owner of a symlink using ls -l.
    
    Args:
        symlink_path: Path to the symlink
        
    Returns:
        Username of the symlink owner
    """
    try:
        result = subprocess.run(
            ['ls', '-l', str(symlink_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # ls -l output: lrwxrwxrwx 1 username group ... -> target
            parts = result.stdout.split()
            if len(parts) >= 3:
                return parts[2]  # Third field is the owner
        
    except Exception as e:
        logger.debug(f"Error getting symlink owner for {symlink_path}: {e}")
    
    return 'unknown'

def get_directory_owner(dir_path: Path) -> str:
    """
    Get the owner of a directory using ls -ld.
    
    Args:
        dir_path: Path to the directory
        
    Returns:
        Username of the directory owner
    """
    try:
        result = subprocess.run(
            ['ls', '-ld', str(dir_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # ls -ld output: drwxr-xr-x 10 username group ... dirname
            parts = result.stdout.split()
            if len(parts) >= 3:
                return parts[2]  # Third field is the owner
        
    except Exception as e:
        logger.debug(f"Error getting directory owner for {dir_path}: {e}")
    
    return ''

def analyze_unit_symlinks(unit: str) -> Dict[str, List[SymlinkInfo]]:
    """
    Analyze all symlinks in a unit directory and map them to their targets.
    
    Args:
        unit: Unit name
        
    Returns:
        Dict mapping release_path -> List[SymlinkInfo]
    """
    unit_path = Path(RELEASE_BASE_PATH) / unit
    
    if not unit_path.exists():
        return {}
    
    symlink_map = {}
    
    logger.debug(f"  [DEBUG] Analyzing symlinks in {unit}...")
    
    try:
        # Find all symlinks in the unit directory
        for item in unit_path.iterdir():
            if not item.is_symlink():
                continue
            
            try:
                # Resolve the symlink target
                target = item.resolve()
                
                # Get symlink owner
                owner = get_symlink_owner(item)
                
                # Create SymlinkInfo
                symlink_info = SymlinkInfo(
                    symlink_name=item.name,
                    symlink_owner=owner,
                    symlink_path=str(item),
                    target_release=target.name if target.exists() else 'broken'
                )
                
                # Map to target path
                target_str = str(target)
                if target_str not in symlink_map:
                    symlink_map[target_str] = []
                symlink_map[target_str].append(symlink_info)
                
                logger.debug(f"    [DEBUG] Found symlink: {item.name}")
                logger.debug(f"      Symlink path: {str(item)}")
                logger.debug(f"      Target (resolved): {target_str}")
                logger.debug(f"      Target name: {target.name}")
                logger.debug(f"      Owner: {owner}")
                
            except Exception as e:
                logger.debug(f"  Error resolving symlink {item}: {e}")
    
    except PermissionError as e:
        logger.error(f"Permission denied accessing symlinks in {unit_path}: {e}")
    except Exception as e:
        logger.error(f"Error analyzing symlinks in {unit_path}: {e}")
    
    return symlink_map

def calculate_directory_size(path: str) -> Tuple[int, str]:
    """
    Calculate directory size using du command.
    
    Args:
        path: Directory path
        
    Returns:
        Tuple of (size_bytes, human_readable_size)
    """
    try:
        # Use du -sb for bytes, du -sh for human readable
        result_bytes = subprocess.run(
            ['du', '-sb', path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per directory
        )
        
        result_human = subprocess.run(
            ['du', '-sh', path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        size_bytes = 0
        size_human = '0'
        
        if result_bytes.returncode == 0:
            parts = result_bytes.stdout.split()
            if parts:
                size_bytes = int(parts[0])
        
        if result_human.returncode == 0:
            parts = result_human.stdout.split()
            if parts:
                size_human = parts[0]
        
        return size_bytes, size_human
        
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout calculating size for {path}")
        return 0, 'timeout'
    except Exception as e:
        logger.debug(f"Error calculating size for {path}: {e}")
        return 0, 'error'

def calculate_sizes_parallel(releases: List[ReleaseInfo], max_workers: int = 10) -> List[ReleaseInfo]:
    """
    Calculate disk usage for all releases using parallel du commands.
    
    Args:
        releases: List of ReleaseInfo objects
        max_workers: Number of parallel processes
        
    Returns:
        Updated list with size information
    """
    logger.info(f"\nCalculating disk usage (parallel={max_workers})...")
    
    total_bytes = 0
    completed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_release = {
            executor.submit(calculate_directory_size, release.full_path): release
            for release in releases
        }
        
        # Process results as they complete
        for future in as_completed(future_to_release):
            release = future_to_release[future]
            try:
                size_bytes, size_human = future.result()
                release.size_bytes = size_bytes
                release.size_human = size_human
                total_bytes += size_bytes
                completed += 1
                
                if completed % 10 == 0:
                    logger.info(f"  Progress: {completed}/{len(releases)} releases calculated")
                
                logger.debug(f"  {release.release_dir}: {size_human}")
                
            except Exception as e:
                logger.error(f"Error processing {release.release_dir}: {e}")
                release.size_bytes = 0
                release.size_human = 'error'
    
    # Convert total to human readable
    total_human = format_bytes(total_bytes)
    logger.info(f"  Total reclaimable space: {total_human}")
    
    return releases

def extract_owner_from_log(log_file_path: str) -> Optional[str]:
    """
    Extract owner from block_release.log file.
    
    Looks for line like: "-I- [timestamp] USER: username"
    
    Args:
        log_file_path: Path to block_release.log
        
    Returns:
        Username or None if not found
    """
    if not os.path.exists(log_file_path):
        return None
    
    try:
        with open(log_file_path, 'r', errors='ignore') as f:
            for line in f:
                if 'USER:' in line:
                    # Format: -I- [timestamp] USER: username
                    match = re.search(r'USER:\s+(\w+)', line)
                    if match:
                        return match.group(1)
                    break  # USER line is usually near the top
    except Exception as e:
        logger.debug(f"Error reading log file {log_file_path}: {e}")
    
    return None

def enrich_releases_with_log_data(releases: List[ReleaseInfo]) -> List[ReleaseInfo]:
    """
    Extract owner information from block_release.log files.
    
    Sets log_owner field and updates owner to folder_owner (priority).
    This ensures emails go to current owner (folder_owner) with previous owner (log_owner) CC'd.
    
    Args:
        releases: List of ReleaseInfo objects
        
    Returns:
        Updated list with owner information from logs
    """
    logger.info("\nExtracting owner information from logs...")
    
    log_owner_count = 0
    folder_owner_count = 0
    
    for release in releases:
        # Extract log owner (original release creator)
        log_owner = extract_owner_from_log(release.log_file_path)
        if log_owner:
            release.log_owner = log_owner
            log_owner_count += 1
        
        # Set primary owner to folder owner (current owner) - PRIORITY
        if release.folder_owner:
            if release.folder_owner != release.owner:
                logger.debug(f"  {release.release_dir}: Owner {release.owner} -> {release.folder_owner} (folder owner)")
                folder_owner_count += 1
            release.owner = release.folder_owner
        elif log_owner:
            # Fallback to log owner if no folder owner detected
            if log_owner != release.owner:
                logger.debug(f"  {release.release_dir}: Owner {release.owner} -> {log_owner} (log owner)")
            release.owner = log_owner
        # else: keep default owner from AGUR_UNITS_TABLE.csv
    
    if log_owner_count > 0:
        logger.info(f"  Extracted {log_owner_count} log owners (release creators)")
    if folder_owner_count > 0:
        logger.info(f"  Updated {folder_owner_count} owners to folder owner (current owner)")
    
    return releases

def generate_csv_report(releases: List[ReleaseInfo], output_file: Path):
    """Generate detailed CSV report of all old releases"""
    logger.info(f"  Writing CSV report: {output_file}")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Unit', 'Chiplet', 'Release Directory', 'Age (days)', 'Size', 
            'Owner', 'Release Timestamp', 'Has Symlinks', 'Symlink Names', 
            'Symlink Owners', 'Requires Coordination', 'Recommendation'
        ])
        
        for release in sorted(releases, key=lambda r: r.size_bytes, reverse=True):
            symlink_names = ','.join(s.symlink_name for s in release.symlink_infos) if release.symlink_infos else 'None'
            symlink_owners = ','.join(set(s.symlink_owner for s in release.symlink_infos)) if release.symlink_infos else 'None'
            
            if release.requires_coordination:
                recommendation = 'Coordinate with symlink owners first'
            elif release.has_symlinks:
                recommendation = 'Remove symlinks first'
            else:
                recommendation = 'Safe to delete'
            
            writer.writerow([
                release.unit,
                release.chiplet,
                release.release_dir,
                release.age_days,
                release.size_human,
                release.owner,
                release.release_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if release.has_symlinks else 'No',
                symlink_names,
                symlink_owners,
                'Yes' if release.requires_coordination else 'No',
                recommendation
            ])

def generate_dashboard_report(releases: List[ReleaseInfo], output_file: Path):
    """Generate interactive multi-tab dashboard HTML report with Chart.js visualizations"""
    logger.info(f"  Writing Dashboard report: {output_file}")
    
    # Load approval state to check which releases have been emailed
    output_dir = output_file.parent
    state = load_approval_state(output_dir)
    emailed_releases = state.get('emailed_releases', {})
    
    # Calculate all metrics
    age_dist = calculate_age_distribution(releases)
    chiplet_breakdown = calculate_chiplet_breakdown(releases)
    coord_stats = calculate_coordination_stats(releases)
    top_consumers = get_top_consumers(releases, 10)
    chiplet_groups = group_by_chiplet_detailed(releases)
    owner_groups = group_by_owner_detailed(releases)
    
    # Calculate totals
    total_releases = len(releases)
    total_size_bytes = sum(r.size_bytes for r in releases)
    total_size_human = format_bytes(total_size_bytes)
    
    # Calculate disk utilization - GET ACTUAL VALUES DYNAMICALLY
    usage_pct, total_capacity_tb, current_used_tb, _ = get_actual_disk_usage(RELEASE_BASE_PATH)
    current_utilization = usage_pct
    freed_tb = total_size_bytes / (1024**4)
    new_used_tb = current_used_tb - freed_tb
    new_utilization = (new_used_tb / total_capacity_tb) * 100
    
    # Prepare data for Chart.js
    import json
    age_labels = list(age_dist.keys())
    age_values = list(age_dist.values())
    
    chiplet_labels = list(chiplet_breakdown.keys())
    chiplet_sizes = [chiplet_breakdown[c]['size_bytes']/(1024**3) for c in chiplet_labels]  # GB
    chiplet_counts = [chiplet_breakdown[c]['count'] for c in chiplet_labels]
    
    # Build per-unit-per-owner summary for "By Unit" tab
    unit_owner_summary = {}
    for release in releases:
        key = (release.unit, release.owner)
        if key not in unit_owner_summary:
            unit_owner_summary[key] = {
                'unit': release.unit,
                'chiplet': release.chiplet,
                'owner': release.owner,
                'count': 0,
                'size_bytes': 0,
                'symlinks': {},
                'release_dirs': []
            }
        unit_owner_summary[key]['count'] += 1
        unit_owner_summary[key]['size_bytes'] += release.size_bytes
        unit_owner_summary[key]['release_dirs'].append(release.release_dir)
        for sym in release.symlink_infos:
            unit_owner_summary[key]['symlinks'][sym.symlink_name] = sym.symlink_owner
    
    # Build unit table by chiplet (expandable sections) for "By Unit" tab with per-release checkboxes
    unit_by_chiplet_sections = ''
    
    # Group releases by chiplet
    chiplet_releases_map = {}
    for release in releases:
        if release.chiplet not in chiplet_releases_map:
            chiplet_releases_map[release.chiplet] = []
        chiplet_releases_map[release.chiplet].append(release)
    
    # Build sections for each chiplet
    for chiplet_name in sorted(chiplet_releases_map.keys()):
        chiplet_releases = chiplet_releases_map[chiplet_name]
        chiplet_total_size = sum(r.size_bytes for r in chiplet_releases)
        chiplet_count = len(chiplet_releases)
        
        # Build table rows for this chiplet - ONE ROW PER RELEASE
        chiplet_unit_rows = ''
        for release in sorted(chiplet_releases, key=lambda x: (x.unit, x.release_timestamp)):
            release_id = get_release_id(release)
            
            # Check if this release has been emailed
            is_emailed = release_id in emailed_releases
            row_class = ' class="emailed-release"' if is_emailed else ''
            
            # Determine badge based on email history
            emailed_badge = ''
            if is_emailed:
                emailed_info = emailed_releases[release_id]
                email_history = emailed_info.get('email_history', [])
                email_count = len(email_history)
                
                if email_count > 0:
                    # Get test_mode from most recent email
                    last_email = email_history[-1]
                    is_test_mode = last_email.get('test_mode', False)
                    
                    # Show count badge (e.g., "✉ 3x")
                    if is_test_mode:
                        emailed_badge = f'<span class="emailed-badge-test">✉ {email_count}x</span>'
                    else:
                        emailed_badge = f'<span class="emailed-badge">✉ {email_count}x</span>'
            
            # Format symlinks for this specific release
            symlinks_list = []
            for sym in release.symlink_infos:
                symlinks_list.append(f"{sym.symlink_name} <span style='color: #666;'>({sym.symlink_owner})</span>")
            symlinks_html = '<br/>'.join(symlinks_list) if symlinks_list else '<span style="color: #999;">None</span>'
            
            chiplet_unit_rows += f'''
            <tr data-release-id="{release_id}" data-chiplet="{release.chiplet}"{row_class}>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; text-align: center;">
                    <input type="checkbox" class="approval-checkbox" data-release-id="{release_id}" />
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold;">{release.unit}{emailed_badge}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{release.owner}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-family: monospace; font-size: 11px; max-width: 400px; word-break: break-all;">{release.release_dir}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; text-align: center;">{release.age_days}d</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-size: 12px; max-width: 250px; word-break: break-all;">{symlinks_html}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; text-align: right; font-weight: bold;">{release.size_human}</td>
            </tr>'''
        
        # Build chiplet section
        unit_by_chiplet_sections += f'''
        <div class="chiplet-section">
            <div class="chiplet-header" onclick="toggleChiplet('unit-{chiplet_name}')">
                <span class="toggle-icon" id="icon-unit-{chiplet_name}">▼</span>
                <strong>{chiplet_name}</strong>
                <span style="margin-left: 20px; color: #666;">
                    {chiplet_count} releases | {format_bytes(chiplet_total_size)}
                </span>
            </div>
            <div class="chiplet-content" id="content-unit-{chiplet_name}">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #dee2e6; width: 50px;">Approve</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Unit</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Owner</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Release Directory</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #dee2e6;">Age</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Symlinks (User)</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #dee2e6;">Size</th>
                        </tr>
                    </thead>
                    <tbody>
                        {chiplet_unit_rows}
                    </tbody>
                </table>
            </div>
        </div>'''
    
    # Build chiplet sections HTML for "By Chiplet" tab
    chiplet_sections = ''
    for chiplet_name in sorted(chiplet_groups.keys()):
        chiplet_releases = chiplet_groups[chiplet_name]
        chiplet_total_size = sum(r.size_bytes for r in chiplet_releases)
        chiplet_count = len(chiplet_releases)
        
        # Group by unit within chiplet
        unit_map = {}
        for r in chiplet_releases:
            if r.unit not in unit_map:
                unit_map[r.unit] = []
            unit_map[r.unit].append(r)
        
        unit_rows = ''
        for unit_name in sorted(unit_map.keys()):
            unit_releases = unit_map[unit_name]
            unit_size = sum(r.size_bytes for r in unit_releases)
            unit_count = len(unit_releases)
            owners = ', '.join(sorted(set(r.owner for r in unit_releases)))
            
            unit_rows += f'''
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{unit_name}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{owners}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{unit_count}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">{format_bytes(unit_size)}</td>
            </tr>'''
        
        chiplet_sections += f'''
        <div class="chiplet-section">
            <div class="chiplet-header" onclick="toggleChiplet('{chiplet_name}')">
                <span class="toggle-icon" id="icon-{chiplet_name}">▼</span>
                <strong>{chiplet_name}</strong>
                <span style="margin-left: 20px; color: #666;">
                    {chiplet_count} releases | {format_bytes(chiplet_total_size)}
                </span>
            </div>
            <div class="chiplet-content" id="content-{chiplet_name}">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Unit</th>
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6;">Owners</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #dee2e6;"># Releases</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #dee2e6;">Total Size</th>
                        </tr>
                    </thead>
                    <tbody>
                        {unit_rows}
                    </tbody>
                </table>
            </div>
        </div>'''
    
    # Build owner rows for "By Owner" tab
    owner_rows = ''
    for owner_email in sorted(owner_groups.keys()):
        owner_data = owner_groups[owner_email]
        chiplets = ', '.join(sorted(owner_data['chiplets']))
        units = ', '.join(sorted(owner_data['units']))
        
        owner_rows += f'''
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-weight: bold;">{owner_email}</td>
            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{chiplets}</td>
            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{units}</td>
            <td style="padding: 10px; border-bottom: 1px solid #dee2e6; text-align: center;">{len(owner_data['releases'])}</td>
            <td style="padding: 10px; border-bottom: 1px solid #dee2e6; text-align: right; font-weight: bold;">{format_bytes(owner_data['total_size'])}</td>
        </tr>'''
    
    # Build complete HTML dashboard
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AGUR Release Cleanup Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .dashboard-container {{
            max-width: 95%;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            overflow-x: auto;
        }}
        .tab {{
            padding: 15px 25px;
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 15px;
            font-weight: 500;
            color: #6c757d;
            transition: all 0.3s;
            white-space: nowrap;
        }}
        .tab:hover {{
            background: #e9ecef;
            color: #495057;
        }}
        .tab.active {{
            background: white;
            color: #0d47a1;
            border-bottom: 3px solid #0d47a1;
        }}
        .tab-content {{
            display: none;
            padding: 30px;
            animation: fadeIn 0.3s;
        }}
        .tab-content.active {{
            display: block;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .stat-card.green {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .stat-card.orange {{
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        }}
        .stat-card.blue {{
            background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: 700;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        .chart-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 18px;
            font-weight: 600;
            color: #212529;
            margin-bottom: 20px;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-size: 13px;
            font-weight: 600;
            color: #495057;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #dee2e6;
        }}
        td {{
            padding: 10px;
            font-size: 13px;
            color: #212529;
            border-bottom: 1px solid #f1f3f5;
            vertical-align: top;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .alert {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .alert strong {{
            color: #856404;
            font-size: 16px;
        }}
        .chiplet-section {{
            margin: 15px 0;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }}
        .chiplet-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
            user-select: none;
        }}
        .chiplet-header:hover {{
            background: #e9ecef;
        }}
        .chiplet-content {{
            padding: 20px;
            background: white;
        }}
        .chiplet-content.collapsed {{
            display: none;
        }}
        .toggle-icon {{
            display: inline-block;
            margin-right: 10px;
            transition: transform 0.3s;
            font-size: 12px;
        }}
        .toggle-icon.collapsed {{
            transform: rotate(-90deg);
        }}
        .approval-panel {{
            background: #fff;
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .approval-stats {{
            display: flex;
            gap: 30px;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .approval-stats span {{
            color: #666;
        }}
        .approval-stats strong {{
            color: #212529;
            font-size: 20px;
        }}
        .approval-actions {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .status-message {{
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            display: none;
        }}
        .status-message.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }}
        .status-message.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }}
        .approval-checkbox {{
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        .emailed-release {{
            background-color: #d4edda !important;
            border-left: 4px solid #28a745 !important;
        }}
        .emailed-badge {{
            display: inline-block;
            padding: 2px 8px;
            background-color: #28a745;
            color: white;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .emailed-badge-test {{
            display: inline-block;
            padding: 2px 8px;
            background-color: #fd7e14;
            color: white;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .section-title {{
            font-size: 24px;
            color: #212529;
            margin: 30px 0 20px 0;
            font-weight: 600;
            border-bottom: 3px solid #0d47a1;
            padding-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🗂️ AGUR Release Cleanup Dashboard</h1>
            <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Age Threshold: 90 days</div>
        </div>
        
        <div class="approval-panel">
            <div class="approval-stats">
                <span>Total Releases: <strong id="total-releases">0</strong></span>
                <span>Approved: <strong id="approved-count" style="color: #28a745;">0</strong></span>
                <span>Emailed: <strong id="emailed-count" style="color: #17a2b8;">0</strong></span>
                <span>Pending: <strong id="pending-count" style="color: #ffc107;">0</strong></span>
            </div>
            <div class="approval-actions">
                <button id="select-all-btn" class="btn btn-secondary">Select All Visible</button>
                <button id="clear-all-btn" class="btn btn-secondary">Clear All Selections</button>
                <button id="send-emails-btn" class="btn btn-primary" disabled>Send Emails for Approved Releases</button>
            </div>
            <div id="status-message" class="status-message"></div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('summary')">📊 Summary</button>
            <button class="tab" onclick="switchTab('chiplet')">🔧 By Chiplet</button>
            <button class="tab" onclick="switchTab('unit')">📦 By Unit</button>
            <button class="tab" onclick="switchTab('owner')">👤 By Owner</button>
        </div>
        
        <!-- SUMMARY TAB -->
        <div id="tab-summary" class="tab-content active">
            <div class="alert">
                <strong>⚠️ Critical Disk Usage Alert</strong><br/>
                AGUR Release Area: 90% capacity (108T/120T used). Immediate action required to prevent workflow disruption.
            </div>
            
            <div class="stats-grid">
                <div class="stat-card orange">
                    <div class="stat-label">Old Releases</div>
                    <div class="stat-value">{total_releases}</div>
                </div>
                <div class="stat-card blue">
                    <div class="stat-label">Reclaimable Space</div>
                    <div class="stat-value">{total_size_human}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Current Utilization</div>
                    <div class="stat-value">{current_utilization}%</div>
                </div>
                <div class="stat-card green">
                    <div class="stat-label">After Cleanup</div>
                    <div class="stat-value">{new_utilization:.1f}%</div>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">Release Age Distribution</div>
                    <canvas id="ageChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Size by Chiplet</div>
                    <canvas id="chipletChart"></canvas>
                </div>
            </div>
            
            <div class="section-title">Top 10 Space Consumers</div>
            <table>
                <thead>
                    <tr>
                        <th>Unit</th>
                        <th>Owner</th>
                        <th>Chiplet</th>
                        <th style="text-align: center;"># Releases</th>
                        <th style="text-align: right;">Total Size</th>
                    </tr>
                </thead>
                <tbody>'''
    
    for consumer in top_consumers:
        html_content += f'''
                    <tr>
                        <td style="font-weight: bold;">{consumer['unit']}</td>
                        <td>{consumer['owner']}</td>
                        <td>{consumer['chiplet']}</td>
                        <td style="text-align: center;">{consumer['count']}</td>
                        <td style="text-align: right; font-weight: bold; color: #dc3545;">{format_bytes(consumer['size_bytes'])}</td>
                    </tr>'''
    
    html_content += f'''
                </tbody>
            </table>
            
            <div style="margin-top: 30px; padding: 20px; background: #e7f3ff; border-radius: 8px; border-left: 4px solid #2196F3;">
                <h3 style="color: #1976D2; margin-bottom: 10px;">📈 Coordination Statistics</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="padding: 8px 0; font-size: 14px;">✅ <strong>No Symlinks:</strong> {coord_stats['no_symlinks']} releases (safe to delete)</li>
                    <li style="padding: 8px 0; font-size: 14px;">🔗 <strong>Self-Owned Symlinks:</strong> {coord_stats['self_symlinks']} releases (remove symlinks first)</li>
                    <li style="padding: 8px 0; font-size: 14px;">⚠️ <strong>Coordination Needed:</strong> {coord_stats['coordination_needed']} releases (multi-user action required)</li>
                </ul>
            </div>
        </div>
        
        <!-- BY CHIPLET TAB -->
        <div id="tab-chiplet" class="tab-content">
            <h2 class="section-title">Releases Grouped by Chiplet</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">
                Click on a chiplet to expand/collapse details. Each section shows units and their space consumption.
            </p>
            {chiplet_sections}
        </div>
        
        <!-- BY UNIT TAB -->
        <div id="tab-unit" class="tab-content">
            <h2 class="section-title">Detailed Unit Summary by Chiplet</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">
                Click on a chiplet to expand/collapse details. Each section shows units with their owners, release areas, and symlinks.
            </p>
            
            <div style="background: #e7f3ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #2196F3;">
                <strong style="color: #1976D2;">📊 Overall Summary:</strong>
                <span style="color: #1976D2; margin-left: 20px;">
                    <strong>{total_releases}</strong> releases | 
                    <strong style="color: #dc3545;">{total_size_human}</strong> reclaimable
                </span>
                <br/>
                <span style="color: #1976D2;">
                    Impact: Current {current_utilization}% ({current_used_tb}TB/{total_capacity_tb}TB) → 
                    After cleanup: <strong>{new_utilization:.1f}%</strong> (~{new_used_tb:.1f}TB/{total_capacity_tb}TB)
                </span>
            </div>
            
            {unit_by_chiplet_sections}
        </div>
        
        <!-- BY OWNER TAB -->
        <div id="tab-owner" class="tab-content">
            <h2 class="section-title">Owner-Centric View</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">
                Aggregated view showing each owner's total impact across all units and chiplets.
            </p>
            <table>
                <thead>
                    <tr>
                        <th style="width: 25%;">Owner Email</th>
                        <th style="width: 20%;">Chiplets</th>
                        <th style="width: 35%;">Units</th>
                        <th style="width: 10%; text-align: center;"># Releases</th>
                        <th style="width: 10%; text-align: right;">Total Size</th>
                    </tr>
                </thead>
                <tbody>
                    {owner_rows}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // API base URL
        const API_BASE = 'http://localhost:5000/api';
        
        // Load approval state on page load
        async function loadApprovalState() {{
            try {{
                const response = await fetch(`${{API_BASE}}/releases`);
                const data = await response.json();
                
                if (data.success) {{
                    // Update checkboxes based on loaded state
                    data.releases.forEach(release => {{
                        const checkbox = document.querySelector(`input[data-release-id="${{release.id}}"]`);
                        if (checkbox) {{
                            checkbox.checked = release.approved;
                        }}
                    }});
                    
                    // Update stats
                    await updateApprovalStats();
                }}
            }} catch (error) {{
                console.error('Error loading approval state:', error);
                showStatus('Error connecting to server. Make sure you ran with --interactive flag.', 'error');
            }}
        }}
        
        // Toggle approval for a release
        async function toggleApproval(releaseId, approved) {{
            try {{
                const response = await fetch(`${{API_BASE}}/approve`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ release_id: releaseId, approved: approved }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    await updateApprovalStats();
                }}
            }} catch (error) {{
                console.error('Error toggling approval:', error);
                showStatus('Error updating approval status', 'error');
            }}
        }}
        
        // Apply green highlighting to specific releases dynamically
        function applyEmailedStyling(releaseIds, isTestMode) {{
            releaseIds.forEach(releaseId => {{
                // Find the table row
                const row = document.querySelector(`tr[data-release-id="${{releaseId}}"]`);
                if (!row) return;
                
                // Add green background class
                row.classList.add('emailed-release');
                
                // Find the unit name cell (second td)
                const unitCell = row.querySelectorAll('td')[1];
                if (!unitCell) return;
                
                // Check if badge already exists
                const existingBadge = unitCell.querySelector('.emailed-badge, .emailed-badge-test');
                if (existingBadge) {{
                    // Badge exists - increment count
                    const match = existingBadge.textContent.match(/(\d+)x/);
                    if (match) {{
                        const currentCount = parseInt(match[1]);
                        const newCount = currentCount + 1;
                        existingBadge.textContent = `✉ ${{newCount}}x`;
                        // Update class if test mode changed
                        if (isTestMode) {{
                            existingBadge.className = 'emailed-badge-test';
                        }} else {{
                            existingBadge.className = 'emailed-badge';
                        }}
                    }}
                    return;
                }}
                
                // Create and insert new badge with count 1
                const badge = document.createElement('span');
                if (isTestMode) {{
                    badge.className = 'emailed-badge-test';
                    badge.textContent = '✉ 1x';
                }} else {{
                    badge.className = 'emailed-badge';
                    badge.textContent = '✉ 1x';
                }}
                unitCell.appendChild(badge);
            }});
        }}
        
        // Update approval statistics
        async function updateApprovalStats() {{
            try {{
                const response = await fetch(`${{API_BASE}}/status`);
                const data = await response.json();
                
                if (data.success) {{
                    // Count only releases that are visible in the current dashboard (not filtered out)
                    const allCheckboxes = Array.from(document.querySelectorAll('.approval-checkbox'));
                    const visibleReleaseIds = new Set(allCheckboxes.map(cb => cb.dataset.releaseId));
                    
                    // Load approval state to check which visible releases are approved
                    const stateResponse = await fetch(`${{API_BASE}}/releases`);
                    const stateData = await stateResponse.json();
                    
                    let visibleApprovedCount = 0;
                    let visibleEmailedCount = 0;
                    
                    if (stateData.success) {{
                        stateData.releases.forEach(release => {{
                            if (visibleReleaseIds.has(release.id)) {{
                                if (release.approved) visibleApprovedCount++;
                                if (release.emailed) visibleEmailedCount++;
                            }}
                        }});
                    }}
                    
                    const totalVisible = allCheckboxes.length;
                    const pendingVisible = totalVisible - visibleApprovedCount;
                    
                    // Update counters with visible release counts
                    document.getElementById('total-releases').textContent = totalVisible;
                    document.getElementById('approved-count').textContent = visibleApprovedCount;
                    document.getElementById('emailed-count').textContent = visibleEmailedCount;
                    document.getElementById('pending-count').textContent = pendingVisible;
                    
                    // Enable/disable send button based on visible approved releases
                    const sendBtn = document.getElementById('send-emails-btn');
                    sendBtn.disabled = visibleApprovedCount === 0;
                }}
            }} catch (error) {{
                console.error('Error updating stats:', error);
            }}
        }}
        
        // Send emails for approved releases
        async function sendApprovedEmails() {{
            if (!confirm('Send emails for all approved releases? This action cannot be undone.')) {{
                return;
            }}
            
            showStatus('Sending emails...', 'success');
            document.getElementById('send-emails-btn').disabled = true;
            
            try {{
                const response = await fetch(`${{API_BASE}}/send_emails`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{}})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    const testModeMsg = data.test_mode ? ' (TEST MODE - emails sent to current user only)' : '';
                    let message = `Success! Emails sent for ${{data.total_sent}} release(s)${{testModeMsg}}`;
                    
                    if (data.resends > 0) {{
                        message += `\\n(${{data.new_sends}} new, ${{data.resends}} resent)`;
                    }}
                    
                    // Apply green highlighting and update counts immediately
                    if (data.newly_emailed_ids && data.newly_emailed_ids.length > 0) {{
                        applyEmailedStyling(data.newly_emailed_ids, data.test_mode);
                    }}
                    
                    showStatus(message, 'success');
                    await updateApprovalStats();  // Update the emailed count
                }} else {{
                    showStatus(`Error: ${{data.error}}`, 'error');
                    document.getElementById('send-emails-btn').disabled = false;
                }}
            }} catch (error) {{
                console.error('Error sending emails:', error);
                showStatus('Error sending emails: ' + error.message, 'error');
                document.getElementById('send-emails-btn').disabled = false;
            }}
        }}
        
        // Select all visible releases in current tab
        async function selectAllVisible() {{
            const activeTab = document.querySelector('.tab-content.active');
            if (!activeTab) {{
                return;
            }}
            
            const checkboxes = Array.from(activeTab.querySelectorAll('.approval-checkbox'));
            const unchecked = checkboxes.filter(cb => !cb.checked);
            
            if (unchecked.length === 0) {{
                showStatus('All visible releases are already approved', 'success');
                return;
            }}
            
            // Disable buttons during operation
            document.getElementById('select-all-btn').disabled = true;
            document.getElementById('clear-all-btn').disabled = true;
            showStatus(`Approving ${{unchecked.length}} releases...`, 'success');
            
            let successCount = 0;
            let failCount = 0;
            
            // Process checkboxes sequentially to avoid overwhelming the server
            for (const cb of unchecked) {{
                cb.checked = true;
                try {{
                    await toggleApproval(cb.dataset.releaseId, true);
                    successCount++;
                    
                    // Small delay to avoid overwhelming the server
                    if (successCount % 10 === 0) {{
                        showStatus(`Progress: ${{successCount}}/${{unchecked.length}} approved...`, 'success');
                    }}
                }} catch (error) {{
                    console.error('Error approving release:', cb.dataset.releaseId, error);
                    failCount++;
                    cb.checked = false;  // Uncheck if failed
                }}
            }}
            
            // Re-enable buttons
            document.getElementById('select-all-btn').disabled = false;
            document.getElementById('clear-all-btn').disabled = false;
            
            if (failCount === 0) {{
                showStatus(`Success! Approved ${{successCount}} releases`, 'success');
            }} else {{
                showStatus(`Approved ${{successCount}}, Failed ${{failCount}}. Please try again for failed items.`, 'error');
            }}
        }}
        
        // Clear all selections
        async function clearAllSelections() {{
            if (!confirm('Clear all approval selections?')) {{
                return;
            }}
            
            const checkboxes = Array.from(document.querySelectorAll('.approval-checkbox'));
            const checked = checkboxes.filter(cb => cb.checked);
            
            if (checked.length === 0) {{
                showStatus('No releases are currently approved', 'success');
                return;
            }}
            
            // Disable buttons during operation
            document.getElementById('select-all-btn').disabled = true;
            document.getElementById('clear-all-btn').disabled = true;
            showStatus(`Clearing ${{checked.length}} approvals...`, 'success');
            
            let successCount = 0;
            let failCount = 0;
            
            // Process checkboxes sequentially
            for (const cb of checked) {{
                cb.checked = false;
                try {{
                    await toggleApproval(cb.dataset.releaseId, false);
                    successCount++;
                    
                    // Update progress
                    if (successCount % 10 === 0) {{
                        showStatus(`Progress: ${{successCount}}/${{checked.length}} cleared...`, 'success');
                    }}
                }} catch (error) {{
                    console.error('Error clearing approval:', cb.dataset.releaseId, error);
                    failCount++;
                    cb.checked = true;  // Recheck if failed
                }}
            }}
            
            // Re-enable buttons
            document.getElementById('select-all-btn').disabled = false;
            document.getElementById('clear-all-btn').disabled = false;
            
            if (failCount === 0) {{
                showStatus(`Success! Cleared ${{successCount}} approvals`, 'success');
            }} else {{
                showStatus(`Cleared ${{successCount}}, Failed ${{failCount}}. Please try again for failed items.`, 'error');
            }}
        }}
        
        // Show status message
        function showStatus(message, type) {{
            const statusDiv = document.getElementById('status-message');
            statusDiv.textContent = message;
            statusDiv.className = `status-message ${{type}}`;
            
            if (type === 'success') {{
                setTimeout(() => {{
                    statusDiv.style.display = 'none';
                }}, 5000);
            }}
        }}
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', async () => {{
            // Load approval state
            await loadApprovalState();
            
            // Add event listeners to checkboxes
            document.querySelectorAll('.approval-checkbox').forEach(checkbox => {{
                checkbox.addEventListener('change', (e) => {{
                    toggleApproval(e.target.dataset.releaseId, e.target.checked);
                }});
            }});
            
            // Add event listeners to buttons
            document.getElementById('select-all-btn').addEventListener('click', selectAllVisible);
            document.getElementById('clear-all-btn').addEventListener('click', clearAllSelections);
            document.getElementById('send-emails-btn').addEventListener('click', sendApprovedEmails);
        }});
        
        // Tab switching
        function switchTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // Chiplet expand/collapse
        function toggleChiplet(chipletName) {{
            const content = document.getElementById('content-' + chipletName);
            const icon = document.getElementById('icon-' + chipletName);
            
            if (content.classList.contains('collapsed')) {{
                content.classList.remove('collapsed');
                icon.classList.remove('collapsed');
                icon.textContent = '▼';
            }} else {{
                content.classList.add('collapsed');
                icon.classList.add('collapsed');
                icon.textContent = '▶';
            }}
        }}
        
        // Chart.js visualizations
        const ageCtx = document.getElementById('ageChart').getContext('2d');
        new Chart(ageCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(age_labels)},
                datasets: [{{
                    label: 'Number of Releases',
                    data: {json.dumps(age_values)},
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{ display: false }},
                    title: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ precision: 0 }}
                    }}
                }}
            }}
        }});
        
        const chipletCtx = document.getElementById('chipletChart').getContext('2d');
        new Chart(chipletCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(chiplet_labels)},
                datasets: [{{
                    label: 'Size (GB)',
                    data: {json.dumps(chiplet_sizes)},
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)',
                        'rgba(199, 199, 199, 0.8)'
                    ],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'right'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"  Dashboard generated with {len(chiplet_groups)} chiplets, {len(unit_owner_summary)} unit-owner pairs, {len(owner_groups)} owners")

def generate_markdown_summary(owner_recommendations: Dict[str, OwnerRecommendation], 
                              releases: List[ReleaseInfo], 
                              output_file: Path,
                              age_threshold: int):
    """Generate markdown summary report"""
    logger.info(f"  Writing Markdown summary: {output_file}")
    
    total_size = sum(r.size_bytes for r in releases)
    total_releases = len(releases)
    coordination_needed = sum(1 for r in releases if r.requires_coordination)
    protected_releases = sum(1 for r in releases if r.has_symlinks)
    
    # Group by chiplet
    chiplet_stats = {}
    for release in releases:
        if release.chiplet not in chiplet_stats:
            chiplet_stats[release.chiplet] = {'count': 0, 'size': 0}
        chiplet_stats[release.chiplet]['count'] += 1
        chiplet_stats[release.chiplet]['size'] += release.size_bytes
    
    with open(output_file, 'w') as f:
        f.write(f"# AGUR Release Area Cleanup Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Age Threshold**: {age_threshold} days  \n")
        f.write(f"**Disk Usage**: 90% (108T/120T) - **CRITICAL**\n\n")
        
        f.write(f"## Overview\n\n")
        f.write(f"- **Total Old Releases**: {total_releases}\n")
        f.write(f"- **Total Reclaimable Space**: {format_bytes(total_size)}\n")
        f.write(f"- **Protected by Symlinks**: {protected_releases} releases\n")
        f.write(f"- **Require Coordination**: {coordination_needed} releases\n")
        f.write(f"- **Unique Owners**: {len(owner_recommendations)}\n\n")
        
        f.write(f"## Impact\n\n")
        current_usage = 90
        freed_percent = (total_size / (120 * 1024**4)) * 100  # 120TB total
        new_usage = current_usage - freed_percent
        f.write(f"If all old releases are removed:\n")
        f.write(f"- Current usage: **{current_usage}%** (CRITICAL)\n")
        f.write(f"- After cleanup: **~{new_usage:.1f}%** (estimated)\n")
        f.write(f"- Space freed: **{format_bytes(total_size)}** (~{freed_percent:.1f}% of total)\n\n")
        
        f.write(f"## By Chiplet\n\n")
        f.write(f"| Chiplet | Releases | Reclaimable Space | Manager |\n")
        f.write(f"|---------|----------|-------------------|----------|\n")
        for chiplet in sorted(chiplet_stats.keys()):
            stats = chiplet_stats[chiplet]
            manager = CHIPLET_MANAGERS.get(chiplet, 'N/A')
            f.write(f"| {chiplet} | {stats['count']} | {format_bytes(stats['size'])} | {manager} |\n")
        f.write(f"\n")
        
        f.write(f"## By Owner\n\n")
        f.write(f"| Owner | Releases | Units | Reclaimable Space | Coordination |\n")
        f.write(f"|-------|----------|-------|-------------------|---------------|\n")
        
        sorted_owners = sorted(owner_recommendations.items(), 
                              key=lambda x: x[1].total_size_bytes, 
                              reverse=True)
        
        for owner_email, rec in sorted_owners:
            coord = 'Required' if any(r.requires_coordination for r in rec.releases) else 'No'
            f.write(f"| {owner_email} | {rec.release_count} | {rec.unit_count} | {rec.total_size_human} | {coord} |\n")
        f.write(f"\n")
        
        f.write(f"## Top 10 Largest Releases\n\n")
        f.write(f"| Unit | Release Directory | Age | Size | Owner | Has Symlinks |\n")
        f.write(f"|------|-------------------|-----|------|-------|---------------|\n")
        
        top_releases = sorted(releases, key=lambda r: r.size_bytes, reverse=True)[:10]
        for release in top_releases:
            symlinks = 'Yes' if release.has_symlinks else 'No'
            f.write(f"| {release.unit} | {release.release_dir[:50]}... | {release.age_days}d | {release.size_human} | {release.owner} | {symlinks} |\n")
        f.write(f"\n")
        
        f.write(f"## Next Steps\n\n")
        f.write(f"1. **Review Reports**: Check the detailed CSV report for all releases\n")
        f.write(f"2. **Owner Notifications**: Emails have been sent to all unit owners\n")
        f.write(f"3. **Coordination**: {coordination_needed} releases require multi-user coordination\n")
        f.write(f"4. **Cleanup**: Owners must manually execute deletion commands\n")
        f.write(f"5. **Verification**: Monitor disk usage after cleanup actions\n\n")
        
        f.write(f"## Safety Notes\n\n")
        f.write(f"- This utility is **analysis-only** - it never deletes anything\n")
        f.write(f"- All deletions must be performed manually by unit owners\n")
        f.write(f"- Symlink coordination is critical to avoid broken links\n")
        f.write(f"- Always verify symlinks before deleting releases\n")

def load_logo_base64() -> str:
    """Load logo and encode as base64 for email embedding"""
    try:
        if os.path.exists(LOGO_PATH):
            with open(LOGO_PATH, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode('utf-8')
                if len(logo_data) < 500000:  # Only if less than 500KB encoded
                    return logo_data
    except Exception as e:
        logger.debug(f"Could not load logo: {e}")
    return ''

def build_email_html(recommendation: OwnerRecommendation, test_mode: bool = False) -> str:
    """
    Build HTML email for cleanup recommendations.
    
    Args:
        recommendation: OwnerRecommendation object
        test_mode: If True, add test mode banner
        
    Returns:
        HTML string for email body
    """
    logo_data = load_logo_base64()
    
    # Build logo cell
    logo_cell = ''
    if logo_data:
        logo_cell = f'''
                        <td style="width: 100px; text-align: center; vertical-align: middle; border-right: 2px solid rgba(255,255,255,0.3); padding: 0 10px;">
                            <img src="data:image/png;base64,{logo_data}" alt="" width="80" height="80" style="display: block; margin: 0 auto; border-radius: 6px;">
                        </td>'''
    
    # Count coordination requirements
    coord_count = sum(1 for r in recommendation.releases if r.requires_coordination)
    
    # Build appropriate greeting based on recipient role
    owner_name = recommendation.owner_email.split('@')[0]
    
    # Check if there are other symlink owners (coordination needed)
    has_symlink_owners = len(recommendation.all_symlink_owners) > 0
    
    if has_symlink_owners:
        # This email is going to release owner AND symlink owners (CC'd)
        greeting_text = f'''
            <p style="margin: 0; font-size: 22px; color: #212529; font-weight: bold;">
                Hello <strong>{owner_name}</strong> (Release Owner) and <strong>Symlink Owners</strong> (CC'd),
            </p>
            <p style="margin: 10px 0 20px 0; font-size: 22px; color: #212529;">
                <strong>{owner_name}</strong>: You have <strong>{recommendation.release_count}</strong> old releases consuming <strong>{recommendation.total_size_human}</strong>. 
                <strong style="color: #dc3545;">DELETE THEM</strong> to free up space.<br/>
                <strong>Symlink Owners (CC'd)</strong>: Remove your symlinks FIRST before {owner_name} deletes the releases.
            </p>'''
    else:
        # Only release owner, no coordination needed
        greeting_text = f'''
            <p style="margin: 0; font-size: 22px; color: #212529; font-weight: bold;">
                Hello <strong>{owner_name}</strong>,
            </p>
            <p style="margin: 10px 0 20px 0; font-size: 22px; color: #212529;">
                You have <strong>{recommendation.release_count}</strong> old releases consuming <strong>{recommendation.total_size_human}</strong>. 
                <strong style="color: #dc3545;">DELETE THEM</strong> to free up space.
            </p>'''
    
    # Build header
    if coord_count > 0:
        title_text = "Block Release Cleanup - Coordination Required"
        desc_text = f"⚠️ {coord_count} release(s) require coordination with other users"
        header_color = "#ff9800"  # Orange for coordination
    else:
        title_text = "Block Release Cleanup Required"
        desc_text = "AGUR Release Area at 90% - Action Required"
        header_color = "#dc3545"  # Red for critical
    
    test_banner = ''
    if test_mode:
        test_banner = '''
        <div style="background-color: #ff9800; color: white; padding: 10px; text-align: center; font-weight: bold;">
            [TEST MODE] This email would normally be sent to the release owner
        </div>'''
    
    # Build simplified release table (removed Status column)
    release_rows = ''
    for release in sorted(recommendation.releases, key=lambda r: r.size_bytes, reverse=True):
        # Build symlink info
        symlink_cell = 'None'
        if release.symlink_infos:
            symlink_list = []
            for sym in release.symlink_infos:
                owner_badge = f" ({sym.symlink_owner})" if sym.symlink_owner != release.owner else ""
                symlink_list.append(f"{sym.symlink_name}{owner_badge}")
            symlink_cell = '<br/>'.join(symlink_list)
        
        release_rows += f'''
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-size: 16px;">{release.unit}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-size: 16px; font-family: monospace; word-break: break-all;">{release.release_dir}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; text-align: center; font-size: 16px;">{release.age_days}d</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; text-align: right; font-weight: bold; font-size: 16px;">{release.size_human}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; font-size: 16px;">{symlink_cell}</td>
            </tr>'''
    
    # Build coordination section - action-oriented
    coordination_section = ''
    if coord_count > 0:
        coord_releases = [r for r in recommendation.releases if r.requires_coordination]
        coordination_section = '''
        <div style="background-color: #fff3cd; border-left: 4px solid #ff9800; padding: 15px; margin: 15px 0;">
            <p style="margin: 0 0 10px 0; font-weight: bold; color: #856404; font-size: 24px;">
                ⚠️ ⚠️ COORDINATION REQUIRED ⚠️ ⚠️
            </p>
            <p style="margin: 0 0 10px 0; color: #856404; font-size: 18px;">
                Other users (CC'd on this email) created symlinks to your releases. 
                <strong>Wait for them to remove their symlinks before deleting the releases.</strong>
            </p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <tr style="background-color: #ffc107;">
                    <th style="padding: 8px; text-align: left; font-size: 17px; font-weight: bold;">Your Release</th>
                    <th style="padding: 8px; text-align: left; font-size: 17px; font-weight: bold;">Other User</th>
                    <th style="padding: 8px; text-align: left; font-size: 17px; font-weight: bold;">Their Symlink</th>
                </tr>'''
        
        for release in coord_releases:
            for symlink_info in release.symlink_infos:
                if symlink_info.symlink_owner != release.owner:
                    coordination_section += f'''
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-size: 16px; font-family: monospace; word-break: break-all;">{release.unit}/{release.release_dir}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-size: 16px;"><strong>{symlink_info.symlink_owner}</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-size: 16px; font-family: monospace;">{symlink_info.symlink_name}</td>
                </tr>'''
        
        coordination_section += '''
            </table>
        </div>'''
    
    # Build per-release commands - only owner's own symlinks
    commands_list = ''
    for i, release in enumerate(sorted(recommendation.releases, key=lambda r: r.size_bytes, reverse=True), 1):
        # Only include symlinks owned by the release owner
        owner_symlinks = [s for s in release.symlink_infos if s.symlink_owner == release.owner]
        
        symlink_commands = ''
        if owner_symlinks:
            symlink_commands = '<p style="margin: 5px 0; color: #856404; font-size: 18px;"><strong>Step 1: Remove your symlinks</strong></p>\n'
            for sym in owner_symlinks:
                symlink_commands += f'<pre style="background: #263238; color: #ffc107; padding: 8px; border-radius: 4px; margin: 3px 0; font-size: 15px;">rm {sym.symlink_path}</pre>\n'
        
        # Verification command
        verify_cmd = f'find /home/agur_backend_blockRelease/block/{release.unit}/ -type l -exec ls -l {{}} \\; | grep "{release.release_dir}"'
        
        # Deletion command
        delete_cmd = f'rm -rf {release.full_path}'
        
        step_num_verify = 2 if owner_symlinks else 1
        step_num_delete = 3 if owner_symlinks else 2
        
        commands_list += f'''
        <div style="background-color: #f8f9fa; border-left: 3px solid #0d47a1; padding: 12px; margin: 10px 0;">
            <p style="margin: 0 0 8px 0; font-weight: bold; color: #0d47a1; font-size: 18px;">Release {i}: {release.unit}/{release.release_dir} ({release.size_human})</p>
            
            {symlink_commands}
            
            <p style="margin: 10px 0 5px 0; font-size: 18px;"><strong>Step {step_num_verify}: Verify no symlinks remain</strong></p>
            <pre style="background: #263238; color: #4fc3f7; padding: 8px; border-radius: 4px; margin: 3px 0; font-size: 15px;">{verify_cmd}</pre>
            <p style="margin: 5px 0; font-size: 15px; color: #666;"><em>Output should be empty</em></p>
            
            <p style="margin: 10px 0 5px 0; font-size: 18px;"><strong>Step {step_num_delete}: Delete the release</strong></p>
            <pre style="background: #263238; color: #f48fb1; padding: 8px; border-radius: 4px; margin: 3px 0; font-size: 15px;">{delete_cmd}</pre>
        </div>'''
    
    # Build full HTML
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px;">
    {test_banner}
    <div style="max-width: 1000px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
        
        <!-- Header (Keep as-is) -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: {header_color};">
            <tr>{logo_cell}
                <td style="padding: 15px 20px; vertical-align: middle;">
                    <span style="color: white; font-size: 22px; font-weight: bold; display: block;">{title_text}</span>
                    <span style="color: white; font-size: 18px;">{desc_text}</span>
                </td>
                <td style="width: 300px; text-align: right; vertical-align: middle; padding: 10px 15px;">
                    <table cellpadding="0" cellspacing="0" border="0" align="right">
                        <tr>
                            <td style="background-color: #fff; border: 3px solid #fff; border-radius: 6px; padding: 10px 20px; text-align: center;">
                                <span style="color: {header_color}; font-size: 32px; font-weight: bold; display: block; line-height: 1;">{recommendation.release_count}</span>
                                <span style="color: #666; font-size: 13px; display: block; margin-top: 3px;">OLD RELEASES</span>
                            </td>
                            <td style="width: 10px;"></td>
                            <td style="background-color: #fff; border: 3px solid #fff; border-radius: 6px; padding: 10px 20px; text-align: center;">
                                <span style="color: {header_color}; font-size: 32px; font-weight: bold; display: block; line-height: 1;">{recommendation.total_size_human}</span>
                                <span style="color: #666; font-size: 13px; display: block; margin-top: 3px;">RECLAIMABLE</span>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        <!-- Content -->
        <div style="padding: 20px;">
            <!-- Greeting - Addresses both release owner and symlink owners -->
            {greeting_text}
            
            {coordination_section}
            
            <!-- Release Table - Simplified (no Status column) -->
            <h3 style="color: #0d47a1; margin: 20px 0 10px 0; font-size: 26px; font-weight: bold;">📋 Your Old Releases</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background-color: #f8f9fa;">
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6; font-size: 17px; font-weight: bold;">Unit</th>
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6; font-size: 17px; font-weight: bold;">Release Directory</th>
                    <th style="padding: 10px; text-align: center; border-bottom: 2px solid #dee2e6; font-size: 17px; font-weight: bold;">Age</th>
                    <th style="padding: 10px; text-align: right; border-bottom: 2px solid #dee2e6; font-size: 17px; font-weight: bold;">Size</th>
                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6; font-size: 17px; font-weight: bold;">Symlinks</th>
                </tr>
                {release_rows}
            </table>
            
            <!-- Commands - Per Release -->
            <h3 style="color: #0d47a1; margin: 20px 0 10px 0; font-size: 26px; font-weight: bold;">⚠️ DELETION COMMANDS - YOU MUST RUN THESE ⚠️</h3>
            {commands_list}
            
            <!-- Acknowledgment Request -->
            <div style="background: #fff3cd; border: 3px solid #ff9800; padding: 20px; margin: 20px 0; border-radius: 4px; text-align: center;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #856404; font-size: 24px;">
                    ⚠️ REPLY REQUIRED ⚠️
                </p>
                <p style="margin: 0; font-weight: bold; color: #856404; font-size: 20px;">
                    📧 You MUST reply to this email after deleting.
                </p>
            </div>
            
            <!-- Contact Info -->
            <p style="text-align: center; color: #666; font-size: 16px; margin: 10px 0;">
                Questions? Contact {ALWAYS_CC} or {recommendation.chiplet_manager}
            </p>
        </div>
    </div>
</body>
</html>'''
    
    return html

def send_cleanup_email(recommendation: OwnerRecommendation, test_mode: bool = False) -> bool:
    """
    Send cleanup recommendation email to owner with CC to symlink owners and manager.
    
    Args:
        recommendation: OwnerRecommendation object
        test_mode: If True, send to current user only
        
    Returns:
        True if successful, False otherwise
    """
    try:
        msg = MIMEMultipart('alternative')
        
        # Build recipient lists
        if test_mode:
            to_address = get_test_mode_recipient()
            cc_list = []
            msg['Subject'] = f'[TEST] [AGUR] Release Cleanup - {recommendation.total_size_human} Can Be Freed'
        else:
            to_address = recommendation.owner_email
            cc_list = [ALWAYS_CC, recommendation.chiplet_manager]
            
            # Add backup manager for QNS/TCB chiplets (temporary - ohamama on vacation)
            chiplets_in_recommendation = set(r.chiplet for r in recommendation.releases)
            if 'QNS' in chiplets_in_recommendation or 'TCB' in chiplets_in_recommendation:
                cc_list.append('vliberchuk@nvidia.com')
            
            # Add log owners (previous owners) to CC
            cc_list.extend(recommendation.cc_log_owners)
            
            # Add symlink owners to CC if coordination required
            cc_list.extend(recommendation.all_symlink_owners)
            
            # Remove duplicates and sort
            cc_list = sorted(set(cc_list))
            
            msg['Subject'] = f'[AGUR] Release Cleanup Required - {recommendation.total_size_human} Can Be Freed'
        
        msg['From'] = ALWAYS_CC
        msg['To'] = to_address
        if cc_list:
            msg['Cc'] = ', '.join(cc_list)
        
        # Build HTML body
        html_body = build_email_html(recommendation, test_mode)
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        all_recipients = [to_address] + cc_list
        with smtplib.SMTP('localhost') as smtp:
            smtp.send_message(msg, to_addrs=all_recipients)
        
        if test_mode:
            logger.info(f"  [TEST] Sent to {to_address} (originally for {recommendation.owner_email})")
        else:
            logger.info(f"  Sent to {to_address} (CC: {len(cc_list)} recipients)")
        
        return True
        
    except Exception as e:
        logger.error(f"  Failed to send email to {recommendation.owner_email}: {e}")
        return False

def send_cleanup_emails(owner_recommendations: Dict[str, OwnerRecommendation], 
                        test_mode: bool = False,
                        approved_releases_set: Set[str] = None):
    """
    Send cleanup emails to all owners
    
    Args:
        owner_recommendations: Dict of OwnerRecommendation objects keyed by owner email
        test_mode: If True, send all emails to current user only
        approved_releases_set: Set of approved release IDs. If provided, only send emails
                               for releases that are in this set. If None, send for all releases.
    """
    logger.info("\nSending cleanup recommendation emails...")
    
    sent_count = 0
    failed_count = 0
    
    for owner_email, recommendation in owner_recommendations.items():
        # Filter recommendation if approved_releases_set is provided
        if approved_releases_set is not None:
            # Filter releases to only include approved ones
            approved_releases = [r for r in recommendation.releases 
                                if get_release_id(r) in approved_releases_set]
            
            if not approved_releases:
                logger.info(f"  Skipping {owner_email}: No approved releases")
                continue
            
            # Create filtered recommendation with all required fields
            filtered_recommendation = OwnerRecommendation(
                owner_email=recommendation.owner_email,
                releases=approved_releases,
                total_size_bytes=sum(r.size_bytes for r in approved_releases),
                total_size_human=format_bytes(sum(r.size_bytes for r in approved_releases)),
                unit_count=len(set(r.unit for r in approved_releases)),
                release_count=len(approved_releases),
                chiplet_manager=recommendation.chiplet_manager,
                all_symlink_owners=recommendation.all_symlink_owners
            )
            
            if send_cleanup_email(filtered_recommendation, test_mode):
                sent_count += 1
            else:
                failed_count += 1
        else:
            # Send for all releases (original behavior)
            if send_cleanup_email(recommendation, test_mode):
                sent_count += 1
            else:
                failed_count += 1
    
    logger.info(f"  Emails sent: {sent_count}, Failed: {failed_count}")

def generate_reports(owner_recommendations: Dict[str, OwnerRecommendation], 
                     releases: List[ReleaseInfo],
                     output_dir: str,
                     age_threshold: int):
    """Generate all reports"""
    logger.info("\nGenerating reports...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate detailed CSV report
    csv_file = output_path / f"cleanup_report_{timestamp}.csv"
    generate_csv_report(releases, csv_file)
    
    # Generate unit summary CSV report
    unit_summary_file = output_path / f"cleanup_unit_summary_{timestamp}.html"
    generate_dashboard_report(releases, unit_summary_file)
    
    # Generate Markdown summary
    md_file = output_path / f"cleanup_summary_{timestamp}.md"
    generate_markdown_summary(owner_recommendations, releases, md_file, age_threshold)
    
    logger.info(f"  Reports written to {output_path}/")

def group_releases_by_owner(releases: List[ReleaseInfo]) -> Dict[str, OwnerRecommendation]:
    """
    Group releases by owner and create recommendations.
    
    Args:
        releases: List of ReleaseInfo objects
        
    Returns:
        Dict mapping owner_email -> OwnerRecommendation
    """
    logger.info("\nGrouping releases by owner...")
    
    owner_map = {}
    
    for release in releases:
        owner_email = f"{release.owner}@nvidia.com"
        
        if owner_email not in owner_map:
            # Get chiplet manager
            chiplet_manager = CHIPLET_MANAGERS.get(release.chiplet, ALWAYS_CC)
            
            owner_map[owner_email] = OwnerRecommendation(
                owner_email=owner_email,
                releases=[],
                total_size_bytes=0,
                total_size_human='',
                unit_count=0,
                release_count=0,
                chiplet_manager=chiplet_manager,
                all_symlink_owners=set()
            )
        
        recommendation = owner_map[owner_email]
        recommendation.releases.append(release)
        recommendation.total_size_bytes += release.size_bytes
        recommendation.release_count += 1
        
        # Collect symlink owners for coordination
        for symlink_info in release.symlink_infos:
            if symlink_info.symlink_owner != release.owner:
                recommendation.all_symlink_owners.add(f"{symlink_info.symlink_owner}@nvidia.com")
        
        # Collect log owners (previous owners) for CC if different from current folder owner
        if release.log_owner and release.log_owner != release.folder_owner:
            recommendation.cc_log_owners.add(f"{release.log_owner}@nvidia.com")
    
    # Calculate unique units and format sizes
    for owner_email, recommendation in owner_map.items():
        unique_units = set(r.unit for r in recommendation.releases)
        recommendation.unit_count = len(unique_units)
        recommendation.total_size_human = format_bytes(recommendation.total_size_bytes)
        
        logger.info(f"  {owner_email}: {recommendation.release_count} releases, " +
                   f"{recommendation.unit_count} units, {recommendation.total_size_human}")
    
    return owner_map

def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f}PB"

def calculate_age_distribution(releases: List[ReleaseInfo]) -> Dict:
    """Calculate age distribution buckets"""
    buckets = {
        '0-30d': 0,
        '30-60d': 0,
        '60-90d': 0,
        '90-180d': 0,
        '180+d': 0
    }
    
    for release in releases:
        age = release.age_days
        if age <= 30:
            buckets['0-30d'] += 1
        elif age <= 60:
            buckets['30-60d'] += 1
        elif age <= 90:
            buckets['60-90d'] += 1
        elif age <= 180:
            buckets['90-180d'] += 1
        else:
            buckets['180+d'] += 1
    
    return buckets

def calculate_chiplet_breakdown(releases: List[ReleaseInfo]) -> Dict:
    """Calculate size breakdown by chiplet"""
    chiplet_data = {}
    
    for release in releases:
        if release.chiplet not in chiplet_data:
            chiplet_data[release.chiplet] = {
                'size_bytes': 0,
                'count': 0
            }
        chiplet_data[release.chiplet]['size_bytes'] += release.size_bytes
        chiplet_data[release.chiplet]['count'] += 1
    
    return chiplet_data

def calculate_coordination_stats(releases: List[ReleaseInfo]) -> Dict:
    """Calculate coordination statistics"""
    stats = {
        'no_symlinks': 0,
        'self_symlinks': 0,
        'coordination_needed': 0
    }
    
    for release in releases:
        if not release.has_symlinks:
            stats['no_symlinks'] += 1
        elif release.requires_coordination:
            stats['coordination_needed'] += 1
        else:
            stats['self_symlinks'] += 1
    
    return stats

def get_top_consumers(releases: List[ReleaseInfo], limit: int = 10) -> List:
    """Get top N space consumers"""
    # Group by unit and owner
    consumer_map = {}
    
    for release in releases:
        key = (release.unit, release.owner)
        if key not in consumer_map:
            consumer_map[key] = {
                'unit': release.unit,
                'owner': release.owner,
                'chiplet': release.chiplet,
                'count': 0,
                'size_bytes': 0
            }
        consumer_map[key]['count'] += 1
        consumer_map[key]['size_bytes'] += release.size_bytes
    
    # Sort by size and return top N
    sorted_consumers = sorted(consumer_map.values(), key=lambda x: x['size_bytes'], reverse=True)
    return sorted_consumers[:limit]

def group_by_chiplet_detailed(releases: List[ReleaseInfo]) -> Dict:
    """Group releases by chiplet with detailed breakdown"""
    chiplet_groups = {}
    
    for release in releases:
        if release.chiplet not in chiplet_groups:
            chiplet_groups[release.chiplet] = []
        chiplet_groups[release.chiplet].append(release)
    
    return chiplet_groups

def group_by_owner_detailed(releases: List[ReleaseInfo]) -> Dict:
    """Group releases by owner across all chiplets"""
    owner_groups = {}
    
    for release in releases:
        owner = release.owner
        if owner not in owner_groups:
            owner_groups[owner] = {
                'releases': [],
                'units': set(),
                'chiplets': set(),
                'total_size': 0
            }
        
        owner_groups[owner]['releases'].append(release)
        owner_groups[owner]['units'].add(release.unit)
        owner_groups[owner]['chiplets'].add(release.chiplet)
        owner_groups[owner]['total_size'] += release.size_bytes
    
    return owner_groups

def enrich_releases_with_symlinks(releases: List[ReleaseInfo]) -> List[ReleaseInfo]:
    """
    Analyze symlinks and enrich release info with symlink data.
    
    Args:
        releases: List of ReleaseInfo objects
        
    Returns:
        Updated list with symlink information
    """
    logger.info("\nAnalyzing symlinks...")
    
    # Group releases by unit
    units = {}
    for release in releases:
        if release.unit not in units:
            units[release.unit] = []
        units[release.unit].append(release)
    
    # Analyze symlinks per unit
    for unit in units:
        logger.debug(f"Analyzing symlinks in {unit}...")
        symlink_map = analyze_unit_symlinks(unit)
        
        logger.debug(f"  [DEBUG] Symlink map for {unit} has {len(symlink_map)} entries")
        logger.debug(f"  [DEBUG] Symlink map keys: {list(symlink_map.keys())[:3]}...")  # Show first 3
        
        # Enrich releases with symlink info
        for release in units[unit]:
            logger.debug(f"  [DEBUG] Checking release: {release.release_dir}")
            logger.debug(f"    full_path: {release.full_path}")
            logger.debug(f"    In symlink_map? {release.full_path in symlink_map}")
            
            if release.full_path in symlink_map:
                symlinks = symlink_map[release.full_path]
                release.has_symlinks = True
                release.symlink_infos = symlinks
                release.is_protected = True
                
                logger.debug(f"    ✓ MATCHED! Found {len(symlinks)} symlink(s)")
                
                # Check if coordination is required (symlinks created by other users)
                release_owner = release.owner
                for symlink in symlinks:
                    if symlink.symlink_owner != release_owner and symlink.symlink_owner != 'unknown':
                        release.requires_coordination = True
                        break
                
                logger.debug(f"  {release.release_dir}: {len(symlinks)} symlink(s), " +
                           f"coordination={'required' if release.requires_coordination else 'not needed'}")
            else:
                logger.debug(f"    ✗ NO MATCH - Release not found in symlink map")
    
    # Count results
    protected_count = sum(1 for r in releases if r.is_protected)
    coordination_count = sum(1 for r in releases if r.requires_coordination)
    
    logger.info(f"  Protected by symlinks: {protected_count}/{len(releases)}")
    logger.info(f"  Require coordination: {coordination_count}/{len(releases)}")
    
    return releases

def scan_all_releases(units: Dict[str, Dict], age_threshold_days: int, 
                      specific_units: Optional[List[str]] = None) -> List[ReleaseInfo]:
    """
    Scan all units for old releases.
    
    Args:
        units: Dict of unit info from AGUR_UNITS_TABLE.csv
        age_threshold_days: Age threshold in days
        specific_units: Optional list of specific units to scan
        
    Returns:
        List of all old ReleaseInfo objects
    """
    all_releases = []
    
    units_to_scan = specific_units if specific_units else list(units.keys())
    
    logger.info(f"\nScanning {len(units_to_scan)} units for releases older than {age_threshold_days} days...")
    
    for unit in units_to_scan:
        if unit not in units:
            logger.warning(f"Unit {unit} not found in units table, skipping")
            continue
        
        unit_releases = scan_unit_releases(unit, units[unit], age_threshold_days)
        all_releases.extend(unit_releases)
    
    logger.info(f"Found {len(all_releases)} old releases across {len(units_to_scan)} units")
    
    return all_releases

# Global variable to store releases for the approval server
_approval_server_releases = []
_approval_server_output_dir = None
_approval_server_test_mode = False

def load_approval_state(output_dir: Path) -> Dict:
    """Load approval state from JSON file"""
    state_files = sorted(output_dir.glob('approval_state_*.json'), reverse=True)
    if state_files:
        with open(state_files[0], 'r') as f:
            state = json.load(f)
        
        # Backward compatibility: Convert old emailed_releases format to new format
        if 'emailed_releases' in state:
            for release_id, info in state['emailed_releases'].items():
                # Old format has 'emailed_at', new format has 'email_history'
                if 'emailed_at' in info and 'email_history' not in info:
                    # Convert to new format
                    info['email_history'] = [{
                        'sent_at': info['emailed_at'],
                        'test_mode': info.get('test_mode', False)
                    }]
                    # Remove old field
                    del info['emailed_at']
                    if 'test_mode' in info:
                        del info['test_mode']
        
        return state
    
    # Return empty state if no file exists
    return {
        'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
        'approvals': {},
        'emailed_releases': {},  # Track which releases have been emailed
        'email_sent': False,
        'email_sent_at': None
    }

def save_approval_state(state: Dict, output_dir: Path):
    """Save approval state to JSON file"""
    state['last_updated'] = datetime.now().isoformat()
    state_file = output_dir / f"approval_state_{state['session_id']}.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    logger.info(f"  Approval state saved: {state_file}")

def get_release_id(release: ReleaseInfo) -> str:
    """Generate unique release ID from release info"""
    timestamp = release.release_timestamp.strftime('%Y%m%d_%H%M%S')
    return f"{release.unit}_{timestamp}_{release.owner}"

def filter_releases_by_approved(releases: List[ReleaseInfo], approved_ids: Set[str]) -> List[ReleaseInfo]:
    """Filter releases to only include approved ones"""
    return [r for r in releases if get_release_id(r) in approved_ids]

def create_approval_server(releases: List[ReleaseInfo], output_dir: Path, test_mode: bool = False) -> Flask:
    """Create and configure Flask server for approval management"""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for file:// protocol
    
    # Store releases, output dir, and test_mode globally for access in routes
    global _approval_server_releases, _approval_server_output_dir, _approval_server_test_mode
    _approval_server_releases = releases
    _approval_server_output_dir = output_dir
    _approval_server_test_mode = test_mode
    
    @app.route('/api/releases', methods=['GET'])
    def get_releases():
        """Get all releases with approval status"""
        state = load_approval_state(output_dir)
        
        # Ensure emailed_releases key exists
        if 'emailed_releases' not in state:
            state['emailed_releases'] = {}
        
        releases_data = []
        for release in _approval_server_releases:
            release_id = get_release_id(release)
            approval_info = state['approvals'].get(release_id, {'approved': False})
            is_emailed = release_id in state['emailed_releases']
            
            releases_data.append({
                'id': release_id,
                'unit': release.unit,
                'chiplet': release.chiplet,
                'owner': release.owner,
                'release_dir': release.release_dir,
                'age_days': release.age_days,
                'size_human': release.size_human,
                'size_bytes': release.size_bytes,
                'approved': approval_info.get('approved', False),
                'emailed': is_emailed,
                'has_symlinks': release.has_symlinks,
                'requires_coordination': release.requires_coordination
            })
        
        return jsonify({
            'success': True,
            'releases': releases_data,
            'total': len(releases_data)
        })
    
    @app.route('/api/approve', methods=['POST'])
    def toggle_approval():
        """Toggle approval status for a release"""
        data = request.get_json()
        release_id = data.get('release_id')
        approved = data.get('approved', False)
        
        if not release_id:
            return jsonify({'success': False, 'error': 'Missing release_id'}), 400
        
        state = load_approval_state(output_dir)
        
        if release_id not in state['approvals']:
            state['approvals'][release_id] = {}
        
        state['approvals'][release_id]['approved'] = approved
        state['approvals'][release_id]['approved_by'] = 'browser_session'
        state['approvals'][release_id]['approved_at'] = datetime.now().isoformat()
        
        save_approval_state(state, output_dir)
        
        approved_count = sum(1 for a in state['approvals'].values() if a.get('approved', False))
        
        return jsonify({
            'success': True,
            'approved': approved,
            'approved_count': approved_count
        })
    
    @app.route('/api/status', methods=['GET'])
    def get_status():
        """Get server status and approval counts"""
        state = load_approval_state(output_dir)
        
        # Ensure emailed_releases key exists (for backwards compatibility)
        if 'emailed_releases' not in state:
            state['emailed_releases'] = {}
        
        total_releases = len(_approval_server_releases)
        approved_count = sum(1 for a in state['approvals'].values() if a.get('approved', False))
        emailed_count = len(state['emailed_releases'])
        pending_count = total_releases - approved_count
        
        return jsonify({
            'success': True,
            'total_releases': total_releases,
            'approved_count': approved_count,
            'emailed_count': emailed_count,
            'pending_count': pending_count,
            'email_sent': state.get('email_sent', False),
            'email_sent_at': state.get('email_sent_at')
        })
    
    @app.route('/api/send_emails', methods=['POST'])
    def send_approved_emails():
        """Send emails for approved releases only"""
        try:
            # Use the test_mode from server initialization, not from request
            # This ensures consistency with how the server was started
            test_mode = _approval_server_test_mode
            
            state = load_approval_state(output_dir)
            
            # Ensure emailed_releases key exists (for backwards compatibility)
            if 'emailed_releases' not in state:
                state['emailed_releases'] = {}
            
            # Get approved release IDs
            approved_ids = {rid for rid, info in state['approvals'].items() 
                           if info.get('approved', False)}
            
            if not approved_ids:
                return jsonify({
                    'success': False,
                    'error': 'No releases approved for email sending'
                }), 400
            
            # Allow resending - send to ALL approved releases
            # Calculate resend statistics for logging
            resend_count = sum(1 for rid in approved_ids if rid in state['emailed_releases'])
            new_count = len(approved_ids) - resend_count
            
            # Log what we're doing
            logger.info(f"\nEmail sending summary:")
            logger.info(f"  Total approved releases: {len(approved_ids)}")
            logger.info(f"  New releases: {new_count}")
            logger.info(f"  Resending to: {resend_count}")
            
            # Send to ALL approved releases (no filtering)
            approved_releases = filter_releases_by_approved(_approval_server_releases, approved_ids)
            
            # Group by owner
            owner_recommendations = group_releases_by_owner(approved_releases)
            
            # Send emails
            send_cleanup_emails(owner_recommendations, test_mode, approved_releases_set=approved_ids)
            
            # Update email history for each release
            timestamp = datetime.now().isoformat()
            for release_id in approved_ids:
                # Find the release to get owner info
                release = next((r for r in approved_releases if get_release_id(r) == release_id), None)
                if release:
                    # Initialize release entry if it doesn't exist
                    if release_id not in state['emailed_releases']:
                        state['emailed_releases'][release_id] = {
                            'owner': release.owner,
                            'unit': release.unit,
                            'email_history': []
                        }
                    
                    # Append to email history
                    state['emailed_releases'][release_id]['email_history'].append({
                        'sent_at': timestamp,
                        'test_mode': test_mode
                    })
            
            # Mark overall email_sent flag
            state['email_sent'] = True
            state['email_sent_at'] = timestamp
            save_approval_state(state, output_dir)
            
            return jsonify({
                'success': True,
                'message': f'Emails sent for {len(approved_ids)} releases',
                'total_sent': len(approved_ids),
                'new_sends': new_count,
                'resends': resend_count,
                'newly_emailed_ids': list(approved_ids),
                'test_mode': test_mode
            })
            
        except Exception as e:
            logger.error(f"Error sending emails: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app

def run_approval_server(releases: List[ReleaseInfo], output_dir: Path, test_mode: bool = False, port: int = 5000):
    """Run the Flask approval server"""
    app = create_approval_server(releases, output_dir, test_mode)
    logger.info(f"Starting approval server on http://localhost:{port}")
    if test_mode:
        test_recipient = get_test_mode_recipient()
        logger.info(f"Test mode: ENABLED (emails to {test_recipient} only)")
    else:
        logger.info("Test mode: DISABLED (emails to actual owners)")
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

def get_latest_dashboard(output_dir: Path) -> Path:
    """Get the most recently generated dashboard file"""
    dashboard_files = sorted(output_dir.glob('cleanup_unit_summary_*.html'), reverse=True)
    if dashboard_files:
        return dashboard_files[0].absolute()
    return None

def main():
    """Main entry point"""
    global logger
    
    args = parse_arguments()
    logger = setup_logging(args.quiet)
    
    logger.info("=" * 80)
    logger.info(f"AGUR Release Cleanup Utility - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    if args.test_mode:
        test_recipient = get_test_mode_recipient()
        logger.info(f"[TEST MODE] All emails will be sent to {test_recipient} only!")
        # test_mode implies send_emails
        args.send_emails = True
    if args.dry_run:
        logger.info("[DRY-RUN MODE] No emails or reports will be generated")
    elif args.email_only:
        logger.info("[EMAIL-ONLY MODE] No reports will be generated")
    elif not args.send_emails:
        logger.info("[REPORT-ONLY MODE] No emails will be sent (default behavior)")
    
    logger.info(f"Age threshold: {args.age_threshold} days")
    logger.info(f"Parallel processes: {args.parallel}")
    
    # Load units table
    units = load_units_table()
    
    # Parse specific units if provided
    specific_units = None
    scanned_chiplets = []
    if args.chiplet:
        chiplet_input = args.chiplet.upper().strip()
        
        # Handle "ALL" special case
        if chiplet_input == 'ALL':
            scanned_chiplets = list(CHIPLET_UNITS.keys())
            specific_units = []
            for chiplet in scanned_chiplets:
                specific_units.extend(CHIPLET_UNITS[chiplet])
            logger.info(f"Scanning ALL chiplets ({len(scanned_chiplets)} chiplets, {len(specific_units)} units)")
        else:
            # Parse comma-separated chiplets
            chiplet_names = [c.strip() for c in chiplet_input.split(',')]
            specific_units = []
            for chiplet in chiplet_names:
                if chiplet not in CHIPLET_UNITS:
                    logger.error(f"Unknown chiplet: {chiplet}. Valid chiplets: {', '.join(CHIPLET_UNITS.keys())}")
                    sys.exit(1)
                scanned_chiplets.append(chiplet)
                specific_units.extend(CHIPLET_UNITS[chiplet])
            
            if len(scanned_chiplets) == 1:
                logger.info(f"Scanning chiplet {scanned_chiplets[0]}: {', '.join(CHIPLET_UNITS[scanned_chiplets[0]])}")
            else:
                logger.info(f"Scanning {len(scanned_chiplets)} chiplets: {', '.join(scanned_chiplets)} ({len(specific_units)} total units)")
    elif args.units:
        specific_units = [u.strip() for u in args.units.split(',')]
        logger.info(f"Scanning specific units: {', '.join(specific_units)}")
    
    # Scan for old releases
    old_releases = scan_all_releases(units, args.age_threshold, specific_units)
    
    if not old_releases:
        logger.info("\n✓ No old releases found!")
        return
    
    logger.info(f"\nFound {len(old_releases)} releases to analyze...")
    
    # Analyze symlinks
    old_releases = enrich_releases_with_symlinks(old_releases)
    
    # Extract owner info from logs
    old_releases = enrich_releases_with_log_data(old_releases)
    
    # Calculate disk usage
    old_releases = calculate_sizes_parallel(old_releases, args.parallel)
    
    # Group by owner
    owner_recommendations = group_releases_by_owner(old_releases)
    
    # Generate reports (unless dry-run or email-only)
    if not args.dry_run and not args.email_only:
        generate_reports(owner_recommendations, old_releases, args.output_dir, args.age_threshold)
    
    # Send emails only if explicitly requested AND not in interactive mode
    # In interactive mode, emails are sent via the dashboard button
    if not args.dry_run and args.send_emails and not args.interactive:
        send_cleanup_emails(owner_recommendations, args.test_mode)
    
    # Interactive mode: Start approval server
    if args.interactive:
        logger.info("\n" + "=" * 80)
        logger.info("Starting Interactive Approval Mode")
        logger.info("=" * 80)
        
        # Ensure reports were generated
        if args.dry_run or args.email_only:
            logger.error("Interactive mode requires reports to be generated. Remove --dry-run or --email-only flags.")
            return
        
        # Start HTTP server in background thread
        output_dir_path = Path(args.output_dir)
        server_thread = Thread(
            target=run_approval_server, 
            args=(old_releases, output_dir_path, args.test_mode, 5000)
        )
        server_thread.daemon = True
        server_thread.start()
        
        # Give server a moment to start
        time.sleep(1)
        
        # Open dashboard in browser
        dashboard_path = get_latest_dashboard(output_dir_path)
        if dashboard_path:
            logger.info(f"Opening dashboard: {dashboard_path}")
            webbrowser.open(f'file://{dashboard_path}')
        else:
            logger.error("Dashboard file not found!")
            return
        
        logger.info("\n" + "=" * 80)
        logger.info("Interactive Approval Server Running")
        logger.info("=" * 80)
        logger.info(f"  Server URL: http://localhost:5000")
        logger.info(f"  Dashboard: {dashboard_path}")
        logger.info("\nInstructions:")
        logger.info("  1. Review releases in the dashboard")
        logger.info("  2. Check boxes next to releases you approve for deletion")
        logger.info("  3. Click 'Send Emails for Approved Releases' button")
        logger.info("  4. Press Ctrl+C to stop the server")
        logger.info("=" * 80)
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n\nServer stopped by user")
            logger.info("Approval state saved. You can resume later by running with --interactive again.")
    else:
        logger.info("\n" + "=" * 80)
        logger.info("Analysis complete!")
        logger.info("=" * 80)

if __name__ == '__main__':
    main()
