# Agur Project - All Chiplet Block Releases

## Overview
This document tracks the latest block releases for all units across all chiplets in the AGUR project.

**Total Units**: 73  
**Total Chiplets**: 7  
**Last Updated**: 2025-11-17 06:00:02

### Chiplet Breakdown
- **HIOPL**: 5 units (hiopl, ioplca, ioplcb, ioplcc, ioplcd)
- **CPORT**: 5 units (fdb, fth, lnd, pmux, prt)
- **HPORT**: 6 units (ccorea, ccoreb, ccorec, ccored, ccoree, ccoref)
- **NDQ**: 27 units (clt, cscore, dcmp, fdbm, fdbs, fthm, ftos, fwam, fwas, glc, iopl, ioplm, iopx, ir, lndm, nvrisc, pmuxm, prtm, psca, pscb, pscc, pscd, px, riba, ribs, sma, yu)
- **QNS**: 20 units (dqaa, dqaci, dqaco, dqai, dqamci, dqamco, dqamdi, dqamdo, dqap, dqavi, dqavo, dqax, dql, dqs, eds, qcorei, qcorer, tecorel, tecorer, tds)
- **TCB**: 4 units (alm, bta, eri, hib)
- **TOP_YC**: 6 units (top_yc_clock, top_yc_gpio, yc_clock_macro, yc_fuse, yc_fuse_macro, yu_mng)

## Release Tracking Method
- **STA Releases**: Tracked via `last_sta_rel` symbolic link
- **FCL Releases**: Tracked via `fcl_release` symbolic link  
- **Previous STA**: Tracked via `prev_last_sta_rel` symbolic link
- **Source**: `/home/agur_backend_blockRelease/block/{unit}/logs/block_release.log`

---

# Chiplet: HIOPL

## Unit: hiopl

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/07/28 08:46:49 |
| **Release User** | yshlush |
| **Workarea Name** | `hiopl_condb_int1_52_2r1` |
| **Source Workarea Path** | `/home/scratch.yshlush_vlsi/hiopl/hiopl_condb_int1_52_2r1/export/export_icc2` |
| **RTL Tag** | `export_icc2` |
| **Release Directory** | `hiopl_condb_int1_52_2r1__2025_7_28_8_46_49` |

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

## Unit: ioplca

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/03/25 16:54:53 |
| **Release User** | ysapojnikov |
| **Workarea Name** | `ioplca_rbv_2024_03_17_starling_LO_fe_silver_new_flp_ref_final_2` |
| **Source Workarea Path** | `/home/scratch.ysapojnikov_vlsi/ioplca/ioplca_rbv_2024_03_17_starling_LO_fe_silver_new_flp_ref_final_2` |
| **RTL Tag** | `starling_LO_fe_silver_new_flp_ref` |
| **Release Directory** | `ioplca_rbv_2024_03_17_starling_LO_fe_silver_new_flp_ref_final_2__2025_3_25_16_54_53` |

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

## Unit: ioplcb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/03/15 08:54:54 |
| **Release User** | maximkr |
| **Workarea Name** | `ioplcb_rbv_2024_03_17_starling_LO_fe_silver_PD_fix_ref_uphy` |
| **Source Workarea Path** | `/home/scratch.maximkr_vlsi/starling/ioplcb/ioplcb_rbv_2024_03_17_starling_LO_fe_silver_PD_fix_ref_uphy` |
| **RTL Tag** | `starling_LO_fe_silver_PD` |
| **Release Directory** | `ioplcb_rbv_2024_03_17_starling_LO_fe_silver_PD_fix_ref_uphy__2025_3_15_8_54_54` |

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

## Unit: ioplcc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/03/17 14:02:53 |
| **Release User** | roir |
| **Workarea Name** | `ioplcc_rbv_2024_03_17_starling_LO_fe_silver_NewUphy` |
| **Source Workarea Path** | `/home/scratch.roir_vlsi_1/starling/ioplcc/ioplcc_rbv_2024_03_17_starling_LO_fe_silver_NewUphy` |
| **RTL Tag** | `starling_LO_fe_silver_NewUphy` |
| **Release Directory** | `ioplcc_rbv_2024_03_17_starling_LO_fe_silver_NewUphy__2025_3_17_14_2_53` |

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

## Unit: ioplcd

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/07/08 11:56:00 |
| **Release User** | ysapojnikov |
| **Workarea Name** | `ioplcd_rbv_2024_03_17_starling_LO_fe_silver_ref_new_flp_2` |
| **Source Workarea Path** | `/home/scratch.ysapojnikov_vlsi/ioplcd/ioplcd_rbv_2024_03_17_starling_LO_fe_silver_ref_new_flp_2` |
| **RTL Tag** | `starling_LO_fe_silver_ref_new_flp_2` |
| **Release Directory** | `ioplcd_rbv_2024_03_17_starling_LO_fe_silver_ref_new_flp_2__2025_7_8_11_56_0` |

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


# Chiplet: CPORT

## Unit: fdb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/12 09:47:58 |
| **Release User** | dkolesnikov |
| **Workarea Name** | `fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1` |
| **Source Workarea Path** | `/home/scratch.dkolesnikov_vlsi/agur/fdb/1NL/fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1` |
| **RTL Tag** | `fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1__2025_11_12_9_47_58` |

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
| **Release Timestamp** | 2025/11/11 19:26:54 |
| **Release Directory** | `fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__flp_06_11__2025_11_11_19_26_54` |

---

## Unit: fth

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/12 12:55:33 |
| **Release User** | lmustafa |
| **Workarea Name** | `fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run` |
| **Source Workarea Path** | `/home/scratch.lmustafa_vlsi/agur/fth/fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run` |
| **RTL Tag** | `fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run__2025_11_12_12_55_33` |

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
| **Release Timestamp** | 2025/11/06 12:03:29 |
| **Release Directory** | `fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run__2025_11_6_12_3_29` |

---

## Unit: lnd

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 22:01:15 |
| **Release User** | shlomoc |
| **Workarea Name** | `run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi/agur/lnd/run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065` |
| **RTL Tag** | `lnd_rbv_2025_09_26_trex_response_tag` |
| **Release Directory** | `run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065__2025_11_16_22_1_15` |

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
| **Release Timestamp** | 2025/11/12 14:58:31 |
| **Release Directory** | `run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065__2025_11_12_14_58_31` |

---

## Unit: pmux

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/12 09:44:36 |
| **Release User** | brachas |
| **Workarea Name** | `pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |
| **RTL Tag** | `pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10__2025_11_12_9_44_36` |

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
| **Release Timestamp** | 2025/11/06 19:20:32 |
| **Release Directory** | `pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10__2025_11_6_19_20_32` |

---

## Unit: prt

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 18:11:44 |
| **Release User** | ykatzav |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_rabin_flp/pnr_flow/nv_flow/prt/ipo1020/nbu_signoff` |
| **RTL Tag** | `prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_rabin_flp_ipo1020_2025_11_13_18_11_44` |

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
| **Release Timestamp** | 2025/11/13 17:31:59 |
| **Release Directory** | `prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap__2025_11_13_17_31_59` |

---


# Chiplet: HPORT

