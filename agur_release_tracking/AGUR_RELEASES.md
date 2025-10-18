# Agur Project - All Chiplet Block Releases

## Overview
This document tracks the latest block releases for all units across all chiplets in the AGUR project.

**Total Units**: 67  
**Total Chiplets**: 7  
**Last Updated**: 2025-10-18 19:32:26

### Chiplet Breakdown
- **HIOPL**: 4 units (ioptca, ioptcb, ioptcc, ioptcd)
- **CPORT**: 5 units (fdb, fth, lnd, pmux, prt)
- **HPORT**: 6 units (ccorea, ccoreb, ccorec, ccored, ccoree, ccoref)
- **NDQ**: 26 units (clt, cscore, dcmp, fdbm, fdbs, fthm, ftos, fwam, fwas, glc, iopl, ioplm, iopx, lndm, nvrisc, pmuxm, prtm, psca, pscb, pscc, pscd, px, riba, ribs, sma, yu)
- **QNS**: 18 units (dqaa, dqaci, dqaco, dqai, dqamci, dqamco, dqamdi, dqamdo, dqap, dqavi, dqavo, dqax, dql, dqs, eds, qcorei, qcorer, tds)
- **TCB**: 5 units (atm, bta, eri, hib, tecorei)
- **TOP_YC**: 3 units (yc_clk, yc_top, yu_rng)

## Release Tracking Method
- **STA Releases**: Tracked via `last_sta_rel` symbolic link
- **FCL Releases**: Tracked via `fcl_release` symbolic link  
- **Previous STA**: Tracked via `prev_last_sta_rel` symbolic link
- **Source**: `/home/agur_backend_blockRelease/block/{unit}/logs/block_release.log`

---

# Chiplet: HIOPL

## Unit: ioptca

---

## Unit: ioptcb

---

## Unit: ioptcc

---

## Unit: ioptcd

---


# Chiplet: CPORT

## Unit: fdb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 17:30:09 |
| **Release User** | dkolesnikov |
| **Workarea Name** | `fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1` |
| **Source Workarea Path** | `/home/scratch.dkolesnikov_vlsi/agur/fdb/1NL/fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1` |
| **RTL Tag** | `fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1__2025_10_16_17_30_9` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/09 10:51:41 |
| **Release Directory** | `fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1__2025_10_9_10_51_41` |

---

## Unit: fth

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/17 10:54:41 |
| **Release User** | lmustafa |
| **Workarea Name** | `fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run` |
| **Source Workarea Path** | `/home/scratch.lmustafa_vlsi/agur/fth/fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run` |
| **RTL Tag** | `fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run__2025_10_17_10_54_41` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 15:10:17 |
| **Release Directory** | `fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner__2025_10_8_15_10_17` |

---

## Unit: lnd

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/17 08:26:05 |
| **Release User** | shlomoc |
| **Workarea Name** | `run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi/agur/lnd/run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065` |
| **RTL Tag** | `lnd_rbv_2025_09_26_trex_response_tag` |
| **Release Directory** | `run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065__2025_10_17_8_26_5` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 09:00:34 |
| **Release Directory** | `run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065__2025_10_8_9_0_34` |

---

## Unit: pmux

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 12:49:23 |
| **Release User** | brachas |
| **Workarea Name** | `pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |
| **RTL Tag** | `pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10__2025_10_16_12_49_23` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/09 17:04:55 |
| **Release Directory** | `pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10__2025_10_9_17_4_55` |

---

## Unit: prt

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 09:36:11 |
| **Release User** | ykatzav |
| **Workarea Name** | `prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_16_9_36_11` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 10:14:33 |
| **Release Directory** | `prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_10_14_33` |

---


# Chiplet: HPORT

## Unit: ccorea

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 14:36:32 |
| **Release User** | roir |
| **Workarea Name** | `ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.roir_vlsi/agur/ccorea/ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_14_36_32` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 14:24:14 |
| **Release Directory** | `ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_14_24_14` |

---

## Unit: ccoreb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 14:35:39 |
| **Release User** | roir |
| **Workarea Name** | `ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.roir_vlsi/agur/ccoreb/ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_14_35_39` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 14:35:39 |
| **Release Directory** | `ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_14_25_49` |

---

## Unit: ccorec

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 14:34:09 |
| **Release User** | roir |
| **Workarea Name** | `ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.roir_vlsi/agur/ccorec/ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_14_34_9` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 14:34:09 |
| **Release Directory** | `ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_8_14_21_42` |

---

## Unit: ccored

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 16:40:05 |
| **Release User** | sorino |
| **Workarea Name** | `ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |
| **Source Workarea Path** | `/home/scratch.sorino_vlsi/ccored/ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |
| **RTL Tag** | `ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins__2025_10_8_16_40_5` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/18 10:29:01 |
| **Release Directory** | `ccored_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap__new_pins__2025_9_18_10_29_1` |

---

## Unit: ccoree

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 16:28:05 |
| **Release User** | sorino |
| **Workarea Name** | `ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |
| **Source Workarea Path** | `/home/scratch.sorino_vlsi/ccoree/ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |
| **RTL Tag** | `ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins__2025_10_8_16_28_5` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/18 10:30:23 |
| **Release Directory** | `ccoree_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap__new_pins__2025_9_18_10_30_23` |

---

## Unit: ccoref

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 14:36:00 |
| **Release User** | sorino |
| **Workarea Name** | `ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |
| **Source Workarea Path** | `/home/scratch.sorino_vlsi/ccoref/ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |
| **RTL Tag** | `ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins__2025_10_8_14_36_0` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/18 10:29:56 |
| **Release Directory** | `ccoref_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap__new_pins__2025_9_18_10_29_56` |

---


# Chiplet: NDQ

## Unit: clt

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 10:00:09 |
| **Release User** | aamsalem |
| **Workarea Name** | `clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_part3` |
| **Source Workarea Path** | `/home/scratch.aamsalem_vlsi/agur/clt/1NL/9_9_new_flow/clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_part3` |
| **RTL Tag** | `clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_part3__2025_10_15_10_0_9` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/06 17:11:32 |
| **Release Directory** | `clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_part3__2025_10_6_17_11_32` |

---

## Unit: cscore

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 09:38:17 |
| **Release User** | ynaim |
| **Workarea Name** | `cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_eco_fix_vivid` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi_1/agur/1NL/cscore/cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_eco_fix_vivid` |
| **RTL Tag** | `cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_eco_fix_vivid__2025_10_15_9_38_17` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 16:05:40 |
| **Release Directory** | `cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_eco_fix__2025_10_8_16_5_40` |

