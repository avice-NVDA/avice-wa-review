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
#   -t, --type TYPE          Regression type: formal|timing|pv|clock|release (REQUIRED)
#   -c, --chiplet CHIPLET    Filter by chiplet - case-insensitive (default: all chiplets)
#   -u, --unit UNIT          Run for specific unit only
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
#
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNITS_TABLE="$SCRIPT_DIR/AGUR_UNITS_TABLE.txt"
AVICE_SCRIPT="/home/avice/scripts/avice_wa_review/avice_wa_review.py"
PYTHON_BIN="/home/utils/Python/builds/3.11.9-20250715/bin/python3"

# Regression configuration
REGRESSION_TYPES=()  # Array to store multiple regression types: formal, timing, pv, clock, release

# Output files (generated in user's current working directory)
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
TEMP_DIR="/tmp/agur_regression_$$"

# Filters
FILTER_CHIPLETS=()  # Array to store multiple chiplets: CPORT, HPORT, NDQ, QNS, TCB
FILTER_UNIT=""

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
# Args: current, total, unit_name
show_progress() {
    local current=$1
    local total=$2
    local unit_name=$3
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
    
    echo -ne "\r${CYAN}Progress:${NC} $bar ${percentage}% (${current}/${total}) - ${unit_name}${eta_str}     "
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
        if command -v timeout &> /dev/null; then
            timeout 1800 "$PYTHON_BIN" "$AVICE_SCRIPT" "$workarea" -s "$analysis_section" --no-logo > "$output_file" 2>&1
            local exit_code=$?
            
            if [ $exit_code -eq 124 ]; then
                log_verbose "Unit $unit: Analysis timed out after 30 minutes"
                ((retry_count++))
                continue
            fi
        else
            "$PYTHON_BIN" "$AVICE_SCRIPT" "$workarea" -s "$analysis_section" --no-logo > "$output_file" 2>&1
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
    
    # Convert formal section to array for easier processing
    local formal_lines=()
    while IFS= read -r line; do
        formal_lines+=("$line")
    done <<< "$formal_section"
    
    # Process array line by line
    local current_flow=""
    for i in "${!formal_lines[@]}"; do
        line="${formal_lines[$i]}"
        
        # Detect which flow this is - look for "Formal Log:" prefix
        if [[ "$line" == *"Formal Log:"* ]] && [[ "$line" == *"rtl_vs_pnr_bbox_fm/log/rtl_vs_pnr_bbox_fm.log"* ]]; then
            current_flow="rtl_vs_pnr_bbox"
        elif [[ "$line" == *"Formal Log:"* ]] && [[ "$line" == *"rtl_vs_pnr_fm/log/rtl_vs_pnr_fm.log"* ]]; then
            current_flow="rtl_vs_pnr"
        elif [[ "$line" == *"Formal Log:"* ]] && [[ "$line" == *"rtl_vs_syn_fm/log/rtl_vs_syn_fm.log"* ]]; then
            current_flow="rtl_vs_syn"
        elif [[ "$line" == *"Formal Log:"* ]] && [[ "$line" == *"rtl_vs_syn_bbox_fm/log/rtl_vs_syn_bbox_fm.log"* ]]; then
            current_flow="rtl_vs_syn_bbox"
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
            
            # Extract runtime
            if [[ "$line" =~ Runtime:[[:space:]]*([0-9.]+[[:space:]]*(hours?|minutes?)) ]]; then
                case "$current_flow" in
                    rtl_vs_pnr) rtl_vs_pnr_runtime="${BASH_REMATCH[1]}" ;;
                    rtl_vs_pnr_bbox) rtl_vs_pnr_bbox_runtime="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn) rtl_vs_syn_runtime="${BASH_REMATCH[1]}" ;;
                    rtl_vs_syn_bbox) rtl_vs_syn_bbox_runtime="${BASH_REMATCH[1]}" ;;
                esac
                # After runtime, reset current_flow for next flow
                current_flow=""
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
    
    # Return pipe-delimited string: status|details|runtime
    echo "${overall_status}|${details}|${runtime}"
}

