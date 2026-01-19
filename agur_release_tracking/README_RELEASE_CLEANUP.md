# AGUR Release Area Cleanup Utility

## Overview

The AGUR Release Area Cleanup Utility is a comprehensive tool designed to identify, analyze, and provide cleanup recommendations for old block releases in the AGUR project. It helps maintain disk space health by detecting releases older than a configurable threshold (default: 90 days) and coordinating cleanup actions among multiple users.

**Critical:** This is an **analysis-only** utility. It never deletes files or modifies symlinks - all cleanup actions must be performed manually by unit owners.

## Current Situation

- **AGUR Release Area**: `/home/agur_backend_blockRelease/`
- **Disk Usage**: 90% (108T/120T used) - **CRITICAL**
- **Impact**: Designers cannot release blocks when storage is full
- **Solution**: Identify and remove old releases (>90 days old)

## Features

### Core Capabilities

1. **Release Scanning**
   - Scans all 73 AGUR units across 7 chiplets
   - Identifies releases older than configurable threshold
   - Parses timestamps from directory names
   - Extracts owner information from block_release.log files
   - **NEW**: Filter by specific chiplets or scan ALL (case-insensitive)

2. **Symlink Analysis with Multi-User Coordination**
   - Detects all symlinks pointing to releases
   - Identifies symlink owners via Linux file ownership (`ls -l`)
   - Handles coordination when fullchip STA/PV/PI users create links to unit releases
   - Distinguishes between self-owned and cross-user symlinks

3. **Disk Usage Calculation**
   - Parallel `du` commands for fast scanning
   - Configurable number of parallel processes (default: 10)
   - Calculates reclaimable space per owner and per chiplet

4. **Comprehensive Reporting**
   - **NEW**: Interactive multi-tab HTML dashboard with Chart.js visualizations
   - **Dashboard Tabs**:
     - **Summary**: Overall metrics, age distribution chart, chiplet breakdown, top consumers
     - **By Chiplet**: Expand/collapse sections per chiplet with unit details
     - **By Unit**: Complete unit-owner table with release areas and symlinks
     - **By Owner**: Owner-centric aggregated view across all units
   - Detailed CSV report with all releases
   - Markdown summary with statistics and impact analysis
   - Top 10 space consumers
   - Breakdown by chiplet and owner

5. **Coordinated Email Notifications**
   - Group emails to release owners
   - CC to symlink owners when coordination needed
   - CC to chiplet managers
   - Always CC to avice@nvidia.com
   - Safe deletion commands with verification steps

## Installation

No installation required. The utility is a standalone Python3 script located in:

```bash
/home/scratch.avice_vlsi/cursor/avice_wa_review/agur_release_tracking/agur_release_cleanup.py
```

### Prerequisites

- Python 3.6 or later (available at `/home/utils/Python/builds/3.11.9-20250715/bin/python3`)
- Access to `/home/agur_backend_blockRelease/` (read permissions)
- Access to `AGUR_UNITS_TABLE.csv` (in same directory)

## Usage

### Basic Usage

```bash
# Default: Generate reports only (NO emails sent)
python3 agur_release_cleanup.py

# Generate reports for specific chiplet
python3 agur_release_cleanup.py -c CPORT

# Send emails in test mode (to avice@nvidia.com only)
python3 agur_release_cleanup.py --test-mode

# Send emails to actual owners (PRODUCTION MODE)
python3 agur_release_cleanup.py --send-emails

# Analysis only, no emails or reports
python3 agur_release_cleanup.py --dry-run

# Send emails only, no reports
python3 agur_release_cleanup.py --email-only --send-emails
```

**⚠️ IMPORTANT**: By default, the utility generates reports only and does NOT send emails. You must explicitly use `--send-emails` or `--test-mode` to send emails.

### Chiplet Filtering (NEW)

```bash
# Scan specific chiplet
python3 agur_release_cleanup.py -c CPORT

# Scan multiple chiplets (comma-separated, case-insensitive)
python3 agur_release_cleanup.py -c CPORT,NDQ
python3 agur_release_cleanup.py --chiplet cport,hport,hiopl

# Scan all chiplets (default behavior)
python3 agur_release_cleanup.py -c ALL
python3 agur_release_cleanup.py  # Same as ALL

# Test mode with specific chiplets
python3 agur_release_cleanup.py --test-mode -c cport,ndq
```

