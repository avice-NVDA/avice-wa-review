# Runtime Section - Terminal Output Design
## Compact, Table-Organized, Readable Format

**Design Principles:**
1. ✅ Minimize vertical lines (keep under 50 lines total)
2. ✅ Use tables for structured data
3. ✅ Hierarchical organization (Global → IPO-specific)
4. ✅ Status indicators (emoji/ASCII symbols)
5. ✅ Show only summary + expandable details
6. ✅ Highlight RUNNING flows prominently

---

## Terminal Output Format (Compact Design)

### Option A: Unified Table with IPO Grouping (RECOMMENDED)

```
===============================================================================
                              RUNTIME ANALYSIS                                  
===============================================================================

Global Synthesis:
  Fast DC:  0.25h (10/15 08:00 -> 08:15)  [OK] COMPLETED
  Full DC:  2.50h (10/15 08:15 -> 10:45)  [OK] COMPLETED

PnR + Signoff Summary (per IPO):
┌──────────┬──────────┬─────────────┬────────────────────────────────────────┐
│ IPO      │ PnR      │ Signoff     │ Status & Details                       │
├──────────┼──────────┼─────────────┼────────────────────────────────────────┤
│ IPO1000  │ 5.2h     │ 4.8h        │ [OK] All flows completed               │
│          │          │             │   Star(1.5h) PT(2.2h) Formal(0.8h)     │
│          │          │             │   LVS(0.3h) DRC(0.5h) Ant(0.2h)        │
├──────────┼──────────┼─────────────┼────────────────────────────────────────┤
│ IPO1001  │ 3.1h     │ 1.2h        │ [RUNNING] PnR: route (2h 30m elapsed)  │
│          │ [RUN]    │             │   Signoff: Star(0.8h) PT(0.4h) STALE   │
├──────────┼──────────┼─────────────┼────────────────────────────────────────┤
│ IPO1100  │ -        │ -           │ [--] Not started                       │
├──────────┼──────────┼─────────────┼────────────────────────────────────────┤
│ IPO1101  │ 4.8h     │ 3.2h        │ [RUNNING] Signoff: DRC (45m elapsed)   │
│          │          │ [RUN]       │   PnR completed, DRC in progress       │
└──────────┴──────────┴─────────────┴────────────────────────────────────────┘

Active Flows (RUNNING now):
  [*] IPO1001 -> PnR route       (started: 10/15 10:00, elapsed: 2h 30m)
  [*] IPO1101 -> Signoff DRC     (started: 10/15 12:15, elapsed: 45m)

Total Runtime: 28.5 hours across 4 IPOs (2 running, 1 completed, 1 pending)

Runtime HTML Report:
  Open with: /home/utils/firefox-118.0.1/firefox test_outputs/html/design_avice_runtime_report_20251204_160000.html &

===============================================================================
                    [Completed: 11 flows, Running: 2 flows]
===============================================================================
```

**Line Count:** ~25 lines (compact!)

---

### Option B: Separate Tables (Alternative)

```
===============================================================================
                              RUNTIME ANALYSIS                                  
===============================================================================

Synthesis Flows:
  Fast DC:  0.25h (10/15 08:00 -> 08:15)  [OK]
  Full DC:  2.50h (10/15 08:15 -> 10:45)  [OK]

PnR Flows:
┌──────────┬──────────┬────────────────────┬──────────────────────────────┐
│ IPO      │ Runtime  │ Start -> End       │ Status                       │
├──────────┼──────────┼────────────────────┼──────────────────────────────┤
│ IPO1000  │ 5.2h     │ 10/15 09:00 -> ... │ [OK] postroute               │
│ IPO1001  │ 3.1h     │ 10/15 10:00 -> ... │ [RUN] route (2h 30m)         │
│ IPO1100  │ -        │ -                  │ [--] Not started             │
│ IPO1101  │ 4.8h     │ 10/15 08:30 -> ... │ [OK] postroute               │
└──────────┴──────────┴────────────────────┴──────────────────────────────┘

Signoff Flows (summary per IPO - 6 flows: Star, PT, Formal, LVS, DRC, Ant):
┌──────────┬──────────┬──────────────────────────────────────────────────┐
│ IPO      │ Total    │ Flow Status                                      │
├──────────┼──────────┼──────────────────────────────────────────────────┤
│ IPO1000  │ 4.8h     │ [OK] All 6 completed                             │
│ IPO1001  │ 1.2h     │ [WARN] Star(0.8h) PT(0.4h) completed, 4 pending  │
│ IPO1100  │ -        │ [--] Not started                                 │
│ IPO1101  │ 3.2h     │ [RUN] 5 completed, DRC running (45m)             │
└──────────┴──────────┴──────────────────────────────────────────────────┘

Active Flows:
  [*] IPO1001 -> PnR route   (2h 30m elapsed)
  [*] IPO1101 -> DRC         (45m elapsed)

Total: 28.5h | Completed: 11 flows | Running: 2 flows | Pending: 7 flows
===============================================================================
```

**Line Count:** ~30 lines

---

### Option C: Ultra-Compact Single Table (For Many IPOs)

