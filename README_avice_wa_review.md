# Avice Workarea Review Tool

A comprehensive Python tool for reviewing ASIC/SoC design workareas, converted from the original C-shell script with improved organization and structure.

## Overview

This tool provides a complete review of semiconductor design workareas, generating comprehensive reports covering all major aspects of the design flow from synthesis to signoff. The Python version offers better maintainability, error handling, and modular organization compared to the original C-shell script.

## Features

- **Modular Design**: Organized by design flow stages for better maintainability
- **Comprehensive Coverage**: Covers entire ASIC design flow from RTL to GDSII
- **Error Handling**: Robust error handling and file existence checks
- **Colorized Output**: Color-coded terminal output for better readability
- **Flexible Input**: Command-line arguments with optional IPO specification
- **Detailed Reporting**: Both summary and detailed information for each stage
- **Logo Display**: ASCII art logo with optional image viewer integration
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Design Flow Stages

The tool is organized into the following flow stages:

1. **Setup** - Design information extraction and configuration
2. **Synthesis (DC)** - Design Compiler synthesis analysis with QoR metrics
3. **Recipe** - Recipe analysis and configuration
4. **Place & Route (PnR)** - Place and route analysis with status tracking
5. **Clock Analysis** - Clock tree analysis (Innovus and PrimeTime)
6. **Formal Verification** - Formal verification results
7. **Parasitic Extraction (Star)** - Star extraction analysis
8. **Signoff Timing (PT)** - PrimeTime timing signoff
9. **Physical Verification (PV)** - LVS, DRC, and antenna checks
10. **GL Check** - GL check analysis
11. **ECO Analysis** - Engineering Change Order analysis (PT-ECO)
12. **NV Gate ECO** - NVIDIA Gate ECO analysis
13. **Runtime** - Comprehensive runtime analysis and timing summaries
14. **Block Release** - Block release status and logs

## Usage

### Basic Usage (Recommended)
```bash
# Use the C-shell launcher (recommended)
/home/avice/scripts/avice_wa_review_launcher.csh <workarea_path>

# Or run directly with Python
/home/utils/Python/builds/3.11.9-20250715/bin/python3 /home/avice/scripts/avice_wa_review/avice_wa_review.py <workarea_path>
```

**Note**: The C-shell launcher (`avice_wa_review_launcher.csh`) is recommended because it:
- Handles Python path setup automatically
- Works regardless of `python3` alias availability
- Sets up proper environment variables
- Provides better compatibility across different systems
- Works from any directory using absolute paths

### With IPO Specification
```bash
# Using launcher
/home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> <ipo_name>

# Or directly with Python
/home/utils/Python/builds/3.11.9-20250715/bin/python3 /home/avice/scripts/avice_wa_review/avice_wa_review.py <workarea_path> <ipo_name>
```

### Selective Section Analysis
```bash
# Using launcher (recommended)
/home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> --sections setup runtime synthesis

# Or directly with Python
/home/utils/Python/builds/3.11.9-20250715/bin/python3 /home/avice/scripts/avice_wa_review/avice_wa_review.py <workarea_path> --sections setup runtime synthesis

# Available sections: setup, runtime, synthesis (syn/dc), pnr, clock, formal, 
# star, pt, pv, gl-check, eco, nv-gate-eco, block-release
# Aliases: syn/dc = synthesis, star = parasitic extraction, pt = signoff timing

# Use aliases for shorter commands
/home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> -s setup dc pnr
```

### Verbose Output
```bash
# Using launcher
/home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> --verbose

# Or directly with Python
/home/utils/Python/builds/3.11.9-20250715/bin/python3 /home/avice/scripts/avice_wa_review/avice_wa_review.py <workarea_path> --verbose
```

### Logo Options
```bash
# Show logo only
/home/utils/Python/builds/3.11.9-20250715/bin/python3 /home/avice/scripts/avice_wa_review/avice_wa_review.py --show-logo

# Disable logo display
/home/avice/scripts/avice_wa_review_launcher.csh <workarea_path> --no-logo
```

