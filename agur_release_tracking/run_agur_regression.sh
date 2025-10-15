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
#   -c, --chiplet CHIPLET    Filter by chiplet (default: all chiplets)
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
REGRESSION_TYPE=""  # formal, timing, pv, clock, release

# Output files (generated in user's current working directory)
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
TEMP_DIR="/tmp/agur_regression_$$"

# Filters
FILTER_CHIPLET=""
FILTER_UNIT=""

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

#===============================================================================
# Functions
#===============================================================================

show_help() {
    cat << EOF
Usage: $0 -t TYPE [options]

Run various analysis regressions on all released AGUR units.

Required Options:
  -t, --type TYPE          Regression type (REQUIRED)
                           Options: formal, timing, pv, clock, release

Optional Filters:
  -c, --chiplet CHIPLET    Filter by chiplet (e.g., CPORT)
  -u, --unit UNIT          Run for specific unit only
  -h, --help               Show this help message

Examples:
  $0 -t formal             # Run formal regression on all units
  $0 -t formal -c CPORT    # Run formal on CPORT units only
  $0 -t timing -u prt      # Run timing regression on prt unit only
  $0 -t pv                 # Run PV regression on all units
  $0 -t clock              # Run clock analysis on all units
  $0 -t release            # Run block release check on all units

Regression Types:
  formal    - Formal verification status (RTL vs PNR/Synthesis)
  timing    - PT signoff timing analysis (WNS, TNS, paths)
  pv        - Physical verification (DRC, LVS, Antenna)
  clock     - Clock tree analysis (latency, skew)
  release   - Block release status and completeness

Output Files (generated in current directory):
  agur_<type>_regression_dashboard_YYYYMMDD_HHMMSS.html  (HTML dashboard)

EOF
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
    
    # Extract status for each formal flow
    local rtl_vs_pnr_status=""
    local rtl_vs_pnr_bbox_status=""
    local rtl_vs_syn_status=""
    local rtl_vs_syn_bbox_status=""
    
    while IFS= read -r line; do
        if [[ "$line" == *"rtl_vs_pnr_fm/log/rtl_vs_pnr_fm.log"* ]]; then
            read -r status_line
            rtl_vs_pnr_status=$(echo "$status_line" | grep -oP "(SUCCEEDED|FAILED|CRASHED|RUNNING|UNRESOLVED)" | head -1)
        elif [[ "$line" == *"rtl_vs_pnr_bbox_fm/log/rtl_vs_pnr_bbox_fm.log"* ]]; then
            read -r status_line
            rtl_vs_pnr_bbox_status=$(echo "$status_line" | grep -oP "(SUCCEEDED|FAILED|CRASHED|RUNNING|UNRESOLVED)" | head -1)
        elif [[ "$line" == *"rtl_vs_syn_fm/log/rtl_vs_syn_fm.log"* ]]; then
            read -r status_line
            rtl_vs_syn_status=$(echo "$status_line" | grep -oP "(SUCCEEDED|FAILED|CRASHED|RUNNING|UNRESOLVED)" | head -1)
        elif [[ "$line" == *"rtl_vs_syn_bbox_fm/log/rtl_vs_syn_bbox_fm.log"* ]]; then
            read -r status_line
            rtl_vs_syn_bbox_status=$(echo "$status_line" | grep -oP "(SUCCEEDED|FAILED|CRASHED|RUNNING|UNRESOLVED)" | head -1)
        fi
    done <<< "$formal_section"
    
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
    
    # Extract runtime
    runtime=$(echo "$formal_section" | grep "Runtime:" | head -1 | grep -oP "Runtime: \K[0-9.]+ (hours|minutes)")
    [ -z "$runtime" ] && runtime="N/A"
    
    # Build details string
    details=""
    [ -n "$rtl_vs_pnr_bbox_status" ] && details="${details}rtl_vs_pnr_bbox: $rtl_vs_pnr_bbox_status, "
    [ -n "$rtl_vs_pnr_status" ] && details="${details}rtl_vs_pnr: $rtl_vs_pnr_status, "
    [ -n "$rtl_vs_syn_status" ] && details="${details}rtl_vs_syn: $rtl_vs_syn_status, "
    [ -n "$rtl_vs_syn_bbox_status" ] && details="${details}rtl_vs_syn_bbox: $rtl_vs_syn_bbox_status"
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
    
    # Extract PT Signoff Timing section
    local timing_section=$(grep -A 200 "PT Signoff Timing Analysis" "$output_file")
    
    if [ -z "$timing_section" ]; then
        echo "NOT_FOUND|No PT timing analysis found|N/A"
        return
    fi
    
    # Check for "No PT signoff timing" message
    if echo "$timing_section" | grep -q "No PT signoff timing"; then
        echo "NOT_FOUND|No PT timing analysis found|N/A"
        return
    fi
    
    # Extract key timing metrics
    local wns=$(echo "$timing_section" | grep -i "Worst Negative Slack (WNS)" | grep -oP "[-+]?[0-9]*\.?[0-9]+" | head -1)
    local tns=$(echo "$timing_section" | grep -i "Total Negative Slack (TNS)" | grep -oP "[-+]?[0-9]*\.?[0-9]+" | head -1)
    local nvp=$(echo "$timing_section" | grep -i "Number of Violating Paths" | grep -oP "[0-9]+" | head -1)
    
    # Alternative patterns for WNS/TNS extraction
    if [ -z "$wns" ]; then
        wns=$(echo "$timing_section" | grep -i "WNS:" | grep -oP "WNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
    fi
    if [ -z "$tns" ]; then
        tns=$(echo "$timing_section" | grep -i "TNS:" | grep -oP "TNS:\s*\K[-+]?[0-9]*\.?[0-9]+" | head -1)
    fi
    
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
        
        if [ "$wns_check" = "PASS" ]; then
            overall_status="PASSED"
            details="WNS: ${wns}ps, TNS: ${tns}ps"
            [ "$nvp" != "N/A" ] && details="${details}, Violating Paths: ${nvp}"
        else
            # Check severity of violation
            local wns_abs=$(echo "$wns" | tr -d '-')
            local is_critical=$(echo "$wns_abs 50" | awk '{if ($1 > $2) print "YES"; else print "NO"}')
            
            if [ "$is_critical" = "YES" ]; then
                overall_status="FAILED"
            else
                overall_status="WARN"
            fi
            details="WNS: ${wns}ps (VIOLATION), TNS: ${tns}ps"
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
    
    # Extract runtime if available
    runtime=$(echo "$pv_section" | grep -i "Runtime:" | head -1 | grep -oP "Runtime:\s*\K[0-9.]+ (hours|minutes|seconds)")
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
    
    # Extract clock metrics - try multiple patterns
    local max_latency=$(echo "$clock_section" | grep -i "Maximum.*latency\|Max.*latency" | grep -oP "[0-9]*\.?[0-9]+" | head -1)
    local clock_skew=$(echo "$clock_section" | grep -i "Clock skew\|Skew" | grep -oP "[0-9]*\.?[0-9]+" | head -1)
    local insertion_delay=$(echo "$clock_section" | grep -i "Insertion delay" | grep -oP "[0-9]*\.?[0-9]+" | head -1)
    
    # Alternative patterns
    if [ -z "$max_latency" ]; then
        max_latency=$(echo "$clock_section" | grep -i "Latency:" | grep -oP "Latency:\s*\K[0-9]*\.?[0-9]+" | head -1)
    fi
    if [ -z "$clock_skew" ]; then
        clock_skew=$(echo "$clock_section" | grep -i "Skew:" | grep -oP "Skew:\s*\K[0-9]*\.?[0-9]+" | head -1)
    fi
    
    # Set defaults if extraction failed
    [ -z "$max_latency" ] && max_latency="N/A"
    [ -z "$clock_skew" ] && clock_skew="N/A"
    [ -z "$insertion_delay" ] && insertion_delay="N/A"
    
    # Determine overall clock status
    local overall_status="UNKNOWN"
    
    if [ "$max_latency" = "N/A" ] && [ "$clock_skew" = "N/A" ]; then
        overall_status="NO_DATA"
        details="No clock data available"
    elif [ "$max_latency" != "N/A" ]; then
        # Evaluate clock quality based on latency (thresholds in ps)
        # PASSED: latency <= 550ps
        # WARN: 550ps < latency < 580ps
        # FAILED: latency >= 580ps
        
        local lat_check=$(echo "$max_latency 550" | awk '{if ($1 <= $2) print "PASS"; else if ($1 < 580) print "WARN"; else print "FAIL"}')
        
        if [ "$lat_check" = "PASS" ]; then
            overall_status="PASSED"
            details="Max Latency: ${max_latency}ps, Skew: ${clock_skew}ps"
        elif [ "$lat_check" = "WARN" ]; then
            overall_status="WARN"
            details="Max Latency: ${max_latency}ps (HIGH), Skew: ${clock_skew}ps"
        else
            overall_status="FAILED"
            details="Max Latency: ${max_latency}ps (CRITICAL), Skew: ${clock_skew}ps"
        fi
        
        [ "$insertion_delay" != "N/A" ] && details="${details}, Insertion: ${insertion_delay}ps"
    else
        overall_status="UNKNOWN"
        details="Unable to determine clock status"
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
    
    # Extract Block Release section
    local release_section=$(grep -A 200 "Block Release\|Release Status\|Release Check" "$output_file")
    
    if [ -z "$release_section" ]; then
        echo "NOT_FOUND|No block release information found|N/A"
        return
    fi
    
    # Check for "No release" message
    if echo "$release_section" | grep -q "No release.*found\|No block release"; then
        echo "NOT_FOUND|No block release found|N/A"
        return
    fi
    
    # Extract release information - try multiple patterns
    local release_type=$(echo "$release_section" | grep -i "Release type\|Type:" | head -1)
    local release_date=$(echo "$release_section" | grep -i "Release date\|Date:" | head -1)
    local release_complete=$(echo "$release_section" | grep -i "Completeness\|Complete:" | head -1)
    
    # Check for specific release flags
    local has_sta=$(echo "$release_section" | grep -i "STA.*release\|Sta:.*True" | head -1)
    local has_fcl=$(echo "$release_section" | grep -i "FCL.*release\|Fcl:.*True" | head -1)
    local has_pnr=$(echo "$release_section" | grep -i "PNR.*release\|Pnr:.*True" | head -1)
    
    # Count release types
    local release_count=0
    [ -n "$has_sta" ] && release_count=$((release_count + 1))
    [ -n "$has_fcl" ] && release_count=$((release_count + 1))
    [ -n "$has_pnr" ] && release_count=$((release_count + 1))
    
    # Determine overall release status
    local overall_status="UNKNOWN"
    
    if [ -z "$release_type" ] && [ -z "$release_date" ]; then
        overall_status="NO_DATA"
        details="No release data available"
    elif [ $release_count -gt 0 ]; then
        # Build release types string
        local types=""
        [ -n "$has_sta" ] && types="${types}STA, "
        [ -n "$has_fcl" ] && types="${types}FCL, "
        [ -n "$has_pnr" ] && types="${types}PNR, "
        types=${types%, }  # Remove trailing comma
        
        # Check if release is complete (all 3 types present)
        if [ $release_count -ge 3 ]; then
            overall_status="PASSED"
            details="Complete release: ${types}"
        elif [ $release_count -eq 2 ]; then
            overall_status="PARTIAL_PASS"
            details="Partial release: ${types}"
        else
            overall_status="WARN"
            details="Minimal release: ${types}"
        fi
        
        # Add date if found
        if [ -n "$release_date" ]; then
            local date_str=$(echo "$release_date" | grep -oP "[0-9]{4}[/-][0-9]{1,2}[/-][0-9]{1,2}" | head -1)
            [ -n "$date_str" ] && details="${details} (${date_str})"
        fi
    else
        # No clear release types found, try to determine from content
        if echo "$release_section" | grep -qi "complete\|success"; then
            overall_status="PASSED"
            details="Release found and appears complete"
        elif echo "$release_section" | grep -qi "incomplete\|partial"; then
            overall_status="WARN"
            details="Release found but may be incomplete"
        else
            overall_status="UNKNOWN"
            details="Release status unclear"
        fi
    fi
    
    # Extract runtime if available
    runtime=$(echo "$release_section" | grep -i "Runtime:" | head -1 | grep -oP "Runtime:\s*\K[0-9.]+ (hours|minutes|seconds)")
    [ -z "$runtime" ] && runtime="N/A"
    
    # Return pipe-delimited string
    echo "${overall_status}|${details}|${runtime}"
}

# Get section flag for avice_wa_review.py based on regression type
get_analysis_section() {
    case "$REGRESSION_TYPE" in
        formal)
            echo "formal"
            ;;
        timing)
            echo "timing"
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
            REGRESSION_TYPE="$2"
            shift 2
            ;;
        -c|--chiplet)
            FILTER_CHIPLET="$2"
            shift 2
            ;;
        -u|--unit)
            FILTER_UNIT="$2"
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

