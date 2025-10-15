#!/bin/bash
#===============================================================================
# Auto-Update Checker for AGUR Units Table
#===============================================================================
# This script checks if AGUR_UNITS_TABLE.txt needs updating and regenerates
# it automatically if new releases are detected.
#
# Usage:
#   ./check_and_update_agur_table.sh [--force] [--quiet]
#
# Options:
#   --force    Force update even if no changes detected
#   --quiet    Suppress output (only show errors)
#
# Return codes:
#   0 = Table is up-to-date or successfully updated
#   1 = Update needed but failed
#   2 = Table file doesn't exist (first run)
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TABLE_FILE="$SCRIPT_DIR/AGUR_UNITS_TABLE.txt"
RELEASE_BASE="/home/agur_backend_blockRelease/block"
EXTRACT_SCRIPT="$SCRIPT_DIR/extract_agur_releases.sh"

FORCE=false
QUIET=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --force) FORCE=true ;;
        --quiet) QUIET=true ;;
    esac
done

# Helper function for output
log_info() {
    if [ "$QUIET" = false ]; then
        echo "[INFO] $1"
    fi
}

log_error() {
    echo "[ERROR] $1" >&2
}

# Check if table file exists
if [ ! -f "$TABLE_FILE" ]; then
    log_info "AGUR_UNITS_TABLE.txt not found - first time setup"
    if [ -x "$EXTRACT_SCRIPT" ]; then
        log_info "Running initial extraction..."
        "$EXTRACT_SCRIPT"
        exit 2
    else
        log_error "Extraction script not found or not executable: $EXTRACT_SCRIPT"
        exit 1
    fi
fi

# Check if force update requested
if [ "$FORCE" = true ]; then
    log_info "Force update requested - regenerating table..."
    "$EXTRACT_SCRIPT"
    exit 0
fi

# Get table file modification time (in seconds since epoch)
table_mtime=$(stat -c %Y "$TABLE_FILE" 2>/dev/null)
if [ -z "$table_mtime" ]; then
    log_error "Cannot read table file timestamp"
    exit 1
fi

# Check for newer releases in the release area
# We'll check the modification time of last_sta_rel symlinks for tracked units
UNITS="prt pmux fdb fth lnd"  # Current CPORT units
UPDATE_NEEDED=false

for unit in $UNITS; do
    symlink="$RELEASE_BASE/$unit/last_sta_rel"
    if [ -L "$symlink" ]; then
        # Get the actual release directory the symlink points to
        release_dir=$(readlink -f "$symlink")
        if [ -d "$release_dir" ]; then
            # Check the release directory's modification time
            release_mtime=$(stat -c %Y "$release_dir" 2>/dev/null)
            if [ -n "$release_mtime" ] && [ "$release_mtime" -gt "$table_mtime" ]; then
                log_info "New release detected for unit: $unit"
                log_info "  Release time: $(date -d @$release_mtime '+%Y-%m-%d %H:%M:%S')"
                log_info "  Table time:   $(date -d @$table_mtime '+%Y-%m-%d %H:%M:%S')"
                UPDATE_NEEDED=true
                break
            fi
        fi
    fi
done

# Update if needed
if [ "$UPDATE_NEEDED" = true ]; then
    log_info "Updating AGUR units table with latest release data..."
    if "$EXTRACT_SCRIPT"; then
        log_info "Table successfully updated"
        exit 0
    else
        log_error "Failed to update table"
        exit 1
    fi
else
    log_info "Table is up-to-date (last updated: $(date -d @$table_mtime '+%Y-%m-%d %H:%M:%S'))"
    exit 0
fi