### Interactive Approval Mode (NEW)

Run the utility in interactive mode to review and approve releases before sending emails:

```bash
# Start interactive approval server
python3 agur_release_cleanup.py --interactive

# With specific chiplet
python3 agur_release_cleanup.py --interactive -c CPORT

# With multiple chiplets
python3 agur_release_cleanup.py --interactive -c CPORT,NDQ
```

**Workflow**:
1. Script generates reports and opens dashboard in your browser
2. A local HTTP server starts on `http://localhost:5000`
3. Review individual releases in the "By Unit" tab
4. Check the box next to each release you approve for deletion
5. Approval selections are automatically saved (persistent across sessions)
6. Click "Send Emails for Approved Releases" button when ready
7. Emails are sent ONLY to owners of approved releases
8. Press Ctrl+C to stop the server

**Features**:
- Per-release approval granularity (checkbox for each release)
- Persistent approval state (saved to JSON file, can resume later)
- Real-time approval counts displayed in control panel
- Bulk actions:
  - "Select All Visible" - Select all releases in current tab/chiplet
  - "Clear All Selections" - Clear all checkboxes
- Server runs on localhost:5000 (not accessible remotely)
- Safe: Only approved releases trigger emails

**Requirements**:
```bash
# Install required Python packages
pip install Flask==3.0.0 Flask-CORS==4.0.0
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Advanced Options

```bash
# Custom age threshold (60 days instead of 90)
python3 agur_release_cleanup.py --age-threshold 60

# Specific units only
python3 agur_release_cleanup.py --units prt,fdb,pmux

# Custom number of parallel processes
python3 agur_release_cleanup.py --parallel 20

# Custom output directory
python3 agur_release_cleanup.py --output-dir /tmp/cleanup_reports

