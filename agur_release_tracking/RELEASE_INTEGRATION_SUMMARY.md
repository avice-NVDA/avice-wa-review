# Block Release Data Integration Summary

**Date**: October 16, 2025  
**Component**: AGUR Regression Framework - Block Release Type

---

## Overview

This document summarizes the integration of comprehensive block release analysis data into the AGUR regression framework. The integration leverages the rich block release information extracted from umake logs to provide detailed insights across all released units.

---

## What Changed

### 1. Enhanced Data Extraction Parser

**File**: `run_agur_regression.sh`  
**Function**: `parse_release_output()`  
**Lines**: 836-933

#### Previous Behavior
- Parsed basic release flags (STA, FCL, PNR)
- Determined completeness based on number of release types
- Limited information about release history

#### New Behavior
- Extracts comprehensive release statistics from umake logs:
  - **Total Attempts**: Number of release attempts made
  - **Successful Attempts**: Count of successful releases
  - **Failed Attempts**: Count of failed releases
  - **Custom Links**: List of user-defined symbolic links
  - **Latest Success Date**: Date of the most recent successful release
  - **Runtime**: Runtime of the latest release attempt

#### Key Improvements
1. **Accurate Status Detection**: 
   - `PASSED`: All attempts successful
   - `WARN`: Mixed success and failure
   - `FAILED`: All attempts failed
   - `NOT_FOUND`: No release attempts detected

2. **Rich Details String**: Format is now `status|details|runtime` where details include:
   - Attempt statistics (e.g., "3 successful / 5 total attempts")
   - Custom links list (e.g., "Links: SEP_10, SEP_10_eco_01, SEP_10_cport_eco_01")
   - Latest success date (e.g., "Latest: 2025-10-16")
   - All separated by semicolons for easy parsing

3. **ANSI Color Code Stripping**: Removes color codes from console output before parsing

---

### 2. Enhanced HTML Display

**File**: `run_agur_regression.sh`  
**Section**: HTML Generation for Unit Cards  
**Lines**: 2335-2382

#### New Release-Specific HTML Section

Added a dedicated HTML rendering section for release regression type that:

1. **Parses Semicolon-Delimited Details**: Splits the details string by semicolons
2. **Creates Visual Metrics**: Displays each piece of information with appropriate icons:
   - 📊 **Attempts**: Shows success/total statistics
   - 🔗 **Custom Links**: Lists user-defined symbolic links
   - 📅 **Latest Success**: Displays the most recent successful release date
   - ℹ️ **Info**: Generic fallback for other information

3. **Consistent Styling**: Uses the same `.formal-flows` and `.flow-item` CSS classes as other regression types

#### Example HTML Output

```html
<div class="formal-flows">
    <div class="flow-title">Release Summary:</div>
    <div class="flow-item">
        <span><strong>📊 Attempts</strong></span>
        <span>3 successful / 5 total attempts</span>
    </div>
    <div class="flow-item">
        <span><strong>🔗 Custom Links</strong></span>
        <span>SEP_10, SEP_10_eco_01, SEP_10_cport_eco_01</span>
    </div>
    <div class="flow-item">
        <span><strong>📅 Latest Success</strong></span>
        <span>2025-10-16</span>
    </div>
</div>
```

---

## Data Flow

### Step 1: avice_wa_review.py Analysis
The `avice_wa_review.py` script runs with `--sections block-release` and:

1. Searches all `umake_log/*/*.log` files for block release commands
2. Parses each release attempt to extract:
   - Timestamp and username
   - Command with flags
   - Status (SUCCESS/FAILED)
   - Custom links created
   - Failure reasons (if applicable)
3. Checks central block release area for all custom links
4. Generates comprehensive console output with:
   - Release attempts from workarea (numbered, with full details)
   - Custom/Pre-defined links detected (with dates)
   - All custom links in central release area (sorted table)
5. Creates detailed HTML report with all information

### Step 2: run_agur_regression.sh Parsing
The regression script:

1. Calls `avice_wa_review.py -u <unit> -s block-release`
2. Captures the console output to a text file
3. Calls `parse_release_output()` to extract:
   - Overall status (PASSED/WARN/FAILED/NOT_FOUND)
   - Details string with all key metrics
   - Runtime of latest attempt
4. Stores parsed data in `REGRESSION_RESULTS` associative array

### Step 3: HTML Dashboard Generation
The regression framework:

1. Iterates through all units for the release regression type
2. For each unit:
   - Retrieves status, details, and runtime from results
   - Determines status badge (✅ PASSED, ⚠️ WARN, ❌ FAILED, etc.)
   - Generates unit card with header and metadata
   - Calls release-specific HTML formatter to parse details
   - Creates visual metrics display with icons
3. Aggregates statistics (passed count, failed count, etc.)
4. Generates summary bar and overall statistics

---

## Benefits

### 1. **Comprehensive Release History**
- See not just the current release status, but the entire release history
- Understand how many attempts were made before success
- Identify units with repeated release failures

### 2. **Custom Link Tracking**
- Visibility into all custom symbolic links created
- Helps identify custom releases and their purposes
- Useful for tracking ECOs and special releases

### 3. **Trend Analysis**
- Latest success date helps track release currency
- Attempt statistics reveal release difficulty
- Runtime data shows resource usage

### 4. **Failure Visibility**
- Units with failed attempts are flagged with WARN status
- Easy to spot units that need attention
- Detailed HTML reports provide failure reasons

