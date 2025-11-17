# AGUR Regression Framework Guide

## Overview

The AGUR regression framework automatically tests all released AGUR unit workareas for various analysis types. It reads the `AGUR_UNITS_TABLE.txt`, runs the specified analysis on each workarea, and generates comprehensive HTML dashboards with statistics and status information.

---

## Supported Regression Types

| Type | Icon | Analysis | Sections Analyzed |
|------|------|----------|-------------------|
| **formal** | 🔍 | Formal Verification | RTL vs PNR/Synthesis formal verification flows |
| **timing** | ⏱️ | PT Signoff Timing | WNS, TNS, timing paths, DSR skew |
| **pv** | ✓ | Physical Verification | DRC, LVS, Antenna violations |
| **clock** | 🕒 | Clock Tree Analysis | Clock latency, skew, insertion delay |
| **release** | 📦 | Block Release Status | Release completeness and validation |
| **glcheck** | 🔧 | GL Check Analysis | Gate-level check errors (waived vs non-waived) |

---

## Quick Start

```bash
cd /home/avice/scripts/avice_wa_review/agur_release_tracking

# Run formal verification regression on all units
./run_agur_regression.sh -t formal

# Run timing regression on CPORT chiplet only
./run_agur_regression.sh -t timing -c CPORT

# Run PV regression on specific unit
./run_agur_regression.sh -t pv -u prt

# Run clock analysis regression
./run_agur_regression.sh -t clock

# Run block release status check
./run_agur_regression.sh -t release

# Run GL Check regression on all units
./run_agur_regression.sh -t glcheck
```

---

## Command Line Options

### Required Options

| Option | Description | Example |
|--------|-------------|---------|
| `-t, --type TYPE` | **Regression type (REQUIRED)** | `-t formal` |

Valid types: `formal`, `timing`, `pv`, `clock`, `release`, `glcheck`

### Optional Filters

| Option | Description | Example |
|--------|-------------|---------|
| `-c, --chiplet CHIPLET` | Filter by chiplet | `-c CPORT` |
| `-u, --unit UNIT` | Run for specific unit only | `-u prt` |
| `-h, --help` | Show help message | `--help` |

---

## Regression Types Details

### 1. Formal Verification (`-t formal`)

**Purpose**: Check RTL vs netlist formal verification status

**Status Indicators**:
- **PASSED** ✅: All PNR formal flows succeeded
- **PARTIAL_PASS** ⚠️: Some formal flows succeeded  
- **UNRESOLVED** ⚠️: Formal completed with unmatched points
- **FAILED** ❌: Formal completed with errors
- **CRASHED** 💥: Formal tool crashed during run
- **RUNNING** 🔄: Formal verification still running

**Flows Detected**:
- `rtl_vs_pnr_fm` - RTL vs PNR netlist (primary)
- `rtl_vs_pnr_bbox_fm` - RTL vs PNR with black boxes (primary)
- `rtl_vs_syn_fm` - RTL vs Synthesis netlist (secondary)
- `rtl_vs_syn_bbox_fm` - RTL vs Synthesis with black boxes (secondary)

**Example**:
```bash
./run_agur_regression.sh -t formal -c CPORT
```

---

### 2. PT Signoff Timing (`-t timing`)

**Purpose**: Analyze PT signoff timing across all units

**Metrics Tracked**:
- Worst Negative Slack (WNS)
- Total Negative Slack (TNS)
- Number of Violating Paths (NVP)
- DSR mux clock skew
- Timing path groups status

**Status Indicators**:
- **PASSED** ✅: No timing violations
- **WARN** ⚠️: Minor violations or warnings
- **FAILED** ❌: Critical timing failures

**Example**:
```bash
./run_agur_regression.sh -t timing
```

---

### 3. Physical Verification (`-t pv`)

**Purpose**: Check DRC, LVS, and Antenna violations

**Metrics Tracked**:
- DRC violation count
- LVS failures
- Antenna violations

**Status Indicators**:
- **PASSED** ✅: All violations = 0
- **WARN** ⚠️: Some violations exist
- **FAILED** ❌: Critical violations (LVS > 5, DRC > 100, Antenna > 10)

**Example**:
```bash
./run_agur_regression.sh -t pv -c CPORT
```

---

### 4. Clock Tree Analysis (`-t clock`)

**Purpose**: Analyze clock tree quality and skew

**Metrics Tracked**:
- Maximum clock latency
- Clock skew
- Clock tree insertion delay

**Status Indicators**:
- **PASSED** ✅: Latency within spec
- **WARN** ⚠️: Latency > 550ps
- **FAILED** ❌: Latency >= 580ps

**Example**:
```bash
./run_agur_regression.sh -t clock -u fth
```

---

### 5. Block Release Status (`-t release`)

**Purpose**: Verify block release completeness

**Checks**:
- Release directory structure
- Required files presence
- Release log validation

**Example**:
```bash
./run_agur_regression.sh -t release
```

---

## Output Files

Each regression run generates an HTML dashboard with timestamp:

**Filename Format**: `agur_<type>_regression_dashboard_YYYYMMDD_HHMMSS.html`

**Examples**:
- `agur_formal_regression_dashboard_20251014_153022.html`
- `agur_timing_regression_dashboard_20251014_160515.html`
- `agur_pv_regression_dashboard_20251014_162030.html`

**HTML Dashboard Features**:
- ✅ **AVICE PNG logo** (base64-encoded, clickable to enlarge)
- ✅ **Overall statistics** with color-coded cards
- ✅ **Units organized by chiplet** with collapsible sections
- ✅ **Individual analysis status** for each unit
- ✅ **Release information** (who released, when)
- ✅ **Runtime information**
- ✅ **Self-contained and portable** (no external dependencies)
- ✅ **Professional styling** with gradients
- ✅ **Back to top button** for navigation
- ✅ **Copyright footer**

