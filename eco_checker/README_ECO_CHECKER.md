# ECO Checker - Standalone ECO Validation Utility

## Overview

Standalone tool for validating ECO TCL files against design rules **before implementation**.  
Features smart workarea auto-detection and comprehensive violation checks.

**Author:** Alon Vice (avice@nvidia.com)  
**Date:** November 6, 2025  
**Status:** ✅ Production Ready

---

## Features

### **Core Checks**
1. **instNotAllowedOnClocks** - Detects non-allowed cells on clock network
   - Enhanced with `-term` checking for `ecoAddRepeater`
   - Validates both NEW and PREVIOUS instances
   
2. **DontUse Cells** - Detects cells that shouldn't be used anywhere
   - Parses GL-Check patterns
   - Flags critical violations
   
3. **ClockCellsOnData** - Identifies clock cells on data paths
   - Informational (potential area optimization)
   - Non-blocking

### **Smart Workarea Detection**
- **Auto-detects** workarea from ECO file location
- Walks up directory tree looking for markers (`signoff_flow/`, `pnr_flow/`, `syn_flow/`)
- Supports override with `--workarea` flag
- Works with multiple units from different workareas

### **Flexible Reference File Discovery**
Priority order:
1. **Explicit paths** (highest priority)
   - `--clock-tree`, `--beflow-config`, `--dont-use`
2. **Workarea override**
   - `--workarea /path/to/workarea`
3. **Auto-detection** (default)
   - Detects from ECO file location

---

## Installation

The tool is already installed and ready to use:
```bash
/home/avice/scripts/avice_wa_review/eco_checker.csh
```

**No setup required** - just run the launcher script!

**Dependencies:**
- Python 3.6+ (tested with 3.11.9) - handled automatically by launcher
- `eco_checker_lib.py` (shared library) - included
- `eco_checker.py` (core script) - called by launcher

---

## Usage

### **Quick Start (Auto-Detection)**

```bash
# Single ECO file (workarea auto-detected)
/home/avice/scripts/avice_wa_review/eco_checker.csh /path/to/workarea/signoff_flow/auto_pt/my_eco.tcl

# Multiple ECO files from same workarea
/home/avice/scripts/avice_wa_review/eco_checker.csh /path/to/workarea/signoff_flow/auto_pt/*.tcl

# Multiple units (each auto-detects its own workarea)
/home/avice/scripts/avice_wa_review/eco_checker.csh \\
    /path/to/pmux_wa/signoff_flow/auto_pt/pmux_eco.tcl \\
    /path/to/ccorea_wa/unit_scripts/ccorea_eco.tcl
```

### **External ECOs (Use Reference Workarea)**

```bash
# Check Radu's ECOs using pmux as reference
/home/avice/scripts/avice_wa_review/eco_checker.csh /path/to/radu/ECO_VIVID_AND_MANUAL/*.tcl \\
    --workarea /home/scratch.brachas_vlsi/.../pmux_rbv_.../
```

### **Explicit Reference Files**

```bash
# No workarea needed - provide files directly
/home/avice/scripts/avice_wa_review/eco_checker.csh my_eco.tcl \\
    --clock-tree /path/to/ClockTree.rpt \\
    --beflow-config /path/to/beflow_config.yaml \\
    --dont-use /path/to/dont_use_patterns.tcl
```

### **Output Modes**

```bash
# Verbose (detailed violations)
/home/avice/scripts/avice_wa_review/eco_checker.csh *.tcl --verbose

# Quiet (summary only - good for scripting)
/home/avice/scripts/avice_wa_review/eco_checker.csh *.tcl --quiet

# No color (for log files)
/home/avice/scripts/avice_wa_review/eco_checker.csh *.tcl --no-color
```

---

## Command-Line Options

