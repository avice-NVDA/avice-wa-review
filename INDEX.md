# avice_wa_review.py - Comprehensive Index

## Overview
**File**: `avice_wa_review.py`  
**Total Lines**: 8128  
**Purpose**: Comprehensive workarea review tool for ASIC/SoC design flow analysis

---

## Table of Contents
1. [Utility Classes](#utility-classes)
2. [Main WorkareaReviewer Class](#main-workareareviewer-class)
3. [Analysis Stages (run_* methods)](#analysis-stages)
4. [Extraction Methods](#extraction-methods)
5. [Generation Methods](#generation-methods)
6. [Analysis Helper Methods](#analysis-helper-methods)
7. [Display & Output Methods](#display--output-methods)

---

## Utility Classes

### LVSViolationParser (Lines 101-173)
- **Purpose**: Parser for LVS error files to extract detailed violation information
- **Methods**:
  - `parse_lvs_errors(file_path)` - Parse LVS error files

### Color (Lines 175-186)
- **Purpose**: ANSI color codes for terminal output
- **Constants**: RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, BOLD, RESET

### FlowStage (Lines 188-205)
- **Purpose**: Enum for design flow stages
- **Stages**:
  - SETUP
  - SYNTHESIS
  - PLACE_ROUTE
  - PNR_ANALYSIS
  - CLOCK_ANALYSIS
  - FORMAL_VERIFICATION
  - PARASITIC_EXTRACTION
  - SIGNOFF_TIMING
  - PHYSICAL_VERIFICATION
  - GL_CHECK
  - ECO_ANALYSIS
  - NV_GATE_ECO
  - BLOCK_RELEASE
  - RUNTIME
  - COMMON

### DesignInfo (Lines 208-215)
- **Purpose**: Data class for design information
- **Attributes**: workarea, top_hier, tag, ipo, all_ipos

### LogoDisplay (Lines 217-247)
- **Purpose**: Handle logo display functionality
- **Methods**:
  - `get_logo_path()` - Get path to logo image
  - `display_logo()` - Display graphical logo
  - `print_ascii_logo()` - Print ASCII art logo

### FileUtils (Lines 249-302)
- **Purpose**: Utility functions for file operations
- **Methods**:
  - `realpath(path)` - Get real absolute path
  - `file_exists(path)` - Check if file exists
  - `dir_exists(path)` - Check if directory exists
  - `find_files(pattern, base_path)` - Find files matching pattern
  - `grep_file(pattern, file_path)` - Search for pattern in file
  - `run_command(cmd)` - Execute shell command

---

## Main WorkareaReviewer Class (Lines 304-7977)

### Initialization & Validation (Lines 307-491)

#### Core Methods
- `__init__(workarea, ipo, show_logo, skip_validation)` (Line 307)
- `_validate_workarea()` (Line 323) - Validate workarea structure
- `_extract_design_info()` (Line 436) - Extract design information

#### Display Methods
- `print_header(stage)` (Line 494) - Print section header with index number
- `print_file_info(file_path, description)` (Line 500) - Print file information

#### Stage Index Mapping (Line 208)
The `STAGE_INDEX` dictionary maps each `FlowStage` to its index number for display purposes.

---

## Analysis Stages

### 1. Setup Analysis (Line 1963)
```python
def run_setup_analysis()
```
**Analyzes**: Design setup and environment configuration
- Environment information
- Design configuration
- Tool versions
- Setup files

**Supporting Methods**:
- `_extract_environment_info()` (Line 1990)

---

### 2. Runtime Analysis (Line 6267)
```python
def run_runtime_analysis()
```
**Analyzes**: Runtime statistics for all flow stages
- PnR stage runtimes
- DC synthesis runtime
- StarRC extraction runtime
- PT timing analysis runtime
- Formal verification runtime
- GL check runtime
- PV runtime
- ECO generation runtime
- Timeline visualization

**Supporting Methods**:
- `_extract_star_runtime()` (Line 6715)
- `_extract_auto_pt_runtime()` (Line 6745)
- `_extract_formal_runtime()` (Line 6822)
- `_extract_gl_check_runtime()` (Line 6889)
- `_extract_auto_pt_fix_runtime()` (Line 6942)
- `_extract_gen_eco_runtime()` (Line 6967)
- `_extract_pv_runtime()` (Line 6989)
- `_extract_timestamps_from_log(log_file)` (Line 7063)
- `_calculate_start_time_from_duration(end_time_epoch, runtime_str)` (Line 7118)
- `_print_runtime_summary_table(runtime_data, pnr_runtimes, runtime_timestamps)` (Line 7135)
- `_print_runtime_summary_table_advanced(runtime_data, pnr_runtimes)` (Line 7229)
- `_generate_runtime_html_report(...)` (Line 7290)
- `_extract_detailed_pnr_stage_data(prc_status_file)` (Line 7333)
- `_create_runtime_html_content(...)` (Line 7383)

---

### 3. Synthesis Analysis (Line 1623)
```python
def run_synthesis_analysis()
```
**Analyzes**: Design Compiler (DC) synthesis results
- QoR reports
- Area, timing, power metrics
- Floorplan dimensions
- BEFLOW configuration

**Supporting Methods**:
- `_extract_floorplan_dimensions()` (Line 1717)
- `_analyze_qor_report(qor_file)` (Line 1762)
- `_analyze_beflow_config(beflow_file)` (Line 1883)

---

### 4. PnR Analysis (Line 2573)
```python
def run_pnr_analysis()
```
**Analyzes**: Place & Route (PnR) implementation results
- PRC status and configuration
- Flow sequences and hooks
- Step execution details
- PnR variables and runsets
- Postroute data parameters
- Timing histograms
- Power summaries

**Supporting Methods**:
- `_analyze_pnr_status(prc_status_file)` (Line 2051)
- `_analyze_step_sequence(steps, category_name)` (Line 2144)
- `_extract_prc_configuration(prc_file)` (Line 2192)
- `_print_flow_sequence_with_hooks(ipo, flow_sequence, hooks)` (Line 2217)
- `_extract_yaml_prc_configuration(content)` (Line 2260)
- `_verify_tcl_usage_in_prc(prc_file, common_dir)` (Line 2474)
- `_extract_pnr_flow_variables(runset_file)` (Line 2528)
- `_extract_power_summary_table(power_file)` (Line 488)
- `_extract_pnr_timing_histogram()` (Line 538)
- `_extract_postroute_data_parameters(data_file, stage)` (Line 1048)

---

### 5. Clock Analysis (Line 3123)
```python
def run_clock_analysis()
```
**Analyzes**: Clock tree implementation and metrics
- Clock tree data from PnR
- Clock latency from PT
- Clock network statistics

**Supporting Methods**:
- `_extract_clock_tree_data(clock_file)` (Line 742)
- `_extract_pt_clock_latency(pt_clock_file)` (Line 833)

---

### 6. Formal Verification (Line 3143)
```python
def run_formal_verification()
```
**Analyzes**: Formal verification status and results
- Verification status
- Timestamps and duration
- Comparison with ECO timestamps

**Supporting Methods**:
- `_extract_formal_verification_status(log_file)` (Line 897)
- `_display_formal_timestamps(log_file)` (Line 972)
- `_check_formal_vs_eco_timestamps(formal_end_time)` (Line 1005)
- `_check_rtl_formal_exists()` (Line 7320)

---

### 7. Parasitic Extraction (Line 3167)
```python
def run_parasitic_extraction()
```
**Analyzes**: StarRC parasitic extraction results
- Extraction logs
- SPEF file status
- Extraction statistics

**Supporting Methods**:
- `_extract_star_runtime()` (Line 6715)

---

### 8. Signoff Timing (Line 3230)
```python
def run_signoff_timing()
```
**Analyzes**: PrimeTime (PT) signoff timing analysis
- Timing data from work areas
- Setup/hold violations
- TNS/WNS metrics
- Path group summaries
- Multi-corner analysis

**Supporting Methods**:
- `_extract_timing_data_from_work_areas()` (Line 3331)
- `_generate_timing_summary_html(timing_data)` (Line 3521)
- `_generate_timing_summary_report()` (Line 3959)
- `_extract_auto_pt_runtime()` (Line 6745)
- `_extract_auto_pt_fix_runtime()` (Line 6942)

---

### 9. Physical Verification (Line 4122)
```python
def run_physical_verification()
```
**Analyzes**: Physical verification (DRC, LVS, Antenna)
- PV flow status and configuration
- DRC errors
- LVS violations
- Antenna violations
- Flow sequences and timestamps

**Supporting Methods**:
- `_show_flow_timeline(flow_name, local_flow_dirs)` (Line 4202)
- `_show_pv_flow_timestamps()` (Line 4297)
- `_analyze_pv_flow()` (Line 4302)
- `_parse_pv_flow_status(status_file)` (Line 4324)
- `_parse_pv_flow_config(config_file)` (Line 4408)
- `_extract_flow_sequences(content)` (Line 4433)
- `_extract_flow_sequence_simple(content, flow_type)` (Line 4455)
- `_analyze_drc_errors(drc_file)` (Line 4492)
- `_analyze_antenna_errors(antenna_file)` (Line 4547)
- `_extract_pv_runtime()` (Line 6989)

---

### 10. GL Check (Line 5539)
```python
def run_gl_check()
```
**Analyzes**: Gate-level checks and verification
- GL check errors (waived/non-waived)
- Checker statistics
- Error details and violations
- Don't-use cells and clock tree cells
- Key reports and logs

**Supporting Methods**:
- `_analyze_gl_check_errors(waived_file, non_waived_file)` (Line 4576)
- `_generate_gl_check_html_content(...)` (Line 4662)
- `_generate_gl_check_html_report(...)` (Line 5405)
- `_extract_gl_check_runtime()` (Line 6889)

---

### 11. ECO Analysis (Line 5921)
```python
def run_eco_analysis()
```
**Analyzes**: Engineering Change Order (ECO) analysis
- ECO commands and changes
- Don't-use cell violations in ECOs
- ECO timing impact
- BEFLOW path validation

**Supporting Methods**:
- `_find_beflow_path()` (Line 5625)
- `_check_eco_for_dont_use_cells(eco_file, eco_commands)` (Line 5663)
- `_extract_gen_eco_runtime()` (Line 6967)

---

### 12. NV Gate ECO (Line 6021)
```python
def run_nv_gate_eco()
```
**Analyzes**: NVIDIA-specific gate ECO flow
- NV gate ECO status
- ECO statistics
- Implementation details

---

### 13. Block Release (Line 6203)
```python
def run_block_release()
```
**Analyzes**: Block release readiness
- Release information
- Release logs
- UMake block release commands

**Supporting Methods**:
- `_extract_block_release_info(release_log)` (Line 5980)
- `_extract_umake_block_release_commands()` (Line 5995)

---

### 14. Common Analysis (Line 7960)
```python
def run_common_analysis()
```
**Analyzes**: Common checks across all stages
- Generic checks applicable to all flow stages

---

### 16. Complete Review (Line 6242)
```python
def run_complete_review()
```
**Executes**: All analysis stages in sequence
- Runs all analysis methods
- Generates comprehensive workarea review

---

## Extraction Methods

### Data Extraction
- `_extract_design_info()` (Line 436) - Extract basic design info
- `_extract_environment_info()` (Line 1990) - Extract environment variables
- `_extract_floorplan_dimensions()` (Line 1717) - Extract floorplan data
- `_extract_power_summary_table(power_file)` (Line 488) - Extract power metrics
- `_extract_pnr_timing_histogram()` (Line 538) - Extract timing histogram from PnR
- `_extract_timing_histogram_for_html()` (Line 625) - Extract timing data for HTML
- `_extract_clock_tree_data(clock_file)` (Line 742) - Extract clock tree metrics
- `_extract_pt_clock_latency(pt_clock_file)` (Line 833) - Extract PT clock data
- `_extract_formal_verification_status(log_file)` (Line 897) - Extract formal status
- `_extract_postroute_data_parameters(data_file, stage)` (Line 1048) - Extract postroute data
- `_extract_prc_configuration(prc_file)` (Line 2192) - Extract PRC config
- `_extract_yaml_prc_configuration(content)` (Line 2260) - Extract YAML PRC config
- `_extract_pnr_flow_variables(runset_file)` (Line 2528) - Extract PnR variables
- `_extract_timing_data_from_work_areas()` (Line 3331) - Extract PT timing data
- `_extract_flow_sequences(content)` (Line 4433) - Extract PV flow sequences
- `_extract_flow_sequence_simple(content, flow_type)` (Line 4455) - Simple flow sequence extraction
- `_extract_block_release_info(release_log)` (Line 5980) - Extract release info
- `_extract_umake_block_release_commands()` (Line 5995) - Extract UMake commands

### Runtime Extraction
- `_extract_star_runtime()` (Line 6715) - StarRC runtime
- `_extract_auto_pt_runtime()` (Line 6745) - Auto PT runtime
- `_extract_formal_runtime()` (Line 6822) - Formal verification runtime
- `_extract_gl_check_runtime()` (Line 6889) - GL check runtime
- `_extract_auto_pt_fix_runtime()` (Line 6942) - Auto PT fix runtime
- `_extract_gen_eco_runtime()` (Line 6967) - ECO generation runtime
- `_extract_pv_runtime()` (Line 6989) - PV runtime
- `_extract_timestamps_from_log(log_file)` (Line 7063) - Extract timestamps
- `_extract_detailed_pnr_stage_data(prc_status_file)` (Line 7333) - Extract detailed PnR data

---

## Generation Methods

### HTML Report Generation
- `_generate_image_html_report()` (Line 688) - Generate image debug report
- `_generate_postroute_html_table(all_params)` (Line 1096) - Generate postroute HTML table
- `_generate_timing_histogram_html()` (Line 2668) - Generate timing histogram HTML
- `_generate_timing_summary_html(timing_data)` (Line 3521) - Generate timing summary HTML
- `_generate_timing_summary_report()` (Line 3959) - Generate timing report
- `_generate_gl_check_html_content(...)` (Line 4662) - Generate GL check HTML content
- `_generate_gl_check_html_report(...)` (Line 5405) - Generate GL check HTML report
- `_generate_runtime_html_report(...)` (Line 7290) - Generate runtime HTML report

### HTML Table Creation
- `_create_postroute_html_table(stage_data, ...)` (Line 1159) - Create postroute HTML table
- `_create_timing_histogram_html(category_data, sub_category_data, scenario_data, stage)` (Line 2729) - Create timing histogram HTML
- `_create_runtime_html_content(...)` (Line 7383) - Create runtime HTML content

---

## Analysis Helper Methods

### Flow Analysis
- `_analyze_qor_report(qor_file)` (Line 1762) - Analyze QoR report
- `_analyze_beflow_config(beflow_file)` (Line 1883) - Analyze BEFLOW config
- `_analyze_pnr_status(prc_status_file)` (Line 2051) - Analyze PnR status
- `_analyze_step_sequence(steps, category_name)` (Line 2144) - Analyze step sequences
- `_analyze_pv_flow()` (Line 4302) - Analyze PV flow
- `_analyze_drc_errors(drc_file)` (Line 4492) - Analyze DRC errors
- `_analyze_antenna_errors(antenna_file)` (Line 4547) - Analyze antenna errors
- `_analyze_gl_check_errors(waived_file, non_waived_file)` (Line 4576) - Analyze GL errors

### Parsing Methods
- `_parse_pv_flow_status(status_file)` (Line 4324) - Parse PV flow status
- `_parse_pv_flow_config(config_file)` (Line 4408) - Parse PV flow config

### Verification & Checking
- `_verify_tcl_usage_in_prc(prc_file, common_dir)` (Line 2474) - Verify TCL usage
- `_check_formal_vs_eco_timestamps(formal_end_time)` (Line 1005) - Check timestamp consistency
- `_check_eco_for_dont_use_cells(eco_file, eco_commands)` (Line 5663) - Check don't-use cells
- `_check_rtl_formal_exists()` (Line 7320) - Check if RTL formal exists

### Utility Methods
- `_find_beflow_path()` (Line 5625) - Find BEFLOW path
- `_calculate_start_time_from_duration(end_time_epoch, runtime_str)` (Line 7118) - Calculate start time

---

## Display & Output Methods

### Terminal Output
- `print_header(stage)` (Line 494) - Print section header with index number
- `print_file_info(file_path, description)` (Line 500) - Print file info
- `_print_flow_sequence_with_hooks(ipo, flow_sequence, hooks)` (Line 2217) - Print flow sequence
- `_display_formal_timestamps(log_file)` (Line 972) - Display formal timestamps
- `_print_runtime_summary_table(runtime_data, pnr_runtimes, runtime_timestamps)` (Line 7135) - Print runtime table
- `_print_runtime_summary_table_advanced(runtime_data, pnr_runtimes)` (Line 7229) - Print advanced runtime table

**Note**: Section headers now include index numbers that correspond to this INDEX.md document.

**Example Output**:
```
----------------------------------- [1] Setup -----------------------------------
----------------------------------- [2] Runtime -----------------------------------
----------------------------------- [3] Synthesis (DC) -----------------------------------
----------------------------------- [4] PnR Analysis -----------------------------------
```

### Timeline Display
- `_show_flow_timeline(flow_name, local_flow_dirs)` (Line 4202) - Show flow timeline
- `_show_pv_flow_timestamps()` (Line 4297) - Show PV flow timestamps

---

## Main Entry Point

### main() (Line 7978)
**Purpose**: Command-line interface entry point
- Argument parsing
- Workarea validation
- Analysis execution
- Error handling

**Usage**:
```bash
python avice_wa_review.py <workarea> [options]
```

**Options**:
- `--ipo`: Specify IPO to analyze
- `--stage`: Specific stage to analyze
- `--no-logo`: Skip logo display
- `--skip-validation`: Skip workarea validation

---

## Key Features Summary

### Multi-Stage Analysis
1. ✓ Setup & Environment
2. ✓ Runtime Analysis
3. ✓ Synthesis (DC)
4. ✓ Place & Route (PnR) Analysis
5. ✓ Clock Analysis
6. ✓ Formal Verification
7. ✓ Parasitic Extraction (Star)
8. ✓ Signoff Timing (PT)
9. ✓ Physical Verification (DRC/LVS)
10. ✓ GL Checks
11. ✓ ECO Analysis
12. ✓ NV Gate ECO
13. ✓ Block Release
14. ✓ Common Checks

### HTML Report Generation
- Postroute data tables
- Timing histograms
- Timing summaries
- GL check reports
- Runtime visualizations
- Image debug reports

### Data Extraction
- Timing metrics (TNS, WNS, violations)
- Power metrics
- Area metrics
- Clock tree data
- Error summaries
- Runtime statistics

### File Support
- Log files (.log, .rpt)
- Configuration files (.prc, .yaml)
- Status files
- Data files
- Error reports
- TCL scripts

---

## Dependencies

### Python Modules
- os, sys, re
- argparse
- glob
- gzip
- subprocess
- datetime
- enum
- dataclasses
- typing

### External Tools
- Unix shell commands (grep, find, etc.)
- ASIC design tools (references to DC, PT, PV, etc.)

---

## File Structure

```
avice_wa_review.py (8128 lines)
├── Imports & Constants (Lines 1-90)
├── Utility Classes (Lines 91-302)
│   ├── LVSViolationParser
│   ├── Color
│   ├── FlowStage
│   ├── DesignInfo
│   ├── LogoDisplay
│   └── FileUtils
├── WorkareaReviewer Class (Lines 304-7977)
│   ├── Initialization (Lines 307-473)
│   ├── Data Extraction (Lines 474-1622)
│   ├── Analysis Stages (Lines 1623-7959)
│   └── Runtime Analysis (Lines 6267-7959)
└── Main Entry Point (Lines 7978-8128)
```

---

## Version & Metadata

**Author**: Alon Vice (avice@nvidia.com)  
**Copyright**: 2025 Alon Vice  
**Tool Suite**: Alon Vice Tools  

---

*Index generated: October 9, 2025*

