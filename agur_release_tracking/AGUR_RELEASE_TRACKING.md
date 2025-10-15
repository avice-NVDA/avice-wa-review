# Agur Project Block Release Tracking System

## Overview
This document describes the structure and tracking system for agur project block releases.

## Release Area Structure

### Base Directory
```
/home/agur_backend_blockRelease/block/
```

### CPORT Chiplet Units (Phase 1)
- **prt** - Port
- **pmux** - Port Multiplexer  
- **fdb** - Feedback
- **fth** - ?
- **lnd** - ?

## Unit Directory Structure

Each unit directory contains:

### 1. Timestamped Release Directories
Format: `{unit}_rbv_YYYY_MM_DD_{workarea_suffix}__YYYY_M_D_H_M_S`

Example:
```
prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_10_14_33
```

Structure breakdown:
- `prt` - Unit name
- `rbv_2025_09_03` - RBV date
- `agur_condb_int3_2025_08_27_0_1NL_snap` - Workarea suffix/identifier
- `__2025_10_8_10_14_33` - Release timestamp (YYYY_M_D_H_M_S)

### 2. Symbolic Links (Release Pointers)

Common symbolic link names:
- `fcl_release` → Latest FCL (Functional) release
- `fe_dct_golden_release` → Latest FE DCT golden release
- `last_sta_rel` → Latest STA (Static Timing Analysis) release
- `FC_ww41_last_sta_rel` → Work week specific STA release
- `AUG07_cport_eco_01` → ECO release milestone
- `AUG_07_FP` → Floor plan release milestone
- `full_release` → Full release

These links point to actual timestamped release directories.

## Release Directory Internal Structure

Each release directory contains:

### Standard Directories
- `COMMON/` - Common files
- `DBs/` - Database files (.enc, .enc.dat)
- `IOs/` - I/O related files
- `def/` - DEF files
- `flp/` - Floorplan files
- `lef/` - LEF files
- `lib/` - Library files
- `logs/` - **Release logs (CRITICAL)**
- `mcmm/` - Multi-corner multi-mode files
- `netlist/` - Netlists
- `pv_flow/` - Physical verification flow files
- `reports/` - Reports
- `sdc/` - SDC constraint files
- `spef/` - SPEF parasitic files
- `spef_info/` - SPEF information
- `unit_scripts/` - Unit-specific scripts

### Critical Log File

**File**: `logs/block_release.log`

This file contains all release metadata including:

#### 1. Source Workarea Path
Extract from file copy paths (e.g., db_source line):
```
-I- [2025/10/08 10:14:38] db_source            /home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap/export/export_innovus/prt_ipo1000.enc
```

Workarea path: `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap`

#### 2. Release Metadata Section
```
-I- [2025/10/08 10:14:33] USER: ykatzav
-I- [2025/10/08 10:14:33] Release prt from prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap
-I- [2025/10/08 10:14:33] Release to: /home/agur_backend_blockRelease/block/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_10_14_33
-I- [2025/10/08 10:14:33]  Copy only: False
-I- [2025/10/08 10:14:33]      Force: False
-I- [2025/10/08 10:14:33]       Text: _2025_10_8_10_14_33
-I- [2025/10/08 10:14:33]       Full: False
-I- [2025/10/08 10:14:33]        Pnr: False
-I- [2025/10/08 10:14:33]        Sta: True
-I- [2025/10/08 10:14:33]        Fcl: True
-I- [2025/10/08 10:14:33]         DC: False
-I- [2025/10/08 10:14:33]     FE_DCT: False
-I- [2025/10/08 10:14:33]  Build ndm: None
-I- [2025/10/08 10:14:33]   No Clean: False
-I- [2025/10/08 10:14:33]     Beview: True
-I- [2025/10/08 10:14:33]         HS: False
```

## Release Flag Types

### Flag Definitions

| Flag | Command Line | Description | What Gets Released |
|------|--------------|-------------|-------------------|
| **Sta** | `-s` | Static Timing Analysis | SPEF files, SDC files, netlists |
| **Fcl** | `-l` | Functional | Layout database, IOs, OASIS files |
| **Pnr** | ? | Place and Route | PnR database files |
| **DC** | ? | Design Compiler | DC synthesis files |
| **FE_DCT** | `-fe_dct` | Front End DCT | FE DCT specific files |
| **Full** | `-f` | Full Release | All files |

### Release Type Patterns Observed

