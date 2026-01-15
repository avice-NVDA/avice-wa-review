# Runtime Section Enhancement Plan
## Comprehensive Flow Detection Across All IPO Directories

**Issue:** Some users run signoff tools under `ipo*/nbu_signoff/` directories. Current runtime section only detects flows in standard root locations.

**Goal:** Detect ALL flows (completed and running) across ALL IPO-specific directories and present hierarchical view.

---

## 1. Current Runtime Detection (Root-Level Only)

### Flows Detected:
```
workarea/
├── syn_flow/
│   ├── fast_dc/log/fast_dc.log          → Fast DC runtime
│   └── dc/log/dc.log                    → Full DC runtime
├── pnr_flow/nv_flow/{design}.prc.status  → PnR runtime (all IPOs)
├── signoff_flow/
│   ├── star/                            → Star extraction (root level)
│   ├── auto_pt/                         → Auto PT (root level)
│   ├── formal_flow/                     → Formal verification
│   ├── gl-check/                        → GL Check
│   └── pv_flow/                         → PV flows
```

### Limitations:
- ❌ Does not detect IPO-specific signoff flows
- ❌ Does not show RUNNING status for flows
- ❌ No detection of flows in `ipo*/nbu_signoff/` directories
- ❌ Limited visibility into parallel IPO executions

---

## 2. Enhanced Detection Strategy

### A. Directory Structure to Scan

```
workarea/
└── pnr_flow/nv_flow/{design}/
    ├── ipo1000/
    │   └── nbu_signoff/
    │       └── signoff_flow/          ← IPO-specific signoff
    │           ├── star/
    │           ├── auto_pt/
    │           ├── formal_flow/
    │           ├── gl-check/
    │           └── pv_flow/
    ├── ipo1001/
    │   └── nbu_signoff/signoff_flow/
    ├── ipo1100/
    │   └── nbu_signoff/signoff_flow/
    └── ... (all IPOs)
```

### B. Flow Detection Hierarchy

**Level 1: Root Flows (Existing)**
- Synthesis (DC/Fast DC)
- PnR (per IPO from prc.status)

**Level 2: IPO-Specific Signoff Flows (NEW)**
```
For each IPO (ipo1000, ipo1001, ipo1100, ...):
  - Star Extraction
  - Auto PT (multiple work directories)
  - Formal Verification
  - GL Check
  - Physical Verification (LVS, DRC, Antenna)
```

---

## 3. Running Flow Detection

### Status Determination Logic

```python
def detect_flow_status(log_file, completion_marker=None):
    """
    Detect if flow is RUNNING, COMPLETED, FAILED, or STALE
    
    Returns:
        status: 'RUNNING' | 'COMPLETED' | 'FAILED' | 'STALE' | 'NOT_RUN'
        elapsed_time: Time since start (for RUNNING flows)
        last_modified: Minutes since last log update
    """
    
    # 1. Check if log file exists
    if not os.path.exists(log_file):
        return ('NOT_RUN', None, None)
    
    # 2. Get log file age
    mtime = os.path.getmtime(log_file)
    current_time = time.time()
    minutes_since_update = (current_time - mtime) / 60
    
    # 3. Check for completion markers
    if completion_marker and os.path.exists(completion_marker):
        return ('COMPLETED', None, minutes_since_update)
    
    # 4. Check for error patterns in log
    with open(log_file, 'r') as f:
        last_lines = f.readlines()[-50:]  # Check last 50 lines
        for line in last_lines:
            if re.search(r'Error|FAILED|fatal', line, re.I):
                return ('FAILED', None, minutes_since_update)
    
    # 5. Determine if RUNNING based on recent activity
    if minutes_since_update < 5:  # Modified within last 5 minutes
        # Extract start time from log
        start_time = extract_start_time(log_file)
        if start_time:
            elapsed = current_time - start_time
            return ('RUNNING', elapsed, minutes_since_update)
        return ('RUNNING', None, minutes_since_update)
    
    # 6. STALE if not modified recently and no completion marker
    return ('STALE', None, minutes_since_update)
```

