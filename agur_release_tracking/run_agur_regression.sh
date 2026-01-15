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
# Script: run_agur_regression.sh
# Version: 2.0.0
# Purpose: Run various analysis regressions on all released AGUR units
#
# Description:
#   This script reads the AGUR units release table and runs specified analysis
#   type on each released workarea. It collects the status for each unit and
#   generates a comprehensive HTML dashboard.
#
# Usage:
#   ./run_agur_regression.sh -t TYPE [options]
#
# Options:
#   -t, --type TYPE          Regression type: formal|timing|pv|clock|release|glcheck (REQUIRED)
#   -c, --chiplet CHIPLET    Filter by chiplet - case-insensitive (default: all chiplets)
#   -u, --unit UNIT          Run for specific unit only
#   -r, --release NAME       Test specific release (case-insensitive, fallback to last_sta_rel)
#   -h, --help               Show this help message
#
# Output:
#   - Console: Real-time status updates
#   - File: agur_<type>_regression_dashboard_YYYYMMDD_HHMMSS.html (current directory)
#
# Examples:
#   ./run_agur_regression.sh -t formal                    # Run formal regression on all units
#   ./run_agur_regression.sh -t formal -c CPORT           # Run formal on CPORT units only
#   ./run_agur_regression.sh -t timing -u prt             # Run timing regression on prt unit
#   ./run_agur_regression.sh -t pv                        # Run PV regression on all units
#   ./run_agur_regression.sh -t glcheck -c CPORT          # Run GL Check regression on CPORT units
#   ./run_agur_regression.sh -t formal --release NOV_02   # Run formal on NOV_02 release (fallback to last_sta_rel)
#   ./run_agur_regression.sh -t timing -c CPORT -r nov_02 # Run timing on CPORT units using NOV_02 release
#
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNITS_TABLE="$SCRIPT_DIR/AGUR_UNITS_TABLE.txt"
AVICE_SCRIPT="/home/scratch.avice_vlsi/cursor/avice_wa_review/avice_wa_review.py"
PYTHON_BIN="/home/utils/Python/builds/3.11.9-20250715/bin/python3"

# Regression configuration
REGRESSION_TYPES=()  # Array to store multiple regression types: formal, timing, pv, clock, release, glcheck

# Output files (generated in user's current working directory)
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
TEMP_DIR="/tmp/agur_regression_$$"

# Filters
FILTER_CHIPLETS=()  # Array to store multiple chiplets: CPORT, HPORT, NDQ, QNS, TCB
FILTER_UNIT=""
CUSTOM_RELEASE=""   # Custom release name (e.g., NOV_02) - case-insensitive

# Execution options
# Default: auto-detect with smart capping (min(cpu_cores, 16))
CPU_CORES=$(nproc 2>/dev/null || echo 8)
PARALLEL_JOBS=$([[ $CPU_CORES -le 16 ]] && echo $CPU_CORES || echo 16)
AUTO_DETECTED_JOBS=1      # Flag to track if jobs were auto-detected (default: auto)
DRY_RUN=0                 # Dry-run mode (preview only)
VERBOSE=0                 # Verbose/debug mode
QUIET=1                   # Quiet mode (only show progress bar) - default: enabled
NO_UPDATE=0               # Skip auto-update of AGUR units table
RESUME_FILE=""            # Resume from previous run
CONFIG_FILE=""            # Optional configuration file
MAX_RETRIES=2             # Number of retries for failed analyses
RETRY_DELAY=5             # Delay in seconds between retries

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

#===============================================================================
# Functions
#===============================================================================

show_help() {
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Call the Python help script with colorized output
    /home/utils/Python/builds/3.11.9-20250715/bin/python3 "${SCRIPT_DIR}/show_agur_help.py" "$0"
    exit 0
}

print_header() {
    local title=""
    case "$REGRESSION_TYPE" in
        formal)
            title="AGUR FORMAL VERIFICATION REGRESSION"
            ;;
        timing)
            title="AGUR PT SIGNOFF TIMING REGRESSION"
            ;;
        pv)
            title="AGUR PHYSICAL VERIFICATION REGRESSION"
            ;;
        clock)
            title="AGUR CLOCK TREE ANALYSIS REGRESSION"
            ;;
        release)
            title="AGUR BLOCK RELEASE STATUS REGRESSION"
            ;;
        *)
            title="AGUR REGRESSION"
            ;;
    esac
    
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${CYAN}        $title${NC}"
    echo -e "${CYAN}===============================================================================${NC}"
    echo ""
}

print_section() {
    echo -e "${CYAN}--- $1 ---${NC}"
}

# Verbose logging function
log_verbose() {
    if [ $VERBOSE -eq 1 ]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1"
    fi
}

# Debug logging function
log_debug() {
    if [ $VERBOSE -eq 1 ]; then
        echo -e "${MAGENTA}[DEBUG]${NC} $(date '+%H:%M:%S') - $1"
    fi
}

# Progress tracking function
# Args: current, total, unit_name, regression_type (optional)
show_progress() {
    local current=$1
    local total=$2
    local unit_name=$3
    local regression_type="${4:-}"
    local percentage=$((current * 100 / total))
    local completed_bars=$((percentage / 2))
    local remaining_bars=$((50 - completed_bars))
    
    # Build progress bar
    local bar="["
    for ((i=0; i<completed_bars; i++)); do bar+="="; done
    [ $completed_bars -gt 0 ] && bar+=">"
    for ((i=0; i<remaining_bars-1; i++)); do bar+=" "; done
    bar+="]"
    
    # Calculate ETA (if more than one unit processed)
    local eta_str=""
    if [ $current -gt 0 ]; then
        local elapsed=$((SECONDS - START_TIME))
        local avg_time=$((elapsed / current))
        local remaining=$((total - current))
        local eta=$((avg_time * remaining))
        
        local eta_min=$((eta / 60))
        local eta_sec=$((eta % 60))
        eta_str=" - ETA: ${eta_min}m ${eta_sec}s"
    fi
    
    # Add regression type badge with color coding (Option A: before progress bar)
    # NOTE: ASCII-only characters for Unix terminal compatibility
    local regression_badge=""
    if [ -n "$regression_type" ]; then
        local badge_color=""
        local badge_text=""
        case "$regression_type" in
            formal)
                badge_color="${CYAN}"
                badge_text="Formal"
                ;;
            timing)
                badge_color="${MAGENTA}"
                badge_text="Timing"
                ;;
            pv)
                badge_color="${BLUE}"
                badge_text="PV"
                ;;
            clock)
                badge_color="${YELLOW}"
                badge_text="Clock"
                ;;
            release)
                badge_color="${GREEN}"
                badge_text="Release"
                ;;
            glcheck)
                badge_color="${RED}"
                badge_text="GL Check"
                ;;
            *)
                badge_color="${CYAN}"
                badge_text="$regression_type"
                ;;
        esac
        regression_badge="${badge_color}[${badge_text}]${NC} "
    fi
    
    echo -ne "\r${CYAN}Progress:${NC} ${regression_badge}$bar ${percentage}% (${current}/${total}) - ${unit_name}${eta_str}     "
}

# Load configuration from file
load_config() {
    local config_file="$1"
    if [ ! -f "$config_file" ]; then
        echo -e "${RED}[ERROR]${NC} Configuration file not found: $config_file"
        exit 1
    fi
    
    log_verbose "Loading configuration from: $config_file"
    
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        
        # Trim whitespace
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        
        case "$key" in
            PYTHON_BIN)
                PYTHON_BIN="$value"
                log_verbose "  Python binary: $PYTHON_BIN"
                ;;
            AVICE_SCRIPT)
                AVICE_SCRIPT="$value"
                log_verbose "  Avice script: $AVICE_SCRIPT"
                ;;
            UNITS_TABLE)
                UNITS_TABLE="$value"
                log_verbose "  Units table: $UNITS_TABLE"
                ;;
            PARALLEL_JOBS)
                PARALLEL_JOBS="$value"
                log_verbose "  Parallel jobs: $PARALLEL_JOBS"
                ;;
        esac
    done < "$config_file"
}

# Save state for resume capability
save_state() {
    local state_file="$1"
    local regression_type="$2"
    local unit_index="$3"
    local unit_name="$4"
    
    echo "${regression_type}|${unit_index}|${unit_name}|$(date '+%Y-%m-%d %H:%M:%S')" >> "$state_file"
    log_debug "State saved: $unit_name ($unit_index)"
}

# Check if unit was already processed (for resume)
is_unit_processed() {
    local state_file="$1"
    local regression_type="$2"
    local unit_index="$3"
    
    if [ ! -f "$state_file" ]; then
        return 1  # Not processed
    fi
    
    if grep -q "^${regression_type}|${unit_index}|" "$state_file"; then
        return 0  # Already processed
    else
        return 1  # Not processed
    fi
}

# Run analysis for a single unit (can be called in parallel)
# Args: unit_index, unit_name, chiplet, workarea, regression_type, analysis_section, temp_dir, state_file
run_unit_analysis() {
    local unit_idx="$1"
    local unit="$2"
    local chiplet="$3"
    local workarea="$4"
    local regression_type="$5"
    local analysis_section="$6"
    local temp_dir="$7"
    local state_file="$8"
    
    local output_file="$temp_dir/${unit}_${regression_type}_output.txt"
    local result_file="$temp_dir/${unit}_${regression_type}_result.txt"
    local retry_count=0
    local success=0
    
    log_debug "Starting analysis for unit: $unit (index: $unit_idx)"
    
    # Check if workarea exists
    if [ ! -d "$workarea" ]; then
        echo "MISSING|Workarea path not found or deleted|N/A" > "$result_file"
        log_debug "Unit $unit: Workarea missing"
        save_state "$state_file" "$regression_type" "$unit_idx" "$unit"
        return
    fi
    
    # Retry loop for robustness
    while [ $retry_count -le $MAX_RETRIES ] && [ $success -eq 0 ]; do
        if [ $retry_count -gt 0 ]; then
            log_verbose "Retry attempt $retry_count/$MAX_RETRIES for unit: $unit"
            sleep $RETRY_DELAY
        fi
        
        # Run analysis with timeout protection (30 minutes max)
        log_debug "Executing avice_wa_review.py for $unit (attempt $((retry_count+1)))"
        
        # Use timeout if available
        # NOTE: Do NOT use --quiet here - we need the full output for parser functions to extract data!
        # NOTE: $analysis_section is intentionally unquoted to allow word splitting for multiple sections
        if command -v timeout &> /dev/null; then
            timeout 1800 "$PYTHON_BIN" "$AVICE_SCRIPT" "$workarea" -s $analysis_section --no-logo > "$output_file" 2>&1
            local exit_code=$?
            
            if [ $exit_code -eq 124 ]; then
                log_verbose "Unit $unit: Analysis timed out after 30 minutes"
                ((retry_count++))
                continue
            fi
        else
            "$PYTHON_BIN" "$AVICE_SCRIPT" "$workarea" -s $analysis_section --no-logo > "$output_file" 2>&1
            local exit_code=$?
        fi
        
        # Parse output based on regression type
        if [ $exit_code -ne 0 ]; then
            log_debug "Unit $unit: Analysis failed with exit code $exit_code (attempt $((retry_count+1)))"
            
            # Check if it's a transient error (e.g., file system issues)
            if [ $exit_code -eq 1 ] && [ $retry_count -lt $MAX_RETRIES ]; then
                ((retry_count++))
                continue
            fi
            
            echo "ERROR|Script execution failed (exit code: $exit_code) after $((retry_count+1)) attempts|N/A" > "$result_file"
            success=1  # Exit retry loop
        else
            # Call appropriate parser function based on regression type
            local parse_result=""
            case "$regression_type" in
                formal)
                    parse_result=$(parse_formal_output "$output_file")
                    ;;
                timing)
                    parse_result=$(parse_timing_output "$output_file")
                    ;;
                pv)
                    parse_result=$(parse_pv_output "$output_file")
                    ;;
                clock)
                    parse_result=$(parse_clock_output "$output_file")
                    ;;
                release)
                    parse_result=$(parse_release_output "$output_file")
                    ;;
                glcheck)
                    parse_result=$(parse_glcheck_output "$output_file")
                    ;;
                *)
                    parse_result="ERROR|Unknown regression type|N/A"
                    ;;
            esac
            
            echo "$parse_result" > "$result_file"
            log_debug "Unit $unit: Analysis complete (attempt $((retry_count+1)))"
            success=1  # Exit retry loop
        fi
    done
    
    # Save state
    save_state "$state_file" "$regression_type" "$unit_idx" "$unit"
}

#===============================================================================
# Regression Type Functions
#===============================================================================

#===============================================================================
# Parser Functions - Extract results from avice_wa_review.py output
#===============================================================================

# Parse formal verification output
# Args: $1 = output file path
# Returns: Sets ANALYSIS_STATUS, ANALYSIS_DETAILS, ANALYSIS_RUNTIMES (via echo)
parse_formal_output() {
    local output_file="$1"
    local status=""
    local details=""
    local runtime="N/A"
    
    # Extract formal verification results
    local formal_section=$(grep -A 100 "Formal Verification" "$output_file")
    
    if [ -z "$formal_section" ]; then
        echo "NOT_FOUND|No formal flow detected|N/A"
        return
    elif echo "$formal_section" | grep -q "No formal verification logs found"; then
        echo "NOT_FOUND|No formal flow detected|N/A"
        return
    fi
    
    # Extract status and runtime for each formal flow
    local rtl_vs_pnr_status=""
    local rtl_vs_pnr_bbox_status=""
    local rtl_vs_syn_status=""
    local rtl_vs_syn_bbox_status=""
    local rtl_vs_pnr_runtime=""
    local rtl_vs_pnr_bbox_runtime=""
    local rtl_vs_syn_runtime=""
    local rtl_vs_syn_bbox_runtime=""
    local rtl_vs_pnr_failing_pts=""
    local rtl_vs_pnr_bbox_failing_pts=""
    local rtl_vs_syn_failing_pts=""
    local rtl_vs_syn_bbox_failing_pts=""
    
    # Convert formal section to array for easier processing
    local formal_lines=()
    while IFS= read -r line; do
        formal_lines+=("$line")
    done <<< "$formal_section"
    
    # Process array line by line
    local current_flow=""
    for i in "${!formal_lines[@]}"; do
        line="${formal_lines[$i]}"
        
        # Strip ANSI color codes from the line before processing
        line=$(echo "$line" | sed 's/\x1b\[[0-9;]*m//g')
        
        # Detect which flow this is - look for "Formal Log:" prefix
        # When we encounter a new flow, reset current_flow first (for the previous flow)
        if [[ "$line" == *"Formal Log:"* ]]; then
            # Reset flow when encountering new formal log (end of previous flow's data)
            current_flow=""
            
            if [[ "$line" == *"rtl_vs_pnr_bbox_fm/log/rtl_vs_pnr_bbox_fm.log"* ]]; then
                current_flow="rtl_vs_pnr_bbox"
            elif [[ "$line" == *"rtl_vs_pnr_fm/log/rtl_vs_pnr_fm.log"* ]]; then
                current_flow="rtl_vs_pnr"
            elif [[ "$line" == *"rtl_vs_syn_fm/log/rtl_vs_syn_fm.log"* ]]; then
                current_flow="rtl_vs_syn"
            elif [[ "$line" == *"rtl_vs_syn_bbox_fm/log/rtl_vs_syn_bbox_fm.log"* ]]; then
                current_flow="rtl_vs_syn_bbox"
            fi
        fi
        
        # If we have a current flow, check for Status and Runtime
        if [ -n "$current_flow" ]; then
            # Extract status - handle ANSI color codes
            if [[ "$line" =~ Status:[[:space:]]*.*?(SUCCEEDED|FAILED|CRASHED|RUNNING|UNRESOLVED) ]]; then
                case "$current_flow" in
                    rtl_vs_pnr) rtl_vs_pnr_status="${BASH_REMATCH[1]}" ;;
                    rtl_vs_pnr_bbox) rtl_vs_pnr_bbox_status="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn) rtl_vs_syn_status="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn_bbox) rtl_vs_syn_bbox_status="${BASH_REMATCH[1]}" ;;
                esac
            fi
            
            # Extract failing compare points (BEFORE runtime extraction to ensure current_flow is still set)
            # Format 1: "Failing compare points: 123" (in terminal output)
            # Format 2: "123 Failing compare points" (in log files)
            if [[ "$line" =~ Failing[[:space:]]compare[[:space:]]points:[[:space:]]*([0-9]+) ]]; then
                case "$current_flow" in
                    rtl_vs_pnr) rtl_vs_pnr_failing_pts="${BASH_REMATCH[1]}" ;;
                    rtl_vs_pnr_bbox) rtl_vs_pnr_bbox_failing_pts="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn) rtl_vs_syn_failing_pts="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn_bbox) rtl_vs_syn_bbox_failing_pts="${BASH_REMATCH[1]}" ;;
                esac
            elif [[ "$line" =~ ([0-9]+)[[:space:]]Failing[[:space:]]compare[[:space:]]points ]]; then
                case "$current_flow" in
                    rtl_vs_pnr) rtl_vs_pnr_failing_pts="${BASH_REMATCH[1]}" ;;
                    rtl_vs_pnr_bbox) rtl_vs_pnr_bbox_failing_pts="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn) rtl_vs_syn_failing_pts="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn_bbox) rtl_vs_syn_bbox_failing_pts="${BASH_REMATCH[1]}" ;;
                esac
            fi
            
            # Extract runtime
            if [[ "$line" =~ Runtime:[[:space:]]*([0-9.]+[[:space:]]*(hours?|minutes?)) ]]; then
                case "$current_flow" in
                    rtl_vs_pnr) rtl_vs_pnr_runtime="${BASH_REMATCH[1]}" ;;
                    rtl_vs_pnr_bbox) rtl_vs_pnr_bbox_runtime="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn) rtl_vs_syn_runtime="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn_bbox) rtl_vs_syn_bbox_runtime="${BASH_REMATCH[1]}" ;;
                esac
                # Note: Don't reset current_flow here - failing compare points comes after runtime!
            fi
        fi
    done
    
    # Determine overall status (prioritize PNR flows over SYN flows)
    local overall_status="UNKNOWN"
    
    # Check for crashes (highest priority)
    if [[ "$rtl_vs_pnr_status" == "CRASHED" ]] || [[ "$rtl_vs_pnr_bbox_status" == "CRASHED" ]] || \
       [[ "$rtl_vs_syn_status" == "CRASHED" ]] || [[ "$rtl_vs_syn_bbox_status" == "CRASHED" ]]; then
        overall_status="CRASHED"
    # Check for failures
    elif [[ "$rtl_vs_pnr_status" == "FAILED" ]] || [[ "$rtl_vs_pnr_bbox_status" == "FAILED" ]] || \
         [[ "$rtl_vs_syn_status" == "FAILED" ]] || [[ "$rtl_vs_syn_bbox_status" == "FAILED" ]]; then
        overall_status="FAILED"
    # Check for running
    elif [[ "$rtl_vs_pnr_status" == "RUNNING" ]] || [[ "$rtl_vs_pnr_bbox_status" == "RUNNING" ]] || \
         [[ "$rtl_vs_syn_status" == "RUNNING" ]] || [[ "$rtl_vs_syn_bbox_status" == "RUNNING" ]]; then
        overall_status="RUNNING"
    # Check for unresolved
    elif [[ "$rtl_vs_pnr_status" == "UNRESOLVED" ]] || [[ "$rtl_vs_pnr_bbox_status" == "UNRESOLVED" ]] || \
         [[ "$rtl_vs_syn_status" == "UNRESOLVED" ]] || [[ "$rtl_vs_syn_bbox_status" == "UNRESOLVED" ]]; then
        overall_status="UNRESOLVED"
    # All succeeded (PNR flows are most important)
    elif [[ "$rtl_vs_pnr_status" == "SUCCEEDED" ]] && [[ "$rtl_vs_pnr_bbox_status" == "SUCCEEDED" ]]; then
        overall_status="PASSED"
    # At least PNR flows exist and passed (even if SYN failed)
    elif [[ "$rtl_vs_pnr_status" == "SUCCEEDED" ]] || [[ "$rtl_vs_pnr_bbox_status" == "SUCCEEDED" ]]; then
        overall_status="PARTIAL_PASS"
    fi
    
    # Calculate max runtime for overall display
    runtime="N/A"
    for rt in "$rtl_vs_pnr_bbox_runtime" "$rtl_vs_pnr_runtime" "$rtl_vs_syn_runtime" "$rtl_vs_syn_bbox_runtime"; do
        if [ -n "$rt" ]; then
            runtime="$rt"
            break
        fi
    done
    
    # Build details string with status and runtime for each flow
    details=""
    if [ -n "$rtl_vs_pnr_bbox_status" ]; then
        details="${details}rtl_vs_pnr_bbox: $rtl_vs_pnr_bbox_status"
        [ -n "$rtl_vs_pnr_bbox_runtime" ] && details="${details} ($rtl_vs_pnr_bbox_runtime)"
        details="${details}, "
    fi
    if [ -n "$rtl_vs_pnr_status" ]; then
        details="${details}rtl_vs_pnr: $rtl_vs_pnr_status"
        [ -n "$rtl_vs_pnr_runtime" ] && details="${details} ($rtl_vs_pnr_runtime)"
        details="${details}, "
    fi
    if [ -n "$rtl_vs_syn_status" ]; then
        details="${details}rtl_vs_syn: $rtl_vs_syn_status"
        [ -n "$rtl_vs_syn_runtime" ] && details="${details} ($rtl_vs_syn_runtime)"
        details="${details}, "
    fi
    if [ -n "$rtl_vs_syn_bbox_status" ]; then
        details="${details}rtl_vs_syn_bbox: $rtl_vs_syn_bbox_status"
        [ -n "$rtl_vs_syn_bbox_runtime" ] && details="${details} ($rtl_vs_syn_bbox_runtime)"
    fi
    details=${details%, }  # Remove trailing comma and space
    
    # If no formal flows were found at all, mark as NOT_FOUND
    if [ -z "$details" ]; then
        overall_status="NOT_FOUND"
        details="No formal flow logs detected"
    fi
    
    # Build failing compare points string (colon-delimited per flow to avoid conflict with main pipe delimiter)
    local failing_pts="${rtl_vs_pnr_bbox_failing_pts:-N/A}:${rtl_vs_pnr_failing_pts:-N/A}:${rtl_vs_syn_failing_pts:-N/A}:${rtl_vs_syn_bbox_failing_pts:-N/A}"
    
    # Extract run date from Runtime Summary table for Formal verification
    # Format: "  Signoff      Formal (rtl_vs_pnr_bbox_fm) 4.07 hours           10/20 08:20 10/20 12:24"
    local runtime_line=$(grep -A 100 "\[2\] Runtime\|Runtime Summary" "$output_file" | grep -E "Signoff\s+Formal" | sed 's/\x1b\[[0-9;]*m//g' | head -1)
    
    # Extract start date/time (format: MM/DD HH:MM)
    local run_date=$(echo "$runtime_line" | awk '{
        for (i=1; i<=NF; i++) {
            if ($i ~ /^[0-9]{1,2}\/[0-9]{1,2}$/) {
                # Found date, next field is time
                if (i+1 <= NF) {
                    print $i, $(i+1)
                    break
                }
            }
        }
    }')
    [ -z "$run_date" ] && run_date="N/A"
    
    # Return pipe-delimited string: status|details|runtime|failing_compare_points|run_date
    echo "${overall_status}|${details}|${runtime}|${failing_pts}|${run_date}"
}

