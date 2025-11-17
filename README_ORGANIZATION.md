# Avice Workarea Review Tool - Organization

This directory contains all files related to the `avice_wa_review.py` tool for comprehensive ASIC/SoC design workarea analysis.

## Directory Structure

```
avice_wa_review/
├── Core Scripts
│   ├── avice_wa_review.py              # Main Python script (8,150 lines)
│   ├── avice_image_debug_report.py     # Image debug report generator (1,370 lines)
│   ├── batch_review.py                 # Batch workarea review script (237 lines)
│   ├── summarize_results.py            # Results summarization tool (237 lines)
│   └── docs_generator.py               # Documentation generator (510 lines)
│
├── Documentation
│   ├── README_avice_wa_review.md       # Main user documentation (360 lines)
│   ├── README_ORGANIZATION.md          # Organization and structure guide (this file)
│   ├── INDEX.md                        # Complete script index with line numbers (583 lines)
│   ├── .cursor/
│   │   └── rules/
│   │       └── architecture.mdc        # Architecture rules and standards (940 lines - AUTO-LOADED)
│   ├── MASTER_DASHBOARD.md             # Master Dashboard complete documentation (400 lines)
│   ├── HTML_PORTABILITY_IMPROVEMENTS.md # HTML portability fixes summary (600 lines)
│   ├── DEVELOPMENT_HISTORY.md          # Development history and changes (350 lines)
│   └── CONSOLIDATION_PLAN.md           # Documentation consolidation plan
│
├── Configuration & Data
│   └── workareas.txt                   # Workarea tracking database (41 lines)
│
├── Utilities
│   ├── cleanup_test_reports.sh         # Cleanup HTML test reports
│   └── tablog_launcher.sh              # Tablog viewer launcher
│
├── Assets
│   ├── icons/                          # HTML report icons
│   │   ├── *.png                       # PNG icon files
│   │   ├── *.svg                       # SVG source files
│   │   └── *.b64                       # Base64 encoded icons for HTML
│   └── images/                         # Logo and images
│       └── avice_logo.png              # Alon Vice logo
│
└── Output Directories
    ├── review_results/                 # Review output files
    │   └── *.txt                       # Review result files
    └── test_results/                   # Test output files
        └── *.txt                       # Test review results
```

## Removed Files (Cleanup)

The following files were removed during code cleanup as they were unused or redundant:

### October 9, 2025 Cleanup
- `extract_timing_summary.py` - Standalone PT timing extraction (functionality fully integrated into main script at Lines 3230-3959)
- `unix_shell_compatibility_guide.md` - Merged into `.cursor/rules/architecture.mdc` for better organization

### Previous Cleanup
- `lvs_analyzer.py` - LVS analysis (functionality integrated into main script)
- `log_viewer_gui.py` - PyQt5 GUI log viewer (unused)
- `ascii_utils.py` - ASCII utilities (functionality integrated)
- `MtbuPyUtils.py` - Utility functions (unused)
- `avice_prime_log_viewer.csh` - Shell script (unused)

## Usage

### From any directory (Recommended):
```bash
# Use the launcher script (recommended)
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea

# Or run directly with Python
/home/utils/Python/builds/3.11.9-20250715/bin/python3 /home/avice/scripts/avice_wa_review/avice_wa_review.py /path/to/workarea
```

### From within the avice_wa_review directory:
```bash
cd /home/avice/scripts/avice_wa_review
/home/utils/Python/builds/3.11.9-20250715/bin/python3 avice_wa_review.py /path/to/workarea
```

**Why use the launcher?**
- Handles Python path setup automatically (`/home/utils/Python/builds/3.11.9-20250715/bin/python3`)
- Works regardless of `python3` alias availability  
- Sets up proper environment variables
- Better compatibility across different systems
- Passes all arguments through to the Python script

## File Dependencies

### Core Dependencies
- **avice_wa_review.py** - Main script (8,150 lines)
- **avice_image_debug_report.py** - Called by main script for image reports (Line 710)
- **icons/** - Used for HTML report generation (embedded as base64)
- **images/** - Contains logo files for reports
- **workareas.txt** - Tracks test workareas (managed by AI assistant)

### Documentation Files
- **INDEX.md** - Complete script index with all methods and line numbers
- **.cursor/rules/architecture.mdc** - Architecture rules, patterns, and standards (auto-loaded in Cursor)
- **SECTION_HEADERS.md** - Section header formatting and numbering
- **README_avice_wa_review.md** - Main user-facing documentation

### Support Scripts
- **docs_generator.py** - Generates HTML documentation
- **batch_review.py** - Run reviews on multiple workareas
- **summarize_results.py** - Summarize review results
- **cleanup_test_reports.sh** - Clean up old test HTML files

## Key Features

### Analysis Sections (15 stages, indexed 1-14)

**Note**: Sections are numbered in display output (e.g., [1] Setup, [2] Runtime, etc.)

1. `setup` - Design information extraction
2. `runtime` - Comprehensive runtime analysis (moved to #2 for early visibility)
3. `synthesis` - DC synthesis with QoR metrics
4. `pnr` - Place & Route analysis with status tracking
5. `clock` - Clock tree analysis
6. `formal` - Formal verification
7. `parasitic` - Star extraction
8. `timing` - Signoff timing
9. `pv` - Physical verification (LVS/DRC/Antenna)
10. `gl-check` - GL check analysis
11. `eco` - PT-ECO analysis
12. `nv-gate-eco` - NVIDIA Gate ECO
13. `block-release` - Block release information
14. `common` - Common checks across all stages

See **INDEX.md** for complete method listing and line numbers.

### HTML Reports Generated
- PnR Data Report (timestamped)
- Timing Histogram Report (timestamped)
- PrimeTime Timing Summary (timestamped)
- Runtime Report (timestamped)
- Image Debug Report (timestamped)

## Migration Notes

All files have been moved from `/home/avice/scripts/` to `/home/avice/scripts/avice_wa_review/` to keep related functionality organized together. The launcher script `avice_wa_review.csh` in the main scripts directory provides backward compatibility.

## Maintenance

### Regular Maintenance Tasks
- **Cleanup HTML reports**: Run `cleanup_test_reports.sh` to remove old test files
- **Update documentation**: When code changes, update INDEX.md and `.cursor/rules/architecture.mdc`
- **Track workareas**: Add new test workareas to `workareas.txt`
- **Review file count**: Periodically verify line counts in documentation

### File Management
- Icons are embedded as base64 data URIs in HTML reports for portability
- Workareas are tracked in `workareas.txt` for testing purposes
- All paths are relative to the script location for portability
- Test HTML files (avice_*.html) are excluded from git via .gitignore

### Documentation Files Created (October 9, 2025)
During the October 2025 organization effort, the following documentation files were created:
- **INDEX.md** - Complete script index with method catalog
- **SECTION_HEADERS.md** - Documentation of section numbering system
- **ORDERING_CHANGE.md** - Documentation of section reordering (Runtime moved to #2)
- **MERGE_SUMMARY.md** - Unix compatibility guide consolidation
- **CLEANUP_SUMMARY.md** - File cleanup documentation

See **CLEANUP_SUMMARY.md** for details on removed files and cleanup history.
