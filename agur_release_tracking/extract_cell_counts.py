#!/usr/bin/env python3
"""
Extract Cell Counts for All AGUR Units

This script scans all AGUR units' release workareas to extract cell count information
from PnR reports (typically found in nbu_signoff directories).

Cell count is extracted from:
1. Innovus reports (innovus.logv) - searches for "Total number of instances"
2. Summary reports (.rpt files) - searches for cell/instance counts
3. Design data files

Output: CSV and formatted table of top N units by cell count

Author: Alon Vice (avice@nvidia.com)
Date: January 4, 2026
"""

import os
import csv
import re
import subprocess
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Color codes for terminal output
class Color:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


def extract_cell_count_from_workarea(unit: str, workarea_path: str, chiplet: str) -> Optional[Dict]:
    """Extract cell count from a unit's workarea
    
    Strategy:
    1. Look for netlist files (*.nopower.gv.gz or *.gv.gz) in export directories
    2. Count cell instances in the netlist (lines with " (" pattern)
    3. Fall back to innovus logs if netlist not found
    
    Args:
        unit: Unit name (e.g., 'fdb', 'pmux')
        workarea_path: Path to released workarea
        chiplet: Chiplet name
    
    Returns:
        Dict with unit info and cell count, or None if not found
    """
    cell_count = None
    source_file = None
    
    # Check if workarea exists
    if not os.path.exists(workarea_path):
        return None
    
    # Strategy 1: Extract from netlist files (most accurate!)
    # Look for *.nopower.gv.gz or *.gv.gz files in export/export_innovus directories
    try:
        # Find netlist files (gv.gz files)
        find_cmd = f"find {workarea_path} -maxdepth 10 -type f \\( -name '*.nopower.gv.gz' -o -name '*.gv.gz' \\) -path '*/export/*' 2>/dev/null | head -5"
        result = subprocess.run(find_cmd, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True,
                               timeout=15)
        
        if result.returncode == 0 and result.stdout.strip():
            netlist_files = result.stdout.strip().split('\n')
            
            # Try each netlist file
            for netlist_file in netlist_files:
                if not os.path.exists(netlist_file):
                    continue
                
                try:
                    # Count cell instantiations in netlist
                    # Cell instances appear as lines with " (" pattern (module instantiation)
                    # e.g., "  NAND2_X1 U1234 ("
                    count_cmd = f"zcat {netlist_file} 2>/dev/null | grep -c ' ('"
                    count_result = subprocess.run(count_cmd, shell=True,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 universal_newlines=True,
                                                 timeout=30)
                    
                    if count_result.returncode == 0 and count_result.stdout.strip():
                        count = int(count_result.stdout.strip())
                        # Sanity check: cell count should be reasonable (> 100)
                        if count > 100:
                            cell_count = count
                            source_file = netlist_file
                            break
                
                except (subprocess.TimeoutExpired, ValueError, Exception):
                    continue
        
    except (subprocess.TimeoutExpired, Exception):
        pass
    
    # Strategy 2: Look for innovus log files (backup method)
    if not cell_count:
        cell_count_patterns = [
            r'Total number of instances:\s+(\d+)',
            r'Total instances:\s+(\d+)',
            r'Number of instances:\s+(\d+)',
            r'Cell count:\s+(\d+)',
            r'Total cells:\s+(\d+)',
        ]
        
        try:
            # Search for innovus log files
            find_cmd = f"find {workarea_path} -maxdepth 10 -type f \\( -name 'innovus.logv' -o -name 'innovus.log' -o -name '*.logv' \\) 2>/dev/null | head -20"
            result = subprocess.run(find_cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True,
                                   timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                log_files = result.stdout.strip().split('\n')
                
                # Search each log file for cell count
                for log_file in log_files:
                    if not os.path.exists(log_file):
                        continue
                    
                    try:
                        # Use grep for fast searching
                        grep_cmd = f"grep -i -E 'Total number of instances|Total instances|Cell count|Total cells' {log_file} | tail -5"
                        grep_result = subprocess.run(grep_cmd, shell=True,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    universal_newlines=True,
                                                    timeout=5)
                        
                        if grep_result.returncode == 0 and grep_result.stdout.strip():
                            # Try each pattern
                            for pattern in cell_count_patterns:
                                match = re.search(pattern, grep_result.stdout, re.IGNORECASE)
                                if match:
                                    cell_count = int(match.group(1))
                                    source_file = log_file
                                    break
                            
                            if cell_count:
                                break
                    
                    except (subprocess.TimeoutExpired, Exception):
                        continue
        
        except (subprocess.TimeoutExpired, Exception):
            pass
    
    # Return result
    if cell_count:
        return {
            'unit': unit,
            'chiplet': chiplet,
            'cell_count': cell_count,
            'workarea_path': workarea_path,
            'source_file': source_file
        }
    
    return None


def load_units_from_csv(csv_path: str) -> List[Dict]:
    """Load units from AGUR_UNITS_TABLE.csv
    
    Returns:
        List of unit dictionaries with unit, chiplet, and workarea_path
    """
    units = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            units.append({
                'unit': row['UNIT'],
                'chiplet': row['CHIPLET'],
                'workarea_path': row['RELEASED_WA_PATH'],
                'release_user': row['RELEASE_USER'],
                'release_timestamp': row['RELEASE_TIMESTAMP']
            })
    
    return units


def main():
    """Main execution"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'AGUR_UNITS_TABLE.csv')
    output_csv = os.path.join(script_dir, 'AGUR_CELL_COUNTS.csv')
    output_txt = os.path.join(script_dir, 'AGUR_CELL_COUNTS_TOP15.txt')
    
    print(f"{Color.BOLD}{'='*80}{Color.END}")
    print(f"{Color.CYAN}{Color.BOLD}AGUR Units Cell Count Extraction{Color.END}")
    print(f"{Color.BOLD}{'='*80}{Color.END}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load units
    print(f"{Color.YELLOW}Loading units from CSV...{Color.END}")
    units = load_units_from_csv(csv_path)
    print(f"{Color.GREEN}✓ Loaded {len(units)} units{Color.END}\n")
    
    # Extract cell counts in parallel (faster!)
    print(f"{Color.YELLOW}Extracting cell counts (parallel processing)...{Color.END}")
    print(f"{Color.CYAN}This may take a few minutes depending on workarea accessibility...{Color.END}\n")
    
    results = []
    processed = 0
    found = 0
    
    # Use ThreadPoolExecutor for parallel extraction (max 10 concurrent threads)
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_unit = {
            executor.submit(extract_cell_count_from_workarea, 
                          u['unit'], u['workarea_path'], u['chiplet']): u
            for u in units
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_unit):
            unit_info = future_to_unit[future]
            processed += 1
            
            try:
                result = future.result()
                if result:
                    found += 1
                    results.append(result)
                    print(f"{Color.GREEN}[{processed:2d}/{len(units)}] ✓ {result['unit']:15s} - {result['cell_count']:>10,} cells{Color.END}")
                else:
                    print(f"{Color.RED}[{processed:2d}/{len(units)}] ✗ {unit_info['unit']:15s} - No cell count found{Color.END}")
            except Exception as e:
                print(f"{Color.RED}[{processed:2d}/{len(units)}] ✗ {unit_info['unit']:15s} - Error: {e}{Color.END}")
    
    print(f"\n{Color.BOLD}{'='*80}{Color.END}")
    print(f"{Color.GREEN}Successfully extracted cell counts for {found}/{len(units)} units{Color.END}")
    print(f"{Color.BOLD}{'='*80}{Color.END}\n")
    
    if not results:
        print(f"{Color.RED}No cell count data found. Exiting.{Color.END}")
        return
    
    # Sort by cell count (descending)
    results.sort(key=lambda x: x['cell_count'], reverse=True)
    
    # Write full CSV
    print(f"{Color.YELLOW}Writing full results to CSV: {output_csv}{Color.END}")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['unit', 'chiplet', 'cell_count', 'workarea_path', 'source_file'])
        writer.writeheader()
        writer.writerows(results)
    print(f"{Color.GREEN}✓ CSV written{Color.END}\n")
    
    # Generate top 15 report
    top_15 = results[:15]
    
    print(f"{Color.YELLOW}Generating top 15 report: {output_txt}{Color.END}")
    with open(output_txt, 'w') as f:
        # Header
        f.write("="*80 + "\n")
        f.write("AGUR Project - Top 15 Units by Cell Count\n")
        f.write("="*80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total units analyzed: {len(units)}\n")
        f.write(f"Units with cell count data: {found}\n\n")
        
        # Table
        f.write(f"{'Rank':<6} {'Unit':<15} {'Chiplet':<10} {'Cell Count':>15} {'% of Top Unit':>12}\n")
        f.write("-"*80 + "\n")
        
        max_cell_count = top_15[0]['cell_count']
        
        for idx, result in enumerate(top_15, 1):
            percentage = (result['cell_count'] / max_cell_count) * 100
            f.write(f"{idx:<6} {result['unit']:<15} {result['chiplet']:<10} {result['cell_count']:>15,} {percentage:>11.1f}%\n")
        
        f.write("\n" + "="*80 + "\n\n")
        
        # Chiplet summary
        f.write("Chiplet Distribution (Top 15):\n")
        f.write("-"*40 + "\n")
        
        chiplet_counts = {}
        for result in top_15:
            chiplet = result['chiplet']
            chiplet_counts[chiplet] = chiplet_counts.get(chiplet, 0) + 1
        
        for chiplet in sorted(chiplet_counts.keys()):
            f.write(f"  {chiplet:<10}: {chiplet_counts[chiplet]} units\n")
    
    print(f"{Color.GREEN}✓ Top 15 report written{Color.END}\n")
    
    # Display top 15 to console
    print(f"\n{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}TOP 15 AGUR UNITS BY CELL COUNT{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{'='*80}{Color.END}\n")
    
    print(f"{Color.BOLD}{'Rank':<6} {'Unit':<15} {'Chiplet':<10} {'Cell Count':>15} {'% of Top':>12}{Color.END}")
    print(f"{Color.BOLD}{'-'*80}{Color.END}")
    
    for idx, result in enumerate(top_15, 1):
        percentage = (result['cell_count'] / max_cell_count) * 100
        color = Color.GREEN if idx <= 5 else Color.YELLOW if idx <= 10 else Color.CYAN
        print(f"{color}{idx:<6} {result['unit']:<15} {result['chiplet']:<10} {result['cell_count']:>15,} {percentage:>11.1f}%{Color.END}")
    
    print(f"\n{Color.BOLD}{'='*80}{Color.END}")
    print(f"{Color.GREEN}✓ Complete! Check files:{Color.END}")
    print(f"  - Full data: {Color.CYAN}{output_csv}{Color.END}")
    print(f"  - Top 15:    {Color.CYAN}{output_txt}{Color.END}")
    print(f"{Color.BOLD}{'='*80}{Color.END}\n")


if __name__ == '__main__':
    main()