---

## Unit: dcmp

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 11:30:10 |
| **Release User** | rmenasheof |
| **Workarea Name** | `dcmp_manual_flp_21_9_for_vivid` |
| **Source Workarea Path** | `/home/scratch.rmenasheof_vlsi/agur/dcmp/dcmp_manual_flp_21_9_for_vivid` |
| **RTL Tag** | `dcmp_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dcmp_manual_flp_21_9_for_vivid__2025_10_15_11_30_10` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 13:53:32 |
| **Release Directory** | `dcmp_manual_flp_21_9_for_vivid__2025_10_8_13_53_32` |

---

## Unit: fdbm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 08:39:51 |
| **Release User** | dkolesnikov |
| **Workarea Name** | `fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1` |
| **Source Workarea Path** | `/home/scratch.dkolesnikov_vlsi/agur/fdbm/1NL/fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1` |
| **RTL Tag** | `fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1__2025_10_15_8_39_51` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/12 09:03:46 |
| **Release Directory** | `fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1__2025_10_12_9_3_46` |

---

## Unit: fdbs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 12:54:27 |
| **Release User** | brachas |
| **Workarea Name** | `fdbs_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ctsfix2` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi/agur/1NL/fdbs/fdbs_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ctsfix2` |
| **RTL Tag** | `fdbs_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fdbs_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ctsfix2__2025_10_15_12_54_27` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/07 22:57:20 |
| **Release Directory** | `fdbs_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ctsfix2__2025_10_7_22_57_20` |

---

## Unit: fthm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 18:13:16 |
| **Release User** | ayerushalmy |
| **Workarea Name** | `fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3` |
| **Source Workarea Path** | `/home/scratch.ayerushalmy_vlsi/agur/fthm/1NL/fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3` |
| **RTL Tag** | `fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3__2025_10_16_18_13_16` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/14 09:43:10 |
| **Release Directory** | `fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_1st_side__2025_10_14_9_43_10` |

---

## Unit: ftos

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 12:49:16 |
| **Release User** | thadad |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.thadad_vlsi_1/agur/1NL/ftos/condb_int3_2025_08_27_0_1NL_snap_th/pnr_flow/nv_flow/ftos/ipo1000/nbu_signoff` |
| **RTL Tag** | `ftos_rbv_2025_09_04_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_condb_int3_2025_08_27_0_1NL_snap_th_ipo1000_2025_10_16_12_49_16` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/14 23:49:28 |
| **Release Directory** | `nbu_signoff_condb_int3_2025_08_27_0_1NL_snap_th_ipo1000_2025_10_14_23_49_28` |

---

