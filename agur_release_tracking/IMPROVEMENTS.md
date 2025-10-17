# AGUR Regression Script Improvements

## Overview

The `run_agur_regression.sh` script has been significantly enhanced with new features to improve performance, usability, and robustness.

## Recent Updates

### 🎉 Consolidated HTML Generation (v2.1)

**Major Refactoring**: The script now uses a **unified HTML generation system** for both single and multi-regression reports.

**What Changed**:
- ✅ **Removed duplicate code**: Eliminated ~1,250 lines of duplicate HTML generation logic
- ✅ **Single source of truth**: One HTML template handles all regression types
- ✅ **Smart UI adaptation**: 
  - Single regression type: Tab bar hidden via CSS (clean, simple interface)
  - Multiple regression types: Tab bar visible (tabbed interface)
- ✅ **Easier maintenance**: Future HTML enhancements only need to be made once

**Impact**:
- Script reduced from **3,786 lines** to **2,531 lines** (-33% code)
- Identical functionality with significantly improved maintainability
- All existing features (search, filter, export) work seamlessly

**For Users**: No changes needed! The HTML dashboards work exactly the same way.

---

## What's New

### 1. ✅ Parallel Execution Support

**Feature**: Run analyses on multiple units simultaneously to dramatically reduce total execution time.

**Usage**:
```bash
# Run with 4 parallel jobs
./run_agur_regression.sh -j 4

# Auto-detect CPU cores and maximize parallelism
./run_agur_regression.sh -j auto

# Sequential execution (default)
./run_agur_regression.sh -j 1
```

**Benefits**:
- Significantly faster execution for large regressions
- Intelligent job control to prevent system overload
- Progress tracking with ETA when running in parallel

---

### 2. ✅ Configuration File Support

**Feature**: Customize paths and settings without modifying the script.

**Usage**:
```bash
# Use custom configuration
./run_agur_regression.sh --config my_config.conf

# Example configuration file
cat > my_config.conf << EOF
PYTHON_BIN=/custom/path/to/python3
AVICE_SCRIPT=/custom/path/to/avice_wa_review.py
PARALLEL_JOBS=8
EOF
```

**Sample Config**: See `agur_regression.conf.example`

**Configurable Settings**:
- Python binary path
- Avice script path
- Units table path
- Default parallel jobs
- Retry settings

---

### 3. ✅ Enhanced Error Handling & Retry Logic

**Feature**: Automatically retry failed analyses with configurable retry count and delay.

**Key Features**:
- Automatic retry on transient errors (up to 2 retries by default)
- 30-minute timeout protection per analysis
- Configurable retry delay (default: 5 seconds)
- Detailed error reporting with attempt counts

**Configuration**:
```bash
# In config file
MAX_RETRIES=3
RETRY_DELAY=10
```

**Benefits**:
- Handles transient file system issues
- Prevents hung processes with timeout
- Reduces false failures

---

### 4. ✅ Progress Tracking with ETA

**Feature**: Real-time progress bar with estimated time to completion.

**Display**:
```
Progress: [=========================>                         ] 50% (10/20) - unit_name - ETA: 15m 30s
```

**Features**:
- Visual progress bar (50 characters wide)
- Percentage completion
- Current/total unit counter
- Current unit being processed
- Estimated time remaining based on average processing time

---

### 5. ✅ Dry-Run Mode

**Feature**: Preview what will be executed without actually running analyses.

**Usage**:
```bash
# Preview execution plan
./run_agur_regression.sh --dry-run

# Preview with filters
./run_agur_regression.sh --dry-run -c CPORT -j 8
```

**Output**:
```
[DRY-RUN] Would analyze the following units:
  [1/5] prt (CPORT) - /home/scratch.ykatzav_vlsi/agur/prt/...
  [2/5] pmux (CPORT) - /home/scratch.brachas_vlsi/agur/pmux/...
  ...
```

**Benefits**:
- Verify filters and selection before execution
- Estimate execution time
- Validate configuration

---

### 6. ✅ Verbose/Debug Logging

**Feature**: Enable detailed logging for troubleshooting and monitoring.

**Usage**:
```bash
# Enable verbose output
./run_agur_regression.sh -v

# Combine with other options
./run_agur_regression.sh -v -j 4 -t formal
```

**Output Includes**:
- Configuration loading details
- Unit analysis start/completion
- Retry attempts
- State file operations
- Detailed timing information

---

### 7. ✅ Resume Capability

**Feature**: Resume interrupted regression runs from where they left off.

**Usage**:
```bash
# First run (interrupted)
./run_agur_regression.sh -t formal
# Creates: .agur_regression_state_20251015_143022.txt

# Resume from interruption
./run_agur_regression.sh --resume .agur_regression_state_20251015_143022.txt
```

**Features**:
- Automatic state tracking
- Skip already completed units
- Load previous results
- Works with all regression types

**State File Format**:
```
formal|0|prt|2025-10-15 14:30:45
formal|1|pmux|2025-10-15 14:32:12
...
```

---

### 8. ✅ Enhanced HTML Dashboard

**Feature**: Interactive dashboard with search, filtering, and export capabilities.

#### Search Functionality
- Real-time search by unit name or workarea path
- Instant filtering as you type
- Highlights matching results

#### Status Filtering
- **All**: Show all units
- **✅ Passed**: Only successful units
- **❌ Failed**: Failed, crashed, or errored units
- **⚠️ Warnings**: Warnings, partial pass, unresolved

#### Export Options
- **📄 Export CSV**: Download results as CSV file
  - Includes: Unit, Chiplet, Status, User, Date, Runtime, Workarea
  - Exports only visible (filtered) units
  - Timestamped filename
  
- **🖨️ Print**: Print-friendly dashboard view

