#!/usr/bin/env python3
"""
Extract Cell Counts for All AGUR Units (Using avice_wa_review)

This script leverages the existing avice_wa_review.py tool to extract cell count
information from all AGUR units by running it in PnR-only mode.

Strategy:
1. Read all units from AGUR_UNITS_TABLE.csv
2. Run avice_wa_review.py -u <unit> -s pnr for each unit (parallel)
3. Parse the PnR output to extract cell count
4. Generate top 15 report

Author: Alon Vice (avice@nvidia.com)
Date: January 4, 2026
"""

import os
import csv
import re
import subprocess
from typing import Dict, List, Optional
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


def extract_cell_count_for_unit(unit: str, chiplet: str) -> Optional[Dict]:
    """Extract cell count for a unit by running avice_wa_review
    
    Args:
        unit: Unit name (e.g., 'fdb', 'pmux')
        chiplet: Chiplet name
    
    Returns:
        Dict with unit info and cell count, or None if not found
    """
    try:
        # Run avice_wa_review in PnR-only mode with auto-approve
        script_path = "/home/avice/scripts/avice_wa_review_launcher.csh"
        cmd = f"{script_path} -u {unit} -s pnr"
        
        # Run with timeout (max 2 minutes per unit)
        result = subprocess.run(cmd, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True,
                               timeout=120)
        
        if result.returncode == 0 and result.stdout:
            # Parse output for cell count
            # Look for pattern: "Cell Counts     Cell: 1,216,941 |"
            cell_match = re.search(r'Cell Counts\s+Cell:\s*([\d,]+)', result.stdout)
            if cell_match:
                cell_count_str = cell_match.group(1).replace(',', '')
                cell_count = int(cell_count_str)
                
                # Also try to get workarea path from output
                wa_match = re.search(r'Workarea:\s*(.+)', result.stdout)
                workarea_path = wa_match.group(1).strip() if wa_match else 'N/A'
                
                return {
                    'unit': unit,
                    'chiplet': chiplet,
                    'cell_count': cell_count,
                    'workarea_path': workarea_path
                }
    
    except subprocess.TimeoutExpired:
        pass  # Timeout - unit may not be accessible
    except (ValueError, Exception):
        pass  # Parsing error or other issue
    
    return None


def load_units_from_csv(csv_path: str) -> List[Dict]:
    """Load units from AGUR_UNITS_TABLE.csv
    
    Returns:
        List of unit dictionaries with unit and chiplet
    """
    units = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            units.append({
                'unit': row['UNIT'],
                'chiplet': row['CHIPLET']
            })
    
    return units


def main():
    """Main execution"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'AGUR_UNITS_TABLE.csv')
    output_csv = os.path.join(script_dir, 'AGUR_CELL_COUNTS.csv')
    output_txt = os.path.join(script_dir, 'AGUR_CELL_COUNTS_TOP15.txt')
    
    print(f"{Color.BOLD}{'='*80}{Color.END}")
    print(f"{Color.CYAN}{Color.BOLD}AGUR Units Cell Count Extraction (via avice_wa_review){Color.END}")
    print(f"{Color.BOLD}{'='*80}{Color.END}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load units
    print(f"{Color.YELLOW}Loading units from CSV...{Color.END}")
    units = load_units_from_csv(csv_path)
    print(f"{Color.GREEN}✓ Loaded {len(units)} units{Color.END}\n")
    
    # Extract cell counts in parallel (faster!)
    print(f"{Color.YELLOW}Extracting cell counts (parallel processing)...{Color.END}")
    print(f"{Color.CYAN}Running avice_wa_review.py for each unit (PnR section only)...{Color.END}")
    print(f"{Color.CYAN}This will take several minutes (~2 min per unit, 10 parallel)...{Color.END}\n")
    
    results = []
    processed = 0
    found = 0
    
    # Use ThreadPoolExecutor for parallel extraction (max 10 concurrent threads)
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_unit = {
            executor.submit(extract_cell_count_for_unit, u['unit'], u['chiplet']): u
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
                    print(f"{Color.GREEN}[{processed:2d}/{len(units)}] ✓ {result['unit']:15s} ({result['chiplet']:<7s}) - {result['cell_count']:>10,} cells{Color.END}")
                else:
                    print(f"{Color.RED}[{processed:2d}/{len(units)}] ✗ {unit_info['unit']:15s} ({unit_info['chiplet']:<7s}) - No data{Color.END}")
            except Exception as e:
                print(f"{Color.RED}[{processed:2d}/{len(units)}] ✗ {unit_info['unit']:15s} ({unit_info['chiplet']:<7s}) - Error: {e}{Color.END}")
    
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
        writer = csv.DictWriter(f, fieldnames=['unit', 'chiplet', 'cell_count', 'workarea_path'])
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






