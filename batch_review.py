#!/usr/bin/env python3
"""
Batch Workarea Review Script
============================

Runs Avice workarea review on multiple workareas from workareas.txt
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def read_workareas(file_path):
    """Read workareas from file with IPO information"""
    workareas = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse the line: PATH|DESCRIPTION|DATE_ADDED|STATUS|IPOS
                    parts = line.split('|')
                    if len(parts) >= 5:
                        path = parts[0]
                        description = parts[1]
                        date_added = parts[2]
                        status = parts[3]
                        ipos = parts[4].split(',') if parts[4] else ['auto']
                        
                        workareas.append({
                            'path': path,
                            'description': description,
                            'date_added': date_added,
                            'status': status,
                            'ipos': ipos
                        })
                    else:
                        # Fallback for old format
                        workareas.append({
                            'path': line,
                            'description': 'Legacy workarea',
                            'date_added': 'Unknown',
                            'status': 'ACTIVE',
                            'ipos': ['auto']
                        })
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        sys.exit(1)
    return workareas

def run_review(workarea_path, output_file, ipo=None, skip_validation=False):
    """Run review on a single workarea with optional IPO"""
    print(f"\n{'='*80}")
    if ipo and ipo != 'auto':
        print(f"REVIEWING: {workarea_path} (IPO: {ipo})")
    else:
        print(f"REVIEWING: {workarea_path} (Auto-detect IPO)")
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
    
    parser = argparse.ArgumentParser(description="Batch workarea review tool")
    parser.add_argument("workareas_file", nargs="?", default="workareas.txt",
                       help="Path to workareas.txt file (default: workareas.txt)")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip workarea validation for all workareas")
    parser.add_argument("--output-dir", default="batch_review_results",
                       help="Output directory for results (default: batch_review_results)")
    
    args = parser.parse_args()
    workareas_file = args.workareas_file
    output_dir = args.output_dir
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read workareas
    workareas = read_workareas(workareas_file)
    print(f"Found {len(workareas)} workareas to review")
    
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
            success = run_review(workarea_path, output_file, ipo, args.skip_validation)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
    
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

if __name__ == "__main__":
    main()
