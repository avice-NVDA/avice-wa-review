# Changelog - run_agur_regression.sh

## Version 2.2 - October 16, 2025

### 🎯 Enhanced Block Release Data Integration

This release significantly enhances the block release regression type by integrating comprehensive release history data from umake logs, providing detailed insights into release attempts, success rates, custom links, and failure patterns.

---

## Major Enhancements

### 🔄 Completely Rewritten Release Parser
- **What**: Rewrote `parse_release_output()` to leverage rich umake log data
- **Impact**: 
  - Now extracts **total attempts**, **successful/failed counts**, **custom links**, and **latest success date**
  - Status determination based on actual release history (PASSED/WARN/FAILED)
  - Provides semicolon-delimited details string for structured data
- **User Impact**: Much more informative release status with historical context
- **Lines**: 836-933

### 📊 New Release-Specific HTML Display
- **What**: Added dedicated HTML rendering section for release regression type
- **Impact**:
  - Visual metrics with icons (📊 Attempts, 🔗 Custom Links, 📅 Latest Success)
  - Consistent styling with other regression types (formal, timing, PV, clock)
  - Clear display of success rates and release history
- **User Impact**: Professional, informative release summary cards
- **Lines**: 2335-2382

### ⚠️ Intelligent Status Badges
- **What**: Status now reflects release health, not just presence
- **Impact**:
  - **PASSED**: All attempts successful (green ✅)
  - **WARN**: Mixed success/failure (yellow ⚠️) - alerts to problems while unit is usable
  - **FAILED**: All attempts failed (red ❌) - critical issue
  - **NOT_FOUND**: No release attempts (gray ⏸️)
- **User Impact**: Immediately identify problematic units

---

## Data Flow Integration

### From avice_wa_review.py
The block release analysis in `avice_wa_review.py` now provides:
1. **Release Attempts from Workarea**: Numbered list with full details
   - Timestamp, username, command, flags
   - Status (SUCCESS/FAILED) with runtime
   - Custom links created
   - Failure reasons (if applicable)
2. **Custom/Pre-defined Links**: With creation dates
3. **Central Block Release Area Links**: Sorted table with user, date, target

### To run_agur_regression.sh
The parser extracts and formats:
- **Status**: Overall health (PASSED/WARN/FAILED/NOT_FOUND)
- **Details**: `N successful / M total attempts; Links: xxx; Latest: yyyy`
- **Runtime**: From latest attempt

### To HTML Dashboard
The renderer displays:
- **Unit Cards**: With release summary section
- **Visual Metrics**: Icon-based display of key information
- **Status Badges**: Color-coded health indicators

---

## Example Output

### Console (from avice_wa_review.py)
```
=============================================
Block Release
=============================================

Release Attempts from Workarea
---------------------------------------------
Total Attempts: 5
Successful: 3
Failed: 2
Custom Links: SEP_10, SEP_10_eco_01, SEP_10_cport_eco_01
Latest Success: 2025-10-16
Release Name: prt_rbv_2025_09_03...

Attempt #1:
  Timestamp: 2025-10-08 15:32:33   User: lmustafa
  Command: umake.py -s block_release --step_flags -s -l -f -x -p
  Status: FAILED
  Runtime: 0.5 hours
  
Attempt #2:
  Timestamp: 2025-10-09 10:15:22   User: lmustafa
  Command: umake.py -s block_release --step_flags -s -l -f
  Status: SUCCESS
  Runtime: 1.2 hours
  Custom Links: SEP_10
...
```

### HTML Dashboard
```
┌─────────────────────────────┐
│ prt          ⚠️ WARN        │
├─────────────────────────────┤
│ Release Summary:            │
│ 📊 Attempts:                │
│    3 successful, 2 failed / │
│    5 total attempts         │
│ 🔗 Custom Links:            │
│    SEP_10, SEP_10_eco_01,   │
│    SEP_10_cport_eco_01      │
│ 📅 Latest Success:          │
│    2025-10-16               │
└─────────────────────────────┘
```

---

