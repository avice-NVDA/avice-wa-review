#!/usr/bin/env python3
"""
Batch Workarea Review Script
============================

Runs Avice workarea review on multiple workareas from AGUR_UNITS_TABLE.csv
Uses the authoritative AGUR units database from central block release area
"""

import os
import sys
import subprocess
import csv
import glob
import shutil
from datetime import datetime
from pathlib import Path

def read_workareas(file_path):
    """Read workareas from AGUR_UNITS_TABLE.csv
    
    CSV Format: UNIT,CHIPLET,RELEASED_WA_PATH,RTL_TAG,RELEASE_TYPES,RELEASE_USER,RELEASE_TIMESTAMP
    """
    workareas = []
    try:
        with open(file_path, 'r') as f:
            csv_reader = csv.reader(f)
            
            # Skip header line
            header = next(csv_reader)
            
            for line_num, row in enumerate(csv_reader, start=2):
                if not row or (len(row) > 0 and row[0].startswith('#')):
                    continue
                
                # Parse CSV: UNIT,CHIPLET,RELEASED_WA_PATH,RTL_TAG,RELEASE_TYPES,RELEASE_USER,RELEASE_TIMESTAMP
                if len(row) >= 7:
                    unit = row[0].strip()
                    chiplet = row[1].strip()
                    path = row[2].strip()
                    rtl_tag = row[3].strip()
                    release_types = row[4].strip()
                    release_user = row[5].strip()
                    release_timestamp = row[6].strip() if len(row) > 6 else ''
                    
                    # Convert release timestamp to date (YYYY/MM/DD HH:MM:SS -> YYYY-MM-DD)
                    try:
                        date_added = release_timestamp.split()[0].replace('/', '-')
                    except:
                        date_added = release_timestamp
                    
                    workareas.append({
                        'path': path,
                        'unit': unit,
                        'chiplet': chiplet,
                        'description': f"{unit} ({chiplet}) - Released by {release_user}",
                        'date_added': date_added,
                        'status': 'ACTIVE',
                        'ipos': ['auto'],  # Auto-detect IPO from workarea
                        'rtl_tag': rtl_tag,
                        'release_user': release_user,
                        'release_types': release_types
                    })
                else:
                    print(f"Warning: Line {line_num} has {len(row)} fields (expected 7+), skipping")
                    
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        print(f"Expected path: {os.path.abspath(file_path)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    return workareas

def organize_leftover_htmls():
    """Organize any HTML files left in root directory after review"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_dir = os.path.join(script_dir, "html")
        os.makedirs(html_dir, exist_ok=True)
        
        # Find all HTML files in script directory
        html_files = glob.glob(os.path.join(script_dir, "*.html"))
        
        if html_files:
            moved_count = 0
            for html_file in html_files:
                try:
                    filename = os.path.basename(html_file)
                    dest_path = os.path.join(html_dir, filename)
                    shutil.move(html_file, dest_path)
                    moved_count += 1
                except:
                    pass
            
            if moved_count > 0:
                print(f"📁 Organized {moved_count} HTML file(s) into html/ folder")
    except:
        pass  # Don't fail batch run if cleanup fails

def run_review(workarea_path, output_file, ipo=None, skip_validation=False, section=None):
    """Run review on a single workarea with optional IPO and section"""
    print(f"\n{'='*80}")
    if ipo and ipo != 'auto':
        print(f"REVIEWING: {workarea_path} (IPO: {ipo})")
    else:
        print(f"REVIEWING: {workarea_path} (Auto-detect IPO)")
    if section:
        print(f"SECTION: {section}")
    if skip_validation:
        print(f"SKIPPING VALIDATION: {skip_validation}")
    print(f"{'='*80}")
    
    # Check if workarea exists
    if not os.path.isdir(workarea_path):
        print(f"❌ ERROR: Workarea does not exist: {workarea_path}")
        return False
    
    # Run the review using the C-shell launcher
    try:
        # Use the C-shell launcher as per architecture standards
        launcher_path = "/home/avice/scripts/avice_wa_review_launcher.csh"
        cmd = [launcher_path, workarea_path]
        if ipo and ipo != 'auto':
            cmd.append(ipo)
        if section:
            cmd.extend(['-s', section])
        if skip_validation:
            cmd.append("--skip-validation")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        
        # Decode output
        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')
        
        # Write output to file
        with open(output_file, 'w') as f:
            f.write(f"# Review for: {workarea_path}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Command: {' '.join(cmd)}\n")
            f.write(f"# Return code: {result.returncode}\n\n")
            f.write("STDOUT:\n")
            f.write(stdout)
            f.write("\n\nSTDERR:\n")
            f.write(stderr)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: Review completed for {os.path.basename(workarea_path)}")
            return True
        else:
            print(f"❌ ERROR: Review failed for {os.path.basename(workarea_path)} (return code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: Review timed out for {os.path.basename(workarea_path)}")
        return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    # Get script directory to locate AGUR_UNITS_TABLE.csv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_units_table = os.path.join(script_dir, "agur_release_tracking", "AGUR_UNITS_TABLE.csv")
    
    parser = argparse.ArgumentParser(
        description="Batch workarea review tool - Uses AGUR units database",
        epilog="Example: python3 batch_review.py --output-dir my_results"
    )
    parser.add_argument("workareas_file", nargs="?", default=default_units_table,
                       help=f"Path to units CSV file (default: {default_units_table})")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip workarea validation for all workareas")
    parser.add_argument("--output-dir", default="batch_review_results",
                       help="Output directory for results (default: batch_review_results)")
    parser.add_argument("--units", nargs="+",
                       help="Filter to specific units (e.g., --units prt ccorea fdb)")
    parser.add_argument("--chiplet",
                       help="Filter to specific chiplet (e.g., --chiplet CPORT)")
    parser.add_argument("--limit", type=int,
                       help="Limit number of units to process (e.g., --limit 5 for quick testing)")
    parser.add_argument("--random", action="store_true",
                       help="Randomize unit order (useful with --limit for varied testing)")
    parser.add_argument("--section", "-s",
                       help="Test specific section only (e.g., --section pnr, -s formal)")
    
    args = parser.parse_args()
    workareas_file = args.workareas_file
    output_dir = args.output_dir
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read workareas
    workareas = read_workareas(workareas_file)
    print(f"Loaded {len(workareas)} units from database")
    
    # Apply filters
    if args.units:
        unit_names = [u.lower() for u in args.units]
        workareas = [wa for wa in workareas if wa['unit'].lower() in unit_names]
        print(f"Filtered to {len(workareas)} unit(s): {', '.join(args.units)}")
    
    if args.chiplet:
        workareas = [wa for wa in workareas if wa['chiplet'].upper() == args.chiplet.upper()]
        print(f"Filtered to {len(workareas)} unit(s) in {args.chiplet} chiplet")
    
    if args.random:
        import random
        random.shuffle(workareas)
        print(f"Randomized unit order")
    
    if args.limit:
        workareas = workareas[:args.limit]
        print(f"Limited to first {len(workareas)} unit(s)")
    
    if not workareas:
        print("No units matched the filters. Exiting.")
        sys.exit(0)
    
    print(f"\nWill process {len(workareas)} workarea(s)")
    
    # Summary tracking
    results = {
        'total': len(workareas),
        'success': 0,
        'failed': 0,
        'not_found': 0
    }
    
    # Process each workarea
    total_tests = sum(len(wa['ipos']) for wa in workareas)
    current_test = 0
    
    for i, workarea in enumerate(workareas, 1):
        workarea_path = workarea['path']
        workarea_name = os.path.basename(workarea_path)
        ipos = workarea['ipos']
        
        print(f"\n[{i}/{len(workareas)}] Processing: {workarea_name}")
        print(f"    Description: {workarea['description']}")
        print(f"    IPOs to test: {', '.join(ipos)}")
        
        # Check if workarea exists
        if not os.path.isdir(workarea_path):
            print(f"❌ NOT FOUND: {workarea_path}")
            results['not_found'] += 1
            continue
        
        # Test each IPO for this workarea
        for ipo in ipos:
            current_test += 1
            print(f"\n[{current_test}/{total_tests}] Testing IPO: {ipo}")
            
            # Create output filename
            safe_name = workarea_name.replace('/', '_').replace(' ', '_')
            ipo_suffix = f"_{ipo}" if ipo != 'auto' else ""
            output_file = os.path.join(output_dir, f"{safe_name}{ipo_suffix}_review.txt")
            
            # Run review
            success = run_review(workarea_path, output_file, ipo, args.skip_validation, args.section)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            # Organize any leftover HTML files after each review
            # (handles cases where review times out or fails before internal cleanup)
            organize_leftover_htmls()
    
    # Print summary
    print(f"\n{'='*80}")
    print("BATCH REVIEW SUMMARY")
    print(f"{'='*80}")
    print(f"Total workareas: {len(workareas)}")
    print(f"Total tests run: {total_tests}")
    print(f"✅ Successful: {results['success']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"🔍 Not found: {results['not_found']}")
    print(f"📁 Results saved in: {output_dir}/")
    print(f"{'='*80}")
    
    # Print detailed workarea summary
    print(f"\nDETAILED WORKAREA SUMMARY:")
    print(f"{'='*80}")
    for wa in workareas:
        status_icon = "✅" if os.path.isdir(wa['path']) else "❌"
        print(f"{status_icon} {os.path.basename(wa['path'])}: {', '.join(wa['ipos'])}")
    print(f"{'='*80}")
    
    # Final cleanup: organize any remaining HTML files
    organize_leftover_htmls()

if __name__ == "__main__":
    main()