# Parse timing (PT) output
# Args: $1 = output file path
# Returns: status|details|runtime
parse_timing_output() {
    local output_file="$1"
    local status=""
    local details=""
    local runtime="N/A"
    
    # Extract PT Signoff Timing section - match actual output format
    local timing_section=$(grep -A 200 "Signoff Timing (PT)\|PT Timing Summary" "$output_file")
    
    if [ -z "$timing_section" ]; then
        echo "NOT_FOUND|No PT timing analysis found|N/A"
        return
    fi
    
    # Check for "No PT signoff timing" message
    if echo "$timing_section" | grep -q "No PT signoff timing"; then
        echo "NOT_FOUND|No PT timing analysis found|N/A"
        return
    fi
    
    # Strip ANSI color codes from the section (format: [32m text [0m)
    timing_section=$(echo "$timing_section" | sed 's/\x1b\[[0-9;]*m//g')
    
    # Extract key timing metrics - match actual format with units (ns)
    # Format: "      WNS:   0.000 ns" or "      WNS:  -1.234 ns"
    local wns=$(echo "$timing_section" | grep -i "WNS:" | grep -oP "WNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
    local tns=$(echo "$timing_section" | grep -i "TNS:" | grep -oP "TNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
    local nvp=$(echo "$timing_section" | grep -i "NVP:" | grep -oP "NVP:\s*\K[0-9]+" | head -1)
    
    # Set defaults if extraction failed
    [ -z "$wns" ] && wns="N/A"
    [ -z "$tns" ] && tns="N/A"
    [ -z "$nvp" ] && nvp="N/A"
    
    # Determine overall timing status
    local overall_status="UNKNOWN"
    
    if [ "$wns" = "N/A" ] && [ "$tns" = "N/A" ]; then
        overall_status="NO_DATA"
        details="No timing data available"
    elif [ "$wns" != "N/A" ]; then
        # Convert WNS to float for comparison (bash doesn't handle floats well, use awk)
        local wns_check=$(echo "$wns 0" | awk '{if ($1 >= $2) print "PASS"; else print "FAIL"}')
        
        # Format timing values: if < 0.5ns, show in ps for better readability
        local wns_formatted="$wns"
        local tns_formatted="$tns"
        local wns_unit="ns"
        local tns_unit="ns"
        
        # Check if WNS absolute value is less than 0.5ns
        local wns_abs=$(echo "$wns" | tr -d '-')
        if [ $(echo "$wns_abs 0.5" | awk '{if ($1 < $2) print "1"; else print "0"}') -eq 1 ]; then
            wns_formatted=$(echo "$wns" | awk '{printf "%.0f", $1 * 1000}')
            wns_unit="ps"
        fi
        
        # Check if TNS absolute value is less than 0.5ns
        local tns_abs=$(echo "$tns" | tr -d '-')
        if [ $(echo "$tns_abs 0.5" | awk '{if ($1 < $2) print "1"; else print "0"}') -eq 1 ]; then
            tns_formatted=$(echo "$tns" | awk '{printf "%.0f", $1 * 1000}')
            tns_unit="ps"
        fi
        
        if [ "$wns_check" = "PASS" ]; then
            overall_status="PASSED"
            details="WNS: ${wns_formatted}${wns_unit}, TNS: ${tns_formatted}${tns_unit}"
            [ "$nvp" != "N/A" ] && details="${details}, Violating Paths: ${nvp}"
        else
            # Check severity of violation (in nanoseconds)
            # Critical if WNS < -0.05ns (50ps)
            local is_critical=$(echo "$wns_abs 0.05" | awk '{if ($1 > $2) print "YES"; else print "NO"}')
            
            if [ "$is_critical" = "YES" ]; then
                overall_status="FAILED"
            else
                overall_status="WARN"
            fi
            details="WNS: ${wns_formatted}${wns_unit} (VIOLATION), TNS: ${tns_formatted}${tns_unit}"
            [ "$nvp" != "N/A" ] && details="${details}, Violating Paths: ${nvp}"
        fi
    else
        overall_status="UNKNOWN"
        details="Unable to determine timing status"
    fi
    
    # Extract runtime if available
    runtime=$(echo "$timing_section" | grep -i "Runtime:" | head -1 | grep -oP "Runtime:\s*\K[0-9.]+ (hours|minutes|seconds)")
    [ -z "$runtime" ] && runtime="N/A"
    
    # Return pipe-delimited string
    echo "${overall_status}|${details}|${runtime}"
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
    
    # Extract runtime if available (look for Duration from PV Flow Timeline)
    runtime=$(echo "$pv_section" | grep -i "Duration:" | head -1 | grep -oP "Duration:\s*\K.*")
    [ -z "$runtime" ] && runtime="N/A"
    
    # Return pipe-delimited string
    echo "${overall_status}|${details}|${runtime}"
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
    
    # Return pipe-delimited string
    echo "${overall_status}|${details}|${runtime}"
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
    
    # Check for "No block release attempts found" message
    if echo "$release_section" | grep -q "No block release attempts found"; then
        echo "NOT_FOUND|No block release attempts found|N/A"
        return
    fi
    
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
    
    # Extract custom links list from the summary section (not from individual attempts)
    # Format: "Custom Links: SEP_28_FP_eco_01, SEP_28_FP, SEP_10_eco_01, SEP_10_cport_eco_01, SEP_10"
    # Use awk to extract only from the "Release Attempts from Workarea" summary section
    local custom_links=$(echo "$release_section" | awk '/Release Attempts from Workarea/,/^[[:space:]]*$/ {print}' | grep -i "Custom Links:" | head -1 | sed 's/.*Custom Links:\s*//')
    
    # Determine overall release status based on attempts
    local overall_status="UNKNOWN"
    
    if [ $total_attempts -eq 0 ]; then
        overall_status="NOT_FOUND"
        details="No release attempts detected"
    elif [ $successful_attempts -gt 0 ] && [ $failed_attempts -eq 0 ]; then
        # All attempts successful
        overall_status="PASSED"
        details="${successful_attempts} successful / ${total_attempts} total attempts"
        
        # Add custom links if available
        if [ -n "$custom_links" ]; then
            # Truncate long custom links list for display
            if [ ${#custom_links} -gt 60 ]; then
                custom_links="${custom_links:0:57}..."
            fi
            details="${details}; Links: ${custom_links}"
        fi
        
    elif [ $successful_attempts -gt 0 ] && [ $failed_attempts -gt 0 ]; then
        # Mixed success and failure - partial success
        overall_status="WARN"
        details="${successful_attempts} successful, ${failed_attempts} failed / ${total_attempts} total"
        
        # Add custom links if available
        if [ -n "$custom_links" ]; then
            if [ ${#custom_links} -gt 50 ]; then
                custom_links="${custom_links:0:47}..."
            fi
            details="${details}; Links: ${custom_links}"
        fi
        
    elif [ $failed_attempts -gt 0 ] && [ $successful_attempts -eq 0 ]; then
        # All attempts failed
        overall_status="FAILED"
        details="All ${failed_attempts} release attempts FAILED"
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

# Export functions and variables for parallel execution
# Note: Must export AFTER functions are defined to avoid warnings
export -f run_unit_analysis
export -f parse_formal_output
export -f parse_timing_output
export -f parse_pv_output
export -f parse_clock_output
export -f parse_release_output
export -f save_state
export -f log_debug
export -f log_verbose
export PYTHON_BIN AVICE_SCRIPT VERBOSE QUIET BLUE MAGENTA NC MAX_RETRIES RETRY_DELAY

# Get section flag for avice_wa_review.py based on regression type
get_analysis_section() {
    case "$REGRESSION_TYPE" in
        formal)
            echo "formal"
            ;;
        timing)
            echo "pt"
            ;;
        pv)
            echo "pv"
            ;;
        clock)
            echo "clock"
            ;;
        release)
            echo "block-release"
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
        *)
            echo "Analysis"
            ;;
    esac
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
    REGRESSION_TYPES=("formal" "timing" "pv" "clock" "release")
    echo ""
fi

# Validate each regression type
for type in "${REGRESSION_TYPES[@]}"; do
    case "$type" in
        formal|timing|pv|clock|release)
            # Valid regression type
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Invalid regression type: $type"
            echo "Valid types: formal, timing, pv, clock, release"
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

while IFS='|' read -r unit chiplet workarea rtl_tag release_types release_date release_user; do
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
    
    UNITS+=("$unit")
    CHIPLETS+=("$chiplet")
    WORKAREAS+=("$workarea")
    RTL_TAGS+=("$rtl_tag")
    RELEASE_DATES+=("$release_date")
    RELEASE_USERS+=("$release_user")
done < "$UNITS_TABLE"

TOTAL_UNITS=${#UNITS[@]}

if [ $TOTAL_UNITS -eq 0 ]; then
    echo -e "${RED}[ERROR]${NC} No units found matching the filter criteria"
    exit 1
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
                    show_progress "$units_completed" "$TOTAL_UNITS" "$unit"
                else
                    echo ""
                    print_section "Unit $((i+1))/$TOTAL_UNITS: $unit ($chiplet)"
                    echo "Workarea: $workarea"
                    echo "Released: ${RELEASE_DATES[$i]} by ${RELEASE_USERS[$i]}"
                    echo ""
                    echo -e "${CYAN}Running $REGRESSION_NAME analysis...${NC}"
                fi
            else
                show_progress "$units_completed" "$TOTAL_UNITS" "$unit"
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
            show_progress "$TOTAL_UNITS" "$TOTAL_UNITS" "All units completed"
            echo ""  # New line after progress bar
        fi
        
        # Collect results from result files
        ANALYSIS_STATUS=()
        ANALYSIS_DETAILS=()
        ANALYSIS_RUNTIMES=()
        ANALYSIS_FLAGS=()
        
        for i in "${!UNITS[@]}"; do
            unit="${UNITS[$i]}"
            result_file="$TEMP_DIR/${unit}_${REGRESSION_TYPE}_result.txt"
            
            if [ -f "$result_file" ]; then
                parse_result=$(cat "$result_file")
                IFS='|' read -r overall_status details runtime flags <<< "$parse_result"
                ANALYSIS_STATUS+=("$overall_status")
                ANALYSIS_DETAILS+=("$details")
                ANALYSIS_RUNTIMES+=("$runtime")
                ANALYSIS_FLAGS+=("$flags")
            else
                ANALYSIS_STATUS+=("ERROR")
                ANALYSIS_DETAILS+=("Result file not found")
                ANALYSIS_RUNTIMES+=("N/A")
                ANALYSIS_FLAGS+=("N/A")
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
    
    .chiplet-header .toggle {
        font-size: 0.8em;
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
    
    .filter-buttons {
        display: flex;
        gap: 10px;
    }
    
    .filter-btn {
        padding: 10px 20px;
        border: 2px solid #667eea;
        background: white;
        color: #667eea;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        white-space: nowrap;
    }
    
    .filter-btn:hover {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    .filter-btn.active {
        background: #667eea;
        color: white;
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
        <img class="logo-modal-content" src="file:///home/avice/scripts/avice_wa_review/images/avice_logo.png" alt="AVICE Logo">
    </div>
    
    <div class="header">
        <img class="header-logo" src="file:///home/avice/scripts/avice_wa_review/images/avice_logo.png" alt="AVICE Logo" onclick="showLogoModal()" title="Click to enlarge">
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
        timing) tab_name="⏱️ Timing" ;;
        pv) tab_name="✓ PV" ;;
        clock) tab_name="🕒 Clock" ;;
        release) tab_name="📦 Release" ;;
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
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterStatus(event, 'all')">All</button>
                <button class="filter-btn" onclick="filterStatus(event, 'passed')">✅ Passed</button>
                <button class="filter-btn" onclick="filterStatus(event, 'failed')">❌ Failed</button>
                <button class="filter-btn" onclick="filterStatus(event, 'warn')">⚠️ Warnings</button>
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
                    <span class="toggle" id="toggle-${REGRESSION_TYPE}_$chiplet">▼</span>
                </div>
                <div class="collapsible-content active" id="content-${REGRESSION_TYPE}_$chiplet">
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
            case "$status" in
                PASSED)
                    status_class="status-passed"
                    status_text="✅ PASSED"
                    ;;
                WARN)
                    status_class="status-unresolved"
                    status_text="⚠️ WARN"
                    ;;
                PARTIAL_PASS)
                    status_class="status-partial"
                    status_text="⚠️ PARTIAL"
                    ;;
                UNRESOLVED)
                    status_class="status-unresolved"
                    status_text="⚠️ UNRESOLVED"
                    ;;
                FAILED)
                    status_class="status-failed"
                    status_text="❌ FAILED"
                    ;;
                CRASHED)
                    status_class="status-crashed"
                    status_text="💥 CRASHED"
                    ;;
                RUNNING)
                    status_class="status-running"
                    status_text="🔄 RUNNING"
                    ;;
                ERROR)
                    status_class="status-error"
                    status_text="⚠️ ERROR"
                    ;;
                NOT_FOUND)
                    status_class="status-notfound"
                    status_text="⏸️ NOT RUN"
                    ;;
                NO_DATA)
                    status_class="status-notfound"
                    status_text="📊 NO DATA"
                    ;;
                MISSING)
                    status_class="status-failed"
                    status_text="🚫 MISSING"
                    ;;
                *)
                    status_class="status-notfound"
                    status_text="❔ UNKNOWN"
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
                    badges="${badges}<span class='release-badge' style='background: #9b59b6; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin: 0 2px;' title='FCL Release'>F</span>"
                fi
                if [[ "$release_flags" =~ pnr_release ]]; then
                    badges="${badges}<span class='release-badge' style='background: #e67e22; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin: 0 2px;' title='PnR Release'>P</span>"
                fi
                if [[ "$release_flags" =~ fe_dct_release ]]; then
                    badges="${badges}<span class='release-badge' style='background: #27ae60; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin: 0 2px;' title='FE DCT Release'>D</span>"
                fi
                
                if [ -n "$badges" ]; then
                    release_badges_html="<div style='display: flex; align-items: center; gap: 4px;'>$badges</div>"
                fi
            fi
            
            cat >> "$HTML_FILE" << UNIT_CARD
                        <div class="unit-card">
                            <div class="unit-header">
                                <div class="unit-name">$unit</div>
                                $release_badges_html
                                <div class="status-badge $status_class">$status_text</div>
                            </div>
                            <div class="unit-info">
                                <div class="info-row">
                                    <span class="info-label">Released By:</span>
                                    <span class="info-value">$release_user</span>
                                </div>