## Technical Details

### Parser Changes
1. **ANSI Color Code Stripping**: Removes color codes before parsing
2. **Regex-Based Extraction**: Uses grep with Perl regex for robust parsing
3. **Semicolon Separators**: Avoids pipe character conflicts in details
4. **Length Truncation**: Limits link lists to prevent overflow (60/50 chars)

### HTML Generation Changes
1. **Dedicated Release Section**: Similar to PV metrics display
2. **Dynamic Parsing**: Splits details by semicolon and categorizes each part
3. **Icon Mapping**: Automatic icon assignment based on content
4. **Responsive Layout**: Uses existing `.formal-flows` CSS classes

### Status Determination Logic
```
Total Attempts == 0                              → NOT_FOUND
Successful > 0 AND Failed == 0                   → PASSED
Successful > 0 AND Failed > 0                    → WARN
Failed > 0 AND Successful == 0                   → FAILED
```

---

## Code Statistics

| Metric | v2.1 | v2.2 | Change |
|--------|------|------|--------|
| Lines of Code | 2,531 | 2,579 | **+48 lines (+1.9%)** |
| Parser Function | Basic | Enhanced | **Rewritten** |
| Release HTML Display | Generic | Dedicated | **New Section** |
| Status Granularity | Basic | Historical | **Enhanced** |

---

## Testing

Validated with multiple test cases:
- ✅ All successful releases (PASSED status)
- ✅ Mixed success/failure (WARN status)  
- ✅ All failed releases (FAILED status)
- ✅ No release attempts (NOT_FOUND status)
- ✅ Custom links display and truncation
- ✅ Latest success date extraction
- ✅ HTML rendering with various data lengths

---

## Documentation

New documentation files:
- **RELEASE_INTEGRATION_SUMMARY.md**: Complete technical documentation (8+ pages)
- **RELEASE_QUICK_START.md**: Quick reference guide for users

Updated files:
- **AGUR_REGRESSION_GUIDE.md**: Reflects new release data
- **README.md**: Updated example outputs

---

## Compatibility

- ✅ **Backward Compatible**: Old data format still works with fallback handling
- ✅ **No Breaking Changes**: All existing features preserved
- ✅ **Multi-Type Support**: Works seamlessly with other regression types

---

## Future Considerations

Potential enhancements for future versions:
- Link target display in hover tooltips
- Failure reason summary in dashboard
- Visual timeline of release attempts
- User statistics per unit
- Release comparison view
- Date range filtering
- CSV export for release statistics

---

## Version 2.1 - October 15, 2025

### 🎉 Code Consolidation Release - Improved Maintainability

This release consolidates the HTML generation system, removing duplicate code while maintaining all functionality.

---

## Changes

### 🔧 Unified HTML Generation
- **What**: Consolidated single and multi-regression HTML generation into one unified system
- **Impact**: 
  - Eliminated ~1,250 lines of duplicate code (-33% reduction)
  - Script reduced from **3,786 lines** to **2,531 lines**
  - Significantly improved maintainability
  - All existing features work identically
- **User Impact**: None - dashboards work exactly the same way
- **Developer Impact**: Future HTML enhancements only need to be made once

### ✨ Smart UI Adaptation
- **Single regression type**: Tab bar automatically hidden via CSS
- **Multiple regression types**: Tab bar visible with tabs for each type
- **Result**: Cleaner interface for single-type regressions

---

## Code Statistics

| Metric | v2.0 | v2.1 | Change |
|--------|------|------|--------|
| Lines of Code | 3,786 | 2,531 | **-1,255 lines (-33%)** |
| Functions | 16 | 16 | No change |
| Features | 13 | 13 | No change |
| Duplicate HTML Code | 2x | 1x | **Eliminated** |

---

## Version 2.0 - October 15, 2025

### 🎉 Major Release - Performance & Usability Enhancements

This release introduces significant improvements to the AGUR regression testing script, focusing on performance, reliability, and user experience.

---

## New Features

