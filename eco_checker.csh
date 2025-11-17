#!/bin/csh -f
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
#
# Script: eco_checker.csh
# Purpose: Launcher script for ECO Checker - Standalone ECO Validation Utility
#
# Description:
#   C-shell wrapper for eco_checker.py that provides a simple, zero-setup
#   interface for validating ECO TCL files. This launcher ensures the correct
#   Python environment is used and passes all arguments through to the Python
#   script.
#
# Usage:
#   /home/scratch.avice_vlsi/cursor/avice_wa_review/eco_checker.csh <eco_file(s)> [options]
#
# Examples:
#   # Check single ECO file (workarea auto-detected)
#   /home/scratch.avice_vlsi/cursor/avice_wa_review/eco_checker.csh my_eco.tcl
#
#   # Check multiple ECO files
#   /home/scratch.avice_vlsi/cursor/avice_wa_review/eco_checker.csh *.tcl
#
#   # Check external ECOs with explicit workarea
#   /home/scratch.avice_vlsi/cursor/avice_wa_review/eco_checker.csh /path/to/*.tcl --workarea /path/to/wa
#
#   # Verbose mode
#   /home/scratch.avice_vlsi/cursor/avice_wa_review/eco_checker.csh my_eco.tcl --verbose
#
# Prerequisites:
#   - Python 3.6+ (uses 3.11.9 build at /home/utils/Python/builds/3.11.9-20250715)
#   - eco_checker.py and eco_checker_lib.py in the same directory
#
# Output:
#   - Terminal output with color-coded validation results
#   - Exit code: 0 (pass), 1 (violations), 2 (error)
#
# Author: Alon Vice (avice@nvidia.com)
# Date: November 6, 2025
#===============================================================================

# Get the directory where this script is located
set SCRIPT_DIR = `dirname $0`
set SCRIPT_DIR = `cd $SCRIPT_DIR && pwd`

# Python executable path
set PYTHON_BIN = "/home/utils/Python/builds/3.11.9-20250715/bin/python3"

# ECO Checker Python script
set ECO_CHECKER_PY = "${SCRIPT_DIR}/eco_checker.py"

# Verify Python exists
if (! -x $PYTHON_BIN) then
    echo "ERROR: Python not found at: $PYTHON_BIN"
    echo "Please verify Python installation."
    exit 2
endif

# Verify eco_checker.py exists
if (! -f $ECO_CHECKER_PY) then
    echo "ERROR: eco_checker.py not found at: $ECO_CHECKER_PY"
    echo "Please verify installation."
    exit 2
endif

# Execute eco_checker.py with all arguments
$PYTHON_BIN $ECO_CHECKER_PY $argv:q

# Preserve exit code
set EXIT_CODE = $status
exit $EXIT_CODE