## Unit: ccorea

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/12 23:42:08 |
| **Release User** | arcohen |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.arcohen_vlsi_1/agur/channels/ccorea/ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref_COPY_COPY/pnr_flow/nv_flow/ccorea/ipo1006/nbu_signoff` |
| **RTL Tag** | `ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref_COPY_COPY_ipo1006_2025_11_12_23_42_8` |

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
| **Release Timestamp** | 2025/11/08 17:57:47 |
| **Release Directory** | `nbu_signoff_ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref_COPY_COPY_ipo1005_2025_11_8_17_57_47` |

---

## Unit: ccoreb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 17:53:47 |
| **Release User** | arcohen |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.arcohen_vlsi_1/agur/channels/ccoreb/ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__copy_COPY/pnr_flow/nv_flow/ccoreb/ipo1005/nbu_signoff` |
| **RTL Tag** | `ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__copy_COPY_ipo1005_2025_11_13_17_53_47` |

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
| **Release Timestamp** | 2025/11/07 10:31:56 |
| **Release Directory** | `nbu_signoff_ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__copy_COPY_ipo1004_2025_11_7_10_31_56` |

---

## Unit: ccorec

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 19:00:10 |
| **Release User** | dkolesnikov |
| **Workarea Name** | `ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__roi_ref` |
| **Source Workarea Path** | `/home/scratch.dkolesnikov_vlsi_1/agur/ccorec/1NL/ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__roi_ref` |
| **RTL Tag** | `ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__roi_ref__2025_11_13_19_0_10` |

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
| **Release Timestamp** | 2025/11/06 22:01:11 |
| **Release Directory** | `ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__roi_ref__2025_11_6_22_1_11` |

---

## Unit: ccored

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 15:25:52 |
| **Release User** | brachas |
| **Workarea Name** | `ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi_1/agur/1NL/ccored/ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |
| **RTL Tag** | `ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy__2025_11_13_15_25_52` |

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
| **Release Timestamp** | 2025/11/06 21:51:11 |
| **Release Directory** | `ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy__2025_11_6_21_51_11` |

---

## Unit: ccoree

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 18:10:19 |
| **Release User** | ykatzav |
| **Workarea Name** | `ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |
| **Source Workarea Path** | `/home/scratch.ykatzav_vlsi_1/agur/ccoree/ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |
| **RTL Tag** | `ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy__2025_11_13_18_10_19` |

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
| **Release Timestamp** | 2025/11/06 22:26:48 |
| **Release Directory** | `ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy__2025_11_6_22_26_48` |

---

## Unit: ccoref

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/12 20:47:02 |
| **Release User** | brachas |
| **Workarea Name** | `ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi_1/agur/1NL/ccoref/ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |
| **RTL Tag** | `ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy__2025_11_12_20_47_2` |

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
| **Release Timestamp** | 2025/11/06 19:47:30 |
| **Release Directory** | `ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy__2025_11_6_19_47_30` |

---


# Chiplet: NDQ

## Unit: clt

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/09 11:07:16 |
| **Release User** | aamsalem |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.aamsalem_vlsi/agur/clt/1NL/run_2_11/clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_3_11/pnr_flow/nv_flow/clt/ipo1021/nbu_signoff` |
| **RTL Tag** | `clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_3_11_ipo1021_2025_11_9_11_7_16` |

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
| **Release Timestamp** | 2025/10/23 11:29:40 |
| **Release Directory** | `clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_part3__2025_10_23_11_29_40` |

---

## Unit: cscore

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 11:32:57 |
| **Release User** | ynaim |
| **Workarea Name** | `cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_lockup_vivid` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi/agur/1NL/cscore/cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_lockup_vivid` |
| **RTL Tag** | `cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_lockup_vivid__2025_11_16_11_32_57` |

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
| **Release Timestamp** | 2025/11/06 19:03:30 |
| **Release Directory** | `cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_lockup_vivid__2025_11_6_19_3_30` |

---

## Unit: dcmp

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 13:57:05 |
| **Release User** | rmenasheof |
| **Workarea Name** | `dcmp_manual_flp_21_9_for_vivid` |
| **Source Workarea Path** | `/home/scratch.rmenasheof_vlsi/agur/dcmp/dcmp_manual_flp_21_9_for_vivid` |
| **RTL Tag** | `dcmp_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dcmp_manual_flp_21_9_for_vivid__2025_11_16_13_57_5` |

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
| **Release Timestamp** | 2025/11/09 18:31:47 |
| **Release Directory** | `dcmp_2_11_closer_flp_6x6_script_against_short_ipo1003_newgolden__2025_11_9_18_31_47` |

---

## Unit: fdbm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/14 14:11:28 |
| **Release User** | dkolesnikov |
| **Workarea Name** | `fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1` |
| **Source Workarea Path** | `/home/scratch.dkolesnikov_vlsi/agur/fdbm/1NL/fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1` |
| **RTL Tag** | `fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1__2025_11_14_14_11_28` |

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
| **Release Timestamp** | 2025/11/13 09:06:46 |
| **Release Directory** | `fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__nov4_tpi__2025_11_13_9_6_46` |

---

## Unit: fdbs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 12:40:39 |
| **Release User** | brachas |
| **Workarea Name** | `fdbs_eco_imp_2025_10_19_17_25` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi/agur/1NL/fdbs/fdbs_eco_imp_2025_10_19_17_25` |
| **RTL Tag** | `fdbs_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fdbs_eco_imp_2025_10_19_17_25__2025_11_16_12_40_39` |

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
| **Release Timestamp** | 2025/11/06 14:37:05 |
| **Release Directory** | `fdbs_eco_imp_2025_10_19_17_25__2025_11_6_14_37_5` |

---

## Unit: fthm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 13:26:34 |
| **Release User** | ayerushalmy |
| **Workarea Name** | `fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3` |
| **Source Workarea Path** | `/home/scratch.ayerushalmy_vlsi/agur/fthm/1NL/fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3` |
| **RTL Tag** | `fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3__2025_11_16_13_26_34` |

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
| **Release Timestamp** | 2025/11/09 09:55:21 |
| **Release Directory** | `fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3_4__2025_11_9_9_55_21` |

---

## Unit: ftos

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/09 11:06:48 |
| **Release User** | thadad |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.thadad_vlsi_1/agur/1NL/ftos/condb_int3_2025_08_27_0_1NL_snap_th/pnr_flow/nv_flow/ftos/ipo1000/nbu_signoff` |
| **RTL Tag** | `ftos_rbv_2025_09_04_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_condb_int3_2025_08_27_0_1NL_snap_th_ipo1000_2025_11_9_11_6_48` |

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
| **Release Timestamp** | 2025/11/09 10:49:33 |
| **Release Directory** | `condb_int3_2025_08_27_0_1NL_snap_th__2025_11_9_10_49_33` |

---

