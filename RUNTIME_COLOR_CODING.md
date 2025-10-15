# Runtime Table Color Coding Enhancement

## Overview
Enhanced the Runtime Summary Table to use color coding for visual identification of crashed and running stages.

## Color Scheme

| Status | Color | Visual Indicator | Use Case |
|--------|-------|------------------|----------|
| **CRASHED** | 🔴 RED | Entire row in red | Formal verification tool crashes, flow errors |
| **RUNNING** | 🟡 YELLOW | Entire row in yellow | Currently executing stages |
| **COMPLETED** | ⚪ Default | Normal white/default | Successfully completed stages |

## Implementation Details

### Detection Logic

**CRASHED Detection:**
- Checks if "CRASHED" appears in the runtime or end columns
- Applied to formal verification crashes (FM-036, FM-008, CMD-081 errors)
- Shows runtime + "(CRASHED)" marker

**RUNNING Detection:**
- Checks if end timestamp is "RUNNING"
- Applied to currently executing stages
- Updated within last 5 minutes of file modification

### Modified Functions

1. **`_print_runtime_summary_table()` (lines 13576-13595)**
   - Added color determination logic based on runtime/end status
   - RED for CRASHED
   - YELLOW for RUNNING
   - Default for completed

2. **`_extract_formal_runtime()` (lines 13188-13206)**
   - Added crash detection for formal verification
   - Checks for error patterns: `FM-036`, `FM-008`, `CMD-081`
   - Appends "(CRASHED)" to runtime string
   - Extracts elapsed time even for crashed runs

## Example Output

### Crashed Formal Verification (RED)
```
  Category     Stage                       Runtime                 Start       End        
  ------------ --------------------------- ----------------------- ----------- -----------
  Construction Fast DC                     0.48 hours              09/08 18:34 09/08 19:03
  [RED] Signoff      Formal (rtl_vs_pnr_fm)      0.22 hours (CRASHED)    10/12 13:58 10/12 14:11 [/RED]
  Signoff      Auto PT                     1.75 hours              10/12 14:29 10/12 16:14
```

### Running Stage (YELLOW)
```
  Category     Stage                       Runtime                 Start       End        
  ------------ --------------------------- ----------------------- ----------- -----------
  Construction PnR (ipo1000)               32.93 hours             08/15 07:33 RUNNING
  [YELLOW] Signoff      Star                        In progress             10/14 10:00 RUNNING [/YELLOW]
```

### Completed Stages (Default)
```
  Category     Stage                       Runtime                 Start       End        
  ------------ --------------------------- ----------------------- ----------- -----------
  Construction DC                          7.68 hours              08/14 23:03 08/15 06:44
  Signoff      Auto PT                     0.76 hours              08/16 17:58 08/16 18:43
```

## Benefits

✅ **Instant Visual Feedback**: Crashed/running stages immediately visible
✅ **Better Debugging**: Red rows draw attention to problematic flows
✅ **Status Awareness**: Yellow indicates flows still in progress
✅ **Consistent with Other Sections**: Matches color scheme used in formal verification section
✅ **No Performance Impact**: Color check is O(1) per row

## Testing

### Test Workarea: nvrisc (with crashes)
- ✅ Both formal verification crashes shown in RED
- ✅ Runtime includes "(CRASHED)" marker
- ✅ Other stages shown in default color

### Expected Behavior
- Formal crashes: RED with "(CRASHED)"
- Running stages: YELLOW with "RUNNING"
- Completed stages: Default/white
- Console color codes: `\033[31m` (red), `\033[33m` (yellow), `\033[0m` (reset)

---

*Enhancement completed: October 14, 2025*  
*Implemented by: AI Assistant*  
*Requested by: Sir avice*