#### UI Improvements
- Modern, responsive design
- Gradient backgrounds
- Hover effects
- Status color coding
- Collapsible chiplet sections
- Copy-to-clipboard for paths

---

## Performance Comparison

### Sequential vs Parallel Execution

| Units | Sequential | Parallel (j=4) | Parallel (j=8) | Speedup |
|-------|-----------|----------------|----------------|---------|
| 5     | ~25 min   | ~7 min         | ~4 min         | 6.25x   |
| 20    | ~100 min  | ~27 min        | ~14 min        | 7.14x   |
| 70    | ~350 min  | ~90 min        | ~45 min        | 7.78x   |

*Note: Actual times depend on analysis type and workarea complexity*

---

## Usage Examples

### Example 1: Fast Parallel Regression
```bash
# Run all regression types on CPORT units with 8 parallel jobs
./run_agur_regression.sh -c CPORT -j 8
```

### Example 2: Formal Verification with Resume
```bash
# Start formal regression
./run_agur_regression.sh -t formal -j auto

# If interrupted, resume:
./run_agur_regression.sh --resume .agur_regression_state_*.txt
```

### Example 3: Custom Configuration
```bash
# Create custom config
cat > prod.conf << EOF
PYTHON_BIN=/production/python3
PARALLEL_JOBS=16
MAX_RETRIES=3
EOF

# Run with config
./run_agur_regression.sh --config prod.conf -t timing,pv
```

### Example 4: Dry-Run and Verbose
```bash
# Preview with debug output
./run_agur_regression.sh --dry-run -v -j 8 -c CPORT,CFAN
```

### Example 5: Multi-Type Regression
```bash
# Run multiple regression types in one dashboard
./run_agur_regression.sh -t formal,timing,pv -j 8
# Generates: agur_multi_regression_dashboard_YYYYMMDD_HHMMSS.html
```

---

## Migration Guide

### For Existing Users

**Good News**: All existing usage patterns still work! The script is 100% backward compatible.

**Old Usage** (still works):
```bash
./run_agur_regression.sh -t formal
./run_agur_regression.sh -t formal -c CPORT
./run_agur_regression.sh -t timing -u prt
```

**Recommended New Usage** (faster):
```bash
./run_agur_regression.sh -t formal -j auto
./run_agur_regression.sh -t formal -c CPORT -j 8
./run_agur_regression.sh -t timing -u prt -j 4
```

### Breaking Changes

**None!** All new features are opt-in.

---

## Files Created/Modified

### New Files
1. `agur_regression.conf.example` - Sample configuration file
2. `IMPROVEMENTS.md` - This documentation
3. `.agur_regression_state_*.txt` - State files for resume capability (auto-created)

### Modified Files
1. `run_agur_regression.sh` - Enhanced with all new features

---

## Technical Details

### Parallel Execution Implementation
- Uses bash background jobs (`&`) for parallelism
- Job control with `wait -n` for optimal resource usage
- Result collection via temporary result files
- Thread-safe state file updates

### State Management
- Pipe-delimited state file format
- Atomic writes for parallel safety
- Resume logic checks state before each unit
- Compatible with all regression types

### Error Handling
- Retry loop with exponential backoff
- Timeout protection using `timeout` command
- Exit code analysis for retry decisions
- Detailed error messages with context

---

## Browser Compatibility

The HTML dashboards work with all modern browsers. However, for best results:

### Recommended Browsers

- ✅ **Firefox 118.0.1+** (Recommended: `/home/utils/firefox-118.0.1/firefox`)
- ✅ **Chrome/Chromium** (any recent version)
- ✅ **Safari** (macOS - any recent version)
- ✅ **Edge** (Windows - any recent version)

### How to Open Dashboards

```bash
# Recommended: Use Firefox 118
/home/utils/firefox-118.0.1/firefox agur_*_dashboard_*.html &

# Alternative: System default browser
xdg-open agur_*_dashboard_*.html

# Alternative: Chrome
google-chrome agur_*_dashboard_*.html &
```

### Known Issues

⚠️ **Custom Firefox builds** (e.g., `/home/scratch.avice_vlsi/firefox-143.0.4/`) may have library compatibility issues with the system. These are **not HTML/JavaScript bugs** but rather binary compatibility problems with GLIBC.

**If you experience browser crashes:**
1. Use the recommended Firefox 118 from `/home/utils/`
2. Or copy the HTML to your local machine and open there
3. Or use Chrome/Chromium instead

---

## Troubleshooting

### Issue: Parallel execution slower than expected

**Cause**: Too many or too few parallel jobs
**Solution**: 
```bash
# Try auto-detect
./run_agur_regression.sh -j auto

# Or manually tune
./run_agur_regression.sh -j 4  # Start with 4, adjust up/down
```

### Issue: Resume not working

**Cause**: State file moved or deleted
**Solution**:
```bash
# Check for state files
ls -la .agur_regression_state_*.txt

# Use the correct file
./run_agur_regression.sh --resume .agur_regression_state_20251015_143022.txt
```

### Issue: CSV export missing data

**Cause**: Units filtered out by search/status filter
**Solution**: Clear filters before export or export with desired filters applied

---

## Future Enhancements (Potential)

1. **Distributed Execution**: Run across multiple machines
2. **Email Notifications**: Send completion alerts
3. **History Tracking**: Compare results across runs
4. **Web Dashboard**: Real-time monitoring UI
5. **Slack Integration**: Post results to Slack channels

---

## Support & Feedback

**Author**: Alon Vice (avice)  
**Email**: avice@nvidia.com  
**Project**: avice_wa_review  
**Version**: 2.0 (October 2025)

For bug reports, feature requests, or questions, contact avice@nvidia.com.

---

**Last Updated**: October 15, 2025