## Unit: fwam

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/09 11:29:44 |
| **Release User** | zbirman |
| **Workarea Name** | `run_19_10_2025__fwam_rbv_2025_09_07_GOLDEN_no_xcap_NDR` |
| **Source Workarea Path** | `/home/scratch.zbirman_vlsi/agur/fwam/run_19_10_2025__fwam_rbv_2025_09_07_GOLDEN_no_xcap_NDR` |
| **RTL Tag** | `fwam_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `run_19_10_2025__fwam_rbv_2025_09_07_GOLDEN_no_xcap_NDR__2025_11_9_11_29_44` |

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
| **Release Timestamp** | 2025/10/29 19:14:32 |
| **Release Directory** | `run_15_09_2025_fwam_rbv_2025_09_07_4x6_clock_tree_Tzlil_Hook_for_vivid__2025_10_29_19_14_32` |

---

## Unit: fwas

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 13:55:47 |
| **Release User** | rmenasheof |
| **Workarea Name** | `fwas_golden_ipo4_21_9_for_vivid` |
| **Source Workarea Path** | `/home/scratch.rmenasheof_vlsi/agur/fwas/fwas_golden_ipo4_21_9_for_vivid` |
| **RTL Tag** | `fwas_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fwas_golden_ipo4_21_9_for_vivid__2025_11_16_13_55_47` |

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
| **Release Timestamp** | 2025/11/09 17:44:19 |
| **Release Directory** | `fwas_5_11_flp_closer_moved_i1_bbox_ipo1002_with_anti_short_hook_to_realse__2025_11_9_17_44_19` |

---

## Unit: glc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 21:07:59 |
| **Release User** | ynaim |
| **Workarea Name** | `glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi_1/agur/1NL/glc/glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid` |
| **RTL Tag** | `glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid__2025_11_16_21_7_59` |

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
| **Release Timestamp** | 2025/11/10 08:56:27 |
| **Release Directory** | `glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_0.60__2025_11_10_8_56_27` |

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

## Unit: ir

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 17:55:52 |
| **Release User** | thadad |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.thadad_vlsi/agur/1NL/ir/ir_rbv_2025_10_19_agur_issu128_util/pnr_flow/nv_flow/ir/ipo1002/nbu_signoff` |
| **RTL Tag** | `ir_rbv_2025_10_19_agur_issu128` |
| **Release Directory** | `nbu_signoff_ir_rbv_2025_10_19_agur_issu128_util_ipo1002_2025_11_13_17_55_52` |

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
| **Release Timestamp** | 2025/11/09 09:44:07 |
| **Release Directory** | `ir_rbv_2025_10_19_agur_issu128__2025_11_9_9_44_7` |

---

## Unit: lndm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 16:06:13 |
| **Release User** | shlomoc |
| **Workarea Name** | `run_07_09_2025_lndm_rbv_2025_09_01_new_flow` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi/agur/lndm/run_07_09_2025_lndm_rbv_2025_09_01_new_flow` |
| **RTL Tag** | `lndm_rbv_2025_09_01_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `run_07_09_2025_lndm_rbv_2025_09_01_new_flow__2025_11_16_16_6_13` |

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
| **Release Timestamp** | 2025/11/06 16:48:51 |
| **Release Directory** | `nbu_signoff_run_27_10_25_lndm_rbv_2025_09_01_ipo1000_2025_11_6_16_48_51` |

---

## Unit: nvrisc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/09 09:28:57 |
| **Release User** | ykatzav |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ykatzav_vlsi/agur/nvrisc/nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2_PI/pnr_flow/nv_flow/nvrisc/ipo1020/nbu_signoff` |
| **RTL Tag** | `nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2_PI_ipo1020_2025_11_9_9_28_57` |

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
| **Release Timestamp** | 2025/11/09 09:10:02 |
| **Release Directory** | `nbu_signoff_nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2_PI_ipo1020_2025_11_9_9_10_2` |

---

## Unit: pmuxm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/09 11:27:36 |
| **Release User** | zbirman |
| **Workarea Name** | `run_15_10_pmuxm_rbv_2025_10_08_sram_size_80k_sram_resize_incremental` |
| **Source Workarea Path** | `/home/scratch.zbirman_vlsi/agur/pmuxm/run_15_10_pmuxm_rbv_2025_10_08_sram_size_80k_sram_resize_incremental` |
| **RTL Tag** | `pmuxm_rbv_2025_10_08_agur_sram_size_80k` |
| **Release Directory** | `run_15_10_pmuxm_rbv_2025_10_08_sram_size_80k_sram_resize_incremental__2025_11_9_11_27_36` |

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
| **Release Timestamp** | 2025/10/29 16:33:52 |
| **Release Directory** | `run_15_10_pmuxm_rbv_2025_09_03_release_sep10__2025_10_29_16_33_52` |

---

## Unit: prtm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/06 15:11:14 |
| **Release User** | lmustafa |
| **Workarea Name** | `prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry` |
| **Source Workarea Path** | `/home/scratch.lmustafa_vlsi/agur/prtm/prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry` |
| **RTL Tag** | `prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1` |
| **Release Directory** | `prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry__2025_11_6_15_11_14` |

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
| **Release Timestamp** | 2025/11/06 11:59:42 |
| **Release Directory** | `prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry__2025_11_6_11_59_42` |

---

## Unit: psca

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 10:17:46 |
| **Release User** | nkahaz |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.nkahaz_vlsi/ww38_5_fixes/psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_ref/pnr_flow/nv_flow/psca/ipo1050/nbu_signoff` |
| **RTL Tag** | `psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_ref_ipo1050_2025_11_16_10_17_46` |

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
| **Release Timestamp** | 2025/11/06 15:34:53 |
| **Release Directory** | `nbu_signoff_psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_ref_ipo1049_2025_11_6_15_34_53` |

---

## Unit: pscb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/06 11:18:37 |
| **Release User** | nkahaz |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.nkahaz_vlsi/ww38_5_fixes/pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ref/pnr_flow/nv_flow/pscb/ipo1048/nbu_signoff` |
| **RTL Tag** | `pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ref_ipo1048_2025_11_6_11_18_37` |

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
| **Release Timestamp** | 2025/11/06 10:56:34 |
| **Release Directory** | `nbu_signoff_pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ref_ipo1048_2025_11_6_10_56_34` |

---

## Unit: pscc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/07 06:59:08 |
| **Release User** | dtraitelovic |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.dtraitelovic_vlsi/agur/pscc/pscc_2025_09_02_1NL_snap_new_flow_flp_cdc/pnr_flow/nv_flow/pscc/ipo1007/nbu_signoff` |
| **RTL Tag** | `pscc_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_pscc_2025_09_02_1NL_snap_new_flow_flp_cdc_ipo1007_2025_11_7_6_59_8` |

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
| **Release Timestamp** | 2025/10/30 09:47:22 |
| **Release Directory** | `nbu_signoff_pscc_2025_09_02_1NL_snap_new_flow_flp_cdc_ipo1006_2025_10_30_9_47_22` |

---

## Unit: pscd

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 10:19:33 |
| **Release User** | gibell |
| **Workarea Name** | `pscd_rbv_2025_09_02_ver4_Sep25_gb` |
| **Source Workarea Path** | `/home/scratch.gibell_vlsi/agur/1nl/pscd/pscd_rbv_2025_09_02_ver4_Sep25_gb` |
| **RTL Tag** | `pscd_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `pscd_rbv_2025_09_02_ver4_Sep25_gb__2025_11_16_10_19_33` |

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
| **Release Timestamp** | 2025/11/10 12:09:47 |
| **Release Directory** | `nbu_signoff_pscd_rbv_2025_10_22_Oct25_ver2_gb_ipo1005_2025_11_10_12_9_47` |

---

## Unit: px

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 10:48:39 |
| **Release User** | aamsalem |
| **Workarea Name** | `px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65` |
| **Source Workarea Path** | `/home/scratch.aamsalem_vlsi/agur/px/1NL/run_9_9_old_util65/px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65` |
| **RTL Tag** | `px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65__2025_11_16_10_48_39` |

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
| **Release Timestamp** | 2025/11/09 09:50:44 |
| **Release Directory** | `nbu_signoff_px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_new_flow_8_10_ipo1019_2025_11_9_9_50_44` |

---

## Unit: riba

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 13:56:14 |
| **Release User** | rmenasheof |
| **Workarea Name** | `riba_10_9_1nl_new_flow_golden` |
| **Source Workarea Path** | `/home/scratch.rmenasheof_vlsi/agur/riba/riba_10_9_1nl_new_flow_golden` |
| **RTL Tag** | `riba_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `riba_10_9_1nl_new_flow_golden__2025_11_16_13_56_14` |

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
| **Release Timestamp** | 2025/11/09 16:26:44 |
| **Release Directory** | `nbu_signoff_riba_26_10_drc_fixing_test_blockage_route_and_placement_ipo1000_2025_11_9_16_26_44` |