### Status Indicators

| Status | Color | Meaning | Display |
|--------|-------|---------|---------|
| RUNNING | Yellow | Log updated <5 min, no completion | ⚙️ RUNNING (2h 15m elapsed) |
| COMPLETED | Green | Completion marker found | ✅ COMPLETED |
| FAILED | Red | Error found in log | ❌ FAILED |
| STALE | Gray | Log >5 min old, no completion | ⏸️ STALE (stopped at X) |
| NOT_RUN | Gray | No log file found | - NOT RUN |

---

## 4. Enhanced Runtime Display

### A. Hierarchical Terminal Output

```
===============================================================================
                              RUNTIME ANALYSIS                                  
===============================================================================

Global Flows:
┌──────────────┬──────────────┬──────────────┬─────────────────┬──────────────┐
│ Stage        │ Category     │ Runtime      │ Start → End     │ Status       │
├──────────────┼──────────────┼──────────────┼─────────────────┼──────────────┤
│ Fast DC      │ Synthesis    │ 0.25 hours   │ 10/15 08:00 → … │ ✅ COMPLETED  │
│ Full DC      │ Synthesis    │ 2.50 hours   │ 10/15 08:15 → … │ ✅ COMPLETED  │
└──────────────┴──────────────┴──────────────┴─────────────────┴──────────────┘

PnR Flows (per IPO):
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────────┐
│ IPO          │ Runtime      │ Start → End  │ Status       │ Current Stage    │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────────┤
│ IPO1000      │ 5.25 hours   │ 10/15 09:00  │ ✅ COMPLETED  │ postroute        │
│ IPO1001      │ 3.15 hours   │ 10/15 10:00  │ ⚙️ RUNNING    │ route (2h 30m)   │
│ IPO1100      │ -            │ -            │ - NOT RUN    │ -                │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘

Signoff Flows (per IPO):
▼ IPO1000 (expand for details)
  ├─ Star Extraction:   1.5 hours     ✅ COMPLETED  (10/15 14:00 → 15:30)
  ├─ Auto PT:           2.2 hours     ✅ COMPLETED  (18 work directories)
  ├─ Formal Verify:     0.8 hours     ✅ COMPLETED  (3 flows)
  ├─ GL Check:          0.3 hours     ✅ COMPLETED  
  └─ PV Flows:
      ├─ LVS:           0.5 hours     ✅ COMPLETED
      ├─ DRC:           1.2 hours     ⚙️ RUNNING (45m elapsed)
      └─ Antenna:       -             - NOT RUN

▼ IPO1001 (expand for details)
  ├─ Star Extraction:   -             ⏸️ STALE (log 2h old)
  ├─ Auto PT:           -             - NOT RUN
  ├─ Formal Verify:     0.9 hours     ✅ COMPLETED
  └─ ... (collapsed flows)

□ IPO1100 (collapsed - click to expand)
```

### B. Enhanced HTML Report Features

**New Sections:**

1. **Real-Time Flow Dashboard**
   - Live status indicators (green/yellow/red/gray)
   - Progress bars for RUNNING flows
   - Last update timestamp
   - Elapsed time counters

2. **IPO-Level Drill-Down**
   - Expandable/collapsible IPO sections
   - Per-IPO timeline visualization
   - Parallel execution detection (multiple flows running simultaneously)
   - Resource utilization (estimated based on active flows)

3. **Flow History Timeline**
   - Gantt chart showing flow execution over time
   - Identify bottlenecks and parallel execution opportunities
   - Visual indication of idle time between flows

4. **Active Flow Monitoring**
   - Dedicated section for RUNNING flows
   - Auto-refresh indicator (manual refresh required)
   - Quick links to log files

---

## 5. Implementation Plan

### Phase 1: IPO Directory Scanner (Week 1)

**Files to Modify:**
- `avice_wa_review.py` → `run_runtime_analysis()`