```
===============================================================================
                              RUNTIME ANALYSIS                                  
===============================================================================

Synthesis: Fast DC(0.2h) [OK] | Full DC(2.5h) [OK]

IPO Status (PnR | Signoff):
┌──────────┬─────────────┬─────────────┬────────────────────────────────┐
│ IPO      │ PnR         │ Signoff     │ Active/Issues                  │
├──────────┼─────────────┼─────────────┼────────────────────────────────┤
│ IPO1000  │ 5.2h [OK]   │ 4.8h [OK]   │ -                              │
│ IPO1001  │ 3.1h [RUN]  │ 1.2h [WARN] │ PnR:route(2h30m) 4 pending     │
│ IPO1100  │ - [--]      │ - [--]      │ Not started                    │
│ IPO1101  │ 4.8h [OK]   │ 3.2h [RUN]  │ DRC(45m)                       │
│ IPO2000  │ 6.1h [OK]   │ 5.5h [OK]   │ -                              │
│ IPO2001  │ - [--]      │ - [--]      │ Not started                    │
│ ... (8 more IPOs, use --verbose to show all)                          │
└──────────┴─────────────┴─────────────┴────────────────────────────────┘

Active: 2 flows running | Total: 28.5h across 14 IPOs | HTML report available
===============================================================================
```

**Line Count:** ~18 lines (ultra-compact for 14 IPOs!)

---

## Verbosity Levels

### Default Mode (Compact - 20-30 lines)
- Shows summary only
- Collapsed signoff details
- "N more IPOs" if >10 IPOs

### Verbose Mode (-v flag)
- Shows all IPOs
- Expanded signoff flow details
- Individual flow timestamps

### Ultra-Verbose Mode (-vv flag)
- Per-flow status with log paths
- Stale flow detection details
- Resource utilization estimates

---

## Status Indicators (ASCII-Safe)

| Symbol | Meaning | Color |
|--------|---------|-------|
| `[OK]` | Completed | Green |
| `[RUN]` | Running | Yellow |
| `[FAIL]` | Failed | Red |
| `[WARN]` | Incomplete/Stale | Orange |
| `[--]` | Not started | Gray |
| `[*]` | Active flow marker | Yellow |

---

## Column Width Guidelines

```
IPO Column:       10 chars (IPO1000)
Runtime Column:   10 chars (5.2h [OK])
Timestamp:        20 chars (10/15 09:00 -> ...)
Status/Details:   40 chars (expandable)
```

**Total Table Width:** ~80 characters (fits standard terminal)

---

## Expandable Details (On-Demand)

**Trigger:** User runs with `--show-ipo IPO1000` flag

```
===============================================================================
                     IPO1000 - DETAILED RUNTIME BREAKDOWN
===============================================================================

PnR Flow:
  Total Runtime: 5.2 hours
  Start: 10/15 09:00  →  End: 10/15 14:12
  Stages:
    ├─ setup:      0.5h  [OK]  (09:00 -> 09:30)
    ├─ edi_plan:   0.8h  [OK]  (09:30 -> 10:18)
    ├─ place:      1.2h  [OK]  (10:18 -> 11:30)
    ├─ cts:        0.9h  [OK]  (11:30 -> 12:24)
    ├─ route:      1.5h  [OK]  (12:24 -> 13:54)
    └─ postroute:  0.3h  [OK]  (13:54 -> 14:12)

Signoff Flows:
  Star Extraction:      1.5h  [OK]  (14:15 -> 15:45)
  Auto PT (18 work):    2.2h  [OK]  (15:50 -> 18:02)
  Formal (3 flows):     0.8h  [OK]  (18:05 -> 18:53)
  LVS:                  0.3h  [OK]  (18:55 -> 19:13)
  DRC:                  0.5h  [OK]  (19:15 -> 19:45)
  Antenna:              0.2h  [OK]  (19:47 -> 19:59)

Total IPO1000 Runtime: 10.0 hours (PnR: 5.2h, Signoff: 4.8h)
===============================================================================
```

---

## Design Rationale

### Why Option A (Unified Table) is RECOMMENDED:

**Pros:**
✅ **Most compact:** Shows PnR + Signoff in single table
✅ **Easy scanning:** Status at a glance
✅ **Scalable:** Works for 1-50 IPOs
✅ **Hierarchical:** Clear grouping of related data
✅ **Actionable:** Highlights RUNNING flows immediately

**Cons:**
⚠️ Details column may wrap for complex statuses

### Fallback Strategy:
- **1-5 IPOs:** Use Option A (Unified Table) with full details
- **6-15 IPOs:** Use Option A with collapsed details
- **16+ IPOs:** Use Option C (Ultra-Compact) + show top 10 + "N more"

---

## Implementation Guidelines

### Terminal Output Generation