UNIT_CARD
            
            # Calculate release date age and add color coding
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
            
            # Show runtime only for non-formal and non-release types
            # (formal shows runtime per flow, release shows detailed attempt history)
            if [ "$REGRESSION_TYPE" != "formal" ] && [ "$REGRESSION_TYPE" != "release" ]; then
                cat >> "$HTML_FILE" << RUNTIME_SECTION
                                <div class="info-row">
                                    <span class="info-label">Runtime:</span>
                                    <span class="info-value">$runtime</span>
                                </div>
RUNTIME_SECTION
            fi
            
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
            if [ "$REGRESSION_TYPE" = "pv" ]; then
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
                            # Extract both regular and manual custom link details from output file
                            # Combine and sort them by date (oldest first)
                            
                            # Format: "  Custom Link Detail: LINK_NAME|DATE" (exclude Manual Custom Link Detail)
                            custom_link_details=$(grep "Custom Link Detail:" "$TEMP_DIR/${unit}_${REGRESSION_TYPE}_output.txt" 2>/dev/null | grep -v "Manual Custom Link Detail:" | sed 's/.*Custom Link Detail:[[:space:]]*//' | sed 's/\x1b\[[0-9;]*m//g')
                            
                            # Format: "  Manual Custom Link Detail: LINK_NAME|DATE"
                            manual_link_details=$(grep "Manual Custom Link Detail:" "$TEMP_DIR/${unit}_${REGRESSION_TYPE}_output.txt" 2>/dev/null | sed 's/.*Manual Custom Link Detail:[[:space:]]*//' | sed 's/\x1b\[[0-9;]*m//g')
                            
                            # Combine both types with a marker: LINK_NAME|DATE|TYPE
                            all_links=""
                            if [ -n "$custom_link_details" ]; then
                                while IFS='|' read -r link_name link_date; do
                                    all_links="${all_links}${link_name}|${link_date}|regular"$'\n'
                                done <<< "$custom_link_details"
                            fi
                            if [ -n "$manual_link_details" ]; then
                                while IFS='|' read -r link_name link_date; do
                                    all_links="${all_links}${link_name}|${link_date}|manual"$'\n'
                                done <<< "$manual_link_details"
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
                                while IFS='|' read -r link_name link_date link_type; do
                                    link_num=$((link_num + 1))
                                    
                                    # Color coding: 1st=green, 2nd=orange, 3rd=gray
                                    if [ $link_num -eq 1 ]; then
                                        link_color="#27ae60"  # Green - newest
                                    elif [ $link_num -eq 2 ]; then
                                        link_color="#f39c12"  # Orange - 2nd newest
                                    else
                                        link_color="#7f8c8d"  # Gray - 3rd newest
                                    fi
                                    
                                    # Manual badge if applicable
                                    manual_badge=""
                                    if [ "$link_type" = "manual" ]; then
                                        manual_badge=" <span style=\"color: #3498db; font-size: 0.85em;\">Manual</span>"
                                    fi
                                    
                                    cat >> "$HTML_FILE" << COMPACT_LINK
                                    <div style="margin-bottom: 4px;">
                                        • <span style="color: $link_color; font-weight: 500;">$link_name</span> <span style="color: #95a5a6; font-size: 0.9em;">($link_date)</span>$manual_badge
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
                                    while IFS='|' read -r link_name link_date link_type; do
                                        # Manual badge if applicable
                                        manual_badge=""
                                        if [ "$link_type" = "manual" ]; then
                                            manual_badge=" <span style=\"color: #3498db; font-size: 0.85em;\">Manual</span>"
                                        fi
                                        
                                        cat >> "$HTML_FILE" << OLDER_LINK
                                        <div style="margin-bottom: 4px;">
                                            • <span style="color: #7f8c8d; font-weight: 500;">$link_name</span> <span style="color: #95a5a6; font-size: 0.9em;">($link_date)</span>$manual_badge
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
                    
                    echo "                                </div>" >> "$HTML_FILE"
                fi
            else
                # For other types: Display as flows
                if [ "$details" != "No formal flows found" ] && [ "$details" != "No formal flow detected" ]; then
                    cat >> "$HTML_FILE" << FLOWS_START
                            <div class="formal-flows">
                                <div class="flow-title">Formal Flows:</div>
FLOWS_START
                    
                    # Parse details string (format: "flow: STATUS (runtime)")
                    IFS=',' read -ra flows <<< "$details"
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
                        
                        cat >> "$HTML_FILE" << FLOW_ITEM
                                <div class="flow-item $flow_class">
                                    <span>$flow_name</span>
                                    <span>$flow_display</span>
                                </div>
FLOW_ITEM
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
            const filterButtons = document.getElementsByClassName('filter-btn');
            const statCards = document.getElementsByClassName('stat-card');
            
            // Update active button (filter buttons in the bar)
            for (let btn of filterButtons) {
                btn.classList.remove('active');
            }
            
            // Update active stat card (statistics cards at top)
            for (let card of statCards) {
                card.classList.remove('active');
            }
            
            // Add active class to clicked element
            if (evt && evt.target) {
                // If clicked on a child element (like stat-value), find parent stat-card
                let targetElement = evt.target;
                if (!targetElement.classList.contains('stat-card') && !targetElement.classList.contains('filter-btn')) {
                    targetElement = evt.target.closest('.stat-card') || evt.target.closest('.filter-btn');
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
        } catch (e) {
            console.error('Error in filterStatus:', e);
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