### 5. **Consistency Across Regression Types**
- Release data now matches the detail level of formal, timing, PV, and clock
- Uniform HTML presentation
- Same filtering and sorting capabilities

---

## Testing

### Test Cases Validated

1. **All Successful Releases**
   - Input: 2 attempts, both successful, with custom links
   - Result: `PASSED|2 successful / 2 total attempts; Links: eco_01, eco_02; Latest: 2025-10-15|1.5 hours`
   - Status Badge: ✅ PASSED

2. **Mixed Success/Failure**
   - Input: 5 attempts, 3 successful, 2 failed, with custom links
   - Result: `WARN|3 successful, 2 failed / 5 total; Links: SEP_10, SEP_10_eco_01, SEP_10_cport_eco_01; Latest: 2025-10-16|1.3 hours`
   - Status Badge: ⚠️ WARN

3. **All Failed Releases**
   - Input: 3 attempts, all failed
   - Result: `FAILED|All 3 release attempts FAILED|0.5 hours`
   - Status Badge: ❌ FAILED

4. **No Release Attempts**
   - Input: Empty or missing release section
   - Result: `NOT_FOUND|No block release attempts found|N/A`
   - Status Badge: ⏸️ NOT RUN

---

## Usage

### Run Release Regression

```bash
# Single unit
cd /home/avice/scripts/avice_wa_review/agur_release_tracking
./run_agur_regression.sh -t release -u prt

# All units
./run_agur_regression.sh -t release

# With parallelism (faster)
./run_agur_regression.sh -t release -j 8

# Multiple regression types (includes release)
./run_agur_regression.sh -t formal,release -j auto

# Filter by chiplet
./run_agur_regression.sh -t release -c CPORT
```

### View Results

The generated HTML dashboard will be located in:
```
agur_release_regression_dashboard_YYYYMMDD_HHMMSS.html
```

For multi-type regressions:
```
agur_multi_regression_dashboard_YYYYMMDD_HHMMSS.html
```

### Interpreting Results

#### Status Badges
- **✅ PASSED**: All release attempts successful, unit is in good state
- **⚠️ WARN**: Some attempts failed, but unit has successful releases
- **❌ FAILED**: All release attempts failed, unit needs attention
- **⏸️ NOT RUN**: No release attempts detected

#### Release Summary Section
Each unit card shows:
- **📊 Attempts**: Success rate and total number of attempts
- **🔗 Custom Links**: User-defined symbolic links (if any)
- **📅 Latest Success**: Date of most recent successful release

---

## Implementation Details

### Code Architecture

1. **Separation of Concerns**
   - Data extraction: `avice_wa_review.py` (Python)
   - Data parsing: `parse_release_output()` (Bash)
   - HTML generation: `generate_html_dashboard()` (Bash)

2. **Data Format**
   - Console output: Human-readable with ANSI colors
   - Parsed data: Pipe-delimited `status|details|runtime`
   - Details: Semicolon-delimited key-value pairs

3. **Error Handling**
   - Graceful fallback if parsing fails
   - Default values for missing data
   - Clear error messages in status badges

### Key Design Decisions

1. **Semicolon Separator**: Used semicolons instead of pipes in details to avoid conflicts with the main pipe delimiter

2. **Icon-Based Display**: Added emojis/icons for visual clarity:
   - 📊 for statistics
   - 🔗 for links
   - 📅 for dates

3. **Length Truncation**: Long custom link lists are truncated (60 chars for PASSED, 50 chars for WARN) to prevent overflow

4. **Status Priority**: 
   - PASSED: Only if all attempts successful
   - WARN: If mixed success/failure (alerts user to problems)
   - FAILED: If all attempts failed (critical issue)

---

## Future Enhancements

### Potential Improvements

1. **Link Target Display**: Show where custom links point to
2. **Failure Reason Summary**: Include common failure reasons in dashboard
3. **Release Timeline**: Visual timeline of release attempts
4. **User Statistics**: Show which users made releases
5. **Comparison View**: Compare release history across units
6. **Filter by Date Range**: Show only releases within specific timeframe
7. **Export to CSV**: Export release statistics for further analysis

### Architecture Considerations

- All enhancements should maintain backward compatibility
- Data format should remain pipe-delimited for easy parsing
- HTML should use existing CSS classes for consistency
- Parser should handle missing/malformed data gracefully

---

## Related Files

### Modified Files
- `/home/avice/scripts/avice_wa_review/agur_release_tracking/run_agur_regression.sh`
  - `parse_release_output()` function (lines 836-933)
  - HTML generation section (lines 2335-2382)

### Supporting Files
- `/home/avice/scripts/avice_wa_review/avice_wa_review.py`
  - `run_block_release()` method
  - `_extract_umake_block_release_commands()` method
  - `_parse_release_log_file()` method
  - `_check_central_block_release_links()` method
  - `_generate_block_release_html_report()` method

### Documentation
- `/home/avice/scripts/avice_wa_review/.cursor/rules/architecture.mdc`
  - Symlink filtering guidelines
  - Console output standards
  - HTML report standards

---

## Contact

For questions or issues with the block release integration:
- Review this document
- Check the inline comments in `run_agur_regression.sh`
- Examine the test cases in this document
- Review the `avice_wa_review.py` block release methods

---

**Last Updated**: October 16, 2025  
**Version**: 1.0  
**Author**: AVICE Team