# Quiet mode (minimal output)
python3 agur_release_cleanup.py --quiet
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--age-threshold DAYS` | Age threshold in days | 90 |
| `-c, --chiplet NAMES` | Chiplet name(s), comma-separated, case-insensitive (CPORT, HPORT, HIOPL, NDQ, QNS, TCB, TOP_YC, ALL) | ALL |
| `--dry-run` | Analysis only, no emails or reports | False |
| `--send-emails` | Send emails to owners (otherwise reports only) | False |
| `--email-only` | Send emails only, no reports | False |
| `--interactive` | **NEW**: Start interactive approval server (opens dashboard in browser) | False |
| `--units U1,U2` | Check only specific units | All units |
| `--parallel N` | Number of parallel du processes | 10 |
| `--output-dir DIR` | Output directory for reports | ./cleanup_reports |
| `--test-mode` | Send all emails to avice@nvidia.com (implies --send-emails) | False |
| `--quiet` | Minimal output | False |
| `--help` | Show help message | - |

## Output

### Reports

The utility generates three types of reports in the `cleanup_reports/` directory:

#### 1. Interactive Dashboard (`cleanup_unit_summary_YYYYMMDD_HHMMSS.html`) **NEW**

Modern multi-tab HTML dashboard with Chart.js visualizations:

**Summary Tab**:
- Key metrics cards (releases, reclaimable space, current/after utilization)
- Age distribution bar chart
- Size by chiplet doughnut chart
- Top 10 space consumers table
- Coordination statistics

**By Chiplet Tab**:
- Expand/collapse sections per chiplet
- Units grouped by chiplet with release counts and sizes
- Interactive UI for easy navigation

**By Unit Tab**:
- Complete detailed table (same as old HTML report)
- Unit, chiplet, owner, release count
- All old release area names (not truncated)
- Symlinks and their owners
- Total size per unit-owner pair

**By Owner Tab**:
- Owner-centric aggregated view
- Shows all chiplets and units per owner
- Total releases and size across all units
- Useful for coordinating with owners managing multiple units

#### 2. CSV Report (`cleanup_report_YYYYMMDD_HHMMSS.csv`)

Detailed spreadsheet with columns:
- Unit, Chiplet, Release Directory
- Age (days), Size, Owner
- Release Timestamp
- Has Symlinks, Symlink Names, Symlink Owners
- Requires Coordination
- Recommendation

#### 3. Markdown Summary (`cleanup_summary_YYYYMMDD_HHMMSS.md`)

Executive summary with:
- Overview statistics
- Impact analysis (before/after cleanup)
- Breakdown by chiplet
- Breakdown by owner
- Top 10 largest releases
- Next steps and safety notes

### Emails

Emails are sent to release owners with:
- **TO:** Release owner (unit owner from AGUR_UNITS_TABLE.csv)
- **CC:** Symlink owners (if coordination required) + Chiplet manager + avice@nvidia.com
- **Subject:** `[AGUR] Release Cleanup Required - {size} Can Be Freed`

Email contains:
- Avice logo header
- Summary of old releases
- Coordination section (if needed) with symlink owner details
- Table of all releases with status indicators
- Safe deletion commands
- Verification instructions

### Logs

All activity is logged to:
```
logs/release_cleanup_YYYYMMDD.log
```

## Multi-User Coordination

### Scenario

When a unit owner (e.g., `ykatzav`) creates a release, but fullchip STA/PV/PI users (e.g., `aregev`, `nduanis`) create symlinks to that release:

1. **Detection**: The utility detects symlinks via `ls -l` file ownership
2. **Email**: Group email is sent:
   - TO: `ykatzav@nvidia.com` (release owner)
   - CC: `aregev@nvidia.com`, `nduanis@nvidia.com` (symlink owners)
   - CC: `avice@nvidia.com` (chiplet manager)
   - CC: `avice@nvidia.com` (always CC'd)
3. **Coordination Section**: Email includes table showing:
   - Which symlinks need to be removed
   - Who created each symlink
   - Action required for each user

### Process

1. **Symlink owners** must remove their symlinks first:
   ```bash
   rm /home/agur_backend_blockRelease/block/prt/FC_ww46a_last_sta_rel
   ```

2. **Release owner** can then safely delete the release:
   ```bash
   # Verify no symlinks remain
   find /home/agur_backend_blockRelease/block/prt/ -type l -exec ls -l {} \; | grep "release_name"
   
   # If clean, delete
   rm -rf /home/agur_backend_blockRelease/block/prt/release_dir_name
   ```

## Chiplet Managers

The utility knows about chiplet managers and includes them in email coordination:

| Chiplet | Manager |
|---------|---------|
| CPORT | avice@nvidia.com |
| HPORT | avice@nvidia.com |
| HIOPL | avice@nvidia.com |
| NDQ | arot@nvidia.com |
| TOP_YC | arot@nvidia.com |
| QNS | ohamama@nvidia.com |
| TCB | ohamama@nvidia.com |

**Note:** `avice@nvidia.com` is always CC'd on all emails regardless of chiplet.

Project Manager: `oberkovitz@nvidia.com`

## Safety Features

### Read-Only Operation

- **Never deletes files** - Analysis only
- **Never modifies symlinks** - Detection only
- **Never changes permissions** - Inspection only

### Verification Steps

All deletion commands in emails include verification:

```bash
# 1. Verify no symlinks point to release
find /home/agur_backend_blockRelease/block/UNIT/ -type l -exec ls -l {} \; | grep "release_name"

# 2. If output is empty, safe to delete
# 3. Execute deletion command
```

### Coordination Awareness

- Detects symlinks created by other users
- Sends group emails to all involved parties
- Clearly identifies coordination requirements
- Provides step-by-step coordination process

## Examples

### Example 1: Test Run

```bash
# See what would be found without sending emails
python3 agur_release_cleanup.py --dry-run
```

Output:
```
================================================================================
AGUR Release Cleanup Utility - 2026-01-18 17:00:00
================================================================================
[DRY-RUN MODE] No emails or reports will be generated
Age threshold: 90 days
Parallel processes: 10

Loaded 73 units from AGUR_UNITS_TABLE.csv

Scanning 73 units for releases older than 90 days...
Found 287 old releases across 73 units

Analyzing symlinks...
  Protected by symlinks: 42/287
  Require coordination: 18/287

Extracting owner information from logs...
  Updated 15 release owners from log files

Calculating disk usage (parallel=10)...
  Total reclaimable space: 18.4TB