```
Positional Arguments:
  eco_files             ECO TCL file(s) to validate (supports wildcards)

Discovery Options:
  --workarea, -w        Workarea path (overrides auto-detection)
  --clock-tree          Path to ClockTree.rpt (overrides workarea)
  --beflow-config       Path to beflow_config.yaml (overrides workarea)
  --dont-use            Path to dont_use patterns file (overrides workarea)

Check Options:
  --skip-clock-check    Skip instNotAllowedOnClocks check
  --skip-dontuse-check  Skip DontUse cells check
  --skip-clock-data     Skip clock cells on data paths check

Output Options:
  --quiet, -q           Minimal output (summary only)
  --verbose, -v         Detailed output with all violations
  --no-color            Disable colored output
  --strict              Exit code 1 even for informational warnings
```

---

## Exit Codes

- **0** : All checks passed
- **1** : Violations found (DontUse or instNotAllowedOnClocks)
- **2** : Error (missing files, parse errors)

---

## Example Workflows

### **Workflow 1: Check Radu's ECOs Before Implementation**

```bash
cd /home/agur_fullchip/chiplets/hport/hport1/fc_func2/signoff_flow/auto_pt/work_31.10.25_11:56/vivid_block_cashing/ECO_VIVID_AND_MANUAL

# Check all 11 ECO files using pmux as reference
/home/avice/scripts/avice_wa_review/eco_checker.csh *.tcl --workarea /home/scratch.brachas_vlsi/.../pmux_rbv_.../

# Expected output:
# - 15,514 ECO commands analyzed
# - 1 violation found (pmux - BUFFCS1D3T6HVT on clock network)
# - Exit code: 1
```

### **Workflow 2: Quick Feedback During ECO Development**

```bash
# Developer creates ECO file in their workarea
cd /home/scratch.avice_vlsi/.../my_workarea/signoff_flow/auto_pt/
vim my_timing_fixes.tcl

# Quick check (workarea auto-detected)
/home/avice/scripts/avice_wa_review/eco_checker.csh my_timing_fixes.tcl

# If violations found, fix and re-check
vim my_timing_fixes.tcl
/home/avice/scripts/avice_wa_review/eco_checker.csh my_timing_fixes.tcl

# Repeat until clean (exit code 0)
```

### **Workflow 3: CI/CD Integration (Automated Validation)**

```bash
#!/bin/bash
# CI script to validate ECOs before commit

/home/avice/scripts/avice_wa_review/eco_checker.csh *.tcl --quiet --no-color

if [ $? -ne 0 ]; then
    echo "[ERROR] ECO validation failed!"
    exit 1
fi

echo "[OK] ECO validation passed"
```

---

## Test Results

### **Test 1: Batch Processing (11 ECO Files)**
- **Files:** All 11 of Radu's ECO files
- **Total Commands:** 15,514
- **Violations:** 1 (pmux - BUFFCS1D3T6HVT)
- **Result:** ✅ PASS

### **Test 2: Auto-Detection (Multiple Files)**
- **Files:** 2 ECO files from same workarea (different directories)
- **Detection:** Both correctly detected workarea
- **Result:** ✅ PASS

### **Test 3: Error Handling**
- **Test 3A:** ECO outside workarea → Clear error message ✅
- **Test 3B:** Quiet mode → Only summary shown ✅
- **Test 3C:** Help documentation → Clear and comprehensive ✅

---

## Technical Details

### **Auto-Detection Algorithm**

```python
1. Start from ECO file directory
2. Walk up to 5 levels max
3. Look for workarea markers:
   - signoff_flow/ directory exists, OR
   - pnr_flow/ AND syn_flow/ directories exist
4. Return first directory with markers
5. If not found, return None (error)
```

### **Enhanced ecoAddRepeater Logic**

```
ecoAddRepeater -term {PREV_INST/PIN} ... -name {NEW_INST} -cell {CELLTYPE}
                     ↓                           ↓
           Check in ClockTree.rpt        Validate cell type
                     ↓
         If PREV_INST on clock tree
                     ↓
    Then NEW_INST will also be on clock tree
                     ↓
       Check if CELLTYPE is allowed
                     ↓
          If not → Report violation
```

