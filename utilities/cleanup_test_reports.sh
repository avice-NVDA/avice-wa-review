#!/bin/bash
#===============================================================================
# cleanup_test_reports.sh - Clean up old HTML test reports
#===============================================================================
# Usage: ./cleanup_test_reports.sh [days]
# 
# Arguments:
#   days - Delete reports older than N days (default: 1)
#
# Examples:
#   ./cleanup_test_reports.sh      # Delete reports older than 1 day
#   ./cleanup_test_reports.sh 7    # Delete reports older than 7 days
#===============================================================================

DAYS=${1:-1}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HTML_DIR="$SCRIPT_DIR/../html"

echo "Cleaning HTML reports older than $DAYS day(s)..."

# Clean avice_wa_review directory
COUNT1=$(find "$SCRIPT_DIR" -maxdepth 1 -name "avice_*.html" -type f -mtime +$DAYS 2>/dev/null | wc -l)
if [ $COUNT1 -gt 0 ]; then
    find "$SCRIPT_DIR" -maxdepth 1 -name "avice_*.html" -type f -mtime +$DAYS -delete
    echo "  Deleted $COUNT1 HTML report(s) from avice_wa_review/"
fi

# Clean html directory if it exists
if [ -d "$HTML_DIR" ]; then
    COUNT2=$(find "$HTML_DIR" -maxdepth 1 -name "*.html" -type f -mtime +$DAYS 2>/dev/null | wc -l)
    if [ $COUNT2 -gt 0 ]; then
        find "$HTML_DIR" -maxdepth 1 -name "*.html" -type f -mtime +$DAYS -delete
        echo "  Deleted $COUNT2 HTML report(s) from html/"
    fi
fi

TOTAL=$((COUNT1 + COUNT2))
if [ $TOTAL -eq 0 ]; then
    echo "  No old HTML reports found"
fi

# Show remaining reports
REMAINING1=$(find "$SCRIPT_DIR" -maxdepth 1 -name "avice_*.html" -type f 2>/dev/null | wc -l)
REMAINING2=$(find "$HTML_DIR" -maxdepth 1 -name "*.html" -type f 2>/dev/null | wc -l)
echo ""
echo "Remaining HTML reports:"
echo "  avice_wa_review/: $REMAINING1"
echo "  html/: $REMAINING2"