**New Methods:**
```python
def _scan_ipo_directories(self) -> Dict[str, Dict]:
    """Scan all IPO directories for signoff flows"""
    
def _detect_ipo_signoff_flows(self, ipo_path: str) -> Dict:
    """Detect all signoff flows for specific IPO"""
    
def _get_flow_status(self, log_file: str, completion_marker: str = None) -> Tuple:
    """Determine flow status (RUNNING/COMPLETED/FAILED/STALE)"""
```

### Phase 2: Running Flow Detection (Week 1)

**Logic:**
1. Check log file modification time
2. Extract start time from log content
3. Calculate elapsed time for RUNNING flows
4. Display live status with elapsed time

**Status Algorithm:**
- Last modified < 5 min → RUNNING
- Completion marker exists → COMPLETED
- Error pattern found → FAILED
- Last modified > 5 min, no completion → STALE

### Phase 3: Enhanced Terminal Display (Week 2)

**Components:**
1. Global flows table (existing + enhanced)
2. PnR flows table (existing + status column)
3. **NEW:** IPO signoff flows section
   - Collapsible/expandable per IPO
   - Hierarchical tree view
   - Status indicators

### Phase 4: Enhanced HTML Report (Week 2)

**New HTML Sections:**
1. Real-time flow dashboard (status cards)
2. IPO drill-down tables (per-IPO signoff details)
3. Timeline visualization (Gantt chart using Chart.js)
4. Active flows monitoring section

**JavaScript Features:**
- Expandable/collapsible IPO sections
- Filter by status (show only RUNNING, FAILED, etc.)
- Search by IPO or flow name
- Export to CSV functionality

### Phase 5: Testing & Validation (Week 3)

**Test Cases:**
1. Workarea with root-level signoff flows only
2. Workarea with IPO-specific signoff flows only
3. Workarea with mixed (root + IPO-specific)
4. Workarea with RUNNING flows
5. Workarea with FAILED/STALE flows
6. Empty workarea (no flows run yet)

**Validation:**
- Verify all IPO directories are scanned
- Verify status detection accuracy
- Verify timestamps are correct
- Verify HTML report completeness

---

## 6. Expected Benefits

### User Benefits:
1. ✅ **Complete Visibility:** See ALL flows across ALL IPOs
2. ✅ **Real-Time Status:** Know which flows are currently running
3. ✅ **Parallel Tracking:** Identify flows running simultaneously
4. ✅ **Bottleneck Detection:** See where time is spent
5. ✅ **Quick Navigation:** Jump to specific IPO/flow details

### Technical Benefits:
1. ✅ **Scalable:** Handles any number of IPOs
2. ✅ **Flexible:** Works with root-level or IPO-specific flows
3. ✅ **Accurate:** Reliable status detection
4. ✅ **Maintainable:** Modular, well-documented code
5. ✅ **Performant:** Efficient directory scanning

---

## 7. API Design

### New Configuration

```python
# Runtime detection configuration
RUNTIME_CONFIG = {
    'running_threshold_minutes': 5,  # Log updated < 5 min = RUNNING
    'scan_ipo_signoff': True,        # Enable IPO-specific flow detection
    'detect_parallel_flows': True,   # Track simultaneous executions
    'timeline_visualization': True,  # Generate Gantt charts in HTML
}
```

### Data Structure