## Unit: fwam

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 11:08:39 |
| **Release User** | zbirman |
| **Workarea Name** | `run_15_09_2025_fwam_rbv_2025_09_07_4x6_clock_tree_Tzlil_Hook_for_vivid` |
| **Source Workarea Path** | `/home/scratch.zbirman_vlsi/agur/fwam/run_15_09_2025_fwam_rbv_2025_09_07_4x6_clock_tree_Tzlil_Hook_for_vivid` |
| **RTL Tag** | `fwam_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `run_15_09_2025_fwam_rbv_2025_09_07_4x6_clock_tree_Tzlil_Hook_for_vivid__2025_10_15_11_8_39` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 13:05:32 |
| **Release Directory** | `run_15_09_2025_fwam_rbv_2025_09_07_4x6_clock_tree_Tzlil_Hook__2025_10_8_13_5_32` |

---

## Unit: fwas

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 14:40:41 |
| **Release User** | rmenasheof |
| **Workarea Name** | `fwas_golden_ipo4_21_9_for_vivid` |
| **Source Workarea Path** | `/home/scratch.rmenasheof_vlsi/agur/fwas/fwas_golden_ipo4_21_9_for_vivid` |
| **RTL Tag** | `fwas_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fwas_golden_ipo4_21_9_for_vivid__2025_10_15_14_40_41` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 09:06:50 |
| **Release Directory** | `fwas_golden_ipo4_21_9_for_vivid__2025_10_8_9_6_50` |

---

## Unit: glc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 09:29:21 |
| **Release User** | ynaim |
| **Workarea Name** | `glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi_1/agur/1NL/glc/glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid` |
| **RTL Tag** | `glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid__2025_10_15_9_29_21` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 15:57:13 |
| **Release Directory** | `glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound__2025_10_8_15_57_13` |

---

## Unit: iopl

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/07/27 10:38:26 |
| **Release User** | yshlush |
| **Workarea Name** | `iopl_condb_int1_52_2r1` |
| **Source Workarea Path** | `/home/scratch.yshlush_vlsi/iopl/iopl_condb_int1_52_2r1/export/export_icc2` |
| **RTL Tag** | `export_icc2` |
| **Release Directory** | `iopl_condb_int1_52_2r1__2025_7_27_10_38_26` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** |  | Front End DCT |
| **DC** |  | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

---

## Unit: ioplm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2024/11/14 11:05:29 |
| **Release User** | netaa |
| **Workarea Name** | `starling_ioplm_2024_10_30` |
| **Source Workarea Path** | `/home/sunbird_netaa/ioplm/starling_ioplm_2024_10_30` |
| **RTL Tag** | `starling_ioplm_2024_10_30` |
| **Release Directory** | `starling_ioplm_2024_10_30__2024_11_14_11_5_29` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** |  | Front End DCT |
| **DC** |  | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

---

## Unit: iopx

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/03/05 13:10:45 |
| **Release User** | vmoshkovich |
| **Workarea Name** | `starling_iopx_2024_11_06` |
| **Source Workarea Path** | `/home/sunbird_vmoshkovich/iopx/starling_iopx_2024_11_06` |
| **RTL Tag** | `starling_iopx_2024_11_06` |
| **Release Directory** | `starling_iopx_2024_11_06__2025_3_5_13_10_45` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** |  | Front End DCT |
| **DC** |  | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

---

## Unit: lndm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 16:05:35 |
| **Release User** | shlomoc |
| **Workarea Name** | `run_07_09_2025_lndm_rbv_2025_09_01_new_flow` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi/agur/lndm/run_07_09_2025_lndm_rbv_2025_09_01_new_flow` |
| **RTL Tag** | `lndm_rbv_2025_09_01_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `run_07_09_2025_lndm_rbv_2025_09_01_new_flow__2025_10_15_16_5_35` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 15:50:51 |
| **Release Directory** | `run_07_09_2025_lndm_rbv_2025_09_01_new_flow__2025_10_15_15_50_51` |

---

## Unit: nvrisc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 13:28:31 |
| **Release User** | ykatzav |
| **Workarea Name** | `nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2` |
| **Source Workarea Path** | `/home/scratch.ykatzav_vlsi/agur/nvrisc/nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2` |
| **RTL Tag** | `nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2__2025_10_15_13_28_31` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/06 10:19:07 |
| **Release Directory** | `nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2__2025_10_6_10_19_7` |

---

## Unit: pmuxm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 11:53:00 |
| **Release User** | brachas |
| **Workarea Name** | `pmuxm_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi/agur/1NL/pmuxm/pmuxm_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |
| **RTL Tag** | `pmuxm_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `pmuxm_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10__2025_10_15_11_53_0` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/06 11:13:14 |
| **Release Directory** | `pmuxm_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10__2025_10_6_11_13_14` |

---

## Unit: prtm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 16:32:41 |
| **Release User** | lmustafa |
| **Workarea Name** | `prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry` |
| **Source Workarea Path** | `/home/scratch.lmustafa_vlsi/agur/prtm/prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry` |
| **RTL Tag** | `prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1` |
| **Release Directory** | `prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry__2025_10_15_16_32_41` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 15:52:10 |
| **Release Directory** | `prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry__2025_10_8_15_52_10` |

---

## Unit: psca

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 20:48:53 |
| **Release User** | nkahaz |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.nkahaz_vlsi/ww38_5_fixes/psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_ref` |
| **RTL Tag** | `psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_ref_ipo1045_2025_10_15_20_48_53` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/12 08:45:31 |
| **Release Directory** | `nbu_signoff_psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_ref_ipo1044_2025_10_12_8_45_31` |

---

## Unit: pscb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/14 19:38:28 |
| **Release User** | nkahaz |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.nkahaz_vlsi/ww38_5_fixes/pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ref` |
| **RTL Tag** | `pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ref_ipo1044_2025_10_14_19_38_28` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/11 10:26:18 |
| **Release Directory** | `nbu_signoff_pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ref_ipo1044_2025_10_11_10_26_18` |

---

## Unit: pscc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 11:44:08 |
| **Release User** | dtraitelovic |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.dtraitelovic_vlsi/agur/pscc/pscc_2025_09_02_1NL_snap_new_flow_flp_cdc` |
| **RTL Tag** | `pscc_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_pscc_2025_09_02_1NL_snap_new_flow_flp_cdc_ipo1003_2025_10_16_11_44_8` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 14:47:33 |
| **Release Directory** | `nbu_signoff_pscc_2025_09_02_1NL_snap_new_flow_flp_cdc_ipo1000_2025_10_8_14_47_33` |

---

