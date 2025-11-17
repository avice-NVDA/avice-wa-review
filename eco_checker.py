#!/usr/bin/env python3
"""
===============================================================================
     +===+ +--+ +--+ +=+ +===+ +===+
     |   | |  | |  | | | |     |    
     |===| |  +-+  | | | |     |=== 
     |   |  |     |  | | |     |    
     |   |   +---+   +=+ +===+ +===+                                 
           ~ Alon Vice Tools ~
Copyright (c) 2025 Alon Vice (avice)
All rights reserved.
This script is the intellectual property of Alon Vice.
For permissions and licensing, contact: avice@nvidia.com
===============================================================================

ECO Checker - Standalone ECO Validation Utility

DESCRIPTION:
    Standalone tool for validating ECO TCL files against design rules.
    Performs comprehensive checks for:
      - instNotAllowedOnClocks: Non-allowed cells on clock network
      - DontUse cells: Cells that shouldn't be used anywhere
      - ClockCellsOnData: Clock cells on data paths (informational)
    
    Features smart workarea auto-detection from ECO file location.

USAGE:
    # Auto-detect workarea from ECO location (recommended)
    eco_checker.py /path/to/workarea/signoff_flow/auto_pt/my_eco.tcl
    
    # Multiple units (each auto-detects its own workarea)
    eco_checker.py \\
        /path/to/pmux_wa/signoff_flow/auto_pt/pmux_eco.tcl \\
        /path/to/ccorea_wa/unit_scripts/ccorea_eco.tcl
    
    # External ECOs (use specific workarea as reference)
    eco_checker.py /shared/external_ecos/*.tcl --workarea /path/to/reference_wa
    
    # Explicit reference files (no workarea needed)
    eco_checker.py eco.tcl \\
        --clock-tree /path/ClockTree.rpt \\
        --beflow-config /path/beflow_config.yaml \\
        --dont-use /path/dont_use_patterns.tcl

ARGUMENTS:
    eco_files           : ECO TCL file(s) to validate (required)
    --workarea, -w      : Workarea path (overrides auto-detection)
    --clock-tree        : Path to ClockTree.rpt (overrides workarea)
    --beflow-config     : Path to beflow_config.yaml (overrides workarea)
    --dont-use          : Path to dont_use patterns file (overrides workarea)
    --skip-clock-check  : Skip instNotAllowedOnClocks check
    --skip-dontuse-check: Skip DontUse cells check
    --skip-clock-data   : Skip clock cells on data paths check
    --quiet, -q         : Minimal output (summary only)
    --verbose, -v       : Detailed output with all violations
    --no-color          : Disable colored output
    --strict            : Exit code 1 even for informational warnings

EXIT CODES:
    0 : All checks passed
    1 : Violations found
    2 : Error (missing files, parse errors, etc.)

EXAMPLES:
    # Check ECO with auto-detection
    eco_checker.py my_eco.tcl
    
    # Check multiple ECOs from different units
    eco_checker.py pmux_eco.tcl ccorea_eco.tcl fdb_eco.tcl
    
    # Check external ECOs with reference workarea
    eco_checker.py /tmp/radu_eco.tcl --workarea /path/to/pmux/workarea
    
    # Quiet mode (summary only)
    eco_checker.py *.tcl --quiet

AUTHOR: Alon Vice (avice@nvidia.com)
DATE: November 6, 2025
===============================================================================
"""

import sys
import os
import re
import argparse
from collections import defaultdict
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eco_checker_lib import ECOCheckerLib, Color


class ColorHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter with color coding for better readability"""
    
    def _colors_enabled(self):
        """Check if colors are enabled by checking if Color.RESET is not empty"""
        return bool(Color.RESET)
    
    def _format_usage(self, usage, actions, groups, prefix):
        """Format usage line with color"""
        usage_text = super()._format_usage(usage, actions, groups, prefix)
        if self._colors_enabled():
            # Color the word 'usage:' in cyan
            usage_text = usage_text.replace('usage:', f'{Color.CYAN}usage:{Color.RESET}')
        return usage_text
    
    def _format_action(self, action):
        """Format each argument with color"""
        result = super()._format_action(action)
        if self._colors_enabled() and action.option_strings:
            # Color option strings (--workarea, -w, etc.) in yellow
            # Sort by length (longest first) to avoid partial replacements
            for opt_str in sorted(action.option_strings, key=len, reverse=True):
                # Use word boundaries to avoid partial matches
                # Match the option string followed by space, comma, or end of line
                pattern = re.escape(opt_str) + r'(?=[\s,]|$)'
                result = re.sub(pattern, f'{Color.YELLOW}{opt_str}{Color.RESET}', result, count=1)
        return result
    
    def add_usage(self, usage, actions, groups, prefix=None):
        """Override to add color to usage"""
        if prefix is None:
            prefix = 'usage: '
        return super().add_usage(usage, actions, groups, prefix)
    
    def format_help(self):
        """Format the entire help message with colors"""
        help_text = super().format_help()
        
        if self._colors_enabled():
            # Color section headers
            help_text = help_text.replace('positional arguments:', f'{Color.CYAN}positional arguments:{Color.RESET}')
            help_text = help_text.replace('options:', f'{Color.CYAN}options:{Color.RESET}')
            help_text = help_text.replace('Examples:', f'{Color.CYAN}Examples:{Color.RESET}')
            help_text = help_text.replace('Author:', f'{Color.MAGENTA}Author:{Color.RESET}')
            
            # Color the description
            if 'Standalone ECO file validator' in help_text:
                help_text = help_text.replace(
                    'Standalone ECO file validator with smart workarea detection',
                    f'{Color.GREEN}Standalone ECO file validator with smart workarea detection{Color.RESET}'
                )
        
        return help_text


def print_header():
    """Print tool header"""
    print("=" * 79)
    print("ECO Checker - Standalone ECO Validation Utility")
    print("=" * 79)


def print_summary_separator():
    """Print summary separator"""
    print("\n" + "=" * 79)
    print("SUMMARY")
    print("=" * 79)


def format_violations_by_type(violations: List[Dict], check_type: str) -> str:
    """
    Format violations grouped by cell type
    
    Args:
        violations: List of violation dicts
        check_type: Check type name for display
    
    Returns:
        Formatted string
    """
    if not violations:
        return ""
    
    # Group by cell type
    by_type = defaultdict(list)
    for v in violations:
        by_type[v['cell_type']].append(v)
    
    output = []
    output.append(f"\n[{check_type}] Found {len(violations)} violation(s):")
    
    for cell_type, viols in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        output.append(f"  Cell Type '{cell_type}': {len(viols)} instance(s)")
        
        # Show first 3 examples
        for v in viols[:3]:
            output.append(f"    Instance: {v['instance']}")
            if v.get('prev_instance'):
                output.append(f"    Previous: {v['prev_instance']} (on clock network)")
            output.append(f"    Command:  {v['command'][:80]}...")
        
        if len(viols) > 3:
            output.append(f"    ... and {len(viols) - 3} more instance(s)")
    
    return "\n".join(output)


def main():
    # Check if --no-color flag is present before creating parser
    # (needed for colored help output)
    if '--no-color' in sys.argv:
        Color.disable()
    
    parser = argparse.ArgumentParser(
        description='Standalone ECO file validator with smart workarea detection',
        formatter_class=ColorHelpFormatter,
        epilog='''
Examples:
  # Auto-detect workarea from ECO location (recommended)
  eco_checker.py /path/to/workarea/signoff_flow/auto_pt/my_eco.tcl
  
  # Multiple units (each auto-detects its own workarea)
  eco_checker.py \\
      /path/to/pmux_wa/signoff_flow/auto_pt/pmux_eco.tcl \\
      /path/to/ccorea_wa/unit_scripts/ccorea_eco.tcl
  
  # External ECOs (use specific workarea as reference)
  eco_checker.py /shared/external_ecos/*.tcl --workarea /path/to/reference_wa
  
  # Explicit reference files (no workarea)
  eco_checker.py eco.tcl \\
      --clock-tree /path/ClockTree.rpt \\
      --beflow-config /path/beflow_config.yaml

Author: Alon Vice (avice@nvidia.com)
        '''
    )
    
    # Required arguments
    parser.add_argument('eco_files', nargs='+', help='ECO TCL file(s) to validate')
    
    # Discovery options
    parser.add_argument('--workarea', '-w', help='Workarea path for reference files (overrides auto-detection)')
    
    # Explicit reference files
    parser.add_argument('--clock-tree', help='Path to ClockTree.rpt')
    parser.add_argument('--beflow-config', help='Path to beflow_config.yaml')
    parser.add_argument('--dont-use', help='Path to dont_use_cell_patterns.tcl or gl-check.log')
    
    # Check options
    parser.add_argument('--skip-clock-check', action='store_true', help='Skip instNotAllowedOnClocks check')
    parser.add_argument('--skip-dontuse-check', action='store_true', help='Skip DontUse cells check')
    parser.add_argument('--skip-clock-data', action='store_true', help='Skip clock cells on data paths check')
    
    # Output options
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output (summary only)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Detailed output with all violations')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--strict', action='store_true', help='Exit code 1 even for informational warnings')
    
    args = parser.parse_args()
    
    # Disable colors if requested
    if args.no_color:
        Color.disable()
    
    # Print header
    if not args.quiet:
        print_header()
    
    # Initialize library
    lib = ECOCheckerLib(
        workarea=args.workarea,
        clock_tree_rpt=args.clock_tree,
        beflow_config=args.beflow_config,
        dont_use_patterns=args.dont_use,
        verbose=args.verbose
    )
    
    # Process each ECO file
    total_commands = 0
    total_violations = {
        'dontuse': [],
        'clock': [],
        'clock_data': []
    }
    files_with_violations = set()
    
    if not args.quiet:
        print(f"Analyzing {len(args.eco_files)} ECO file(s)...\n")
    
    for idx, eco_file in enumerate(args.eco_files, 1):
        if not os.path.exists(eco_file):
            print(f"{Color.RED}[ERROR] File not found: {eco_file}{Color.RESET}")
            continue
        
        eco_name = os.path.basename(eco_file)
        
        if not args.quiet:
            print(f"[{idx}/{len(args.eco_files)}] {eco_name}")
            print("-" * 70)
        
        # Discover reference files
        refs = lib.discover_reference_files(eco_file, args.workarea)
        
        if not args.quiet and args.verbose:
            print(f"  ECO Location: {os.path.abspath(eco_file)}")
            if refs['workarea']:
                print(f"  Workarea:     {refs['workarea']} (auto-detected)")
            print(f"  Reference Files:")
            print(f"    ClockTree.rpt:  {refs['clock_tree_rpt'] or 'NOT FOUND'}")
            print(f"    beflow_config:  {refs['beflow_config'] or 'NOT FOUND'}")
            print(f"    dont_use:       {refs['dont_use_patterns'] or 'NOT FOUND'}")
            print()
        
        # Check if we have all required reference files
        missing_refs = []
        if not args.skip_clock_check and not refs['clock_tree_rpt']:
            missing_refs.append('ClockTree.rpt')
        if not args.skip_clock_check and not refs['beflow_config']:
            missing_refs.append('beflow_config.yaml')
        if not args.skip_dontuse_check and not refs['dont_use_patterns']:
            missing_refs.append('dont_use patterns')
        
        if missing_refs and not refs['workarea']:
            print(f"{Color.RED}[ERROR] Could not auto-detect workarea for: {eco_file}{Color.RESET}")
            print(f"  Missing reference files: {', '.join(missing_refs)}")
            print(f"\nSuggestions:")
            print(f"  1. Copy ECO file to your workarea (e.g., signoff_flow/auto_pt/)")
            print(f"  2. Specify workarea explicitly: --workarea /path/to/workarea")
            print(f"  3. Provide reference files directly:")
            print(f"     --clock-tree /path/ClockTree.rpt \\")
            print(f"     --beflow-config /path/beflow_config.yaml \\")
            print(f"     --dont-use /path/dont_use_patterns.tcl")
            print()
            continue
        
        # Parse ECO file
        eco_commands, cmd_breakdown = lib.parse_eco_file(eco_file)
        total_commands += len(eco_commands)
        
        if not args.quiet:
            # Show workarea being used (full path)
            if refs['workarea']:
                print(f"  Workarea:     {refs['workarea']}")
            
            # Show command breakdown
            cmd_str = ", ".join([f"{k}:{v}" for k, v in sorted(cmd_breakdown.items(), 
                                                               key=lambda x: x[1], reverse=True)[:5]])
            print(f"  Commands:     {len(eco_commands)} ({cmd_str})")
        
        # Run checks
        file_violations = {'dontuse': [], 'clock': [], 'clock_data': []}
        check_status = {'dontuse': None, 'clock': None, 'clock_data': None}  # None, 'PASS', 'FAIL', 'SKIPPED'
        
        # Check 1: DontUse cells
        if args.skip_dontuse_check:
            check_status['dontuse'] = 'SKIPPED'
        elif not refs['dont_use_patterns']:
            check_status['dontuse'] = 'SKIPPED'
        else:
            patterns = lib.parse_dont_use_patterns(refs['dont_use_patterns'])
            file_violations['dontuse'] = lib.check_dont_use_cells(eco_commands, patterns)
            total_violations['dontuse'].extend(file_violations['dontuse'])
            check_status['dontuse'] = 'FAIL' if file_violations['dontuse'] else 'PASS'
        
        # Check 2: instNotAllowedOnClocks
        if args.skip_clock_check:
            check_status['clock'] = 'SKIPPED'
        elif not refs['clock_tree_rpt'] or not refs['beflow_config']:
            check_status['clock'] = 'SKIPPED'
        else:
            clock_instances = lib.parse_clock_tree_cells(refs['clock_tree_rpt'])
            allowed_patterns = lib.parse_allowed_clock_patterns(refs['beflow_config'])
            file_violations['clock'] = lib.check_inst_not_allowed_on_clocks(
                eco_commands, clock_instances, allowed_patterns
            )
            total_violations['clock'].extend(file_violations['clock'])
            check_status['clock'] = 'FAIL' if file_violations['clock'] else 'PASS'
        
        # Check 3: Clock cells on data paths
        if args.skip_clock_data:
            check_status['clock_data'] = 'SKIPPED'
        elif not refs['clock_tree_rpt'] or not refs['beflow_config']:
            check_status['clock_data'] = 'SKIPPED'
        else:
            clock_instances = lib.parse_clock_tree_cells(refs['clock_tree_rpt'])
            allowed_patterns = lib.parse_allowed_clock_patterns(refs['beflow_config'])
            file_violations['clock_data'] = lib.check_clock_cells_on_data(
                eco_commands, clock_instances, allowed_patterns
            )
            total_violations['clock_data'].extend(file_violations['clock_data'])
            check_status['clock_data'] = 'INFO'  # Always informational
        
        # Display results
        if not args.quiet:
            # DontUse
            if check_status['dontuse'] == 'SKIPPED':
                missing_file = 'dont_use patterns' if not refs['dont_use_patterns'] else 'user requested'
                print(f"  {Color.GRAY}[SKIPPED] DontUse: No reference files ({missing_file}){Color.RESET}")
            elif file_violations['dontuse']:
                print(f"  {Color.RED}[CRITICAL] DontUse: {len(file_violations['dontuse'])} violations{Color.RESET}")
                files_with_violations.add(eco_name)
            else:
                print(f"  {Color.GREEN}[OK] DontUse: 0 violations{Color.RESET}")
            
            # instNotAllowedOnClocks
            if check_status['clock'] == 'SKIPPED':
                missing = []
                if not refs['clock_tree_rpt']: missing.append('ClockTree.rpt')
                if not refs['beflow_config']: missing.append('beflow_config.yaml')
                missing_str = ', '.join(missing) if missing else 'user requested'
                print(f"  {Color.GRAY}[SKIPPED] instNotAllowedOnClocks: No reference files ({missing_str}){Color.RESET}")
            elif file_violations['clock']:
                print(f"  {Color.YELLOW}[WARN] instNotAllowedOnClocks: {len(file_violations['clock'])} violations{Color.RESET}")
                files_with_violations.add(eco_name)
            else:
                print(f"  {Color.GREEN}[OK] instNotAllowedOnClocks: 0 violations{Color.RESET}")
            
            # Clock cells on data
            if check_status['clock_data'] == 'SKIPPED':
                missing = []
                if not refs['clock_tree_rpt']: missing.append('ClockTree.rpt')
                if not refs['beflow_config']: missing.append('beflow_config.yaml')
                missing_str = ', '.join(missing) if missing else 'user requested'
                print(f"  {Color.GRAY}[SKIPPED] ClockCellsOnData: No reference files ({missing_str}){Color.RESET}")
            elif file_violations['clock_data']:
                print(f"  {Color.CYAN}[INFO] ClockCellsOnData: {len(file_violations['clock_data'])} instances{Color.RESET}")
            else:
                print(f"  {Color.CYAN}[INFO] ClockCellsOnData: 0 instances{Color.RESET}")
            
            print()
    
    # Print detailed violations if requested
    if args.verbose and (total_violations['dontuse'] or total_violations['clock']):
        print("\n" + "=" * 79)
        print("DETAILED VIOLATIONS")
        print("=" * 79)
        
        if total_violations['dontuse']:
            print(format_violations_by_type(total_violations['dontuse'], "DontUse Cells"))
        
        if total_violations['clock']:
            print(format_violations_by_type(total_violations['clock'], "instNotAllowedOnClocks"))
    
    # Print summary
    print_summary_separator()
    print(f"Total Files:                 {len(args.eco_files)}")
    print(f"Total ECO Commands:          {total_commands}")
    print()
    print("Violations by Category:")
    
    # DontUse
    if total_violations['dontuse']:
        print(f"  {Color.RED}[CRITICAL] DontUse Cells:               {len(total_violations['dontuse'])}{Color.RESET}")
    else:
        print(f"  {Color.GREEN}[OK] DontUse Cells:                     0{Color.RESET}")
    
    # instNotAllowedOnClocks
    if total_violations['clock']:
        print(f"  {Color.YELLOW}[WARN] instNotAllowedOnClocks:         {len(total_violations['clock'])} (across {len(files_with_violations)} files){Color.RESET}")
    else:
        print(f"  {Color.GREEN}[OK] instNotAllowedOnClocks:            0{Color.RESET}")
    
    # Clock cells on data
    if total_violations['clock_data']:
        print(f"  {Color.CYAN}[INFO] ClockCellsOnData:                {len(total_violations['clock_data'])} (informational){Color.RESET}")
    else:
        print(f"  {Color.GREEN}[INFO] ClockCellsOnData:                 0{Color.RESET}")
    
    if files_with_violations:
        print(f"\nAffected Files:")
        for fname in sorted(files_with_violations):
            print(f"  {fname}")
    
    print("=" * 79)
    
    # Determine exit code
    has_violations = bool(total_violations['dontuse'] or total_violations['clock'])
    has_warnings = bool(total_violations['clock_data'])
    
    if has_violations:
        print(f"{Color.RED}Exit code: 1 (violations found){Color.RESET}")
        return 1
    elif args.strict and has_warnings:
        print(f"{Color.YELLOW}Exit code: 1 (informational warnings in strict mode){Color.RESET}")
        return 1
    else:
        print(f"{Color.GREEN}Exit code: 0 (all checks passed){Color.RESET}")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}[INTERRUPTED] Aborted by user{Color.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Color.RED}[ERROR] Unexpected error: {e}{Color.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