# Parse timing (PT) output
# Args: $1 = output file path
# Returns: status|details|runtime|setup_wns|setup_tns|setup_nvp|hold_wns|hold_tns|hold_nvp|dsr_skew_setup|dsr_skew_hold
parse_timing_output() {
    local output_file="$1"
    local status=""
    local details=""
    local runtime="N/A"
    
    # Initialize scenario-specific variables
    local setup_wns="N/A"
    local setup_tns="N/A"
    local setup_nvp="N/A"
    local hold_wns="N/A"
    local hold_tns="N/A"
    local hold_nvp="N/A"
    local dsr_skew_setup="N/A"
    local dsr_skew_hold="N/A"
    local setup_scenario="N/A"
    local hold_scenario="N/A"
    local pt_work_areas="N/A"
    
    # Extract PT Signoff Timing section - match actual output format
    local timing_section=$(grep -A 300 "Signoff Timing (PT)\|PT Timing Summary" "$output_file")
    
    if [ -z "$timing_section" ]; then
        echo "NOT_FOUND|No PT timing analysis found|N/A|N/A|N/A|N/A|N/A|N/A|N/A|N/A|N/A"
        return
    fi
    
    # Check for "No PT signoff timing" message
    if echo "$timing_section" | grep -q "No PT signoff timing"; then
        echo "NOT_FOUND|No PT timing analysis found|N/A|N/A|N/A|N/A|N/A|N/A|N/A|N/A|N/A"
        return
    fi
    
    # Strip ANSI color codes from the section
    timing_section=$(echo "$timing_section" | sed 's/\x1b\[[0-9;]*m//g')
    
    # Extract total work areas count (e.g., "Total Work Areas: 7")
    pt_work_areas=$(echo "$timing_section" | grep "Total Work Areas:" | grep -oP "Total Work Areas:\s*\K\d+" | head -1)
    [ -z "$pt_work_areas" ] && pt_work_areas="N/A"
    
    # Try to extract Setup and Hold scenario data (dual-scenario format)
    local setup_section=$(echo "$timing_section" | awk '/Latest Setup Scenario/,/Latest Hold Scenario|DSR Skew Trend/ {print}')
    local hold_section=$(echo "$timing_section" | awk '/Latest Hold Scenario/,/DSR Skew Trend|^$/ {print}')
    
    # Extract scenario names from headers (e.g., "Latest Setup Scenario (func.std_tt_0c_0p6v.setup.typical):")
    setup_scenario=$(echo "$timing_section" | grep "Latest Setup Scenario" | grep -oP '\([^)]+\)' | tr -d '()')
    hold_scenario=$(echo "$timing_section" | grep "Latest Hold Scenario" | grep -oP '\([^)]+\)' | tr -d '()')
    [ -z "$setup_scenario" ] && setup_scenario="N/A"
    [ -z "$hold_scenario" ] && hold_scenario="N/A"
    
    if [ -n "$setup_section" ]; then
        # Extract Setup scenario timing
        setup_wns=$(echo "$setup_section" | grep "WNS:" | grep -oP "WNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
        setup_tns=$(echo "$setup_section" | grep "TNS:" | grep -oP "TNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
        setup_nvp=$(echo "$setup_section" | grep "NVP:" | grep -oP "NVP:\s*\K[0-9]+" | head -1)
        
        [ -z "$setup_wns" ] && setup_wns="N/A"
        [ -z "$setup_tns" ] && setup_tns="N/A"
        [ -z "$setup_nvp" ] && setup_nvp="N/A"
    fi
    
    if [ -n "$hold_section" ]; then
        # Extract Hold scenario timing
        hold_wns=$(echo "$hold_section" | grep "WNS:" | grep -oP "WNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
        hold_tns=$(echo "$hold_section" | grep "TNS:" | grep -oP "TNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
        hold_nvp=$(echo "$hold_section" | grep "NVP:" | grep -oP "NVP:\s*\K[0-9]+" | head -1)
        
        [ -z "$hold_wns" ] && hold_wns="N/A"
        [ -z "$hold_tns" ] && hold_tns="N/A"
        [ -z "$hold_nvp" ] && hold_nvp="N/A"
    fi
    
    # Extract DSR Skew - handle two formats:
    # Format 1 (multiple PT runs): "DSR Skew Trend: Setup Scenario: work_XXX: N.NN ps"
    # Format 2 (single PT run): "Latest DSR Mux Clock Skew: Setup: N.NN ps"
    
    # Try Format 1 first (multiple PT runs with trend)
    local dsr_section=$(echo "$timing_section" | awk '/DSR Skew Trend/,/^$/ {print}')
    if [ -n "$dsr_section" ]; then
        # Extract setup skew: Find "Setup Scenario:" then get first value (work_XXX: N.NN ps)
        dsr_skew_setup=$(echo "$dsr_section" | awk '/Setup Scenario:/,/Hold Scenario|Trend:/ {print}' | grep "work_.*ps" | head -1 | grep -oP "[\d.]+\s*ps" | grep -oP "[\d.]+" | head -1)
        
        # Extract hold skew: Find "Hold Scenario:" then get first value (work_XXX: N.NN ps)
        dsr_skew_hold=$(echo "$dsr_section" | awk '/Hold Scenario:/,/^$|Trend:/ {print}' | grep "work_.*ps" | head -1 | grep -oP "[\d.]+\s*ps" | grep -oP "[\d.]+" | head -1)
        
        [ -z "$dsr_skew_setup" ] && dsr_skew_setup="N/A"
        [ -z "$dsr_skew_hold" ] && dsr_skew_hold="N/A"
    fi
    
    # Try Format 2 if Format 1 didn't find values (single PT run)
    if [ "$dsr_skew_setup" = "N/A" ] && [ "$dsr_skew_hold" = "N/A" ]; then
        local dsr_latest=$(echo "$timing_section" | awk '/Latest DSR Mux Clock Skew/,/^$/ {print}')
        if [ -n "$dsr_latest" ]; then
            # Extract: "Setup:   1.94 ps"
            dsr_skew_setup=$(echo "$dsr_latest" | grep "Setup:" | grep -oP "[\d.]+\s*ps" | grep -oP "[\d.]+" | head -1)
            # Extract: "Hold:    4.70 ps"
            dsr_skew_hold=$(echo "$dsr_latest" | grep "Hold:" | grep -oP "[\d.]+\s*ps" | grep -oP "[\d.]+" | head -1)
            
            [ -z "$dsr_skew_setup" ] && dsr_skew_setup="N/A"
            [ -z "$dsr_skew_hold" ] && dsr_skew_hold="N/A"
        fi
    fi
    
    # Fallback: If scenarios not found, try simple extraction (old format)
    if [ "$setup_wns" = "N/A" ] && [ "$hold_wns" = "N/A" ]; then
    local wns=$(echo "$timing_section" | grep -i "WNS:" | grep -oP "WNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
    local tns=$(echo "$timing_section" | grep -i "TNS:" | grep -oP "TNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
    local nvp=$(echo "$timing_section" | grep -i "NVP:" | grep -oP "NVP:\s*\K[0-9]+" | head -1)
    
        # Use as setup values for backward compatibility
        [ -n "$wns" ] && setup_wns="$wns"
        [ -n "$tns" ] && setup_tns="$tns"
        [ -n "$nvp" ] && setup_nvp="$nvp"
    fi
    
    # Determine overall timing status (based on worst case between setup and hold)
    local overall_status="UNKNOWN"
    local worst_wns="N/A"
    local worst_tns="N/A"
    
    # Find worst WNS
    if [ "$setup_wns" != "N/A" ] && [ "$hold_wns" != "N/A" ]; then
        worst_wns=$(echo "$setup_wns $hold_wns" | awk '{if ($1 < $2) print $1; else print $2}')
        worst_tns=$(echo "$setup_tns $hold_tns" | awk '{if ($1 < $2) print $1; else print $2}')
    elif [ "$setup_wns" != "N/A" ]; then
        worst_wns="$setup_wns"
        worst_tns="$setup_tns"
    elif [ "$hold_wns" != "N/A" ]; then
        worst_wns="$hold_wns"
        worst_tns="$hold_tns"
    fi
    
    if [ "$worst_wns" = "N/A" ]; then
        overall_status="NO_DATA"
        details="No timing data available"
    else
        # Convert WNS to float for comparison
        local wns_check=$(echo "$worst_wns 0" | awk '{if ($1 >= $2) print "PASS"; else print "FAIL"}')
        
        # Format timing values for details
        local wns_formatted="$worst_wns"
        local tns_formatted="$worst_tns"
        local wns_unit="ns"
        local tns_unit="ns"
        
        # Check if WNS absolute value is less than 0.5ns (convert to ps)
        local wns_abs=$(echo "$worst_wns" | tr -d '-')
        if [ $(echo "$wns_abs 0.5" | awk '{if ($1 < $2) print "1"; else print "0"}') -eq 1 ]; then
            wns_formatted=$(echo "$worst_wns" | awk '{printf "%.0f", $1 * 1000}')
            wns_unit="ps"
        fi
        
        # Check if TNS absolute value is less than 0.5ns
        local tns_abs=$(echo "$worst_tns" | tr -d '-')
        if [ $(echo "$tns_abs 0.5" | awk '{if ($1 < $2) print "1"; else print "0"}') -eq 1 ]; then
            tns_formatted=$(echo "$worst_tns" | awk '{printf "%.0f", $1 * 1000}')
            tns_unit="ps"
        fi
        
        if [ "$wns_check" = "PASS" ]; then
            overall_status="PASSED"
            details="Setup/Hold WNS: ${wns_formatted}${wns_unit}, TNS: ${tns_formatted}${tns_unit}"
        else
            # Check severity of violation (in nanoseconds)
            # Critical if WNS < -0.05ns (50ps)
            local is_critical=$(echo "$wns_abs 0.05" | awk '{if ($1 > $2) print "YES"; else print "NO"}')
            
            if [ "$is_critical" = "YES" ]; then
                overall_status="FAILED"
            else
                overall_status="WARN"
            fi
            details="Setup/Hold WNS: ${wns_formatted}${wns_unit} (VIOLATION), TNS: ${tns_formatted}${tns_unit}"
        fi
    fi
    
    # Extract PT runtime from Runtime section (not PT section)
    # Extract runtime and run date from Runtime section (look for Auto PT runtime line)
    # Format: "  Signoff      Auto PT                     3.90 hours              10/15 23:31 10/16 03:25"
    local runtime_line=$(grep -A 100 "\[2\] Runtime\|Runtime Summary" "$output_file" | grep -E "Signoff\s+Auto PT" | sed 's/\x1b\[[0-9;]*m//g' | head -1)
    
    runtime=$(echo "$runtime_line" | awk '{
        # Find the column with "hours" or "minutes"
        for (i=1; i<=NF; i++) {
            if ($i ~ /hours|minutes|seconds/) {
                print $(i-1), $i
                break
            }
        }
    }')
    [ -z "$runtime" ] && runtime="N/A"
    
    # Extract start date/time (format: MM/DD HH:MM)
    local run_date=$(echo "$runtime_line" | awk '{
        for (i=1; i<=NF; i++) {
            if ($i ~ /^[0-9]{1,2}\/[0-9]{1,2}$/) {
                # Found date, next field is time
                if (i+1 <= NF) {
                    print $i, $(i+1)
                    break
                }
            }
        }
    }')
    [ -z "$run_date" ] && run_date="N/A"
    
    # Return pipe-delimited string with all fields (including scenario names, PT work areas count, and run_date)
    echo "${overall_status}|${details}|${runtime}|${setup_wns}|${setup_tns}|${setup_nvp}|${hold_wns}|${hold_tns}|${hold_nvp}|${dsr_skew_setup}|${dsr_skew_hold}|${setup_scenario}|${hold_scenario}|${pt_work_areas}|${run_date}"
}

# Parse PV (Physical Verification) output
# Args: $1 = output file path
# Returns: status|details|runtime
parse_pv_output() {
    local output_file="$1"
    local status=""
    local details=""
    local runtime="N/A"
    
    # Extract Physical Verification section
    local pv_section=$(grep -A 200 "Physical Verification" "$output_file")
    
    if [ -z "$pv_section" ]; then
        echo "NOT_FOUND|No PV analysis found|N/A"
        return
    fi
    
    # Check for "No physical verification" message
    if echo "$pv_section" | grep -q "No physical verification"; then
        echo "NOT_FOUND|No PV analysis found|N/A"
        return
    fi
    
    # Extract PV metrics - match actual avice_wa_review.py output format
    
    # LVS: Extract "Failed Equivalence Points: X"
    local lvs_violations=$(echo "$pv_section" | grep -i "Failed Equivalence Points:" | grep -oP "Failed Equivalence Points:\s*\K[0-9]+" | head -1)
    
    # DRC: Extract "Total DRC violations: X" or check for CLEAN
    local drc_violations=$(echo "$pv_section" | grep -i "Total DRC violations:" | grep -oP "Total DRC violations:\s*\K[0-9]+" | head -1)
    if [ -z "$drc_violations" ]; then
        # Check if it says CLEAN
        if echo "$pv_section" | grep -qi "CLEAN.*No DRC violations"; then
            drc_violations="0"
        fi
    fi
    
    # Antenna: Check for "No antenna violations found" or extract count
    if echo "$pv_section" | grep -qi "No antenna violations found"; then
        antenna_violations="0"
    else
        antenna_violations=$(echo "$pv_section" | grep -i "Total.*antenna.*violations\|Antenna.*violations:" | grep -oP "[0-9]+" | head -1)
    fi
    
    # Set defaults if extraction failed
    [ -z "$drc_violations" ] && drc_violations="N/A"
    [ -z "$lvs_violations" ] && lvs_violations="N/A"
    [ -z "$antenna_violations" ] && antenna_violations="N/A"
    
    # Determine overall PV status
    local overall_status="UNKNOWN"
    
    if [ "$drc_violations" = "N/A" ] && [ "$lvs_violations" = "N/A" ] && [ "$antenna_violations" = "N/A" ]; then
        overall_status="NO_DATA"
        details="No PV data available"
    else
        # Convert to numbers for comparison (use 0 if N/A)
        local drc_num=${drc_violations}
        local lvs_num=${lvs_violations}
        local ant_num=${antenna_violations}
        
        [ "$drc_num" = "N/A" ] && drc_num=0
        [ "$lvs_num" = "N/A" ] && lvs_num=0
        [ "$ant_num" = "N/A" ] && ant_num=0
        
        # Calculate total violations
        local total_violations=$((drc_num + lvs_num + ant_num))
        
        if [ $total_violations -eq 0 ]; then
            overall_status="PASSED"
            details="DRC: ${drc_violations}, LVS: ${lvs_violations}, Antenna: ${antenna_violations} (ALL CLEAN)"
        else
            # Determine severity
            # Critical: LVS > 5 OR DRC > 100 OR Antenna > 10
            if [ $lvs_num -gt 5 ] || [ $drc_num -gt 100 ] || [ $ant_num -gt 10 ]; then
                overall_status="FAILED"
                details="DRC: ${drc_violations}, LVS: ${lvs_violations}, Antenna: ${antenna_violations} (CRITICAL)"
            else
                overall_status="WARN"
                details="DRC: ${drc_violations}, LVS: ${lvs_violations}, Antenna: ${antenna_violations} (MINOR)"
            fi
        fi
    fi
    
    # Extract runtime and run date from Runtime section (look for PV runtime line)
    # Format: "  Signoff      PV                          2.81 hours           10/19 15:30 10/19 18:24"
    local runtime_line=$(grep -A 100 "\[2\] Runtime\|Runtime Summary" "$output_file" | grep -E "Signoff\s+PV" | sed 's/\x1b\[[0-9;]*m//g' | head -1)
    
    runtime=$(echo "$runtime_line" | awk '{
        for (i=1; i<=NF; i++) {
            if ($i ~ /hours|minutes|seconds/) {
                print $(i-1), $i
                break
            }
        }
    }')
    
    # Fallback: If not in Runtime section, try Duration from PV section itself
    if [ -z "$runtime" ]; then
        runtime=$(echo "$pv_section" | grep -i "Duration:" | head -1 | grep -oP "Duration:\s*\K.*")
    fi
    [ -z "$runtime" ] && runtime="N/A"
    
    # Extract start date/time (format: MM/DD HH:MM)
    local run_date=$(echo "$runtime_line" | awk '{
        for (i=1; i<=NF; i++) {
            if ($i ~ /^[0-9]{1,2}\/[0-9]{1,2}$/) {
                # Found date, next field is time
                if (i+1 <= NF) {
                    print $i, $(i+1)
                    break
                }
            }
        }
    }')
    [ -z "$run_date" ] && run_date="N/A"
    
    # Return pipe-delimited string (added run_date as last field)
    echo "${overall_status}|${details}|${runtime}|${run_date}"
}

# Parse clock tree analysis output
# Args: $1 = output file path
# Returns: status|details|runtime
parse_clock_output() {
    local output_file="$1"
    local status=""
    local details=""
    local runtime="N/A"
    
    # Extract Clock Tree Analysis section
    local clock_section=$(grep -A 200 "Clock Tree Analysis\|Clock Analysis" "$output_file")
    
    if [ -z "$clock_section" ]; then
        echo "NOT_FOUND|No clock tree analysis found|N/A"
        return
    fi
    
    # Check for "No clock" message
    if echo "$clock_section" | grep -q "No clock.*analysis\|No clock.*data"; then
        echo "NOT_FOUND|No clock tree analysis found|N/A"
        return
    fi
    
    # Extract per-clock details from "Clock Detail:" lines
    # Format: "Clock Detail: CLOCK_NAME|MAX_LATENCY_PS|SKEW_PS"
    local clock_details=$(grep "Clock Detail:" "$output_file" 2>/dev/null | sed 's/.*Clock Detail:[[:space:]]*//' | sed 's/\x1b\[[0-9;]*m//g')
    
    if [ -z "$clock_details" ]; then
        # Fallback to old extraction method
        local max_latency=$(echo "$clock_section" | grep -i "Maximum.*latency\|Max.*latency" | grep -oP "[0-9]*\.?[0-9]+" | head -1)
        local clock_skew=$(echo "$clock_section" | grep -i "Clock skew\|Skew" | grep -oP "[0-9]*\.?[0-9]+" | head -1)
        
        [ -z "$max_latency" ] && max_latency="N/A"
        [ -z "$clock_skew" ] && clock_skew="N/A"
        
        if [ "$max_latency" = "N/A" ]; then
            overall_status="NO_DATA"
            details="No clock data available"
        else
            local lat_check=$(echo "$max_latency 550" | awk '{if ($1 <= $2) print "PASS"; else if ($1 < 580) print "WARN"; else print "FAIL"}')
            
            if [ "$lat_check" = "PASS" ]; then
                overall_status="PASSED"
                details="Max Latency: ${max_latency}ps"
            elif [ "$lat_check" = "WARN" ]; then
                overall_status="WARN"
                details="Max Latency: ${max_latency}ps (HIGH)"
            else
                overall_status="FAILED"
                details="Max Latency: ${max_latency}ps (CRITICAL)"
            fi
        fi
    else
        # Process per-clock details
        local overall_status="PASSED"
        local max_latency_overall=0
        local num_clocks=0
        local clocks_list=""
        
        while IFS='|' read -r clock_name max_latency skew; do
            ((num_clocks++))
            # Track max latency across all clocks for status determination
            max_lat_int=$(echo "$max_latency" | awk '{print int($1)}')
            if [ $max_lat_int -gt $max_latency_overall ]; then
                max_latency_overall=$max_lat_int
            fi
            
            # Build details with clock count
            if [ $num_clocks -eq 1 ]; then
                clocks_list="$clock_name"
            else
                clocks_list="$clocks_list, $clock_name"
            fi
        done <<< "$clock_details"
        
        # Determine overall status based on max latency
        if [ $max_latency_overall -ge 580 ]; then
            overall_status="FAILED"
            details="$num_clocks clocks: Max ${max_latency_overall}ps (CRITICAL)"
        elif [ $max_latency_overall -gt 550 ]; then
            overall_status="WARN"
            details="$num_clocks clocks: Max ${max_latency_overall}ps (HIGH)"
        else
            overall_status="PASSED"
            details="$num_clocks clocks: Max ${max_latency_overall}ps"
        fi
    fi
    
    # Extract runtime if available
    runtime=$(echo "$clock_section" | grep -i "Runtime:" | head -1 | grep -oP "Runtime:\s*\K[0-9.]+ (hours|minutes|seconds)")
    [ -z "$runtime" ] && runtime="N/A"
    
    # Extract clock latency file path (contains trace per clock with highest latency path)
    # Format: "PT Clock Analysis: /path/to/...clock_latency"
    clock_latency_file=$(echo "$clock_section" | grep "PT Clock Analysis:" | grep -oP "PT Clock Analysis:\s*\K/[^\s]+" | head -1)
    [ -z "$clock_latency_file" ] && clock_latency_file="N/A"
    
    # Return pipe-delimited string (added clock_latency_file as 4th field)
    echo "${overall_status}|${details}|${runtime}|${clock_latency_file}"
}

# Parse block release output
# Args: $1 = output file path
# Returns: status|details|runtime
parse_release_output() {
    local output_file="$1"
    local status=""
    local details=""
    local runtime="N/A"
    
    # Extract Block Release section - using new comprehensive output format
    local release_section=$(grep -A 300 "Block Release\|Release Attempts from Workarea" "$output_file")
    
    if [ -z "$release_section" ]; then
        echo "NOT_FOUND|No block release information found|N/A"
        return
    fi
    
    # Don't check for "No block release attempts found" here - it might be in the log
    # We'll determine based on actual attempt counts below
    
    # Strip ANSI color codes from the section
    release_section=$(echo "$release_section" | sed 's/\x1b\[[0-9;]*m//g')
    
    # Extract total attempts, successful, and failed counts
    # Format: "Total Attempts: 5"
    local total_attempts=$(echo "$release_section" | grep -i "Total Attempts:" | head -1 | grep -oP "Total Attempts:\s*\K[0-9]+" | head -1)
    local successful_attempts=$(echo "$release_section" | grep -i "Successful:" | head -1 | grep -oP "Successful:\s*\K[0-9]+" | head -1)
    local failed_attempts=$(echo "$release_section" | grep -i "Failed:" | head -1 | grep -oP "Failed:\s*\K[0-9]+" | head -1)
    
    # Set defaults if extraction failed
    [ -z "$total_attempts" ] && total_attempts=0
    [ -z "$successful_attempts" ] && successful_attempts=0
    [ -z "$failed_attempts" ] && failed_attempts=0
    
    # Extract custom links from "All Custom Links in Central Release Area" table
    # Parse the table to get link names with their sources (NBU/ROOT)
    local custom_links=""
    local nbu_links_count=0
    local root_links_count=0
    local has_nbu_signoff=0
    
    # Check for NBU Signoff Mode indicator
    if echo "$release_section" | grep -q "NBU Signoff Mode"; then
        has_nbu_signoff=1
    fi
    
    # Parse custom links from the comprehensive table
    # Extract link names from lines between table header and summary line
    local in_table=0
    local link_names=()
    while IFS= read -r line; do
        # Start of table
        if [[ "$line" =~ "Link Name".*"Date".*"User".*"Source" ]]; then
            in_table=1
            continue
        fi
        
        # End of table (summary line)
        if [[ "$line" =~ "Total:".*"custom links" ]]; then
            # Extract NBU and ROOT counts from summary
            if [[ "$line" =~ ([0-9]+)\ from\ NBU\ signoff ]]; then
                nbu_links_count="${BASH_REMATCH[1]}"
            fi
            if [[ "$line" =~ ([0-9]+)\ from\ ROOT ]]; then
                root_links_count="${BASH_REMATCH[1]}"
            fi
            break
        fi
        
        # Skip separator lines
        if [[ "$line" =~ ^[[:space:]]*-+[[:space:]]*-+[[:space:]]* ]]; then
            continue
        fi
        
        # Extract link name (first column, may have color codes)
        if [ $in_table -eq 1 ]; then
            # Parse table row: link_name is first field after whitespace
            local link_name=$(echo "$line" | awk '{print $1}' | tr -d '[:space:]')
            if [ -n "$link_name" ] && [ "$link_name" != "Link" ]; then
                link_names+=("$link_name")
            fi
        fi
    done <<< "$release_section"
    
    # Build custom_links string
    if [ ${#link_names[@]} -gt 0 ]; then
        custom_links=$(IFS=', '; echo "${link_names[*]}")
    fi
    
    # Determine overall release status based on attempts
    local overall_status="UNKNOWN"
    
    if [ $total_attempts -eq 0 ]; then
        overall_status="NOT_FOUND"
        details="No release attempts detected"
    elif [ $successful_attempts -gt 0 ] && [ $failed_attempts -eq 0 ]; then
        # All attempts successful
        overall_status="PASSED"
        details="${successful_attempts} successful / ${total_attempts} total attempts"
        
        # Add NBU signoff indicator if detected
        if [ $has_nbu_signoff -eq 1 ]; then
            details="${details} [NBU]"
        fi
        
        # Add custom links if available
        if [ -n "$custom_links" ]; then
            # Truncate long custom links list for display
            if [ ${#custom_links} -gt 60 ]; then
                custom_links="${custom_links:0:57}..."
            fi
            details="${details}; Links: ${custom_links}"
            
            # Add NBU/ROOT breakdown if available
            if [ $nbu_links_count -gt 0 ] || [ $root_links_count -gt 0 ]; then
                details="${details} (${nbu_links_count} NBU, ${root_links_count} ROOT)"
            fi
        fi
        
    elif [ $successful_attempts -gt 0 ] && [ $failed_attempts -gt 0 ]; then
        # Mixed success and failure - partial success
        overall_status="WARN"
        details="${successful_attempts} successful, ${failed_attempts} failed / ${total_attempts} total"
        
        # Add NBU signoff indicator if detected
        if [ $has_nbu_signoff -eq 1 ]; then
            details="${details} [NBU]"
        fi
        
        # Add custom links if available
        if [ -n "$custom_links" ]; then
            if [ ${#custom_links} -gt 50 ]; then
                custom_links="${custom_links:0:47}..."
            fi
            details="${details}; Links: ${custom_links}"
            
            # Add NBU/ROOT breakdown if available
            if [ $nbu_links_count -gt 0 ] || [ $root_links_count -gt 0 ]; then
                details="${details} (${nbu_links_count} NBU, ${root_links_count} ROOT)"
            fi
        fi
        
    elif [ $failed_attempts -gt 0 ] && [ $successful_attempts -eq 0 ]; then
        # All attempts failed
        overall_status="FAILED"
        details="All ${failed_attempts} release attempts FAILED"
        
        # Add NBU signoff indicator if detected
        if [ $has_nbu_signoff -eq 1 ]; then
            details="${details} [NBU]"
        fi
    else
        # Unknown state
        overall_status="UNKNOWN"
        details="Unable to determine release status"
    fi
    
    # Extract runtime from latest attempt (if available)
    # Look for "Status: SUCCESS" or "Status: FAILED" lines, then find Runtime nearby
    runtime=$(echo "$release_section" | grep -i "Runtime:" | tail -1 | grep -oP "Runtime:\s*\K[0-9.]+ (hours|minutes|seconds)")
    [ -z "$runtime" ] && runtime="N/A"
    
    # Extract flags from latest successful attempt for release type badges
    # Find the last SUCCESS attempt and get its flags
    latest_flags=""
    if [ $successful_attempts -gt 0 ]; then
        # Extract the last successful attempt's flags line
        # Format: "Flags: sta_release, fcl_release, pnr_release, fe_dct_release"
        latest_flags=$(awk '/Block Release Attempts:/,/Release Attempts from Workarea/ {
            if (/Status:.*SUCCESS/) {
                success=1
                next
            }
            if (success && /Flags:/) {
                print
                success=0
            }
        }' <<< "$release_section" | tail -1 | sed 's/.*Flags:[[:space:]]*//' | tr -d '\n')
    fi
    [ -z "$latest_flags" ] && latest_flags="N/A"
    
    # Return pipe-delimited string (added flags as 4th field)
    echo "${overall_status}|${details}|${runtime}|${latest_flags}"
}

# Parse GL Check output
# Args: $1 = output file path
# Returns: status|details|runtime|total_errors|waived|non_waived|top_3_checkers
parse_glcheck_output() {
    local output_file="$1"
    local status=""
    local details=""
    local runtime="N/A"
    
    # Extract GL Check section
    local glcheck_section=$(grep -A 200 "GL Check\|GL Checks" "$output_file")
    
    if [ -z "$glcheck_section" ]; then
        echo "NOT_FOUND|No GL Check analysis found|N/A|N/A|N/A|N/A|N/A"
        return
    fi
    
    # Check for "Didn't run GL checks" message
    if echo "$glcheck_section" | grep -q "Didn't run GL checks"; then
        echo "NOT_FOUND|GL checks not run|N/A|N/A|N/A|N/A|N/A"
        return
    fi
    
    # Strip ANSI color codes
    glcheck_section=$(echo "$glcheck_section" | sed 's/\x1b\[[0-9;]*m//g')
    
    # Extract error counts
    # Format: "Total Errors: 150", "Waived: 100", "Non-Waived: 50"
    local total_errors=$(echo "$glcheck_section" | grep -i "Total Errors:" | grep -oP "Total Errors:\s*\K[0-9]+" | head -1)
    local waived=$(echo "$glcheck_section" | grep -i "^\s*Waived:" | grep -oP "Waived:\s*\K[0-9]+" | head -1)
    local non_waived=$(echo "$glcheck_section" | grep -i "^\s*Non-Waived:" | grep -oP "Non-Waived:\s*\K[0-9]+" | head -1)
    
    # Set defaults if extraction failed
    [ -z "$total_errors" ] && total_errors="N/A"
    [ -z "$waived" ] && waived="N/A"
    [ -z "$non_waived" ] && non_waived="N/A"
    
    # Determine overall GL Check status based on non-waived count
    local overall_status="UNKNOWN"
    
    if [ "$total_errors" = "N/A" ] && [ "$waived" = "N/A" ] && [ "$non_waived" = "N/A" ]; then
        overall_status="NO_DATA"
        details="No GL Check data available"
    elif [ "$non_waived" = "N/A" ]; then
        overall_status="NO_DATA"
        details="Unable to parse GL Check data"
    else
        # Convert to number for comparison
        local non_waived_num=$non_waived
        
        if [ $non_waived_num -eq 0 ]; then
            overall_status="PASSED"
            details="Total: ${total_errors}, Waived: ${waived}, Non-Waived: ${non_waived} (CLEAN)"
        elif [ $non_waived_num -lt 50 ]; then
            overall_status="WARN"
            details="Total: ${total_errors}, Waived: ${waived}, Non-Waived: ${non_waived} (MINOR)"
        else
            overall_status="FAILED"
            details="Total: ${total_errors}, Waived: ${waived}, Non-Waived: ${non_waived} (CRITICAL)"
        fi
    fi
    
    # Extract top 3 checkers with highest non-waived counts (for detailed display)
    # Format: "Checker [Code](Name)    Waived    Non-Waived   Total"
    # Parse the table, extract all checkers, sort by non-waived count, take top 3
    local checkers_table=$(echo "$glcheck_section" | awk '/GL Check Results by Checker:/,/^$/ {print}' | grep -E "^\s+\[" | sed 's/\x1b\[[0-9;]*m//g')
    
    # Parse all checkers and extract name + non-waived count, then sort by non-waived descending
    local top_3_checkers=""
    if [ -n "$checkers_table" ]; then
        # Parse each line: extract checker name and non-waived count (2nd numeric column)
        # Then sort by non-waived count (descending) and take top 3
        local sorted_checkers=$(echo "$checkers_table" | while IFS= read -r line; do
            if [ -z "$line" ]; then
                continue
            fi
            # Extract checker name (first field with brackets)
            checker=$(echo "$line" | awk '{print $1}')
            # Extract non-waived count (2nd numeric column in the table)
            # Table format: Checker    Waived    Non-Waived    Total
            #               $1         $2        $3            $4
            nw=$(echo "$line" | awk '{for(i=1;i<=NF;i++){if($i~/^[0-9]+$/){count++; if(count==2){print $i; break}}}}')
            
            if [ -n "$checker" ] && [ -n "$nw" ]; then
                # Output format: non_waived_count|checker_name (for sorting)
                echo "${nw}|${checker}"
            fi
        done | sort -t'|' -k1,1nr | head -3)
        
        # Convert sorted results to semicolon-delimited format
        while IFS='|' read -r nw checker; do
            [ -n "$top_3_checkers" ] && top_3_checkers="${top_3_checkers};"
            top_3_checkers="${top_3_checkers}${checker}:${nw}"
        done <<< "$sorted_checkers"
    fi
    
    [ -z "$top_3_checkers" ] && top_3_checkers="N/A"
    
    # Extract runtime and run date from Runtime section (look for GL Check runtime line)
    # Format: "  Signoff      GL Check                    0.59 hours           10/20 08:27 10/20 09:02"
    local runtime_line=$(grep -A 100 "\[2\] Runtime\|Runtime Summary" "$output_file" | grep -E "Signoff\s+GL Check" | sed 's/\x1b\[[0-9;]*m//g' | head -1)
    
    runtime=$(echo "$runtime_line" | awk '{
        for (i=1; i<=NF; i++) {
            if ($i ~ /hours|minutes|seconds/) {
                print $(i-1), $i
                break
            }
        }
    }')
    [ -z "$runtime" ] && runtime="N/A"
    
    # Extract start date/time (format: MM/DD HH:MM)
    local run_date=$(echo "$runtime_line" | awk '{
        for (i=1; i<=NF; i++) {
            if ($i ~ /^[0-9]{1,2}\/[0-9]{1,2}$/) {
                # Found date, next field is time
                if (i+1 <= NF) {
                    print $i, $(i+1)
                    break
                }
            }
        }
    }')
    [ -z "$run_date" ] && run_date="N/A"
    
    # Return pipe-delimited string with all fields (added run_date as last field)
    echo "${overall_status}|${details}|${runtime}|${total_errors}|${waived}|${non_waived}|${top_3_checkers}|${run_date}"
}

# Export functions and variables for parallel execution
# Note: Must export AFTER functions are defined to avoid warnings
export -f run_unit_analysis
export -f parse_formal_output
export -f parse_timing_output
export -f parse_pv_output
export -f parse_clock_output
export -f parse_release_output
export -f parse_glcheck_output
export -f save_state
export -f log_debug
export -f log_verbose
export PYTHON_BIN AVICE_SCRIPT VERBOSE QUIET BLUE MAGENTA NC MAX_RETRIES RETRY_DELAY

# Get section flag for avice_wa_review.py based on regression type
get_analysis_section() {
    case "$REGRESSION_TYPE" in
        formal)
            # Request both runtime and formal sections to get Formal runtime data
            echo "runtime formal"
            ;;
        timing)
            # Request both runtime and pt sections to get PT runtime data
            echo "runtime pt"
            ;;
        pv)
            # Request both runtime and pv sections to get PV runtime data
            echo "runtime pv"
            ;;
        clock)
            echo "clock"
            ;;
        release)
            echo "block-release"
            ;;
        glcheck)
            # Request both runtime and gl-check sections to get GL Check runtime data
            echo "runtime gl-check"
            ;;
        *)
            echo "ERROR"
            ;;
    esac
}

# Get friendly name for regression type
get_regression_name() {
    case "$REGRESSION_TYPE" in
        formal)
            echo "Formal Verification"
            ;;
        timing)
            echo "PT Signoff Timing"
            ;;
        pv)
            echo "Physical Verification"
            ;;
        clock)
            echo "Clock Tree Analysis"
            ;;
        release)
            echo "Block Release Status"
            ;;
        glcheck)
            echo "GL Check Analysis"
            ;;
        *)
            echo "Analysis"
            ;;
    esac
}

