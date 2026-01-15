# PFNL Unit DB & AGUR Release Area Monitoring

## Summary of Changes

### What Was Added
1. **PFNL Unit DB monitoring** - Now tracks `/home/PFNL_Unit_DB/` in addition to AGUR release area
2. **Two-tier alert system** for shared infrastructure (AGUR release area + PFNL DB)
3. **State tracking** to prevent duplicate 80% warnings

### Alert System

#### Shared Infrastructure (AGUR Release Area + PFNL Unit DB)

| Usage Level | Alert Type | Frequency | Recipients | Description |
|-------------|-----------|-----------|------------|-------------|
| **< 80%** | None | - | - | All clear, no alerts |
| **80-89%** | Warning | **ONE-TIME** | avice@nvidia.com only | Initial warning to plan cleanup |
| **≥ 90%** | Critical | **DAILY at 8:00 AM** | avice + ALL managers* | Daily alerts until resolved |

*ALL managers includes:
- avice@nvidia.com
- arot@nvidia.com (NDQ, TOP_YC)
- ohamama@nvidia.com (QNS, TCB)
- oberkovitz@nvidia.com (Project Manager)

#### Unit Workareas (existing behavior, unchanged)

| Usage Level | Recipients |
|-------------|------------|
| **≥ 90%** | Unit owner + avice + chiplet manager |
| **≥ 100%** | Unit owner + avice + chiplet manager + **project manager (oberkovitz)** |

### How It Works

1. **First time reaching 80%:**
   - Send warning email to avice@nvidia.com
   - Record warning in `.disk_monitor_warnings.state` file
   - Email subject: `[WARNING] {Path Name} Disk Usage: 80% (First Alert)`

2. **Between 80-89%:**
   - No additional emails sent (waiting for cleanup or escalation)
   - User sees in logs: "WARNING SENT" status

3. **Reaching 90% or above:**
   - Send daily critical alerts to avice + ALL managers
   - Email subject: `[CRITICAL] {Path Name} Disk Usage: {percentage}%`
   - Management escalation notice included in email

4. **Dropping below 80%:**
   - Clear warning state (allows new 80% warning if it rises again)
   - No emails sent while below 80%

### State File Management

**File:** `.disk_monitor_warnings.state`

- Automatically created when first 80% warning is sent
- Tracks which paths have received 80% warnings
- Automatically cleared when usage drops below 80%
- Plain text format (one path name per line)
- No manual intervention needed

**Example content:**
```
AGUR Release Area
PFNL Unit DB
```

### Email Examples

#### 80% Warning Email (One-Time)
- **To:** avice@nvidia.com
- **CC:** None
- **Subject:** [WARNING] PFNL Unit DB Disk Usage: 82% (First Alert)
- **Content:** 
  - Warning notice (first time alert)
  - Disk information
  - Action required: Plan cleanup
  - Notice: Daily alerts start at 90%

#### 90% Critical Email (Daily)
- **To:** avice@nvidia.com
- **CC:** arot@nvidia.com, ohamama@nvidia.com, oberkovitz@nvidia.com
- **Subject:** [CRITICAL] PFNL Unit DB Disk Usage: 91%
- **Content:**
  - Critical alert notice
  - Management escalation notice (lists all CC'd managers)
  - Disk information
  - Cleanup recommendations
  - Daily alert notice

### Testing

#### Dry Run (No Emails)
```bash
cd /home/scratch.avice_vlsi/cursor/avice_wa_review/agur_release_tracking
python3 agur_disk_monitor.py --dry-run
```

#### Test Mode (Emails to avice only)
```bash
python3 agur_disk_monitor.py --test-mode
```

### Monitoring Output

The script now shows shared infrastructure status in summary:

```
SUMMARY:
  Shared Infrastructure:
    AGUR Release Area: 70% [OK]
    PFNL Unit DB: 7% [OK]
  Total units checked: 73
  Critical units (>=90%): 10
  Unique owners: 6
  Emails sent: 6 successful, 0 failed
  Execution time: 131.5 seconds
```

Status indicators:
- `[OK]` - Below 80%, no issues
- `[WARNING SENT]` - 80-89%, initial warning already sent
- `[CRITICAL - DAILY ALERTS]` - 90%+, daily alerts active

### Bug Fixes Included

1. **Fixed max_usage calculation** - Now considers both unit usage AND disk summary usage to correctly show the maximum percentage in email headers
2. **Project manager escalation** - oberkovitz@nvidia.com now correctly receives emails at 100%+ (applies to both units and shared infrastructure)

### Files Modified

- `agur_disk_monitor.py` - Main script with all new features

### Files Created (Auto-Generated)

- `.disk_monitor_warnings.state` - Tracks 80% warning state (auto-managed)

### Backward Compatibility

✅ All existing functionality preserved:
- Unit monitoring unchanged (still uses --threshold flag, default 90%)
- User email format unchanged
- Existing cron job works without modification
- Existing disable mechanism works

### Next Steps

1. **Review this summary** ✅
2. **Test with --dry-run** ✅
3. **Test with --test-mode** (optional, sends test emails to avice)
4. **Deploy to production** (already active via cron at 8:00 AM daily)

### Questions?

Contact: Alon Vice (avice@nvidia.com)

---

**Date:** January 1, 2026
**Version:** 2.0 (Added PFNL monitoring + two-tier alerts)

