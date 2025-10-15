# Agur Project Block Release Tracking System

## Overview

This tracking system provides automated extraction and documentation of block releases for the agur project. It monitors the central release area and maintains up-to-date information about all unit releases, their source workareas, and release types.

## Quick Start

### View CPORT Chiplet Releases

```bash
cat /home/avice/scripts/avice_wa_review/AGUR_CPORT_RELEASES.md
```

### Update Release Data

```bash
cd /home/avice/scripts/avice_wa_review
./extract_agur_cport_releases.sh
```

## Files in This System

### 1. Documentation Files

#### `AGUR_RELEASE_TRACKING.md` (7.8K)
- **Purpose**: Technical documentation of the release area structure
- **Contents**:
  - Release directory structure and naming conventions
  - Symbolic link types and their meanings
  - Log file formats and parsing patterns
  - Data extraction strategies
  - Implementation status and next steps

#### `AGUR_CPORT_RELEASES.md` (8.0K)
- **Purpose**: Current release tracking for CPORT chiplet units
- **Contents**:
  - Detailed information for all 5 CPORT units (prt, pmux, fdb, fth, lnd)
  - Latest STA/FCL release timestamps
  - Release users
  - Source workarea paths (validated and accessible)
  - Release flags (Sta, Fcl, Pnr, FE_DCT, DC, Full)
  - Previous release tracking
  - Summary table

#### `README_AGUR_TRACKING.md` (this file)
- **Purpose**: User guide and system overview
- **Contents**: Usage instructions, file descriptions, architecture

### 2. Extraction Script

#### `extract_agur_cport_releases.sh` (7.8K)
- **Purpose**: Automated data extraction from block release logs
- **Features**:
  - Parses `/home/agur_backend_blockRelease/block/{unit}/logs/block_release.log`
  - Follows symbolic links (`last_sta_rel`, `fcl_release`, `prev_last_sta_rel`)
  - Extracts release metadata (user, timestamp, flags, paths)
  - Generates formatted markdown documentation
  - Auto-updates timestamps

## Block Release Area Structure

### Base Directory
```
/home/agur_backend_blockRelease/block/
├── prt/                           # Unit: Port
│   ├── last_sta_rel -> {...}      # Latest STA release (symlink)
│   ├── fcl_release -> {...}       # Latest FCL release (symlink)
│   ├── prev_last_sta_rel -> {...} # Previous STA release (symlink)
│   └── prt_rbv_2025_09_03_...     # Actual release directory
│       ├── logs/
│       │   └── block_release.log  # Release metadata (KEY FILE)
│       ├── spef/                  # SPEF files (if Sta=True)
│       ├── sdc/                   # SDC files (if Sta=True)
│       ├── netlist/               # Netlist files
│       ├── DBs/                   # Database files (if Fcl=True)
│       └── pv_flow/               # PV files
├── pmux/                          # Unit: Port Multiplexer
├── fdb/                           # Unit: Feedback
├── fth/                           # Unit: FTH
└── lnd/                           # Unit: LND
```

## Release Types

| Flag | Command | Description | Files Included |
|------|---------|-------------|----------------|
| **Sta** | `-s` | Static Timing Analysis | SPEF, SDC, netlists |
| **Fcl** | `-l` | Functional/Layout | Database, IOs, OASIS |
| **Pnr** | (TBD) | Place & Route | PnR databases |
| **FE_DCT** | `-fe_dct` | Front End DCT | FE DCT files |
| **DC** | (TBD) | Design Compiler | Synthesis files |
| **Full** | `-f` | Full Release | All files |

## CPORT Chiplet Status

### Current Tracking (Phase 1)

| Unit | Chiplet | User | Latest Release | Release Types | Workarea Status |
|------|---------|------|----------------|---------------|-----------------|
| **prt** | CPORT | ykatzav | 2025/10/08 10:14 | STA, FCL | ✅ Accessible |
| **pmux** | CPORT | brachas | 2025/10/09 17:04 | STA, FCL, PNR, FE_DCT | ✅ Accessible |
| **fdb** | CPORT | dkolesnikov | 2025/10/09 10:51 | STA, FCL, PNR, FE_DCT | ✅ Accessible |
| **fth** | CPORT | miancu | 2025/10/08 15:10 | STA, FCL, FE_DCT | ✅ Accessible |
| **lnd** | CPORT | shlomoc | 2025/10/08 09:00 | STA, FCL, FE_DCT | ✅ Accessible |

**Total Units Tracked**: 5/70 (7%)  
**Total Chiplets Tracked**: 1/5 (20%)

## Usage Examples

### Example 1: View Latest Release for PRT Unit

```bash
grep -A 30 "## Unit: prt" /home/avice/scripts/avice_wa_review/AGUR_CPORT_RELEASES.md
```

