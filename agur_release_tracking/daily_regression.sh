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
#
# Script: daily_regression.sh
# Purpose: Run daily AGUR regression on all 72 units (all regression types)
#
# Description:
#   Automated daily regression that runs ALL regression types (formal, timing,
#   pv, clock, release, glcheck) on all AGUR units. Generates a single 
#   comprehensive dashboard HTML per day.
#
# Usage:
#   ./daily_regression.sh
#
# Cron Example:
#   0 9 * * * cd /home/avice/scripts/avice_wa_review/agur_release_tracking && bash daily_regression.sh >> logs/daily_regression_$(date +\%Y\%m\%d).log 2>&1
#
# Output Location:
#   /home/scratch.avice_vlsi/agur_daily_regression/YYYYMMDD/
#
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGRESSION_SCRIPT="$SCRIPT_DIR/run_agur_regression.sh"

# Generate dated output directory
DATE_DIR=$(date '+%Y%m%d')
OUTPUT_BASE="/home/scratch.avice_vlsi/agur_daily_regression"
OUTPUT_DIR="$OUTPUT_BASE/$DATE_DIR"

#===============================================================================
# Main Execution
#===============================================================================

echo "================================================================================"
echo "AGUR Daily Regression - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"
echo ""
echo "Configuration:"
echo "  Units: All 72 AGUR units"
echo "  Regression Types: All (formal, timing, pv, clock, release, glcheck)"
echo "  Output: $OUTPUT_DIR"
echo ""
echo "================================================================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Change to output directory (run_agur_regression.sh generates HTML in current dir)
cd "$OUTPUT_DIR"

# Run AGUR regression (no -t flag = all regression types)
echo "Starting AGUR regression (all types)..."
echo ""

bash "$REGRESSION_SCRIPT"

EXIT_CODE=$?

echo ""
echo "================================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "[OK] Daily Regression Completed Successfully"
else
    echo "[WARN] Daily Regression Completed with Errors (exit code: $EXIT_CODE)"
fi
echo "================================================================================"
echo ""
echo "Results Location:"
echo "  Directory: $OUTPUT_DIR"
echo ""

# Count generated files
HTML_COUNT=$(find "$OUTPUT_DIR" -name "*.html" 2>/dev/null | wc -l)
LOG_COUNT=$(find "$OUTPUT_DIR" -name "*.log" 2>/dev/null | wc -l)

echo "Generated Files:"
echo "  HTML Dashboards: $HTML_COUNT"
echo "  Log Files: $LOG_COUNT"
echo ""

# Show disk usage
DIR_SIZE=$(du -sh "$OUTPUT_DIR" 2>/dev/null | cut -f1)
echo "Disk Usage: $DIR_SIZE"
echo ""

# List generated HTML files
if [ $HTML_COUNT -gt 0 ]; then
    echo "Dashboard Files:"
    find "$OUTPUT_DIR" -name "*.html" -exec basename {} \; 2>/dev/null | sed 's/^/  - /'
    echo ""
fi

echo "================================================================================"
echo "Execution Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"

exit $EXIT_CODE