```python
RuntimeData = {
    'global_flows': {
        'Fast DC': {
            'runtime': '0.25 hours',
            'start': '10/15 08:00',
            'end': '10/15 08:15',
            'status': 'COMPLETED',
            'log_file': '/path/to/fast_dc.log'
        },
        # ... more global flows
    },
    'pnr_flows': {
        'ipo1000': {
            'runtime': '5.25 hours',
            'start': '10/15 09:00',
            'end': '10/15 14:15',
            'status': 'COMPLETED',
            'current_stage': 'postroute',
            'prc_status': '/path/to/prc.status'
        },
        # ... more IPOs
    },
    'ipo_signoff_flows': {
        'ipo1000': {
            'star': {
                'runtime': '1.5 hours',
                'status': 'COMPLETED',
                'start': '10/15 14:00',
                'end': '10/15 15:30',
                'log_file': '/path/to/star.log'
            },
            'auto_pt': {
                'runtime': '2.2 hours',
                'status': 'COMPLETED',
                'work_dirs': 18,
                'log_file': '/path/to/auto_pt.log'
            },
            # ... more signoff flows
        },
        # ... more IPOs
    },
    'running_flows': [
        {
            'ipo': 'ipo1001',
            'flow': 'DRC',
            'elapsed': '45 minutes',
            'log_file': '/path/to/drc.log'
        }
    ]
}
```

---

## 8. Success Criteria

1. ✅ Detects flows in BOTH root and IPO-specific directories
2. ✅ Accurately identifies RUNNING flows (< 5 min activity)
3. ✅ Shows elapsed time for RUNNING flows
4. ✅ Provides hierarchical IPO-level view
5. ✅ HTML report includes timeline visualization
6. ✅ Performance: Scans 100+ IPO directories in < 10 seconds
7. ✅ Backwards compatible: Works with existing single-IPO flows

---

## 9. Example Scenarios

### Scenario 1: User Running DRC on IPO1001
```
Terminal Output:
  Signoff Flows:
    IPO1001:
      ├─ Star:     ✅ COMPLETED  (1.2h)
      ├─ Auto PT:  ✅ COMPLETED  (2.5h)
      ├─ LVS:      ✅ COMPLETED  (0.5h)
      ├─ DRC:      ⚙️ RUNNING (45m elapsed, last update: 1 min ago)
      └─ Antenna:  - NOT RUN

HTML Report:
  [Active Flows Dashboard]
  ⚙️ DRC (IPO1001) - Running for 45 minutes
     Last activity: 1 minute ago
     Log: /path/to/ipo1001/nbu_signoff/signoff_flow/pv_flow/...
     [View Log] [Stop Flow] [Refresh Status]
```

### Scenario 2: Multiple IPOs Running in Parallel
```
Terminal Output:
  Active Flows:
    ⚙️ IPO1001 → route (2h 30m elapsed)
    ⚙️ IPO1002 → DRC (45m elapsed)
    ⚙️ IPO1003 → Auto PT (1h 15m elapsed)

HTML Report:
  [Timeline View - Gantt Chart]
  IPO1001: ████████████████████░░░░░░  (PnR route)
  IPO1002: ░░░░░░░░░░░░░░░░░████░░░░░░  (DRC)
  IPO1003: ░░░░░░░░░░░░████████████░░░  (Auto PT)
```

---

## 10. Open Questions

1. **Refresh Mechanism:** Auto-refresh HTML report or manual refresh only?
   - **Recommendation:** Manual refresh (avoid polling overhead)
   - Add "Last updated: [timestamp]" + [Refresh] button

2. **Notification System:** Alert users when flow completes/fails?
   - **Recommendation:** Phase 2 feature (email notifications)
   - Requires monitoring daemon

3. **Historical Data:** Store runtime history for trend analysis?
   - **Recommendation:** Phase 3 feature (database integration)
   - Current: Single snapshot per run

4. **Parallel Execution Warning:** Warn if too many flows running simultaneously?
   - **Recommendation:** Yes - add resource utilization warning
   - Threshold: >5 concurrent flows = WARNING

---

## 11. Next Steps

1. **Review & Approve Plan** → Get Sir avice's feedback
2. **Prototype IPO Scanner** → Test on real workarea
3. **Implement Status Detection** → Validate RUNNING flow detection
4. **Create Enhanced Display** → Terminal + HTML mockups
5. **Full Implementation** → Follow phased approach
6. **Testing & Validation** → Comprehensive test suite
7. **Documentation** → Update user guide

---

**Author:** Alon Vice (avice@nvidia.com)  
**Date:** December 4, 2025  
**Status:** PLANNING - Awaiting Approval