### Example 2: Get Source Workarea for PMUX

```bash
grep "pmux" /home/avice/scripts/avice_wa_review/AGUR_CPORT_RELEASES.md | grep "Source Workarea"
```

Output:
```
| **Source Workarea Path** | `/home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |
```

### Example 3: Run avice_wa_review.py on a Released Workarea

```bash
# Get the source workarea for prt
wa_path="/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap"

# Run the workarea review script
/home/avice/scripts/avice_wa_review_launcher.csh $wa_path
```

### Example 4: Update Release Data

```bash
cd /home/avice/scripts/avice_wa_review
./extract_agur_cport_releases.sh
```

This regenerates `AGUR_CPORT_RELEASES.md` with the latest information from the block release logs.

## Relationship with avice_wa_review.py

### ⚠️ STANDALONE UTILITY - NOT INTEGRATED

This release tracking system is a **completely separate utility** from `avice_wa_review.py`.

**They work together but remain independent:**
- **This utility**: Extracts and tracks block release information
- **avice_wa_review.py**: Analyzes individual workareas

### How to Use Them Together

```bash
# Step 1: Get workarea path from release table
wa_path=$(grep "^prt" AGUR_CPORT_UNITS_TABLE.txt | cut -d'|' -f3 | xargs)

# Step 2: Run avice_wa_review on that workarea (separate tool)
/home/avice/scripts/avice_wa_review_launcher.csh "$wa_path"
```

### Batch Processing Example

```bash
# Process all CPORT units
cat AGUR_CPORT_UNITS_TABLE.txt | grep -v "^#" | while IFS='|' read unit chiplet path types; do
    echo "Analyzing unit: $unit"
    /home/avice/scripts/avice_wa_review_launcher.csh "$path"
done
```

## Roadmap

### Phase 1: CPORT Chiplet ✅ COMPLETE
- [x] Analyze release area structure
- [x] Document 5 CPORT units
- [x] Extract source workarea paths
- [x] Validate workarea accessibility
- [x] Create automated extraction script

### Phase 2: Expand to All Chiplets (Planned)
- [ ] Add remaining 4 chiplets
- [ ] Track all 70 units
- [ ] Create chiplet-level summary reports
- [ ] Cross-chiplet comparison tools

### Phase 3: Automation (Planned)
- [ ] Scheduled updates (cron job)
- [ ] Change notifications
- [ ] Release validation checks
- [ ] Batch processing scripts

### Phase 4: Advanced Features (Planned)
- [ ] Web-based dashboard (separate tool)
- [ ] Release history tracking
- [ ] Trend analysis
- [ ] Comparison reports

## Technical Details

### How Symbolic Links Work

The block release system uses three key symbolic links per unit:

1. **`last_sta_rel`** - Points to the most recent STA release
   - Updated when user runs block release with `-s` flag
   - Previous link is moved to `prev_last_sta_rel`

2. **`fcl_release`** - Points to the most recent FCL release
   - Updated when user runs block release with `-l` flag
   - Can point to same directory as `last_sta_rel` (combined release)

3. **`prev_last_sta_rel`** - Points to the previous STA release
   - Maintained for rollback purposes
   - Useful for comparing releases

### Log File Format

The `logs/block_release.log` file contains all metadata:

```
-I- [2025/10/08 10:14:33] USER: ykatzav
-I- [2025/10/08 10:14:33] Release prt from prt_rbv_2025_09_03_...
-I- [2025/10/08 10:14:33]        Sta: True
-I- [2025/10/08 10:14:33]        Fcl: True
-I- [2025/10/08 10:14:33]        Pnr: False
-I- [2025/10/08 10:14:38] db_source /home/scratch.ykatzav_vlsi/agur/prt/...
```

## Troubleshooting

### Issue: Extraction script fails

**Solution**: Check permissions and log file accessibility:
```bash
ls -l /home/agur_backend_blockRelease/block/prt/*/logs/block_release.log
```

### Issue: Workarea path not accessible

**Possible causes**:
- User storage may have been cleaned up
- Path format changed
- Permissions issue

**Solution**: Verify path exists:
```bash
ls -ld /home/scratch.{user}_vlsi/agur/{unit}/{workarea}
```

### Issue: Old release data

**Solution**: Run the extraction script to refresh:
```bash
./extract_agur_cport_releases.sh
```

## Contact and Support

- **Tool Author**: Alon Vice (avice)
- **Email**: avice@nvidia.com
- **Project**: avice_wa_review
- **Documentation**: `/home/avice/scripts/avice_wa_review/`

---

*Last Updated: October 14, 2025*  
*Version: 1.0 (Phase 1 - CPORT Chiplet)*  
*Part of: avice_wa_review project*