## Unit: pscd

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 11:54:04 |
| **Release User** | gibell |
| **Workarea Name** | `pscd_rbv_2025_09_02_ver4_Sep25_gb` |
| **Source Workarea Path** | `/home/scratch.gibell_vlsi/agur/1nl/pscd/pscd_rbv_2025_09_02_ver4_Sep25_gb` |
| **RTL Tag** | `pscd_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `pscd_rbv_2025_09_02_ver4_Sep25_gb__2025_10_16_11_54_4` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 11:54:04 |
| **Release Directory** | `pscd_rbv_2025_09_02_ver4_Sep25_gb__2025_10_16_11_52_47` |

---

## Unit: px

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 10:08:41 |
| **Release User** | aamsalem |
| **Workarea Name** | `px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65` |
| **Source Workarea Path** | `/home/scratch.aamsalem_vlsi/agur/px/1NL/run_9_9_old_util65/px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65` |
| **RTL Tag** | `px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65__2025_10_15_10_8_41` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 10:08:41 |
| **Release Directory** | `px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65__2025_10_15_10_5_44` |

---

## Unit: riba

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 10:53:34 |
| **Release User** | rmenasheof |
| **Workarea Name** | `riba_10_9_1nl_new_flow_golden` |
| **Source Workarea Path** | `/home/scratch.rmenasheof_vlsi/agur/riba/riba_10_9_1nl_new_flow_golden` |
| **RTL Tag** | `riba_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `riba_10_9_1nl_new_flow_golden__2025_10_15_10_53_34` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 09:07:41 |
| **Release Directory** | `riba_10_9_1nl_new_flow_golden__2025_10_8_9_7_41` |

---

## Unit: ribs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 09:29:31 |
| **Release User** | ynaim |
| **Workarea Name** | `ribs.ribs_rbv_2025_09_02_condb_int3_08_27_0_1NL_snap_no_route_blk_vivid` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi_1/agur/1NL/ribs/ribs.ribs_rbv_2025_09_02_condb_int3_08_27_0_1NL_snap_no_route_blk_vivid` |
| **RTL Tag** | `ribs_rbv_2025_09_02_condb_int3_08_27_0_1NL_snap` |
| **Release Directory** | `ribs.ribs_rbv_2025_09_02_condb_int3_08_27_0_1NL_snap_no_route_blk_vivid__2025_10_15_9_29_31` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/08 15:54:01 |
| **Release Directory** | `ribs.ribs_rbv_2025_09_02_condb_int3_08_27_0_1NL_snap_no_route_blk__2025_10_8_15_54_1` |

---

## Unit: sma

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 16:05:39 |
| **Release User** | shlomoc |
| **Workarea Name** | `run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi/agur/sma/run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix` |
| **RTL Tag** | `sma_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix__2025_10_15_16_5_39` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/15 15:51:49 |
| **Release Directory** | `run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix__2025_10_15_15_51_49` |

---

## Unit: yu

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/05/25 09:29:17 |
| **Release User** | ashahock |
| **Workarea Name** | `yu_agur_rbv_2025_03_17_condb_int1_11_3_BE_TNL_snap_ver7_new_flow` |
| **Source Workarea Path** | `/home/scratch.ashahock_vlsi_1/agur/yu/yu_agur_rbv_2025_03_17_condb_int1_11_3_BE_TNL_snap_ver7_new_flow` |
| **RTL Tag** | `yu_agur_rbv_2025_03_17_condb_int1_11_3_BE_TNL` |
| **Release Directory** | `yu_agur_rbv_2025_03_17_condb_int1_11_3_BE_TNL_snap_ver7_new_flow__2025_5_25_9_29_17` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** |  | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

---


# Chiplet: QNS

## Unit: dqaa

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/12 04:26:30 |
| **Release User** | siddharthasa |
| **Workarea Name** | `dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_10_sep` |
| **Source Workarea Path** | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqaa/dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_10_sep` |
| **RTL Tag** | `dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_10_sep__2025_10_12_4_26_30` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/05 07:10:55 |
| **Release Directory** | `dqaa_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_run1__2025_9_5_7_10_55` |

---

## Unit: dqaci

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/26 21:44:33 |
| **Release User** | mbetzer |
| **Workarea Name** | `dqaci_250609_new_pin_placement` |
| **Source Workarea Path** | `/home/scratch.mbetzer_vlsi/agur/dqaci/dqaci_250609_new_pin_placement` |
| **RTL Tag** | `dqaci_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap` |
| **Release Directory** | `dqaci_250609_new_pin_placement__2025_8_26_21_44_33` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/19 17:46:16 |
| **Release Directory** | `dqaci_250609_new_pin_placement__2025_8_19_17_46_16` |

---

## Unit: dqaco

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/26 11:31:56 |
| **Release User** | mbetzer |
| **Workarea Name** | `dqaco_250609_new_pin_placement` |
| **Source Workarea Path** | `/home/scratch.mbetzer_vlsi/agur/dqaco/dqaco_250609_new_pin_placement` |
| **RTL Tag** | `dqaco_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap` |
| **Release Directory** | `dqaco_250609_new_pin_placement__2025_8_26_11_31_56` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/19 17:45:06 |
| **Release Directory** | `dqaco_250609_new_pin_placement__2025_8_19_17_45_6` |

---

## Unit: dqai

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/31 08:59:25 |
| **Release User** | mlanzerer |
| **Workarea Name** | `dqai_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap` |
| **Source Workarea Path** | `/home/scratch.mlanzerer_vlsi/dqai_dir/dqai_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap` |
| **RTL Tag** | `dqai_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap` |
| **Release Directory** | `dqai_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap__2025_8_31_8_59_25` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/31 08:40:57 |
| **Release Directory** | `dqai_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap__2025_8_31_8_40_57` |

---