---

## Unit: ribs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 11:23:52 |
| **Release User** | ynaim |
| **Workarea Name** | `ribs.ribs_rbv_2025_10_20_agur_condb_int3_2025_08_31_0_no_split_fifo_with_bypass_0_inff_1_vivid` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi_1/agur/1NL/ribs/ribs.ribs_rbv_2025_10_20_agur_condb_int3_2025_08_31_0_no_split_fifo_with_bypass_0_inff_1_vivid` |
| **RTL Tag** | `ribs_rbv_2025_10_20_agur_condb_int3_2025_08_31_0_no_split_fifo_with_bypass_0_inff_1` |
| **Release Directory** | `ribs.ribs_rbv_2025_10_20_agur_condb_int3_2025_08_31_0_no_split_fifo_with_bypass_0_inff_1_vivid__2025_11_16_11_23_52` |

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
| **Release Timestamp** | 2025/11/06 10:57:23 |
| **Release Directory** | `ribs.ribs_rbv_2025_10_20_agur_condb_int3_2025_08_31_0_no_split_fifo_with_bypass_0_inff_1_vivid__2025_11_6_10_57_23` |

---

## Unit: sma

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 16:08:48 |
| **Release User** | shlomoc |
| **Workarea Name** | `run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi/agur/sma/run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix` |
| **RTL Tag** | `sma_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix__2025_11_16_16_8_48` |

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
| **Release Timestamp** | 2025/11/08 17:17:52 |
| **Release Directory** | `nbu_signoff_run_2_11_25_sma_rbv_2025_09_04_ipo1001_2025_11_8_17_17_52` |

---

## Unit: yu

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 19:51:31 |
| **Release User** | ashahock |
| **Workarea Name** | `yu_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_ver5_lib_fix` |
| **Source Workarea Path** | `/home/scratch.ashahock_vlsi/agur/yu/yu_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_ver5_lib_fix` |
| **RTL Tag** | `yu_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `yu_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_ver5_lib_fix__2025_11_16_19_51_31` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/10 11:44:37 |
| **Release Directory** | `yu_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_ver5_lib_fix__2025_11_10_11_44_37` |

---


# Chiplet: QNS

## Unit: dqaa

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 16:05:53 |
| **Release User** | siddharthasa |
| **Workarea Name** | `dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_final` |
| **Source Workarea Path** | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqaa/dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_final` |
| **RTL Tag** | `dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_final__2025_11_13_16_5_53` |

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
| **Release Timestamp** | 2025/11/09 04:50:38 |
| **Release Directory** | `dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_final__2025_11_9_4_50_38` |

---

## Unit: dqaci

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 14:35:02 |
| **Release User** | siddharthasa |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqaci/dqaci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel/signoff_flow/nv_gate_eco/dqaci/ipo1000/nbu_signoff` |
| **RTL Tag** | `dqaci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_dqaci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel_ipo1000_2025_11_13_14_35_2` |

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
| **Release Timestamp** | 2025/11/05 11:24:17 |
| **Release Directory** | `nbu_signoff_dqaci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel_ipo1000_2025_11_5_11_24_17` |

---

## Unit: dqaco

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 07:44:09 |
| **Release User** | gnarla |
| **Workarea Name** | `dqaco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_lat_pin_def` |
| **Source Workarea Path** | `/home/scratch.gnarla_vlsi_1/agur/1NL/dqaco/dqaco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_lat_pin_def` |
| **RTL Tag** | `dqaco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqaco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_lat_pin_def__2025_11_13_7_44_9` |

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
| **Release Timestamp** | 2025/11/05 14:26:06 |
| **Release Directory** | `dqaco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_lat_pin_def__2025_11_5_14_26_6` |

---

## Unit: dqai

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 11:55:13 |
| **Release User** | mlanzerer |
| **Workarea Name** | `fix_tag_1nl` |
| **Source Workarea Path** | `/home/scratch.mlanzerer_vlsi/dqai_dir/fix_tag_1nl` |
| **RTL Tag** | `dqai_rbv_2025_10_08_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `fix_tag_1nl__2025_11_16_11_55_13` |

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
| **Release Timestamp** |  |
| **Release Directory** | `fix_tag_1nl__2025_11_15_18_45_52` |

---

## Unit: dqamci

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 08:52:52 |
| **Release User** | mlanzerer |
| **Workarea Name** | `dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.mlanzerer_vlsi/dqamci_dir/dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap__2025_11_13_8_52_52` |

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
| **Release Timestamp** | 2025/11/05 18:31:45 |
| **Release Directory** | `dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap__2025_11_5_18_31_45` |

---

## Unit: dqamco

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 14:27:43 |
| **Release User** | siddharthasa |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqamco/dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel/signoff_flow/nv_gate_eco/dqamco/ipo1000/nbu_signoff` |
| **RTL Tag** | `dqaci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel_ipo1001_2025_11_13_14_27_43` |

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
| **Release Timestamp** | 2025/11/05 12:09:14 |
| **Release Directory** | `nbu_signoff_dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel_ipo1001_2025_11_5_12_9_14` |

---

## Unit: dqamdi

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 17:18:16 |
| **Release User** | seeman |
| **Workarea Name** | `dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si_dsr` |
| **Source Workarea Path** | `/home/scratch.seeman_vlsi_1/agur/1nl/dqamdi/dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si_dsr` |
| **RTL Tag** | `dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si_dsr__2025_11_13_17_18_16` |

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
| **Release Timestamp** | 2025/11/06 07:52:32 |
| **Release Directory** | `dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si_dsr__2025_11_6_7_52_32` |

---

## Unit: dqamdo

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 18:23:21 |
| **Release User** | abarman |
| **Workarea Name** | `dqamdo_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_vivideco` |
| **Source Workarea Path** | `/home/scratch.abarman_vlsi/agur/1NL/DQAMO_NEW/1NL_run2_scan_VIVID_ECO/dqamdo_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_vivideco` |
| **RTL Tag** | `dqamdo_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqamdo_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_vivideco__2025_11_13_18_23_21` |

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
| **Release Timestamp** | 2025/11/06 03:23:46 |
| **Release Directory** | `dqamdo_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_vivideco__2025_11_6_3_23_46` |

---

## Unit: dqap

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 18:23:59 |
| **Release User** | drazmizrahi |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.drazmizrahi_vlsi/dqap/dqap_copy_from_tal/pnr_flow/nv_flow/dqap/ipo1013_chiplet_4_eco/nbu_signoff` |
| **RTL Tag** | `dqap_rbv_2025_09_05_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_dqap_copy_from_tal_ipo1013_2025_11_13_18_23_59` |

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
| **Release Timestamp** | 2025/11/05 09:31:09 |
| **Release Directory** | `nbu_signoff_dqap_copy_from_tal_ipo1011_2025_11_5_9_31_9` |

---

## Unit: dqavi

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 10:40:17 |
| **Release User** | abarman |
| **Workarea Name** | `dqavi_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_eco` |
| **Source Workarea Path** | `/home/scratch.abarman_vlsi/agur/1NL/DQAVI/1NL_run1_eco/dqavi_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_eco` |
| **RTL Tag** | `dqavi_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqavi_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_eco__2025_11_13_10_40_17` |

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
| **Release Timestamp** | 2025/11/05 22:22:19 |
| **Release Directory** | `dqavi_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_eco__2025_11_5_22_22_19` |

---

## Unit: dqavo

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 08:58:17 |
| **Release User** | gnarla |
| **Workarea Name** | `dqavo_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_path_groups` |
| **Source Workarea Path** | `/home/scratch.gnarla_vlsi_1/agur/1NL/dqavo/dqavo_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_path_groups` |
| **RTL Tag** | `dqavo_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqavo_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_path_groups__2025_11_13_8_58_17` |

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
| **Release Timestamp** | 2025/11/13 07:36:01 |
| **Release Directory** | `dqavo_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snaplat_sram_fix__2025_11_13_7_36_1` |

---

## Unit: dqax

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/12 22:33:43 |
| **Release User** | hmendelovich |
| **Workarea Name** | `dqax_from_matan2` |
| **Source Workarea Path** | `/home/scratch.hmendelovich_vlsi/dqax_from_matan2` |
| **RTL Tag** | `dqax_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `dqax_from_matan2__2025_11_12_22_33_43` |

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
| **Release Timestamp** | 2025/11/05 09:59:52 |
| **Release Directory** | `dqax_from_matan2__2025_11_5_9_59_52` |

