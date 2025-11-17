#!/home/utils/Python/builds/3.11.9-20250715/bin/python3
"""
Colorized help display for AGUR Multi-Regression Analysis Tool
"""

import sys
import os

def supports_color():
    """
    Fast check if terminal supports colors (no runtime impact)
    Returns True if colors are supported, False otherwise
    """
    # Check if stdout is a TTY and TERM indicates color support
    if not sys.stdout.isatty():
        return False
    
    term = os.environ.get('TERM', '')
    # Most color-capable terminals have 'color' in TERM or are xterm variants
    return 'color' in term or 'xterm' in term or 'screen' in term or term == 'linux'

# ANSI color codes - will be empty strings if colors not supported
class Color:
    def __init__(self, use_color=True):
        if use_color:
            self.RED = '\033[31m'
            self.GREEN = '\033[32m'
            self.YELLOW = '\033[33m'
            self.BLUE = '\033[34m'
            self.CYAN = '\033[36m'
            self.BOLD = '\033[1m'
            self.DIM = '\033[2m'
            self.RESET = '\033[0m'
        else:
            # No colors - all empty strings
            self.RED = ''
            self.GREEN = ''
            self.YELLOW = ''
            self.BLUE = ''
            self.CYAN = ''
            self.BOLD = ''
            self.DIM = ''
            self.RESET = ''