```python
def _print_runtime_summary_compact(self, runtime_data, pnr_runtimes, ipo_signoff_data):
    """
    Print compact runtime summary (target: <30 lines)
    """
    
    # 1. Global synthesis (2 lines)
    print("\nGlobal Synthesis:")
    print(f"  Fast DC:  {runtime_data.get('Fast DC', 'N/A')}  [OK]")
    print(f"  Full DC:  {runtime_data.get('Full DC', 'N/A')}  [OK]")
    
    # 2. IPO unified table (1 header + N IPO rows)
    print("\nPnR + Signoff Summary (per IPO):")
    headers = ["IPO", "PnR", "Signoff", "Status & Details"]
    
    # Determine how many IPOs to show
    num_ipos = len(pnr_runtimes)
    show_count = min(num_ipos, 10)  # Show max 10 by default
    
    for ipo in sorted(pnr_runtimes.keys())[:show_count]:
        pnr_status = self._get_pnr_status(ipo, pnr_runtimes)
        signoff_status = self._get_signoff_summary(ipo, ipo_signoff_data)
        details = self._format_ipo_details(ipo, pnr_status, signoff_status)
        
        # Print row (2-3 lines per IPO with details)
        print_table_row(ipo, pnr_status, signoff_status, details)
    
    if num_ipos > show_count:
        print(f"  ... ({num_ipos - show_count} more IPOs, use -v to show all)")
    
    # 3. Active flows section (if any running)
    active_flows = self._get_active_flows(pnr_runtimes, ipo_signoff_data)
    if active_flows:
        print("\nActive Flows (RUNNING now):")
        for flow in active_flows[:5]:  # Show max 5 active
            print(f"  [*] {flow['ipo']} -> {flow['name']}  (elapsed: {flow['elapsed']})")
    
    # 4. Summary line
    print(f"\nTotal Runtime: {total_runtime} | Completed: {n_complete} | Running: {n_running}")
```

### Verbosity Flags

```python
# Default: Compact mode (20-30 lines)
python3 avice_wa_review.py -s runtime

# Verbose: Show all IPOs + expanded details (40-60 lines)
python3 avice_wa_review.py -s runtime -v

# Ultra-verbose: Full details with log paths (80+ lines)
python3 avice_wa_review.py -s runtime -vv

# Show specific IPO details
python3 avice_wa_review.py -s runtime --show-ipo IPO1000
```

---

## Example Output (Real Scenario - 14 IPOs)

```
===============================================================================
                              RUNTIME ANALYSIS                                  
===============================================================================

Global Synthesis:
  Fast DC:  0.25h (10/15 08:00 -> 08:15)  [OK] COMPLETED
  Full DC:  2.50h (10/15 08:15 -> 10:45)  [OK] COMPLETED

PnR + Signoff Summary (per IPO):
┌──────────┬──────────┬─────────────┬────────────────────────────────────────┐
│ IPO      │ PnR      │ Signoff     │ Status & Details                       │
├──────────┼──────────┼─────────────┼────────────────────────────────────────┤
│ IPO1000  │ 5.2h     │ 4.8h        │ [OK] All flows completed               │
│ IPO1001  │ 3.1h     │ 1.2h        │ [RUN] PnR: route (2h 30m)              │
│ IPO1100  │ 4.8h     │ 3.5h        │ [OK] All flows completed               │
│ IPO1101  │ 4.2h     │ 3.2h        │ [RUN] Signoff: DRC (45m)               │
│ IPO2000  │ 6.1h     │ 5.5h        │ [OK] All flows completed               │
│ IPO2001  │ 5.8h     │ 4.9h        │ [OK] All flows completed               │
│ IPO3000  │ 5.5h     │ 4.2h        │ [OK] All flows completed               │
│ IPO3001  │ 5.9h     │ 5.1h        │ [OK] All flows completed               │
│ IPO4000  │ 6.2h     │ 5.8h        │ [OK] All flows completed               │
│ IPO4001  │ 5.7h     │ 5.3h        │ [OK] All flows completed               │
│ ... (4 more IPOs, use -v to show all)                                     │
└──────────┴──────────┴─────────────┴────────────────────────────────────────┘

Active Flows (RUNNING now):
  [*] IPO1001 -> PnR route       (started: 10/15 10:00, elapsed: 2h 30m)
  [*] IPO1101 -> Signoff DRC     (started: 10/15 12:15, elapsed: 45m)

Total Runtime: 78.5 hours across 14 IPOs (2 running, 10 completed, 2 pending)

Runtime HTML Report:
  Open with: /home/utils/firefox-118.0.1/firefox test_outputs/html/design_avice_runtime_report_20251204_160000.html &

===============================================================================
                    [Completed: 72 flows, Running: 2 flows]
===============================================================================
```

**Total Lines:** 28 lines ✅

---

## Summary: Final Recommendation

**Use Option A (Unified Table) with these parameters:**

| Scenario | Display Strategy | Lines |
|----------|-----------------|-------|
| **1-5 IPOs** | Show all with full details | 20-25 |
| **6-10 IPOs** | Show all with compact details | 25-30 |
| **11-20 IPOs** | Show first 10 + "N more" | 28-30 |
| **21+ IPOs** | Show first 10 + summary stats | 28-30 |

**Key Features:**
1. ✅ Always <30 lines in default mode
2. ✅ Table-organized for easy scanning
3. ✅ Highlights RUNNING flows prominently
4. ✅ Shows summary statistics
5. ✅ Expandable with verbosity flags

**Next:** Implement with test plan for 40 units!