# Validate regression type
if [ -z "$REGRESSION_TYPE" ]; then
    echo -e "${RED}[ERROR]${NC} Regression type (-t) is required"
    echo ""
    show_help
fi

case "$REGRESSION_TYPE" in
    formal|timing|pv|clock|release)
        # Valid regression type
        ;;
    *)
        echo -e "${RED}[ERROR]${NC} Invalid regression type: $REGRESSION_TYPE"
        echo "Valid types: formal, timing, pv, clock, release"
        echo ""
        show_help
        ;;
esac

# Set HTML output filename based on regression type
HTML_FILE="agur_${REGRESSION_TYPE}_regression_dashboard_${TIMESTAMP}.html"

#===============================================================================
# Main Script
#===============================================================================

print_header

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
    if [ -n "$FILTER_CHIPLET" ] && [ "$chiplet" != "$FILTER_CHIPLET" ]; then
        continue
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

echo -e "${GREEN}Found $TOTAL_UNITS unit(s) to analyze${NC}"
if [ -n "$FILTER_CHIPLET" ]; then
    echo "Filter: Chiplet = $FILTER_CHIPLET"
fi
if [ -n "$FILTER_UNIT" ]; then
    echo "Filter: Unit = $FILTER_UNIT"
fi
echo ""

# Arrays to store results (generic for all regression types)
declare -a ANALYSIS_STATUS
declare -a ANALYSIS_DETAILS
declare -a ANALYSIS_RUNTIMES