**Why this matters:** NEW buffers aren't in ClockTree.rpt yet (ECO not applied), so we check the PREVIOUS instance to determine if the new buffer will be on the clock network.

---

## Known Issues / Future Enhancements

### **Minor Issues**
1. Exit code is 0 when auto-detection fails (should be 2)
2. "across X files" count in quiet mode sometimes shows 0

### **Future Enhancements**
1. HTML report generation (optional with `--html`)
2. JSON output mode (for machine parsing)
3. Diff mode (compare two ECO files)
4. Statistics dashboard (cell type distribution, etc.)

---

## Integration Status

### **Current State**
- ✅ **Standalone tool:** Fully functional and tested
- ✅ **Shared library:** `eco_checker_lib.py` ready for reuse
- ⏳ **Integration with avice_wa_review.py:** Pending (can be done later)

### **Future Integration**
The shared library can be integrated into `avice_wa_review.py`:
- Add `--eco-only` mode for quick ECO checks
- Refactor existing ECO analysis to use library
- Unified codebase for ECO validation

---

## Support

**Questions or Issues:**
- Contact: Alon Vice (avice@nvidia.com)
- Location: `/home/avice/scripts/avice_wa_review/`

**Documentation:**
- This README: `README_ECO_CHECKER.md`
- User Guide: `ECO_CHECKER_USER_GUIDE.txt`
- Main tool help: `/home/avice/scripts/avice_wa_review/eco_checker.csh --help`
- Library source: `eco_checker_lib.py`

---

## Changelog

### **Version 1.0** (November 6, 2025)
- Initial release
- Smart workarea auto-detection
- All 3 ECO checks implemented
- Enhanced ecoAddRepeater logic
- Comprehensive testing completed
- Production ready

---

## Examples Output

### **Example 1: Single ECO with Violations**

```bash
$ /home/avice/scripts/avice_wa_review/eco_checker.csh my_eco.tcl

===============================================================================
ECO Checker - Standalone ECO Validation Utility
===============================================================================
Analyzing 1 ECO file(s)...

[1/1] my_eco.tcl
----------------------------------------------------------------------
  Commands: 45 (ecoAddRepeater:20, ecoChangeCell:25)
  [OK] DontUse: 0 violations
  [WARN] instNotAllowedOnClocks: 2 violations
  [INFO] ClockCellsOnData: 0 instances

===============================================================================
SUMMARY
===============================================================================
Total Files:                 1
Total ECO Commands:          45

Violations by Category:
  [OK] DontUse Cells:                     0
  [WARN] instNotAllowedOnClocks:         2
  [INFO] ClockCellsOnData:                0

Affected Files:
  my_eco.tcl
===============================================================================
Exit code: 1 (violations found)
```

### **Example 2: Batch Processing (Clean)**

```bash
$ /home/avice/scripts/avice_wa_review/eco_checker.csh *.tcl --quiet

===============================================================================
SUMMARY
===============================================================================
Total Files:                 5
Total ECO Commands:          234

Violations by Category:
  [OK] DontUse Cells:                     0
  [OK] instNotAllowedOnClocks:            0
  [INFO] ClockCellsOnData:                12
===============================================================================
Exit code: 0 (all checks passed)
```

### **Example 3: Verbose Mode with Details**

```bash
$ /home/avice/scripts/avice_wa_review/eco_checker.csh my_eco.tcl --verbose

[... standard output ...]

===============================================================================
DETAILED VIOLATIONS
===============================================================================

[instNotAllowedOnClocks] Found 2 violation(s):
  Cell Type 'BUFFCS1D3T6HVT': 2 instance(s)
    Instance: eco_buf_123
    Previous: CTSOPT_FE_OFC12345 (on clock network)
    Command:  ecoAddRepeater -term {CTSOPT_FE_OFC12345/I} ...
    
    Instance: eco_buf_456
    Previous: CKBD4T6_inst (on clock network)
    Command:  ecoAddRepeater -term {CKBD4T6_inst/I} ...

[... summary ...]
```

---

**End of Documentation**