**Location**: Generated in user's **current working directory** for portability

---

## Example Workflows

### Daily Formal Regression

```bash
# Run formal regression on all units
cd ~/reports
/home/avice/scripts/avice_wa_review/agur_release_tracking/run_agur_regression.sh -t formal
```

### Pre-Tapeout Checks

```bash
# Run all regressions for CPORT chiplet
cd ~/tapeout_checks
./run_agur_regression.sh -t formal -c CPORT
./run_agur_regression.sh -t timing -c CPORT
./run_agur_regression.sh -t pv -c CPORT
./run_agur_regression.sh -t clock -c CPORT
./run_agur_regression.sh -t release -c CPORT
```

### Single Unit Deep Dive

```bash
# Analyze all aspects of prt unit
./run_agur_regression.sh -t formal -u prt
./run_agur_regression.sh -t timing -u prt
./run_agur_regression.sh -t pv -u prt
```

---

## Integration with AGUR Release Table

The regression framework uses the auto-updating `AGUR_UNITS_TABLE.txt`:

**Location**: `/home/avice/scripts/avice_wa_review/agur_release_tracking/AGUR_UNITS_TABLE.txt`

**Auto-Update**: The table is automatically updated when using `avice_wa_review.py --unit` flag or manually:

```bash
cd /home/avice/scripts/avice_wa_review/agur_release_tracking
./check_and_update_agur_table.sh --force
```

---

## Adding New Chiplets/Units

The regression automatically picks up new units from `AGUR_UNITS_TABLE.txt`:

1. Add new units to extraction script
2. Run: `./extract_agur_releases.sh`
3. Run regression: `./run_agur_regression.sh -t <type>`

**No code changes needed!** The script is fully modular and extensible.

---

## Scheduled/Automated Runs

### Example Cron Jobs

```bash
# Daily formal regression at 6 AM
0 6 * * * cd /home/reports && /home/avice/scripts/avice_wa_review/agur_release_tracking/run_agur_regression.sh -t formal

# Daily timing regression at 7 AM
0 7 * * * cd /home/reports && /home/avice/scripts/avice_wa_review/agur_release_tracking/run_agur_regression.sh -t timing

# Weekly PV regression on Sundays at 2 AM
0 2 * * 0 cd /home/reports && /home/avice/scripts/avice_wa_review/agur_release_tracking/run_agur_regression.sh -t pv
```

### CI/CD Integration

```bash
#!/bin/bash
# In your CI/CD pipeline

TYPES=("formal" "timing" "pv" "clock" "release")
FAILED=0

for type in "${TYPES[@]}"; do
    echo "Running $type regression..."
    ./run_agur_regression.sh -t "$type" -c CPORT
    if [ $? -ne 0 ]; then
        echo "ERROR: $type regression failed!"
        FAILED=1
    fi
done

if [ $FAILED -ne 0 ]; then
    echo "Some regressions failed!"
    exit 1
fi

echo "All regressions passed!"
exit 0
```

---

## Troubleshooting

### No Analysis Section Found

- Check if workarea has the required analysis section
- Run manually: `/home/avice/scripts/avice_wa_review_launcher.csh <workarea> -s <section>`
- Verify logs exist in workarea

### Script Execution Errors

- Check console output for error messages
- Verify Python path: `/home/utils/Python/builds/3.11.9-20250715/bin/python3`
- Verify `avice_wa_review.py` exists and is executable

### Stale Results

- Ensure `AGUR_UNITS_TABLE.txt` is up to date
- Run: `./check_and_update_agur_table.sh --force`
- Verify workarea paths still exist

### HTML Dashboard Not Generated

- Check write permissions in current directory
- Verify sufficient disk space
- Check for bash syntax errors

---

## Files and Locations

```
agur_release_tracking/
├── run_agur_regression.sh             (main regression script)
├── AGUR_UNITS_TABLE.txt               (input: units to test)
├── AGUR_REGRESSION_GUIDE.md           (this file)
├── extract_agur_releases.sh           (extract release data)
└── check_and_update_agur_table.sh     (auto-update table)

Output files (generated in user's current directory):
└── agur_<type>_regression_dashboard_YYYYMMDD_HHMMSS.html
```

**Important**: Output files are generated in the directory where you run the script, not in the script's directory. This ensures portability and allows multiple users to use the script without permission issues.

---

## Current Status (CPORT Chiplet)

### Formal Verification

| Unit | Status | Details |
|------|--------|---------|
| **prt** | ⚠️ UNRESOLVED | rtl_vs_syn_bbox flow has unresolved points |
| **pmux** | ✅ PASSED | All formal flows clean |
| **fdb** | ✅ PASSED | All formal flows clean |
| **fth** | ✅ PASSED | All formal flows clean |
| **lnd** | ✅ PASSED | All formal flows clean |

**Overall**: 80% PASS rate (4/5 units)

---

## Related Scripts

- `extract_agur_releases.sh` - Extract release data to AGUR_UNITS_TABLE.txt
- `check_and_update_agur_table.sh` - Auto-update release table
- `avice_wa_review.py` - Main workarea analysis tool (used internally)

---

## Future Enhancements

1. ✅ Generic regression framework supporting multiple analysis types
2. ✅ CPORT chiplet formal regression (5 units)
3. 📋 Add remaining 4 chiplets (65 more units)
4. 📋 Historical trend tracking (store results over time)
5. 📋 Email notifications on failures
6. 📋 Slack/Teams integration
7. 📋 Comparison between releases

---

*Last Updated: 2025-10-14*  
*Script Location: `/home/avice/scripts/avice_wa_review/agur_release_tracking/run_agur_regression.sh`*  
*Contact: avice@nvidia.com*