# Extract workarea path from a release directory
# Args: $1 = release_dir (e.g., /home/agur_backend_blockRelease/block/pmux/pmux_rbv_...)
# Returns: workarea path (via echo)
extract_workarea_from_release() {
    local release_dir="$1"
    local log_file="$release_dir/logs/block_release.log"
    
    if [ ! -f "$log_file" ]; then
        log_verbose "Warning: block_release.log not found in $release_dir"
        echo ""
        return 1
    fi
    
    # Extract source workarea from log file
    # Try multiple patterns:
    # 1. "Create block_release beflow workdir = /home/scratch.USER/..."
    # 2. "Release <unit> from <workarea_name>" (need to reconstruct full path)
    # 3. Extract from copy paths (first Copy line has full source path)
    
    local workarea=""
    
    # Pattern 1: beflow workdir line (most reliable, contains full path)
    workarea=$(grep -a "beflow workdir = " "$log_file" | head -1 | sed 's/^.*beflow workdir = *//' | sed 's|/export/block_release.*||')
    
    if [ -z "$workarea" ]; then
        # Pattern 2: Extract from Copy lines (they show full source paths)
        workarea=$(grep -a "Copy /home/" "$log_file" | head -1 | sed 's/^.*Copy *//' | sed 's|/export/.*||')
    fi
    
    if [ -z "$workarea" ]; then
        log_verbose "Warning: Could not extract workarea from $log_file"
        echo ""
        return 1
    fi
    
    echo "$workarea"
    return 0
}

# Resolve release for a unit: Try custom release first, fallback to last_sta_rel
# Args: $1 = unit name, $2 = custom_release_name (optional)
# Sets global: RESOLVED_WORKAREA, RESOLVED_RELEASE_NAME, RESOLVED_RTL_TAG, RESOLVED_RELEASE_DATE, RESOLVED_RELEASE_USER
# Returns: 0 if custom release found, 1 if fallback used
resolve_release() {
    local unit="$1"
    local custom_release="$2"
    local base_dir="/home/agur_backend_blockRelease/block/$unit"
    
    # Initialize globals
    RESOLVED_WORKAREA=""
    RESOLVED_RELEASE_NAME="last_sta_rel"
    RESOLVED_RTL_TAG=""
    RESOLVED_RELEASE_DATE=""
    RESOLVED_RELEASE_USER=""
    
    # If no custom release specified, use default last_sta_rel
    if [ -z "$custom_release" ]; then
        log_debug "No custom release specified for $unit - using last_sta_rel"
        return 1  # Indicate fallback (default behavior)
    fi
    
    # Convert custom release name to lowercase for case-insensitive matching
    local custom_release_lower=$(echo "$custom_release" | tr '[:upper:]' '[:lower:]')
    log_debug "Looking for custom release '$custom_release' (lowercase: $custom_release_lower) for unit $unit"
    
    # Search for matching release directory (case-insensitive, partial match)
    local release_dir=""
    local best_match=""
    local newest_mtime=0
    
    # First, check if it's a symbolic link (e.g., NOV_02 -> actual release dir)
    for item in "$base_dir"/*; do
        [ -e "$item" ] || continue  # Skip if doesn't exist
        local basename=$(basename "$item")
        local basename_lower=$(echo "$basename" | tr '[:upper:]' '[:lower:]')
        
        # Check for partial match
        if [[ "$basename_lower" == *"$custom_release_lower"* ]]; then
            # Resolve symlinks
            local resolved_item=$(readlink -f "$item")
            if [ -d "$resolved_item" ]; then
                # If multiple matches, use the most recent one
                local mtime=$(stat -c %Y "$resolved_item" 2>/dev/null || echo 0)
                if [ $mtime -gt $newest_mtime ]; then
                    newest_mtime=$mtime
                    best_match="$resolved_item"
                    release_dir="$resolved_item"
                    RESOLVED_RELEASE_NAME="$basename"
                    log_debug "Found matching release: $basename -> $resolved_item (mtime: $mtime)"
                fi
            fi
        fi
    done
    
    # If custom release found, extract workarea from it
    if [ -n "$release_dir" ] && [ -d "$release_dir" ]; then
        local workarea=$(extract_workarea_from_release "$release_dir")
        if [ -n "$workarea" ]; then
            RESOLVED_WORKAREA="$workarea"
            
            # Extract additional metadata from release log
            local log_file="$release_dir/logs/block_release.log"
            if [ -f "$log_file" ]; then
                RESOLVED_RELEASE_DATE=$(grep -a "^\-I\- \[" "$log_file" | grep "Release $unit from" | head -1 | sed 's/^-I- \[\(.*\)\].*/\1/')
                RESOLVED_RELEASE_USER=$(grep -a "^\-I\- \[" "$log_file" | grep " USER:" | head -1 | sed 's/^-I- \[.*\] USER: //')
                
                # Try to extract RTL tag from rbv/README in the source workarea
                if [ -d "$workarea/rbv" ] && [ -f "$workarea/rbv/README" ]; then
                    RESOLVED_RTL_TAG=$(sed -n '2p' "$workarea/rbv/README" | sed 's/^TAG: //')
                fi
            fi
            
            log_verbose "✓ Using custom release '$RESOLVED_RELEASE_NAME' for $unit"
            log_verbose "  Workarea: $RESOLVED_WORKAREA"
            return 0  # Custom release found and used
        else
            log_verbose "⚠ Custom release found but could not extract workarea - falling back to last_sta_rel"
        fi
    else
        log_verbose "⚠ Custom release '$custom_release' not found for $unit - falling back to last_sta_rel"
    fi
    
    # Fallback to last_sta_rel (return 1 to indicate fallback)
    return 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            # Support comma-separated types: -t formal,pv
            IFS=',' read -ra TYPES <<< "$2"
            for type in "${TYPES[@]}"; do
                REGRESSION_TYPES+=("$type")
            done
            shift 2
            ;;
        -c|--chiplet)
            # Support comma-separated chiplets: -c CPORT,CFAN (case-insensitive)
            IFS=',' read -ra TEMP_CHIPLETS <<< "$2"
            for chiplet in "${TEMP_CHIPLETS[@]}"; do
                # Convert to uppercase for case-insensitive matching
                FILTER_CHIPLETS+=("$(echo "$chiplet" | tr '[:lower:]' '[:upper:]')")
            done
            shift 2
            ;;
        -u|--unit)
            FILTER_UNIT="$2"
            shift 2
            ;;
        -r|--release)
            CUSTOM_RELEASE="$2"
            shift 2
            ;;
        -j|--jobs)
            if [ "$2" = "auto" ]; then
                # Smart auto-detect: Consider CPU cores but cap at reasonable maximum
                # Logic: min(num_cores, 16) for optimal balance
                # Reason: Beyond 16 jobs, overhead dominates and performance degrades
                CPU_CORES=$(nproc 2>/dev/null || echo 4)
                if [ $CPU_CORES -le 16 ]; then
                    PARALLEL_JOBS=$CPU_CORES
                else
                    PARALLEL_JOBS=16  # Cap at 16 for optimal performance
                fi
                AUTO_DETECTED_JOBS=1
            else
                PARALLEL_JOBS="$2"
                AUTO_DETECTED_JOBS=0  # User explicitly set jobs
            fi
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -q|--quiet)
            QUIET=1
            shift
            ;;
        -nq|--no-quiet)
            QUIET=0
            shift
            ;;
        --no-update)
            NO_UPDATE=1
            shift
            ;;
        --resume)
            RESUME_FILE="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Default to all regression types if none specified
