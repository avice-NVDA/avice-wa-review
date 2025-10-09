# Section Header Enhancement

## Overview
Section headers now include index numbers that correspond to the INDEX.md document, making it easier to navigate between the terminal output and the documentation.

## Changes Made

### Code Changes (Lines 207-224)
Added `STAGE_INDEX` dictionary to map each `FlowStage` to its corresponding index:

```python
# Stage index mapping for display (corresponds to INDEX.md)
STAGE_INDEX = {
    FlowStage.SETUP: 1,
    FlowStage.RUNTIME: 2,
    FlowStage.SYNTHESIS: 3,
    FlowStage.PNR_ANALYSIS: 4,
    FlowStage.CLOCK_ANALYSIS: 5,
    FlowStage.FORMAL_VERIFICATION: 6,
    FlowStage.PARASITIC_EXTRACTION: 7,
    FlowStage.SIGNOFF_TIMING: 8,
    FlowStage.PHYSICAL_VERIFICATION: 9,
    FlowStage.GL_CHECK: 10,
    FlowStage.ECO_ANALYSIS: 11,
    FlowStage.NV_GATE_ECO: 12,
    FlowStage.BLOCK_RELEASE: 13,
    FlowStage.COMMON: 14,
    FlowStage.PLACE_ROUTE: 15,  # Placeholder, not commonly used
}
```

### Updated Method (Line 494-498)
Modified `print_header()` to include index numbers:

```python
def print_header(self, stage: FlowStage):
    """Print section header with index number"""
    stage_num = STAGE_INDEX.get(stage, "")
    stage_prefix = f"[{stage_num}] " if stage_num else ""
    print(f"\n{'-' * 35} {Color.GREEN}{stage_prefix}{stage.value}{Color.RESET} {'-' * 35}")
```

## Visual Comparison

### Before
```
---------------------------------------- Setup ----------------------------------------
---------------------------------------- Synthesis (DC) ----------------------------------------
---------------------------------------- PnR Analysis ----------------------------------------
---------------------------------------- Signoff Timing (PT) ----------------------------------------
```

### After
```
----------------------------------- [1] Setup -----------------------------------
----------------------------------- [2] Runtime -----------------------------------
----------------------------------- [3] Synthesis (DC) -----------------------------------
----------------------------------- [4] PnR Analysis -----------------------------------
```

## Complete Section Index

When running `avice_wa_review.py`, you'll now see these numbered sections:

| Index | Section Name                        | FlowStage                   |
|-------|-------------------------------------|----------------------------|
| **1** | Setup                               | `SETUP`                    |
| **2** | Runtime                             | `RUNTIME`                  |
| **3** | Synthesis (DC)                      | `SYNTHESIS`                |
| **4** | PnR Analysis                        | `PNR_ANALYSIS`             |
| **5** | Clock Analysis                      | `CLOCK_ANALYSIS`           |
| **6** | Formal Verification                 | `FORMAL_VERIFICATION`      |
| **7** | Parasitic Extraction (Star)         | `PARASITIC_EXTRACTION`     |
| **8** | Signoff Timing (PT)                 | `SIGNOFF_TIMING`           |
| **9** | Physical Verification (PV)          | `PHYSICAL_VERIFICATION`    |
| **10** | GL Checks                          | `GL_CHECK`                 |
| **11** | ECO Analysis                       | `ECO_ANALYSIS`             |
| **12** | NV Gate ECO                        | `NV_GATE_ECO`              |
| **13** | Block Release                      | `BLOCK_RELEASE`            |
| **14** | COMMON                             | `COMMON`                   |
| **15** | Place & Route (PnR)                | `PLACE_ROUTE`              |

## Benefits

1. **Easy Navigation**: Quickly reference sections between terminal output and INDEX.md
2. **Progress Tracking**: Know exactly which stage (by number) you're reviewing
3. **Documentation Alignment**: Perfect correlation between code behavior and documentation
4. **User-Friendly**: Clear, numbered progression through the analysis stages

## Usage Example

When running a complete review:

```bash
python avice_wa_review.py /path/to/workarea
```

The output will show:
```
[Logo and initialization...]

----------------------------------- [1] Setup -----------------------------------
  Environment: /home/user/workarea
  Top Hierarchy: my_design
  Tag: v1.0
  IPO: ipo1
  
----------------------------------- [2] Runtime -----------------------------------
  Total Runtime: 5h 30m
  [Runtime summary table...]
  
----------------------------------- [3] Synthesis (DC) -----------------------------------
  QoR Report: /path/to/qor.rpt
  Area: 1234.56 um^2
  ...

[Continue through all numbered sections...]

----------------------------------- [4] PnR Analysis -----------------------------------
  PRC Status: COMPLETE
  [PnR analysis details...]
```

## Related Files

- **avice_wa_review.py** (Lines 207-224, 494-498) - Implementation
- **INDEX.md** - Complete script index with section references
- **README_avice_wa_review.md** - User documentation

---

*Enhancement added: October 9, 2025*

