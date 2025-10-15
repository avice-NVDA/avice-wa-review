# AGUR Release Table Auto-Update System

## Overview

The AGUR units table is automatically checked and updated whenever you use the `--unit` flag with `avice_wa_review.py`. This ensures you're always analyzing the latest released workareas.

## How It Works

### Automatic Update Flow

```
User runs: avice_wa_review_launcher.csh --unit prt
    ↓
Script checks: Is AGUR_UNITS_TABLE.txt outdated?
    ↓
If YES → Auto-regenerate table from release logs
    ↓
If NO → Use existing table
    ↓
Look up workarea path for "prt"
    ↓
Run analysis on that workarea
```

### Update Detection Logic

The system checks:
1. **Table file timestamp** - When was the table last updated?
2. **Release area timestamps** - When were new releases made?
3. **Comparison** - If any release is newer than the table → auto-update

**Checked locations:**
- `/home/agur_backend_blockRelease/block/prt/last_sta_rel`
- `/home/agur_backend_blockRelease/block/pmux/last_sta_rel`
- `/home/agur_backend_blockRelease/block/fdb/last_sta_rel`
- `/home/agur_backend_blockRelease/block/fth/last_sta_rel`
- `/home/agur_backend_blockRelease/block/lnd/last_sta_rel`

## Files Involved

| File | Purpose |
|------|---------|
| `check_and_update_agur_table.sh` | Auto-update checker script |
| `extract_agur_releases.sh` | Table extraction/generation script |
| `AGUR_UNITS_TABLE.txt` | The units table (auto-updated) |

## Usage Scenarios

### 1. Automatic Update (Recommended)

**Just use `--unit` flag** - updates happen automatically!

```bash
# The script auto-checks for updates
/home/avice/scripts/avice_wa_review_launcher.csh --unit prt

# Example output when new release detected:
# [INFO] New release detected for unit: pmux
# [INFO] Updating AGUR units table with latest release data...
# [INFO] Table successfully updated
# [INFO] Unit 'prt' found in release table
```

**When auto-update runs:**
- On first use (table doesn't exist)
- When a new release is detected
- Runs silently in the background (~5-10 seconds)

### 2. Manual Update

Force update anytime:

```bash
cd /home/avice/scripts/avice_wa_review

# Check if update needed
./check_and_update_agur_table.sh

# Force update regardless
./check_and_update_agur_table.sh --force

# Silent mode (for scripts)
./check_and_update_agur_table.sh --quiet
```

### 3. Direct Extraction

Regenerate table directly:

```bash
cd /home/avice/scripts/avice_wa_review
./extract_agur_releases.sh
```

## Update Frequency

### Automatic
- ✅ Every time you use `--unit` flag
- ✅ Only updates if new releases detected
- ✅ Minimal overhead (~0.1s if up-to-date)

### Manual Options
- Update on demand: Run checker script manually
- Scheduled updates: Set up cron job (see below)

## Setting Up Scheduled Updates (Optional)

For environments with frequent releases, set up a cron job:

```bash
# Edit crontab
crontab -e

# Add this line to update table every hour
0 * * * * /home/avice/scripts/avice_wa_review/check_and_update_agur_table.sh --quiet

# Or update every 4 hours
0 */4 * * * /home/avice/scripts/avice_wa_review/check_and_update_agur_table.sh --quiet

# Or update daily at 8 AM
0 8 * * * /home/avice/scripts/avice_wa_review/check_and_update_agur_table.sh --quiet
```

**Benefits of cron job:**
- Table always fresh when you need it
- No waiting for auto-update when running analysis
- Updates happen during off-peak hours

**When NOT needed:**
- If you use `--unit` flag regularly (auto-updates anyway)
- If releases are infrequent (once a day or less)

## Troubleshooting

### Issue: "Table is outdated but didn't auto-update"

**Cause:** Auto-update only runs when using `--unit` flag

**Solutions:**
```bash
# Option 1: Force update manually
./check_and_update_agur_table.sh --force

# Option 2: Set up cron job (see above)
```

### Issue: "Failed to auto-update release table"

**Possible causes:**
- Permission issues accessing release area
- Extraction script not found
- Network/filesystem issues

**Solutions:**
```bash
# Check permissions
ls -l /home/agur_backend_blockRelease/block/prt/last_sta_rel

# Check script exists and is executable
ls -l check_and_update_agur_table.sh extract_agur_releases.sh

# Try manual update to see error details
./check_and_update_agur_table.sh --force
```

### Issue: "Table update check timed out"

**Cause:** Update took longer than 60 seconds (very rare)

**Solution:**
- Wait a few minutes
- Run manual update: `./check_and_update_agur_table.sh --force`
- Check if release area is accessible

### Issue: "Unit not found even after update"

**Possible causes:**
1. Unit not in tracked chiplets yet
2. No `last_sta_rel` symlink for that unit
3. Release log file missing or corrupted

**Solutions:**
```bash
# Check if unit has releases
ls -l /home/agur_backend_blockRelease/block/<unit>/last_sta_rel

# Check what units are in table
cat AGUR_UNITS_TABLE.txt

# Force regenerate
./extract_agur_releases.sh
```

## Update Logs

The auto-update checker provides feedback:

```bash
# Normal operation (no update needed)
[INFO] Table is up-to-date (last updated: 2025-10-14 12:40:08)

# New release detected
[INFO] New release detected for unit: pmux
[INFO]   Release time: 2025-10-14 15:30:22
[INFO]   Table time:   2025-10-14 12:40:08
[INFO] Updating AGUR units table with latest release data...
[INFO] Table successfully updated

# First-time setup
[INFO] AGUR_UNITS_TABLE.txt not found - first time setup
[INFO] Running initial extraction...
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| **Check if update needed** | ~0.1s | Just timestamp comparison |
| **Full table regeneration** | ~5-10s | Parses all release logs |
| **Auto-update overhead** | ~0.1s | If table is current |

**Impact on workflow:** Minimal - auto-checks are fast!

## Best Practices

### ✅ DO:
- Let auto-update handle it (easiest option)
- Set up cron job if you have frequent releases
- Use `--quiet` flag in automated scripts
- Run manual update after major release events

### ❌ DON'T:
- Manually edit `AGUR_UNITS_TABLE.txt` (will be overwritten)
- Delete the checker script (breaks auto-update)
- Run updates too frequently (unnecessary load)

## Integration with Other Scripts

If you write scripts that use the units table:

```bash
#!/bin/bash

# Ensure table is up-to-date before using it
/home/avice/scripts/avice_wa_review/check_and_update_agur_table.sh --quiet

# Now use the table
for unit in prt pmux fdb fth lnd; do
    wa_path=$(grep "^$unit" AGUR_UNITS_TABLE.txt | cut -d'|' -f3 | xargs)
    echo "Processing $unit: $wa_path"
    # Your processing here
done
```

## Summary

| Update Method | When to Use | Frequency |
|---------------|-------------|-----------|
| **Auto-update** | Default (using `--unit` flag) | Every `--unit` invocation |
| **Manual check** | Verify table status | As needed |
| **Force update** | After known releases | As needed |
| **Cron job** | High-frequency releases | Hourly/Daily |

---

**Key Takeaway:** Just use `--unit` flag - auto-update handles everything! 🚀

---

*Last Updated: 2025-10-14*  
*Part of: avice_wa_review - AGUR Release Tracking System*