Grouping releases by owner...
  ykatzav@nvidia.com: 42 releases, 5 units, 3.2TB
  brachas@nvidia.com: 38 releases, 6 units, 2.8TB
  ...

================================================================================
Analysis complete!
================================================================================
```

### Example 2: Test Mode (Emails to Avice Only)

```bash
# Test email formatting without spamming users
python3 agur_release_cleanup.py --test-mode
```

All emails will be sent to `avice@nvidia.com` with subject `[TEST]` prefix.

### Example 3: Specific Units Only

```bash
# Check only CPORT chiplet units
python3 agur_release_cleanup.py --units prt,fdb,pmux,fth,lnd
```

### Example 4: Custom Threshold

```bash
# Find releases older than 60 days
python3 agur_release_cleanup.py --age-threshold 60
```

### Example 5: Reports Only (No Emails)

```bash
# Generate reports for review before sending emails
python3 agur_release_cleanup.py --report-only

# Review reports
cat cleanup_reports/cleanup_summary_20260118_170000.md

# If satisfied, send emails
python3 agur_release_cleanup.py --email-only
```

## Troubleshooting

### Permission Denied Errors

**Problem:** Cannot access unit directories

**Solution:** Ensure you have read permissions to `/home/agur_backend_blockRelease/block/`

### Timeout on Large Directories

**Problem:** `du` commands timing out on very large releases

**Solution:** Increase timeout or reduce parallel processes:
```bash
python3 agur_release_cleanup.py --parallel 5
```

### Missing Units Table

**Problem:** `AGUR_UNITS_TABLE.csv` not found

**Solution:** Run from the correct directory:
```bash
cd /home/scratch.avice_vlsi/cursor/avice_wa_review/agur_release_tracking
python3 agur_release_cleanup.py
```

### Email Sending Failures

**Problem:** SMTP connection failures

**Solution:** Check localhost SMTP is running:
```bash
telnet localhost 25
```

## Maintenance

### Updating Chiplet Managers

Edit the `CHIPLET_MANAGERS` dictionary in the script:

```python
CHIPLET_MANAGERS = {
    'HIOPL': 'avice@nvidia.com',
    'CPORT': 'avice@nvidia.com',
    # ... update as needed
}
```

### Updating Age Threshold Default

Edit the `DEFAULT_AGE_THRESHOLD` constant:

```python
DEFAULT_AGE_THRESHOLD = 90  # Change to desired default
```

## Best Practices

1. **Start with Dry-Run**: Always test with `--dry-run` first
2. **Use Test Mode**: Verify email formatting with `--test-mode`
3. **Review Reports**: Check CSV/Markdown reports before sending emails
4. **Coordinate Early**: For coordination cases, reach out to symlink owners before automated emails
5. **Monitor Results**: Track disk usage after cleanup actions
6. **Run Regularly**: Consider monthly scans to prevent future buildup

## Automation (Future)

While currently run manually, this could be automated:

```bash
# Monthly cron job (first Monday at 9 AM)
0 9 * * 1 [ $(date +\%d) -le 7 ] && cd /home/scratch.avice_vlsi/cursor/avice_wa_review/agur_release_tracking && python3 agur_release_cleanup.py >> logs/cleanup_cron_$(date +\%Y\%m\%d).log 2>&1
```

## Support

For questions or issues:
- **Primary Contact**: avice@nvidia.com (Alon Vice)
- **Project Manager**: oberkovitz@nvidia.com
- **Documentation**: This README and in-script help (`--help`)

## Related Tools

- **agur_disk_monitor.py**: Daily disk usage monitoring and alerts
- **extract_agur_releases.sh**: Extract release information
- **AGUR_UNITS_TABLE.csv**: Unit and owner mapping

## Version History

- **v1.0 (2026-01-18)**: Initial release
  - Release scanning with age filtering
  - Symlink analysis with owner detection
  - Multi-user coordination support
  - Parallel disk usage calculation
  - CSV and Markdown reports
  - Group email notifications
  - Comprehensive safety features

## License

Copyright (c) 2026 Alon Vice (avice@nvidia.com)  
All rights reserved.  
For permissions and licensing, contact: avice@nvidia.com
