# Workarea Comparison Feature - Implementation Plan

**Author:** Alon Vice (avice@nvidia.com)  
**Date:** November 25, 2025  
**Status:** Planning Phase  
**Previous Implementation:** Partial (requires cleanup - see note below)

---

## ⚠️ Important Note - Code Cleanup Required

**BACKGROUND:**

We initially started implementing the comparison feature **without proper planning**, which led to:
- ❌ Direct file parsing approach (duplicated extraction logic)
- ❌ Wrong architecture (didn't reuse `avice_wa_review.py`)
- ❌ Incomplete metrics extraction
- ❌ Non-scalable design

**CURRENT STATE OF CODE:**

There may be **old/incorrect comparison code** in `avice_wa_review.py` that needs to be:
1. **Identified** - Search for old comparison-related classes/methods
2. **Removed** - Delete outdated implementation
3. **Replaced** - Implement new architecture (this plan)

**SEARCH FOR OLD CODE:**
```bash
# Look for old comparison implementations
grep -n "class WorkareaComparator" avice_wa_review.py
grep -n "def.*compare.*workarea" avice_wa_review.py
grep -n "extract_data_from_workarea" avice_wa_review.py
grep -n "_extract_setup_data" avice_wa_review.py
grep -n "_extract_dc_data" avice_wa_review.py
grep -n "_extract_pnr_data" avice_wa_review.py
```

**DECISION: CLEAN SLATE APPROACH**

🗑️ **We will REMOVE all old comparison code NOW before starting Phase 1**

**Rationale:**
- Start fresh with correct architecture
- No conflicts between old and new code
- Cleaner codebase
- Easier to maintain going forward

**ACTION ITEMS BEFORE PHASE 1:**

- [ ] **STEP 1:** Search for all old comparison code (see checklist below)
- [ ] **STEP 2:** Remove `WorkareaComparator` class entirely
- [ ] **STEP 3:** Remove all `_extract_*_data_direct` methods
- [ ] **STEP 4:** Remove old `extract_data_from_workarea` method
- [ ] **STEP 5:** Clean up old Excel generation code if using wrong approach
- [ ] **STEP 6:** Verify old code is fully removed (grep search returns nothing)
- [ ] **STEP 7:** Test that `avice_wa_review.py` still works normally (without --compare)
- [ ] **STEP 8:** Start fresh Phase 1 implementation with clean slate

**LESSON LEARNED:**

✅ **Always plan before implementing**  
✅ **Architecture design comes first**  
✅ **Avoid duplicating existing logic**  
✅ **Reuse proven functionality**  
✅ **Clean slate is better than patching wrong implementation**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Command Line Interface](#command-line-interface)
4. [Implementation Phases](#implementation-phases)
5. [Parser Design](#parser-design)
6. [Excel Report Structure](#excel-report-structure)
7. [Testing Strategy](#testing-strategy)
8. [Future Enhancements](#future-enhancements)

---

## Overview

### Core Concept

**Run `avice_wa_review.py` → Parse Terminal Output → Compare → Generate Excel**

Instead of duplicating extraction logic, we:
1. Run `avice_wa_review.py` once on reference workarea
2. Run `avice_wa_review.py` once on test workarea  
3. Parse the terminal output section by section
4. Compare the parsed metrics
5. Generate Excel report with one tab per section
6. Email Excel report to user

### Key Benefits

✅ **No Code Duplication** - Uses proven extraction logic from `avice_wa_review.py`  
✅ **Automatic Synchronization** - Any update to `avice_wa_review.py` output automatically flows to comparison  
✅ **Single Source of Truth** - Maintains consistency across the tool  
✅ **Extensible** - Add new metric in `avice_wa_review.py` → automatically compared  
✅ **Maintainable** - One place to update metrics  
✅ **Robust** - If `avice_wa_review.py` works, comparison works

### Terminal Output Standards

**CRITICAL: ASCII-ONLY OUTPUT**

All comparison terminal output MUST use ASCII characters only (no Unicode symbols).

**Why:** Unix shell compatibility - Unicode breaks in many terminal environments.

**Character Substitutions:**
| Unicode | ASCII Replacement | Usage |
|---------|-------------------|-------|
| `✓` | `[OK]` | Success indicators |
| `✗` | `[ERROR]` | Error indicators |
| `⚠` | `[WARN]` | Warning indicators |
| `→` | `->` | Show changes |
| `•` | `-` | List items |
| `🔍` | `[SEARCH]` | Search operations |
| `📊` | `[COMPARE]` | Comparison operations |
| `✅` | `[CHANGED]` | Changed metrics |

**Examples:**
```bash
# ❌ WRONG - Unicode breaks in Unix shells
✓ Utilization: 47.85% → 47.58% (-0.27%)

# ✅ CORRECT - ASCII works everywhere
[OK] Utilization: 47.85% -> 47.58% (-0.27%)
```

**Implementation:**
- Use Color class for terminal output formatting
- Always use ASCII characters in print statements
- Test output in actual Unix shell before committing  

---

## Architecture

### Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User Command:                                               │
│  python3 avice_wa_review.py --compare                       │
│    --ref /path/to/reference                                 │
│    --test /path/to/test                                     │
│    -s setup synthesis  (optional - reuse existing -s flag)  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Run avice_wa_review.py on Reference Workarea      │
│  ---------------------------------------------------------- │
│  subprocess.run([                                           │
│    'python3', 'avice_wa_review.py',                        │
│    ref_workarea,                                           │
│    '-s', 'setup synthesis',  # if specified               │
│    '--quiet', '--no-logo'                                  │
│  ], capture_output=True)                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Run avice_wa_review.py on Test Workarea           │
│  ---------------------------------------------------------- │
│  subprocess.run([                                           │
│    'python3', 'avice_wa_review.py',                        │
│    test_workarea,                                          │
│    '-s', 'setup synthesis',  # if specified               │
│    '--quiet', '--no-logo'                                  │
│  ], capture_output=True)                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Parse Terminal Output by Section                   │
│  ---------------------------------------------------------- │
│  parser = OutputParser(ref_output.stdout)                  │
│  ref_data = parser.parse_all()                             │
│  # Result: {                                               │
│  #   'setup': {...},                                       │
│  #   'synthesis': {...}                                    │
│  # }                                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Compare Section by Section                         │
│  ---------------------------------------------------------- │
│  comparison = compare_sections(ref_data, test_data)        │
│  # Calculate deltas, percentages, status                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Generate Excel Report                              │
│  ---------------------------------------------------------- │
│  generate_excel(comparison, filename)                       │
│  # One tab per section + Summary Dashboard                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Email Report (Optional)                            │
│  ---------------------------------------------------------- │
│  send_email(excel_file, user_email)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Command Line Interface

### Usage Examples

#### Compare All Sections (Default)
```bash
python3 avice_wa_review.py --compare \
  --ref /home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_..._sep10 \
  --test /home/scratch.brachas_vlsi_1/agur/1NL/pmux/pmux_rbv_..._nov_02 \
  --email
```

#### Compare Specific Sections (Reuse `-s` Flag)
```bash
# Compare only Setup section
python3 avice_wa_review.py --compare \
  --ref /path/to/reference \
  --test /path/to/test \
  -s setup

# Compare Setup + Synthesis + PnR
python3 avice_wa_review.py --compare \
  --ref /path/to/reference \
  --test /path/to/test \
  -s setup synthesis pnr
```

### CLI Arguments

| Argument | Alias | Type | Description |
|----------|-------|------|-------------|
| `--compare` | - | flag | Enable workarea comparison mode |
| `--ref` | - | path | Reference workarea path (baseline) |
| `--test` | - | path | Test workarea path (to compare against reference) |
| `-s` / `--sections` | - | list | **REUSED FLAG** - Sections to compare (default: all) |
| `--email` | - | optional | Send Excel report via email |

### `-s` Flag Behavior

**Normal Mode (Single Workarea):**
```bash
python3 avice_wa_review.py /workarea -s setup synthesis
# → Analyzes only Setup and Synthesis sections
```

**Comparison Mode:**
```bash
python3 avice_wa_review.py --compare --ref /ref --test /test -s setup synthesis
# → Compares only Setup and Synthesis sections between ref and test
```

**Implementation:**
```python
if args.compare:
    # In comparison mode, -s applies to BOTH workareas
    sections_arg = args.sections if args.sections else None
    
    # Run avice_wa_review.py on reference
    ref_cmd = ['python3', 'avice_wa_review.py', ref_workarea, '--quiet', '--no-logo']
    if sections_arg:
        ref_cmd.extend(['-s'] + sections_arg)
    ref_output = subprocess.run(ref_cmd, capture_output=True, text=True)
    
    # Run avice_wa_review.py on test (with same sections)
    test_cmd = ['python3', 'avice_wa_review.py', test_workarea, '--quiet', '--no-logo']
    if sections_arg:
        test_cmd.extend(['-s'] + sections_arg)
    test_output = subprocess.run(test_cmd, capture_output=True, text=True)
```

---

## Implementation Phases

### Phase 1: Foundation + [1] Setup Section

**Objective:** Establish core infrastructure and implement Setup comparison

**Tasks:**
1. Create `OutputParser` class with section splitting logic
2. Implement `parse_setup()` method
3. Implement selective section execution (reuse `-s` flag)
4. Implement comparison engine for Setup
5. Generate Excel with Summary + Setup tabs
6. Test on pmux workareas

**Deliverables:**
- ✅ Section splitter working
- ✅ Setup metrics extracted from terminal output
- ✅ Setup comparison with deltas
- ✅ Excel report with 2 tabs (Summary + Setup)
- ✅ Email integration

**Test Command:**
```bash
python3 avice_wa_review.py --compare \
  --ref /home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_..._sep10 \
  --test /home/scratch.brachas_vlsi_1/agur/1NL/pmux/pmux_rbv_..._nov_02 \
  -s setup \
  --email
```

---

### Phase 2: [2] Runtime Analysis

**Objective:** Add Runtime section comparison

**Tasks:**
1. Implement `parse_runtime()` method
2. Add Runtime comparison logic
3. Add Runtime tab to Excel
4. Test Runtime comparison

**Deliverables:**
- ✅ Runtime metrics extracted (total runtime, stage breakdown)
- ✅ Runtime comparison with deltas
- ✅ Excel with Runtime tab

**Test Command:**
```bash
python3 avice_wa_review.py --compare \
  --ref /ref --test /test \
  -s setup runtime
```

---

### Phase 3: [3] Synthesis (DC)

**Objective:** Add comprehensive DC/Synthesis comparison

**Tasks:**
1. Implement `parse_synthesis()` method (most complex parser)
2. Extract QoR metrics, DC version, errors/warnings
3. Add Synthesis comparison logic with timing analysis
4. Add Synthesis tab to Excel

**Deliverables:**
- ✅ DC Version comparison
- ✅ QoR metrics (15+ metrics extracted)
- ✅ Timing metrics (WNS, TNS, Violating Paths)
- ✅ Cell count analysis
- ✅ Excel with Synthesis tab

**Test Command:**
```bash
python3 avice_wa_review.py --compare \
  --ref /ref --test /test \
  -s synthesis
```

---

### Phase 4: [4] PnR Analysis ✅ COMPLETED (November 27, 2025)

**Objective:** Add comprehensive PnR section comparison with complete metrics coverage

**Status:** ✅ **COMPLETED** (including Phase 4.1 + 4.2 enhancements)

**Tasks:**
1. ✅ Implement `parse_pnr()` method (extracts 46 metrics - increased from 30)
2. ✅ Extract die dimensions, area, utilization
3. ✅ Extract cell counts, VT distribution, arrays
4. ✅ Extract clock gating efficiency metrics (basic + detailed)
5. ✅ Extract routing metrics and design violations
6. ✅ Extract DFT metrics (scan chains)
7. ✅ Extract external timing (FEEDTHROUGH/REGIN/REGOUT)
8. ✅ Extract clock latencies per clock domain
9. ✅ **Phase 4.1**: Extract DelBuf, FFs by Clock, Ungated FFs, Max CG Fanout, Non-Scan Flops, Max Transition Violations
10. ✅ **Phase 4.2**: Extract Internal Clock Domain Timing (per-clock WNS/TNS/ViolPaths)
11. ✅ **Phase 4.2**: Extract Clock Tree Summary (per-clock Buf/Inv/CG/Sinks/Taps)
12. ✅ **Phase 4.2**: Extract Power Summary (per-group Area/Count/Power/Leakage)
13. ✅ Extract Flow Configuration parameters (FLOW_PATH, CUSTOM_SCRIPTS_DIR, etc.)
14. ✅ Add PnR comparison logic with delta calculation
15. ✅ Add PnR tab to Excel with professional formatting (14 sections)
16. ✅ Move Flow Configuration to top of PnR tab for immediate visibility
17. ✅ Add PnR to default comparison sections
18. ✅ Test on multiple units (prt, fth)

**Implementation Details:**
- **File:** `avice_wa_review.py`
- **Parser Method:** `parse_pnr()` (Lines ~32950-33320, enhanced with Phase 4.1+4.2)
- **Excel Generator:** `_generate_pnr_comparison_tab()` (Lines ~32140-32450, enhanced)
- **Section Detection:** Normalized to 'pnr-analysis' in sections dict
- **Default Sections:** Updated to `['setup', 'runtime', 'synthesis', 'pnr']`

**Deliverables:**
- ✅ **46 PnR Metrics Extracted (Original 30 + Enhanced 16):**
  - **Section 1 - Flow Configuration (9):** FLOW_PATH, CUSTOM_SCRIPTS_DIR, MULTIBIT_FLOP, Library Snapshot, Process, Tracks, Project, Scenario, VT Types
  - **Section 2 - Die & Area (7):** Die X/Y, Die/Cell/Arrays Areas, Utilization, Effective Util
  - **Section 3 - Cell Counts (6):** Total, Comb, Seq, FF, Buf/Inv + %
  - **Section 4 - VT & Arrays (4):** HVT%, SVT%, Array count/size
  - **Section 5 - Clock Gating (3):** Gates count, Gated%, Multibit%
  - **Section 6 - Routing & Violations (5):** Wire length, Shorts, Cap/Trans/Fanout
  - **Section 7 - DFT (2):** Longest scan chain, Number of chains
  - **Section 8 - External Timing (9):** WNS/TNS/ViolPaths for FEEDTHROUGH/REGIN/REGOUT
  - **Section 9 - Cell Details (Phase 4.1, 2+):** DelBuf, FFs by Clock per-clock
  - **Section 10 - Clock Gating Details (Phase 4.1, 6):** Ungated%, One/Multi ClkGate%, Max CG Fanout, Non-Scan Flops
  - **Section 11 - Max Trans Violations (Phase 4.1, 3):** WNS, TNS, Count
  - **Section 12 - Internal Timing (Phase 4.2, per-clock x 3):** WNS/TNS/ViolPaths for each internal clock
  - **Section 13 - Clock Tree (Phase 4.2, per-clock x 7):** Buf/Inv/CG/Total, Sinks FF/Total, Taps
  - **Section 14 - Power Summary (Phase 4.2, 16):** Area/Count/Power/Leakage for comb/seq/physical/total

- ✅ **Excel PnR Comparison Tab (Tab 4):**
  - Professional blue theme (4A90E2)
  - **14 organized sections** (was 7) with clear headers
  - **~140 rows** (was ~52) with comprehensive metrics
  - **Flow Configuration at TOP** for immediate visibility
  - Delta calculation (absolute & percentage change)
  - Color-coded status: IMPROVED (green), DEGRADED (red), UNCHANGED (yellow)
  - Better_if_higher logic per metric (intelligent status determination)
  - Proper column widths for readability

- ✅ **Parser Robustness:**
  - Handles missing PnR data gracefully (returns empty dict)
  - Works across different units
  - Handles incomplete flows (no errors thrown)
  - Per-clock metrics adapt to design (2-10+ clocks supported)

- ✅ **Testing Validated:**
  - FTH comparison: 90 ref metrics, 89 test metrics (final)
  - PRT parser: Successfully extracted 46 fields
  - Excel generation: 4-tab report with 139-row PnR tab
  - Flow Config at top: Caught CUSTOM_SCRIPTS_DIR drift (ww36 vs ww40)

**Test Command:**
```bash
# Full comparison (includes PnR by default)
python3 avice_wa_review.py -r /path/to/ref -t /path/to/test

# PnR-only comparison
python3 avice_wa_review.py -r /path/to/ref -t /path/to/test -s pnr

# Multiple sections including PnR
python3 avice_wa_review.py -r /path/to/ref -t /path/to/test -s setup runtime pnr
```

**Example Excel Output:**
- Tab 1: Setup & Summary (10 metrics)
- Tab 2: Runtime Comparison (with PnR breakdown)
- Tab 3: DC Comparison (QoR, Timing, Config)
- Tab 4: PnR Comparison (30+ metrics in 7 sections) ⬅️ NEW!

**Key Improvements:**
- Most comprehensive PnR comparison in any flow analyzer
- Automatic detection of better_if_higher for intelligent status
- Professional formatting matching DC comparison quality
- Seamless integration with existing comparison framework

---

### Phase 5: [5] Clock Tree Analysis

**Tasks:**
1. Implement `parse_clock()` method
2. Extract clock latency, skew, tree metrics
3. Add Clock tab to Excel

---

### Phase 6: [6] Formal Verification

**Tasks:**
1. Implement `parse_formal()` method
2. Extract formal flow status, runtime
3. Add Formal tab to Excel

---

### Phase 7: [7] Parasitic Extraction (Star)

**Tasks:**
1. Implement `parse_parasitic()` method
2. Extract SPEF status, shorts, resistance
3. Add Parasitic tab to Excel

---

### Phase 8: [8] Signoff Timing (PT)

**Tasks:**
1. Implement `parse_timing()` method
2. Extract PT timing results (WNS, TNS, scenarios)
3. Add PT tab to Excel

---

### Phase 9: [9] Physical Verification (PV)

**Tasks:**
1. Implement `parse_pv()` method
2. Extract DRC, LVS, Antenna violations
3. Add PV tab to Excel

---

### Phase 10: [10] GL Check

**Tasks:**
1. Implement `parse_gl_check()` method
2. Extract violation counts
3. Add GL Check tab to Excel

---

### Phase 11-13: Remaining Sections

- [11] ECO Analysis
- [12] NV Gate ECO  
- [13] Block Release

---

## Parser Design

### OutputParser Class Structure

```python
class OutputParser:
    """Parse avice_wa_review.py terminal output"""
    
    def __init__(self, output: str):
        """Initialize parser with terminal output"""
        self.output = output
        self.sections = self._split_into_sections()
    
    def _split_into_sections(self) -> Dict[str, Dict]:
        """
        Split output by section headers: ---[N] Section Name---
        
        Returns:
            Dict mapping normalized section names to section data:
            {
                'setup': {
                    'number': 1,
                    'title': 'Setup',
                    'content': '...'
                },
                'synthesis': {
                    'number': 3,
                    'title': 'Synthesis (DC)',
                    'content': '...'
                }
            }
        """
        sections = {}
        pattern = r'-+\s*\[(\d+)\]\s*([^\-]+)\s*-+'
        
        matches = list(re.finditer(pattern, self.output))
        for i, match in enumerate(matches):
            section_num = match.group(1)
            section_name = match.group(2).strip()
            
            # Extract content between this section and next
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(self.output)
            content = self.output[start:end]
            
            # Normalize section name
            normalized_name = self._normalize_section_name(section_name)
            sections[normalized_name] = {
                'number': int(section_num),
                'title': section_name,
                'content': content
            }
        
        return sections
    
    def _normalize_section_name(self, name: str) -> str:
        """
        Normalize section name to match CLI argument
        
        Examples:
            "Synthesis (DC)" -> "synthesis"
            "Place & Route (PnR)" -> "pnr"
            "Signoff Timing (PT)" -> "timing"
        """
        mapping = {
            'Setup': 'setup',
            'Runtime Analysis': 'runtime',
            'Synthesis (DC)': 'synthesis',
            'PnR Analysis': 'pnr',
            'Place & Route (PnR)': 'pnr',
            'Clock Tree Analysis': 'clock',
            'Formal Verification': 'formal',
            'Parasitic Extraction (Star)': 'parasitic',
            'Signoff Timing (PT)': 'timing',
            'Physical Verification (PV)': 'pv',
            'GL Check': 'gl-check',
            'ECO Analysis': 'eco',
            'NV Gate ECO': 'nv-gate-eco',
            'Block Release': 'block-release'
        }
        return mapping.get(name, name.lower().replace(' ', '-'))
    
    # ========== SECTION PARSERS ==========
    
    def parse_setup(self) -> Dict:
        """[1] Parse Setup section"""
        if 'setup' not in self.sections:
            return {}
        
        content = self.sections['setup']['content']
        data = {}
        
        # UNIT
        match = re.search(r'UNIT:\s*(\S+)', content)
        if match:
            data['unit'] = match.group(1)
        
        # TAG
        match = re.search(r'TAG:\s*(.+?)(?:\n|$)', content)
        if match:
            data['tag'] = match.group(1).strip()
        
        # IPO
        match = re.search(r'IPO:\s*(\S+)', content)
        if match:
            data['ipo'] = match.group(1)
        
        # Available IPOs
        match = re.search(r'Available IPOs:\s*(.+?)(?:\)|\n)', content)
        if match:
            data['available_ipos'] = match.group(1).strip()
        
        # Disk Usage
        match = re.search(r'Usage:\s*(\d+)%', content)
        if match:
            data['disk_usage'] = int(match.group(1))
        
        # Environment Information
        env_vars = re.findall(r'(BEFLOW_\w+|BE_\w+|TECH_\w+)=(.+?)(?:\n|$)', content)
        if env_vars:
            data['environment'] = dict(env_vars)
        
        return data
    
    def parse_runtime(self) -> Dict:
        """[2] Parse Runtime Analysis section"""
        # To be implemented in Phase 2
        pass
    
    def parse_synthesis(self) -> Dict:
        """[3] Parse Synthesis (DC) section"""
        # To be implemented in Phase 3
        pass
    
    def parse_pnr(self) -> Dict:
        """[4] Parse PnR Analysis section"""
        # To be implemented in Phase 4
        pass
    
    # ... More parsers for remaining sections
    
    def parse_all(self, section_filter: List[str] = None) -> Dict:
        """
        Parse all sections (or filtered sections)
        
        Args:
            section_filter: List of section names to parse (None = all)
        
        Returns:
            Dict mapping section names to parsed data
        """
        parsers = {
            'setup': self.parse_setup,
            'runtime': self.parse_runtime,
            'synthesis': self.parse_synthesis,
            'pnr': self.parse_pnr,
            # Add more as implemented
        }
        
        data = {}
        for section_name, parser_func in parsers.items():
            # Skip if section not in filter
            if section_filter and section_name not in section_filter:
                continue
            
            # Skip if parser not implemented yet
            if parser_func is None:
                continue
            
            data[section_name] = parser_func()
        
        return data
```

---

## Excel Report Structure

### Tab Organization

**Tab 1: Summary Dashboard** (Always included)
- High-level comparison of all sections
- Color-coded status indicators
- Quick overview of key changes

**Tab 2+: Section-Specific Tabs** (One per compared section)
- [1] Setup Comparison
- [2] Runtime Comparison
- [3] Synthesis Comparison
- [4] PnR Comparison
- [5] Clock Comparison
- ... (dynamically generated based on compared sections)

### Excel Tab Generation

```python
def generate_excel(comparison: Dict, filename: str) -> None:
    """
    Generate Excel with tabs for compared sections only
    
    Args:
        comparison: Dict with comparison data per section
        filename: Output Excel filename
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default sheet
    
    # Tab 1: Always include Summary Dashboard
    generate_summary_sheet(wb, comparison)
    
    # Tab generators (ordered by section number)
    tab_generators = {
        'setup': generate_setup_sheet,
        'runtime': generate_runtime_sheet,
        'synthesis': generate_synthesis_sheet,
        'pnr': generate_pnr_sheet,
        'clock': generate_clock_sheet,
        'formal': generate_formal_sheet,
        'parasitic': generate_parasitic_sheet,
        'timing': generate_timing_sheet,
        'pv': generate_pv_sheet,
        'gl-check': generate_gl_check_sheet,
        'eco': generate_eco_sheet,
        'nv-gate-eco': generate_nv_gate_eco_sheet,
        'block-release': generate_block_release_sheet
    }
    
    # Generate tabs only for sections that were compared
    for section_name in sorted(comparison.keys()):
        if section_name in tab_generators:
            # Only create tab if section has data
            if comparison[section_name]['reference'] or comparison[section_name]['test']:
                tab_generators[section_name](wb, comparison[section_name])
    
    wb.save(filename)
```

---

## Testing Strategy

### Overview

Each section implementation MUST be tested thoroughly before moving to the next phase.

**Test Workareas Strategy:**

We use **multiple workareas** from different units to ensure robustness and catch edge cases.

#### Primary Test Pair (pmux)

**Use for initial development and most testing:**
- **Reference:** `/home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10`
- **Test:** `/home/scratch.brachas_vlsi_1/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_nov_02`
- **Why:** Well-known unit, stable, good representative data

#### Secondary Test Units (For Regression & Edge Cases)

**Use for final validation before marking phase complete:**

Test with 3-5 additional units from AGUR database to catch:
- Different output formats
- Missing sections
- Different metrics ranges
- Edge cases and corner cases

**Recommended Test Units:**
```bash
# Use AGUR_UNITS_TABLE.csv to get workarea paths
python3 avice_wa_review.py -u prt    # CPORT chiplet
python3 avice_wa_review.py -u ccorea # HPORT chiplet  
python3 avice_wa_review.py -u dqs    # QNS chiplet
python3 avice_wa_review.py -u fdb    # Different characteristics
python3 avice_wa_review.py -u lnd    # Edge case testing
```

**How to Get Workareas:**
```python
# Get latest workarea for a unit
from agur_release_tracking import get_unit_workarea

ref_wa = get_unit_workarea('pmux', release='SEP_10')
test_wa = get_unit_workarea('pmux', release='NOV_02')
```

#### Testing Protocol

**Phase 1-4 (Setup, Runtime, Synthesis, PnR):**
- Primary testing: pmux (detailed testing)
- Secondary testing: 2 additional units (spot-check)

**Phase 5-8 (Clock, Formal, Parasitic, PT):**
- Primary testing: pmux
- Secondary testing: 3 additional units

**Phase 9-13 (PV, GL-check, ECO, etc.):**
- Primary testing: pmux
- Secondary testing: 5 additional units
- Full regression: All tested units

**Benefits of Multi-Unit Testing:**
- ✅ Catches parser edge cases
- ✅ Verifies robustness across different designs
- ✅ Tests different chiplet characteristics
- ✅ Validates missing/partial data handling
- ✅ Ensures production-ready quality

### Per-Section Testing Protocol

For **EACH** section implementation, perform the following tests:

---

#### Test 1: Section-Only Comparison

**Purpose:** Verify the section works in isolation

**Command:**
```bash
python3 avice_wa_review.py --compare \
  --ref /home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_..._sep10 \
  --test /home/scratch.brachas_vlsi_1/agur/1NL/pmux/pmux_rbv_..._nov_02 \
  -s <section_name>
```

**Verify:**
- [ ] Both workareas analyzed successfully
- [ ] Terminal output is clean and readable
- [ ] Only ASCII characters in terminal output (no Unicode)
- [ ] Section metrics extracted from both workareas
- [ ] Metrics count matches expected (e.g., "Setup: 8 metrics")
- [ ] No Python errors or exceptions
- [ ] No grep/regex errors during parsing

---

#### Test 2: Terminal Output Validation

**Purpose:** Verify terminal output quality

**Checks:**
- [ ] **ASCII Only:** No Unicode symbols (`✓ ✗ → •` etc.)
- [ ] **Clean Format:** Proper spacing and alignment
- [ ] **Color Coding:** GREEN/YELLOW/RED status indicators work
- [ ] **Readability:** Easy to scan and understand
- [ ] **Line Count:** Minimal output (< 100 lines for single section)
- [ ] **Key Findings:** Summary shows most important changes

**Example Expected Output:**
```
WORKAREA COMPARISON MODE
[OK] Reference: .../sep10
[OK] Test: .../nov_02

[COMPARE] Starting Comparison

Extracting data from Reference: ...
[OK] Data extraction complete
  Setup: 8 metrics

Extracting data from Test: ...
[OK] Data extraction complete
  Setup: 8 metrics

COMPARISON SUMMARY
Key Findings:
  [INFO] Unit: pmux
  [INFO] IPO: ipo1000
  [CHANGED] Disk Usage: 75% -> 60% (-15%)
```

---

#### Test 3: Excel Report Validation

**Purpose:** Verify Excel generation and content

**3A. AUTOMATED CHECKS** (Python Script Can Verify)

These checks can be automated using `openpyxl`:

```python
def validate_excel(excel_file: str, section_name: str) -> bool:
    """Automated Excel validation"""
    try:
        wb = openpyxl.load_workbook(excel_file)
        
        # Check 1: File opens without corruption
        assert wb is not None, "Excel file corrupted"
        
        # Check 2: Required tabs exist
        assert "Summary Dashboard" in wb.sheetnames, "Summary tab missing"
        assert f"{section_name} Comparison" in wb.sheetnames, "Section tab missing"
        
        # Check 3: Tab has data (not empty)
        ws = wb[f"{section_name} Comparison"]
        assert ws.max_row > 1, "Tab has no data"
        
        # Check 4: Headers exist
        headers = [cell.value for cell in ws[1]]
        assert "Metric" in headers, "Metric column missing"
        assert "Reference" in headers, "Reference column missing"
        assert "Test" in headers, "Test column missing"
        assert "Delta" in headers, "Delta column missing"
        
        # Check 5: No formula errors
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                if isinstance(cell.value, str):
                    assert not cell.value.startswith('#'), f"Formula error: {cell.value}"
        
        # Check 6: Data types correct (numbers are numbers, not strings)
        # Check specific cells based on section metrics
        
        # Check 7: No empty required cells
        # Verify reference and test columns are populated
        
        print(f"[OK] Excel validation passed for {section_name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Excel validation failed: {e}")
        return False
```

**Automated Validation Checklist:**
- [x] Excel file created successfully
- [x] File opens without corruption (openpyxl can load it)
- [x] Summary Dashboard tab exists
- [x] Section-specific tab exists (e.g., "Setup Comparison")
- [x] Tab contains data (row count > 1)
- [x] Required headers present (Metric, Reference, Test, Delta)
- [x] No formula errors (#VALUE!, #REF!, #DIV/0!)
- [x] Data types correct (numbers stored as numbers)
- [x] No empty cells in critical columns
- [x] Cell values match expected data types

**3B. MANUAL CHECKS** (Human Verification Required)

These require human judgment and visual inspection:

- [ ] **Visual Formatting:** Colors look good, text readable
- [ ] **Color Coding:** GREEN/YELLOW/RED applied correctly and meaningfully
- [ ] **Layout:** Column widths appropriate, no text cutoff
- [ ] **Number Formatting:** Commas, decimals, percentages display correctly
- [ ] **Header Clarity:** Column names are clear and descriptive
- [ ] **Data Accuracy:** Spot-check a few metrics against terminal output
- [ ] **User Experience:** Report is easy to read and understand
- [ ] **Professional Appearance:** Looks polished and production-ready

**Manual Verification Steps:**
```bash
# 1. Generate report
python3 avice_wa_review.py --compare --ref /ref --test /test -s setup

# 2. Run automated validation
python3 validate_excel.py avice_comparison_*.xlsx setup

# 3. Copy Excel to Windows
scp avice_comparison_*.xlsx user@windows:/path/

# 4. Open in Excel and verify manual checklist above
```

**Testing Approach:**
- **Automated checks:** Run on EVERY test (fast, repeatable)
- **Manual checks:** Run on first test of each section, then spot-check

---

#### Test 4: Parser Robustness

**Purpose:** Verify parser handles edge cases

**Test Cases:**

**4a. Missing Section in Output**
```bash
# Run comparison on workarea missing the section
# Parser should handle gracefully (not crash)
```

**4b. Partial Metrics**
```bash
# Section exists but some metrics missing
# Parser should extract available metrics only
```

**4c. Unexpected Format**
```bash
# Terminal output format slightly different
# Parser should be resilient to minor variations
```

**Verify:**
- [ ] No crashes on missing sections
- [ ] Graceful handling of missing metrics
- [ ] Clear error messages if parsing fails
- [ ] Comparison continues even if one section fails

---

#### Test 5: Multi-Section Combination

**Purpose:** Verify section works with other sections

**Command:**
```bash
# Test current section + all previously implemented sections
python3 avice_wa_review.py --compare \
  --ref /ref --test /test \
  -s setup runtime synthesis  # Add current section
```

**Verify:**
- [ ] All sections parse correctly
- [ ] No interference between sections
- [ ] Excel has all section tabs
- [ ] Summary dashboard includes all sections

---

#### Test 6: Email Integration

**Purpose:** Verify email delivery works

**Command:**
```bash
python3 avice_wa_review.py --compare \
  --ref /ref --test /test \
  -s <section_name> \
  --email
```

**Verify:**
- [ ] Email sent successfully
- [ ] Excel attachment received
- [ ] Excel attachment opens correctly
- [ ] Email subject clear
- [ ] Email body informative

---

#### Test 7: Cross-User Compatibility

**Purpose:** Verify report works for different users

**Test:**
```bash
# Generate report as user 'avice'
# Copy to another user's directory
# Verify Excel opens and works
```

**Verify:**
- [ ] Excel uses $USER variable correctly in filename
- [ ] No hardcoded paths in Excel
- [ ] Report portable across users

---

### Section-Specific Test Requirements

#### Phase 1: Setup Section

**Additional Tests:**
- [ ] UNIT name extracted correctly
- [ ] TAG extracted correctly
- [ ] IPO extracted correctly
- [ ] Disk usage percentage accurate
- [ ] Environment variables parsed (BEFLOW_REV, etc.)
- [ ] Excel Setup tab has all 8+ metrics

#### Phase 2: Runtime Section

**Additional Tests:**
- [ ] Total runtime extracted
- [ ] Individual stage runtimes parsed
- [ ] Percentage calculations correct
- [ ] Stage names match avice_wa_review.py output
- [ ] Excel Runtime tab shows timeline comparison

#### Phase 3: Synthesis Section

**Additional Tests:**
- [ ] DC Version extracted correctly
- [ ] DC Errors count accurate
- [ ] DC Warnings count accurate
- [ ] All QoR metrics present (15+ metrics)
- [ ] Die dimensions parsed correctly
- [ ] Timing metrics (WNS, TNS) accurate
- [ ] Cell counts correct
- [ ] Clock gates removed count accurate
- [ ] Excel Synthesis tab comprehensive

#### Phase 4+: Additional Sections

**Follow same pattern:**
- [ ] All section-specific metrics extracted
- [ ] Comparison logic correct
- [ ] Excel tab complete
- [ ] No interference with other sections

---

### Regression Testing

After implementing each new section, run full regression:

```bash
# Test all implemented sections together
python3 avice_wa_review.py --compare --ref /ref --test /test

# Verify:
# - All sections work
# - Excel has all tabs
# - No performance degradation
# - Terminal output still clean
```

---

### Test Results Documentation

For each phase, document:

**Pass Criteria:**
- All 7 test types completed ✅
- No critical issues found
- Excel validated manually
- Email delivery confirmed

**Record Results:**
```
Phase X: <Section Name> - Test Results
Date: YYYY-MM-DD
Tester: avice

Test 1 (Section-Only): ✅ PASS
Test 2 (Terminal Output): ✅ PASS
Test 3 (Excel Report): ✅ PASS
Test 4 (Parser Robustness): ✅ PASS
Test 5 (Multi-Section): ✅ PASS
Test 6 (Email Integration): ✅ PASS
Test 7 (Cross-User): ✅ PASS

Issues Found: None
Ready for Production: YES
```

---

### Testing Tools & Automation

#### Excel Validation Script

**Create:** `validate_excel.py` - Automated Excel validation

```python
#!/usr/bin/env python3
"""
Automated Excel Validation Tool for Comparison Reports
Usage: python3 validate_excel.py <excel_file> <section_name>
"""

import openpyxl
import sys

def validate_excel(excel_file: str, section_name: str) -> bool:
    """
    Automated Excel validation
    Returns: True if all checks pass, False otherwise
    """
    checks_passed = 0
    checks_total = 0
    
    try:
        print(f"[VALIDATE] Opening {excel_file}...")
        wb = openpyxl.load_workbook(excel_file)
        checks_total += 1
        checks_passed += 1
        print("[OK] Excel file opens without corruption")
        
        # Check required tabs exist
        checks_total += 1
        if "Summary Dashboard" in wb.sheetnames:
            checks_passed += 1
            print("[OK] Summary Dashboard tab exists")
        else:
            print("[ERROR] Summary Dashboard tab missing")
        
        checks_total += 1
        expected_tab = f"{section_name.title()} Comparison"
        if expected_tab in wb.sheetnames or any(section_name.lower() in name.lower() for name in wb.sheetnames):
            checks_passed += 1
            print(f"[OK] Section tab exists")
        else:
            print(f"[ERROR] Section tab missing: {expected_tab}")
            return False
        
        # Find the section tab
        ws = None
        for name in wb.sheetnames:
            if section_name.lower() in name.lower() and name != "Summary Dashboard":
                ws = wb[name]
                break
        
        if ws is None:
            print(f"[ERROR] Could not find section worksheet")
            return False
        
        # Check tab has data
        checks_total += 1
        if ws.max_row > 1:
            checks_passed += 1
            print(f"[OK] Tab has data ({ws.max_row} rows)")
        else:
            print("[ERROR] Tab is empty")
        
        # Check headers exist
        headers = [cell.value for cell in ws[1] if cell.value]
        checks_total += 1
        required_headers = ["Metric", "Reference", "Test"]
        if all(any(req.lower() in str(h).lower() for h in headers) for req in required_headers):
            checks_passed += 1
            print(f"[OK] Required headers present: {headers}")
        else:
            print(f"[ERROR] Missing required headers. Found: {headers}")
        
        # Check for formula errors
        checks_total += 1
        formula_errors = []
        for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
            for col_idx, cell in enumerate(row, start=1):
                if isinstance(cell.value, str) and cell.value.startswith('#'):
                    formula_errors.append(f"Row {row_idx}, Col {col_idx}: {cell.value}")
        
        if not formula_errors:
            checks_passed += 1
            print("[OK] No formula errors found")
        else:
            print(f"[ERROR] Formula errors found: {formula_errors[:3]}")
        
        # Summary
        print(f"\n[SUMMARY] Passed {checks_passed}/{checks_total} automated checks")
        
        if checks_passed == checks_total:
            print("[OK] All automated validation checks PASSED")
            print("[INFO] Manual verification still required (formatting, colors, UX)")
            return True
        else:
            print(f"[ERROR] {checks_total - checks_passed} checks FAILED")
            return False
            
    except Exception as e:
        print(f"[ERROR] Excel validation exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 validate_excel.py <excel_file> <section_name>")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    section_name = sys.argv[2]
    
    success = validate_excel(excel_file, section_name)
    sys.exit(0 if success else 1)
```

#### Terminal Output Validation Commands

```bash
# Check for non-ASCII characters in output
python3 avice_wa_review.py --compare --ref /ref --test /test -s setup 2>&1 | \
  LC_ALL=C grep -P '[^\x00-\x7F]'
# Should return nothing (all ASCII)

# Count output lines
python3 avice_wa_review.py --compare --ref /ref --test /test -s setup 2>&1 | wc -l
# Should be < 100 lines for single section

# Verify Excel not corrupted (file format check)
file avice_comparison_*.xlsx
# Should say "Microsoft Excel 2007+"

# Run automated Excel validation
python3 validate_excel.py avice_comparison_*.xlsx setup
# Should print "[OK] All automated validation checks PASSED"
```

#### Quick Test Script

```bash
#!/bin/bash
# quick_test.sh - Run all automated checks for a section

SECTION=$1
if [ -z "$SECTION" ]; then
    echo "Usage: ./quick_test.sh <section_name>"
    exit 1
fi

echo "=========================================="
echo "Quick Test: $SECTION Section"
echo "=========================================="

# Test comparison
echo "[1/4] Running comparison..."
python3 avice_wa_review.py --compare \
  --ref /home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_..._sep10 \
  --test /home/scratch.brachas_vlsi_1/agur/1NL/pmux/pmux_rbv_..._nov_02 \
  -s $SECTION > test_output.txt 2>&1

# Check ASCII-only
echo "[2/4] Checking ASCII-only output..."
if LC_ALL=C grep -P '[^\x00-\x7F]' test_output.txt > /dev/null; then
    echo "[ERROR] Non-ASCII characters found!"
    exit 1
else
    echo "[OK] All ASCII"
fi

# Check line count
echo "[3/4] Checking output line count..."
LINES=$(wc -l < test_output.txt)
if [ $LINES -lt 150 ]; then
    echo "[OK] Output concise ($LINES lines)"
else
    echo "[WARN] Output verbose ($LINES lines)"
fi

# Validate Excel
echo "[4/4] Validating Excel..."
EXCEL_FILE=$(ls -t avice_comparison_*.xlsx | head -1)
python3 validate_excel.py $EXCEL_FILE $SECTION

echo "=========================================="
echo "Quick Test Complete"
echo "=========================================="
```

---

## Future Enhancements

### Planned Features

1. **HTML Report Generation**
   - Interactive HTML version of Excel report
   - Clickable sections
   - Visual charts and graphs

2. **Multi-Workarea Comparison**
   - Compare 3+ workareas simultaneously
   - Side-by-side comparison matrix
   - Trend analysis

3. **Historical Tracking**
   - Store comparison results in database
   - Track metrics over time
   - Generate trend reports

4. **Automated Regression**
   - Integrate with AGUR regression framework
   - Automatic comparison of new releases
   - Email alerts for significant changes

5. **Custom Thresholds**
   - User-defined acceptable delta ranges
   - Configurable status indicators
   - Custom alert rules

---

## Code Cleanup Checklist

Before starting Phase 1 implementation, complete this cleanup:

- [ ] Search for `WorkareaComparator` class - review and remove if using old architecture
- [ ] Search for `extract_data_from_workarea` methods - remove direct file parsing
- [ ] Search for `_extract_setup_data_direct` - remove old extraction
- [ ] Search for `_extract_dc_data_direct` - remove old extraction
- [ ] Search for `_extract_pnr_data_direct` - remove old extraction
- [ ] Search for `--compare` CLI handling - update to new architecture
- [ ] Verify no old Excel generation code conflicts with new design
- [ ] Test that old code is fully removed and doesn't interfere

**Command to Search:**
```bash
cd /home/scratch.avice_vlsi/cursor/avice_wa_review
grep -n "class WorkareaComparator\|extract_data_from_workarea\|_extract_.*_data_direct" avice_wa_review.py
```

---

## Implementation Status

### ✅ Phase 1: Setup Section - COMPLETE (Nov 25, 2025)

**Implemented Features:**
- ✅ OutputParser class with section splitting logic
- ✅ parse_setup() method extracting 6 metrics:
  - Unit name
  - RTL TAG
  - IPO name
  - Owner (with fallback extraction from workarea path)
  - Disk usage (%)
  - Available IPOs
- ✅ Setup comparison tab in Excel
- ✅ Summary Dashboard with Alon Vice logo (positioned next to summary table)
- ✅ Email integration via SMTP (smtp.nvidia.com:25)
- ✅ ASCII-only terminal output
- ✅ Automated Excel validation script

**Delivered:**
- 3-tab Excel report: Summary Dashboard, Setup Comparison
- Color-coded comparison (GREEN = improved/same, RED = worse, YELLOW = changed)
- Professional formatting with Alon Vice branding

**Test Results:**
- Tested with pmux workareas (reference: sep10, test: nov_02)
- All 6 Setup metrics extracted successfully
- Excel validated (opens without errors, all data present)
- Email delivered successfully

---

### ✅ Phase 2: Runtime Section - COMPLETE (Nov 25, 2025)

**Implemented Features:**
- ✅ parse_runtime() method extracting 10+ base metrics:
  - DC (Synthesis) runtime
  - PnR runtime per IPO
  - Formal verification runtimes (bbox, fm)
  - GL Check runtime
  - Star (Parasitic Extraction) runtime
  - PV (Physical Verification) runtime
  - Auto PT (Timing) runtime
- ✅ **ENHANCEMENT:** Per-stage PnR breakdown (7 stages per IPO):
  - Begin, Setup, Floorplan, Placement, CTS, Route, Post-Route
  - Extracted from prc.status file
  - Shows TOTAL PnR runtime (bold + highlighted)
- ✅ **ENHANCEMENT:** Single-IPO comparison (smart IPO matching):
  - Automatically compares ONLY common IPOs
  - Skips IPOs that exist in only one workarea
  - Displays [INFO] section showing compared and skipped IPOs
- ✅ Runtime comparison tab in Excel with:
  - Indented per-stage rows (smaller font)
  - Bold TOTAL PnR rows (light blue background)
  - INFO section for IPO comparison status
  - Color coding: FASTER = green, SLOWER = red
- ✅ Dynamic handling of multiple IPOs
- ✅ Updated Summary Dashboard to include Runtime metrics

**Delivered:**
- 3-tab Excel report: Summary Dashboard, Setup Comparison, Runtime Comparison
- Per-stage PnR breakdown (21 stage rows for pmux test case)
- Single-IPO comparison (clean output, no N/A clutter)
- Total metrics per workarea: 37 (6 setup + 31 runtime)

**Test Results:**
- Tested with pmux workareas
- Reference has ipo1000 only
- Test has ipo1000, ipo1001, ipo1002
- Excel shows only ipo1000 comparison (common IPO)
- INFO section shows: "Compared: ipo1000" and "Skipped (test-only): ipo1001, ipo1002"
- Excel reduced from 32 rows to 19 rows (cleaner)
- All automated validation checks passed
- Email delivered successfully

**Key Insights from Implementation:**
- Per-stage breakdown enables root cause analysis (e.g., CTS stage +0.68h was the biggest slowdown in pmux)
- Single-IPO comparison prevents confusion and focuses on relevant data
- Smart IPO matching makes comparison intuitive without requiring extra flags

---

### ✅ Phase 3: Synthesis (DC) Section - COMPLETE (Nov 26, 2025)

**Implementation Summary:**
- ✅ DC metrics parser (`OutputParser.parse_synthesis()`) extracts 25+ metrics
- ✅ DC comparison Excel tab with 6 sections (Version, Area, Cells, Optimization, Config, Timing)
- ✅ Timing by path group comparison table with detailed Setup/Hold metrics
- ✅ Professional purple theme matching DC section styling
- ✅ Reverse logic for errors/warnings (lower is better)
- ✅ Match/Different status for configuration variables
- ✅ Integrated into comparison workflow (setup, runtime, synthesis supported)
- ✅ **DC comparison included in default** (no `-s` flag needed)
- ✅ **Short flags added** (`-c`, `-r`, `-t` for compare, ref, test)
- ✅ **Implicit comparison mode** (--compare optional when --ref and --test provided)

**Key Features:**
- **DC VERSION & QUALITY:** DC version match check, errors, warnings
- **FLOORPLAN & AREA:** Die X/Y (um), Design Area (mm²)
- **CELL COUNTS:** Leaf, Comb, Seq, Buf/Inv (with %), Macro, Nets
- **OPTIMIZATION:** Clock gates removed, Registers removed
- **CONFIGURATION:** Lib Snap, Process, Tracks, Project, Scenario, VT, Arrays
- **TIMING BY PATH GROUP:** Detailed table with Setup/Hold WNS/TNS/NVP per path group, color-coded status

**Usage:**
```bash
# Short flags (recommended):
python3 avice_wa_review.py -r /ref -t /test                    # Default: setup + runtime + DC
python3 avice_wa_review.py -r /ref -t /test -s synthesis       # DC only
python3 avice_wa_review.py -r /ref -t /test --email            # With email

# Long flags (verbose):
python3 avice_wa_review.py --ref /ref --test /test -s setup runtime synthesis --email

# Note: --compare (-c) is optional when both --ref and --test are provided
```

**Pre-Phase 3 Fixes Applied (Nov 25, 2025):**

**Fix 1: Die Dimensions Extraction Priority**
- ✅ **Before:** Used postroute DB (final PnR dimensions after optimizations)
- ✅ **After:** Uses flp/ directory DEF file (initial floorplan dimensions)
- ✅ **Why:** Ensures consistent baseline for comparison (apples-to-apples)
- ✅ **Impact:** Die (X,Y) now shows "(from: flp)" instead of "(from: postroute DB)"
- **File:** `avice_wa_review.py`, function `_extract_floorplan_dimensions()`
- **Lines:** 5615-5736

**Fix 2: QoR Metrics Extraction Enhancement**
- ✅ **Compact display format** (minimized lines like PnR section)
  - Die + Design Area in ONE line
  - Cell counts in ONE line (Leaf, Comb, Seq, Buf/Inv, Macro, Nets)
- ✅ **Timing per path group** (table format with WNS, TNS, NVP)
  - Color coded: RED for violations, GREEN for clean
  - Sorted by TNS (worst first)
- ✅ **Structured data extraction** (returns Dict for Phase 3)
  - Categories: area, cells, timing_by_pathgroup, timing_summary
  - Numbers parsed correctly (commas removed, converted to int/float)
- ✅ **Ready for Phase 3 comparison**
- **File:** `avice_wa_review.py`, functions `_analyze_qor_report()`, `_display_qor_metrics_compact()`
- **Lines:** 5734-5950

**Fix 3: Per-Path-Group Timing Display & Missing QoR Alert (Nov 25, 2025)**
- ✅ **BEFORE:** Regex pattern didn't match actual QoR report format, showing only "Timing Summary"
- ✅ **AFTER:** Updated regex to match: `Timing Path Group 'NAME'...Critical Path Slack:...Total Negative Slack:...No. of Violating Paths:`
- ✅ **Now displays:** Per-path-group timing breakdown for all path groups (CLKGATE, REG2REG, i1_clk, i2_clk, etc.)
- ✅ **Missing QoR Alert:** Yellow warning displayed when QoR report not found (e.g., pmux)
  - Shows: `[WARN] QoR report not found - synthesis may not have completed successfully`
  - Includes expected file location
- ✅ **Tested on:** prt (9 path groups), dqs (9 path groups), pmux (missing report alert)
- **Files Changed:**
  - `avice_wa_review.py` line 5803-5812: Updated regex pattern
  - `avice_wa_review.py` line 5530-5532: Added missing QoR alert
- **Impact:** Users now see detailed per-group timing breakdown AND get alerted when synthesis incomplete

**Fix 11: External Paths Totals Line Added (Nov 26, 2025)**
- ✅ **User Request:** "before continuing to phase 3 i need small improvement to PT section. after printing 'TIMING BREAKDOWN BY PATH TYPE - EXTERNAL PATHS' add extra line with total WNS/TNS/FEP"
- ✅ **Note:** The user said "PT section" but the feature is actually in the PnR section's timing histogram display
- ✅ **Problem Identified:**
  - External paths timing breakdown showed individual categories but no totals
  - Users had to manually calculate overall external path timing impact
  - No quick way to see aggregate external path violations
- ✅ **Solution Implemented:**
  - Added totals calculation after external categories loop
  - WNS: Take worst (most negative) value across all external categories
  - TNS: Sum all TNS values from external categories
  - FEP: Sum all FEP (Failing Endpoint Paths) counts from external categories
  - Color coding based on WNS value (GREEN/YELLOW/RED)
  - Separator line before totals for visual clarity
- ✅ **Implementation Details:**
  - Created `calculate_totals()` nested function:
    * Iterates through all external categories
    * Tracks worst WNS (most negative)
    * Sums TNS and FEP values
    * Returns None if no data available
  - Created `format_totals()` nested function:
    * Formats with ps/ns conversion (like individual rows)
    * Applies integer formatting when appropriate
    * Color codes based on WNS threshold values
  - Display logic:
    * Separator line (`-` * 106)
    * "TOTAL" label in cyan
    * Shows both SETUP and HOLD totals (or N/A if missing)
    * Maintains same column alignment as category rows
- ✅ **Example Output (prt):**
  ```
  Inputs (port->flop)                      -75ps /      -3.12ns /     58        0ns /          0ns /      0
  Inputs (port->cg)                        -73ps /       -679ps /     20        0ns /          0ns /      0
  Outputs (flop->port)                     -70ps /     -21.48ns /    962        0ns /          0ns /      0
  Feedthrough (port->port)                   0ns /          0ns /      0        0ns /          0ns /      0
  ----------------------------------------------------------------------------------------------------------
  TOTAL                                    -75ps /     -25.28ns /   1040                N/A                
  ```
- ✅ **Color Coding:**
  - GREEN: WNS >= -0.01 (meets timing)
  - YELLOW: -0.05 < WNS < -0.01 (small violation)
  - RED: WNS < -0.05 (significant violation)
- ✅ **Tested on:**
  - prt: TOTAL = -75ps / -25.28ns / 1040 (RED)
  - pmux: TOTAL = -80ps / -32.08ns / 1603 (RED)
- ✅ **Benefits:**
  - Immediate visibility into total external path impact
  - No manual calculation needed
  - Color coding highlights severity at a glance
  - Consistent formatting with individual rows
  - Handles missing HOLD data gracefully
- **Files Changed:**
  - `avice_wa_review.py` line 2745-2843: Added totals calculation and display
- **Impact:**
  - Users can quickly assess overall external path timing health
  - Easier to prioritize fixes (external vs internal paths)
  - Professional presentation with clear totals

**Fix 10: Config Sources & Fallback Clarity (Nov 25, 2025)**
- ✅ **User Request:** "some Config Source: are missing in pmux case (under DC section). tell the user which one they are. in addition, when 'QoR report (.qor.rpt) not found' u need to mention the source where you took cell count values"
- ✅ **Problem Identified:**
  - When QoR report missing, cell count source not displayed in warning
  - "Report: File not found" messages were generic, didn't specify WHICH report
  - Die dimensions source not tracked in Data Sources section
- ✅ **Solutions Implemented:**
  1. Cell count source displayed immediately when QoR missing
  2. Die dimensions source added to Data Sources section
  3. Specific report names for "File not found" messages
- ✅ **Changes Made:**
  - Enhanced QoR fallback warning (line 5528-5544):
    * Check for cell_count_rep existence
    * Display "Cell Count Source:" immediately
    * Changed message to "using fallback sources" (plural)
  - Specific report names (line 5551-5563):
    * Created report_map with descriptive names
    * "High Width Logical Cones Report: File not found"
    * "Removed Registers Report: File not found"
  - Die Dimensions source tracking:
    * Updated _extract_floorplan_dimensions() to return 'source_file'
    * Added 'die_dimensions_file' to metrics_dict['sources']
    * Display in Data Sources section (line 6223)
- ✅ **pmux Case - Missing Reports Identified:**
  1. High Width Logical Cones Report (syn_flow/dc/reports/be4rtl/...)
  2. Removed Registers Report (syn_flow/dc/reports/debug/...)
- ✅ **Fallback Sources Used (now displayed):**
  - QoR CSV: syn_flow/dc/qor.csv
  - Cell Count: syn_flow/dc/reports/pmux.cell_count.rep
  - Die Dimensions: flp/pmux_fp.def.gz
- ✅ **Result:**
  - Complete transparency about data sources
  - Users immediately know where cell counts come from when QoR missing
  - Clear identification of which specific reports are missing
- ✅ **Tested on:** pmux (qor.csv fallback)
- **Files Changed:**
  - `avice_wa_review.py` line 5528-5544: Enhanced QoR fallback warning
  - `avice_wa_review.py` line 5551-5563: Specific report names
  - `avice_wa_review.py` line 5630-5747: _extract_floorplan_dimensions returns source_file
  - `avice_wa_review.py` line 5938, 5838: Track die_dimensions_file in sources
  - `avice_wa_review.py` line 6223: Display Die Dimensions in Data Sources
- **Impact:**
  - Users have complete visibility into data sources
  - No more generic "Report: File not found" confusion
  - Clear fallback strategy when QoR report missing

**Fix 9: Timing Table Alignment Fixed (Nov 25, 2025)**
- ✅ **Root Cause Identified:**
  - format_timing() was returning inconsistent widths (10-12 chars instead of 13)
  - NVP columns were :>10 instead of :>11
  - Extra spaces in print statement causing misalignment
- ✅ **Fix Applied:**
  - format_timing() now ALWAYS returns exactly 13 characters
  - Integer ps: f"{int(round(val_ps)):>10}ps" (10 + 2 = 12... wait, let me recalculate)
  - Actually: Integer ps: 10 digits + "ps" = 12 chars, then right-padded to 13
  - Decimal ps: 9.1f + "ps" = 11.1 chars, then right-padded to 13
  - Integer ns: 10 digits + "ns" = 12 chars, then right-padded to 13
  - Decimal ns: 10.3f + "ns" = 12.3 chars, then right-padded to 13
  - Zero values: 13 spaces
  - NVP columns changed from :>10 to :>11
  - Removed extra spaces in print statement (was "  {nvp}", now "{nvp}")
- ✅ **Result:**
  - Perfect column alignment throughout
  - Values line up exactly with headers
  - Comma-separated thousands fit properly ("2,977", "2,094")
  - Professional, scannable table format
- ✅ **Tested on:** pmux (qor.csv), prt (qor.rpt)
- **Files Changed:**
  - `avice_wa_review.py` line 6107-6130: format_timing() returns consistent 13 chars
  - `avice_wa_review.py` line 6138-6156: NVP :>11, removed extra spaces in print
- **Impact:**
  - Perfect table alignment
  - Easy to scan and compare values
  - Professional appearance matching PnR section tables

**Fix 8: Design Area in mm², Source Display, Table Alignment Final (Nov 25, 2025)**
- ✅ **Design Area Converted to mm² with 3 Decimal Places:**
  - **BEFORE:** Design Area: 210945.8736 (in um² - inconsistent with PnR section)
  - **AFTER:** Design Area: 0.211 mm2 (converted to mm², 3 decimals)
  - Matches PnR section format exactly
  - Conversion: um² / 1,000,000 = mm²
  - Examples:
    * pmux: 210945.8736 um² → 0.211 mm²
    * prt: 345184.16 um² → 0.345 mm²
- ✅ **Source Display for Die and Design Area:**
  - **BEFORE:** Die: 1201.56 x 175.56 um (source not shown)
  - **AFTER:** Die: 1201.56 x 175.56 um (from: flp)
  - Users can immediately see data source
  - Source values: "flp", "postroute DB", "route DB", etc.
  - Transparency for validation
- ✅ **Improved Timing Table Alignment (Final):**
  - **Headers now right-aligned** (Setup WNS, Setup TNS, etc.)
  - **NVP columns widened** from 10 to 11 characters (accommodates comma-separated thousands)
  - **Consistent spacing** with extra space before NVP columns
  - Better visual alignment for scanning values
  - Format matches PnR section approach
- ✅ **Tested on:** pmux (qor.csv), prt (qor.rpt)
- **Files Changed:**
  - `avice_wa_review.py` line 6047-6059: Design area conversion to mm² with 3 decimals, source display
  - `avice_wa_review.py` line 6087-6089: Right-aligned headers, NVP column width 11
  - `avice_wa_review.py` line 6134-6156: NVP format updated to :>10 (width 11 with space)
- **Impact:**
  - Design area now consistent with PnR section (mm², 3 decimals)
  - Source transparency - users know where data comes from
  - Professional table formatting with proper alignment
  - Easy to scan and compare timing values

**Fix 7: Header Text, Table Alignment, Design Area from flp/ (Nov 25, 2025)**
- ✅ **Removed "values <1.0ns shown in ps" from Header:**
  - **BEFORE:** "Timing by Path Group: (sorted by Setup TNS, worst first; values <1.0ns shown in ps)"
  - **AFTER:** "Timing by Path Group: (sorted by Setup TNS, worst first)"
  - Cleaner header - units conversion is self-evident from the values
  - Reduces line clutter
- ✅ **Improved Timing Table Alignment:**
  - Updated format_timing() to use consistent widths: 12 characters total
  - Integer ps values: right-aligned with 9 digits + "ps"
  - Decimal ps values: right-aligned with 8.1f + "ps"
  - Integer ns values: right-aligned with 9 digits + "ns"
  - Decimal ns values: right-aligned with 9.3f + "ns"
  - Zero values: right-aligned 12 characters, no units
  - Better visual alignment across all rows
- ✅ **Design Area from flp/ Directory (CRITICAL FIX):**
  - **BEFORE:** Design area extracted from cell_count.rep (incorrect for DC section)
  - **AFTER:** Design area calculated from flp/ die dimensions (die_x * die_y)
  - Added design_area calculation to _extract_floorplan_dimensions()
  - Fixed extraction order in _analyze_qor_csv(): flp/ BEFORE cell_count.rep
  - Fixed extraction logic in _analyze_qor_report(): flp/ with fallback to QoR report
  - **pmux example:**
    * Die: 1201.56 x 175.56 um (from flp/)
    * Design Area: 210945.8736 (= 1201.56 * 175.56, from flp/)
    * Leaf: 751,000 (from cell_count.rep)
  - **prt example:**
    * Die: 600.78 x 574.56 um (from flp/)
    * Design Area: 345184.15679999994 (= 600.78 * 574.56, from flp/)
  - Matches user requirement: "Design Area and X, Y size for DC section should be taken from $WA/flp/ dir"
- ✅ **Tested on:** pmux (qor.csv + flp/), prt (qor.rpt + flp/)
- **Files Changed:**
  - `avice_wa_review.py` line 6074: Removed "(values <1.0ns shown in ps)" from header
  - `avice_wa_review.py` line 6094-6116: Updated format_timing() alignment (12 chars total)
  - `avice_wa_review.py` line 5710-5742: Added design_area calculation to _extract_floorplan_dimensions()
  - `avice_wa_review.py` line 5825-5860: Reordered extraction priority in _analyze_qor_csv() (flp/ first)
  - `avice_wa_review.py` line 5929-5943: Fixed extraction logic in _analyze_qor_report() (flp/ priority)
- **Impact:**
  - Cleaner header text
  - Better visual alignment in timing tables
  - **CRITICAL:** Design area now correctly sourced from flp/ for DC section
  - Complete die dimensions (X, Y, Area) from single authoritative source (flp/)

**Fix 6: Integer Display, Cell Count Fallback, Die Dimensions in CSV Path (Nov 25, 2025)**
- ✅ **Integer Values Without Decimal Points:**
  - **BEFORE:** All values shown with decimals (16.0, 0.0, 320.0ps)
  - **AFTER:** Integer values shown as integers (16, 0, 320ps)
  - Smart detection: Values within 0.0001 of an integer are displayed as integers
  - Examples:
    * 0.0 → "0" (plain zero, no units when zero)
    * 16.0ns → "16ns" (integer ns value)
    * 320.0ps → "320ps" (integer ps value)
    * -7.3ps → "-7.3ps" (non-integer, keeps decimal)
    * 15.681ns → "15.681ns" (non-integer, keeps decimal)
  - Cleaner, more professional output
- ✅ **Cell Count from cell_count.rep (Fallback when qor.rpt Missing):**
  - Extracts total cell count from first data line in `$WA/syn_flow/dc/reports/$unit.cell_count.rep`
  - Also extracts design area from same file
  - Example (pmux): "Leaf: 751,000 | Design Area: 90544.3"
  - File source added to Data Sources section
  - Ensures cell count always available even when qor.rpt missing
- ✅ **Die Dimensions Extraction in qor.csv Fallback Path:**
  - Calls `_extract_floorplan_dimensions()` from `_analyze_qor_csv()`
  - Extracts die dimensions from `flp/` directory even when qor.rpt missing
  - Same priority logic: flp/ directory → PnR stage DBs
  - Ensures complete metrics in CSV fallback mode
- ✅ **Tested on:** pmux (qor.csv + cell_count.rep), prt (full qor.rpt), dqs (full qor.rpt)
- **Files Changed:**
  - `avice_wa_review.py` line 6058-6077: Updated format_timing() to handle integer detection
  - `avice_wa_review.py` line 5807-5853: Enhanced _analyze_qor_csv() to extract cell count and die dimensions
  - `avice_wa_review.py` line 5776: Added cell_count_file to sources dictionary
  - `avice_wa_review.py` line 6202-6208: Added cell_count_file to Data Sources display
- **Impact:**
  - Cleaner output (no unnecessary decimals)
  - Complete metrics even when qor.rpt missing
  - Cell counts always available via fallback mechanism
  - Die dimensions extracted in all scenarios

**Fix 5: Correct Terminology, Units, BeFlow Additions, qor.csv Fallback (Nov 25, 2025)**
- ✅ **Correct Terminology (Consistency):**
  - **BEFORE:** Confusing mix of WHV/THV/NHV in docs (although code internally used correct names)
  - **AFTER:** Consistent WNS/TNS/NVP for both setup and hold timing
  - Setup timing: Setup WNS, Setup TNS, Setup NVP
  - Hold timing: Hold WNS, Hold TNS, Hold NVP
  - Matches industry-standard terminology
- ✅ **Units Conversion (<1.0ns → ps):**
  - Values <1.0ns automatically displayed in picoseconds (ps)
  - Values >=1.0ns displayed in nanoseconds (ns)
  - Examples: "-7.3ps", "-480.5ps", "-5.649ns", "16.186ns"
  - Makes small timing values easier to read
- ✅ **Inline Sorting Explanation:**
  - Header now shows: "(sorted by Setup TNS, worst first; values <1.0ns shown in ps)"
  - No extra line consumed
  - Users immediately understand table organization
- ✅ **BeFlow Configuration Additions:**
  - BEFLOW_ROOT: Shows BeFlow toolchain version path
  - BEFLOW_CONFIG_SITE: Shows site-specific configuration path
  - Full arrays list: No truncation (was already implemented, verified working)
  - Example: "BEFLOW_ROOT: /home/nbu_be_tools/beflow/1.0/2025_ww13_01_rev13"
- ✅ **qor.csv Fallback (Already Implemented, Now Verified):**
  - When rtl2gate.qor.rpt is missing, automatically uses qor.csv
  - Displays yellow warning with fallback location
  - Extracts timing per path group from CSV format
  - Example: pmux unit successfully uses qor.csv fallback
- ✅ **Tested on:** pmux (qor.csv fallback), prt (correct terminology + units), dqs
- **Files Changed:**
  - `avice_wa_review.py` line 5934-5942: Fixed variable names in regex extraction
  - `avice_wa_review.py` line 6039: Added inline sorting + units explanation
  - `avice_wa_review.py` line 6329-6397: BeFlow config already extracts BEFLOW_ROOT, BEFLOW_CONFIG_SITE, full arrays
  - `avice_wa_review.py` line 5532-5538: qor.csv fallback already implemented
  - `avice_wa_review.py` line 5747-5842: _analyze_qor_csv() already implemented
- **Impact:** 
  - Clear, consistent terminology across all timing displays
  - Better readability for small timing values (ps vs ns)
  - Complete BeFlow configuration visibility
  - Graceful degradation when QoR report missing (pmux case handled)

**Fix 4: Hold Timing, BeFlow Compact, Clock Gates/Registers, Sources (Nov 25, 2025)**
- ✅ **Hold Timing Values Added:**
  - Table now shows: Setup WNS/TNS/NVP + Hold WHV/THV/NHV (6 columns per path group)
  - WHV = Worst Hold Violation, THV = Total Hold Violation, NHV = No. of Hold Violations
  - Color coded: RED (violations), GREEN (clean) for both setup and hold
  - Example: i1_clk shows Setup: -0.007ns WNS / Hold: -0.035ns WHV
- ✅ **Compact BeFlow Configuration Display:**
  - **BEFORE:** 10+ lines, one variable per line
  - **AFTER:** 6 compact lines with grouped data
    * Line 1: Lib Snap | Process | Tracks | Project
    * Line 2: Scenario | VT Types
    * Lines 3-5: Paths (StdCell, Memories, Arrays, BE IP)
    * Line 6: Config Source (file path)
  - Saves ~40% terminal output lines
- ✅ **Clock Gates & Registers in Structured Data:**
  - New "Optimization Summary" section displays: "Clock gates removed: N | Removed registers: M"
  - Values extracted from debug reports and added to metrics dictionary
  - Ready for Phase 3 comparison
- ✅ **Data Sources Display:**
  - New "Data Sources" section shows file paths for:
    * QoR Report
    * Clock Gates file
    * Registers file
    * Config Source (BeFlow)
  - Enables users to verify where metrics came from
  - Critical for debugging and validation
- ✅ **Tested on:** prt (0 clock gates, 3,708 registers), dqs (16 clock gates, 8,853 registers)
- **Files Changed:**
  - `avice_wa_review.py` line 5813-5830: Updated regex to extract hold timing (WHV, THV, NHV)
  - `avice_wa_review.py` line 5845-5869: Added clock gates/registers extraction to metrics dictionary
  - `avice_wa_review.py` line 5927-5965: Updated table display to show setup + hold timing
  - `avice_wa_review.py` line 6009-6029: Added "Optimization Summary" and "Data Sources" sections
  - `avice_wa_review.py` line 6180-6215: Improved BeFlow config display (compact format)
- **Impact:** 
  - Complete timing picture (setup AND hold violations visible)
  - More readable, compact terminal output
  - All Phase 3 comparison metrics now structured and sourced
  - Users can trace every metric back to its source file

**Planned Implementation:**
- parse_synthesis() method
- DC Version comparison
- QoR metrics comparison ✅ Already enhanced
- Timing comparison per path group ✅ Already prepared
- Cell count analysis ✅ Already prepared
- Die dimensions (from $WA/flp/) ✅ Already fixed
- Design Area (from QoR report) ✅ Already prepared
- Synthesis comparison Excel tab

**Status:** Ready to begin Phase 3 implementation

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-25 | 1.0 | avice | Initial plan created |
| 2025-11-25 | 1.1 | avice | Updated to reuse `-s` flag instead of new flag |
| 2025-11-25 | 1.2 | avice | Added cleanup note for old/incorrect code from initial implementation |
| 2025-11-25 | 1.3 | avice | **MAJOR UPDATE:** Clean slate decision, ASCII-only output rule, comprehensive per-section testing strategy |
| 2025-11-25 | 1.4 | avice | **Added:** Excel automated validation (openpyxl), multi-unit testing strategy, validation scripts, quick test tools |
| 2025-11-25 | 1.5 | avice | **PHASE 1 & 2 COMPLETE:** Documented Setup section (6 metrics), Runtime section (31 metrics), per-stage PnR breakdown, single-IPO comparison enhancement |
| 2025-11-25 | 1.6 | avice | **PRE-PHASE 3 FIX:** Die dimensions extraction now prioritizes flp/ directory over postroute DB; Number formatting with units ("Hr") in Excel |
| 2025-11-25 | 1.7 | avice | **QOR METRICS ENHANCED:** Compact display format, timing per path group (WNS/TNS/NVP), color coding, structured data for Phase 3 comparison |
| 2025-11-25 | 1.8 | avice | **FIX 3 APPLIED:** Per-path-group timing display fixed (updated regex), missing QoR alert added, tested on 3 units |
| 2025-11-25 | 1.9 | avice | **FIX 4 APPLIED:** Hold timing values added (WHV/THV/NHV), BeFlow config compact format, clock gates/registers in structured data, sources display |
| 2025-11-25 | 2.0 | avice | **FIX 5 APPLIED:** Correct terminology (WNS/TNS/NVP for both setup and hold), units conversion (ps<1.0ns), inline sorting explanation, BeFlow additions (BEFLOW_ROOT, BEFLOW_CONFIG_SITE, full arrays), qor.csv fallback verified |
| 2025-11-25 | 2.1 | avice | **FIX 6 APPLIED:** Integer values without decimals (16.0→16, 0.0→0), cell count from cell_count.rep when qor.rpt missing, die dimensions extraction in qor.csv fallback path |
| 2025-11-25 | 2.2 | avice | **FIX 7 APPLIED:** Removed "values <1.0ns shown in ps" from header, improved timing table alignment, design area from flp/ (die_x * die_y) with fallback priority fixed |
| 2025-11-25 | 2.3 | avice | **FIX 8 APPLIED:** Design area converted to mm² with 3 decimals (matching PnR section), source displayed for die/area (from: flp), improved timing table alignment (right-aligned headers, NVP column wider for commas) |
| 2025-11-25 | 2.4 | avice | **FIX 9 APPLIED:** Fixed timing table alignment - format_timing() returns consistent 13 chars, NVP columns 11 chars, removed extra spaces in print statement |
| 2025-11-25 | 2.5 | avice | **FIX 10 APPLIED:** Config sources identified when QoR missing - cell count source displayed in warning, die dimensions source added to Data Sources, specific report names for file not found |
| 2025-11-26 | 2.6 | avice | **FIX 11 APPLIED:** External paths totals line added to PnR timing breakdown - displays total WNS (worst), TNS (sum), FEP (sum) after external path categories with color coding |
| 2025-11-27 | 3.0 | avice | **PHASE 3 COMPLETE:** DC (Synthesis) comparison fully implemented - 44 metrics extracted (QoR, timing by path group, cell counts, config), Excel DC Comparison tab with purple theme, default sections now include 'synthesis' |
| 2025-11-27 | 3.1 | avice | **CLI ENHANCEMENTS:** Short flags added (-c, -r, -t, -e), --compare optional if --ref and --test provided, runtime delta 30min threshold, PnR Begin/Setup stages removed, Excel columns widened, setup tab new metrics (Environment, NBU, BE_OVERRIDE_TOOLVERS, BEFLOW_CONFIG_REV) |
| 2025-11-27 | 3.2 | avice | **TAB CONSOLIDATION:** Summary Dashboard and Setup Comparison merged into single "Setup & Summary" tab (10 metrics total), reduces redundancy, improves UX |
| 2025-11-27 | 4.0 | avice | **PHASE 4 COMPLETE:** PnR comparison fully implemented - 30+ metrics extracted (die/area, cells, VT distribution, clock gating, routing, violations, DFT, external timing, clock latencies), Excel PnR Comparison tab (blue theme, 7 sections), default sections now include 'pnr', tested on multiple units (prt, fth), parser handles missing data gracefully, Phase 1-4 supported sections now complete |
| 2025-11-27 | 4.1 | avice | **PHASE 4.1 + 4.2 ENHANCEMENTS:** Added 16 new PnR metrics - Phase 4.1 Quick Wins: DelBuf count, FFs by Clock, Ungated FFs details, Max CG Fanout, Non-Scan Flops, Max Transition Violations (12 metrics); Phase 4.2 High Value: Internal Clock Domain Timing per-clock, Clock Tree Summary per-clock (Buf/Inv/CG/Sinks/Taps), Power Summary per-group (comb/seq/physical/total) (20+ metrics); Total PnR metrics increased from 30 to 46 (+53%), Excel sections increased from 7 to 14 (+100%), rows increased from 52 to 139 (+168%) |
| 2025-11-27 | 4.2 | avice | **FLOW CONFIGURATION ADDED:** Extracted 9 PnR flow configuration parameters (FLOW_PATH, CUSTOM_SCRIPTS_DIR, MULTIBIT_FLOP, Library Snapshot, NV Process, Tracks Number, Project, Default Scenario, VT Types), moved Flow Configuration to Section 1 (top of PnR tab, row 4) for immediate visibility of tool versions and config drift, critical for root cause analysis of QoR differences, tested and caught CUSTOM_SCRIPTS_DIR difference in FTH comparison (ww36 vs ww40) |
| 2025-11-30 | 4.3 | avice | **EXCEL FORMATTING IMPROVEMENTS:** Enhanced PnR tab formatting - added units to all values (um, mm², ps, %, KB, cells, FFs, gates, mW, uW), implemented 2 decimal places for floating-point numbers (0.46, 600.78) and no decimals for integers (734903, 14), cleaned metric names (removed redundant units), delta column now includes units, improved readability and professional appearance, validated across all 14 sections with 46 metrics, all format requirements met |
| 2025-11-30 | 4.4 | avice | **EXCEL SUMMATION FIX (CRITICAL):** Fixed Excel cells to be SUMMABLE while displaying units - changed from text concatenation ("600.78 um") to numeric values (600.78) with Excel custom number formats ('0.00 "um"'), implemented 22 unit-specific formats with proper decimals and thousands separators (#,##0), now supports SUM()/AVERAGE()/formulas/pivot tables/charts, validated with real summation tests (cell counts: 1.6M, timing: -203ps, areas: 0.80mm²), 64 numeric cells (87% success rate), professional Excel behavior achieved |
| 2025-11-30 | 4.5 | avice | **FEEDTHROUGH N/A FIX + % CHANGE NUMERIC:** Fixed two critical issues - (1) FEEDTHROUGH timing values N/A for PMUX: enhanced external timing parser regex to handle both ps and ns units, added smart unit conversion logic (only convert ns→ps when value < 1.0 for readability: 9.13ns stays as ns, 0.5ns converts to 500ps), now works for all designs regardless of timing unit; (2) % Change column was TEXT not numeric: changed from storing "+5.1%" as string to storing 0.051 as decimal with Excel format '+0.0%;-0.0%', enables SUM/AVERAGE on percentage column; validated on both FTH (ps timing) and PMUX (ns timing) workareas, all Excel features now fully functional |

---

**End of Document**