# Get analysis section name
ANALYSIS_SECTION=$(get_analysis_section)
REGRESSION_NAME=$(get_regression_name)

# Run analysis on each unit
print_section "Running $REGRESSION_NAME Analysis"
echo ""

for i in "${!UNITS[@]}"; do
    unit="${UNITS[$i]}"
    chiplet="${CHIPLETS[$i]}"
    workarea="${WORKAREAS[$i]}"
    release_date="${RELEASE_DATES[$i]}"
    release_user="${RELEASE_USERS[$i]}"
    
    echo ""
    print_section "Unit $((i+1))/$TOTAL_UNITS: $unit ($chiplet)"
    echo "Workarea: $workarea"
    echo "Released: $release_date by $release_user"
    echo ""
    
    # Check if workarea exists
    if [ ! -d "$workarea" ]; then
        echo -e "${RED}[ERROR]${NC} Workarea does not exist"
        ANALYSIS_STATUS+=("ERROR")
        ANALYSIS_DETAILS+=("Workarea not found")
        ANALYSIS_RUNTIMES+=("N/A")
        continue
    fi
    
    # Run analysis
    echo -e "${CYAN}Running $REGRESSION_NAME analysis...${NC}"
    
    OUTPUT_FILE="$TEMP_DIR/${unit}_${REGRESSION_TYPE}_output.txt"
    
    "$PYTHON_BIN" "$AVICE_SCRIPT" "$workarea" -s "$ANALYSIS_SECTION" --no-logo > "$OUTPUT_FILE" 2>&1
    EXIT_CODE=$?
    
    # Parse output based on regression type
    if [ $EXIT_CODE -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Analysis failed (exit code: $EXIT_CODE)"
        ANALYSIS_STATUS+=("ERROR")
        ANALYSIS_DETAILS+=("Script execution failed")
        ANALYSIS_RUNTIMES+=("N/A")
    else
        # Call appropriate parser function based on regression type
        parse_result=""
        case "$REGRESSION_TYPE" in
            formal)
                parse_result=$(parse_formal_output "$OUTPUT_FILE")
                ;;
            timing)
                parse_result=$(parse_timing_output "$OUTPUT_FILE")
                ;;
            pv)
                parse_result=$(parse_pv_output "$OUTPUT_FILE")
                ;;
            clock)
                parse_result=$(parse_clock_output "$OUTPUT_FILE")
                ;;
            release)
                parse_result=$(parse_release_output "$OUTPUT_FILE")
                ;;
            *)
                parse_result="ERROR|Unknown regression type|N/A"
                ;;
        esac
        
        # Parse the pipe-delimited result: status|details|runtime
        IFS='|' read -r overall_status details runtime <<< "$parse_result"
        
        # Add to arrays
        ANALYSIS_STATUS+=("$overall_status")
        ANALYSIS_DETAILS+=("$details")
        ANALYSIS_RUNTIMES+=("$runtime")
        
        # Determine status color for console output
        status_color="${YELLOW}"
        case "$overall_status" in
            PASSED)
                status_color="${GREEN}"
                ;;
            FAILED|CRASHED|ERROR)
                status_color="${RED}"
                ;;
            *)
                status_color="${YELLOW}"
                ;;
        esac
        
        echo -e "${status_color}Status: $overall_status${NC}"
        echo "Details: $details"
        echo "Runtime: $runtime"
    fi