if [ ${#REGRESSION_TYPES[@]} -eq 0 ]; then
    echo -e "${CYAN}No regression type specified - running ALL types${NC}"
    REGRESSION_TYPES=("formal" "timing" "pv" "clock" "release" "glcheck")
    echo ""
fi

# Validate each regression type
for type in "${REGRESSION_TYPES[@]}"; do
    case "$type" in
        formal|timing|pv|clock|release|glcheck)
            # Valid regression type
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Invalid regression type: $type"
            echo "Valid types: formal, timing, pv, clock, release, glcheck"
            echo ""
            show_help
            ;;
    esac
done

# Load configuration file if specified
if [ -n "$CONFIG_FILE" ]; then
    load_config "$CONFIG_FILE"
fi

# Validate parallel jobs setting
if ! [[ "$PARALLEL_JOBS" =~ ^[0-9]+$ ]] || [ "$PARALLEL_JOBS" -lt 1 ]; then
    echo -e "${RED}[ERROR]${NC} Invalid parallel jobs value: $PARALLEL_JOBS"
    echo "Must be a positive integer or 'auto'"
    exit 1
fi

# Set HTML output filename based on number of regression types
if [ ${#REGRESSION_TYPES[@]} -eq 1 ]; then
    HTML_FILE="agur_${REGRESSION_TYPES[0]}_regression_dashboard_${TIMESTAMP}.html"
else
    HTML_FILE="agur_multi_regression_dashboard_${TIMESTAMP}.html"
fi

# Set state file for resume capability
STATE_FILE=".agur_regression_state_${TIMESTAMP}.txt"

# Load resume state if specified
if [ -n "$RESUME_FILE" ]; then
    if [ ! -f "$RESUME_FILE" ]; then
        echo -e "${RED}[ERROR]${NC} Resume file not found: $RESUME_FILE"
        exit 1
    fi
    echo -e "${CYAN}Resuming from previous run: $RESUME_FILE${NC}"
    STATE_FILE="$RESUME_FILE"
    log_verbose "Loaded $(wc -l < "$RESUME_FILE") completed units from state file"
fi

#===============================================================================
# Main Script
#===============================================================================

# Start timer for ETA calculations
START_TIME=$SECONDS

# Print header only if not in quiet mode
if [ $QUIET -eq 0 ]; then
print_header

# Display execution mode information
if [ $DRY_RUN -eq 1 ]; then
    echo -e "${YELLOW}[DRY-RUN MODE]${NC} Preview only - no analyses will be executed"
    echo ""
fi

if [ $VERBOSE -eq 1 ]; then
    echo -e "${BLUE}[VERBOSE MODE]${NC} Debug output enabled"
    echo ""
fi

    # Only show parallel mode message if not auto-detected (already shown above)
    if [ $PARALLEL_JOBS -gt 1 ] && [ $AUTO_DETECTED_JOBS -eq 0 ]; then
    echo -e "${GREEN}[PARALLEL MODE]${NC} Running with $PARALLEL_JOBS parallel jobs"
    log_verbose "CPU cores available: $(nproc 2>/dev/null || echo 'unknown')"
    echo ""
    fi
fi

# Auto-update AGUR units table (unless --no-update is specified)
if [ $NO_UPDATE -eq 0 ]; then
    if [ $QUIET -eq 0 ]; then
        echo -e "${CYAN}Updating AGUR units table...${NC}"
    fi
    
    # Run extract script
    EXTRACT_SCRIPT="$SCRIPT_DIR/extract_agur_releases.sh"
    if [ -f "$EXTRACT_SCRIPT" ]; then
        if [ $QUIET -eq 1 ]; then
            # In quiet mode, suppress extract script output
            "$EXTRACT_SCRIPT" > /dev/null 2>&1
        else
            "$EXTRACT_SCRIPT"
        fi
        
        if [ $? -eq 0 ]; then
            if [ $QUIET -eq 0 ]; then
                echo -e "${GREEN}[OK] AGUR units table updated${NC}"
                echo ""
            fi
        else
            echo -e "${RED}[ERROR]${NC} Failed to update AGUR units table"
            exit 1
        fi
    else
        echo -e "${YELLOW}[WARN]${NC} Extract script not found: $EXTRACT_SCRIPT"
        echo "Continuing with existing units table..."
        echo ""
    fi
fi

# Check if units table exists
if [ ! -f "$UNITS_TABLE" ]; then
    echo -e "${RED}[ERROR]${NC} Units table not found: $UNITS_TABLE"
    echo "Run: cd $SCRIPT_DIR && ./extract_agur_releases.sh"
    exit 1
fi

# Check if avice_wa_review.py exists
if [ ! -f "$AVICE_SCRIPT" ]; then
    echo -e "${RED}[ERROR]${NC} Script not found: $AVICE_SCRIPT"
    exit 1
fi

# Create temp directory
mkdir -p "$TEMP_DIR"

# Validate chiplet filter if specified
if [ ${#FILTER_CHIPLETS[@]} -gt 0 ]; then
    # Extract all valid chiplets from the table (case-insensitive, unique)
    declare -A VALID_CHIPLETS
    while IFS='|' read -r unit chiplet workarea rtl_tag release_types release_date release_user; do
        # Skip comments and empty lines
        [[ "$unit" =~ ^#.*$ ]] && continue
        [[ -z "$unit" ]] && continue
        
        # Trim and uppercase chiplet
        chiplet=$(echo "$chiplet" | xargs | tr '[:lower:]' '[:upper:]')
        VALID_CHIPLETS["$chiplet"]=1
    done < "$UNITS_TABLE"
    
    # Check if user-specified chiplets exist
    INVALID_CHIPLETS=()
    for filter_chiplet in "${FILTER_CHIPLETS[@]}"; do
        if [ -z "${VALID_CHIPLETS[$filter_chiplet]}" ]; then
            INVALID_CHIPLETS+=("$filter_chiplet")
        fi
    done
    
    # Report error if invalid chiplets found
    if [ ${#INVALID_CHIPLETS[@]} -gt 0 ]; then
        echo -e "${RED}Error: Invalid chiplet(s) specified: ${INVALID_CHIPLETS[*]}${NC}"
        echo ""
        echo -e "${CYAN}Available chiplets in AGUR_UNITS_TABLE.txt:${NC}"
        for chiplet in "${!VALID_CHIPLETS[@]}"; do
            echo "  - $chiplet"
        done | sort
        echo ""
        echo "Use: $0 -c <CHIPLET> -t <TYPE>"
        exit 1
    fi
fi

# Read units from table
declare -a UNITS
declare -a CHIPLETS
declare -a WORKAREAS
declare -a RTL_TAGS
declare -a RELEASE_DATES
declare -a RELEASE_USERS
declare -a RELEASE_NAMES  # Track which release was used per unit (e.g., "NOV_02" or "last_sta_rel")

while IFS='|' read -r unit chiplet workarea rtl_tag release_types release_date release_user release_path; do
    # Skip comments and empty lines
    [[ "$unit" =~ ^#.*$ ]] && continue
    [[ -z "$unit" ]] && continue
    
    # Trim whitespace
    unit=$(echo "$unit" | xargs)
    chiplet=$(echo "$chiplet" | xargs)
    workarea=$(echo "$workarea" | xargs)
    rtl_tag=$(echo "$rtl_tag" | xargs)
    release_date=$(echo "$release_date" | xargs)
    release_user=$(echo "$release_user" | xargs)
    # Note: release_path (8th field) is read but not used - prevents field overflow into release_user
    
    # Apply filters
    if [ ${#FILTER_CHIPLETS[@]} -gt 0 ]; then
        # Check if unit's chiplet is in the FILTER_CHIPLETS array (case-insensitive)
        chiplet_upper=$(echo "$chiplet" | tr '[:lower:]' '[:upper:]')
        chiplet_match=0
        for filter_chiplet in "${FILTER_CHIPLETS[@]}"; do
            if [ "$chiplet_upper" = "$filter_chiplet" ]; then
                chiplet_match=1
                break
            fi
        done
        if [ $chiplet_match -eq 0 ]; then
            continue
        fi
    fi
    if [ -n "$FILTER_UNIT" ] && [ "$unit" != "$FILTER_UNIT" ]; then
        continue
    fi
    
    # Try to resolve custom release if specified
    release_name="last_sta_rel"
    if [ -n "$CUSTOM_RELEASE" ]; then
        resolve_release "$unit" "$CUSTOM_RELEASE"
        if [ $? -eq 0 ] && [ -n "$RESOLVED_WORKAREA" ]; then
            # Custom release found - use it
            workarea="$RESOLVED_WORKAREA"
            release_name="$RESOLVED_RELEASE_NAME"
            [ -n "$RESOLVED_RTL_TAG" ] && rtl_tag="$RESOLVED_RTL_TAG"
            [ -n "$RESOLVED_RELEASE_DATE" ] && release_date="$RESOLVED_RELEASE_DATE"
            [ -n "$RESOLVED_RELEASE_USER" ] && release_user="$RESOLVED_RELEASE_USER"
        fi
        # If resolve_release() returned 1 (fallback), keep original values from table
    fi
    
    UNITS+=("$unit")
    CHIPLETS+=("$chiplet")
    WORKAREAS+=("$workarea")
    RTL_TAGS+=("$rtl_tag")
    RELEASE_DATES+=("$release_date")
    RELEASE_USERS+=("$release_user")
    RELEASE_NAMES+=("$release_name")
done < "$UNITS_TABLE"

TOTAL_UNITS=${#UNITS[@]}

if [ $TOTAL_UNITS -eq 0 ]; then
    echo -e "${RED}[ERROR]${NC} No units found matching the filter criteria"
    exit 1
fi

# Calculate release statistics if custom release was specified
if [ -n "$CUSTOM_RELEASE" ]; then
    CUSTOM_RELEASE_COUNT=0
    FALLBACK_COUNT=0
    for release_name in "${RELEASE_NAMES[@]}"; do
        if [ "$release_name" != "last_sta_rel" ]; then
            ((CUSTOM_RELEASE_COUNT++))
        else
            ((FALLBACK_COUNT++))
        fi
    done
    
    # Display release summary (always shown, even in quiet mode)
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${CYAN}  RELEASE SELECTION SUMMARY${NC}"
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${GREEN}Target Release:${NC} $CUSTOM_RELEASE"
    echo -e "${GREEN}Found in:${NC} $CUSTOM_RELEASE_COUNT/$TOTAL_UNITS units"
    if [ $FALLBACK_COUNT -gt 0 ]; then
        echo -e "${YELLOW}Fallback (last_sta_rel):${NC} $FALLBACK_COUNT units"
    fi
    echo ""
fi

# Smart auto-adjust parallel jobs based on unit count (if -j auto was used)
if [ $AUTO_DETECTED_JOBS -eq 1 ]; then
    CPU_CORES=$(nproc 2>/dev/null || echo 4)
    ORIGINAL_JOBS=$PARALLEL_JOBS
    
    # Smart logic: min(cpu_cores, num_units, 16)
    # Don't use more jobs than units, and cap at 16 for optimal performance
    if [ $TOTAL_UNITS -lt $PARALLEL_JOBS ]; then
        PARALLEL_JOBS=$TOTAL_UNITS
    fi
    
    # Display auto-detect message (always shown, even in quiet mode)
    if [ $CPU_CORES -gt 16 ] && [ $ORIGINAL_JOBS -eq 16 ]; then
        # CPU cores were capped at 16
        if [ $PARALLEL_JOBS -lt 16 ]; then
            echo -e "${CYAN}[AUTO-DETECT]${NC} Detected $CPU_CORES CPU cores, $TOTAL_UNITS units -> Using $PARALLEL_JOBS jobs (matched to unit count)"
        else
            echo -e "${CYAN}[AUTO-DETECT]${NC} Detected $CPU_CORES CPU cores -> Using $PARALLEL_JOBS jobs (capped for optimal performance)"
        fi
    elif [ $PARALLEL_JOBS -lt $ORIGINAL_JOBS ]; then
        # Jobs adjusted down to match unit count
        echo -e "${CYAN}[AUTO-DETECT]${NC} Detected $CPU_CORES CPU cores, $TOTAL_UNITS units -> Using $PARALLEL_JOBS jobs (matched to unit count)"
    else
        # Using all detected cores
        echo -e "${CYAN}[AUTO-DETECT]${NC} Using $PARALLEL_JOBS CPU cores (auto-detected via nproc)"
    fi
    echo ""
fi

# Print unit count and filters only if not in quiet mode
if [ $QUIET -eq 0 ]; then
echo -e "${GREEN}Found $TOTAL_UNITS unit(s) to analyze${NC}"
if [ ${#FILTER_CHIPLETS[@]} -gt 0 ]; then
    echo "Filter: Chiplet = ${FILTER_CHIPLETS[*]}"
fi
if [ -n "$FILTER_UNIT" ]; then
    echo "Filter: Unit = $FILTER_UNIT"
fi
echo ""
fi

# Arrays to store results per regression type
# Structure: REGRESSION_RESULTS[type_unitidx_field] = value
declare -A REGRESSION_RESULTS

# Run analysis for each regression type
for REGRESSION_TYPE in "${REGRESSION_TYPES[@]}"; do
    
    # Arrays to store results for this regression type
    declare -a ANALYSIS_STATUS
    declare -a ANALYSIS_DETAILS
    declare -a ANALYSIS_RUNTIMES

    # Get analysis section name for this regression type
    ANALYSIS_SECTION=$(get_analysis_section)
    REGRESSION_NAME=$(get_regression_name)

    # Run analysis on each unit
    if [ $QUIET -eq 0 ]; then
    print_section "Running $REGRESSION_NAME Analysis"
    echo ""
    fi
    
    # Dry-run mode: just preview
    if [ $DRY_RUN -eq 1 ]; then
        if [ $QUIET -eq 0 ]; then
        echo -e "${YELLOW}[DRY-RUN] Would analyze the following units:${NC}"
        for i in "${!UNITS[@]}"; do
            unit="${UNITS[$i]}"
            chiplet="${CHIPLETS[$i]}"
            workarea="${WORKAREAS[$i]}"
            
            # Check if already processed (for resume)
            if [ -n "$RESUME_FILE" ] && is_unit_processed "$STATE_FILE" "$REGRESSION_TYPE" "$i"; then
                echo "  [$((i+1))/$TOTAL_UNITS] $unit ($chiplet) - ${GREEN}ALREADY COMPLETED (skipped)${NC}"
            else
                echo "  [$((i+1))/$TOTAL_UNITS] $unit ($chiplet) - $workarea"
            fi
        done
        echo ""
        fi
        
        # Initialize empty results for dry-run
        for i in "${!UNITS[@]}"; do
            ANALYSIS_STATUS+=("NOT_RUN")
            ANALYSIS_DETAILS+=("Dry-run mode - not executed")
            ANALYSIS_RUNTIMES+=("N/A")
        done
    else
        # Real execution: sequential or parallel
        
        # Launch analyses (parallel or sequential)
        declare -a job_pids=()
        jobs_running=0
        units_completed=0
        
        for i in "${!UNITS[@]}"; do
            unit="${UNITS[$i]}"
            chiplet="${CHIPLETS[$i]}"
            workarea="${WORKAREAS[$i]}"
            
            # Check if already processed (for resume)
            if [ -n "$RESUME_FILE" ] && is_unit_processed "$STATE_FILE" "$REGRESSION_TYPE" "$i"; then
                log_verbose "Skipping already processed unit: $unit"
                
                # Load previous result
                result_file="$TEMP_DIR/${unit}_${REGRESSION_TYPE}_result.txt"
                if [ -f "$result_file" ]; then
                    parse_result=$(cat "$result_file")
                else
                    parse_result="NOT_FOUND|Previous result not found|N/A"
                fi
                
                IFS='|' read -r overall_status details runtime <<< "$parse_result"
                ANALYSIS_STATUS+=("$overall_status")
                ANALYSIS_DETAILS+=("$details")
                ANALYSIS_RUNTIMES+=("$runtime")
                ((units_completed++))
                continue
            fi
            
            # Show progress
            if [ $PARALLEL_JOBS -eq 1 ]; then
                # In sequential mode, show progress bar if quiet, otherwise show detailed info
                if [ $QUIET -eq 1 ]; then
                    show_progress "$units_completed" "$TOTAL_UNITS" "$unit" "$REGRESSION_TYPE"
                else
                echo ""
                print_section "Unit $((i+1))/$TOTAL_UNITS: $unit ($chiplet)"
                echo "Workarea: $workarea"
                echo "Released: ${RELEASE_DATES[$i]} by ${RELEASE_USERS[$i]}"
                if [ -n "$CUSTOM_RELEASE" ]; then
                    if [ "${RELEASE_NAMES[$i]}" != "last_sta_rel" ]; then
                        echo -e "${GREEN}Using release: ${RELEASE_NAMES[$i]}${NC}"
                    else
                        echo -e "${YELLOW}Using release: last_sta_rel (${CUSTOM_RELEASE} not found)${NC}"
                    fi
                fi
                echo ""
                echo -e "${CYAN}Running $REGRESSION_NAME analysis...${NC}"
                fi
            else
                show_progress "$units_completed" "$TOTAL_UNITS" "$unit" "$REGRESSION_TYPE"
            fi
            
            # Run analysis (parallel or sequential)
            if [ $PARALLEL_JOBS -gt 1 ]; then
                # Parallel mode: launch in background
                run_unit_analysis "$i" "$unit" "$chiplet" "$workarea" "$REGRESSION_TYPE" "$ANALYSIS_SECTION" "$TEMP_DIR" "$STATE_FILE" &
                job_pids[$i]=$!
                ((jobs_running++))
                
                # Wait if we've reached max parallel jobs
                if [ $jobs_running -ge $PARALLEL_JOBS ]; then
                    # Wait for any job to complete
                    # Suppress error if wait -n is not supported (falls through silently)
                    wait -n 2>/dev/null || true
                    ((jobs_running--))
                    ((units_completed++))
                fi
            else
                # Sequential mode: run directly
                run_unit_analysis "$i" "$unit" "$chiplet" "$workarea" "$REGRESSION_TYPE" "$ANALYSIS_SECTION" "$TEMP_DIR" "$STATE_FILE"
                ((units_completed++))
                
                # Show result in sequential mode (only if not quiet)
                if [ $QUIET -eq 0 ]; then
                result_file="$TEMP_DIR/${unit}_${REGRESSION_TYPE}_result.txt"
                if [ -f "$result_file" ]; then
                    parse_result=$(cat "$result_file")
                    IFS='|' read -r overall_status details runtime <<< "$parse_result"
                    
                    status_color="${YELLOW}"
                    case "$overall_status" in
                        PASSED)
                            status_color="${GREEN}"
                            ;;
                        FAILED|CRASHED|ERROR|MISSING)
                            status_color="${RED}"
                            ;;
                    esac
                    
                    echo -e "${status_color}Status: $overall_status${NC}"
                    echo "Details: $details"
                    echo "Runtime: $runtime"
                    fi
                fi
            fi
        done
        
        # Wait for all remaining jobs if in parallel mode
        if [ $PARALLEL_JOBS -gt 1 ]; then
            log_verbose "Waiting for remaining parallel jobs to complete..."
            wait
            show_progress "$TOTAL_UNITS" "$TOTAL_UNITS" "All units completed" "$REGRESSION_TYPE"
            echo ""  # New line after progress bar
        fi
        
        # Collect results from result files
        ANALYSIS_STATUS=()
        ANALYSIS_DETAILS=()
        ANALYSIS_RUNTIMES=()
        ANALYSIS_FLAGS=()
        ANALYSIS_CLOCK_LATENCY_FILES=()  # Clock-specific: path to clock_latency file
        
# Timing-specific arrays
ANALYSIS_SETUP_WNS=()
ANALYSIS_SETUP_TNS=()
ANALYSIS_SETUP_NVP=()
ANALYSIS_HOLD_WNS=()
ANALYSIS_HOLD_TNS=()
ANALYSIS_HOLD_NVP=()
ANALYSIS_DSR_SKEW_SETUP=()
ANALYSIS_DSR_SKEW_HOLD=()
ANALYSIS_SETUP_SCENARIO=()
ANALYSIS_HOLD_SCENARIO=()
ANALYSIS_PT_WORK_AREAS=()

# Formal-specific arrays
ANALYSIS_FAILING_COMPARE_PTS=()

# GL Check-specific arrays
ANALYSIS_TOTAL_ERRORS=()
ANALYSIS_WAIVED=()
ANALYSIS_NON_WAIVED=()
ANALYSIS_TOP_CHECKERS=()

# Analysis run dates (for GL Check, Formal, PT, PV)
ANALYSIS_RUN_DATES=()
        
        for i in "${!UNITS[@]}"; do
            unit="${UNITS[$i]}"
            result_file="$TEMP_DIR/${unit}_${REGRESSION_TYPE}_result.txt"
            
            if [ -f "$result_file" ]; then
                parse_result=$(cat "$result_file")
                
                # Timing regression has extra fields (including scenario names, PT work areas count, and run_date)
                if [ "$REGRESSION_TYPE" = "timing" ]; then
                    IFS='|' read -r overall_status details runtime setup_wns setup_tns setup_nvp hold_wns hold_tns hold_nvp dsr_skew_setup dsr_skew_hold setup_scenario hold_scenario pt_work_areas run_date <<< "$parse_result"
                    ANALYSIS_SETUP_WNS+=("$setup_wns")
                    ANALYSIS_SETUP_TNS+=("$setup_tns")
                    ANALYSIS_SETUP_NVP+=("$setup_nvp")
                    ANALYSIS_HOLD_WNS+=("$hold_wns")
                    ANALYSIS_HOLD_TNS+=("$hold_tns")
                    ANALYSIS_HOLD_NVP+=("$hold_nvp")
                    ANALYSIS_DSR_SKEW_SETUP+=("$dsr_skew_setup")
                    ANALYSIS_DSR_SKEW_HOLD+=("$dsr_skew_hold")
                    ANALYSIS_SETUP_SCENARIO+=("$setup_scenario")
                    ANALYSIS_HOLD_SCENARIO+=("$hold_scenario")
                    ANALYSIS_PT_WORK_AREAS+=("$pt_work_areas")
                    ANALYSIS_RUN_DATES+=("$run_date")
                elif [ "$REGRESSION_TYPE" = "formal" ]; then
                    # Formal regression has extra fields: failing_compare_points (4 flows: bbox|pnr|syn|syn_bbox) and run_date
                    IFS='|' read -r overall_status details runtime failing_pts run_date <<< "$parse_result"
                    ANALYSIS_FAILING_COMPARE_PTS+=("$failing_pts")
                    ANALYSIS_RUN_DATES+=("$run_date")
                elif [ "$REGRESSION_TYPE" = "pv" ]; then
                    # PV regression has extra field: run_date
                    IFS='|' read -r overall_status details runtime run_date <<< "$parse_result"
                    ANALYSIS_RUN_DATES+=("$run_date")
                elif [ "$REGRESSION_TYPE" = "clock" ]; then
                    # Clock regression has extra field: clock_latency_file
                    IFS='|' read -r overall_status details runtime clock_latency_file <<< "$parse_result"
                    ANALYSIS_CLOCK_LATENCY_FILES+=("$clock_latency_file")
                elif [ "$REGRESSION_TYPE" = "glcheck" ]; then
                    # GL Check regression has extra fields: total_errors, waived, non_waived, top_checkers, run_date
                    IFS='|' read -r overall_status details runtime total_errors waived non_waived top_checkers run_date <<< "$parse_result"
                    ANALYSIS_TOTAL_ERRORS+=("$total_errors")
                    ANALYSIS_WAIVED+=("$waived")
                    ANALYSIS_NON_WAIVED+=("$non_waived")
                    ANALYSIS_TOP_CHECKERS+=("$top_checkers")
                    ANALYSIS_RUN_DATES+=("$run_date")
                else
                    IFS='|' read -r overall_status details runtime flags <<< "$parse_result"
                    ANALYSIS_FLAGS+=("$flags")
                fi
                
                ANALYSIS_STATUS+=("$overall_status")
                ANALYSIS_DETAILS+=("$details")
                ANALYSIS_RUNTIMES+=("$runtime")
            else
                ANALYSIS_STATUS+=("ERROR")
                ANALYSIS_DETAILS+=("Result file not found")
                ANALYSIS_RUNTIMES+=("N/A")
                ANALYSIS_FLAGS+=("N/A")
                
                # Add N/A for timing fields (including scenario names and PT work areas count)
                if [ "$REGRESSION_TYPE" = "timing" ]; then
                    ANALYSIS_SETUP_WNS+=("N/A")
                    ANALYSIS_SETUP_TNS+=("N/A")
                    ANALYSIS_SETUP_NVP+=("N/A")
                    ANALYSIS_HOLD_WNS+=("N/A")
                    ANALYSIS_HOLD_TNS+=("N/A")
                    ANALYSIS_HOLD_NVP+=("N/A")
                    ANALYSIS_DSR_SKEW_SETUP+=("N/A")
                    ANALYSIS_DSR_SKEW_HOLD+=("N/A")
                    ANALYSIS_SETUP_SCENARIO+=("N/A")
                    ANALYSIS_HOLD_SCENARIO+=("N/A")
                    ANALYSIS_PT_WORK_AREAS+=("N/A")
                    ANALYSIS_RUN_DATES+=("N/A")
                elif [ "$REGRESSION_TYPE" = "formal" ]; then
                    ANALYSIS_FAILING_COMPARE_PTS+=("N/A:N/A:N/A:N/A")
                    ANALYSIS_RUN_DATES+=("N/A")
                elif [ "$REGRESSION_TYPE" = "pv" ]; then
                    ANALYSIS_RUN_DATES+=("N/A")
                elif [ "$REGRESSION_TYPE" = "clock" ]; then
                    ANALYSIS_CLOCK_LATENCY_FILES+=("N/A")
                elif [ "$REGRESSION_TYPE" = "glcheck" ]; then
                    ANALYSIS_TOTAL_ERRORS+=("N/A")
                    ANALYSIS_WAIVED+=("N/A")
                    ANALYSIS_NON_WAIVED+=("N/A")
                    ANALYSIS_TOP_CHECKERS+=("N/A")
                    ANALYSIS_RUN_DATES+=("N/A")
                fi
            fi
        done
    fi

    # Store results for this regression type
    # Use sequential counter to match ANALYSIS_STATUS array indices
    result_idx=0
    for i in "${!UNITS[@]}"; do
        REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_status"]="${ANALYSIS_STATUS[$result_idx]}"
        REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_details"]="${ANALYSIS_DETAILS[$result_idx]}"
        REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_runtime"]="${ANALYSIS_RUNTIMES[$result_idx]}"
        REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_flags"]="${ANALYSIS_FLAGS[$result_idx]}"
        
        # Store timing-specific fields if this is timing regression (including scenario names and PT work areas count)
        if [ "$REGRESSION_TYPE" = "timing" ]; then
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_setup_wns"]="${ANALYSIS_SETUP_WNS[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_setup_tns"]="${ANALYSIS_SETUP_TNS[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_setup_nvp"]="${ANALYSIS_SETUP_NVP[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_hold_wns"]="${ANALYSIS_HOLD_WNS[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_hold_tns"]="${ANALYSIS_HOLD_TNS[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_hold_nvp"]="${ANALYSIS_HOLD_NVP[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_dsr_skew_setup"]="${ANALYSIS_DSR_SKEW_SETUP[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_dsr_skew_hold"]="${ANALYSIS_DSR_SKEW_HOLD[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_setup_scenario"]="${ANALYSIS_SETUP_SCENARIO[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_hold_scenario"]="${ANALYSIS_HOLD_SCENARIO[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_pt_work_areas"]="${ANALYSIS_PT_WORK_AREAS[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_run_date"]="${ANALYSIS_RUN_DATES[$result_idx]}"
        fi
        
        # Store formal-specific fields if this is formal regression
        if [ "$REGRESSION_TYPE" = "formal" ]; then
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_failing_compare_pts"]="${ANALYSIS_FAILING_COMPARE_PTS[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_run_date"]="${ANALYSIS_RUN_DATES[$result_idx]}"
        fi
        
        # Store PV-specific fields if this is PV regression
        if [ "$REGRESSION_TYPE" = "pv" ]; then
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_run_date"]="${ANALYSIS_RUN_DATES[$result_idx]}"
        fi
        
        # Store clock-specific fields if this is clock regression
        if [ "$REGRESSION_TYPE" = "clock" ]; then
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_clock_latency_file"]="${ANALYSIS_CLOCK_LATENCY_FILES[$result_idx]}"
        fi
        
        # Store glcheck-specific fields if this is glcheck regression
        if [ "$REGRESSION_TYPE" = "glcheck" ]; then
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_total_errors"]="${ANALYSIS_TOTAL_ERRORS[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_waived"]="${ANALYSIS_WAIVED[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_non_waived"]="${ANALYSIS_NON_WAIVED[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_top_checkers"]="${ANALYSIS_TOP_CHECKERS[$result_idx]}"
            REGRESSION_RESULTS["${REGRESSION_TYPE}_${i}_run_date"]="${ANALYSIS_RUN_DATES[$result_idx]}"
        fi
        
        ((result_idx++))
    done
    
    # Calculate statistics for this regression type
    passed_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "^PASSED$")
    [[ "$passed_count" == "0" ]] && passed_count=0
    warn_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "^WARN$")
    [[ "$warn_count" == "0" ]] && warn_count=0
    partial_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "PARTIAL_PASS")
    [[ "$partial_count" == "0" ]] && partial_count=0
    unresolved_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "UNRESOLVED")
    [[ "$unresolved_count" == "0" ]] && unresolved_count=0
    failed_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "FAILED")
    [[ "$failed_count" == "0" ]] && failed_count=0
    crashed_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "CRASHED")
    [[ "$crashed_count" == "0" ]] && crashed_count=0
    error_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "ERROR")
    [[ "$error_count" == "0" ]] && error_count=0
    running_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "RUNNING")
    [[ "$running_count" == "0" ]] && running_count=0
    not_found_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "NOT_FOUND")
    [[ "$not_found_count" == "0" ]] && not_found_count=0
    no_data_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "NO_DATA")
    [[ "$no_data_count" == "0" ]] && no_data_count=0
    missing_count=$(printf '%s\n' "${ANALYSIS_STATUS[@]}" | grep -c "MISSING")
    [[ "$missing_count" == "0" ]] && missing_count=0
    
    # Store statistics for this regression type
    REGRESSION_RESULTS["${REGRESSION_TYPE}_passed_count"]=$passed_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_warn_count"]=$warn_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_partial_count"]=$partial_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_unresolved_count"]=$unresolved_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_failed_count"]=$failed_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_crashed_count"]=$crashed_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_error_count"]=$error_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_running_count"]=$running_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_not_found_count"]=$not_found_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_no_data_count"]=$no_data_count
    REGRESSION_RESULTS["${REGRESSION_TYPE}_missing_count"]=$missing_count
    
    # Clean up temporary arrays
    unset ANALYSIS_STATUS
    unset ANALYSIS_DETAILS
    unset ANALYSIS_RUNTIMES
    
    # Print completion message only if not in quiet mode
    if [ $QUIET -eq 0 ]; then
    echo ""
        echo -e "${GREEN}[OK] Completed $REGRESSION_NAME analysis${NC}"
    echo ""
    fi

done  # End of regression types loop

#===============================================================================
# Generate HTML Dashboard
#===============================================================================
# Uses unified tabbed HTML generation for both single and multi-regression
# - Single type: Tab bar is hidden via CSS, content shows immediately
# - Multiple types: Tab bar is visible, tabs switch between regression types

if [ $QUIET -eq 0 ]; then
print_section "Generating HTML Dashboard"
fi

# Note: Logo will be loaded AFTER HTML generation to avoid "Argument list too long" error
# (base64 logo is ~1MB which makes environment too large for subprocesses)

cat > "$HTML_FILE" << 'MULTI_HTML_START'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AGUR Multi-Regression Dashboard</title>
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        min-height: 100vh;
    }
    
    .container {
        max-width: 1400px;
        margin: 0 auto;
        background: white;
        border-radius: 15px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        overflow: hidden;
    }
    
    .header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 30px;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        flex-wrap: wrap;
    }
    
    .header-logo {
        height: 100px;
        width: auto;
        max-width: 200px;
        display: block;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    
    .header-logo:hover {
        transform: scale(1.05);
    }
    
    .header-text {
        flex: 1;
        min-width: 300px;
    }
    
    .header h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header .subtitle {
        font-size: 1.2em;
        opacity: 0.9;
    }
    
    /* Logo Modal */
    .logo-modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto;
        background-color: rgba(0,0,0,0.9);
    }
    
    .logo-modal-content {
        margin: auto;
        display: block;
        width: 80%;
        max-width: 700px;
        animation: zoom 0.6s;
    }
    
    .logo-modal-close {
        position: absolute;
        top: 15px;
        right: 35px;
        color: #f1f1f1;
        font-size: 40px;
        font-weight: bold;
        transition: 0.3s;
        cursor: pointer;
    }
    
    .logo-modal-close:hover,
    .logo-modal-close:focus {
        color: #bbb;
    }
    
    @keyframes zoom {
        from {transform: scale(0)}
        to {transform: scale(1)}
    }
    
    /* Tab Navigation */
    .tab-nav {
        display: flex;
        background: #f8f9fa;
        border-bottom: 3px solid #dee2e6;
        overflow-x: auto;
    }
    
    /* Hide tab navigation when only one regression type */
    .tab-nav.single-type {
        display: none;
    }
    
    .tab-button {
        flex: 1;
        min-width: 150px;
        padding: 18px 25px;
        background: #e9ecef;
        border: none;
        cursor: pointer;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s;
        border-bottom: 4px solid transparent;
        color: #495057;
    }
    
    .tab-button:hover {
        background: #dee2e6;
        transform: translateY(-2px);
    }
    
    .tab-button.active {
        background: white;
        border-bottom-color: #667eea;
        color: #667eea;
    }
    
    /* Tab Content */
    .tab-content {
        display: none;
    }
    
    .tab-content.active {
        display: block;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
        gap: 12px;
        padding: 20px;
        background: #f8f9fa;
    }
    
    .stat-card {
        background: white;
        padding: 15px 10px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease, border 0.3s ease;
        cursor: pointer;
        border: 3px solid transparent;
        position: relative;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        background: #f8f9fa;
    }
    
    .stat-card.active {
        border-color: #667eea;
        background: #f0f4ff;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stat-card.clickable::after {
        content: "Click to filter";
        position: absolute;
        bottom: 5px;
        left: 0;
        right: 0;
        font-size: 0.7em;
        color: #999;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .stat-card.clickable:hover::after {
        opacity: 1;
    }
    
    .stat-value {
        font-size: 2em;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.8em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-passed { color: #28a745; }
    .stat-failed { color: #dc3545; }
    .stat-unresolved { color: #ffc107; }
    .stat-crashed { color: #6c1a1a; }
    
    .content {
        padding: 30px;
    }
    
    .chiplet-section {
        margin-bottom: 40px;
    }
    
    .chiplet-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        font-size: 1.5em;
        margin-bottom: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chiplet-header:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .chiplet-header.highlighted-passed {
        background: linear-gradient(135deg, #27ae60 0%, #219a52 100%);
        box-shadow: 0 0 15px rgba(39, 174, 96, 0.5);
        animation: pulse-passed 2s ease-in-out infinite;
    }
    
    .chiplet-header.highlighted-failed {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        box-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
        animation: pulse-failed 2s ease-in-out infinite;
    }
    
    .chiplet-header.highlighted-crashed {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        box-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
        animation: pulse-failed 2s ease-in-out infinite;
    }
    
    .chiplet-header.highlighted-warn {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        box-shadow: 0 0 15px rgba(243, 156, 18, 0.5);
        animation: pulse-warn 2s ease-in-out infinite;
    }
    
    .chiplet-header.highlighted-unresolved {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        box-shadow: 0 0 15px rgba(243, 156, 18, 0.5);
        animation: pulse-warn 2s ease-in-out infinite;
    }
    
    .chiplet-header.highlighted-not_run {
        background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
        box-shadow: 0 0 15px rgba(149, 165, 166, 0.5);
        animation: pulse-gray 2s ease-in-out infinite;
    }
    
    .chiplet-header.highlighted-no_data {
        background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
        box-shadow: 0 0 15px rgba(149, 165, 166, 0.5);
        animation: pulse-gray 2s ease-in-out infinite;
    }
    
    .chiplet-header.highlighted-missing {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        box-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
        animation: pulse-failed 2s ease-in-out infinite;
    }
    
    @keyframes pulse-passed {
        0%, 100% { box-shadow: 0 0 15px rgba(39, 174, 96, 0.5); }
        50% { box-shadow: 0 0 25px rgba(39, 174, 96, 0.8); }
    }
    
    @keyframes pulse-failed {
        0%, 100% { box-shadow: 0 0 15px rgba(231, 76, 60, 0.5); }
        50% { box-shadow: 0 0 25px rgba(231, 76, 60, 0.8); }
    }
    
    @keyframes pulse-warn {
        0%, 100% { box-shadow: 0 0 15px rgba(243, 156, 18, 0.5); }
        50% { box-shadow: 0 0 25px rgba(243, 156, 18, 0.8); }
    }
    
    @keyframes pulse-gray {
        0%, 100% { box-shadow: 0 0 15px rgba(149, 165, 166, 0.5); }
        50% { box-shadow: 0 0 25px rgba(149, 165, 166, 0.8); }
    }
    
    .chiplet-header .toggle {
        font-size: 0.8em;
    }
    
    /* Action Buttons */
    .action-buttons {
        display: flex;
        justify-content: center;
        gap: 15px;
        padding: 15px 20px;
        background: #f8f9fa;
        border-bottom: 2px solid #dee2e6;
    }
    
    .action-btn {
        padding: 10px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    .action-btn:active {
        transform: translateY(0);
    }
    
    /* Back to Top Button */
    #backToTopBtn {
        display: block;
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 99;
        border: none;
        outline: none;
        background-color: #667eea;
        color: white;
        cursor: pointer;
        padding: 15px 20px;
        border-radius: 50px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        opacity: 0.3;
    }
    
    #backToTopBtn.visible {
        opacity: 1;
    }
    
    #backToTopBtn:hover {
        background-color: #5568d3;
        transform: scale(1.1);
        opacity: 1;
    }
    
    .collapsible-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.5s ease;
    }
    
    .collapsible-content.active {
        max-height: 50000px;
    }
    
    .units-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 20px;
        padding: 10px;
    }
    
    .unit-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        transition: all 0.3s ease;
    }
    
    .unit-card:hover {
        border-color: #667eea;
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.2);
        transform: translateY(-3px);
    }
    
    .unit-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .unit-name {
        font-size: 1.4em;
        font-weight: bold;
        color: #333;
    }
    
    .status-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .status-passed {
        background: #d4edda;
        color: #155724;
    }
    
    .status-partial {
        background: #fff3cd;
        color: #856404;
    }
    
    .status-unresolved {
        background: #fff3cd;
        color: #856404;
    }
    
    .status-failed {
        background: #f8d7da;
        color: #721c24;
    }
    
    .status-crashed {
        background: #f8d7da;
        color: #721c24;
    }
    
    .status-running {
        background: #d1ecf1;
        color: #0c5460;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
    }
    
    .status-notfound {
        background: #e2e3e5;
        color: #383d41;
    }
    
    .unit-info {
        margin: 10px 0;
    }
    
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        font-size: 0.9em;
    }
    
    .workarea-row {
        align-items: center;
        gap: 10px;
    }
    
    .workarea-path {
        flex: 1;
        font-family: monospace;
        font-size: 0.85em;
        color: #555;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .copy-btn {
        background: #667eea;
        color: white;
        border: none;
        padding: 5px 12px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.85em;
        transition: all 0.3s;
    }
    
    .copy-btn:hover {
        background: #5568d3;
        transform: scale(1.05);
    }
    
    .copy-btn:active {
        transform: scale(0.95);
    }
    
    .info-label {
        font-weight: 600;
        color: #666;
    }
    
    .info-value {
        color: #333;
    }
    
    /* Formal Flows / PV Metrics */
    .formal-flows {
        margin-top: 15px;
        padding-top: 15px;
        border-top: 2px solid #f0f0f0;
    }
    
    .flow-title {
        font-weight: bold;
        margin-bottom: 10px;
        color: #667eea;
    }
    
    .flow-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        margin: 5px 0;
        background: #f8f9fa;
        border-radius: 5px;
        font-size: 0.9em;
    }
    
    .flow-succeeded {
        background: #d4edda;
        color: #155724;
    }
    
    .flow-failed {
        background: #f8d7da;
        color: #721c24;
    }
    
    .flow-unresolved {
        background: #fff3cd;
        color: #856404;
    }
    
    .flow-crashed {
        background: #f8d7da;
        color: #721c24;
    }
    
    .flow-running {
        background: #d1ecf1;
        color: #0c5460;
    }
    
    .footer {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        text-align: center;
        padding: 20px;
        margin-top: 40px;
    }
    
    .footer p {
        margin: 5px 0;
    }
    
    .footer strong {
        color: #00ff00;
    }
    
    /* Toast Notification */
    .toast {
        visibility: hidden;
        min-width: 250px;
        background-color: #28a745;
        color: white;
        text-align: center;
        border-radius: 10px;
        padding: 16px;
        position: fixed;
        z-index: 1;
        right: 30px;
        bottom: 30px;
        font-size: 17px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .toast.show {
        visibility: visible;
        animation: fadein 0.5s, fadeout 0.5s 2.5s;
    }
    
    @keyframes fadein {
        from {bottom: 0; opacity: 0;}
        to {bottom: 30px; opacity: 1;}
    }
    
    @keyframes fadeout {
        from {bottom: 30px; opacity: 1;}
        to {bottom: 0; opacity: 0;}
    }
    
    /* Search and Filter Section */
    .filter-section {
        background: #f8f9fa;
        padding: 20px 30px;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .filter-container {
        display: grid;
        grid-template-columns: 1fr auto auto;
        gap: 20px;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .search-box {
        position: relative;
    }
    
    .search-box input {
        width: 100%;
        padding: 12px 20px;
        font-size: 16px;
        border: 2px solid #ddd;
        border-radius: 25px;
        outline: none;
        transition: all 0.3s ease;
    }
    
    .search-box input:focus {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
    }
    
    .export-buttons {
        display: flex;
        gap: 10px;
    }
    
    .export-btn {
        padding: 10px 20px;
        border: 2px solid #28a745;
        background: white;
        color: #28a745;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        white-space: nowrap;
    }
    
    .export-btn:hover {
        background: #28a745;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
    }
    
    .unit-card.hidden {
        display: none;
    }
</style>
</head>
<body>
<div class="container">
MULTI_HTML_START

# Add header with logo
cat >> "$HTML_FILE" << HEADER_START
    <!-- Logo Modal -->
    <div id="logoModal" class="logo-modal" onclick="closeLogoModal()">
        <span class="logo-modal-close">&times;</span>
        <img class="logo-modal-content" src="file:///home/scratch.avice_vlsi/cursor/avice_wa_review/images/avice_logo.png" alt="AVICE Logo">
    </div>
    
    <div class="header">
        <img class="header-logo" src="file:///home/scratch.avice_vlsi/cursor/avice_wa_review/images/avice_logo.png" alt="AVICE Logo" onclick="showLogoModal()" title="Click to enlarge">
        <div class="header-text">
            <h1>🔬 AGUR Multi-Regression Dashboard</h1>
        <div class="subtitle">Generated: $(date '+%Y-%m-%d %H:%M:%S')</div>
        <div class="subtitle">Regression Types: ${REGRESSION_TYPES[*]}</div>
HEADER_START

if [ ${#FILTER_CHIPLETS[@]} -gt 0 ]; then
    echo "            <div class=\"subtitle\">Filter: Chiplet = ${FILTER_CHIPLETS[*]}</div>" >> "$HTML_FILE"
fi

cat >> "$HTML_FILE" << HEADER_END
        </div>
    </div>
HEADER_END

# Add tab navigation (with conditional single-type class)
TAB_NAV_CLASS=""
if [ ${#REGRESSION_TYPES[@]} -eq 1 ]; then
    TAB_NAV_CLASS=" single-type"
fi

cat >> "$HTML_FILE" << MULTI_TABS_START
    
    <div class="tab-nav$TAB_NAV_CLASS">
MULTI_TABS_START

# Generate tab buttons
for idx in "${!REGRESSION_TYPES[@]}"; do
    regression_type="${REGRESSION_TYPES[$idx]}"
    active_class=""
    [ $idx -eq 0 ] && active_class=" active"
    
    # Get regression name for tab
    case "$regression_type" in
        formal) tab_name="🔍 Formal" ;;
        timing) tab_name="⏱️ Timing (PT)" ;;
        pv) tab_name="✓ PV" ;;
        clock) tab_name="🕒 Clock" ;;
        release) tab_name="📦 Release" ;;
        glcheck) tab_name="🔧 GL Check" ;;
        *) tab_name="$regression_type" ;;
    esac
    
    echo "            <button class=\"tab-button$active_class\" onclick=\"openTab('$regression_type')\">$tab_name</button>" >> "$HTML_FILE"
done

cat >> "$HTML_FILE" << 'MULTI_FILTER_SECTION'
    </div>
    
    <!-- Search and Filter Section -->
    <div class="filter-section">
        <div class="filter-container">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="🔍 Search units by name..." onkeyup="filterUnits()">
            </div>
            <div class="action-buttons">
                <button class="action-btn" onclick="expandAll()">Expand All Chiplets</button>
                <button class="action-btn" onclick="collapseAll()">Collapse All Chiplets</button>
            </div>
            <div class="export-buttons">
                <button class="export-btn" onclick="exportToCSV()" title="Export results to CSV">📄 Export CSV</button>
                <button class="export-btn" onclick="printDashboard()" title="Print dashboard">🖨️ Print</button>
            </div>
        </div>
    </div>
MULTI_FILTER_SECTION

# Generate tab content for each regression type
for idx in "${!REGRESSION_TYPES[@]}"; do
    REGRESSION_TYPE="${REGRESSION_TYPES[$idx]}"
    active_class=""
    [ $idx -eq 0 ] && active_class=" active"
    
    # Get statistics for this regression
    passed_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_passed_count"]}
    warn_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_warn_count"]}
    partial_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_partial_count"]}
    unresolved_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_unresolved_count"]}
    failed_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_failed_count"]}
    crashed_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_crashed_count"]}
    error_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_error_count"]}
    running_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_running_count"]}
    not_found_count=${REGRESSION_RESULTS["${REGRESSION_TYPE}_not_found_count"]}
    
    cat >> "$HTML_FILE" << TAB_CONTENT_START
    <div id="$REGRESSION_TYPE" class="tab-content$active_class">
        <div class="stats-grid">
            <div class="stat-card" onclick="filterStatus(event, 'all')" data-filter="all" title="Click to show all units">
                <div class="stat-label">Total Units</div>
                <div class="stat-value">$TOTAL_UNITS</div>
            </div>
            <div class="stat-card clickable" onclick="filterStatus(event, 'passed')" data-filter="passed" title="Click to show only passed units">
                <div class="stat-label">✅ Passed</div>
                <div class="stat-value stat-passed">$passed_count</div>
                <div class="stat-label">$(( passed_count * 100 / TOTAL_UNITS ))%</div>
            </div>
            <div class="stat-card clickable" onclick="filterStatus(event, 'warn')" data-filter="warn" title="Click to show only units with warnings">
                <div class="stat-label">⚠️ Warnings</div>
                <div class="stat-value stat-unresolved">$warn_count</div>
                <div class="stat-label">$(( warn_count * 100 / TOTAL_UNITS ))%</div>
            </div>
TAB_CONTENT_START
    
    # Unresolved is only relevant for formal regression
    if [ "$REGRESSION_TYPE" = "formal" ]; then
        cat >> "$HTML_FILE" << TAB_UNRESOLVED
            <div class="stat-card clickable" onclick="filterStatus(event, 'unresolved')" data-filter="unresolved" title="Click to show only unresolved units">
                <div class="stat-label">⚠️ Unresolved</div>
                <div class="stat-value stat-unresolved">$unresolved_count</div>
                <div class="stat-label">$(( unresolved_count * 100 / TOTAL_UNITS ))%</div>
            </div>
TAB_UNRESOLVED
    fi
    
    cat >> "$HTML_FILE" << TAB_STATS_REST
            <div class="stat-card clickable" onclick="filterStatus(event, 'failed')" data-filter="failed" title="Click to show only failed units">
                <div class="stat-label">❌ Failed</div>
                <div class="stat-value stat-failed">$failed_count</div>
                <div class="stat-label">$(( failed_count * 100 / TOTAL_UNITS ))%</div>
            </div>
            <div class="stat-card clickable" onclick="filterStatus(event, 'crashed')" data-filter="crashed" title="Click to show only crashed units">
                <div class="stat-label">💥 Crashed</div>
                <div class="stat-value stat-crashed">$crashed_count</div>
                <div class="stat-label">$(( crashed_count * 100 / TOTAL_UNITS ))%</div>
            </div>
            <div class="stat-card clickable" onclick="filterStatus(event, 'not_run')" data-filter="not_run" title="Click to show only units not run">
                <div class="stat-label">⏸️ Not Run</div>
                <div class="stat-value stat-unresolved">$not_found_count</div>
                <div class="stat-label">$(( not_found_count * 100 / TOTAL_UNITS ))%</div>
            </div>
            <div class="stat-card clickable" onclick="filterStatus(event, 'no_data')" data-filter="no_data" title="Click to show only units with no data">
                <div class="stat-label">📊 No Data</div>
                <div class="stat-value stat-unresolved">$no_data_count</div>
                <div class="stat-label">$(( no_data_count * 100 / TOTAL_UNITS ))%</div>
            </div>
            <div class="stat-card clickable" onclick="filterStatus(event, 'missing')" data-filter="missing" title="Click to show only missing units">
                <div class="stat-label">🚫 Missing</div>
                <div class="stat-value stat-failed">$missing_count</div>
                <div class="stat-label">$(( missing_count * 100 / TOTAL_UNITS ))%</div>
            </div>
        </div>
        
        <div class="content">
TAB_STATS_REST

    # Group units by chiplet
    declare -A chiplet_units_tab
    for i in "${!UNITS[@]}"; do
        unit="${UNITS[$i]}"
        chiplet="${CHIPLETS[$i]}"
        
        log_debug "Grouping unit $unit (index $i) into chiplet [$chiplet]"
        
        if [ -z "${chiplet_units_tab[$chiplet]}" ]; then
            chiplet_units_tab[$chiplet]="$i"
        else
            chiplet_units_tab[$chiplet]="${chiplet_units_tab[$chiplet]},$i"
        fi
    done
    
    # Debug: Show chiplet grouping
    if [ $VERBOSE -eq 1 ]; then
        for chiplet_key in "${!chiplet_units_tab[@]}"; do
            log_debug "Chiplet [$chiplet_key] has indices: ${chiplet_units_tab[$chiplet_key]}"
        done
    fi
    
    # Generate HTML for each chiplet in this tab
    for chiplet in "${!chiplet_units_tab[@]}"; do
        unit_indices="${chiplet_units_tab[$chiplet]}"
        
        # Count units in this chiplet
        IFS=',' read -ra indices <<< "$unit_indices"
        chiplet_unit_count=${#indices[@]}
        
        cat >> "$HTML_FILE" << CHIPLET_SECTION
            <div class="chiplet-section">
                <div class="chiplet-header" onclick="toggleChiplet('${REGRESSION_TYPE}_$chiplet')">
                    <span>$chiplet Chiplet ($chiplet_unit_count units)</span>
                    <span class="toggle" id="toggle-${REGRESSION_TYPE}_$chiplet">▶</span>
                </div>
                <div class="collapsible-content" id="content-${REGRESSION_TYPE}_$chiplet">
                    <div class="units-grid">
CHIPLET_SECTION
        
        # Add units for this chiplet
        for idx in "${indices[@]}"; do
            unit="${UNITS[$idx]}"
            unit_chiplet="${CHIPLETS[$idx]}"
            workarea="${WORKAREAS[$idx]}"
            rtl_tag="${RTL_TAGS[$idx]}"
            release_date="${RELEASE_DATES[$idx]}"
            release_user="${RELEASE_USERS[$idx]}"
            release_name="${RELEASE_NAMES[$idx]:-last_sta_rel}"
            
            # Validation: Skip if unit doesn't belong to this chiplet (sanity check)
            if [ "$unit_chiplet" != "$chiplet" ]; then
                log_debug "WARNING: Unit $unit has chiplet $unit_chiplet but is in section $chiplet (skipping)"
                continue
            fi
            
            # Get results for this unit in this regression type
            status="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_status]}"
            details="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_details]}"
            runtime="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_runtime]}"
            release_flags="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_flags]}"
            
            # Determine status class and text
            # For GL Check: Add non-waived count to status badge for visibility
            status_suffix=""
            if [ "$REGRESSION_TYPE" = "glcheck" ]; then
                nw="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_non_waived]}"
                if [ "$nw" != "N/A" ] && [ -n "$nw" ] && [[ "$nw" =~ ^[0-9]+$ ]] && [ "$nw" -gt 0 ]; then
                    status_suffix=" ($nw NW)"
                fi
            fi
            
            case "$status" in
                PASSED)
                    status_class="status-passed"
                    status_text="✅ PASSED${status_suffix}"
                    ;;
                WARN)
                    status_class="status-unresolved"
                    status_text="⚠️ WARN${status_suffix}"
                    ;;
                PARTIAL_PASS)
                    status_class="status-partial"
                    status_text="⚠️ PARTIAL${status_suffix}"
                    ;;
                UNRESOLVED)
                    status_class="status-unresolved"
                    status_text="⚠️ UNRESOLVED${status_suffix}"
                    ;;
                FAILED)
                    status_class="status-failed"
                    status_text="❌ FAILED${status_suffix}"
                    ;;
                CRASHED)
                    status_class="status-crashed"
                    status_text="💥 CRASHED${status_suffix}"
                    ;;
                RUNNING)
                    status_class="status-running"
                    status_text="🔄 RUNNING${status_suffix}"
                    ;;
                ERROR)
                    status_class="status-error"
                    status_text="⚠️ ERROR${status_suffix}"
                    ;;
                NOT_FOUND)
                    status_class="status-notfound"
                    status_text="⏸️ NOT RUN${status_suffix}"
                    ;;
                NO_DATA)
                    status_class="status-notfound"
                    status_text="📊 NO DATA${status_suffix}"
                    ;;
                MISSING)
                    status_class="status-failed"
                    status_text="🚫 MISSING${status_suffix}"
                    ;;
                *)
                    status_class="status-notfound"
                    status_text="❔ UNKNOWN${status_suffix}"
                    ;;
            esac
            
            # Generate release type badges for release regression type
            release_badges_html=""
            if [ "$REGRESSION_TYPE" = "release" ] && [ -n "$release_flags" ] && [ "$release_flags" != "N/A" ]; then
                # Parse the flags and create badges
                badges=""
                
                # Check for each release type and add badge
                if [[ "$release_flags" =~ sta_release ]]; then
                    badges="${badges}<span class='release-badge' style='background: #3498db; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin: 0 2px;' title='Timing Release'>S</span>"
                fi
                if [[ "$release_flags" =~ fcl_release ]]; then
                    badges="${badges}<span class='release-badge' style='background: #9b59b6; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin: 0 2px;' title='FCL Release'>L</span>"
                fi
                if [[ "$release_flags" =~ pnr_release ]]; then
                    badges="${badges}<span class='release-badge' style='background: #e67e22; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin: 0 2px;' title='PnR Release'>P</span>"
                fi
                if [[ "$release_flags" =~ fe_dct_release ]]; then
                    badges="${badges}<span class='release-badge' style='background: #27ae60; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin: 0 2px;' title='FE DCT Release'>FE</span>"
                fi
                
                if [ -n "$badges" ]; then
                    release_badges_html="<div style='display: flex; align-items: center; gap: 4px;'>$badges</div>"
                fi
            fi
            
            cat >> "$HTML_FILE" << UNIT_CARD
                        <div class="unit-card">
                            <div class="unit-header">
                                <div class="unit-name">$unit <span style="color: #888; font-size: 0.85em; font-weight: normal;">($release_user)</span></div>
                                $release_badges_html
                                <div class="status-badge $status_class">$status_text</div>
                            </div>
                            <div class="unit-info">
UNIT_CARD
            
            # For GL Check, Formal, PT, and PV: show combined Run Date + Runtime
            # For other types: show Release Date with age color coding
            if [ "$REGRESSION_TYPE" = "glcheck" ] || [ "$REGRESSION_TYPE" = "formal" ] || [ "$REGRESSION_TYPE" = "timing" ] || [ "$REGRESSION_TYPE" = "pv" ]; then
                # Get run date from REGRESSION_RESULTS associative array (using correct unit index)
                run_date="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_run_date]}"
                [ -z "$run_date" ] && run_date="N/A"
                
                # Combine Run Date and Runtime into single line for ALL types (formal, glcheck, timing, pv)
                # For formal: show total runtime (individual flow runtimes shown below)
                # For others: show total runtime
                cat >> "$HTML_FILE" << RUN_INFO
                                <div class="info-row">
                                    <span class="info-label">Run:</span>
                                    <span class="info-value" style="color: #3498db; font-weight: 500;">$run_date <span style="color: #7f8c8d; font-weight: normal;">($runtime)</span></span>
                                </div>
RUN_INFO
            else
                # Calculate release date age and add color coding for release/clock types
                # Color scheme: <1 week=green, 1-2 weeks=orange, >2 weeks=red
                release_date_color="#95a5a6"  # Default gray
                if [ -n "$release_date" ] && [[ "$release_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
                    # Calculate age in days
                    current_date=$(date +%s)
                    release_date_epoch=$(date -d "$release_date" +%s 2>/dev/null || echo "0")
                    
                    if [ "$release_date_epoch" != "0" ]; then
                        age_days=$(( (current_date - release_date_epoch) / 86400 ))
                        
                        if [ $age_days -le 7 ]; then
                            release_date_color="#27ae60"  # Green - fresh (≤1 week)
                        elif [ $age_days -le 14 ]; then
                            release_date_color="#f39c12"  # Orange - attention (1-2 weeks)
                        else
                            release_date_color="#e74c3c"  # Red - old (>2 weeks)
                        fi
                    fi
                fi
                
                cat >> "$HTML_FILE" << RELEASE_DATE_COLORED
                                <div class="info-row">
                                    <span class="info-label">Release Date:</span>
                                    <span class="info-value" style="color: $release_date_color; font-weight: 500;">$release_date</span>
                                </div>
RELEASE_DATE_COLORED
            fi
            
            # If custom release was specified, show which release was actually used (for ALL regression types)
            if [ -n "$CUSTOM_RELEASE" ]; then
                release_badge_color="#27ae60"  # Green for custom release
                release_badge_text="$release_name"
                if [ "$release_name" = "last_sta_rel" ]; then
                    release_badge_color="#f39c12"  # Orange/yellow for fallback
                    release_badge_text="last_sta_rel (fallback)"
                fi
                
                cat >> "$HTML_FILE" << RELEASE_NAME_INFO
                                <div class="info-row">
                                    <span class="info-label">Release Used:</span>
                                    <span class="info-value" style="color: $release_badge_color; font-weight: 500;">$release_badge_text</span>
                                </div>
RELEASE_NAME_INFO
            fi
            
            # RTL Tag is only relevant for formal and release regressions
            if [ "$REGRESSION_TYPE" = "formal" ] || [ "$REGRESSION_TYPE" = "release" ]; then
                cat >> "$HTML_FILE" << RTL_TAG
                                <div class="info-row workarea-row">
                                    <span class="info-label">RTL Tag:</span>
                                    <span class="info-value workarea-path" id="rtl-${REGRESSION_TYPE}-$unit">$rtl_tag</span>
                                    <button class="copy-btn" onclick="copyToClipboard('rtl-${REGRESSION_TYPE}-$unit', this)" title="Copy RTL tag">
                                        📋 Copy
                                    </button>
                                </div>
RTL_TAG
            fi
            
            # Runtime is now combined with Run Date for glcheck/timing/pv
            # Skip separate runtime display for: formal (shows per flow), clock (not relevant), release (detailed history), glcheck/timing/pv (combined above)
            # This section is no longer needed since runtime is shown combined with run date for analysis types
            
            cat >> "$HTML_FILE" << WORKAREA_SECTION
                                <div class="info-row workarea-row">
                                    <span class="info-label">Workarea:</span>
                                    <span class="info-value workarea-path" id="wa-${REGRESSION_TYPE}-$unit">$workarea</span>
                                    <button class="copy-btn" onclick="copyToClipboard('wa-${REGRESSION_TYPE}-$unit', this)" title="Copy workarea path">
                                        📋 Copy
                                    </button>
                                </div>
                            </div>
WORKAREA_SECTION
            
            # Display details based on regression type
            if [ "$REGRESSION_TYPE" = "timing" ]; then
                # For Timing (PT): Display Setup/Hold scenario breakdown
                
                # Get timing-specific data from REGRESSION_RESULTS (including scenario names and PT work areas count)
                setup_wns="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_setup_wns]}"
                setup_tns="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_setup_tns]}"
                setup_nvp="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_setup_nvp]}"
                hold_wns="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_hold_wns]}"
                hold_tns="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_hold_tns]}"
                hold_nvp="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_hold_nvp]}"
                dsr_skew_setup="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_dsr_skew_setup]}"
                dsr_skew_hold="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_dsr_skew_hold]}"
                setup_scenario="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_setup_scenario]}"
                hold_scenario="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_hold_scenario]}"
                pt_work_areas="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_pt_work_areas]}"
                
                # Show timing breakdown if data is available
                if [ "$setup_wns" != "N/A" ] || [ "$hold_wns" != "N/A" ]; then
                    # Create unique ID for this unit's timing breakdown
                    timing_id="timing-breakdown-${REGRESSION_TYPE}-${idx}"
                    
                    # Format PT work areas count for display
                    pt_runs_text=""
                    if [ "$pt_work_areas" != "N/A" ] && [ -n "$pt_work_areas" ]; then
                        if [ "$pt_work_areas" = "1" ]; then
                            pt_runs_text=" (1 run)"
                        else
                            pt_runs_text=" ($pt_work_areas runs)"
                        fi
                    fi
                    
                    cat >> "$HTML_FILE" << TIMING_START
                            <div class="formal-flows">
                                <div class="flow-title" style="color: #667eea; font-weight: bold; margin-bottom: 12px; cursor: pointer; user-select: none; display: flex; align-items: center; gap: 8px;" onclick="toggleTimingBreakdown('${timing_id}')">
                                    <span id="${timing_id}-arrow" style="transition: transform 0.3s ease; display: inline-block;">▶</span>
                                    <span>⏱️ TIMING BREAKDOWN (PT):${pt_runs_text}</span>
                                </div>
                                <div id="${timing_id}" style="display: none; margin-top: 8px;">
TIMING_START
                    
                    # Display Setup Scenario if available
                    if [ "$setup_wns" != "N/A" ]; then
                        # Color coding for Setup WNS
                        setup_wns_color="#27ae60"  # Green (passing)
                        if (( $(echo "$setup_wns < 0" | bc -l 2>/dev/null || echo 0) )); then
                            # Check if critical violation (< -0.05ns)
                            if (( $(echo "$setup_wns < -0.05" | bc -l 2>/dev/null || echo 0) )); then
                                setup_wns_color="#e74c3c"  # Red (critical)
                            else
                                setup_wns_color="#f39c12"  # Yellow (minor)
                            fi
                        fi
                        
                        # Color coding for Setup TNS
                        setup_tns_color="#27ae60"  # Green (passing)
                        if (( $(echo "$setup_tns < 0" | bc -l 2>/dev/null || echo 0) )); then
                            # Check if critical violation (< -10ns)
                            if (( $(echo "$setup_tns < -10" | bc -l 2>/dev/null || echo 0) )); then
                                setup_tns_color="#e74c3c"  # Red (critical)
                            else
                                setup_tns_color="#f39c12"  # Yellow (minor)
                            fi
                        fi
                        
                        # Color coding for DSR Skew (Setup)
                        dsr_skew_setup_color="#27ae60"  # Green (≤10ps)
                        if [ "$dsr_skew_setup" != "N/A" ]; then
                            if (( $(echo "$dsr_skew_setup > 10" | bc -l 2>/dev/null || echo 0) )); then
                                dsr_skew_setup_color="#e74c3c"  # Red (>10ps)
                            fi
                        fi
                        
                    cat >> "$HTML_FILE" << SETUP_SECTION
                            <div style="margin-bottom: 15px; padding: 12px; background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 5px;">
                                <div style="font-weight: 600; color: #667eea; margin-bottom: 8px; font-size: 0.95em;">
                                    📊 Setup Scenario: 
                                    <span style="font-size: 0.85em; cursor: help; color: #888;" title="$setup_scenario">ℹ️</span>
                                </div>
                                <div style="display: grid; grid-template-columns: auto 1fr; gap: 6px 12px; font-size: 0.9em;">
                                    <span style="color: #666;">• WNS:</span>
                                    <span style="color: $setup_wns_color; font-weight: 500;">$setup_wns ns</span>
                                    
                                    <span style="color: #666;">• TNS:</span>
                                    <span style="color: $setup_tns_color; font-weight: 500;">$setup_tns ns</span>
                                    
                                    <span style="color: #666;">• NVP:</span>
                                    <span style="color: #555; font-weight: 500;">$setup_nvp paths</span>
SETUP_SECTION
                        
                        # Add DSR Skew only if available
                        if [ "$dsr_skew_setup" != "N/A" ]; then
                            cat >> "$HTML_FILE" << SETUP_DSR
                                        
                                        <span style="color: #666;">• DSR Skew:</span>
                                        <span style="color: $dsr_skew_setup_color; font-weight: 500;">$dsr_skew_setup ps</span>
SETUP_DSR
                        fi
                        
                        cat >> "$HTML_FILE" << SETUP_END
                                    </div>
                                </div>
SETUP_END
                    fi
                    
                    # Display Hold Scenario if available
                    if [ "$hold_wns" != "N/A" ]; then
                        # Color coding for Hold WNS
                        hold_wns_color="#27ae60"  # Green (passing)
                        if (( $(echo "$hold_wns < 0" | bc -l 2>/dev/null || echo 0) )); then
                            # Check if critical violation (< -0.05ns)
                            if (( $(echo "$hold_wns < -0.05" | bc -l 2>/dev/null || echo 0) )); then
                                hold_wns_color="#e74c3c"  # Red (critical)
                            else
                                hold_wns_color="#f39c12"  # Yellow (minor)
                            fi
                        fi
                        
                        # Color coding for Hold TNS
                        hold_tns_color="#27ae60"  # Green (passing)
                        if (( $(echo "$hold_tns < 0" | bc -l 2>/dev/null || echo 0) )); then
                            # Check if critical violation (< -10ns)
                            if (( $(echo "$hold_tns < -10" | bc -l 2>/dev/null || echo 0) )); then
                                hold_tns_color="#e74c3c"  # Red (critical)
                            else
                                hold_tns_color="#f39c12"  # Yellow (minor)
                            fi
                        fi
                        
                        # Color coding for DSR Skew (Hold)
                        dsr_skew_hold_color="#27ae60"  # Green (≤10ps)
                        if [ "$dsr_skew_hold" != "N/A" ]; then
                            if (( $(echo "$dsr_skew_hold > 10" | bc -l 2>/dev/null || echo 0) )); then
                                dsr_skew_hold_color="#e74c3c"  # Red (>10ps)
                            fi
                        fi
                        
                    cat >> "$HTML_FILE" << HOLD_SECTION
                            <div style="margin-bottom: 10px; padding: 12px; background: #f8f9fa; border-left: 4px solid #9b59b6; border-radius: 5px;">
                                <div style="font-weight: 600; color: #9b59b6; margin-bottom: 8px; font-size: 0.95em;">
                                    📊 Hold Scenario: 
                                    <span style="font-size: 0.85em; cursor: help; color: #888;" title="$hold_scenario">ℹ️</span>
                                </div>
                                <div style="display: grid; grid-template-columns: auto 1fr; gap: 6px 12px; font-size: 0.9em;">
                                    <span style="color: #666;">• WNS:</span>
                                    <span style="color: $hold_wns_color; font-weight: 500;">$hold_wns ns</span>
                                    
                                    <span style="color: #666;">• TNS:</span>
                                    <span style="color: $hold_tns_color; font-weight: 500;">$hold_tns ns</span>
                                    
                                    <span style="color: #666;">• NVP:</span>
                                    <span style="color: #555; font-weight: 500;">$hold_nvp paths</span>
HOLD_SECTION
                        
                        # Add DSR Skew only if available
                        if [ "$dsr_skew_hold" != "N/A" ]; then
                            cat >> "$HTML_FILE" << HOLD_DSR
                                        
                                        <span style="color: #666;">• DSR Skew:</span>
                                        <span style="color: $dsr_skew_hold_color; font-weight: 500;">$dsr_skew_hold ps</span>
HOLD_DSR
                        fi
                        
                        cat >> "$HTML_FILE" << HOLD_END
                                    </div>
                                </div>
HOLD_END
                    fi
                    
                    # Note: PT Runtime display removed as requested by user
                    # Runtime data is still extracted and stored, but not displayed in unit cards
                    
                    # Close the expandable content div and the formal-flows div
                    echo "                                </div>" >> "$HTML_FILE"  # Close expandable content
                    echo "                            </div>" >> "$HTML_FILE"  # Close formal-flows
                fi
            elif [ "$REGRESSION_TYPE" = "pv" ]; then
                # For PV: Display metrics
                if [ "$details" != "No PV data available" ] && [ "$details" != "No PV analysis found" ]; then
                    overall_pv_status=$(echo "$details" | grep -oP '\((MINOR|CRITICAL|ALL CLEAN)\)' | tr -d '()')
                    
                    cat >> "$HTML_FILE" << PV_START
                            <div class="formal-flows">
                                <div class="flow-title">PV Metrics:</div>
PV_START
                    
                    # Parse PV metrics
                    IFS=',' read -ra metrics <<< "$details"
                    for metric_info in "${metrics[@]}"; do
                        metric_info=$(echo "$metric_info" | xargs)
                        metric_info=$(echo "$metric_info" | sed 's/ (MINOR)//' | sed 's/ (CRITICAL)//' | sed 's/ (ALL CLEAN)//')
                        metric_name=$(echo "$metric_info" | cut -d':' -f1 | xargs)
                        metric_value=$(echo "$metric_info" | cut -d':' -f2 | xargs)
                        
                        cat >> "$HTML_FILE" << PV_METRIC
                                <div class="flow-item">
                                    <span>$metric_name</span>
                                    <span>❔ $metric_value</span>
                                </div>
PV_METRIC
                    done
                    
                    # Add overall status
                    if [ -n "$overall_pv_status" ]; then
                        pv_status_icon="❔"
                        pv_status_class=""
                        case "$overall_pv_status" in
                            "ALL CLEAN")
                                pv_status_icon="✅"
                                pv_status_class="flow-succeeded"
                                ;;
                            "MINOR")
                                pv_status_icon="⚠️"
                                pv_status_class="flow-unresolved"
                                ;;
                            "CRITICAL")
                                pv_status_icon="❌"
                                pv_status_class="flow-failed"
                                ;;
                        esac
                        
                        cat >> "$HTML_FILE" << PV_STATUS
                                <div class="flow-item $pv_status_class" style="border-top: 1px solid #ddd; margin-top: 5px; padding-top: 5px;">
                                    <span><strong>Overall</strong></span>
                                    <span>$pv_status_icon $overall_pv_status</span>
                                </div>
PV_STATUS
                    fi
                    
                    echo "                                </div>" >> "$HTML_FILE"
                fi
            elif [ "$REGRESSION_TYPE" = "release" ]; then
                # For Release: Display release statistics and links
                if [ "$details" != "No release attempts detected" ] && [ "$details" != "No block release found" ]; then
                    cat >> "$HTML_FILE" << RELEASE_START
                            <div class="formal-flows">
                                <div class="flow-title">Release Summary:</div>
RELEASE_START
                    
                    # Parse release details (format: "N successful / M total attempts; Links: xxx; Latest: yyyy")
                    # Split by semicolon
                    IFS=';' read -ra release_parts <<< "$details"
                    
                    for part in "${release_parts[@]}"; do
                        part=$(echo "$part" | xargs)  # Trim whitespace
                        
                        # Determine what type of information this is
                        if [[ "$part" =~ ^[0-9]+ ]]; then
                            # This is the attempt summary (e.g., "3 successful / 5 total attempts")
                            # Make it expandable to show all attempts with details
                            metric_value="$part"
                            
                            # Parse all attempts from output file
                            # Format: "Attempt #N: YYYY-MM-DD HH MM SS | User: username"
                            #         "Status: SUCCESS/FAILED"
                            #         "Flags: flag1, flag2, ..."
                            
                            attempts_data=$(awk '/Block Release Attempts:/,/Release Attempts from Workarea/ {print}' "$TEMP_DIR/${unit}_${REGRESSION_TYPE}_output.txt" | grep -E "Attempt #|Status:|Flags:" | sed 's/\x1b\[[0-9;]*m//g')
                            
                            if [ -n "$attempts_data" ]; then
                                # Count total attempts for expandable ID
                                total_count=$(echo "$attempts_data" | grep -c "Attempt #")
                                expand_id="release_attempts_${unit}_$$"
                                
                                # Display summary with expandable button
                                cat >> "$HTML_FILE" << ATTEMPTS_SUMMARY
                                <div class="flow-item">
                                    <span><strong>📊 Attempts</strong></span>
                                    <span>$metric_value</span>
                                </div>
                                <div style="margin-left: 20px; margin-top: 6px;">
                                    <button onclick="toggleCustomLinks('${expand_id}')" 
                                            id="${expand_id}_btn"
                                            style="background: none; border: none; color: #3498db; cursor: pointer; 
                                                   font-size: 0.9em; padding: 4px 8px; text-decoration: underline;
                                                   display: flex; align-items: center; gap: 4px;">
                                        <span style="font-size: 0.8em;">▼</span>
                                        <span>Show all $total_count attempts</span>
                                    </button>
                                </div>
                                <div id="${expand_id}" style="display: none; margin-left: 20px; margin-top: 8px; font-size: 0.9em;">
ATTEMPTS_SUMMARY
                                
                                # Parse and display each attempt
                                attempt_num=""
                                attempt_date=""
                                attempt_status=""
                                attempt_flags=""
                                
                                while IFS= read -r line; do
                                    if [[ "$line" =~ Attempt\ \#([0-9]+):\ ([0-9-]+\ [0-9\ ]+) ]]; then
                                        # New attempt - display previous if exists
                                        if [ -n "$attempt_num" ]; then
                                            status_color="#27ae60"  # Green for success
                                            status_icon="✓"
                                            if [[ "$attempt_status" == *"FAILED"* ]]; then
                                                status_color="#e74c3c"  # Red for failed
                                                status_icon="✗"
                                            fi
                                            
                                            cat >> "$HTML_FILE" << ATTEMPT_ITEM
                                    <div style="margin-bottom: 8px; padding: 8px; background: #f8f9fa; border-left: 3px solid $status_color; border-radius: 4px;">
                                        <div style="margin-bottom: 4px;">
                                            <strong style="color: $status_color;">$status_icon Attempt #$attempt_num</strong> 
                                            <span style="color: #7f8c8d; font-size: 0.85em;">($attempt_date)</span>
                                        </div>
                                        <div style="color: #555; font-size: 0.85em; margin-left: 20px;">
                                            Flags: <span style="color: #3498db;">$attempt_flags</span>
                                        </div>
                                    </div>
ATTEMPT_ITEM
                                        fi
                                        
                                        # Start new attempt
                                        attempt_num="${BASH_REMATCH[1]}"
                                        attempt_date="${BASH_REMATCH[2]}"
                                        attempt_status=""
                                        attempt_flags=""
                                    elif [[ "$line" =~ Status:\ (.+) ]]; then
                                        attempt_status="${BASH_REMATCH[1]}"
                                    elif [[ "$line" =~ Flags:\ (.+) ]]; then
                                        attempt_flags="${BASH_REMATCH[1]}"
                                    fi
                                done <<< "$attempts_data"
                                
                                # Display last attempt
                                if [ -n "$attempt_num" ]; then
                                    status_color="#27ae60"  # Green for success
                                    status_icon="✓"
                                    if [[ "$attempt_status" == *"FAILED"* ]]; then
                                        status_color="#e74c3c"  # Red for failed
                                        status_icon="✗"
                                    fi
                                    
                                    cat >> "$HTML_FILE" << ATTEMPT_ITEM
                                    <div style="margin-bottom: 8px; padding: 8px; background: #f8f9fa; border-left: 3px solid $status_color; border-radius: 4px;">
                                        <div style="margin-bottom: 4px;">
                                            <strong style="color: $status_color;">$status_icon Attempt #$attempt_num</strong> 
                                            <span style="color: #7f8c8d; font-size: 0.85em;">($attempt_date)</span>
                                        </div>
                                        <div style="color: #555; font-size: 0.85em; margin-left: 20px;">
                                            Flags: <span style="color: #3498db;">$attempt_flags</span>
                                        </div>
                                    </div>
ATTEMPT_ITEM
                                fi
                                
                                echo "                                </div>" >> "$HTML_FILE"
                            else
                                # Fallback: simple display if parsing fails
                            cat >> "$HTML_FILE" << RELEASE_METRIC
                                <div class="flow-item">
                                    <span><strong>📊 Attempts</strong></span>
                                    <span>$metric_value</span>
                                </div>
RELEASE_METRIC
                            fi
                        elif [[ "$part" =~ ^Links: ]]; then
                            # Extract custom link details by parsing the visual table
                            # Table format (after stripping ANSI codes):
                            #   Link Name                      Date         User            Source           Target            Status
                            #   AUG_07_FP                      2025-09-08   roir            ROOT [old]       ccorea_rbv...     
                            #   SEP_28_FP                      2025-10-09   raduc           ROOT [old]       ccorea_rbv...     Manual
                            #   SEP_28_FP_eco_02               2025-10-23   arcohen         NBU (ipo1001)    nbu_signoff...    [LATEST]
                            
                            # Extract table section: strip ANSI codes first, then parse rows
                            link_details=$(sed 's/\x1b\[[0-9;]*m//g' "$TEMP_DIR/${unit}_${REGRESSION_TYPE}_output.txt" 2>/dev/null | awk '
                                /All Custom Links in Central Release Area/,/Total:.*custom links/ {
                                    # Skip header, separator, summary lines, empty lines
                                    if ($0 ~ /Link Name.*Date.*User/ || $0 ~ /^[[:space:]]*-+[[:space:]]*-+/ || $0 ~ /Total:/ || $0 ~ /Classification:/ || $0 ~ /Latest NBU release:/ || $0 ~ /Location:/ || $0 ~ /All Custom Links/ || NF < 4) {
                                        next
                                    }
                                    
                                    # Process table rows (lines with actual link data)
                                    # Fields: $1=LinkName, $2=Date, $3=User, $4=Source, $5+=(ipo or [old] or target)
                                    if (NF >= 4 && $1 !~ /^[[:space:]]*$/ && $2 ~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/) {
                                        link_name = $1
                                        date = $2
                                        user = $3
                                        source = $4
                                        
                                        # Check if source has IPO: "NBU" followed by "(ipo1001)"
                                        if ($5 ~ /^\(ipo/) {
                                            # Extract IPO: (ipo1001) -> ipo1001
                                            ipo = $5
                                            gsub(/[()]/, "", ipo)
                                            source = source "(" ipo ")"
                                        }
                                        
                                        # Check for Manual badge anywhere in the line
                                        link_type = "Auto"
                                        if ($0 ~ /Manual/) {
                                            link_type = "Manual"
                                        }
                                        
                                        # Output: LinkName|Date|User|Source|Type
                                        print link_name "|" date "|" user "|" source "|" link_type
                                    }
                                }
                            ')
                            
                            # Extract workarea owner (from "Workarea Owner:" line or from ACTIVE-owner entries)
                            workarea_owner=$(sed 's/\x1b\[[0-9;]*m//g' "$TEMP_DIR/${unit}_${REGRESSION_TYPE}_output.txt" 2>/dev/null | grep -oP "Workarea Owner:\s*\K\w+" | head -1)
                            if [ -z "$workarea_owner" ]; then
                                # Fallback: extract from ACTIVE-owner line in block release locations
                                workarea_owner=$(sed 's/\x1b\[[0-9;]*m//g' "$TEMP_DIR/${unit}_${REGRESSION_TYPE}_output.txt" 2>/dev/null | grep -oP "USER:\s*\K\w+(?=.*\[ACTIVE-owner\])" | head -1)
                            fi
                            
                            # Parse into: LINK_NAME|DATE|USER|SOURCE|TYPE format
                            all_links=""
                            if [ -n "$link_details" ]; then
                                while IFS='|' read -r link_name link_date link_user source link_type; do
                                    # Default values if fields are missing (for backwards compatibility)
                                    [ -z "$source" ] && source="ROOT"
                                    [ -z "$link_type" ] && link_type="Auto"
                                    [ -z "$link_user" ] && link_user="unknown"
                                    all_links="${all_links}${link_name}|${link_date}|${link_user}|${source}|${link_type}"$'\n'
                                done <<< "$link_details"
                            fi
                            
                            # Sort by date (column 2) - newest first, then take only top 3
                            if [ -n "$all_links" ]; then
                                sorted_links=$(echo "$all_links" | grep -v '^$' | sort -t'|' -k2,2 -r)
                                total_links=$(echo "$sorted_links" | wc -l)
                                top_3_links=$(echo "$sorted_links" | head -3)
                                
                                # Display compact custom links section header
                                cat >> "$HTML_FILE" << LINKS_HEADER
                                <div class="flow-item" style="margin-top: 10px;">
                                    <span><strong>🔗 Custom Links:</strong></span>
                                </div>
                                <div style="margin-left: 20px; font-size: 0.95em; line-height: 1.6;">
LINKS_HEADER
                                
                                # Display top 3 most recent links with color coding
                                link_num=0
                                while IFS='|' read -r link_name link_date link_user source link_type; do
                                    link_num=$((link_num + 1))
                                    
                                    # Color coding: 1st=green, 2nd=orange, 3rd=gray
                                    if [ $link_num -eq 1 ]; then
                                        link_color="#27ae60"  # Green - newest
                                    elif [ $link_num -eq 2 ]; then
                                        link_color="#f39c12"  # Orange - 2nd newest
                                    else
                                        link_color="#7f8c8d"  # Gray - 3rd newest
                                    fi
                                    
                                    # User name display (only if different from workarea owner)
                                    user_display=""
                                    if [ -n "$link_user" ] && [ "$link_user" != "$workarea_owner" ] && [ "$link_user" != "unknown" ]; then
                                        user_display=", <span style=\"color: #7f8c8d; font-size: 0.85em;\">$link_user</span>"
                                    fi
                                    
                                    # Source badge (NBU only - ROOT is default, no badge)
                                    source_badge=""
                                    if [[ "$source" == NBU* ]]; then
                                        # Extract IPO if present: NBU(ipo1001) -> ipo1001
                                        ipo_name=$(echo "$source" | sed 's/NBU(\(.*\))/\1/')
                                        if [ "$ipo_name" != "$source" ]; then
                                            source_badge=" <span style=\"background: #9b59b6; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.75em; font-weight: bold; cursor: help;\" title=\"NBU Signoff Release - $ipo_name\">NBU</span>"
                                        else
                                            source_badge=" <span style=\"background: #9b59b6; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.75em; font-weight: bold; cursor: help;\" title=\"NBU Signoff Release\">NBU</span>"
                                        fi
                                    fi
                                    
                                    # Manual badge if applicable
                                    manual_badge=""
                                    if [ "$link_type" = "Manual" ]; then
                                        manual_badge=" <span style=\"background: #3498db; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.75em; font-weight: bold; cursor: help;\" title=\"Manual Alias Link\">M</span>"
                                    fi
                                    
                                    cat >> "$HTML_FILE" << COMPACT_LINK
                                    <div style="margin-bottom: 4px;">
                                        • <span style="color: $link_color; font-weight: 500;">$link_name</span> <span style="color: #95a5a6; font-size: 0.9em;">($link_date$user_display)</span>$source_badge$manual_badge
                                    </div>
COMPACT_LINK
                                done <<< "$top_3_links"
                                
                                # Show expandable section for older links if there are more than 3
                                if [ $total_links -gt 3 ]; then
                                    older_count=$((total_links - 3))
                                    older_links=$(echo "$sorted_links" | tail -n +4)
                                    
                                    # Generate unique ID for this unit's expandable section
                                    expand_id="custom_links_${unit}_$$"
                                    
                                    # Hidden section with older links (initially hidden)
                                    cat >> "$HTML_FILE" << OLDER_LINKS_START
                                    <div id="${expand_id}" style="display: none; margin-top: 4px;">
OLDER_LINKS_START
                                    
                                    # Display all older links (all in gray)
                                    while IFS='|' read -r link_name link_date link_user source link_type; do
                                        # User name display (only if different from workarea owner)
                                        user_display=""
                                        if [ -n "$link_user" ] && [ "$link_user" != "$workarea_owner" ] && [ "$link_user" != "unknown" ]; then
                                            user_display=", <span style=\"color: #7f8c8d; font-size: 0.85em;\">$link_user</span>"
                                        fi
                                        
                                        # Source badge (NBU only - ROOT is default, no badge)
                                        source_badge=""
                                        if [[ "$source" == NBU* ]]; then
                                            # Extract IPO if present: NBU(ipo1001) -> ipo1001
                                            ipo_name=$(echo "$source" | sed 's/NBU(\(.*\))/\1/')
                                            if [ "$ipo_name" != "$source" ]; then
                                                source_badge=" <span style=\"background: #9b59b6; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.75em; font-weight: bold; cursor: help;\" title=\"NBU Signoff Release - $ipo_name\">NBU</span>"
                                            else
                                                source_badge=" <span style=\"background: #9b59b6; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.75em; font-weight: bold; cursor: help;\" title=\"NBU Signoff Release\">NBU</span>"
                                            fi
                                        fi
                                        
                                        # Manual badge if applicable
                                        manual_badge=""
                                        if [ "$link_type" = "Manual" ]; then
                                            manual_badge=" <span style=\"background: #3498db; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.75em; font-weight: bold; cursor: help;\" title=\"Manual Alias Link\">M</span>"
                                        fi
                                        
                                        cat >> "$HTML_FILE" << OLDER_LINK
                                        <div style="margin-bottom: 4px;">
                                            • <span style="color: #7f8c8d; font-weight: 500;">$link_name</span> <span style="color: #95a5a6; font-size: 0.9em;">($link_date$user_display)</span>$source_badge$manual_badge
                                        </div>
OLDER_LINK
                                    done <<< "$older_links"
                                    
                                    # Close hidden section
                                    echo "                                    </div>" >> "$HTML_FILE"
                                    
                                    # Expandable button
                                    cat >> "$HTML_FILE" << EXPAND_BUTTON
                                    <div style="margin-top: 6px;">
                                        <button onclick="toggleCustomLinks('${expand_id}')" 
                                                id="${expand_id}_btn"
                                                style="background: none; border: none; color: #3498db; cursor: pointer; 
                                                       font-size: 0.9em; padding: 4px 8px; text-decoration: underline;
                                                       display: flex; align-items: center; gap: 4px;">
                                            <span style="font-size: 0.8em;">▼</span>
                                            <span>Show $older_count more older link(s)</span>
                                        </button>
                                    </div>
EXPAND_BUTTON
                                fi
                                
                                echo "                                </div>" >> "$HTML_FILE"
                            fi
                        fi
                    done
                    
                    echo "                                </div>" >> "$HTML_FILE"
                fi
            elif [ "$REGRESSION_TYPE" = "clock" ]; then
                # For Clock: Display individual clock latencies
                if [ "$details" != "No clock tree analysis found" ] && [ "$details" != "No clock data available" ]; then
                    # Get clock latency file path for this unit
                    clock_latency_file="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_clock_latency_file]}"
                    
                    cat >> "$HTML_FILE" << CLOCK_START
                            <div class="formal-flows">
                                <div class="flow-title">Clock Latencies:</div>
CLOCK_START
                    
                    # Extract per-clock details from output file
                    # Format: "Clock Detail: CLOCK_NAME|MAX_LATENCY_PS|SKEW_PS"
                    clock_details=$(grep "Clock Detail:" "$TEMP_DIR/${unit}_${REGRESSION_TYPE}_output.txt" 2>/dev/null | sed 's/.*Clock Detail:[[:space:]]*//' | sed 's/\x1b\[[0-9;]*m//g')
                    
                    if [ -n "$clock_details" ]; then
                        # Display each clock with its latency and skew
                        while IFS='|' read -r clock_name max_latency skew; do
                            # Determine status color based on latency
                            if (( $(echo "$max_latency >= 580" | bc -l) )); then
                                latency_class="flow-failed"
                                latency_icon="❌"
                            elif (( $(echo "$max_latency > 550" | bc -l) )); then
                                latency_class="flow-unresolved"
                                latency_icon="⚠️"
                            else
                                latency_class="flow-succeeded"
                                latency_icon="✅"
                            fi
                            
                            # Format latency with proper decimals
                            formatted_latency=$(printf "%.1f" "$max_latency")
                            formatted_skew=$(printf "%.1f" "$skew")
                            
                            cat >> "$HTML_FILE" << CLOCK_ITEM
                                <div class="flow-item $latency_class">
                                    <span><strong>🕐 $clock_name</strong></span>
                                    <span>$latency_icon ${formatted_latency}ps <span style="font-size: 0.85em; color: #666;">(skew: ${formatted_skew}ps)</span></span>
                                </div>
CLOCK_ITEM
                        done <<< "$clock_details"
                    else
                        # Fallback to displaying summary details
                        cat >> "$HTML_FILE" << CLOCK_SUMMARY
                                <div class="flow-item">
                                    <span>Summary</span>
                                    <span>$details</span>
                                </div>
CLOCK_SUMMARY
                    fi
                    
                    # Add link to clock latency file if available (contains trace per clock with highest latency path)
                    if [ "$clock_latency_file" != "N/A" ] && [ -n "$clock_latency_file" ]; then
                        cat >> "$HTML_FILE" << CLOCK_LATENCY_LINK
                                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e0e0e0;">
                                    <a href="file://${clock_latency_file}" target="_blank" 
                                       style="color: #3498db; text-decoration: none; font-size: 0.9em; display: inline-flex; align-items: center; gap: 6px;">
                                        📄 View Clock Latency Report
                                        <span style="font-size: 0.85em; color: #666;">(trace per clock with highest latency path)</span>
                                    </a>
                                </div>
CLOCK_LATENCY_LINK
                    fi
                    
                    echo "                                </div>" >> "$HTML_FILE"
                fi
            elif [ "$REGRESSION_TYPE" = "glcheck" ]; then
                # For GL Check: Display error breakdown
                if [ "$details" != "No GL Check data available" ] && [ "$details" != "No GL Check analysis found" ]; then
                    # Get GL Check-specific data
                    total_errors="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_total_errors]}"
                    waived="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_waived]}"
                    non_waived="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_non_waived]}"
                    top_checkers="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_top_checkers]}"
                    
                    cat >> "$HTML_FILE" << GLCHECK_START
                            <div class="formal-flows">
                                <div class="flow-title">GL Check Results:</div>
                                <div class="flow-item">
                                    <span><strong>📊 Total Errors</strong></span>
                                    <span>$total_errors</span>
                                </div>
                                <div class="flow-item flow-succeeded">
                                    <span>✅ Waived</span>
                                    <span>$waived</span>
                                </div>
GLCHECK_START
                    
                    # Color code non-waived based on severity
                    if [ "$non_waived" != "N/A" ] && [ -n "$non_waived" ] && [[ "$non_waived" =~ ^[0-9]+$ ]]; then
                        non_waived_num=$non_waived
                        if [ $non_waived_num -eq 0 ]; then
                            nw_class="flow-succeeded"
                            nw_icon="✅"
                            nw_label="CLEAN"
                        elif [ $non_waived_num -lt 50 ]; then
                            nw_class="flow-unresolved"
                            nw_icon="⚠️"
                            nw_label="MINOR"
                        else
                            nw_class="flow-failed"
                            nw_icon="❌"
                            nw_label="CRITICAL"
                        fi
                        
                        cat >> "$HTML_FILE" << GLCHECK_NW
                                <div class="flow-item $nw_class">
                                    <span><strong>🔍 Non-Waived</strong></span>
                                    <span>$nw_icon $non_waived ($nw_label)</span>
                                </div>
GLCHECK_NW
                    fi
                    
                    # Show top 3 checkers if available
                    if [ "$top_checkers" != "N/A" ] && [ -n "$top_checkers" ]; then
                        echo '                                <div style="margin-top: 15px; padding-top: 15px; border-top: 2px solid #f0f0f0;">' >> "$HTML_FILE"
                        echo '                                    <div class="flow-title" style="font-size: 0.9em;">🔝 Top Issues by Checker:</div>' >> "$HTML_FILE"
                        
                        IFS=';' read -ra checkers <<< "$top_checkers"
                        for checker_info in "${checkers[@]}"; do
                            IFS=':' read -r checker_name nw_count <<< "$checker_info"
                            
                            # Color code based on count (stricter thresholds for top issues)
                            if [ "$nw_count" -eq 0 ]; then
                                checker_class="flow-succeeded"
                                checker_icon="✅"
                            elif [ "$nw_count" -lt 10 ]; then
                                checker_class="flow-unresolved"
                                checker_icon="⚠️"
                            else
                                checker_class="flow-failed"
                                checker_icon="❌"
                            fi
                            
                            cat >> "$HTML_FILE" << GLCHECK_CHECKER
                                    <div class="flow-item $checker_class" style="font-size: 0.85em;">
                                        <span>$checker_name</span>
                                        <span>$checker_icon $nw_count violations</span>
                                    </div>
GLCHECK_CHECKER
                        done
                        
                        echo '                                </div>' >> "$HTML_FILE"
                    fi
                    
                    echo "                            </div>" >> "$HTML_FILE"
                fi
            else
                # For other types: Display as flows
                if [ "$details" != "No formal flows found" ] && [ "$details" != "No formal flow detected" ]; then
                    cat >> "$HTML_FILE" << FLOWS_START
                            <div class="formal-flows">
                                <div class="flow-title">Formal Flows:</div>
FLOWS_START
                    
                    # Get failing compare points for formal regression (format: bbox|pnr|syn|syn_bbox)
                    failing_compare_pts_data=""
                    if [ "$REGRESSION_TYPE" = "formal" ]; then
                        failing_compare_pts_data="${REGRESSION_RESULTS[${REGRESSION_TYPE}_${idx}_failing_compare_pts]}"
                        # Split into array: [0]=bbox, [1]=pnr, [2]=syn, [3]=syn_bbox (colon-delimited)
                        IFS=':' read -ra failing_pts_arr <<< "$failing_compare_pts_data"
                    fi
                    
                    # Parse details string (format: "flow: STATUS (runtime)")
                    IFS=',' read -ra flows <<< "$details"
                    flow_idx=0
                    for flow_info in "${flows[@]}"; do
                        flow_info=$(echo "$flow_info" | xargs)
                        flow_name=$(echo "$flow_info" | cut -d':' -f1 | xargs)
                        flow_rest=$(echo "$flow_info" | cut -d':' -f2- | xargs)
                        
                        # Extract status and runtime (runtime is in parentheses)
                        # Use variable to avoid shell escaping issues
                        status_runtime_regex='^([A-Z_]+)[[:space:]]*\(([^)]+)\)'
                        if [[ "$flow_rest" =~ $status_runtime_regex ]]; then
                            flow_status="${BASH_REMATCH[1]}"
                            flow_runtime="${BASH_REMATCH[2]}"
                        else
                            flow_status="$flow_rest"
                            flow_runtime=""
                        fi
                        
                        # Determine flow status class
                        case "$flow_status" in
                            SUCCEEDED)
                                flow_class="flow-succeeded"
                                flow_icon="✅"
                                ;;
                            FAILED)
                                flow_class="flow-failed"
                                flow_icon="❌"
                                ;;
                            UNRESOLVED)
                                flow_class="flow-unresolved"
                                flow_icon="⚠️"
                                ;;
                            CRASHED)
                                flow_class="flow-crashed"
                                flow_icon="💥"
                                ;;
                            RUNNING)
                                flow_class="flow-running"
                                flow_icon="🔄"
                                ;;
                            *)
                                flow_class=""
                                flow_icon="❔"
                                ;;
                        esac
                        
                        # Build display text with runtime
                        if [ -n "$flow_runtime" ]; then
                            flow_display="$flow_icon $flow_status <span style=\"font-size: 0.85em; color: #666;\">($flow_runtime)</span>"
                        else
                            flow_display="$flow_icon $flow_status"
                        fi
                        
                        # Get failing compare points for this specific flow (formal only)
                        failing_pts_value=""
                        if [ "$REGRESSION_TYPE" = "formal" ] && [ ${#failing_pts_arr[@]} -gt 0 ]; then
                            # Map flow name to array index: bbox=0, pnr=1, syn=2, syn_bbox=3
                            if [[ "$flow_name" == "rtl_vs_pnr_bbox" ]]; then
                                failing_pts_value="${failing_pts_arr[0]}"
                            elif [[ "$flow_name" == "rtl_vs_pnr" ]]; then
                                failing_pts_value="${failing_pts_arr[1]}"
                            elif [[ "$flow_name" == "rtl_vs_syn" ]]; then
                                failing_pts_value="${failing_pts_arr[2]}"
                            elif [[ "$flow_name" == "rtl_vs_syn_bbox" ]]; then
                                failing_pts_value="${failing_pts_arr[3]}"
                            fi
                            
                            # Add failing compare points to display if available and not N/A
                            if [ -n "$failing_pts_value" ] && [ "$failing_pts_value" != "N/A" ]; then
                                # Color code based on value: 0=green, >0=red
                                if [ "$failing_pts_value" = "0" ]; then
                                    flow_display="$flow_display <span style=\"font-size: 0.85em; color: #27ae60;\">[0 failing pts]</span>"
                                else
                                    flow_display="$flow_display <span style=\"font-size: 0.85em; color: #e74c3c; font-weight: 600;\">[$failing_pts_value failing pts]</span>"
                                fi
                            fi
                        fi
                        
                        cat >> "$HTML_FILE" << FLOW_ITEM
                                <div class="flow-item $flow_class">
                                    <span>$flow_name</span>
                                    <span>$flow_display</span>
                                </div>
FLOW_ITEM
                        ((flow_idx++))
                    done
                    
                    echo "                                </div>" >> "$HTML_FILE"
                fi
            fi
            
            echo "                            </div>" >> "$HTML_FILE"
        done
        
        cat >> "$HTML_FILE" << CHIPLET_END
                    </div>
                </div>
            </div>
CHIPLET_END
    done
    
    unset chiplet_units_tab
    
    cat >> "$HTML_FILE" << 'TAB_CONTENT_END'
        </div>
    </div>
TAB_CONTENT_END
done

# Close HTML with footer and JavaScript
cat >> "$HTML_FILE" << 'MULTI_HTML_END'
    
    <div class="footer">
        <p><strong>AVICE Multi-Regression Dashboard</strong></p>
        <p>Copyright (c) 2025 Alon Vice (avice)</p>
        <p>Contact: avice@nvidia.com</p>
    </div>
</div>

<div id="toast" class="toast">Copied to clipboard!</div>

<script>
    // Logo modal functionality
    function showLogoModal() {
        document.getElementById('logoModal').style.display = 'block';
    }
    
    function closeLogoModal() {
        document.getElementById('logoModal').style.display = 'none';
    }
    
    // Tab switching
    function openTab(tabName) {
        const tabContents = document.getElementsByClassName('tab-content');
        for (let i = 0; i < tabContents.length; i++) {
            tabContents[i].classList.remove('active');
        }
        
        const tabButtons = document.getElementsByClassName('tab-button');
        for (let i = 0; i < tabButtons.length; i++) {
            tabButtons[i].classList.remove('active');
        }
        
        document.getElementById(tabName).classList.add('active');
        event.target.classList.add('active');
    }
    
    // Toggle chiplet sections
    function toggleChiplet(chipletId) {
        const content = document.getElementById('content-' + chipletId);
        const toggle = document.getElementById('toggle-' + chipletId);
        
        if (content.classList.contains('active')) {
            content.classList.remove('active');
            toggle.textContent = '▶';
        } else {
            content.classList.add('active');
            toggle.textContent = '▼';
        }
    }
    
    // Copy to clipboard
    function copyToClipboard(elementId, button) {
        const element = document.getElementById(elementId);
        const text = element.textContent;
        
        navigator.clipboard.writeText(text).then(function() {
            showToast();
            button.textContent = '✓ Copied';
            setTimeout(function() {
                button.textContent = '📋 Copy';
            }, 2000);
        });
    }
    
    function showToast() {
        const toast = document.getElementById('toast');
        toast.classList.add('show');
        setTimeout(function() {
            toast.classList.remove('show');
        }, 3000);
    }
    
    // Toggle custom links expandable section
    function toggleCustomLinks(expandId) {
        const expandDiv = document.getElementById(expandId);
        const button = document.getElementById(expandId + '_btn');
        
        if (expandDiv.style.display === 'none') {
            // Expand - show older links
            expandDiv.style.display = 'block';
            // Change button text and arrow
            const arrow = button.querySelector('span:first-child');
            const text = button.querySelector('span:last-child');
            arrow.textContent = '▲';
            text.textContent = 'Show less';
        } else {
            // Collapse - hide older links
            expandDiv.style.display = 'none';
            // Change button text and arrow
            const arrow = button.querySelector('span:first-child');
            const text = button.querySelector('span:last-child');
            const count = text.textContent.match(/\d+/);
            arrow.textContent = '▼';
            text.textContent = 'Show ' + (count ? count[0] : '') + ' more older link(s)';
        }
    }
    
    // Toggle timing breakdown expandable section
    function toggleTimingBreakdown(timingId) {
        const contentDiv = document.getElementById(timingId);
        const arrow = document.getElementById(timingId + '-arrow');
        
        if (contentDiv.style.display === 'none') {
            // Expand - show timing details
            contentDiv.style.display = 'block';
            arrow.style.transform = 'rotate(90deg)';
        } else {
            // Collapse - hide timing details
            contentDiv.style.display = 'none';
            arrow.style.transform = 'rotate(0deg)';
        }
    }
    
    // Search and filter functionality
    function filterUnits() {
        const searchInput = document.getElementById('searchInput').value.toLowerCase();
        const unitCards = document.getElementsByClassName('unit-card');
        let visibleCount = 0;
        
        for (let card of unitCards) {
            const unitName = card.querySelector('.unit-name').textContent.toLowerCase();
            const workarea = card.querySelector('.workarea-path') ? card.querySelector('.workarea-path').textContent.toLowerCase() : '';
            
            if (unitName.includes(searchInput) || workarea.includes(searchInput)) {
                if (!card.classList.contains('status-filtered')) {
                    card.classList.remove('hidden');
                    visibleCount++;
                }
            } else {
                card.classList.add('hidden');
            }
        }
    }
    
    function filterStatus(evt, status) {
        try {
            const unitCards = document.getElementsByClassName('unit-card');
            const statCards = document.getElementsByClassName('stat-card');
            
            // Update active stat card (statistics cards at top)
            for (let card of statCards) {
                card.classList.remove('active');
            }
            
            // Add active class to clicked stat card
            if (evt && evt.target) {
                // If clicked on a child element (like stat-value), find parent stat-card
                let targetElement = evt.target;
                if (!targetElement.classList.contains('stat-card')) {
                    targetElement = evt.target.closest('.stat-card');
                }
                if (targetElement) {
                    targetElement.classList.add('active');
                }
            }
            
            // Filter unit cards based on status
            for (let card of unitCards) {
                const statusBadgeEl = card.querySelector('.status-badge');
                if (!statusBadgeEl) continue;
                
                const statusBadge = statusBadgeEl.textContent.toLowerCase();
            
            if (status === 'all') {
                card.classList.remove('status-filtered', 'hidden');
            } else if (status === 'passed' && statusBadge.includes('passed')) {
                card.classList.remove('status-filtered', 'hidden');
            } else if (status === 'failed' && (statusBadge.includes('failed') || statusBadge.includes('error'))) {
                card.classList.remove('status-filtered', 'hidden');
            } else if (status === 'crashed' && statusBadge.includes('crashed')) {
                card.classList.remove('status-filtered', 'hidden');
            } else if (status === 'warn' && (statusBadge.includes('warn') || statusBadge.includes('partial'))) {
                card.classList.remove('status-filtered', 'hidden');
            } else if (status === 'unresolved' && statusBadge.includes('unresolved')) {
                card.classList.remove('status-filtered', 'hidden');
            } else if (status === 'not_run' && statusBadge.includes('not run')) {
                card.classList.remove('status-filtered', 'hidden');
            } else if (status === 'no_data' && statusBadge.includes('no data')) {
                card.classList.remove('status-filtered', 'hidden');
            } else if (status === 'missing' && statusBadge.includes('missing')) {
                card.classList.remove('status-filtered', 'hidden');
            } else {
                card.classList.add('status-filtered', 'hidden');
            }
        }
        
        // Re-apply search filter
        filterUnits();
        
        // Highlight chiplets containing matching units
        highlightRelevantChiplets(status);
        } catch (e) {
            console.error('Error in filterStatus:', e);
        }
    }
    
    function highlightRelevantChiplets(status) {
        try {
            const chipletHeaders = document.querySelectorAll('.chiplet-header');
            const chipletSections = document.querySelectorAll('.chiplet-section');
            
            // Remove all previous highlights
            for (let header of chipletHeaders) {
                header.classList.remove('highlighted-passed', 'highlighted-failed', 'highlighted-crashed', 
                                        'highlighted-warn', 'highlighted-unresolved', 'highlighted-not_run', 
                                        'highlighted-no_data', 'highlighted-missing');
            }
            
            // If showing all, don't highlight anything
            if (status === 'all') {
                return;
            }
            
            // Determine highlight class based on status
            const highlightClass = 'highlighted-' + status;
            
            // Check each chiplet section for visible units
            for (let section of chipletSections) {
                const unitsGrid = section.querySelector('.units-grid');
                if (!unitsGrid) continue;
                
                const unitCards = unitsGrid.querySelectorAll('.unit-card');
                let hasVisibleUnits = false;
                
                // Check if this chiplet has any visible (matching) units
                for (let card of unitCards) {
                    if (!card.classList.contains('hidden') && !card.classList.contains('status-filtered')) {
                        hasVisibleUnits = true;
                        break;
                    }
                }
                
                // If chiplet has matching units, highlight and expand it
                if (hasVisibleUnits) {
                    const header = section.querySelector('.chiplet-header');
                    const content = section.querySelector('.collapsible-content');
                    const toggle = section.querySelector('.toggle');
                    
                    if (header) {
                        header.classList.add(highlightClass);
                    }
                    
                    // Auto-expand chiplets with matching units
                    if (content && !content.classList.contains('active')) {
                        content.classList.add('active');
                        if (toggle) {
                            toggle.textContent = '▼';
                        }
                    }
                }
            }
        } catch (e) {
            console.error('Error in highlightRelevantChiplets:', e);
        }
    }
    
    function collapseAll() {
        try {
            const chipletHeaders = document.querySelectorAll('.chiplet-header');
            const chipletContents = document.querySelectorAll('.collapsible-content');
            const toggles = document.querySelectorAll('.chiplet-header .toggle');
            
            // Collapse all chiplet sections
            for (let content of chipletContents) {
                content.classList.remove('active');
            }
            
            // Update all toggle icons to collapsed state
            for (let toggle of toggles) {
                toggle.textContent = '▶';
            }
            
            // Remove all highlights
            for (let header of chipletHeaders) {
                header.classList.remove('highlighted-passed', 'highlighted-failed', 'highlighted-crashed', 
                                        'highlighted-warn', 'highlighted-unresolved', 'highlighted-not_run', 
                                        'highlighted-no_data', 'highlighted-missing');
            }
        } catch (e) {
            console.error('Error in collapseAll:', e);
        }
    }
    
    function expandAll() {
        try {
            const chipletHeaders = document.querySelectorAll('.chiplet-header');
            const chipletContents = document.querySelectorAll('.collapsible-content');
            const toggles = document.querySelectorAll('.chiplet-header .toggle');
            
            // Expand all chiplet sections
            for (let content of chipletContents) {
                content.classList.add('active');
            }
            
            // Update all toggle icons to expanded state
            for (let toggle of toggles) {
                toggle.textContent = '▼';
            }
            
            // Remove all highlights (clean slate)
            for (let header of chipletHeaders) {
                header.classList.remove('highlighted-passed', 'highlighted-failed', 'highlighted-crashed', 
                                        'highlighted-warn', 'highlighted-unresolved', 'highlighted-not_run', 
                                        'highlighted-no_data', 'highlighted-missing');
            }
        } catch (e) {
            console.error('Error in expandAll:', e);
        }
    }
    
    function exportToCSV() {
        try {
        const unitCards = document.getElementsByClassName('unit-card');
        let csv = 'Unit,Chiplet,Status,Released By,Release Date,Runtime,Workarea\n';
        
        for (let card of unitCards) {
            if (card.classList.contains('hidden')) continue;
            
            const unit = card.querySelector('.unit-name').textContent.trim();
            const status = card.querySelector('.status-badge').textContent.trim();
            const infoRows = card.querySelectorAll('.info-value');
            
            let releasedBy = '';
            let releaseDate = '';
            let runtime = '';
            let workarea = '';
            let chiplet = card.closest('.chiplet-section') ? card.closest('.chiplet-section').querySelector('.chiplet-header span').textContent.split(' ')[0] : '';
            
            const infoLabels = card.querySelectorAll('.info-label');
            for (let i = 0; i < infoLabels.length; i++) {
                const label = infoLabels[i].textContent.trim();
                const value = infoRows[i] ? infoRows[i].textContent.trim() : '';
                
                if (label.includes('Released By')) releasedBy = value;
                if (label.includes('Release Date')) releaseDate = value;
                if (label.includes('Runtime')) runtime = value;
                if (label.includes('Workarea')) workarea = value;
            }
            
            csv += `"${unit}","${chiplet}","${status}","${releasedBy}","${releaseDate}","${runtime}","${workarea}"\n`;
        }
        
        // Download CSV
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'agur_regression_results_' + new Date().toISOString().split('T')[0] + '.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showToast();
        } catch (e) {
            console.error('Error in exportToCSV:', e);
            alert('Error exporting CSV: ' + e.message);
        }
    }
    
    function printDashboard() {
        try {
            window.print();
        } catch (e) {
            console.error('Error in printDashboard:', e);
        }
    }
    
    // Initialize page - activate "Total Units" card by default
    window.addEventListener('DOMContentLoaded', function() {
        try {
            // Find and activate the first stat-card (Total Units)
            const firstStatCard = document.querySelector('.stat-card[data-filter="all"]');
            if (firstStatCard) {
                firstStatCard.classList.add('active');
            }
        } catch (e) {
            console.error('Error in page initialization:', e);
        }
    });
</script>

<!-- Back to Top Button -->
<button id="backToTopBtn" title="Go to top">↑ Top</button>

<script>
    // Back to Top Button functionality (must run after button is in DOM)
    document.addEventListener('DOMContentLoaded', function() {
        const backToTopBtn = document.getElementById('backToTopBtn');
        if (backToTopBtn) {
            window.addEventListener('scroll', function() {
                if (window.pageYOffset > 300) {
                    backToTopBtn.classList.add('visible');
                } else {
                    backToTopBtn.classList.remove('visible');
                }
            });
            
            backToTopBtn.addEventListener('click', function() {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    });
</script>

</body>
</html>
MULTI_HTML_END

# Print HTML generation message based on quiet mode
if [ $QUIET -eq 0 ]; then
echo "HTML dashboard generated: $HTML_FILE"
fi

# Set regression name for summary
if [ ${#REGRESSION_TYPES[@]} -gt 1 ]; then
    REGRESSION_NAME="Multi-Type (${REGRESSION_TYPES[*]})"
fi

# Cleanup temp directory
rm -rf "$TEMP_DIR"

#===============================================================================
# Final Summary
#===============================================================================

# Print summary only if not in quiet mode
if [ $QUIET -eq 0 ]; then
echo ""
echo ""
print_header
echo -e "${GREEN}$REGRESSION_NAME Regression Complete!${NC}"
echo ""
echo "Results Summary:"
echo "  - Total Units: $TOTAL_UNITS"
echo -e "  - ${GREEN}Passed: $passed_count${NC}"
echo -e "  - ${YELLOW}Warnings: $warn_count${NC}"
echo -e "  - ${YELLOW}Partial Pass: $partial_count${NC}"
echo -e "  - ${YELLOW}Unresolved: $unresolved_count${NC}"
echo -e "  - ${RED}Failed: $failed_count${NC}"
echo -e "  - ${RED}Crashed: $crashed_count${NC}"
echo -e "  - ${YELLOW}Running: $running_count${NC}"
echo -e "  - ${YELLOW}Errors: $error_count${NC}"
echo -e "  - ${YELLOW}Not Run: $not_found_count${NC}"
echo -e "  - ${YELLOW}No Data: $no_data_count${NC}"
echo -e "  - ${RED}Missing WA: $missing_count${NC}"
echo ""
echo "Output File:"
echo "  - HTML Dashboard: $HTML_FILE"
echo ""
echo -e "${CYAN}===============================================================================${NC}"
else
    # In quiet mode, just print the HTML file location
    echo ""
    echo "HTML Dashboard: $HTML_FILE"
fi

# Exit with appropriate code
if [ $failed_count -gt 0 ] || [ $crashed_count -gt 0 ] || [ $error_count -gt 0 ]; then
    exit 1
else
    exit 0
fi

