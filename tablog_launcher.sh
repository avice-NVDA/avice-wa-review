#!/bin/bash
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
# Script: tablog_launcher.sh
# Purpose: Launch tablog viewer for log files from HTML reports
# Usage: tablog_launcher.sh <logfile_path>
#===============================================================================

LOGFILE="$1"
TABLOG_PATH="/home/scratch.avice_vlsi/tablog/tablog"

if [ -z "$LOGFILE" ]; then
    echo "Error: No log file specified"
    exit 1
fi

if [ ! -f "$LOGFILE" ]; then
    echo "Error: Log file not found: $LOGFILE"
    exit 1
fi

# Launch tablog in a new terminal window
# Try different terminal emulators in order of preference
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "$TABLOG_PATH '$LOGFILE'; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -e "$TABLOG_PATH '$LOGFILE'; exec bash" &
elif command -v konsole &> /dev/null; then
    konsole -e "$TABLOG_PATH '$LOGFILE'; exec bash" &
else
    # Fallback: just run tablog in current terminal
    "$TABLOG_PATH" "$LOGFILE"
fi