done

# Calculate statistics for HTML dashboard
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

#===============================================================================
# Generate HTML Dashboard
#===============================================================================

print_section "Generating HTML Dashboard"

# Read and encode logo as base64 for HTML embedding (portability)
LOGO_DATA=""
LOGO_PATH="/home/avice/scripts/avice_wa_review/images/avice_logo.png"
if [ -f "$LOGO_PATH" ]; then
    LOGO_DATA=$(base64 -w 0 "$LOGO_PATH")
fi

# Generate HTML with embedded CSS and JavaScript
# Generate dynamic title based on regression type
case "$REGRESSION_TYPE" in
    formal)
        HTML_TITLE="AGUR Formal Verification Regression Dashboard"
        HTML_ICON="🔍"
        ;;
    timing)
        HTML_TITLE="AGUR PT Signoff Timing Regression Dashboard"
        HTML_ICON="⏱️"
        ;;
    pv)
        HTML_TITLE="AGUR Physical Verification Regression Dashboard"
        HTML_ICON="✓"
        ;;
    clock)
        HTML_TITLE="AGUR Clock Tree Analysis Regression Dashboard"
        HTML_ICON="🕒"
        ;;
    release)
        HTML_TITLE="AGUR Block Release Status Regression Dashboard"
        HTML_ICON="📦"
        ;;
    *)
        HTML_TITLE="AGUR Regression Dashboard"
        HTML_ICON="📊"
        ;;
