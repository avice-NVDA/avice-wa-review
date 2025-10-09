# Section Index Reordering - October 9, 2025

## Change Summary

The section index numbers have been reordered to prioritize Runtime Analysis early in the review output.

## New Section Order

| Index | Section Name                        | Rationale                                      |
|-------|-------------------------------------|------------------------------------------------|
| **1** | Setup                               | Environment and configuration (always first)   |
| **2** | Runtime                             | **NEW POSITION** - Quick overview of timing    |
| **3** | Synthesis (DC)                      | **MOVED FROM 2** - Design synthesis            |
| **4** | PnR Analysis                        | **KEPT** - Place & Route analysis              |
| **5** | Clock Analysis                      | Clock tree metrics                             |
| **6** | Formal Verification                 | Verification status                            |
| **7** | Parasitic Extraction (Star)         | StarRC extraction                              |
| **8** | Signoff Timing (PT)                 | PrimeTime timing                               |
| **9** | Physical Verification (PV)          | DRC/LVS checks                                 |
| **10** | GL Checks                          | Gate-level verification                        |
| **11** | ECO Analysis                       | Engineering change orders                      |
| **12** | NV Gate ECO                        | NVIDIA-specific ECO                            |
| **13** | Block Release                      | Release readiness                              |
| **14** | COMMON                             | Common checks                                  |
| **15** | Place & Route (PnR)                | Placeholder (rarely used)                      |

## Rationale

### Why Runtime is Now #2

**Problem**: Runtime analysis was buried at the end (#14), making it hard to get a quick overview of the workarea's execution performance.

**Solution**: Moved Runtime to position #2, right after Setup, so users can immediately see:
- Total runtime summary
- Stage-by-stage timing
- Performance bottlenecks
- Timeline visualization

### Benefits

1. **Quick Performance Overview**: See runtime metrics early in the review
2. **Better Context**: Know upfront how long each stage took before diving into details
3. **Prioritized Information**: Most users want to know "how long did it take?" early
4. **Logical Flow**: Setup → Runtime → Design Flow Stages

## Visual Comparison

### Before (Old Order)
```
[1] Setup
[2] Synthesis (DC)
[3] Place & Route (PnR)
[4] PnR Analysis
...
[14] Runtime          <- Hidden at the end!
```

### After (New Order)
```
[1] Setup
[2] Runtime           <- Immediately visible!
[3] Synthesis (DC)
[4] PnR Analysis
...
```

## Terminal Output Example

When running `avice_wa_review.py`, the output now shows:

```
+===+ +--+ +--+ +=+ +===+ +===+
|   | |  | |  | | | |     |    
|===| |  +-+  | | | |     |=== 
|   |  |     |  | | |     |    
|   |   +---+   +=+ +===+ +===+
   ~ Alon Vice Tools ~

----------------------------------- [1] Setup -----------------------------------
Workarea: /home/user/design
Top Hierarchy: my_block
Tag: v1.0
IPO: ipo1

----------------------------------- [2] Runtime -----------------------------------
                                    Runtime Summary                              
================================================================================
Stage                          Category           Runtime        
--------------------------------------------------------------------------------
PnR: place_opt                 PnR               2h 15m 30s     
PnR: route                     PnR               1h 45m 20s     
DC Synthesis                   Synthesis         45m 10s        
StarRC Extraction              Star              30m 05s        
PrimeTime Analysis             PT                25m 45s        
...
Total Runtime: 5h 30m 15s

----------------------------------- [3] Synthesis (DC) -----------------------------------
QoR Report: /path/to/qor.rpt
Area: 1234.56 um^2
...

----------------------------------- [4] PnR Analysis -----------------------------------
PRC Status: COMPLETE
...
```

## Implementation Details

### Files Modified
1. **avice_wa_review.py** (Lines 207-224)
   - Updated `STAGE_INDEX` dictionary

2. **INDEX.md**
   - Reordered analysis stages documentation
   - Updated Key Features Summary

3. **SECTION_HEADERS.md**
   - Updated section index table
   - Updated examples

### Code Change

```python
# OLD ORDER
STAGE_INDEX = {
    FlowStage.SETUP: 1,
    FlowStage.SYNTHESIS: 2,      # DC was #2
    FlowStage.RUNTIME: 14,       # Runtime was #14
    ...
}

# NEW ORDER
STAGE_INDEX = {
    FlowStage.SETUP: 1,
    FlowStage.RUNTIME: 2,        # Runtime now #2
    FlowStage.SYNTHESIS: 3,      # DC now #3
    FlowStage.PNR_ANALYSIS: 4,
    ...
}
```

## Impact

- ✅ **Backward Compatible**: No functional changes, only display order
- ✅ **Documentation Updated**: INDEX.md and SECTION_HEADERS.md reflect new order
- ✅ **User Experience**: Better information hierarchy
- ✅ **No Breaking Changes**: All functionality remains the same

## Related Documents

- **INDEX.md** - Complete script index with updated section order
- **SECTION_HEADERS.md** - Visual guide showing new header format
- **avice_wa_review.py** - Main script with STAGE_INDEX mapping

---

*Ordering change applied: October 9, 2025*
*Requested by: User preference for early runtime visibility*

