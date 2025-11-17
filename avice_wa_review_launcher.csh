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
# Script: avice_wa_review_launcher.csh
# Purpose: C-shell launcher for AVICE Workarea Review Tool
#
# Description:
#   Wrapper script that ensures the correct Python environment is used and
#   provides a simple, zero-setup interface for workarea analysis. This
#   launcher handles Python path resolution and passes all arguments through
#   to the main Python script.
#
# Usage:
#   /home/scratch.avice_vlsi/cursor/avice_wa_review_launcher.csh <workarea_path> [ipo_name]
#   /home/scratch.avice_vlsi/cursor/avice_wa_review_launcher.csh -u <unit_name>
#   /home/scratch.avice_vlsi/cursor/avice_wa_review_launcher.csh --help
#
# Examples:
#   # Full workarea analysis
#   /home/scratch.avice_vlsi/cursor/avice_wa_review_launcher.csh /path/to/workarea
#
#   # Specific IPO
#   /home/scratch.avice_vlsi/cursor/avice_wa_review_launcher.csh /path/to/workarea ipo1000
#
#   # AGUR unit analysis
#   /home/scratch.avice_vlsi/cursor/avice_wa_review_launcher.csh -u prt
#
#   # Selective sections
#   /home/scratch.avice_vlsi/cursor/avice_wa_review_launcher.csh -u prt -s runtime pt
#
# Prerequisites:
#   - Python 3.6+ (uses 3.11.9 build at /home/utils/Python/builds/3.11.9-20250715)
#   - avice_wa_review.py in the same directory
#
# Author: Alon Vice (avice@nvidia.com)
# Date: November 17, 2025
#===============================================================================

# Get the directory where this script is ACTUALLY located (resolve symlinks)
set SCRIPT_PATH = `readlink -f $0`
set SCRIPT_DIR = `dirname $SCRIPT_PATH`

# Python executable path
set PYTHON_BIN = "/home/utils/Python/builds/3.11.9-20250715/bin/python3"

# Main Python script
set MAIN_SCRIPT = "${SCRIPT_DIR}/avice_wa_review.py"

# Verify Python exists
if (! -x $PYTHON_BIN) then
    echo "ERROR: Python not found at: $PYTHON_BIN"
    echo "Please verify Python installation."
    exit 2
endif

# Verify avice_wa_review.py exists
if (! -f $MAIN_SCRIPT) then
    echo "ERROR: avice_wa_review.py not found at: $MAIN_SCRIPT"
    echo "Please verify installation."
    exit 2
endif

# Execute avice_wa_review.py with all arguments
$PYTHON_BIN $MAIN_SCRIPT $argv:q

# Preserve exit code
set EXIT_CODE = $status
exit $EXIT_CODE