esac

cat > "$HTML_FILE" << 'HTML_START'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
HTML_START

cat >> "$HTML_FILE" << EOF
    <title>$HTML_TITLE</title>
    <style>
EOF

cat >> "$HTML_FILE" << 'HTML_STYLE'
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
        }
        
        .header-content {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 25px;
            align-items: center;
        }
        
        .logo {
            width: 100px;
            height: 100px;
            border-radius: 10px;
            background: white;
            padding: 10px;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .logo:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0,0,0,0.5);
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
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.9);
            cursor: pointer;
        }
        
        .logo-modal-content {
            margin: auto;
            display: block;
            max-width: 80%;
            max-height: 80%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        
        .logo-modal-close {
            position: absolute;
            top: 30px;
            right: 50px;
            color: #f1f1f1;
            font-size: 50px;
            font-weight: bold;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-passed { color: #28a745; }
        .stat-partial { color: #ffc107; }
        .stat-unresolved { color: #ff9800; }
        .stat-failed { color: #dc3545; }
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: bold;
            transition: all 0.3s ease;
            white-space: nowrap;
        }
        
        .copy-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        }
        
        .copy-btn:active {
            transform: scale(0.95);
        }
        
        .copy-btn.copied {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        
        .info-label {
            color: #666;
            font-weight: 600;
        }
        
        .info-value {
            color: #333;
        }
        
        .formal-flows {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
        }
        
        .flow-title {
            font-weight: bold;
            color: #666;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        
        .flow-item {
            padding: 5px 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 0.85em;
            display: flex;
            justify-content: space-between;
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
        
        #backToTopBtn {
            display: none;
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
        }
        
        #backToTopBtn:hover {
            background-color: #5568d3;
            transform: scale(1.1);
        }
        
        .collapsible-content {
            display: none;
            overflow: hidden;
        }
        
        .collapsible-content.active {
            display: block;
        }
HTML_STYLE

cat >> "$HTML_FILE" << 'HTML_END_STYLE'
    </style>
</head>
<body>
HTML_END_STYLE

# Add logo modal and header
if [ -n "$LOGO_DATA" ]; then
    cat >> "$HTML_FILE" << EOF
    <!-- Logo Modal -->
    <div id="logoModal" class="logo-modal" onclick="hideLogoModal()">
        <span class="logo-modal-close">&times;</span>
        <img class="logo-modal-content" id="logoModalImg">
    </div>
    
    <div class="container">
        <div class="header">
            <div class="header-content">
                <img class="logo" src="data:image/png;base64,$LOGO_DATA" alt="AVICE Logo" onclick="showLogoModal()" title="Click to enlarge">
                <div>
                    <h1>$HTML_ICON $HTML_TITLE</h1>
EOF
else
    cat >> "$HTML_FILE" << EOF
    <div class="container">
        <div class="header">
            <h1>$HTML_ICON $HTML_TITLE</h1>
EOF
fi

# Add generation timestamp and filter info
if [ -n "$LOGO_DATA" ]; then
    cat >> "$HTML_FILE" << HTML_META
                    <div class="subtitle">Generated: $(date '+%Y-%m-%d %H:%M:%S')</div>
HTML_META
    
    if [ -n "$FILTER_CHIPLET" ]; then
        echo "                    <div class=\"subtitle\">Filter: Chiplet = $FILTER_CHIPLET</div>" >> "$HTML_FILE"
    fi
    if [ -n "$FILTER_UNIT" ]; then
        echo "                    <div class=\"subtitle\">Filter: Unit = $FILTER_UNIT</div>" >> "$HTML_FILE"
    fi
    
    # Close the nested divs for logo layout (close text div, header-content, and header)
    cat >> "$HTML_FILE" << 'EOF'
                </div>
            </div>
        </div>
EOF
else
    cat >> "$HTML_FILE" << HTML_META
            <div class="subtitle">Generated: $(date '+%Y-%m-%d %H:%M:%S')</div>
HTML_META
    
    if [ -n "$FILTER_CHIPLET" ]; then
        echo "            <div class=\"subtitle\">Filter: Chiplet = $FILTER_CHIPLET</div>" >> "$HTML_FILE"
    fi
    if [ -n "$FILTER_UNIT" ]; then
        echo "            <div class=\"subtitle\">Filter: Unit = $FILTER_UNIT</div>" >> "$HTML_FILE"
    fi
    
    # Close the header div
    cat >> "$HTML_FILE" << 'EOF'
        </div>
EOF
fi

cat >> "$HTML_FILE" << 'HTML_CONTINUE'
        
        <!-- Statistics Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Units</div>
HTML_CONTINUE

echo "                <div class=\"stat-value\">$TOTAL_UNITS</div>" >> "$HTML_FILE"

cat >> "$HTML_FILE" << 'HTML_STATS'
            </div>
            <div class="stat-card">
                <div class="stat-label">✅ Passed</div>
HTML_STATS

echo "                <div class=\"stat-value stat-passed\">$passed_count</div>" >> "$HTML_FILE"
echo "                <div class=\"stat-label\">$(( passed_count * 100 / TOTAL_UNITS ))%</div>" >> "$HTML_FILE"

cat >> "$HTML_FILE" << 'HTML_STATS_WARN'
            </div>
            <div class="stat-card">
                <div class="stat-label">⚠️ Warnings</div>
HTML_STATS_WARN

echo "                <div class=\"stat-value stat-unresolved\">$warn_count</div>" >> "$HTML_FILE"
echo "                <div class=\"stat-label\">$(( warn_count * 100 / TOTAL_UNITS ))%</div>" >> "$HTML_FILE"

cat >> "$HTML_FILE" << 'HTML_STATS2'
            </div>
            <div class="stat-card">
                <div class="stat-label">⚠️ Unresolved</div>
HTML_STATS2

echo "                <div class=\"stat-value stat-unresolved\">$unresolved_count</div>" >> "$HTML_FILE"
echo "                <div class=\"stat-label\">$(( unresolved_count * 100 / TOTAL_UNITS ))%</div>" >> "$HTML_FILE"

cat >> "$HTML_FILE" << 'HTML_STATS3'
            </div>
            <div class="stat-card">
                <div class="stat-label">❌ Failed</div>
HTML_STATS3

echo "                <div class=\"stat-value stat-failed\">$failed_count</div>" >> "$HTML_FILE"
echo "                <div class=\"stat-label\">$(( failed_count * 100 / TOTAL_UNITS ))%</div>" >> "$HTML_FILE"

cat >> "$HTML_FILE" << 'HTML_STATS4'
            </div>
            <div class="stat-card">
                <div class="stat-label">💥 Crashed</div>
HTML_STATS4

echo "                <div class=\"stat-value stat-crashed\">$crashed_count</div>" >> "$HTML_FILE"
echo "                <div class=\"stat-label\">$(( crashed_count * 100 / TOTAL_UNITS ))%</div>" >> "$HTML_FILE"

cat >> "$HTML_FILE" << 'HTML_CONTENT_START'
            </div>
        </div>
        
        <div class="content">
HTML_CONTENT_START

# Group units by chiplet
declare -A chiplet_units

for i in "${!UNITS[@]}"; do
    unit="${UNITS[$i]}"
    chiplet="${CHIPLETS[$i]}"
    
    if [ -z "${chiplet_units[$chiplet]}" ]; then
        chiplet_units[$chiplet]="$i"
    else
        chiplet_units[$chiplet]="${chiplet_units[$chiplet]},$i"
    fi
done

# Generate HTML for each chiplet
for chiplet in "${!chiplet_units[@]}"; do
    unit_indices="${chiplet_units[$chiplet]}"
    
    # Count units in this chiplet
    IFS=',' read -ra indices <<< "$unit_indices"
    chiplet_unit_count=${#indices[@]}
    
    cat >> "$HTML_FILE" << CHIPLET_SECTION
            <div class="chiplet-section">
                <div class="chiplet-header" onclick="toggleChiplet('$chiplet')">
                    <span>$chiplet Chiplet ($chiplet_unit_count units)</span>
                    <span class="toggle" id="toggle-$chiplet">▼</span>
                </div>
                <div class="collapsible-content active" id="content-$chiplet">
                    <div class="units-grid">
CHIPLET_SECTION
    
    # Add units for this chiplet
    for idx in "${indices[@]}"; do
        unit="${UNITS[$idx]}"
        status="${ANALYSIS_STATUS[$idx]}"
        details="${ANALYSIS_DETAILS[$idx]}"
        runtime="${ANALYSIS_RUNTIMES[$idx]}"
        release_date="${RELEASE_DATES[$idx]}"
        release_user="${RELEASE_USERS[$idx]}"
        workarea="${WORKAREAS[$idx]}"
        rtl_tag="${RTL_TAGS[$idx]}"
        
        # Determine status class and display text
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
                status_text="❓ NOT FOUND"
                ;;
            *)
                status_class="status-notfound"
                status_text="❔ UNKNOWN"
                ;;
        esac
        
        cat >> "$HTML_FILE" << UNIT_CARD
                        <div class="unit-card">
                            <div class="unit-header">
                                <div class="unit-name">$unit</div>
                                <div class="status-badge $status_class">$status_text</div>
                            </div>
                            <div class="unit-info">
                                <div class="info-row">
                                    <span class="info-label">Released By:</span>
                                    <span class="info-value">$release_user</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Release Date:</span>
                                    <span class="info-value">$release_date</span>
                                </div>
                                <div class="info-row workarea-row">
                                    <span class="info-label">RTL Tag:</span>
                                    <span class="info-value workarea-path" id="rtl-$unit">$rtl_tag</span>
                                    <button class="copy-btn" onclick="copyToClipboard('rtl-$unit', this)" title="Copy RTL tag">
                                        📋 Copy
                                    </button>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">Runtime:</span>
                                    <span class="info-value">$runtime</span>
                                </div>
                                <div class="info-row workarea-row">
                                    <span class="info-label">Workarea:</span>
                                    <span class="info-value workarea-path" id="wa-$unit">$workarea</span>
                                    <button class="copy-btn" onclick="copyToClipboard('wa-$unit', this)" title="Copy workarea path">
                                        📋 Copy
                                    </button>
                                </div>
                            </div>
UNIT_CARD
        
        # Parse and display formal flows
        if [ "$details" != "No formal flows found" ] && [ "$details" != "No formal flow detected" ]; then
            cat >> "$HTML_FILE" << FLOWS_START
                            <div class="formal-flows">
                                <div class="flow-title">Formal Flows:</div>
FLOWS_START
            
            # Parse details string (format: "flow1: STATUS, flow2: STATUS, ...")
            IFS=',' read -ra flows <<< "$details"
            for flow_info in "${flows[@]}"; do
                flow_info=$(echo "$flow_info" | xargs)  # trim whitespace
                flow_name=$(echo "$flow_info" | cut -d':' -f1 | xargs)
                flow_status=$(echo "$flow_info" | cut -d':' -f2 | xargs)
                
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
                
                cat >> "$HTML_FILE" << FLOW_ITEM
                                <div class="flow-item $flow_class">
                                    <span>$flow_name</span>
                                    <span>$flow_icon $flow_status</span>
                                </div>
FLOW_ITEM
            done
            
            echo "                            </div>" >> "$HTML_FILE"
        fi
        
        echo "                        </div>" >> "$HTML_FILE"
    done
    
    cat >> "$HTML_FILE" << CHIPLET_END
                    </div>
                </div>
            </div>
CHIPLET_END
done

# Close HTML and add JavaScript
cat >> "$HTML_FILE" << 'HTML_END'
        </div>
        
        <!-- Copyright Footer -->
        <div class="footer">
            <p><strong>AVICE Formal Regression Dashboard</strong></p>
            <p>Copyright (c) 2025 Alon Vice (avice)</p>
            <p>Contact: avice@nvidia.com</p>
        </div>
    </div>
    
    <!-- Back to Top Button -->
    <button id="backToTopBtn" onclick="scrollToTop()">↑ Top</button>
    
    <script>
        // Toggle chiplet sections
        function toggleChiplet(chiplet) {
            const content = document.getElementById('content-' + chiplet);
            const toggle = document.getElementById('toggle-' + chiplet);
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                toggle.textContent = '▶';
            } else {
                content.classList.add('active');
                toggle.textContent = '▼';
            }
        }
        
        // Back to top functionality
        const backToTopBtn = document.getElementById('backToTopBtn');
        
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
        
        function scrollToTop() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        // Logo modal functionality
        function showLogoModal() {
            const modal = document.getElementById('logoModal');
            const modalImg = document.getElementById('logoModalImg');
            const logo = document.querySelector('.logo');
            
            if (modal && modalImg && logo) {
                modal.style.display = 'block';
                modalImg.src = logo.src;
            }
        }
        
        function hideLogoModal() {
            const modal = document.getElementById('logoModal');
            if (modal) {
                modal.style.display = 'none';
            }
        }
        
        // Copy workarea path to clipboard
        function copyToClipboard(elementId, button) {
            const element = document.getElementById(elementId);
            const text = element.textContent;
            
            // Use modern clipboard API
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function() {
                    // Success feedback
                    const originalText = button.innerHTML;
                    button.innerHTML = '✅ Copied!';
                    button.classList.add('copied');
                    
                    setTimeout(function() {
                        button.innerHTML = originalText;
                        button.classList.remove('copied');
                    }, 2000);
                }).catch(function(err) {
                    console.error('Failed to copy: ', err);
                    alert('Failed to copy to clipboard');
                });
            } else {
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy');
                    const originalText = button.innerHTML;
                    button.innerHTML = '✅ Copied!';
                    button.classList.add('copied');
                    
                    setTimeout(function() {
                        button.innerHTML = originalText;
                        button.classList.remove('copied');
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy: ', err);
                    alert('Failed to copy to clipboard');
                }
                document.body.removeChild(textarea);
            }
        }
    </script>
</body>
</html>
HTML_END

echo "HTML dashboard generated: $HTML_FILE"

# Cleanup temp directory
rm -rf "$TEMP_DIR"

#===============================================================================
# Final Summary
#===============================================================================

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
echo -e "  - ${YELLOW}Not Found: $not_found_count${NC}"
echo ""
echo "Output File:"
echo "  - HTML Dashboard: $HTML_FILE"
echo ""
echo -e "${CYAN}===============================================================================${NC}"

# Exit with appropriate code
if [ $failed_count -gt 0 ] || [ $crashed_count -gt 0 ] || [ $error_count -gt 0 ]; then
    exit 1
else
    exit 0
fi