def print_help(script_name):
    """Print colorized help text"""
    
    # Detect color support (fast, no runtime impact)
    c = Color(supports_color())
    
    help_text = f"""
{c.BOLD}{c.CYAN}===============================================================================
                    AGUR Multi-Regression Analysis Tool
==============================================================================={c.RESET}

{c.BOLD}{c.YELLOW}Usage:{c.RESET} {c.BOLD}{c.GREEN}{script_name}{c.RESET} [{c.BOLD}{c.GREEN}-t{c.RESET} TYPE[,TYPE2,...]] [options]

{c.BOLD}Run various analysis regressions on all released AGUR units.{c.RESET}
{c.YELLOW}If no -t option is specified, runs ALL regression types (formal, timing, pv, clock, release, glcheck).{c.RESET}

{c.BOLD}{c.CYAN}-------------------------------------------------------------------------------
OPTIONS
-------------------------------------------------------------------------------{c.RESET}
  {c.BOLD}{c.GREEN}-t, --type{c.RESET} TYPE          Regression type (optional - defaults to ALL types)
                           Options: {c.YELLOW}formal, timing, pv, clock, release, glcheck{c.RESET}
                           Multiple types: comma-separated or multiple -t flags
                           If omitted: runs all 6 regression types

{c.BOLD}{c.CYAN}FILTERS:{c.RESET}
  {c.BOLD}{c.GREEN}-c, --chiplet{c.RESET} CHIPLET    Filter by chiplet - case-insensitive (e.g., CPORT, cport)
                           Multiple chiplets: comma-separated or multiple -c flags
  {c.BOLD}{c.GREEN}-u, --unit{c.RESET} UNIT          Run for specific unit only

{c.BOLD}{c.CYAN}EXECUTION CONTROL:{c.RESET}
  {c.BOLD}{c.GREEN}-j, --jobs{c.RESET} N             Run N analyses in parallel ({c.YELLOW}default: auto{c.RESET})
                           {c.YELLOW}auto{c.RESET} = smart detection (capped at 16 for optimal performance)
                           Use explicit number (e.g., {c.YELLOW}-j 8{c.RESET}) to override auto-detection
  {c.BOLD}{c.GREEN}--dry-run{c.RESET}                Preview what will be executed without running
  {c.BOLD}{c.GREEN}-v, --verbose{c.RESET}            Enable verbose/debug output
  {c.BOLD}{c.GREEN}-q, --quiet{c.RESET}              Quiet mode - only show progress bar ({c.YELLOW}default{c.RESET})
  {c.BOLD}{c.GREEN}-nq, --no-quiet{c.RESET}          Disable quiet mode - show all analysis output
  {c.BOLD}{c.GREEN}--no-update{c.RESET}              Skip automatic refresh of AGUR units table
  {c.BOLD}{c.GREEN}--resume{c.RESET} FILE            Resume from a previous interrupted run
  {c.BOLD}{c.GREEN}--config{c.RESET} FILE            Load configuration from file

{c.BOLD}{c.CYAN}OTHER:{c.RESET}
  {c.BOLD}{c.GREEN}-h, --help{c.RESET}               Show this help message

{c.BOLD}{c.CYAN}-------------------------------------------------------------------------------
EXAMPLES
-------------------------------------------------------------------------------{c.RESET}
{c.YELLOW}  # Basic Usage{c.RESET}
  {c.GREEN}{script_name}{c.RESET}                               {c.DIM}# Run ALL 5 regression types (auto jobs, quiet mode){c.RESET}
  {c.GREEN}{script_name} -j 8{c.RESET}                          {c.DIM}# Run with explicit 8 parallel jobs{c.RESET}
  {c.GREEN}{script_name} -nq{c.RESET}                           {c.DIM}# Show detailed analysis output (not just progress){c.RESET}
  {c.GREEN}{script_name} --dry-run{c.RESET}                     {c.DIM}# Preview what will be executed{c.RESET}
  {c.GREEN}{script_name} -v{c.RESET}                            {c.DIM}# Run with verbose/debug output{c.RESET}

{c.YELLOW}  # Filtering{c.RESET}
  {c.GREEN}{script_name} -c CPORT{c.RESET}                      {c.DIM}# Run ALL types on CPORT chiplet only{c.RESET}
  {c.GREEN}{script_name} -u fdb{c.RESET}                        {c.DIM}# Run ALL types on fdb unit only{c.RESET}

{c.YELLOW}  # Single Regression Type{c.RESET}
  {c.GREEN}{script_name} -t formal{c.RESET}                     {c.DIM}# Run formal regression on all units (auto, quiet){c.RESET}
  {c.GREEN}{script_name} -t formal -j 4{c.RESET}                {c.DIM}# Run formal with 4 parallel jobs{c.RESET}
  {c.GREEN}{script_name} -t formal --no-update{c.RESET}         {c.DIM}# Run formal without refreshing units table{c.RESET}

{c.YELLOW}  # Multiple Regression Types{c.RESET}
  {c.GREEN}{script_name} -t formal,pv{c.RESET}                  {c.DIM}# Run formal AND PV regressions (multi-tab HTML){c.RESET}
  {c.GREEN}{script_name} -t formal -t pv{c.RESET}               {c.DIM}# Same as above (multiple -t flags){c.RESET}
  {c.GREEN}{script_name} -t pv,formal,timing{c.RESET}           {c.DIM}# Run 3 regressions in one dashboard{c.RESET}

{c.YELLOW}  # Combined Filters{c.RESET}
  {c.GREEN}{script_name} -t formal -c CPORT{c.RESET}            {c.DIM}# Run formal on CPORT chiplet only{c.RESET}
  {c.GREEN}{script_name} -t formal -c CPORT,HPORT{c.RESET}      {c.DIM}# Run formal on CPORT and HPORT chiplets{c.RESET}
  {c.GREEN}{script_name} -t formal -c CPORT -c HPORT{c.RESET}   {c.DIM}# Same as above (multiple -c flags){c.RESET}
  {c.GREEN}{script_name} -t timing -u prt{c.RESET}              {c.DIM}# Run timing regression on prt unit only{c.RESET}

{c.YELLOW}  # Resume{c.RESET}
  {c.GREEN}{script_name} --resume .agur_regression_state.txt{c.RESET}  {c.DIM}# Resume from previous run{c.RESET}

{c.BOLD}{c.CYAN}-------------------------------------------------------------------------------
REGRESSION TYPES
-------------------------------------------------------------------------------{c.RESET}
  {c.BOLD}{c.YELLOW}formal{c.RESET}    - Formal verification status (RTL vs PNR/Synthesis)
  {c.BOLD}{c.YELLOW}timing{c.RESET}    - PT signoff timing analysis (WNS, TNS, paths)
  {c.BOLD}{c.YELLOW}pv{c.RESET}        - Physical verification (DRC, LVS, Antenna)
  {c.BOLD}{c.YELLOW}clock{c.RESET}     - Clock tree analysis (latency, skew)
  {c.BOLD}{c.YELLOW}release{c.RESET}   - Block release status and completeness
  {c.BOLD}{c.YELLOW}glcheck{c.RESET}   - GL Check error analysis (waived vs non-waived)

{c.BOLD}{c.CYAN}-------------------------------------------------------------------------------
OUTPUT FILES (generated in current directory)
-------------------------------------------------------------------------------{c.RESET}
  {c.YELLOW}Single type:{c.RESET}    agur_<type>_regression_dashboard_YYYYMMDD_HHMMSS.html
  {c.YELLOW}Multiple types:{c.RESET} agur_multi_regression_dashboard_YYYYMMDD_HHMMSS.html
  {c.YELLOW}State file:{c.RESET}     .agur_regression_state_YYYYMMDD_HHMMSS.txt (for resume)

{c.BOLD}{c.CYAN}-------------------------------------------------------------------------------
PERFORMANCE TIPS
-------------------------------------------------------------------------------{c.RESET}
  {c.GREEN}->{c.RESET} Smart auto-detection is now {c.YELLOW}default{c.RESET} (caps at 16 jobs for optimal performance)
  {c.GREEN}->{c.RESET} Use {c.YELLOW}-j N{c.RESET} (e.g., -j 8) to override auto-detection if needed
  {c.GREEN}->{c.RESET} Quiet mode is {c.YELLOW}default{c.RESET} - use {c.YELLOW}-nq{c.RESET} for detailed output
  {c.GREEN}->{c.RESET} Use {c.YELLOW}--dry-run{c.RESET} first to preview the execution plan
  {c.GREEN}->{c.RESET} Use {c.YELLOW}--no-update{c.RESET} to skip table refresh if you know data is current

{c.BOLD}{c.CYAN}-------------------------------------------------------------------------------
AUTO-UPDATE BEHAVIOR
-------------------------------------------------------------------------------{c.RESET}
  By default, the script automatically refreshes the AGUR units table before
  each run to ensure latest release data. Use {c.YELLOW}--no-update{c.RESET} to skip this if
  you know the table is current (saves a few seconds).

{c.BOLD}{c.CYAN}==============================================================================={c.RESET}
"""
    print(help_text)

if __name__ == "__main__":
    # Get the script name from command line or default
    script_name = sys.argv[1] if len(sys.argv) > 1 else "./run_agur_regression.sh"
    print_help(script_name)

