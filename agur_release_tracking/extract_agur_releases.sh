#!/bin/bash
# Extract complete block release data for agur project units
# Supports all chiplets - tracking ALL 67 units across 7 chiplets

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
output_file="$SCRIPT_DIR/AGUR_RELEASES.md"
current_date=$(date '+%Y-%m-%d %H:%M:%S')

# Define all units by chiplet
declare -A CHIPLET_UNITS
CHIPLET_UNITS[HIOPL]="ioptca ioptcb ioptcc ioptcd"
CHIPLET_UNITS[CPORT]="fdb fth lnd pmux prt"
CHIPLET_UNITS[HPORT]="ccorea ccoreb ccorec ccored ccoree ccoref"
CHIPLET_UNITS[NDQ]="clt cscore dcmp fdbm fdbs fthm ftos fwam fwas glc iopl ioplm iopx lndm nvrisc pmuxm prtm psca pscb pscc pscd px riba ribs sma yu"
CHIPLET_UNITS[QNS]="dqaa dqaci dqaco dqai dqamci dqamco dqamdi dqamdo dqap dqavi dqavo dqax dql dqs eds qcorei qcorer tds"
CHIPLET_UNITS[TCB]="atm bta eri hib tecorei"
CHIPLET_UNITS[TOP_YC]="yc_clk yc_top yu_rng"

# Function to extract RTL tag from workarea rbv/README file
# The RTL tag is stored in line 2 of $source_wa/rbv/README after "TAG: "
# Example: TAG: fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap
extract_rtl_tag() {
    local unit=$1
    local source_wa=$2
    local readme_file="$source_wa/rbv/README"
    
    # Try to read RTL tag from rbv/README (line 2)
    if [ -f "$readme_file" ]; then
        local tag=$(sed -n '2p' "$readme_file" | sed 's/^TAG: //')
        if [ -n "$tag" ]; then
            echo "$tag"
            return
        fi
    fi
    
    # Fallback: parse from workarea directory name if README doesn't exist
    local wa_basename=$(basename "$source_wa" 2>/dev/null)
    echo "$wa_basename" | sed -E "s/^${unit}_rbv_[0-9_]+_//; s/_(1NL|snap|run[0-9]*|PI|eco|fix|test|debug|final|rel|release)[_].*//"
}