## Unit: dqamci

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/18 07:16:45 |
| **Release User** | mlanzerer |
| **Workarea Name** | `dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.mlanzerer_vlsi/dqamci_dir/dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_18_7_16_45` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 08:46:23 |
| **Release Directory** | `dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_16_8_46_23` |

---

## Unit: dqamco

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/17 14:17:56 |
| **Release User** | siddharthasa |
| **Workarea Name** | `dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_10_sep` |
| **Source Workarea Path** | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqamco/dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_10_sep` |
| **RTL Tag** | `dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_10_sep__2025_10_17_14_17_56` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/05 07:09:42 |
| **Release Directory** | `dqamco_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_run1__2025_9_5_7_9_42` |

---

## Unit: dqamdi

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/13 19:44:12 |
| **Release User** | seeman |
| **Workarea Name** | `dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si` |
| **Source Workarea Path** | `/home/scratch.seeman_vlsi_1/agur/1nl/dqamdi/dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si` |
| **RTL Tag** | `dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si__2025_10_13_19_44_12` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/11 18:52:15 |
| **Release Directory** | `dqamdi_rbv_2025_07_06_agur_int2_condb_int2_23_5r1_BE_SFNL_no_SLCG_block_release_2__2025_9_11_18_52_14` |

---

## Unit: dqamdo

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/16 21:26:44 |
| **Release User** | abarman |
| **Workarea Name** | `dqamdo_rbv_2025_07_06_agur_int2_condb_int2_23_5r1_BE_SFNL_no_SLCG_so2` |
| **Source Workarea Path** | `/home/scratch.abarman_vlsi/agur/SFNL/DQAMDO/DQAMDO_NewPinDef2_SynPNR_run2_SO2/dqamdo_rbv_2025_07_06_agur_int2_condb_int2_23_5r1_BE_SFNL_no_SLCG_so2` |
| **RTL Tag** | `agur_int2_condb_int2_23_5r1_BE_SFNL_no_SLCG_so2` |
| **Release Directory** | `dqamdo_rbv_2025_07_06_agur_int2_condb_int2_23_5r1_BE_SFNL_no_SLCG_so2__2025_9_16_21_26_44` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/16 08:51:24 |
| **Release Directory** | `dqamdo_rbv_2025_07_06_agur_int2_condb_int2_23_5r1_BE_SFNL_no_SLCG_lvs_sid__2025_9_16_8_51_24` |

---

## Unit: dqap

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/21 11:23:47 |
| **Release User** | tmazor |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.tmazor_vlsi/agur/dqap_rbv_2025_09_05_agur_condb_int3_2025_08_27_0_1NL_snap_new_flow` |
| **RTL Tag** | `dqap_rbv_2025_09_05_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff__2025_9_21_11_23_47` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/28 21:24:42 |
| **Release Directory** | `dqap_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap__2025_8_28_21_24_42` |

---

## Unit: dqavi

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/05 12:45:48 |
| **Release User** | abarman |
| **Workarea Name** | `dqavi_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_run6_SO` |
| **Source Workarea Path** | `/home/scratch.abarman_vlsi/agur/SFNL/DQAVI/DQAVI_NewPinDef2_SynPNR_run6_SO/dqavi_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_run6_SO` |
| **RTL Tag** | `dqavi_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap` |
| **Release Directory** | `dqavi_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_run6_SO__2025_9_5_12_45_48` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/05/25 20:15:44 |
| **Release Directory** | `dqavi_rbv_2025_03_13_condb_int1_11_3_BE_TNL_snap_signoff_1001__2025_5_25_20_15_44` |

---

## Unit: dqavo

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/28 14:01:12 |
| **Release User** | hschiffavrah |
| **Workarea Name** | `dqavo_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_nf_wo_blk` |
| **Source Workarea Path** | `/home/scratch.hschiffavrah_vlsi/agur/dqavo/dqavo_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_nf_wo_blk` |
| **RTL Tag** | `dqavo_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap` |
| **Release Directory** | `dqavo_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_nf_wo_blk__2025_8_28_14_1_12` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/05/27 10:23:25 |
| **Release Directory** | `dqavo_rbv_2025_03_13_condb_int1_11_3_BE_TNL_snap_nflow_2_ref__2025_5_27_10_23_25` |

---

## Unit: dqax

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/13 10:35:19 |
| **Release User** | mlanzerer |
| **Workarea Name** | `dqax_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.mlanzerer_vlsi/dqax_dir/dqax_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `dqax_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqax_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap__2025_10_13_10_35_19` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/07 09:27:59 |
| **Release Directory** | `beta_final__2025_9_7_9_27_59` |

---

## Unit: dql

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/28 16:51:24 |
| **Release User** | bnevo |
| **Workarea Name** | `dql_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.bnevo_vlsi/agur/dql/dql_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `dql_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dql_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap__2025_9_28_16_51_24` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/16 08:37:15 |
| **Release Directory** | `dql_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_interface_effort__2025_9_16_8_37_15` |

---

## Unit: dqs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/24 21:41:11 |
| **Release User** | abarman |
| **Workarea Name** | `dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so` |
| **Source Workarea Path** | `/home/scratch.abarman_vlsi/agur/1NL/DQS/1NL_run1_SO/dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so` |
| **RTL Tag** | `dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap` |
| **Release Directory** | `dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so__2025_9_24_21_41_11` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | True | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/24 20:40:13 |
| **Release Directory** | `dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so__2025_9_24_20_40_13` |

---