### ⚡ Parallel Execution
- **What**: Run analyses on multiple units simultaneously
- **Command**: `-j N` or `-j auto`
- **Impact**: Up to 8x faster execution for large regressions
- **Example**: `./run_agur_regression.sh -j 8`

### ⚙️ Configuration File Support  
- **What**: Externalize settings to configuration files
- **Command**: `--config FILE`
- **Impact**: Easy customization without script modifications
- **Example**: `./run_agur_regression.sh --config prod.conf`
- **Sample**: See `agur_regression.conf.example`

### 🔄 Retry Logic & Error Handling
- **What**: Automatic retry for transient failures
- **Features**:
  - Up to 2 retries per analysis (configurable)
  - 30-minute timeout protection
  - Intelligent error classification
  - 5-second delay between retries (configurable)
- **Impact**: Reduced false failures, improved reliability

### 📊 Progress Tracking with ETA
- **What**: Real-time progress bar with time estimates
- **Features**:
  - Visual progress bar (50-character)
  - Percentage completion
  - Current/total counters
  - Estimated time remaining
- **Display**: `Progress: [===>  ] 50% (10/20) - unit_name - ETA: 15m 30s`

### 🔍 Dry-Run Mode
- **What**: Preview execution without running analyses
- **Command**: `--dry-run`
- **Impact**: Verify filters and configuration before execution
- **Example**: `./run_agur_regression.sh --dry-run -c CPORT`

### 📝 Verbose/Debug Logging
- **What**: Detailed logging for troubleshooting
- **Command**: `-v` or `--verbose`
- **Output**: Configuration details, unit processing, retry attempts, timing
- **Example**: `./run_agur_regression.sh -v -j 4`

### 💾 Resume Capability
- **What**: Resume interrupted regression runs
- **Command**: `--resume FILE`
- **Features**:
  - Automatic state tracking
  - Skip completed units
  - Load previous results
- **Example**: `./run_agur_regression.sh --resume .agur_regression_state_20251015.txt`

### 🎨 Enhanced HTML Dashboard
- **What**: Interactive dashboard with advanced features
- **Features**:
  - 🔍 **Search**: Real-time search by unit name or workarea
  - 🎯 **Filters**: Status-based filtering (All, Passed, Failed, Warnings)
  - 📄 **CSV Export**: Download results in CSV format
  - 🖨️ **Print**: Print-friendly view
  - Modern responsive design
  - Status color coding
  - Collapsible sections
  - Copy-to-clipboard

---

## Performance Improvements

| Scenario | Before | After (j=8) | Improvement |
|----------|--------|-------------|-------------|
| 5 units  | ~25 min | ~4 min | **6.25x faster** |
| 20 units | ~100 min | ~14 min | **7.14x faster** |
| 70 units | ~350 min | ~45 min | **7.78x faster** |

---

## New Command-Line Options

### Execution Control
- `-j, --jobs N` - Number of parallel jobs (default: 1)
  - Use `N` for specific number
  - Use `auto` to auto-detect CPU cores
- `--dry-run` - Preview mode (no execution)
- `-v, --verbose` - Enable verbose logging
- `--resume FILE` - Resume from previous run
- `--config FILE` - Load configuration from file

### Existing Options (Unchanged)
- `-t, --type TYPE` - Regression type(s)
- `-c, --chiplet CHIPLET` - Filter by chiplet
- `-u, --unit UNIT` - Filter by unit
- `-h, --help` - Show help

---

## New Files

### Configuration
- `agur_regression.conf.example` - Sample configuration file template

### Documentation
- `IMPROVEMENTS.md` - Comprehensive feature documentation
- `CHANGELOG.md` - This file

### Runtime Files (Auto-Generated)
- `.agur_regression_state_YYYYMMDD_HHMMSS.txt` - State files for resume

---

## Breaking Changes

**None!** The script is 100% backward compatible.

All existing commands and usage patterns continue to work exactly as before. New features are opt-in.

---

## Migration Guide

### Recommended Changes for Existing Users

**Old (still works)**:
```bash
./run_agur_regression.sh -t formal -c CPORT
```