# Count total units
TOTAL_UNITS=0
for chiplet in "${!CHIPLET_UNITS[@]}"; do
    units_array=(${CHIPLET_UNITS[$chiplet]})
    TOTAL_UNITS=$((TOTAL_UNITS + ${#units_array[@]}))
done

cat > "$output_file" << HEADER
# Agur Project - All Chiplet Block Releases

## Overview
This document tracks the latest block releases for all units across all chiplets in the AGUR project.

**Total Units**: $TOTAL_UNITS  
**Total Chiplets**: 7  
**Last Updated**: $current_date

### Chiplet Breakdown
- **HIOPL**: 4 units (ioptca, ioptcb, ioptcc, ioptcd)
- **CPORT**: 5 units (fdb, fth, lnd, pmux, prt)
- **HPORT**: 6 units (ccorea, ccoreb, ccorec, ccored, ccoree, ccoref)
- **NDQ**: 26 units (clt, cscore, dcmp, fdbm, fdbs, fthm, ftos, fwam, fwas, glc, iopl, ioplm, iopx, lndm, nvrisc, pmuxm, prtm, psca, pscb, pscc, pscd, px, riba, ribs, sma, yu)
- **QNS**: 18 units (dqaa, dqaci, dqaco, dqai, dqamci, dqamco, dqamdi, dqamdo, dqap, dqavi, dqavo, dqax, dql, dqs, eds, qcorei, qcorer, tds)
- **TCB**: 5 units (atm, bta, eri, hib, tecorei)
- **TOP_YC**: 3 units (yc_clk, yc_top, yu_rng)

## Release Tracking Method
- **STA Releases**: Tracked via \`last_sta_rel\` symbolic link
- **FCL Releases**: Tracked via \`fcl_release\` symbolic link  
- **Previous STA**: Tracked via \`prev_last_sta_rel\` symbolic link
- **Source**: \`/home/agur_backend_blockRelease/block/{unit}/logs/block_release.log\`

---

HEADER

# Process each chiplet
for chiplet in HIOPL CPORT HPORT NDQ QNS TCB TOP_YC; do
    echo "# Chiplet: $chiplet" >> "$output_file"
    echo "" >> "$output_file"
    
    units_list=${CHIPLET_UNITS[$chiplet]}
    
    for unit in $units_list; do
    base_dir="/home/agur_backend_blockRelease/block/$unit"
    
    echo "## Unit: $unit" >> "$output_file"
    echo "" >> "$output_file"
    
    # Latest STA Release
    if [ -L "$base_dir/last_sta_rel" ]; then
        sta_target=$(readlink -f "$base_dir/last_sta_rel")
        log="$sta_target/logs/block_release.log"
        
        echo "### Latest STA Release (last_sta_rel)" >> "$output_file"
        echo "" >> "$output_file"
        
        if [ -f "$log" ]; then
            timestamp=$(grep -a "^\-I\- \[" "$log" | grep "Release $unit from" | head -1 | sed 's/^-I- \[\(.*\)\].*/\1/')
            user=$(grep -a "^\-I\- \[" "$log" | grep " USER:" | head -1 | sed 's/^-I- \[.*\] USER: //')
            wa_name=$(grep -a "^\-I\- \[" "$log" | grep "Release $unit from" | head -1 | sed 's/^-I-.* Release .* from \(.*\)/\1/')
            
            # Extract source WA - try multiple patterns (different log formats)
            # Use grep -a to handle logs with binary data
            # Pattern 1: db_source (CPORT format - PNR/FCL releases)
            source_wa=$(grep -a "db_source.*scratch" "$log" | head -1 | sed 's|.* \(/home/scratch[^/]*/[^/]*/[^/]*/[^ ]*\)/.*|\1|' | sed 's|/export$||' | sed 's|/export/export_innovus$||')
            
            # Pattern 2: copy_file (STA-only releases)
            if [ -z "$source_wa" ]; then
                source_wa=$(grep -a "copy_file /home/scratch" "$log" | head -1 | sed 's|.*copy_file \(/home/scratch[^[:space:]]*/[^[:space:]]*\)/[ep][xn][pr].*|\1|' | sed 's|/export$||')
            fi
            
            # Pattern 3: Create block_release beflow workdir (NDQ/QNS/HPORT format - any /home directory)
            if [ -z "$source_wa" ]; then
                source_wa=$(grep -a "Create block_release beflow workdir" "$log" | head -1 | sed 's|.* = \(/home/[^/]*/.*\)/export/block_release.*|\1|')
            fi
            
            # Extract RTL tag
            rtl_tag=$(extract_rtl_tag "$unit" "$source_wa")
            
            # Extract flags
            pnr=$(grep -a "^\-I\-.*Pnr:" "$log" | head -1 | awk -F': ' '{print $2}')
            sta=$(grep -a "^\-I\-.*Sta:" "$log" | head -1 | awk -F': ' '{print $2}')
            fcl=$(grep -a "^\-I\-.*Fcl:" "$log" | head -1 | awk -F': ' '{print $2}')
            dc=$(grep -a "^\-I\-.*DC:" "$log" | head -1 | awk -F': ' '{print $2}')
            fe_dct=$(grep -a "^\-I\-.*FE_DCT:" "$log" | head -1 | awk -F': ' '{print $2}')
            full=$(grep -a "^\-I\-.*Full:" "$log" | head -1 | awk -F': ' '{print $2}')
            
            echo "| Property | Value |" >> "$output_file"
            echo "|----------|-------|" >> "$output_file"
            echo "| **Release Timestamp** | $timestamp |" >> "$output_file"
            echo "| **Release User** | $user |" >> "$output_file"
            echo "| **Workarea Name** | \`$wa_name\` |" >> "$output_file"
            echo "| **Source Workarea Path** | \`$source_wa\` |" >> "$output_file"
            echo "| **RTL Tag** | \`$rtl_tag\` |" >> "$output_file"
            echo "| **Release Directory** | \`$(basename $sta_target)\` |" >> "$output_file"
            echo "" >> "$output_file"
            
            echo "**Release Flags:**" >> "$output_file"
            echo "" >> "$output_file"
            echo "| Flag | Status | Description |" >> "$output_file"
            echo "|------|--------|-------------|" >> "$output_file"
            echo "| **Sta** | $sta | Static Timing Analysis (SPEF, SDC, netlist) |" >> "$output_file"
            echo "| **Fcl** | $fcl | Functional/Layout (DB, IOs, OASIS) |" >> "$output_file"
            echo "| **Pnr** | $pnr | Place & Route database |" >> "$output_file"
            echo "| **FE_DCT** | $fe_dct | Front End DCT |" >> "$output_file"
            echo "| **DC** | $dc | Design Compiler synthesis |" >> "$output_file"
            echo "| **Full** | $full | Full release (all files) |" >> "$output_file"
            echo "" >> "$output_file"
        fi
    fi
    
    # Check if FCL is different
    if [ -L "$base_dir/fcl_release" ]; then
        fcl_target=$(readlink -f "$base_dir/fcl_release")
        sta_target=$(readlink -f "$base_dir/last_sta_rel" 2>/dev/null)
        
        if [ "$sta_target" = "$fcl_target" ]; then
            echo "**Note:** FCL release points to same directory as STA release." >> "$output_file"
            echo "" >> "$output_file"
        else
            echo "### Latest FCL Release (fcl_release) - Different from STA" >> "$output_file"
            echo "" >> "$output_file"
            echo "FCL release is in a different directory than STA." >> "$output_file"
            echo "" >> "$output_file"
        fi
    fi
    
    # Previous STA
    if [ -L "$base_dir/prev_last_sta_rel" ]; then
        prev_target=$(readlink -f "$base_dir/prev_last_sta_rel")
        prev_log="$prev_target/logs/block_release.log"
        
        echo "### Previous STA Release (prev_last_sta_rel)" >> "$output_file"
        echo "" >> "$output_file"
        
        if [ -f "$prev_log" ]; then
            prev_timestamp=$(grep -a "^\-I\- \[" "$prev_log" | grep "Release $unit from" | head -1 | sed 's/^-I- \[\(.*\)\].*/\1/')
            echo "| Property | Value |" >> "$output_file"
            echo "|----------|-------|" >> "$output_file"
            echo "| **Release Timestamp** | $prev_timestamp |" >> "$output_file"
            echo "| **Release Directory** | \`$(basename $prev_target)\` |" >> "$output_file"
            echo "" >> "$output_file"
        fi
    fi
    
    echo "---" >> "$output_file"
    echo "" >> "$output_file"
    done  # End unit loop
    
    echo "" >> "$output_file"
done  # End chiplet loop

# Add footer
cat >> "$output_file" << 'FOOTER'

## Summary Table

| Unit | Chiplet | Latest STA Timestamp | User | Source Workarea | Release Types |
|------|---------|---------------------|------|-----------------|---------------|
FOOTER

# Generate summary table for all units
for chiplet in HIOPL CPORT HPORT NDQ QNS TCB TOP_YC; do
    units_list=${CHIPLET_UNITS[$chiplet]}
    
    for unit in $units_list; do
    base_dir="/home/agur_backend_blockRelease/block/$unit"
    
    if [ -L "$base_dir/last_sta_rel" ]; then
        sta_target=$(readlink -f "$base_dir/last_sta_rel")
        log="$sta_target/logs/block_release.log"
        
        if [ -f "$log" ]; then
            timestamp=$(grep -a "^\-I\- \[" "$log" | grep "Release $unit from" | head -1 | sed 's/^-I- \[\(.*\)\].*/\1/')
            user=$(grep -a "^\-I\- \[" "$log" | grep " USER:" | head -1 | sed 's/^-I- \[.*\] USER: //')
            
            # Extract source WA - try multiple patterns (different log formats)
            # Use grep -a to handle logs with binary data
            # Pattern 1: db_source (CPORT format - PNR/FCL releases)
            source_wa=$(grep -a "db_source.*scratch" "$log" | head -1 | sed 's|.* \(/home/scratch[^/]*/[^/]*/[^/]*/[^ ]*\)/.*|\1|' | sed 's|/export$||' | sed 's|/export/export_innovus$||')
            
            # Pattern 2: copy_file (STA-only releases)
            if [ -z "$source_wa" ]; then
                source_wa=$(grep -a "copy_file /home/scratch" "$log" | head -1 | sed 's|.*copy_file \(/home/scratch[^[:space:]]*/[^[:space:]]*\)/[ep][xn][pr].*|\1|' | sed 's|/export$||')
            fi
            
            # Pattern 3: Create block_release beflow workdir (NDQ/QNS/HPORT format - any /home directory)
            if [ -z "$source_wa" ]; then
                source_wa=$(grep -a "Create block_release beflow workdir" "$log" | head -1 | sed 's|.* = \(/home/[^/]*/.*\)/export/block_release.*|\1|')
            fi
            
            # Get active flags
            flags=""
            [ "$(grep -a "^\-I\-.*Sta:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="$flags STA"
            [ "$(grep -a "^\-I\-.*Fcl:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="$flags FCL"
            [ "$(grep -a "^\-I\-.*Pnr:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="$flags PNR"
            [ "$(grep -a "^\-I\-.*FE_DCT:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="$flags FE_DCT"
            [ "$(grep -a "^\-I\-.*DC:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="$flags DC"
            [ "$(grep -a "^\-I\-.*Full:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="$flags FULL"
            
            echo "| **$unit** | $chiplet | $timestamp | $user | \`$source_wa\` | $flags |" >> "$output_file"
        fi
    fi
    done  # End unit loop in summary table
done  # End chiplet loop in summary table

gen_date=$(date '+%Y-%m-%d %H:%M:%S')
cat >> "$output_file" << FOOTER

---

*Document Auto-Generated from Block Release Logs*  
*Generation Date: $gen_date*  
*Script: extract_agur_releases.sh*  
*Base Path: /home/agur_backend_blockRelease/block/*

## Notes

- All 5 CPORT units have both STA and FCL releases pointing to the same directory (combined release)
- Source workarea paths are extracted from the \`db_source\` line in block_release.log
- Flags indicate which types of files were included in each release
- Previous releases are tracked via \`prev_last_sta_rel\` symbolic links

FOOTER

echo "Data extracted successfully to: $output_file"

# Generate table files
table_txt="$SCRIPT_DIR/AGUR_UNITS_TABLE.txt"
table_csv="$SCRIPT_DIR/AGUR_UNITS_TABLE.csv"

# Generate TXT (pipe-delimited)
cat > "$table_txt" << 'TABLEHEADER'
# Agur Project - Units Table (All Chiplets)
# Generated: $(date '+%Y-%m-%d %H:%M:%S')
# 
# Format: UNIT | CHIPLET | RELEASED_WA_PATH | RTL_TAG | RELEASE_TYPES | RELEASE_DATE | RELEASE_USER
# -------------------------------------------------------------------------------------------------

TABLEHEADER

# Generate CSV header
echo "UNIT,CHIPLET,RELEASED_WA_PATH,RTL_TAG,RELEASE_TYPES,RELEASE_USER,RELEASE_TIMESTAMP" > "$table_csv"

# Add data for each unit across all chiplets
for chiplet in HIOPL CPORT HPORT NDQ QNS TCB TOP_YC; do
    units_list=${CHIPLET_UNITS[$chiplet]}
    
    for unit in $units_list; do
    base_dir="/home/agur_backend_blockRelease/block/$unit"
    
    if [ -L "$base_dir/last_sta_rel" ]; then
        sta_target=$(readlink -f "$base_dir/last_sta_rel")
        log="$sta_target/logs/block_release.log"
        
        if [ -f "$log" ]; then
            timestamp=$(grep -a "^\-I\- \[" "$log" | grep "Release $unit from" | head -1 | sed 's/^-I- \[\(.*\)\].*/\1/')
            user=$(grep -a "^\-I\- \[" "$log" | grep " USER:" | head -1 | sed 's/^-I- \[.*\] USER: //')
            
            # Extract source WA - try multiple patterns (different log formats)
            # Use grep -a to handle logs with binary data
            # Pattern 1: db_source (CPORT format - PNR/FCL releases)
            source_wa=$(grep -a "db_source.*scratch" "$log" | head -1 | sed 's|.* \(/home/scratch[^/]*/[^/]*/[^/]*/[^ ]*\)/.*|\1|' | sed 's|/export$||' | sed 's|/export/export_innovus$||')
            
            # Pattern 2: copy_file (STA-only releases)
            if [ -z "$source_wa" ]; then
                source_wa=$(grep -a "copy_file /home/scratch" "$log" | head -1 | sed 's|.*copy_file \(/home/scratch[^[:space:]]*/[^[:space:]]*\)/[ep][xn][pr].*|\1|' | sed 's|/export$||')
            fi
            
            # Pattern 3: Create block_release beflow workdir (NDQ/QNS/HPORT format - any /home directory)
            if [ -z "$source_wa" ]; then
                source_wa=$(grep -a "Create block_release beflow workdir" "$log" | head -1 | sed 's|.* = \(/home/[^/]*/.*\)/export/block_release.*|\1|')
            fi
            
            # Extract RTL tag
            rtl_tag=$(extract_rtl_tag "$unit" "$source_wa")
            
            # Extract date from timestamp (YYYY/MM/DD HH:MM:SS -> YYYY-MM-DD)
            release_date=$(echo "$timestamp" | awk '{print $1}' | tr '/' '-')
            
            # Get active flags
            flags=""
            [ "$(grep -a "^\-I\-.*Sta:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}STA,"
            [ "$(grep -a "^\-I\-.*Fcl:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}FCL,"
            [ "$(grep -a "^\-I\-.*Pnr:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}PNR,"
            [ "$(grep -a "^\-I\-.*FE_DCT:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}FE_DCT,"
            [ "$(grep -a "^\-I\-.*DC:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}DC,"
            [ "$(grep -a "^\-I\-.*Full:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}FULL,"
            flags=${flags%,}  # Remove trailing comma
            
            # Write to TXT (pipe-delimited)
            echo "$unit | $chiplet | $source_wa | $rtl_tag | $flags | $release_date | $user" >> "$table_txt"
            
            # Write to CSV
            echo "$unit,$chiplet,$source_wa,\"$rtl_tag\",\"$flags\",$user,$timestamp" >> "$table_csv"
        fi
    fi
    done  # End unit loop in table generation
done  # End chiplet loop in table generation

# Generate Markdown table
table_md="$SCRIPT_DIR/AGUR_UNITS_TABLE.md"

cat > "$table_md" << 'MDHEADER'
# Agur Project - Units Table (All Chiplets)

## Quick Reference

This markdown table provides an easy-to-read view of all AGUR units and their latest releases.

**Total Units**: See table below  
**Total Chiplets**: 7  
**Auto-Generated**: Yes (via extract_agur_releases.sh)

---

## Units Table

| Unit | Chiplet | Released WA Path | RTL Tag | Release Types | Release User | Release Date |
|------|---------|------------------|---------|---------------|--------------|--------------|
MDHEADER

# Add data for each unit in markdown format
for chiplet in HIOPL CPORT HPORT NDQ QNS TCB TOP_YC; do
    units_list=${CHIPLET_UNITS[$chiplet]}
    
    for unit in $units_list; do
    base_dir="/home/agur_backend_blockRelease/block/$unit"
    
    if [ -L "$base_dir/last_sta_rel" ]; then
        sta_target=$(readlink -f "$base_dir/last_sta_rel")
        log="$sta_target/logs/block_release.log"
        
        if [ -f "$log" ]; then
            timestamp=$(grep -a "^\-I\- \[" "$log" | grep "Release $unit from" | head -1 | sed 's/^-I- \[\(.*\)\].*/\1/')
            user=$(grep -a "^\-I\- \[" "$log" | grep " USER:" | head -1 | sed 's/^-I- \[.*\] USER: //')
            
            # Extract source WA - try multiple patterns (different log formats)
            # Use grep -a to handle logs with binary data
            # Pattern 1: db_source (CPORT format - PNR/FCL releases)
            source_wa=$(grep -a "db_source.*scratch" "$log" | head -1 | sed 's|.* \(/home/scratch[^/]*/[^/]*/[^/]*/[^ ]*\)/.*|\1|' | sed 's|/export$||' | sed 's|/export/export_innovus$||')
            
            # Pattern 2: copy_file (STA-only releases)
            if [ -z "$source_wa" ]; then
                source_wa=$(grep -a "copy_file /home/scratch" "$log" | head -1 | sed 's|.*copy_file \(/home/scratch[^[:space:]]*/[^[:space:]]*\)/[ep][xn][pr].*|\1|' | sed 's|/export$||')
            fi
            
            # Pattern 3: Create block_release beflow workdir (NDQ/QNS/HPORT format - any /home directory)
            if [ -z "$source_wa" ]; then
                source_wa=$(grep -a "Create block_release beflow workdir" "$log" | head -1 | sed 's|.* = \(/home/[^/]*/.*\)/export/block_release.*|\1|')
            fi
            
            # Extract RTL tag
            rtl_tag=$(extract_rtl_tag "$unit" "$source_wa")
            
            release_date=$(echo "$timestamp" | cut -d' ' -f1)
            
            # Get active flags (comma-separated for markdown)
            flags=""
            [ "$(grep -a "^\-I\-.*Sta:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}STA, "
            [ "$(grep -a "^\-I\-.*Fcl:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}FCL, "
            [ "$(grep -a "^\-I\-.*Pnr:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}PNR, "
            [ "$(grep -a "^\-I\-.*FE_DCT:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}FE_DCT, "
            [ "$(grep -a "^\-I\-.*DC:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}DC, "
            [ "$(grep -a "^\-I\-.*Full:" "$log" | head -1 | awk -F': ' '{print $2}')" = "True" ] && flags="${flags}FULL, "
            flags=${flags%, }  # Remove trailing comma and space
            
            # Write to markdown table
            echo "| $unit | $chiplet | \`$source_wa\` | \`$rtl_tag\` | $flags | $user | $release_date |" >> "$table_md"
        fi
    fi
    done
done

cat >> "$table_md" << 'MDFOOTER'

---

## Usage Examples

### Find a specific unit
```bash
grep "prtm" AGUR_UNITS_TABLE.txt
```

### List all NDQ units
```bash
grep "NDQ" AGUR_UNITS_TABLE.txt
```

### Count units by chiplet
```bash
for chiplet in HIOPL CPORT HPORT NDQ QNS TCB TOP_YC; do
    count=$(grep " $chiplet " AGUR_UNITS_TABLE.txt | wc -l)
    echo "$chiplet: $count units"
done
```

---

*Generated by: extract_agur_releases.sh*  
*Last Updated: See timestamp above*
MDFOOTER

echo "Table files generated:"
echo "  - $table_txt"
echo "  - $table_csv"
echo "  - $table_md"