## Unit: eds

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/04/02 15:59:49 |
| **Release User** | ysapojnikov |
| **Workarea Name** | `eds_rbv_2025_03_13_condb_int1_11_3_BE_TNL_snap` |
| **Source Workarea Path** | `/home/scratch.ysapojnikov_vlsi_1/agur/eds/eds_rbv_2025_03_13_condb_int1_11_3_BE_TNL_snap` |
| **RTL Tag** | `condb_int1_11_3_BE_TNL_snap` |
| **Release Directory** | `eds_rbv_2025_03_13_condb_int1_11_3_BE_TNL_snap__2025_4_2_15_59_49` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** |  | Front End DCT |
| **DC** |  | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

---

## Unit: qcorei

---

## Unit: qcorer

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/01 14:32:00 |
| **Release User** | daltman |
| **Workarea Name** | `qcorer_rbv_2025_09_02_1NL_snap_ref` |
| **Source Workarea Path** | `/home/scratch.daltman_vlsi/qcorer/qcorer_rbv_2025_09_02_1NL_snap_ref` |
| **RTL Tag** | `qcorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `qcorer_rbv_2025_09_02_1NL_snap_ref__2025_10_1_14_32_0` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/09 14:12:11 |
| **Release Directory** | `qcorer_rbv_2025_06_09_region_no_skew_interface_effort__2025_9_9_14_12_11` |

---

## Unit: tds

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/10 07:26:36 |
| **Release User** | hsajwan |
| **Workarea Name** | `tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |
| **Source Workarea Path** | `/home/scratch.hsajwan_vlsi/agur/1NL/tds/tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |
| **RTL Tag** | `tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN__2025_10_10_7_26_36` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/25 12:18:42 |
| **Release Directory** | `tds_250615_new_pin_placement__2025_8_25_12_18_42` |

---


# Chiplet: TCB

## Unit: atm

---

## Unit: bta

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/16 15:35:44 |
| **Release User** | vliberchuk |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.vliberchuk_vlsi/agur/1nl/bta/bta_2025_09_25_Oct10` |
| **RTL Tag** | `bta_rbv_2025_09_25new_tag_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_bta_2025_09_25_Oct10_ipo1006_2025_10_16_15_35_44` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/10 10:48:20 |
| **Release Directory** | `nbu_signoff_bta_2025_09_25_Oct10_ipo1005_2025_10_10_10_48_20` |

---

## Unit: eri

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/17 18:13:28 |
| **Release User** | hsajwan |
| **Workarea Name** | `eri_rbv_2025_09_28_timing_fixes_first_run` |
| **Source Workarea Path** | `/home/scratch.hsajwan_vlsi/agur/1NL/ERI/eri_rbv_2025_09_28_timing_fixes_first_run` |
| **RTL Tag** | `eri_rbv_2025_09_28_timing_fixes` |
| **Release Directory** | `eri_rbv_2025_09_28_timing_fixes_first_run__2025_10_17_18_13_28` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/08/28 17:07:57 |
| **Release Directory** | `eri_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_nf__2025_8_28_17_7_57` |

---