---

## Unit: dql

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 17:23:00 |
| **Release User** | aazran |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.aazran_vlsi/dql/040925_1nl_reff_fixed_v0/pnr_flow/nv_flow/dql/ipo1005/nbu_signoff` |
| **RTL Tag** | `dql_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_040925_1nl_reff_fixed_v0_ipo1005_2025_11_13_17_23_0` |

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
| **Release Timestamp** | 2025/11/13 17:01:34 |
| **Release Directory** | `nbu_signoff_040925_1nl_reff_fixed_v0_ipo1005_2025_11_13_17_1_34` |

---

## Unit: dqs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 10:43:14 |
| **Release User** | abarman |
| **Workarea Name** | `dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so` |
| **Source Workarea Path** | `/home/scratch.abarman_vlsi/agur/1NL/DQS/1NL_run1_SO/dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so` |
| **RTL Tag** | `dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap` |
| **Release Directory** | `dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so__2025_11_13_10_43_14` |

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
| **Release Timestamp** | 2025/11/13 08:57:26 |
| **Release Directory** | `dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so__2025_11_13_8_57_26` |

---

## Unit: eds

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 22:16:47 |
| **Release User** | eelgabsi |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.eelgabsi_vlsi/AGUR/PARTITIONS/1nl/qns/eds/eds_rbv_2025_10_06_agur_condb_int3_2025_08_27_0_r0/pnr_flow/nv_flow/eds/ipo1010_eco4/nbu_signoff` |
| **RTL Tag** | `eds_rbv_2025_10_06_agur_condb_int3_2025_08_27_0_r0` |
| **Release Directory** | `nbu_signoff_eds_rbv_2025_10_06_agur_condb_int3_2025_08_27_0_r0_ipo1010_2025_11_13_22_16_47` |

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
| **Release Timestamp** | 2025/11/05 11:42:52 |
| **Release Directory** | `nbu_signoff_eds_rbv_2025_10_06_agur_condb_int3_2025_08_27_0_r0_ipo1008_2025_11_5_11_42_52` |

---

## Unit: qcorel

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 10:19:52 |
| **Release User** | ronil |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ronil_vlsi_1/agur/qcorel/qcorel_l0_21_10_25_new_scratch/pnr_flow/nv_flow/qcorel/ipo1006/nbu_signoff` |
| **RTL Tag** | `qcorel_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_qcorel_l0_21_10_25_new_scratch_ipo1006_2025_11_16_10_19_52` |

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
| **Release Timestamp** | 2025/11/16 10:17:20 |
| **Release Directory** | `nbu_signoff_qcorel_l0_21_10_25_ipo1004_2025_11_16_10_17_20` |

---

## Unit: qcorer

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/11 09:59:05 |
| **Release User** | ronil |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ronil_vlsi/qcorer/qcorer_r2_21_10_25_tpi/pnr_flow/nv_flow/qcorer/ipo1012/nbu_signoff` |
| **RTL Tag** | `qcorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_qcorer_r2_21_10_25_tpi_ipo1012_2025_11_11_9_59_5` |

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
| **Release Timestamp** | 2025/11/11 09:54:49 |
| **Release Directory** | `nbu_signoff_qcorer_r0_19_10_25_new_scratch_ipo1005_2025_11_11_9_54_49` |

---

## Unit: tecorel

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 07:16:03 |
| **Release User** | gnarla |
| **Workarea Name** | `tecorel_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_default_run` |
| **Source Workarea Path** | `/home/scratch.gnarla_vlsi/agur/1NL/tecorel/tecorel_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_default_run` |
| **RTL Tag** | `tecorel_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `tecorel_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_default_run__2025_11_13_7_16_3` |

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
| **Release Timestamp** | 2025/11/05 14:27:21 |
| **Release Directory** | `tecorel_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_default_run__2025_11_5_14_27_21` |

---

## Unit: tecorer

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 10:30:20 |
| **Release User** | hsajwan |
| **Workarea Name** | `tecorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |
| **Source Workarea Path** | `/home/scratch.hsajwan_vlsi/agur/1NL/tecorer/tecorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |
| **RTL Tag** | `tecorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `tecorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN__2025_11_13_10_30_20` |

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
| **Release Timestamp** | 2025/11/05 12:29:14 |
| **Release Directory** | `tecorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN__2025_11_5_12_29_14` |

---

## Unit: tds

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 10:29:37 |
| **Release User** | hsajwan |
| **Workarea Name** | `tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |
| **Source Workarea Path** | `/home/scratch.hsajwan_vlsi/agur/1NL/tds/tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |
| **RTL Tag** | `tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN__2025_11_13_10_29_37` |

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
| **Release Timestamp** | 2025/11/05 12:28:49 |
| **Release Directory** | `tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN__2025_11_5_12_28_49` |

---


# Chiplet: TCB

## Unit: alm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/11 18:08:57 |
| **Release User** | tmazor |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.tmazor_vlsi/agur/agur_alm_rbv_2025_10_09/pnr_flow/nv_flow/alm/ipo1005/nbu_signoff` |
| **RTL Tag** | `agur_alm_rbv_2025_10_09` |
| **Release Directory** | `nbu_signoff_agur_alm_rbv_2025_10_09_ipo1005_2025_11_11_18_8_57` |

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
| **Release Timestamp** | 2025/11/06 08:53:32 |
| **Release Directory** | `nbu_signoff_agur_alm_rbv_2025_10_09_ipo1004_2025_11_6_8_53_32` |

---

## Unit: bta

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/11 11:45:58 |
| **Release User** | vliberchuk |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.vliberchuk_vlsi/agur/1nl/bta/bta_2025_10_28_Oct28_Timing/pnr_flow/nv_flow/bta/ipo1085_vchiplet_ptfix_of1078_ofp/nbu_signoff` |
| **RTL Tag** | `bta_rbv_2025_10_28_agur_condb_int3_2025_08_27_0_1NL_snap_85p_timing_lnkl` |
| **Release Directory** | `nbu_signoff_bta_2025_10_28_Oct28_Timing_ipo1085_2025_11_11_11_45_58` |

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
| **Release Timestamp** | 2025/11/05 22:52:13 |
| **Release Directory** | `nbu_signoff_bta_2025_10_28_Oct28_Timing_ipo1078_2025_11_5_22_52_13` |

---

