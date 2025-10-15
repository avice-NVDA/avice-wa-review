# AGUR Release Tracking System

## Overview
This directory contains all files for the AGUR project block release tracking system - a standalone utility for tracking and managing unit releases across all chiplets.

## Directory Structure

```
agur_release_tracking/
├── README.md                      (This file)
├── extract_agur_releases.sh       (Main extraction script)
├── check_and_update_agur_table.sh (Auto-update checker)
├── run_agur_regression.sh         (Regression framework - NEW!)
├── AGUR_UNITS_TABLE.txt           (Pipe-delimited table)
├── AGUR_UNITS_TABLE.csv           (CSV format table)
├── AGUR_UNITS_TABLE.md            (Markdown formatted table)
├── AGUR_RELEASES.md               (Detailed release information)
├── AGUR_REGRESSION_GUIDE.md       (Regression framework guide - NEW!)
├── AGUR_RELEASE_TRACKING.md       (Technical documentation)
├── README_AGUR_TRACKING.md        (User guide)
├── AGUR_QUICK_REFERENCE.txt       (Quick reference card)
└── AUTO_UPDATE_GUIDE.md           (Auto-update documentation)
```

## Quick Start

### View Available Units
```bash
cd /home/avice/scripts/avice_wa_review/agur_release_tracking
cat AGUR_UNITS_TABLE.txt
```

### Update Release Data
```bash
cd /home/avice/scripts/avice_wa_review/agur_release_tracking
./extract_agur_releases.sh
```

### Check for Updates
```bash
cd /home/avice/scripts/avice_wa_review/agur_release_tracking
./check_and_update_agur_table.sh
```

### Use with avice_wa_review.py
```bash
# No need to cd into this directory!
# Just use --unit flag from anywhere
/home/avice/scripts/avice_wa_review_launcher.csh --unit prt
```

### Run Regression Analysis (NEW!)
```bash
cd /home/avice/scripts/avice_wa_review/agur_release_tracking

# Run formal verification regression
./run_agur_regression.sh -t formal

# Run timing regression on CPORT chiplet
./run_agur_regression.sh -t timing -c CPORT

# Run PV regression on specific unit
./run_agur_regression.sh -t pv -u prt
```

## Files Description

### Scripts (Executable)

**`extract_agur_releases.sh`** (11K)
- Extracts release data from `/home/agur_backend_blockRelease/block/`
- Parses release logs for metadata
- Generates all table files (TXT, CSV, MD) and documentation
- Run this to update release data manually

**`check_and_update_agur_table.sh`** (3.4K)
- Auto-checks if table needs updating
- Compares table timestamp vs release timestamps
- Automatically runs extraction if updates detected
- Used by `avice_wa_review.py` for auto-updates

**`run_agur_regression.sh`** (NEW!)
- **Generic regression framework** for multiple analysis types
- Supports: formal, timing, pv, clock, release
- Runs analysis on all released units
- Generates interactive HTML dashboards
- Modular design for easy expansion
- See `AGUR_REGRESSION_GUIDE.md` for full documentation

### Data Files (Auto-Generated)

**`AGUR_UNITS_TABLE.txt`** (891 bytes)
- Pipe-delimited format: `UNIT | CHIPLET | WA_PATH | FLAGS`
- Optimized for shell scripts and grep
- Primary data source for `--unit` flag lookups

**`AGUR_UNITS_TABLE.csv`** (863 bytes)
- CSV format with headers
- Suitable for Excel, Python pandas, data processing
- Includes user and timestamp columns

**`AGUR_UNITS_TABLE.md`** (3.1K)
- Markdown formatted table
- Human-readable with usage examples
- Best for documentation and viewing

**`AGUR_RELEASES.md`** (8.0K)
- Comprehensive release information for all units
- Detailed per-unit sections with timestamps
- Release flags, users, and workareas
- Summary tables

### Documentation Files

**`AGUR_REGRESSION_GUIDE.md`** (NEW!)
- **Comprehensive regression framework guide**
- All supported regression types (formal, timing, pv, clock, release)
- Usage examples and workflows
- CI/CD integration patterns
- Troubleshooting and best practices

**`README_AGUR_TRACKING.md`** (8.6K)
- Complete user guide
- Architecture overview
- Usage examples
- Integration patterns

**`AGUR_RELEASE_TRACKING.md`** (7.8K)
- Technical documentation
- Release area structure
- Data extraction strategies
- Implementation details

**`AUTO_UPDATE_GUIDE.md`** (7.0K)
- Auto-update mechanism explained
- Troubleshooting guide
- Cron job setup instructions
- Performance information

**`AGUR_QUICK_REFERENCE.txt`** (3.6K)
- Quick reference card
- Common commands
- Current unit status
- Batch processing examples

## Current Status

**Tracked Units**: 5/70 (7%)
- prt (ykatzav) - STA, FCL
- pmux (brachas) - STA, FCL, PNR, FE_DCT
- fdb (dkolesnikov) - STA, FCL, PNR, FE_DCT
- fth (miancu) - STA, FCL, FE_DCT
- lnd (shlomoc) - STA, FCL, FE_DCT

**Tracked Chiplets**: 1/5 (20%)
- CPORT (complete)

## Integration

This tracking system integrates with `avice_wa_review.py` via the `--unit` flag:

```bash
# Automatic workarea lookup
/home/avice/scripts/avice_wa_review_launcher.csh --unit prt

# Works with all existing flags
/home/avice/scripts/avice_wa_review_launcher.csh --unit pmux -s runtime pt
```

**How it works:**
1. User runs `avice_wa_review.py --unit <name>`
2. Script checks table in this directory
3. Auto-updates table if new releases detected
4. Looks up workarea path for the unit
5. Runs analysis on that workarea

## Maintenance

### Update Frequency
- **Automatic**: Every time `--unit` flag is used (minimal overhead)
- **Manual**: Run `./extract_agur_releases.sh` anytime
- **Scheduled**: Optional cron job (see AUTO_UPDATE_GUIDE.md)

### Adding New Chiplets
1. Edit `extract_agur_releases.sh`
2. Add new unit names to the `UNITS` variable
3. Run `./extract_agur_releases.sh`
4. Tables automatically updated with new units

### Adding New Units to Existing Chiplets
- No code changes needed!
- Just run `./extract_agur_releases.sh`
- New units with `last_sta_rel` symlinks automatically detected

## Troubleshooting

**Table out of date?**
```bash
./check_and_update_agur_table.sh --force
```

**Unit not found?**
```bash
# Check what's in the table
cat AGUR_UNITS_TABLE.txt | grep -v "^#"

# Check if unit has releases
ls -l /home/agur_backend_blockRelease/block/<unit>/last_sta_rel

# Regenerate table
./extract_agur_releases.sh
```

**Auto-update not working?**
- Check script is executable: `ls -l check_and_update_agur_table.sh`
- Check permissions on release area
- Run manual update to see errors: `./check_and_update_agur_table.sh --force`

## Architecture

**Standalone System**: This is an independent utility, NOT integrated into `avice_wa_review.py`

**Relationship:**
- **Release Tracking** (this directory): Extracts and manages release data
- **avice_wa_review.py** (parent directory): Analyzes workareas
- **Integration**: `--unit` flag provides convenient lookup, but both tools remain independent

## Contact

- **Author**: Alon Vice (avice)
- **Email**: avice@nvidia.com
- **Location**: `/home/avice/scripts/avice_wa_review/agur_release_tracking/`

---

*Last Updated: 2025-10-14*  
*Version: 1.0 - CPORT Chiplet (Phase 1)*

