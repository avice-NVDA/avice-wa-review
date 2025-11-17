# AGUR Disk Usage Monitor

## Overview
Automated daily disk monitoring system for all AGUR units. Checks disk usage and sends email alerts when units reach >=90% capacity.

## 🚀 Production Deployment Status

**✅ LIVE** - Deployed on **November 2, 2025**

- **Server**: `tlv02-cron-01`
- **Schedule**: Daily at **8:00 AM** (robust version with failure alerts)
- **Cron Entry**:
  ```cron
  0 8 * * * cd /home/avice/scripts/avice_wa_review/agur_release_tracking && /home/utils/Python/builds/3.11.9-20250715/bin/python3 agur_disk_monitor.py >> logs/disk_alert_$(date +\%Y\%m\%d).log 2>&1 || echo "AGUR Disk Monitor failed on $(date)" | mail -s "[ERROR] AGUR Disk Monitor Failed" avice@nvidia.com
  ```
- **Log Location**: `/home/avice/scripts/avice_wa_review/agur_release_tracking/logs/disk_alert_YYYYMMDD.log`
- **Monitoring**: Check daily logs after 8:00 AM for execution status
- **Owner**: avice@nvidia.com

### Verify Production Status
```bash
# SSH to cron server
ssh tlv02-cron-01

# Check cron is installed
crontab -l | grep agur_disk_monitor

# View today's log (after 8 AM)
tail -50 /home/avice/scripts/avice_wa_review/agur_release_tracking/logs/disk_alert_$(date +%Y%m%d).log

# Check if emails were sent
grep "\[EMAIL\]" /home/avice/scripts/avice_wa_review/agur_release_tracking/logs/disk_alert_$(date +%Y%m%d).log
```

## Features
- ✅ Monitors all 72 AGUR units from AGUR_UNITS_TABLE.csv
- ✅ Groups emails by owner (one email per owner)
- ✅ Individual email for 1 critical unit
- ✅ Consolidated email for 2+ critical units per owner
- ✅ CC's avice@nvidia.com on all emails
- ✅ Continues on email failures, notifies avice
- ✅ Daily logging with 30-day retention
- ✅ Disable/enable control via file

## Quick Start

### Test Run (No Emails)
```bash
cd /home/avice/scripts/avice_wa_review/agur_release_tracking
python3 agur_disk_monitor.py --dry-run
```

### Production Run (Sends Emails)
```bash
cd /home/avice/scripts/avice_wa_review/agur_release_tracking
python3 agur_disk_monitor.py
```

### Test Specific Units
```bash
python3 agur_disk_monitor.py --dry-run --units qcorer,pscc,dqavo
```

### Custom Threshold
```bash
python3 agur_disk_monitor.py --dry-run --threshold 85
```

## Disable/Enable Control

### Disable Monitor
```bash
# Simple disable
touch .disk_monitor_disabled

# Disable with reason
echo "Maintenance window" > .disk_monitor_disabled
echo "Testing new email format" > .disk_monitor_disabled
```

### Re-enable Monitor
```bash
rm .disk_monitor_disabled
```

### Check Status
```bash
# Check if disabled
ls .disk_monitor_disabled 2>/dev/null && echo "DISABLED" || echo "ENABLED"

# Run dry-run to see status
python3 agur_disk_monitor.py --dry-run
```

## Cron Setup

Add to your crontab (`crontab -e`):

```bash
# AGUR Daily Disk Usage Alert Monitor (8:00 AM daily)
0 8 * * * cd /home/avice/scripts/avice_wa_review/agur_release_tracking && /home/utils/Python/builds/3.11.9-20250715/bin/python3 agur_disk_monitor.py >> logs/disk_alert_$(date +\%Y\%m\%d).log 2>&1

# Clean up old logs (9:00 AM daily, keep 30 days)
0 9 * * * find /home/avice/scripts/avice_wa_review/agur_release_tracking/logs/disk_alert_*.log -mtime +30 -delete
```

## Integration with avice_wa_review.py

The main `avice_wa_review.py` script now has email alerts **disabled by default**.

### Manual Email Alert (if needed)
```bash
# Run workarea review WITH email alert
/home/avice/scripts/avice_wa_review_launcher.csh -u qcorer -s setup --send-disk-alert

# Run workarea review WITHOUT email alert (default)
/home/avice/scripts/avice_wa_review_launcher.csh -u qcorer -s setup
```

## Logs

### View Today's Log
```bash
tail -f logs/disk_alert_$(date +%Y%m%d).log
```

### View Recent Logs
```bash
ls -lt logs/disk_alert_*.log | head -5
```

### Find Critical Units in Logs
```bash
grep "\[CRITICAL\]" logs/disk_alert_20251030.log
```

## Email Format

### Single Unit Email
- TO: owner@nvidia.com
- CC: avice@nvidia.com
- Subject: [CRITICAL] Disk Usage Alert: 95% on /mount/point
- Body: Avice logo + usage percentage + unit details + cleanup recommendations

### Multiple Units Email (Consolidated)
- TO: owner@nvidia.com
- CC: avice@nvidia.com
- Subject: [CRITICAL] Disk Usage Alert: 3 AGUR units at >=90%
- Body: Avice logo + table of all critical units + cleanup recommendations

## Troubleshooting

### No Emails Received
1. Check if monitor is disabled: `ls .disk_monitor_disabled`
2. Check logs: `tail logs/disk_alert_$(date +%Y%m%d).log`
3. Test with dry-run: `python3 agur_disk_monitor.py --dry-run`
4. Check email failures in log

### Script Not Running via Cron
1. Check crontab: `crontab -l | grep agur_disk_monitor`
2. Check cron logs: `/var/log/cron`
3. Verify Python path: `/home/utils/Python/builds/3.11.9-20250715/bin/python3 --version`
4. Test manually: `python3 agur_disk_monitor.py --dry-run`

### Disable File Not Working
1. Check file location: `pwd` should be `agur_release_tracking/`
2. Check file name: `.disk_monitor_disabled` (with leading dot)
3. Test: `python3 agur_disk_monitor.py --dry-run` should show "DISABLED"

## Current Status (as of Oct 30, 2025)

**Critical Units (>=90%): 13 units**

| Owner | Units | Count |
|-------|-------|-------|
| thadad | ftos, ir | 2 |
| nkahaz | psca, pscb | 2 |
| siddharthasa | dqaa, dqaci, dqamco | 3 |
| abarman | dqamdo, dqavi, dqs | 3 |
| gnarla | dqavo, tecorel | 2 |
| eelgabsi | eds | 1 |

**Expected Emails**: 6 emails daily (one per owner)

## Contact

**Author**: Alon Vice (avice@nvidia.com)  
**Date**: October 30, 2025
