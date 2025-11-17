# Changelog

All notable changes to the Avice Workarea Review project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-15

### Added
- **Master Dashboard**: Comprehensive unified dashboard with 13 integrated sections
  - Expandable/collapsable section cards with statistics
  - Quick navigation and overview of entire workarea
  - Links to individual detailed HTML reports
  - Single-page view of all analysis sections
  
- **AGUR Release Tracking System**:
  - Automated AGUR release extraction script
  - Formal regression testing dashboard
  - Support for 57 design units across multiple projects
  - Auto-update scripts for release tracking
  - Multiple export formats (CSV, Markdown, TXT)
  - Comprehensive documentation and quick reference guides

- **HTML Report Enhancements**:
  - Copyright footer on all HTML reports
  - Back-to-top button for long reports
  - Absolute path support for true portability
  - Username-aware HTML filenames using $USER environment variable
  - Better cross-directory compatibility

- **Runtime Analysis Improvements**:
  - Color-coded runtime values (green/yellow/red thresholds)
  - Stage highlighting for maximum runtime identification
  - Improved timestamp handling and calculation
  - Better detection of RUNNING flows

- **Documentation Updates**:
  - Runtime color coding guide (RUNTIME_COLOR_CODING.md)
  - Quick test guide for Master Dashboard
  - Comprehensive testing plans and results
  - Master Dashboard demo and progress tracking

### Changed
- Updated `.cursor/rules/architecture.mdc` with latest standards and patterns (auto-loaded in Cursor)
- Enhanced `avice_image_debug_report.py` with improved error handling
- Improved HTML generation with better styling and responsiveness
- Better workarea validation and error messages

### Fixed
- Fixed HTML portability issues with relative paths
- Fixed GL-check HTML link generation
- Fixed expandable card functionality in Master Dashboard
- Fixed duplicate DC card display
- Fixed missing PnR/GL-check cards

### Statistics
- 27 files changed
- 21,880 insertions
- 5,082 deletions
- Net change: +16,798 lines

## [1.0.0] - 2025-09-30

### Added
- **Enhanced PnR Analysis**:
  - PnR status tracking with flow progress monitoring
  - Updated key parameters (i1_clk, i2_clk, EffectiveUtilization, ArraysCount)
  - HVT/SVT percentages tracking
  - Comprehensive HTML reports with interactive tables

- **Improved Runtime Analysis**:
  - Core PnR runtime calculation (BEGIN to postroute only)
  - Hours-first display format with days in parentheses
  - Detailed PnR stage breakdown with highlighting
  - Clickable PRC status links in HTML reports

- **Enhanced Synthesis Analysis**:
  - QoR (Quality of Results) report integration
  - BeFlow configuration analysis
  - Scenario summary tables with hold timing detection
  - Timing path groups extraction

- **HTML Report Generation**:
  - Timestamped filenames for all reports
  - Workarea path in headers
  - Modal logo display functionality
  - Responsive design and improved styling

- **Selective Analysis**:
  - Added `--sections` option to run specific analysis sections
  - 14 available analysis sections
  - Renamed "physical" to "pv" for Physical Verification

### Changed
- Improved code organization with object-oriented design
- Better error handling and validation
- Enhanced documentation with comprehensive docstrings
- Streamlined codebase structure

### Removed
- Unused files: lvs_analyzer.py, log_viewer_gui.py, ascii_utils.py, MtbuPyUtils.py
- Cleaned up legacy code and deprecated functions

### Initial Features
- Complete ASIC/SoC design workarea analysis
- Multi-IPO support with automatic detection
- Comprehensive flow coverage: Setup, Runtime, Synthesis, PnR, Clock, Formal, Star, PT, PV, GL-Check, ECO
- Professional HTML reports with Alon Vice branding
- Cross-directory execution support
- Unix shell compatibility with ASCII-only output
- Efficient parsing of large log files
- Timing analysis with dual-scenario extraction
- ECO analysis with dont_use cell validation
- Physical verification flow analysis

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 2.0.0 | 2025-10-15 | Master Dashboard & AGUR Tracking |
| 1.0.0 | 2025-09-30 | Initial Python Release |

---

## Upgrade Notes

### From 1.0.0 to 2.0.0

1. **Master Dashboard**: Use `--master-dashboard` flag to generate unified dashboard
2. **AGUR Tracking**: New `--unit` flag allows workarea lookup by unit name
3. **HTML Reports**: All generated HTML files now use absolute paths for better portability
4. **Version Check**: Run with `--version` to verify you're running 2.0.0

### Breaking Changes
- None - Fully backward compatible with 1.0.0

---

Copyright (c) 2025 Alon Vice (avice)  
Contact: avice@nvidia.com