### Help
```bash
# Using launcher
/home/avice/scripts/avice_wa_review_launcher.csh --help

# Or directly with Python
/home/utils/Python/builds/3.11.9-20250715/bin/python3 /home/avice/scripts/avice_wa_review/avice_wa_review.py --help
```

## Examples

```bash
# Basic review (recommended)
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea

# Review specific IPO
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea ipo1

# Run specific sections
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea --sections pnr runtime

# Run PV and ECO analysis
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea --sections pv eco nv-gate-eco

# Verbose output
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea --verbose

# Direct Python usage (if launcher not available)
/home/utils/Python/builds/3.11.9-20250715/bin/python3 /home/avice/scripts/avice_wa_review/avice_wa_review.py /path/to/workarea
```

## Logo Display

The tool includes a professional ASCII art logo that displays at the start of each review. The logo can be controlled with command-line options:

- **`--show-logo`**: Display only the logo and exit
- **`--no-logo`**: Disable logo display during review
- **Default**: Logo displays automatically during review

The tool displays only the ASCII art logo. Image popup functionality has been disabled for better terminal compatibility.

## HTML Reports

The tool generates comprehensive HTML reports for detailed analysis:

### PnR Data Report
- **Filename**: `{USER}_pnr_data_{top_hier}_{ipo}_{timestamp}.html`
- **Content**: Complete PnR analysis with key parameters, timing histograms, and status
- **Features**: Interactive tables, clickable links to log files, workarea path in header

### Timing Histogram Report
- **Filename**: `{USER}_timing_histogram_{top_hier}_{timestamp}.html`
- **Content**: Detailed timing analysis with histogram tables
- **Features**: Categorized timing data, scenario breakdowns, workarea context

### PrimeTime Timing Summary
- **Filename**: `{USER}_PT_timing_summary_{top_hier}_{timestamp}.html`
- **Content**: PrimeTime-based timing analysis and summaries
- **Features**: PT-specific timing metrics and analysis

### Runtime Report
- **Filename**: `{USER}_runtime_report_{top_hier}_{timestamp}.html`
- **Content**: Comprehensive runtime analysis across all flow stages
- **Features**: Runtime tables, PnR stage breakdown, clickable PRC status links

### Image Debug Report
- **Filename**: `{USER}_image_debug_report_{top_hier}_{ipo}_{timestamp}.html`
- **Content**: Image analysis and visualization
- **Features**: Image galleries, analysis results

All HTML reports include:
- **Workarea path** in headers for context
- **Timestamped filenames** for uniqueness
- **Clickable logo** with modal display
- **Responsive design** for various screen sizes

## Architecture

### Classes

- **`WorkareaReviewer`**: Main class that orchestrates the review process
- **`FileUtils`**: Utility class for file operations and pattern matching
- **`LogoDisplay`**: Handles logo display functionality
- **`DesignInfo`**: Data class for storing design information
- **`FlowStage`**: Enum for different design flow stages
- **`Color`**: ANSI color codes for terminal output

### Key Methods

- `run_complete_review()`: Main method that runs all analysis stages
- `run_<stage>_analysis()`: Individual stage analysis methods
- `_extract_design_info()`: Extracts design information from workarea
- `print_header()`: Prints formatted section headers
- `print_file_info()`: Prints file information with existence checks

## File Structure

The tool expects a standard workarea structure with the following key directories:

```
workarea/
├── unit_scripts/des_def.tcl          # Design definition
├── rbv/README                        # Tag information
├── syn_flow/dc/                      # Synthesis flow
├── pnr_flow/nv_flow/                 # Place & route flow
├── signoff_flow/auto_pt/             # PrimeTime signoff
├── formal_flow/                      # Formal verification
├── pv_flow/                          # Physical verification
├── export/                           # Export files
└── umake_log/                        # Build logs
```

## Dependencies

- Python 3.6+
- Standard library modules only (no external dependencies)

## Error Handling

The tool includes comprehensive error handling:

- File existence checks before processing
- Graceful handling of missing files/directories
- Exception handling for subprocess operations
- User-friendly error messages with color coding

## Output Format

The tool provides colorized output with:

- **Green**: Section headers and success messages
- **Red**: Errors and warnings
- **Yellow**: Warnings and interruptions
- **Cyan**: Information and file paths
- **Bold**: Important information

## Recent Updates and Improvements

### Version 2.0.0 Features (October 2025)

1. **Master Dashboard**:
   - Unified dashboard with 13 integrated sections
   - Single HTML report combining all workarea analysis
   - Expandable/collapsible section cards with statistics
   - Quick navigation and comprehensive overview
   - Linked to individual detailed HTML reports

2. **AGUR Release Tracking System**:
   - Automated AGUR release extraction and tracking
   - Formal regression testing dashboard
   - Support for 57 design units
   - Auto-update scripts and documentation
   - CSV/Markdown/TXT format exports

3. **Enhanced HTML Reports**:
   - Copyright footer on all reports
   - Back-to-top button for long reports
   - Absolute path support for portability
   - Improved styling and responsiveness
   - Better cross-directory compatibility

4. **Runtime Enhancements**:
   - Color-coded runtime analysis
   - Stage highlighting for max runtime
   - Improved timestamp handling
   - Better RUNNING flow detection

5. **Architecture Updates**:
   - Comprehensive architecture.mdc documentation
   - HTML/CSS rendering compatibility updates
   - Cross-directory execution standards
   - Testing and validation guidelines

6. **Image Debug Improvements**:
   - Enhanced reporting capabilities
   - Better error handling
   - Improved image analysis

**Statistics**: 27 files changed, 21,880 insertions, 5,082 deletions

### Version 1.0.0 Features (Initial Release)

1. **Enhanced PnR Analysis**:
   - PnR status tracking with flow progress monitoring
   - Updated key parameters (i1_clk, i2_clk, EffectiveUtilization, ArraysCount, HVT/SVT percentages)
   - Comprehensive HTML reports with interactive tables

2. **Improved Runtime Analysis**:
   - Core PnR runtime calculation (BEGIN to postroute only)
   - Hours-first display format with days in parentheses
   - Detailed PnR stage breakdown with highlighting
   - Clickable PRC status links in HTML reports

3. **Enhanced Synthesis Analysis**:
   - QoR (Quality of Results) report integration
   - BeFlow configuration analysis
   - Scenario summary tables with hold timing detection
   - Timing path groups extraction

4. **Updated Section Names**:
   - Changed "physical" to "pv" for Physical Verification
   - Added selective section analysis with `--sections` option
   - 14 available analysis sections

5. **HTML Report Generation**:
   - Timestamped filenames for all reports
   - Workarea path in headers
   - Modal logo display functionality
   - Responsive design and improved styling

6. **Code Cleanup**:
   - Removed unused files (lvs_analyzer.py, log_viewer_gui.py, ascii_utils.py, MtbuPyUtils.py)
   - Streamlined codebase with only actively used components
   - Improved error handling and validation

## Migration from C-shell Script

### Key Improvements

1. **Better Organization**: Code organized by flow stages
2. **Error Handling**: Robust error handling and validation
3. **Maintainability**: Object-oriented design with clear separation of concerns
4. **Extensibility**: Easy to add new analysis stages
5. **Documentation**: Comprehensive docstrings and comments
6. **Type Hints**: Better code clarity and IDE support
7. **HTML Reports**: Rich interactive reports for detailed analysis
8. **Selective Analysis**: Run only specific sections as needed

### Compatibility

The Python version maintains full compatibility with the original C-shell script's functionality while providing additional features and improvements.

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure the script has execute permissions
   ```bash
   chmod +x /home/avice/scripts/avice_wa_review/avice_wa_review.py
   ```

2. **File Not Found**: Verify the workarea path is correct and contains the expected directory structure

3. **Python Version**: Ensure Python 3.6+ is installed
   ```bash
   /home/utils/Python/builds/3.11.9-20250715/bin/python3 --version
   ```

## Contributing

When adding new analysis stages:

1. Add the stage to the `FlowStage` enum
2. Create a `run_<stage>_analysis()` method
3. Add the method call to `run_complete_review()`
4. Update this documentation

## License

This tool is part of the Avice design flow tools.