## Unit: hib

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/11 11:33:58 |
| **Release User** | maximkr |
| **Workarea Name** | `hib_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_fp2` |
| **Source Workarea Path** | `/home/scratch.maximkr_vlsi/agur/hib/hib_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_fp2` |
| **RTL Tag** | `hib_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `hib_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_fp2__2025_10_11_11_33_58` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | False | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/09/26 10:10:27 |
| **Release Directory** | `hib_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_fp2__2025_9_26_10_10_27` |

---

## Unit: tecorei

---


# Chiplet: TOP_YC

## Unit: yc_clk

---

## Unit: yc_top

---

## Unit: yu_rng

---



## Summary Table

| Unit | Chiplet | Latest STA Timestamp | User | Source Workarea | Release Types |
|------|---------|---------------------|------|-----------------|---------------|
| **fdb** | CPORT | 2025/10/16 17:30:09 | dkolesnikov | `/home/scratch.dkolesnikov_vlsi/agur/fdb/1NL/fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1` |  STA FCL PNR FE_DCT |
| **fth** | CPORT | 2025/10/17 10:54:41 | lmustafa | `/home/scratch.lmustafa_vlsi/agur/fth/fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run` |  STA FCL FE_DCT |
| **lnd** | CPORT | 2025/10/17 08:26:05 | shlomoc | `/home/scratch.shlomoc_vlsi/agur/lnd/run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065` |  STA |
| **pmux** | CPORT | 2025/10/16 12:49:23 | brachas | `/home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |  STA FCL PNR FE_DCT |
| **prt** | CPORT | 2025/10/16 09:36:11 | ykatzav | `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA FCL |
| **ccorea** | HPORT | 2025/10/08 14:36:32 | roir | `/home/scratch.roir_vlsi/agur/ccorea/ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA |
| **ccoreb** | HPORT | 2025/10/08 14:35:39 | roir | `/home/scratch.roir_vlsi/agur/ccoreb/ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA |
| **ccorec** | HPORT | 2025/10/08 14:34:09 | roir | `/home/scratch.roir_vlsi/agur/ccorec/ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA |
| **ccored** | HPORT | 2025/10/08 16:40:05 | sorino | `/home/scratch.sorino_vlsi/ccored/ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |  STA FE_DCT |
| **ccoree** | HPORT | 2025/10/08 16:28:05 | sorino | `/home/scratch.sorino_vlsi/ccoree/ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |  STA FE_DCT |
| **ccoref** | HPORT | 2025/10/08 14:36:00 | sorino | `/home/scratch.sorino_vlsi/ccoref/ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins` |  STA FE_DCT |
| **clt** | NDQ | 2025/10/15 10:00:09 | aamsalem | `/home/scratch.aamsalem_vlsi/agur/clt/1NL/9_9_new_flow/clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_part3` |  STA FCL PNR |
| **cscore** | NDQ | 2025/10/15 09:38:17 | ynaim | `/home/scratch.ynaim_vlsi_1/agur/1NL/cscore/cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_eco_fix_vivid` |  STA |
| **dcmp** | NDQ | 2025/10/15 11:30:10 | rmenasheof | `/home/scratch.rmenasheof_vlsi/agur/dcmp/dcmp_manual_flp_21_9_for_vivid` |  STA |
| **fdbm** | NDQ | 2025/10/15 08:39:51 | dkolesnikov | `/home/scratch.dkolesnikov_vlsi/agur/fdbm/1NL/fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1` |  STA FCL PNR FE_DCT |
| **fdbs** | NDQ | 2025/10/15 12:54:27 | brachas | `/home/scratch.brachas_vlsi/agur/1NL/fdbs/fdbs_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ctsfix2` |  STA FCL PNR FE_DCT |
| **fthm** | NDQ | 2025/10/16 18:13:16 | ayerushalmy | `/home/scratch.ayerushalmy_vlsi/agur/fthm/1NL/fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3` |  STA FCL PNR |
| **ftos** | NDQ | 2025/10/16 12:49:16 | thadad | `/home/scratch.thadad_vlsi_1/agur/1NL/ftos/condb_int3_2025_08_27_0_1NL_snap_th/pnr_flow/nv_flow/ftos/ipo1000/nbu_signoff` |  STA FCL PNR |
| **fwam** | NDQ | 2025/10/15 11:08:39 | zbirman | `/home/scratch.zbirman_vlsi/agur/fwam/run_15_09_2025_fwam_rbv_2025_09_07_4x6_clock_tree_Tzlil_Hook_for_vivid` |  STA |
| **fwas** | NDQ | 2025/10/15 14:40:41 | rmenasheof | `/home/scratch.rmenasheof_vlsi/agur/fwas/fwas_golden_ipo4_21_9_for_vivid` |  STA |
| **glc** | NDQ | 2025/10/15 09:29:21 | ynaim | `/home/scratch.ynaim_vlsi_1/agur/1NL/glc/glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid` |  STA |
| **iopl** | NDQ | 2025/07/27 10:38:26 | yshlush | `/home/scratch.yshlush_vlsi/iopl/iopl_condb_int1_52_2r1/export/export_icc2` |  STA FCL |
| **ioplm** | NDQ | 2024/11/14 11:05:29 | netaa | `/home/sunbird_netaa/ioplm/starling_ioplm_2024_10_30` |  STA |
| **iopx** | NDQ | 2025/03/05 13:10:45 | vmoshkovich | `/home/sunbird_vmoshkovich/iopx/starling_iopx_2024_11_06` |  STA FCL |
| **lndm** | NDQ | 2025/10/15 16:05:35 | shlomoc | `/home/scratch.shlomoc_vlsi/agur/lndm/run_07_09_2025_lndm_rbv_2025_09_01_new_flow` |  STA FCL |
| **nvrisc** | NDQ | 2025/10/15 13:28:31 | ykatzav | `/home/scratch.ykatzav_vlsi/agur/nvrisc/nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2` |  STA FCL |
| **pmuxm** | NDQ | 2025/10/15 11:53:00 | brachas | `/home/scratch.brachas_vlsi/agur/1NL/pmuxm/pmuxm_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |  STA FCL PNR FE_DCT |
| **prtm** | NDQ | 2025/10/15 16:32:41 | lmustafa | `/home/scratch.lmustafa_vlsi/agur/prtm/prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry` |  STA FE_DCT |
| **psca** | NDQ | 2025/10/15 20:48:53 | nkahaz | `/home/scratch.nkahaz_vlsi/ww38_5_fixes/psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_ref` |  STA |
| **pscb** | NDQ | 2025/10/14 19:38:28 | nkahaz | `/home/scratch.nkahaz_vlsi/ww38_5_fixes/pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ref` |  STA |
| **pscc** | NDQ | 2025/10/16 11:44:08 | dtraitelovic | `/home/scratch.dtraitelovic_vlsi/agur/pscc/pscc_2025_09_02_1NL_snap_new_flow_flp_cdc` |  STA |
| **pscd** | NDQ | 2025/10/16 11:54:04 | gibell | `/home/scratch.gibell_vlsi/agur/1nl/pscd/pscd_rbv_2025_09_02_ver4_Sep25_gb` |  STA |
| **px** | NDQ | 2025/10/15 10:08:41 | aamsalem | `/home/scratch.aamsalem_vlsi/agur/px/1NL/run_9_9_old_util65/px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65` |  STA FCL PNR |
| **riba** | NDQ | 2025/10/15 10:53:34 | rmenasheof | `/home/scratch.rmenasheof_vlsi/agur/riba/riba_10_9_1nl_new_flow_golden` |  STA |
| **ribs** | NDQ | 2025/10/15 09:29:31 | ynaim | `/home/scratch.ynaim_vlsi_1/agur/1NL/ribs/ribs.ribs_rbv_2025_09_02_condb_int3_08_27_0_1NL_snap_no_route_blk_vivid` |  STA |
| **sma** | NDQ | 2025/10/15 16:05:39 | shlomoc | `/home/scratch.shlomoc_vlsi/agur/sma/run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix` |  STA FCL |
| **yu** | NDQ | 2025/05/25 09:29:17 | ashahock | `/home/scratch.ashahock_vlsi_1/agur/yu/yu_agur_rbv_2025_03_17_condb_int1_11_3_BE_TNL_snap_ver7_new_flow` |  STA PNR |
| **dqaa** | QNS | 2025/10/12 04:26:30 | siddharthasa | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqaa/dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_10_sep` |  STA FCL PNR |
| **dqaci** | QNS | 2025/08/26 21:44:33 | mbetzer | `/home/scratch.mbetzer_vlsi/agur/dqaci/dqaci_250609_new_pin_placement` |  STA |
| **dqaco** | QNS | 2025/08/26 11:31:56 | mbetzer | `/home/scratch.mbetzer_vlsi/agur/dqaco/dqaco_250609_new_pin_placement` |  STA |
| **dqai** | QNS | 2025/08/31 08:59:25 | mlanzerer | `/home/scratch.mlanzerer_vlsi/dqai_dir/dqai_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap` |  STA FE_DCT |
| **dqamci** | QNS | 2025/10/18 07:16:45 | mlanzerer | `/home/scratch.mlanzerer_vlsi/dqamci_dir/dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA |
| **dqamco** | QNS | 2025/10/17 14:17:56 | siddharthasa | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqamco/dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_10_sep` |  STA FCL PNR |
| **dqamdi** | QNS | 2025/10/13 19:44:12 | seeman | `/home/scratch.seeman_vlsi_1/agur/1nl/dqamdi/dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si` |  STA |
| **dqamdo** | QNS | 2025/09/16 21:26:44 | abarman | `/home/scratch.abarman_vlsi/agur/SFNL/DQAMDO/DQAMDO_NewPinDef2_SynPNR_run2_SO2/dqamdo_rbv_2025_07_06_agur_int2_condb_int2_23_5r1_BE_SFNL_no_SLCG_so2` |  STA PNR FE_DCT |
| **dqap** | QNS | 2025/09/21 11:23:47 | tmazor | `/home/scratch.tmazor_vlsi/agur/dqap_rbv_2025_09_05_agur_condb_int3_2025_08_27_0_1NL_snap_new_flow` |  STA |
| **dqavi** | QNS | 2025/09/05 12:45:48 | abarman | `/home/scratch.abarman_vlsi/agur/SFNL/DQAVI/DQAVI_NewPinDef2_SynPNR_run6_SO/dqavi_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_run6_SO` |  STA FCL PNR FE_DCT |
| **dqavo** | QNS | 2025/08/28 14:01:12 | hschiffavrah | `/home/scratch.hschiffavrah_vlsi/agur/dqavo/dqavo_rbv_2025_06_09_condb_int2_23_5r1_BE_SFNL_snap_nf_wo_blk` |  STA FCL PNR FE_DCT |
| **dqax** | QNS | 2025/10/13 10:35:19 | mlanzerer | `/home/scratch.mlanzerer_vlsi/dqax_dir/dqax_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA |
| **dql** | QNS | 2025/09/28 16:51:24 | bnevo | `/home/scratch.bnevo_vlsi/agur/dql/dql_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA |
| **dqs** | QNS | 2025/09/24 21:41:11 | abarman | `/home/scratch.abarman_vlsi/agur/1NL/DQS/1NL_run1_SO/dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so` |  STA PNR FE_DCT |
| **eds** | QNS | 2025/04/02 15:59:49 | ysapojnikov | `/home/scratch.ysapojnikov_vlsi_1/agur/eds/eds_rbv_2025_03_13_condb_int1_11_3_BE_TNL_snap` |  STA |
| **qcorer** | QNS | 2025/10/01 14:32:00 | daltman | `/home/scratch.daltman_vlsi/qcorer/qcorer_rbv_2025_09_02_1NL_snap_ref` |  STA |
| **tds** | QNS | 2025/10/10 07:26:36 | hsajwan | `/home/scratch.hsajwan_vlsi/agur/1NL/tds/tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |  STA FCL PNR |
| **bta** | TCB | 2025/10/16 15:35:44 | vliberchuk | `/home/scratch.vliberchuk_vlsi/agur/1nl/bta/bta_2025_09_25_Oct10` |  STA |
| **eri** | TCB | 2025/10/17 18:13:28 | hsajwan | `/home/scratch.hsajwan_vlsi/agur/1NL/ERI/eri_rbv_2025_09_28_timing_fixes_first_run` |  STA PNR |
| **hib** | TCB | 2025/10/11 11:33:58 | maximkr | `/home/scratch.maximkr_vlsi/agur/hib/hib_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_fp2` |  STA FCL |

---

*Document Auto-Generated from Block Release Logs*  
*Generation Date: 2025-10-18 19:32:31*  
*Script: extract_agur_releases.sh*  
*Base Path: /home/agur_backend_blockRelease/block/*

## Notes

- All 5 CPORT units have both STA and FCL releases pointing to the same directory (combined release)
- Source workarea paths are extracted from the `db_source` line in block_release.log
- Flags indicate which types of files were included in each release
- Previous releases are tracked via `prev_last_sta_rel` symbolic links