## Unit: eri

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/11 16:03:15 |
| **Release User** | hsajwan |
| **Workarea Name** | `eri_rbv_2025_09_28_timing_fixes_first_run` |
| **Source Workarea Path** | `/home/scratch.hsajwan_vlsi/agur/1NL/ERI/eri_rbv_2025_09_28_timing_fixes_first_run` |
| **RTL Tag** | `eri_rbv_2025_09_28_timing_fixes` |
| **Release Directory** | `eri_rbv_2025_09_28_timing_fixes_first_run__2025_11_11_16_3_15` |

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
| **Release Timestamp** | 2025/11/06 07:31:05 |
| **Release Directory** | `eri_rbv_2025_09_28_timing_fixes_first_run__2025_11_6_7_31_5` |

---

## Unit: hib

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/11 16:33:30 |
| **Release User** | tmazor |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.tmazor_vlsi/agur/hib_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap/pnr_flow/nv_flow/hib/ipo1005/nbu_signoff` |
| **RTL Tag** | `hib_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `nbu_signoff_hib_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_ipo1005_2025_11_11_16_33_30` |

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
| **Release Timestamp** | 2025/11/05 22:00:43 |
| **Release Directory** | `nbu_signoff_hib_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_ipo1004_2025_11_5_22_0_43` |

---


# Chiplet: TOP_YC

## Unit: top_yc_clock

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2024/07/22 23:13:27 |
| **Release User** | abeinhorn |
| **Workarea Name** | `top_yc_clock_sunbird_rbv_2023_05_21_FNL` |
| **Source Workarea Path** | `/home/starling_backend_blockData/top_yc_clock/top_yc_clock_sunbird_rbv_2023_05_21_FNL` |
| **RTL Tag** | `top_yc_clock_sunbird_rbv_2023_05_21_FNL` |
| **Release Directory** | `full_release` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** |  | Front End DCT |
| **DC** |  | Design Compiler synthesis |
| **Full** | True | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

---

## Unit: top_yc_gpio

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/12 16:25:43 |
| **Release User** | lschwartz |
| **Workarea Name** | `top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_new` |
| **Source Workarea Path** | `/home/scratch.lschwartz_vlsi/agur/top_yc_gpio/top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_new` |
| **RTL Tag** | `top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_new__2025_11_12_16_25_43` |

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
| **Release Timestamp** | 2025/11/04 09:59:28 |
| **Release Directory** | `top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_new__2025_11_4_9_59_28` |

---

## Unit: yc_clock_macro

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2024/07/22 23:13:39 |
| **Release User** | abeinhorn |
| **Workarea Name** | `top_yc_clock_sunbird_rbv_2023_05_21_FNL__20230624_sp6` |
| **Source Workarea Path** | `/home/starling_backend_blockData/yc_clock_macro/top_yc_clock_sunbird_rbv_2023_05_21_FNL__20230624_sp6` |
| **RTL Tag** | `top_yc_clock_sunbird_rbv_2023_05_21_FNL__20230624_sp6` |
| **Release Directory** | `full_release` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** |  | Front End DCT |
| **DC** |  | Design Compiler synthesis |
| **Full** | True | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/10/05 10:11:40 |
| **Release Directory** | `top_yc_clock_agur_rbv_2025_06_09_condb_int2_23_5r1_SFNL_snap_00__2025_10_5_10_11_40` |

---

## Unit: yc_fuse

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/16 10:23:53 |
| **Release User** | lhaiby |
| **Workarea Name** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.lhaiby_vlsi/Agur/yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |
| **RTL Tag** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |
| **Release Directory** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap__2025_11_16_10_23_53` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | False | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | False | Full release (all files) |

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/11 13:09:03 |
| **Release Directory** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap__2025_11_11_13_9_3` |

---

## Unit: yc_fuse_macro

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2024/07/22 14:49:01 |
| **Release User** | abeinhorn |
| **Workarea Name** | `yc_fuse_sunbird_rbv_2023_05_21` |
| **Source Workarea Path** | `/home/starling_backend_blockData/yc_fuse_macro/yc_fuse_sunbird_rbv_2023_05_21` |
| **RTL Tag** | `yc_fuse_sunbird_rbv_2023_05_21` |
| **Release Directory** | `full_release` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** |  | Front End DCT |
| **DC** |  | Design Compiler synthesis |
| **Full** | True | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

---