#### PRT (Latest: 2025/10/08 10:14)
- Sta: True
- Fcl: True
- Pnr: False
- DC: False
- FE_DCT: False

#### PMUX (Latest: 2025/10/09 17:04)
- Sta: True
- Fcl: True
- Pnr: True
- DC: False
- FE_DCT: True

#### FDB (Latest: 2025/10/09 10:51)
- Sta: True
- Fcl: True
- Pnr: True
- DC: False
- FE_DCT: True

#### FTH (Latest: 2025/10/08 15:10)
- Sta: True
- Fcl: True
- Pnr: False
- DC: False
- FE_DCT: True

#### LND (Latest: 2025/10/08 09:00)
- Sta: True
- Fcl: True
- Pnr: False
- DC: False
- FE_DCT: True

## Data Extraction Strategy

### Step 1: List All Releases for a Unit
```bash
ls -lt /home/agur_backend_blockRelease/block/{unit}/ | grep -E "^d"
```

### Step 2: Identify Latest Release by Type
Check symbolic links:
```bash
ls -l /home/agur_backend_blockRelease/block/{unit}/ | grep "^l"
```

### Step 3: Extract Release Information
Read the log file:
```bash
cat /home/agur_backend_blockRelease/block/{unit}/{release_dir}/logs/block_release.log
```

### Step 4: Parse Key Information

#### Extract Release Flags
```bash
grep -E "^\-I\-.*( Sta:| Fcl:| Pnr:| DC:| FE_DCT:)" {log_file}
```

#### Extract Source Workarea
```bash
grep "db_source.*scratch" {log_file} | sed 's|/export/export_innovus/.*||'
```

#### Extract Release User
```bash
grep "^\-I\-.*USER:" {log_file}
```

## Target Data Structure

For each CPORT unit, collect:

```
{
    "unit": "prt",
    "chiplet": "CPORT",
    "latest_release": {
        "release_dir": "prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_10_14_33",
        "release_timestamp": "2025-10-08 10:14:33",
        "source_workarea": "/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap",
        "release_user": "ykatzav",
        "release_flags": {
            "Sta": true,
            "Fcl": true,
            "Pnr": false,
            "DC": false,
            "FE_DCT": false,
            "Full": false
        }
    }
}
```

## Implementation Status

### ✅ Phase 1 Complete: CPORT Chiplet (5 units)

**Status**: All CPORT units have been documented with their latest STA releases.

**Documentation**: 
- 📄 `AGUR_CPORT_RELEASES.md` - Comprehensive release tracking for all CPORT units
- 🔧 `extract_agur_cport_releases.sh` - Automated extraction script

**Key Findings**:
1. **Latest STA Release** is identified via `last_sta_rel` symbolic link
2. **Previous STA Release** is tracked via `prev_last_sta_rel` symbolic link
3. **FCL Release** is tracked via `fcl_release` symbolic link
4. All CPORT units currently have **combined STA+FCL releases** (both links point to same directory)
5. Source workarea paths are successfully extracted from `logs/block_release.log`

**CPORT Units Summary**:

| Unit | User | Latest Release | Flags |
|------|------|----------------|-------|
| **prt** | ykatzav | 2025/10/08 10:14 | STA, FCL |
| **pmux** | brachas | 2025/10/09 17:04 | STA, FCL, PNR, FE_DCT |
| **fdb** | dkolesnikov | 2025/10/09 10:51 | STA, FCL, PNR, FE_DCT |
| **fth** | miancu | 2025/10/08 15:10 | STA, FCL, FE_DCT |
| **lnd** | shlomoc | 2025/10/08 09:00 | STA, FCL, FE_DCT |

### 📋 Next Steps

1. **Validate Workarea Paths** - Verify that extracted source workarea paths exist and are accessible
2. **Test avice_wa_review.py** - Run the workarea review script on the extracted source paths
3. **Expand to Other Chiplets** - Add remaining 4 chiplets (65 more units)
4. **Automate Updates** - Create cron job or update script to refresh release data periodically
5. **Integration** - Consider integrating release tracking into `avice_wa_review.py` as a new feature

### 🔄 Updating Release Data

To refresh the CPORT release documentation:

```bash
cd /home/avice/scripts/avice_wa_review
./extract_agur_cport_releases.sh
```

This will regenerate `AGUR_CPORT_RELEASES.md` with the latest release information from the block release area.

---

*Document created: October 14, 2025*  
*Last updated: October 14, 2025*  
*Project: avice_wa_review - Agur Release Tracking Extension*