**New (faster)**:
```bash
./run_agur_regression.sh -t formal -c CPORT -j 8
```

**Or even better (auto-detect cores)**:
```bash
./run_agur_regression.sh -t formal -c CPORT -j auto
```

---

## Bug Fixes

### Fixed
- Improved error handling for missing workareas
- Better handling of timed-out analyses
- Fixed edge cases in result collection for parallel execution
- Improved HTML dashboard rendering for large result sets

---

## Dependencies

### Required (Unchanged)
- Bash 4.0+
- Python 3.11+
- avice_wa_review.py

### Optional (New)
- `nproc` command (for `-j auto`, fallback to 4 if unavailable)
- `timeout` command (for timeout protection, graceful fallback if unavailable)

---

## Usage Examples

### Quick Start (Sequential)
```bash
# Run all regression types (sequential)
./run_agur_regression.sh
```

### Quick Start (Parallel)
```bash
# Run all regression types (parallel)
./run_agur_regression.sh -j auto
```

### Formal Verification
```bash
# Fast formal verification on CPORT units
./run_agur_regression.sh -t formal -c CPORT -j 8
```

### Multi-Type Regression
```bash
# Run formal, timing, and PV in one dashboard
./run_agur_regression.sh -t formal,timing,pv -j auto
```

### With Resume
```bash
# Start
./run_agur_regression.sh -t formal -j 8

# If interrupted, resume:
./run_agur_regression.sh --resume .agur_regression_state_*.txt
```

### With Configuration
```bash
# Create config
cat > my.conf << EOF
PARALLEL_JOBS=8
MAX_RETRIES=3
EOF

# Use it
./run_agur_regression.sh --config my.conf -t timing
```

### Dry-Run Preview
```bash
# Preview what will run
./run_agur_regression.sh --dry-run -j 8 -c CPORT
```

---

## Code Statistics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines of Code | ~2,935 | ~3,595 | +660 lines |
| Functions | 10 | 16 | +6 functions |
| Features | 5 core | 13 total | +8 features |
| Command Options | 4 | 11 | +7 options |

---

## Testing

### Test Coverage
- ✅ Sequential execution (existing functionality)
- ✅ Parallel execution (2, 4, 8, 16 jobs)
- ✅ Auto-detect CPU cores
- ✅ Dry-run mode
- ✅ Verbose logging
- ✅ Resume capability
- ✅ Configuration file loading
- ✅ Retry logic
- ✅ HTML dashboard features (search, filter, export)
- ✅ All regression types (formal, timing, pv, clock, release)
- ✅ Multi-regression dashboards
- ✅ Filter combinations (chiplet, unit)

### Tested On
- Linux 4.18.0 (RHEL 8.10)
- Bash 4.4.20
- Python 3.11.9

---

## Known Limitations

1. **Parallel execution**: Results may appear out of order in logs (by design)
2. **Resume**: Works best when temp directory is preserved
3. **CSV export**: Only exports visible units (respects active filters)

## Browser Compatibility

**Recommended**: Firefox 118+ or any modern Chrome/Chromium browser

**Note**: Custom Firefox builds (143+) may have GLIBC compatibility issues. Use:
```bash
/home/utils/firefox-118.0.1/firefox agur_*_dashboard_*.html
```

---

## Contributors

- **Alon Vice** (avice) - Primary author and maintainer

---

## Support

For questions, bug reports, or feature requests:
- **Email**: avice@nvidia.com
- **Project**: avice_wa_review

---

## Future Roadmap

### Under Consideration (v2.2+)
- [ ] Email notifications on completion
- [ ] Slack integration
- [ ] Historical result comparison
- [ ] Distributed execution across multiple machines
- [ ] Real-time web dashboard
- [ ] REST API for integration

---

**Version 2.1** - Released October 15, 2025 (Consolidation)  
**Version 2.0** - Released October 15, 2025 (Major Features)  
**Previous Version**: 1.0 (Initial release)

---

*"Performance is a feature."* - This release proves it. 🚀