## Unit: yu_mng

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/13 22:42:48 |
| **Release User** | aspiegelglas |
| **Workarea Name** | `yu_mng_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_05` |
| **Source Workarea Path** | `/home/scratch.aspiegelglas_vlsi/Agur/yu_mng/yu_mng_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_05` |
| **RTL Tag** | `yu_mng_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `yu_mng_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_05__2025_11_13_22_42_48` |

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
| **Release Timestamp** | 2025/11/10 20:53:10 |
| **Release Directory** | `yu_mng_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_05__2025_11_10_20_53_10` |

---



## Summary Table

| Unit | Chiplet | Latest STA Timestamp | User | Source Workarea | Release Types |
|------|---------|---------------------|------|-----------------|---------------|
| **hiopl** | HIOPL | 2025/07/28 08:46:49 | yshlush | `/home/scratch.yshlush_vlsi/hiopl/hiopl_condb_int1_52_2r1/export/export_icc2` |  STA FCL |
| **ioplca** | HIOPL | 2025/03/25 16:54:53 | ysapojnikov | `/home/scratch.ysapojnikov_vlsi/ioplca/ioplca_rbv_2024_03_17_starling_LO_fe_silver_new_flp_ref_final_2` |  STA FCL |
| **ioplcb** | HIOPL | 2025/03/15 08:54:54 | maximkr | `/home/scratch.maximkr_vlsi/starling/ioplcb/ioplcb_rbv_2024_03_17_starling_LO_fe_silver_PD_fix_ref_uphy` |  STA FCL |
| **ioplcc** | HIOPL | 2025/03/17 14:02:53 | roir | `/home/scratch.roir_vlsi_1/starling/ioplcc/ioplcc_rbv_2024_03_17_starling_LO_fe_silver_NewUphy` |  STA FCL |
| **ioplcd** | HIOPL | 2025/07/08 11:56:00 | ysapojnikov | `/home/scratch.ysapojnikov_vlsi/ioplcd/ioplcd_rbv_2024_03_17_starling_LO_fe_silver_ref_new_flp_2` |  STA FCL |
| **fdb** | CPORT | 2025/11/12 09:47:58 | dkolesnikov | `/home/scratch.dkolesnikov_vlsi/agur/fdb/1NL/fdb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__floorplanChange_run1` |  STA FCL PNR |
| **fth** | CPORT | 2025/11/12 12:55:33 | lmustafa | `/home/scratch.lmustafa_vlsi/agur/fth/fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_new_tplanner_ref_run` |  STA FCL PNR |
| **lnd** | CPORT | 2025/11/16 22:01:15 | shlomoc | `/home/scratch.shlomoc_vlsi/agur/lnd/run_29_09_2025_lnd_rbv_2025_09_26_trex_response_tag_065` |  STA FCL |
| **pmux** | CPORT | 2025/11/12 09:44:36 | brachas | `/home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10` |  STA FCL |
| **prt** | CPORT | 2025/11/13 18:11:44 | ykatzav | `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_rabin_flp/pnr_flow/nv_flow/prt/ipo1020/nbu_signoff` |  STA |
| **ccorea** | HPORT | 2025/11/12 23:42:08 | arcohen | `/home/scratch.arcohen_vlsi_1/agur/channels/ccorea/ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref_COPY_COPY/pnr_flow/nv_flow/ccorea/ipo1006/nbu_signoff` |  STA FCL PNR FE_DCT |
| **ccoreb** | HPORT | 2025/11/13 17:53:47 | arcohen | `/home/scratch.arcohen_vlsi_1/agur/channels/ccoreb/ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__copy_COPY/pnr_flow/nv_flow/ccoreb/ipo1005/nbu_signoff` |  STA FCL PNR FE_DCT |
| **ccorec** | HPORT | 2025/11/13 19:00:10 | dkolesnikov | `/home/scratch.dkolesnikov_vlsi_1/agur/ccorec/1NL/ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__roi_ref` |  STA FCL PNR FE_DCT |
| **ccored** | HPORT | 2025/11/13 15:25:52 | brachas | `/home/scratch.brachas_vlsi_1/agur/1NL/ccored/ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |  STA FCL |
| **ccoree** | HPORT | 2025/11/13 18:10:19 | ykatzav | `/home/scratch.ykatzav_vlsi_1/agur/ccoree/ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |  STA FCL |
| **ccoref** | HPORT | 2025/11/12 20:47:02 | brachas | `/home/scratch.brachas_vlsi_1/agur/1NL/ccoref/ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` |  STA FCL |
| **clt** | NDQ | 2025/11/09 11:07:16 | aamsalem | `/home/scratch.aamsalem_vlsi/agur/clt/1NL/run_2_11/clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_3_11/pnr_flow/nv_flow/clt/ipo1021/nbu_signoff` |  STA FCL |
| **cscore** | NDQ | 2025/11/16 11:32:57 | ynaim | `/home/scratch.ynaim_vlsi/agur/1NL/cscore/cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_lockup_vivid` |  STA |
| **dcmp** | NDQ | 2025/11/16 13:57:05 | rmenasheof | `/home/scratch.rmenasheof_vlsi/agur/dcmp/dcmp_manual_flp_21_9_for_vivid` |  STA |
| **fdbm** | NDQ | 2025/11/14 14:11:28 | dkolesnikov | `/home/scratch.dkolesnikov_vlsi/agur/fdbm/1NL/fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__run1` |  STA FCL PNR |
| **fdbs** | NDQ | 2025/11/16 12:40:39 | brachas | `/home/scratch.brachas_vlsi/agur/1NL/fdbs/fdbs_eco_imp_2025_10_19_17_25` |  STA FCL |
| **fthm** | NDQ | 2025/11/16 13:26:34 | ayerushalmy | `/home/scratch.ayerushalmy_vlsi/agur/fthm/1NL/fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_V3` |  STA FCL PNR |
| **ftos** | NDQ | 2025/11/09 11:06:48 | thadad | `/home/scratch.thadad_vlsi_1/agur/1NL/ftos/condb_int3_2025_08_27_0_1NL_snap_th/pnr_flow/nv_flow/ftos/ipo1000/nbu_signoff` |  STA |
| **fwam** | NDQ | 2025/11/09 11:29:44 | zbirman | `/home/scratch.zbirman_vlsi/agur/fwam/run_19_10_2025__fwam_rbv_2025_09_07_GOLDEN_no_xcap_NDR` |  STA |
| **fwas** | NDQ | 2025/11/16 13:55:47 | rmenasheof | `/home/scratch.rmenasheof_vlsi/agur/fwas/fwas_golden_ipo4_21_9_for_vivid` |  STA |
| **glc** | NDQ | 2025/11/16 21:07:59 | ynaim | `/home/scratch.ynaim_vlsi_1/agur/1NL/glc/glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid` |  STA |
| **iopl** | NDQ | 2025/07/27 10:38:26 | yshlush | `/home/scratch.yshlush_vlsi/iopl/iopl_condb_int1_52_2r1/export/export_icc2` |  STA FCL |
| **ioplm** | NDQ | 2024/11/14 11:05:29 | netaa | `/home/sunbird_netaa/ioplm/starling_ioplm_2024_10_30` |  STA |
| **iopx** | NDQ | 2025/03/05 13:10:45 | vmoshkovich | `/home/sunbird_vmoshkovich/iopx/starling_iopx_2024_11_06` |  STA FCL |
| **ir** | NDQ | 2025/11/13 17:55:52 | thadad | `/home/scratch.thadad_vlsi/agur/1NL/ir/ir_rbv_2025_10_19_agur_issu128_util/pnr_flow/nv_flow/ir/ipo1002/nbu_signoff` |  STA |
| **lndm** | NDQ | 2025/11/16 16:06:13 | shlomoc | `/home/scratch.shlomoc_vlsi/agur/lndm/run_07_09_2025_lndm_rbv_2025_09_01_new_flow` |  STA FCL |
| **nvrisc** | NDQ | 2025/11/09 09:28:57 | ykatzav | `/home/scratch.ykatzav_vlsi/agur/nvrisc/nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2_PI/pnr_flow/nv_flow/nvrisc/ipo1020/nbu_signoff` |  STA FCL |
| **pmuxm** | NDQ | 2025/11/09 11:27:36 | zbirman | `/home/scratch.zbirman_vlsi/agur/pmuxm/run_15_10_pmuxm_rbv_2025_10_08_sram_size_80k_sram_resize_incremental` |  STA |
| **prtm** | NDQ | 2025/11/06 15:11:14 | lmustafa | `/home/scratch.lmustafa_vlsi/agur/prtm/prtm_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap_r1_fifthtry` |  STA FCL PNR |
| **psca** | NDQ | 2025/11/16 10:17:46 | nkahaz | `/home/scratch.nkahaz_vlsi/ww38_5_fixes/psca_rbv_2025_09_08_agur_condb_int3_2025_08_27_0_1NL_snap_ref/pnr_flow/nv_flow/psca/ipo1050/nbu_signoff` |  STA |
| **pscb** | NDQ | 2025/11/06 11:18:37 | nkahaz | `/home/scratch.nkahaz_vlsi/ww38_5_fixes/pscb_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_ref/pnr_flow/nv_flow/pscb/ipo1048/nbu_signoff` |  STA |
| **pscc** | NDQ | 2025/11/07 06:59:08 | dtraitelovic | `/home/scratch.dtraitelovic_vlsi/agur/pscc/pscc_2025_09_02_1NL_snap_new_flow_flp_cdc/pnr_flow/nv_flow/pscc/ipo1007/nbu_signoff` |  STA |
| **pscd** | NDQ | 2025/11/16 10:19:33 | gibell | `/home/scratch.gibell_vlsi/agur/1nl/pscd/pscd_rbv_2025_09_02_ver4_Sep25_gb` |  STA |
| **px** | NDQ | 2025/11/16 10:48:39 | aamsalem | `/home/scratch.aamsalem_vlsi/agur/px/1NL/run_9_9_old_util65/px_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_old_util65` |  STA |
| **riba** | NDQ | 2025/11/16 13:56:14 | rmenasheof | `/home/scratch.rmenasheof_vlsi/agur/riba/riba_10_9_1nl_new_flow_golden` |  STA |
| **ribs** | NDQ | 2025/11/16 11:23:52 | ynaim | `/home/scratch.ynaim_vlsi_1/agur/1NL/ribs/ribs.ribs_rbv_2025_10_20_agur_condb_int3_2025_08_31_0_no_split_fifo_with_bypass_0_inff_1_vivid` |  STA |
| **sma** | NDQ | 2025/11/16 16:08:48 | shlomoc | `/home/scratch.shlomoc_vlsi/agur/sma/run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix` |  STA FCL |
| **yu** | NDQ | 2025/11/16 19:51:31 | ashahock | `/home/scratch.ashahock_vlsi/agur/yu/yu_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_ver5_lib_fix` |  STA PNR |
| **dqaa** | QNS | 2025/11/13 16:05:53 | siddharthasa | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqaa/dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_final` |  STA PNR |
| **dqaci** | QNS | 2025/11/13 14:35:02 | siddharthasa | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqaci/dqaci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel/signoff_flow/nv_gate_eco/dqaci/ipo1000/nbu_signoff` |  STA PNR |
| **dqaco** | QNS | 2025/11/13 07:44:09 | gnarla | `/home/scratch.gnarla_vlsi_1/agur/1NL/dqaco/dqaco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_lat_pin_def` |  STA PNR |
| **dqai** | QNS | 2025/11/16 11:55:13 | mlanzerer | `/home/scratch.mlanzerer_vlsi/dqai_dir/fix_tag_1nl` |  STA |
| **dqamci** | QNS | 2025/11/13 08:52:52 | mlanzerer | `/home/scratch.mlanzerer_vlsi/dqamci_dir/dqamci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA |
| **dqamco** | QNS | 2025/11/13 14:27:43 | siddharthasa | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqamco/dqamco_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel/signoff_flow/nv_gate_eco/dqamco/ipo1000/nbu_signoff` |  STA PNR |
| **dqamdi** | QNS | 2025/11/13 17:18:16 | seeman | `/home/scratch.seeman_vlsi_1/agur/1nl/dqamdi/dqamdi_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_q2si_dsr` |  STA |
| **dqamdo** | QNS | 2025/11/13 18:23:21 | abarman | `/home/scratch.abarman_vlsi/agur/1NL/DQAMO_NEW/1NL_run2_scan_VIVID_ECO/dqamdo_rbv_2025_09_18_agur_condb_int3_2025_08_27_0_1NL_snap_vivideco` |  STA PNR FE_DCT |
| **dqap** | QNS | 2025/11/13 18:23:59 | drazmizrahi | `/home/scratch.drazmizrahi_vlsi/dqap/dqap_copy_from_tal/pnr_flow/nv_flow/dqap/ipo1013_chiplet_4_eco/nbu_signoff` |  STA |
| **dqavi** | QNS | 2025/11/13 10:40:17 | abarman | `/home/scratch.abarman_vlsi/agur/1NL/DQAVI/1NL_run1_eco/dqavi_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_eco` |  STA FCL PNR FE_DCT |
| **dqavo** | QNS | 2025/11/13 08:58:17 | gnarla | `/home/scratch.gnarla_vlsi_1/agur/1NL/dqavo/dqavo_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_path_groups` |  STA FCL PNR |
| **dqax** | QNS | 2025/11/12 22:33:43 | hmendelovich | `/home/scratch.hmendelovich_vlsi/dqax_from_matan2` |  STA |
| **dql** | QNS | 2025/11/13 17:23:00 | aazran | `/home/scratch.aazran_vlsi/dql/040925_1nl_reff_fixed_v0/pnr_flow/nv_flow/dql/ipo1005/nbu_signoff` |  STA |
| **dqs** | QNS | 2025/11/13 10:43:14 | abarman | `/home/scratch.abarman_vlsi/agur/1NL/DQS/1NL_run1_SO/dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so` |  STA FCL PNR FE_DCT |
| **eds** | QNS | 2025/11/13 22:16:47 | eelgabsi | `/home/scratch.eelgabsi_vlsi/AGUR/PARTITIONS/1nl/qns/eds/eds_rbv_2025_10_06_agur_condb_int3_2025_08_27_0_r0/pnr_flow/nv_flow/eds/ipo1010_eco4/nbu_signoff` |  STA |
| **qcorel** | QNS | 2025/11/16 10:19:52 | ronil | `/home/scratch.ronil_vlsi_1/agur/qcorel/qcorel_l0_21_10_25_new_scratch/pnr_flow/nv_flow/qcorel/ipo1006/nbu_signoff` |  STA |
| **qcorer** | QNS | 2025/11/11 09:59:05 | ronil | `/home/scratch.ronil_vlsi/qcorer/qcorer_r2_21_10_25_tpi/pnr_flow/nv_flow/qcorer/ipo1012/nbu_signoff` |  STA |
| **tecorel** | QNS | 2025/11/13 07:16:03 | gnarla | `/home/scratch.gnarla_vlsi/agur/1NL/tecorel/tecorel_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_default_run` |  STA FCL PNR |
| **tecorer** | QNS | 2025/11/13 10:30:20 | hsajwan | `/home/scratch.hsajwan_vlsi/agur/1NL/tecorer/tecorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |  STA FCL PNR |
| **tds** | QNS | 2025/11/13 10:29:37 | hsajwan | `/home/scratch.hsajwan_vlsi/agur/1NL/tds/tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` |  STA FCL PNR |
| **alm** | TCB | 2025/11/11 18:08:57 | tmazor | `/home/scratch.tmazor_vlsi/agur/agur_alm_rbv_2025_10_09/pnr_flow/nv_flow/alm/ipo1005/nbu_signoff` |  STA |
| **bta** | TCB | 2025/11/11 11:45:58 | vliberchuk | `/home/scratch.vliberchuk_vlsi/agur/1nl/bta/bta_2025_10_28_Oct28_Timing/pnr_flow/nv_flow/bta/ipo1085_vchiplet_ptfix_of1078_ofp/nbu_signoff` |  STA |
| **eri** | TCB | 2025/11/11 16:03:15 | hsajwan | `/home/scratch.hsajwan_vlsi/agur/1NL/ERI/eri_rbv_2025_09_28_timing_fixes_first_run` |  STA FCL PNR |
| **hib** | TCB | 2025/11/11 16:33:30 | tmazor | `/home/scratch.tmazor_vlsi/agur/hib_rbv_2025_09_01_agur_condb_int3_2025_08_27_0_1NL_snap/pnr_flow/nv_flow/hib/ipo1005/nbu_signoff` |  STA |
| **top_yc_clock** | TOP_YC | 2024/07/22 23:13:27 | abeinhorn | `/home/starling_backend_blockData/top_yc_clock/top_yc_clock_sunbird_rbv_2023_05_21_FNL` |  STA FCL PNR FULL |
| **top_yc_gpio** | TOP_YC | 2025/11/12 16:25:43 | lschwartz | `/home/scratch.lschwartz_vlsi/agur/top_yc_gpio/top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_new` |  STA FCL PNR |
| **yc_clock_macro** | TOP_YC | 2024/07/22 23:13:39 | abeinhorn | `/home/starling_backend_blockData/yc_clock_macro/top_yc_clock_sunbird_rbv_2023_05_21_FNL__20230624_sp6` |  STA FCL PNR FULL |
| **yc_fuse** | TOP_YC | 2025/11/16 10:23:53 | lhaiby | `/home/scratch.lhaiby_vlsi/Agur/yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |  STA PNR |
| **yc_fuse_macro** | TOP_YC | 2024/07/22 14:49:01 | abeinhorn | `/home/starling_backend_blockData/yc_fuse_macro/yc_fuse_sunbird_rbv_2023_05_21` |  STA FCL PNR FULL |
| **yu_mng** | TOP_YC | 2025/11/13 22:42:48 | aspiegelglas | `/home/scratch.aspiegelglas_vlsi/Agur/yu_mng/yu_mng_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap_05` |  STA |

---

*Document Auto-Generated from Block Release Logs*  
*Generation Date: 2025-11-17 06:00:22*  
*Script: extract_agur_releases.sh*  
*Base Path: /home/agur_backend_blockRelease/block/*

## Notes

- All 5 CPORT units have both STA and FCL releases pointing to the same directory (combined release)
- Source workarea paths are extracted from the `db_source` line in block_release.log
- Flags indicate which types of files were included in each release
- Previous releases are tracked via `prev_last_sta_rel` symbolic links

