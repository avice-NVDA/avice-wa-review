#!/usr/bin/env python3
"""
Workarea Review Results Summarizer
==================================

Analyzes and summarizes results from batch workarea reviews
Works with batch_review.py output (reads from batch_review_results/)
"""

import os
import re
from datetime import datetime
from pathlib import Path

def extract_design_info(content):
    """Extract key design information from review content"""
    info = {
        'unit': 'Unknown',
        'tag': 'Unknown',
        'ipo': 'Unknown',
        'dc_runtime': 'Unknown',
        'removed_registers': 'Unknown',
        'clock_gates_removed': False,
        'synthesis_complete': False,
        'pnr_complete': False,
        'postroute_complete': False,
        'clock_analysis_complete': False,
        'formal_complete': False,
        'star_complete': False,
        'pt_complete': False,
        'pv_complete': False,
        'eco_complete': False,
        'release_complete': False,
        'errors': []
    }
    
    # Extract unit name
    unit_match = re.search(r'UNIT: (\w+)', content)
    if unit_match:
        info['unit'] = unit_match.group(1)
    
    # Extract tag
    tag_match = re.search(r'TAG: (.+)', content)
    if tag_match:
        info['tag'] = tag_match.group(1)
    
    # Extract IPO
    ipo_match = re.search(r'IPO: (\w+)', content)
    if ipo_match:
        info['ipo'] = ipo_match.group(1)
    
    # Extract DC runtime
    dc_match = re.search(r'DC runtime: ([\d.]+)', content)
    if dc_match:
        info['dc_runtime'] = dc_match.group(1)
    
    # Extract removed registers
    reg_match = re.search(r'Removed registers: (\d+)', content)
    if reg_match:
        info['removed_registers'] = reg_match.group(1)
    
    # Check for clock gates removed
    if 'Clock gates removed: Total clock gates removed' in content:
        info['clock_gates_removed'] = True
    
    # Check completion status
    if 'Synthesis (DC)' in content and 'Report:' in content:
        info['synthesis_complete'] = True
    
    if 'Place & Route (PnR)' in content or 'Post-Route Analysis' in content:
        info['pnr_complete'] = True
    
    if 'Post-Route Analysis' in content and 'Power Summary:' in content:
        info['postroute_complete'] = True
    
    if 'Clock Analysis' in content and 'Innvou Clock Analysis:' in content:
        info['clock_analysis_complete'] = True
    
    if 'Formal Verification' in content and 'No formal verification logs found' not in content:
        info['formal_complete'] = True
    
    if 'Parasitic Extraction (Star)' in content and 'SPEF File:' in content:
        info['star_complete'] = True
    
    if 'Signoff Timing (PT)' in content and 'All Violators:' in content and 'File not found' not in content:
        info['pt_complete'] = True
    
    if 'Physical Verification (PV)' in content and ('LVS Errors:' in content or 'DRC Errors:' in content):
        info['pv_complete'] = True
    
    if 'ECO Analysis' in content and 'ECO loops were done' in content and '0 ECO loops' not in content:
        info['eco_complete'] = True
    
    if 'Block Release' in content and 'No release was done' not in content:
        info['release_complete'] = True
    
    # Check for errors
    if 'Error during review:' in content:
        error_match = re.search(r'Error during review: (.+)', content)
        if error_match:
            info['errors'].append(error_match.group(1))
    
    return info

def analyze_results():
    """Analyze all review results"""
    results_dir = "batch_review_results"
    
    if not os.path.exists(results_dir):
        print("❌ No results directory found")
        return
    
    results = []
    
    # Process each result file
    for filename in os.listdir(results_dir):
        if filename.endswith('_review.txt'):
            filepath = os.path.join(results_dir, filename)
            workarea_name = filename.replace('_review.txt', '')
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                info = extract_design_info(content)
                info['workarea'] = workarea_name
                info['file_size'] = os.path.getsize(filepath)
                results.append(info)
                
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
    
    return results

def print_summary(results):
    """Print comprehensive summary"""
    print("=" * 100)
    print("AVICE WORKAREA BATCH REVIEW SUMMARY")
    print("=" * 100)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Workareas: {len(results)}")
    print()
    
    # Overall completion status
    stages = [
        'synthesis_complete', 'pnr_complete', 'postroute_complete', 
        'clock_analysis_complete', 'formal_complete', 'star_complete',
        'pt_complete', 'pv_complete', 'eco_complete', 'release_complete'
    ]
    
    stage_names = [
        'Synthesis', 'PnR', 'Post-Route', 'Clock Analysis',
        'Formal Verification', 'Star Extraction', 'PT Signoff',
        'Physical Verification', 'ECO', 'Block Release'
    ]
    
    print("OVERALL COMPLETION STATUS:")
    print("-" * 50)
    for stage, name in zip(stages, stage_names):
        completed = sum(1 for r in results if r[stage])
        percentage = (completed / len(results)) * 100 if results else 0
        status = "✅" if completed == len(results) else "⚠️" if completed > 0 else "❌"
        print(f"{status} {name:20} {completed:2}/{len(results)} ({percentage:5.1f}%)")
    
    print()
    
    # Individual workarea details
    print("INDIVIDUAL WORKAREA STATUS:")
    print("-" * 100)
    print(f"{'Workarea':<50} {'Unit':<8} {'IPO':<10} {'Regs':<6} {'Status':<20}")
    print("-" * 100)
    
    for result in results:
        workarea = result['workarea'][:47] + "..." if len(result['workarea']) > 50 else result['workarea']
        unit = result['unit'][:7] if len(result['unit']) > 8 else result['unit']
        ipo = result['ipo'][:9] if len(result['ipo']) > 10 else result['ipo']
        regs = result['removed_registers'][:5] if len(str(result['removed_registers'])) > 6 else str(result['removed_registers'])
        
        # Determine overall status
        completed_stages = sum(1 for stage in stages if result[stage])
        if completed_stages >= 8:
            status = "✅ Complete"
        elif completed_stages >= 5:
            status = "⚠️ Partial"
        else:
            status = "❌ Incomplete"
        
        print(f"{workarea:<50} {unit:<8} {ipo:<10} {regs:<6} {status:<20}")
    
    print()
    
    # Error summary
    errors = [r for r in results if r['errors']]
    if errors:
        print("ERRORS FOUND:")
        print("-" * 50)
        for result in errors:
            print(f"❌ {result['workarea']}:")
            for error in result['errors']:
                print(f"   - {error}")
        print()
    
    # Design statistics
    print("DESIGN STATISTICS:")
    print("-" * 50)
    
    # Units
    units = [r['unit'] for r in results if r['unit'] != 'Unknown']
    if units:
        unit_counts = {}
        for unit in units:
            unit_counts[unit] = unit_counts.get(unit, 0) + 1
        print("Units:")
        for unit, count in sorted(unit_counts.items()):
            print(f"  {unit}: {count}")
    
    # Register optimization
    reg_counts = [int(r['removed_registers']) for r in results if r['removed_registers'] != 'Unknown' and r['removed_registers'].isdigit()]
    if reg_counts:
        print(f"Register Optimization:")
        print(f"  Total removed: {sum(reg_counts):,}")
        print(f"  Average per design: {sum(reg_counts)/len(reg_counts):,.0f}")
        print(f"  Range: {min(reg_counts):,} - {max(reg_counts):,}")
    
    print()
    print("=" * 100)

def main():
    """Main function"""
    results = analyze_results()
    if results:
        print_summary(results)
    else:
        print("❌ No results found to analyze")

if __name__ == "__main__":
    main()
