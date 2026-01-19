# Agur Project - All Chiplet Block Releases

## Overview
This document tracks the latest block releases for all units across all chiplets in the AGUR project.

**Total Units**: 73  
**Total Chiplets**: 7  
**Last Updated**: 2026-01-19 06:00:03

### Chiplet Breakdown
- **HIOPL**: 4 units (ioplca, ioplcb, ioplcc, ioplcd)
- **CPORT**: 5 units (fdb, fth, lnd, pmux, prt)
- **HPORT**: 6 units (ccorea, ccoreb, ccorec, ccored, ccoree, ccoref)
- **NDQ**: 28 units (clr, clt, cscore, dcmp, fdbm, fdbs, fthm, ftos, fwam, fwas, glc, iopl, ioplm, iopx, ir, lndm, nvrisc, pmuxm, prtm, psca, pscb, pscc, pscd, px, riba, ribs, sma, yu)
- **QNS**: 20 units (dqaa, dqaci, dqaco, dqai, dqamci, dqamco, dqamdi, dqamdo, dqap, dqavi, dqavo, dqax, dql, dqs, eds, qcorel, qcorer, tecorel, tecorer, tds)
- **TCB**: 4 units (alm, bta, eri, hib)
- **TOP_YC**: 6 units (top_yc_clock, top_yc_gpio, yc_clock_macro, yc_fuse, yc_fuse_macro, yu_mng)

## Release Tracking Method
- **STA Releases**: Tracked via `last_sta_rel` symbolic link
- **FCL Releases**: Tracked via `fcl_release` symbolic link  
- **Previous STA**: Tracked via `prev_last_sta_rel` symbolic link
- **Source**: `/home/agur_backend_blockRelease/block/{unit}/logs/block_release.log`

---

# Chiplet: HIOPL

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
| **Release Timestamp** | 2025/12/02 13:41:06 |
| **Release User** | avice |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.avice_vlsi_1/ioplc_units_starling/ioplcb/ioplcb_agur_exp_00/pnr_flow/nv_flow/ioplcb/ipo1003/nbu_signoff` |
| **RTL Tag** | `ioplcb_rbv_2024_03_17_starling_LO_fe_silver` |
| **Release Directory** | `nbu_signoff_ioplcb_agur_exp_00_ipo1003_2025_12_2_13_41_6` |

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
| **Release Timestamp** | 2025/03/15 08:54:54 |
| **Release Directory** | `ioplcb_rbv_2024_03_17_starling_LO_fe_silver_PD_fix_ref_uphy__2025_3_15_8_54_54` |

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
| **Release Timestamp** | 2025/12/05 16:52:32 |
| **Release User** | avice |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.avice_vlsi_2/starling_ioplc_units/ioplcd/ioplcd_agur_exp_01/pnr_flow/nv_flow/ioplcd/ipo1003/nbu_signoff` |
| **RTL Tag** | `ioplcd_rbv_2024_03_17_starling_LO_fe_silver` |
| **Release Directory** | `nbu_signoff_ioplcd_agur_exp_01_ipo1003_2025_12_5_16_52_32` |

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
| **Release Timestamp** | 2025/07/08 11:56:00 |
| **Release Directory** | `ioplcd_rbv_2024_03_17_starling_LO_fe_silver_ref_new_flp_2__2025_7_8_11_56_0` |

---


# Chiplet: CPORT

## Unit: fdb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 10:40:58 |
| **Release User** | dkolesnikov |
| **Workarea Name** | `fdb_eco_imp_2026_01_13_13_42` |
| **Source Workarea Path** | `/home/scratch.dkolesnikov_vlsi_2/agur/fdb/PFNL/lib_override_runs/fdb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap__run1_old_lib_pa/fdb_eco_imp_2026_01_13_13_42` |
| **RTL Tag** | `fdb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `fdb_eco_imp_2026_01_13_13_42_fdb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap__run1_old_lib_pa_2026_1_14_10_40_58` |

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
| **Release Timestamp** | 2026/01/13 09:10:41 |
| **Release Directory** | `fdb_eco_imp_2026_01_12_13_34_fdb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap__run1_old_lib_pa_2026_1_13_9_10_41` |

---

## Unit: fth

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 10:18:58 |
| **Release User** | lmustafa |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.lmustafa_vlsi_1/agur/fth/fth_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap_power/pnr_flow/nv_flow/fth/ipo1082/nbu_signoff` |
| **RTL Tag** | `fth_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_fth_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap_power_ipo1082_2026_1_13_10_18_58` |

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
| **Release Timestamp** | 2026/01/08 20:39:55 |
| **Release Directory** | `nbu_signoff_fth_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap_power_ipo1072_2026_1_8_20_39_55` |

---

## Unit: lnd

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 18:19:11 |
| **Release User** | ronil |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi_1/agur/lnd/run_10_12_2025_lnd_rbv_2025_12_09_pfnl_f/pnr_flow/nv_flow/lnd/ipo1032/nbu_signoff` |
| **RTL Tag** | `lnd_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_run_10_12_2025_lnd_rbv_2025_12_09_pfnl_f_ipo1032_2026_1_14_18_19_11` |

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
| **Release Timestamp** | 2026/01/08 09:47:12 |
| **Release Directory** | `nbu_signoff_run_10_12_2025_lnd_rbv_2025_12_09_pfnl_f_ipo1020_2026_1_8_9_47_12` |

---

## Unit: pmux

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 09:13:09 |
| **Release User** | brachas |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi_2/agur/PFNL/pmux/pmux_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_lib_snap_20250819/pnr_flow/nv_flow/pmux/ipo5000/nbu_signoff` |
| **RTL Tag** | `pmux_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_pmux_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_lib_snap_20250819_ipo5000_2026_1_13_9_13_9` |

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
| **Release Timestamp** | 2026/01/07 10:34:42 |
| **Release Directory** | `nbu_signoff_pmux_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_lib_snap_20250819_ipo4000_2026_1_7_10_34_42` |

---

## Unit: prt

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 11:09:12 |
| **Release User** | ykatzav |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_power/pnr_flow/nv_flow/prt/ipo1328/nbu_signoff` |
| **RTL Tag** | `prt_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_prt_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_power_ipo1328_2026_1_15_11_9_12` |

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
| **Release Timestamp** | 2026/01/13 10:12:21 |
| **Release Directory** | `nbu_signoff_prt_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_power_ipo1326_2026_1_13_10_12_21` |

---


# Chiplet: HPORT

## Unit: ccorea

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 19:31:31 |
| **Release User** | arcohen |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.arcohen_vlsi_1/agur/channels/ccorea_0812/ccorea_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ref_rerun_pnr_with_prev_setup/pnr_flow/nv_flow/ccorea/ipo2343/nbu_signoff` |
| **RTL Tag** | `ccorea_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_ccorea_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ref_rerun_pnr_with_prev_setup_ipo2343_2026_1_13_19_31_31` |

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
| **Release Timestamp** | 2026/01/07 19:45:10 |
| **Release Directory** | `nbu_signoff_ccorea_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ref_rerun_pnr_with_prev_setup_ipo2243_2026_1_7_19_45_10` |

---

## Unit: ccoreb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 09:11:22 |
| **Release User** | arcohen |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.arcohen_vlsi_1/agur/channels/ccoreb_0812/ccoreb_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ref_rerun_pnr_with_prev_setup/pnr_flow/nv_flow/ccoreb/ipo2123/nbu_signoff` |
| **RTL Tag** | `ccoreb_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_ccoreb_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ref_rerun_pnr_with_prev_setup_ipo2123_2026_1_14_9_11_22` |

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
| **Release Timestamp** | 2026/01/08 09:21:42 |
| **Release Directory** | `nbu_signoff_ccoreb_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ref_rerun_pnr_with_prev_setup_ipo2023_2026_1_8_9_21_42` |

---

## Unit: ccorec

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 07:53:58 |
| **Release User** | dkolesnikov |
| **Workarea Name** | `ccorec_eco_imp_2026_01_12_13_39` |
| **Source Workarea Path** | `/home/scratch.dkolesnikov_vlsi/agur/ccorec/PFNL/ccorec_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap__run1_dec1_ref_test/ccorec_eco_imp_2026_01_12_13_39` |
| **RTL Tag** | `ccorec_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `ccorec_eco_imp_2026_01_12_13_39_ccorec_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap__run1_dec1_ref_test_2026_1_14_7_53_58` |

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
| **Release Timestamp** | 2026/01/08 17:18:18 |
| **Release Directory** | `ccorec_eco_imp_2026_01_07_16_26_ccorec_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap__run1_dec1_ref_test_2026_1_8_17_18_18` |

---

## Unit: ccored

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 14:35:49 |
| **Release User** | brachas |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi_2/agur/PFNL/ccored/ccored_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_test_2_dec01_cfg/pnr_flow/nv_flow/ccored/ipo1700/nbu_signoff` |
| **RTL Tag** | `ccored_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_ccored_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_test_2_dec01_cfg_ipo1700_2026_1_13_14_35_49` |

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
| **Release Timestamp** | 2026/01/09 11:17:55 |
| **Release Directory** | `nbu_signoff_ccored_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_test_2_dec01_cfg_ipo1601_2026_1_9_11_17_55` |

---

## Unit: ccoree

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 15:43:22 |
| **Release User** | ykatzav |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ykatzav_vlsi_1/agur/ccoree/ccoree_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ww49/pnr_flow/nv_flow/ccoree/ipo1461/nbu_signoff` |
| **RTL Tag** | `ccoree_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_ccoree_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ww49_ipo1461_2026_1_13_15_43_22` |

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
| **Release Timestamp** | 2026/01/08 10:33:32 |
| **Release Directory** | `nbu_signoff_ccoree_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ww49_ipo1460_2026_1_8_10_33_32` |

---

## Unit: ccoref

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 09:48:34 |
| **Release User** | brachas |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi_2/agur/PFNL/ccoref/ccoref_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_test_2_dec01_cfg/pnr_flow/nv_flow/ccoref/ipo1700/nbu_signoff` |
| **RTL Tag** | `ccoref_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_ccoref_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_test_2_dec01_cfg_ipo1700_2026_1_13_9_48_34` |

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
| **Release Timestamp** | 2026/01/07 16:58:52 |
| **Release Directory** | `nbu_signoff_ccoref_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_test_2_dec01_cfg_ipo1600_2026_1_7_16_58_52` |

---


# Chiplet: NDQ

## Unit: clr

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 14:58:30 |
| **Release User** | ayerushalmy |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ayerushalmy_vlsi_2/agur/clr/PFNL/clr_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_2/pnr_flow/nv_flow/clr/ipo1010/nbu_signoff` |
| **RTL Tag** | `clr_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_clr_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_2_ipo1010_2026_1_13_14_58_30` |

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
| **Release Timestamp** | 2026/01/07 10:30:43 |
| **Release Directory** | `nbu_signoff_clr_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_2_ipo1009_2026_1_7_10_30_43` |

---

## Unit: clt

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 15:15:23 |
| **Release User** | aamsalem |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.aamsalem_vlsi/agur/clt/PFNL/run_16_12_lib_pins/clt_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_BE_PFNL_snap_16_12_lib_pins/pnr_flow/nv_flow/clt/ipo1077/nbu_signoff` |
| **RTL Tag** | `clt_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_clt_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_BE_PFNL_snap_16_12_lib_pins_ipo1077_2026_1_14_15_15_23` |

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
| **Release Timestamp** | 2025/12/31 14:55:43 |
| **Release Directory** | `nbu_signoff_clt_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_BE_PFNL_snap_16_12_lib_pins_ipo1071_2025_12_31_14_55_43` |

---

## Unit: cscore

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 10:54:11 |
| **Release User** | ynaim |
| **Workarea Name** | `cscore.cscore_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi_1/agur/PFNL/cscore/cscore.cscore_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **RTL Tag** | `cscore_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `cscore.cscore_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap__2026_1_14_10_54_11` |

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
| **Release Timestamp** | 2026/01/07 15:51:36 |
| **Release Directory** | `cscore.cscore_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap__2026_1_7_15_51_36` |

---

## Unit: dcmp

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 13:06:31 |
| **Release User** | aazran |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.aazran_vlsi/ndq/pfnl/081225_pfnl_reff_v1/pnr_flow/nv_flow/dcmp/ipo1091/nbu_signoff` |
| **RTL Tag** | `dcmp_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_081225_pfnl_reff_v1_ipo1091_2026_1_14_13_6_31` |

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
| **Release Timestamp** | 2026/01/07 11:47:15 |
| **Release Directory** | `nbu_signoff_081225_pfnl_reff_v1_ipo1081_2026_1_7_11_47_15` |

---

## Unit: fdbm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 07:58:02 |
| **Release User** | dkolesnikov |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.dkolesnikov_vlsi_2/agur/fdbm/PFNL/slcg_fixing_runs/fdbm_rbv_2025_12_16_agur_condb_int4_2025_12_04_1_PFNL__run1_identical_fp/pnr_flow/nv_flow/fdbm/ipo1080/nbu_signoff` |
| **RTL Tag** | `fdbm_rbv_2025_12_16_agur_condb_int4_2025_12_04_1_PFNL` |
| **Release Directory** | `nbu_signoff_fdbm_rbv_2025_12_16_agur_condb_int4_2025_12_04_1_PFNL__run1_identical_fp_ipo1080_2026_1_14_7_58_2` |

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
| **Release Timestamp** | 2026/01/07 08:08:01 |
| **Release Directory** | `nbu_signoff_fdbm_rbv_2025_12_16_agur_condb_int4_2025_12_04_1_PFNL__run1_identical_fp_ipo1070_2026_1_7_8_8_1` |

---

## Unit: fdbs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 12:59:01 |
| **Release User** | brachas |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.brachas_vlsi_1/agur/PFNL/fdbs/fdbs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_test_1/pnr_flow/nv_flow/fdbs/ipo4000/nbu_signoff` |
| **RTL Tag** | `fdbs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_fdbs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_test_1_ipo4000_2026_1_13_12_59_1` |

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
| **Release Timestamp** | 2026/01/07 08:36:37 |
| **Release Directory** | `nbu_signoff_fdbs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_test_1_ipo3002_2026_1_7_8_36_37` |

---

## Unit: fthm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 14:57:45 |
| **Release User** | ayerushalmy |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ayerushalmy_vlsi_2/agur/fthm/PFNL/fthm_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap_2/pnr_flow/nv_flow/fthm/ipo3009/nbu_signoff` |
| **RTL Tag** | `fthm_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_fthm_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap_2_ipo3009_2026_1_13_14_57_45` |

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
| **Release Timestamp** | 2026/01/07 10:34:00 |
| **Release Directory** | `nbu_signoff_fthm_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap_2_ipo3008_2026_1_7_10_34_0` |

---

## Unit: ftos

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 12:49:32 |
| **Release User** | thadad |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.thadad_vlsi/agur/PFNL/ftos/ftos_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/ftos/ipo1140/nbu_signoff` |
| **RTL Tag** | `ftos_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_ftos_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap_ipo1140_2026_1_13_12_49_32` |

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
| **Release Timestamp** | 2026/01/08 10:44:40 |
| **Release Directory** | `nbu_signoff_ftos_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap_ipo1106_2026_1_8_10_44_40` |

---

## Unit: fwam

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 14:38:39 |
| **Release User** | zbirman |
| **Workarea Name** | `run_09_12_2025_fwam_rbv_2025_12_08_PFNL_FOR_VIVID` |
| **Source Workarea Path** | `/home/scratch.zbirman_vlsi_1/agur/pfnl/fwam/run_09_12_2025_fwam_rbv_2025_12_08_PFNL_FOR_VIVID` |
| **RTL Tag** | `fwam_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `run_09_12_2025_fwam_rbv_2025_12_08_PFNL_FOR_VIVID__2026_1_13_14_38_39` |

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
| **Release Timestamp** | 2026/01/07 09:06:55 |
| **Release Directory** | `run_09_12_2025_fwam_rbv_2025_12_08_PFNL_FOR_VIVID__2026_1_7_9_6_55` |

---

## Unit: fwas

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 00:16:08 |
| **Release User** | ronil |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ronil_vlsi_1/agur/ndq_units/fwas/fwas_pfnl_1/pnr_flow/nv_flow/fwas/ipo1071/nbu_signoff` |
| **RTL Tag** | `fwas_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_fwas_pfnl_1_ipo1071_2026_1_14_0_16_8` |

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
| **Release Timestamp** | 2026/01/07 11:58:41 |
| **Release Directory** | `nbu_signoff_fwas_pfnl_1_ipo1060_2026_1_7_11_58_41` |

---

## Unit: glc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 19:25:19 |
| **Release User** | ynaim |
| **Workarea Name** | `glc.glc_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi_1/agur/PFNL/glc/glc.glc_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **RTL Tag** | `glc_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `glc.glc_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap__2026_1_13_19_25_19` |

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
| **Release Timestamp** | 2026/01/09 14:40:51 |
| **Release Directory** | `glc.glc_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap__2026_1_9_14_40_51` |

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

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

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

**Note:** FCL release points to same directory as STA release.

---

## Unit: ir

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 09:48:53 |
| **Release User** | thadad |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.thadad_vlsi_1/agur/PFNL/ir/ir_agur_condb_int4_2025_12_04_1_12_10_libsnap_pnr/pnr_flow/nv_flow/ir/ipo1302/nbu_signoff` |
| **RTL Tag** | `ir_rbv_2025_12_10_agur_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_ir_agur_condb_int4_2025_12_04_1_12_10_libsnap_pnr_ipo1302_2026_1_14_9_48_53` |

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
| **Release Timestamp** | 2026/01/08 10:39:15 |
| **Release Directory** | `nbu_signoff_ir_agur_condb_int4_2025_12_04_1_12_10_libsnap_pnr_ipo1092_2026_1_8_10_39_15` |

---

## Unit: lndm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 12:00:41 |
| **Release User** | ronil |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi_1/agur/lndm/run_10_12_2025_lndm_rbv_2025_12_09_pfnl_c/pnr_flow/nv_flow/lndm/ipo1030/nbu_signoff` |
| **RTL Tag** | `lndm_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_run_10_12_2025_lndm_rbv_2025_12_09_pfnl_c_ipo1030_2026_1_14_12_0_41` |

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
| **Release Timestamp** | 2026/01/07 12:10:39 |
| **Release Directory** | `nbu_signoff_run_10_12_2025_lndm_rbv_2025_12_09_pfnl_c_ipo1020_2026_1_7_12_10_39` |

---

## Unit: nvrisc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 08:45:46 |
| **Release User** | ykatzav |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.ykatzav_vlsi/agur/nvrisc/nvrisc_rbv_2025_12_10_agur_condb_int4_2025_12_04_1_BE_PFNL_snap/pnr_flow/nv_flow/nvrisc/ipo1623/nbu_signoff` |
| **RTL Tag** | `nvrisc_rbv_2025_12_10_agur_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_nvrisc_rbv_2025_12_10_agur_condb_int4_2025_12_04_1_BE_PFNL_snap_ipo1623_2026_1_14_8_45_46` |

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
| **Release Timestamp** | 2026/01/07 17:15:07 |
| **Release Directory** | `nbu_signoff_nvrisc_rbv_2025_12_10_agur_condb_int4_2025_12_04_1_BE_PFNL_snap_ipo1142_2026_1_7_17_15_7` |

---

## Unit: pmuxm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 14:38:13 |
| **Release User** | zbirman |
| **Workarea Name** | `run_09_12_2025_pmuxm_rbv_2025_12_07_PFNL_FOR_VIVID` |
| **Source Workarea Path** | `/home/scratch.zbirman_vlsi_1/agur/pfnl/pmuxm/run_09_12_2025_pmuxm_rbv_2025_12_07_PFNL_FOR_VIVID` |
| **RTL Tag** | `pmuxm_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `run_09_12_2025_pmuxm_rbv_2025_12_07_PFNL_FOR_VIVID__2026_1_13_14_38_13` |

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
| **Release Timestamp** | 2026/01/07 09:35:59 |
| **Release Directory** | `run_09_12_2025_pmuxm_rbv_2025_12_07_PFNL_FOR_VIVID__2026_1_7_9_35_59` |

---

## Unit: prtm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 11:19:01 |
| **Release User** | lmustafa |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.lmustafa_vlsi_1/agur/prtm/prtm_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_PFNL/pnr_flow/nv_flow/prtm/ipo1083/nbu_signoff` |
| **RTL Tag** | `prtm_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_prtm_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_PFNL_ipo1083_2026_1_13_11_19_1` |

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
| **Release Timestamp** | 2026/01/07 13:31:20 |
| **Release Directory** | `nbu_signoff_prtm_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_PFNL_ipo1073_2026_1_7_13_31_20` |

---

## Unit: psca

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 10:30:35 |
| **Release User** | nkahaz |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.nkahaz_vlsi_1/ww51_2_pfnl/psca_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_PFNL_snap/pnr_flow/nv_flow/psca/ipo1131/nbu_signoff` |
| **RTL Tag** | `psca_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_PFNL_snap` |
| **Release Directory** | `nbu_signoff_psca_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_PFNL_snap_ipo1131_2026_1_13_10_30_35` |

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
| **Release Timestamp** | 2026/01/08 14:24:59 |
| **Release Directory** | `nbu_signoff_psca_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_PFNL_snap_ipo1129_2026_1_8_14_24_59` |

---

## Unit: pscb

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 10:10:36 |
| **Release User** | nkahaz |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.nkahaz_vlsi_1/ww50_2_pfnl/pscb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/pscb/ipo1112/nbu_signoff` |
| **RTL Tag** | `pscb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_pscb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_ipo1112_2026_1_13_10_10_36` |

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
| **Release Timestamp** | 2026/01/07 10:33:06 |
| **Release Directory** | `nbu_signoff_pscb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_ipo1111_2026_1_7_10_33_6` |

---

## Unit: pscc

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 07:32:07 |
| **Release User** | dtraitelovic |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.dtraitelovic_vlsi_1/agur/pscc/pscc_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/pscc/ipo1025/nbu_signoff` |
| **RTL Tag** | `pscc_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_pscc_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_ipo1025_2026_1_15_7_32_7` |

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
| **Release Timestamp** | 2026/01/08 11:40:38 |
| **Release Directory** | `nbu_signoff_pscc_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_ipo1024_2026_1_8_11_40_38` |

---

## Unit: pscd

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/14 14:03:46 |
| **Release User** | gibell |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.gibell_vlsi_1/agur/official_pfnl/pscd/pscd_rbv_2025_12_07_Dec25_gb/pnr_flow/nv_flow/pscd/ipo9040/nbu_signoff` |
| **RTL Tag** | `pscd_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_pscd_rbv_2025_12_07_Dec25_gb_ipo9040_2026_1_14_14_3_46` |

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
| **Release Timestamp** | 2026/01/09 10:23:50 |
| **Release Directory** | `nbu_signoff_pscd_rbv_2025_12_07_Dec25_gb_ipo9038_2026_1_9_10_23_50` |

---

## Unit: px

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 15:34:48 |
| **Release User** | aamsalem |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.aamsalem_vlsi/agur/px/PFNL/run_15_12_new_flow_dont_use/px_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_15_12_new_flow/pnr_flow/nv_flow/px/ipo1126/nbu_signoff` |
| **RTL Tag** | `px_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_px_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_15_12_new_flow_ipo1126_2026_1_13_15_34_48` |

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
| **Release Timestamp** | 2026/01/07 10:25:19 |
| **Release Directory** | `nbu_signoff_px_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_15_12_new_flow_ipo1116_2026_1_7_10_25_19` |

---

## Unit: riba

### Latest STA Release (last_sta_rel)

### Latest FCL Release (fcl_release) - Different from STA

FCL release is in a different directory than STA.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/07 10:25:37 |
| **Release Directory** | `nbu_signoff_riba_copy_from_roi_ipo1052_2026_1_7_10_25_37` |

---

## Unit: ribs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 10:18:36 |
| **Release User** | ynaim |
| **Workarea Name** | `ribs.ribs_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap_DEC15` |
| **Source Workarea Path** | `/home/scratch.ynaim_vlsi/agur/PFNL/ribs/ribs.ribs_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap_DEC15` |
| **RTL Tag** | `ribs_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `ribs.ribs_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap_DEC15__2026_1_13_10_18_36` |

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
| **Release Timestamp** | 2026/01/08 10:21:00 |
| **Release Directory** | `ribs.ribs_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap_DEC15__2026_1_8_10_21_0` |

---

## Unit: sma

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/13 13:13:57 |
| **Release User** | zbirman |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.shlomoc_vlsi/agur/sma/run_08_12_2025_sma_rbv_2025_12_07_pfnl_d/pnr_flow/nv_flow/sma/ipo1008/nbu_signoff` |
| **RTL Tag** | `sma_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_run_08_12_2025_sma_rbv_2025_12_07_pfnl_d_ipo1008_2026_1_13_13_13_57` |

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
| **Release Timestamp** | 2026/01/07 11:26:14 |
| **Release Directory** | `nbu_signoff_run_08_12_2025_sma_rbv_2025_12_07_pfnl_d_ipo1007_2026_1_7_11_26_14` |

---

## Unit: yu

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/17 22:10:11 |
| **Release User** | ashahock |
| **Workarea Name** | `yu_agur_rbv_2025_12_08_condb_int4_2025_12_04_1_PFNL_snap_ver3` |
| **Source Workarea Path** | `/home/scratch.ashahock_vlsi/agur/yu/yu_agur_rbv_2025_12_08_condb_int4_2025_12_04_1_PFNL_snap_ver3` |
| **RTL Tag** | `yu_agur_rbv_2025_12_08_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `yu_agur_rbv_2025_12_08_condb_int4_2025_12_04_1_PFNL_snap_ver3__2026_1_17_22_10_11` |

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
| **Release Timestamp** | 2026/01/13 14:54:37 |
| **Release Directory** | `yu_agur_rbv_2025_12_08_condb_int4_2025_12_04_1_PFNL_snap_ver3__2026_1_13_14_54_37` |

---


# Chiplet: QNS

## Unit: dqaa

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 08:01:05 |
| **Release User** | hsajwan |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.siddharthasa_vlsi/agur/PFNL/dqaa/dqaa_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_POWER/pnr_flow/nv_flow/dqaa/ipo1010_vivid3_pa7/nbu_signoff` |
| **RTL Tag** | `dqaa_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqaa_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_POWER_ipo1010_2026_1_15_8_1_5` |

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
| **Release Timestamp** | 2026/01/12 15:26:12 |
| **Release Directory** | `nbu_signoff_dqaa_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_POWER_ipo1009_2026_1_12_15_26_12` |

---

## Unit: dqaci

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 07:07:01 |
| **Release User** | gnarla |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.siddharthasa_vlsi/agur/PFNL/dqaci/dqaci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_dont_use/pnr_flow/nv_flow/dqaci/ipo3003_vivid_eco2/nbu_signoff` |
| **RTL Tag** | `dqaci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqaci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_dont_use_ipo3003_2026_1_15_7_7_1` |

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
| **Release Timestamp** | 2026/01/12 15:31:42 |
| **Release Directory** | `nbu_signoff_dqaci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_dont_use_ipo3002_2026_1_12_15_31_42` |

---

## Unit: dqaco

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 08:13:24 |
| **Release User** | gnarla |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.gnarla_vlsi_1/agur/PFNL_official/dqaco/dqaco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_updated_flow_301225/pnr_flow/nv_flow/dqaco/ipo3006_vivid_eco2_PI_fixes/nbu_signoff` |
| **RTL Tag** | `dqaco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqaco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_updated_flow_301225_ipo3006_2026_1_15_8_13_24` |

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
| **Release Timestamp** | 2026/01/12 15:29:35 |
| **Release Directory** | `nbu_signoff_dqaco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_updated_flow_301225_ipo3004_2026_1_12_15_29_35` |

---

## Unit: dqai

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 08:02:52 |
| **Release User** | mlanzerer |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.mlanzerer_vlsi/dqai_dir/power_exp/pnr_flow/nv_flow/dqai/ipo4002/nbu_signoff` |
| **RTL Tag** | `dqai_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_power_exp_ipo4002_2026_1_15_8_2_52` |

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
| **Release Timestamp** | 2026/01/12 15:46:52 |
| **Release Directory** | `nbu_signoff_power_exp_ipo3002_2026_1_12_15_46_52` |

---

## Unit: dqamci

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 08:03:42 |
| **Release User** | mlanzerer |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.mlanzerer_vlsi/dqamci_dir/dqamci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/dqamci/ipo4002/nbu_signoff` |
| **RTL Tag** | `dqamci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqamci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_ipo4002_2026_1_15_8_3_42` |

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
| **Release Timestamp** | 2026/01/12 08:25:16 |
| **Release Directory** | `nbu_signoff_dqamci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_ipo3002_2026_1_12_8_25_16` |

---

## Unit: dqamco

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 08:00:20 |
| **Release User** | hsajwan |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.siddharthasa_vlsi/agur/PFNL/dqamco/dqamco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_POWER/pnr_flow/nv_flow/dqamco/ipo1010_vivid3_ref7/nbu_signoff` |
| **RTL Tag** | `dqamco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqamco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_POWER_ipo1010_2026_1_15_8_0_20` |

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
| **Release Timestamp** | 2026/01/12 08:42:44 |
| **Release Directory** | `nbu_signoff_dqamco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_POWER_ipo1009_2026_1_12_8_42_44` |

---

## Unit: dqamdi

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 10:56:46 |
| **Release User** | seeman |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.seeman_vlsi_1/agur/pfnl/dqamdi/dqamdi_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snapnflow/pnr_flow/nv_flow/dqamdi/ipo5012_vivid_3_predrc/nbu_signoff` |
| **RTL Tag** | `dqamdi_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqamdi_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snapnflow_ipo5001_2026_1_15_10_56_46` |

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
| **Release Timestamp** | 2026/01/12 19:01:35 |
| **Release Directory** | `nbu_signoff_dqamdi_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snapnflow_ipo5001_2026_1_12_19_1_35` |

---

## Unit: dqamdo

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/16 09:49:36 |
| **Release User** | abarman |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.abarman_vlsi_2/agur/OFFICAL_APPROVED_PFNL/DQAMDO/run1/dqamdo_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_run1/pnr_flow/nv_flow/dqamdo/ipo1003_eco8/nbu_signoff` |
| **RTL Tag** | `dqamdo_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqamdo_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_run1_ipo3008_2026_1_16_9_49_36` |

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
| **Release Timestamp** | 2026/01/12 17:39:44 |
| **Release Directory** | `nbu_signoff_dqamdo_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_run1_ipo3005_2026_1_12_17_39_44` |

---

## Unit: dqap

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 09:34:36 |
| **Release User** | drazmizrahi |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.drazmizrahi_vlsi_1/dqap/pfnl_07_12/pnr_flow/nv_flow/dqap/ipo1070_on_1066_vivid_loop3/nbu_signoff` |
| **RTL Tag** | `dqap_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_pfnl_07_12_ipo1070_2026_1_15_9_34_36` |

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
| **Release Timestamp** | 2026/01/12 09:28:53 |
| **Release Directory** | `nbu_signoff_pfnl_07_12_ipo1064_2026_1_12_9_28_53` |

---

## Unit: dqavi

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/16 00:14:45 |
| **Release User** | tmazor |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.tmazor_vlsi/agur/dqavi_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/dqavi/ipo4000/nbu_signoff` |
| **RTL Tag** | `dqavi_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqavi_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap_ipo4000_2026_1_16_0_14_45` |

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
| **Release Timestamp** | 2026/01/15 10:16:10 |
| **Release Directory** | `nbu_signoff_dqavi_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap_oldlib_run2_ipo2009_2026_1_15_10_16_10` |

---

## Unit: dqavo

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 09:33:45 |
| **Release User** | gnarla |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.gnarla_vlsi_1/agur/PFNL_official/dqavo/dqavo_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap_power_aware/pnr_flow/nv_flow/dqavo/ipo3005_vivid_eco3_PI_fixes/nbu_signoff` |
| **RTL Tag** | `dqavo_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqavo_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap_power_aware_ipo3005_2026_1_15_9_33_45` |

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
| **Release Timestamp** | 2026/01/15 09:23:24 |
| **Release Directory** | `nbu_signoff_dqavo_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap_power_aware_ipo3005_2026_1_15_9_23_24` |

---

## Unit: dqax

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 09:22:08 |
| **Release User** | hmendelovich |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.hmendelovich_vlsi_1/dqax/dqax_2025_12_09_DEC11_PFNL_TAG/pnr_flow/nv_flow/dqax/ipo1080/nbu_signoff` |
| **RTL Tag** | `dqax_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dqax_2025_12_09_DEC11_PFNL_TAG_ipo1080_2026_1_15_9_22_8` |

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
| **Release Timestamp** | 2026/01/11 17:51:05 |
| **Release Directory** | `nbu_signoff_dqax_2025_12_09_DEC11_PFNL_TAG_ipo1070_2026_1_11_17_51_5` |

---

## Unit: dql

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 09:59:45 |
| **Release User** | aazran |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.aazran_vlsi/dql/pfnl/071225_pfnl_v1/pnr_flow/nv_flow/dql/ipo1101/nbu_signoff` |
| **RTL Tag** | `dql_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_071225_pfnl_v1_ipo1101_2026_1_15_9_59_45` |

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
| **Release Timestamp** | 2026/01/12 16:21:37 |
| **Release Directory** | `nbu_signoff_071225_pfnl_v1_ipo1091_2026_1_12_16_21_37` |

---

## Unit: dqs

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 11:10:53 |
| **Release User** | abarman |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.abarman_vlsi_2/agur/OFFICAL_APPROVED_PFNL/DQS/run1/dqs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_run1/pnr_flow/nv_flow/dqs/ipo1001_eco8/nbu_signoff` |
| **RTL Tag** | `dqs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff__2026_1_15_11_10_53` |

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
| **Release Timestamp** | 2026/01/12 07:00:25 |
| **Release Directory** | `nbu_signoff_dqs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_run1_ipo2007_2026_1_12_7_0_25` |

---

## Unit: eds

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 08:45:37 |
| **Release User** | nwasserman |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.nwasserman_vlsi/agur/eds/dec09_20251207_int4_202512041_PFNL_snap/pnr_flow/nv_flow/eds/ipo1080/nbu_signoff` |
| **RTL Tag** | `eds_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_dec09_20251207_int4_202512041_PFNL_snap_ipo1080_2026_1_15_8_45_37` |

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
| **Release Timestamp** | 2026/01/12 08:02:15 |
| **Release Directory** | `nbu_signoff_dec09_20251207_int4_202512041_PFNL_snap_ipo1079_2026_1_12_8_2_15` |

---

## Unit: qcorel

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 09:42:08 |
| **Release User** | hmendelovich |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.hmendelovich_vlsi_1/qcorel/qcorel_2025_12_15_DEC11_PFNL_TAG_Previous_LibSnap/pnr_flow/nv_flow/qcorel/ipo1213/nbu_signoff` |
| **RTL Tag** | `qcorel_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_qcorel_2025_12_15_DEC11_PFNL_TAG_Previous_LibSnap_ipo1213_2026_1_15_9_42_8` |

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
| **Release Timestamp** | 2026/01/12 09:17:42 |
| **Release Directory** | `nbu_signoff_qcorel_2025_12_15_DEC11_PFNL_TAG_Previous_LibSnap_ipo1212_2026_1_12_9_17_42` |

---

## Unit: qcorer

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 09:29:03 |
| **Release User** | hmendelovich |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.hmendelovich_vlsi_1/qcorer/qcorer_2025_12_23_DEC11_PFNL_TAG_Previous_LibSnap_NVISM_ROSC_FIX/pnr_flow/nv_flow/qcorer/ipo1308/nbu_signoff` |
| **RTL Tag** | `qcorer_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_qcorer_2025_12_23_DEC11_PFNL_TAG_Previous_LibSnap_NVISM_ROSC_FIX_ipo1308_2026_1_15_9_29_3` |

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
| **Release Timestamp** | 2026/01/12 09:25:10 |
| **Release Directory** | `nbu_signoff_qcorer_2025_12_23_DEC11_PFNL_TAG_Previous_LibSnap_NVISM_ROSC_FIX_ipo1307_2026_1_12_9_25_10` |

---

## Unit: tecorel

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 02:15:04 |
| **Release User** | gnarla |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.gnarla_vlsi_1/agur/PFNL_official/tecorel/tecorel_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_new_flow/pnr_flow/nv_flow/tecorel/ipo3005_vivid_eco3/nbu_signoff` |
| **RTL Tag** | `tecorel_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_tecorel_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_new_flow_ipo3005_2026_1_15_2_15_4` |

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
| **Release Timestamp** | 2026/01/12 06:27:50 |
| **Release Directory** | `nbu_signoff_tecorel_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_new_flow_ipo3004_2026_1_12_6_27_50` |

---

## Unit: tecorer

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 07:48:05 |
| **Release User** | hsajwan |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.hsajwan_vlsi/agur/PFNL_Final/tecorer/tecorer_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_pfnl_rerun/pnr_flow/nv_flow/tecorer/ipo4061_vivid3_eco6/nbu_signoff` |
| **RTL Tag** | `tecorer_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_tecorer_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_pfnl_rerun_ipo4061_2026_1_15_7_48_5` |

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
| **Release Timestamp** | 2026/01/11 19:54:40 |
| **Release Directory** | `nbu_signoff_tecorer_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_pfnl_rerun_ipo4051_2026_1_11_19_54_40` |

---

## Unit: tds

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 07:47:47 |
| **Release User** | hsajwan |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.hsajwan_vlsi/agur/PFNL_Final/tds/tds_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_pfnl_rerun/pnr_flow/nv_flow/tds/ipo4083_vivid3_eco8/nbu_signoff` |
| **RTL Tag** | `tds_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_tds_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_pfnl_rerun_ipo4083_2026_1_15_7_47_47` |

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
| **Release Timestamp** | 2026/01/11 19:52:14 |
| **Release Directory** | `nbu_signoff_tds_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_pfnl_rerun_ipo4073_2026_1_11_19_52_14` |

---


# Chiplet: TCB

## Unit: alm

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/18 09:39:41 |
| **Release User** | tmazor |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.tmazor_vlsi/agur/alm_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_BE_PFNL_snap_fp3/pnr_flow/nv_flow/alm/ipo4050/nbu_signoff` |
| **RTL Tag** | `alm_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_BE_PFNL_snap` |
| **Release Directory** | `nbu_signoff_alm_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_BE_PFNL_snap_fp3_ipo4050_2026_1_18_9_39_41` |

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
| **Release Timestamp** | 2026/01/14 09:00:37 |
| **Release Directory** | `nbu_signoff_alm_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_BE_PFNL_snap_fp3_ipo4047_2026_1_14_9_0_36` |

---

## Unit: bta

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/18 09:26:42 |
| **Release User** | vliberchuk |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.vliberchuk_vlsi_1/agur/1nl/bta/bta_2025_12_07_Dec08_PFNL/pnr_flow/nv_flow/bta/ipo1261_of1199_44_PI_CLK_DATA_ALL_CHIPLET_U8075_nv/nbu_signoff` |
| **RTL Tag** | `bta_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_bta_2025_12_07_Dec08_PFNL_ipo1261_2026_1_18_9_26_42` |

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
| **Release Timestamp** | 2026/01/14 08:28:07 |
| **Release Directory** | `nbu_signoff_bta_2025_12_07_Dec08_PFNL_ipo1246_2026_1_14_8_28_7` |

---

## Unit: eri

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/17 17:09:20 |
| **Release User** | hsajwan |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.hsajwan_vlsi/agur/PFNL_Final/eri/eri_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_pfnl_rerun/pnr_flow/nv_flow/eri/ipo4104_vivid4_eco10/nbu_signoff` |
| **RTL Tag** | `eri_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_eri_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_pfnl_rerun_ipo4104_2026_1_17_17_9_20` |

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
| **Release Timestamp** | 2026/01/14 08:53:48 |
| **Release Directory** | `nbu_signoff_eri_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_pfnl_rerun_ipo4094_2026_1_14_8_53_48` |

---

## Unit: hib

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/18 09:40:34 |
| **Release User** | tmazor |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.tmazor_vlsi/agur/hib_rbv_2025_12_08_no_hbr_slcg_agur_condb_int4_2025_12_04_1_FPNL_snap/pnr_flow/nv_flow/hib/ipo4050/nbu_signoff` |
| **RTL Tag** | `hib_rbv_2025_12_08_no_hbr_slcg_agur_condb_int4_2025_12_04_1_FPNL_snap` |
| **Release Directory** | `nbu_signoff_hib_rbv_2025_12_08_no_hbr_slcg_agur_condb_int4_2025_12_04_1_FPNL_snap_ipo4050_2026_1_18_9_40_34` |

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
| **Release Timestamp** | 2026/01/14 05:41:57 |
| **Release Directory** | `nbu_signoff_hib_rbv_2025_12_08_no_hbr_slcg_agur_condb_int4_2025_12_04_1_FPNL_snap_ipo4047_2026_1_14_5_41_57` |

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
| **Release Timestamp** | 2026/01/12 10:09:56 |
| **Release User** | momar |
| **Workarea Name** | `top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.momar_vlsi/agur/top_yc_gpio/top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__2026_1_12_10_9_56` |

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
| **Release Timestamp** | 2026/01/07 09:42:44 |
| **Release Directory** | `top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__2026_1_7_9_42_44` |

---

## Unit: yc_clock_macro

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/25 14:56:04 |
| **Release User** | momar |
| **Workarea Name** | `top_yc_clock_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.momar_vlsi/agur/yc_clock_macro/top_yc_clock_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **RTL Tag** | `top_yc_clock_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |
| **Release Directory** | `top_yc_clock_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap__2025_11_25_14_56_4` |

**Release Flags:**

| Flag | Status | Description |
|------|--------|-------------|
| **Sta** | True | Static Timing Analysis (SPEF, SDC, netlist) |
| **Fcl** | True | Functional/Layout (DB, IOs, OASIS) |
| **Pnr** | True | Place & Route database |
| **FE_DCT** | False | Front End DCT |
| **DC** | False | Design Compiler synthesis |
| **Full** | True | Full release (all files) |

**Note:** FCL release points to same directory as STA release.

### Previous STA Release (prev_last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2024/07/22 23:13:39 |
| **Release Directory** | `full_release` |

---

## Unit: yc_fuse

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2025/11/30 16:01:16 |
| **Release User** | lhaiby |
| **Workarea Name** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |
| **Source Workarea Path** | `/home/scratch.lhaiby_vlsi/Agur/yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |
| **RTL Tag** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |
| **Release Directory** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap__2025_11_30_16_1_16` |

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
| **Release Timestamp** | 2025/11/16 10:23:53 |
| **Release Directory** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap__2025_11_16_10_23_53` |

---

## Unit: yc_fuse_macro

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 15:39:55 |
| **Release User** | lhaiby |
| **Workarea Name** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap_12_11_arkady` |
| **Source Workarea Path** | `/home/scratch.lhaiby_vlsi/Agur/yc_fuse_macro/yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap_12_11_arkady` |
| **RTL Tag** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |
| **Release Directory** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap_12_11_arkady__2026_1_15_15_39_55` |

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
| **Release Timestamp** | 2026/01/04 14:46:32 |
| **Release Directory** | `yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap_12_11_arkady__2026_1_4_14_46_32` |

---

## Unit: yu_mng

### Latest STA Release (last_sta_rel)

| Property | Value |
|----------|-------|
| **Release Timestamp** | 2026/01/15 16:09:53 |
| **Release User** | yavital |
| **Workarea Name** | `nbu_signoff` |
| **Source Workarea Path** | `/home/scratch.yavital_vlsi/agur/yu_mng/PFNL_exp_01/pnr_flow/nv_flow/yu_mng/ipo1003/nbu_signoff` |
| **RTL Tag** | `yu_mng_agur_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap` |
| **Release Directory** | `nbu_signoff_PFNL_exp_01_ipo1003_2026_1_15_16_9_53` |

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
| **Release Timestamp** | 2026/01/15 12:09:13 |
| **Release Directory** | `nbu_signoff_PFNL_exp_01_ipo1003_2026_1_15_12_9_13` |

---



## Summary Table

| Unit | Chiplet | Latest STA Timestamp | User | Source Workarea | Release Types |
|------|---------|---------------------|------|-----------------|---------------|
| **ioplca** | HIOPL | 2025/03/25 16:54:53 | ysapojnikov | `/home/scratch.ysapojnikov_vlsi/ioplca/ioplca_rbv_2024_03_17_starling_LO_fe_silver_new_flp_ref_final_2` |  STA FCL |
| **ioplcb** | HIOPL | 2025/12/02 13:41:06 | avice | `/home/scratch.avice_vlsi_1/ioplc_units_starling/ioplcb/ioplcb_agur_exp_00/pnr_flow/nv_flow/ioplcb/ipo1003/nbu_signoff` |  STA FCL PNR FE_DCT |
| **ioplcc** | HIOPL | 2025/03/17 14:02:53 | roir | `/home/scratch.roir_vlsi_1/starling/ioplcc/ioplcc_rbv_2024_03_17_starling_LO_fe_silver_NewUphy` |  STA FCL |
| **ioplcd** | HIOPL | 2025/12/05 16:52:32 | avice | `/home/scratch.avice_vlsi_2/starling_ioplc_units/ioplcd/ioplcd_agur_exp_01/pnr_flow/nv_flow/ioplcd/ipo1003/nbu_signoff` |  STA FCL PNR FE_DCT |
| **fdb** | CPORT | 2026/01/14 10:40:58 | dkolesnikov | `/home/scratch.dkolesnikov_vlsi_2/agur/fdb/PFNL/lib_override_runs/fdb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap__run1_old_lib_pa/fdb_eco_imp_2026_01_13_13_42` |  STA FCL PNR FE_DCT |
| **fth** | CPORT | 2026/01/13 10:18:58 | lmustafa | `/home/scratch.lmustafa_vlsi_1/agur/fth/fth_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap_power/pnr_flow/nv_flow/fth/ipo1082/nbu_signoff` |  STA FCL PNR |
| **lnd** | CPORT | 2026/01/14 18:19:11 | ronil | `/home/scratch.shlomoc_vlsi_1/agur/lnd/run_10_12_2025_lnd_rbv_2025_12_09_pfnl_f/pnr_flow/nv_flow/lnd/ipo1032/nbu_signoff` |  STA |
| **pmux** | CPORT | 2026/01/13 09:13:09 | brachas | `/home/scratch.brachas_vlsi_2/agur/PFNL/pmux/pmux_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_lib_snap_20250819/pnr_flow/nv_flow/pmux/ipo5000/nbu_signoff` |  STA FCL PNR FE_DCT |
| **prt** | CPORT | 2026/01/15 11:09:12 | ykatzav | `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_power/pnr_flow/nv_flow/prt/ipo1328/nbu_signoff` |  STA FCL PNR FE_DCT |
| **ccorea** | HPORT | 2026/01/13 19:31:31 | arcohen | `/home/scratch.arcohen_vlsi_1/agur/channels/ccorea_0812/ccorea_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ref_rerun_pnr_with_prev_setup/pnr_flow/nv_flow/ccorea/ipo2343/nbu_signoff` |  STA FCL PNR FE_DCT |
| **ccoreb** | HPORT | 2026/01/14 09:11:22 | arcohen | `/home/scratch.arcohen_vlsi_1/agur/channels/ccoreb_0812/ccoreb_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ref_rerun_pnr_with_prev_setup/pnr_flow/nv_flow/ccoreb/ipo2123/nbu_signoff` |  STA FCL PNR FE_DCT |
| **ccorec** | HPORT | 2026/01/14 07:53:58 | dkolesnikov | `/home/scratch.dkolesnikov_vlsi/agur/ccorec/PFNL/ccorec_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap__run1_dec1_ref_test/ccorec_eco_imp_2026_01_12_13_39` |  STA FCL PNR FE_DCT |
| **ccored** | HPORT | 2026/01/13 14:35:49 | brachas | `/home/scratch.brachas_vlsi_2/agur/PFNL/ccored/ccored_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_test_2_dec01_cfg/pnr_flow/nv_flow/ccored/ipo1700/nbu_signoff` |  STA FCL PNR FE_DCT |
| **ccoree** | HPORT | 2026/01/13 15:43:22 | ykatzav | `/home/scratch.ykatzav_vlsi_1/agur/ccoree/ccoree_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_ww49/pnr_flow/nv_flow/ccoree/ipo1461/nbu_signoff` |  STA FCL PNR FE_DCT |
| **ccoref** | HPORT | 2026/01/13 09:48:34 | brachas | `/home/scratch.brachas_vlsi_2/agur/PFNL/ccoref/ccoref_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_test_2_dec01_cfg/pnr_flow/nv_flow/ccoref/ipo1700/nbu_signoff` |  STA FCL PNR FE_DCT |
| **clr** | NDQ | 2026/01/13 14:58:30 | ayerushalmy | `/home/scratch.ayerushalmy_vlsi_2/agur/clr/PFNL/clr_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_2/pnr_flow/nv_flow/clr/ipo1010/nbu_signoff` |  STA |
| **clt** | NDQ | 2026/01/14 15:15:23 | aamsalem | `/home/scratch.aamsalem_vlsi/agur/clt/PFNL/run_16_12_lib_pins/clt_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_BE_PFNL_snap_16_12_lib_pins/pnr_flow/nv_flow/clt/ipo1077/nbu_signoff` |  STA FCL |
| **cscore** | NDQ | 2026/01/14 10:54:11 | ynaim | `/home/scratch.ynaim_vlsi_1/agur/PFNL/cscore/cscore.cscore_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap` |  STA |
| **dcmp** | NDQ | 2026/01/14 13:06:31 | aazran | `/home/scratch.aazran_vlsi/ndq/pfnl/081225_pfnl_reff_v1/pnr_flow/nv_flow/dcmp/ipo1091/nbu_signoff` |  STA |
| **fdbm** | NDQ | 2026/01/14 07:58:02 | dkolesnikov | `/home/scratch.dkolesnikov_vlsi_2/agur/fdbm/PFNL/slcg_fixing_runs/fdbm_rbv_2025_12_16_agur_condb_int4_2025_12_04_1_PFNL__run1_identical_fp/pnr_flow/nv_flow/fdbm/ipo1080/nbu_signoff` |  STA FCL PNR FE_DCT |
| **fdbs** | NDQ | 2026/01/13 12:59:01 | brachas | `/home/scratch.brachas_vlsi_1/agur/PFNL/fdbs/fdbs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_test_1/pnr_flow/nv_flow/fdbs/ipo4000/nbu_signoff` |  STA FCL PNR FE_DCT |
| **fthm** | NDQ | 2026/01/13 14:57:45 | ayerushalmy | `/home/scratch.ayerushalmy_vlsi_2/agur/fthm/PFNL/fthm_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap_2/pnr_flow/nv_flow/fthm/ipo3009/nbu_signoff` |  STA |
| **ftos** | NDQ | 2026/01/13 12:49:32 | thadad | `/home/scratch.thadad_vlsi/agur/PFNL/ftos/ftos_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/ftos/ipo1140/nbu_signoff` |  STA |
| **fwam** | NDQ | 2026/01/13 14:38:39 | zbirman | `/home/scratch.zbirman_vlsi_1/agur/pfnl/fwam/run_09_12_2025_fwam_rbv_2025_12_08_PFNL_FOR_VIVID` |  STA |
| **fwas** | NDQ | 2026/01/14 00:16:08 | ronil | `/home/scratch.ronil_vlsi_1/agur/ndq_units/fwas/fwas_pfnl_1/pnr_flow/nv_flow/fwas/ipo1071/nbu_signoff` |  STA |
| **glc** | NDQ | 2026/01/13 19:25:19 | ynaim | `/home/scratch.ynaim_vlsi_1/agur/PFNL/glc/glc.glc_rbv_2025_12_08_agur_condb_int4_2025_12_04_1_PFNL_snap` |  STA |
| **iopl** | NDQ | 2025/07/27 10:38:26 | yshlush | `/home/scratch.yshlush_vlsi/iopl/iopl_condb_int1_52_2r1/export/export_icc2` |  STA FCL |
| **ioplm** | NDQ | 2024/11/14 11:05:29 | netaa | `/home/sunbird_netaa/ioplm/starling_ioplm_2024_10_30` |  STA |
| **iopx** | NDQ | 2025/03/05 13:10:45 | vmoshkovich | `/home/sunbird_vmoshkovich/iopx/starling_iopx_2024_11_06` |  STA FCL |
| **ir** | NDQ | 2026/01/14 09:48:53 | thadad | `/home/scratch.thadad_vlsi_1/agur/PFNL/ir/ir_agur_condb_int4_2025_12_04_1_12_10_libsnap_pnr/pnr_flow/nv_flow/ir/ipo1302/nbu_signoff` |  STA |
| **lndm** | NDQ | 2026/01/14 12:00:41 | ronil | `/home/scratch.shlomoc_vlsi_1/agur/lndm/run_10_12_2025_lndm_rbv_2025_12_09_pfnl_c/pnr_flow/nv_flow/lndm/ipo1030/nbu_signoff` |  STA |
| **nvrisc** | NDQ | 2026/01/14 08:45:46 | ykatzav | `/home/scratch.ykatzav_vlsi/agur/nvrisc/nvrisc_rbv_2025_12_10_agur_condb_int4_2025_12_04_1_BE_PFNL_snap/pnr_flow/nv_flow/nvrisc/ipo1623/nbu_signoff` |  STA FCL PNR FE_DCT |
| **pmuxm** | NDQ | 2026/01/13 14:38:13 | zbirman | `/home/scratch.zbirman_vlsi_1/agur/pfnl/pmuxm/run_09_12_2025_pmuxm_rbv_2025_12_07_PFNL_FOR_VIVID` |  STA |
| **prtm** | NDQ | 2026/01/13 11:19:01 | lmustafa | `/home/scratch.lmustafa_vlsi_1/agur/prtm/prtm_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_PFNL/pnr_flow/nv_flow/prtm/ipo1083/nbu_signoff` |  STA FCL PNR |
| **psca** | NDQ | 2026/01/13 10:30:35 | nkahaz | `/home/scratch.nkahaz_vlsi_1/ww51_2_pfnl/psca_rbv_2025_12_08_agur_condb_pfnl_2025_12_08_1_psc_p2p_PFNL_snap/pnr_flow/nv_flow/psca/ipo1131/nbu_signoff` |  STA FCL PNR FE_DCT |
| **pscb** | NDQ | 2026/01/13 10:10:36 | nkahaz | `/home/scratch.nkahaz_vlsi_1/ww50_2_pfnl/pscb_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/pscb/ipo1112/nbu_signoff` |  STA FCL PNR FE_DCT |
| **pscc** | NDQ | 2026/01/15 07:32:07 | dtraitelovic | `/home/scratch.dtraitelovic_vlsi_1/agur/pscc/pscc_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/pscc/ipo1025/nbu_signoff` |  STA |
| **pscd** | NDQ | 2026/01/14 14:03:46 | gibell | `/home/scratch.gibell_vlsi_1/agur/official_pfnl/pscd/pscd_rbv_2025_12_07_Dec25_gb/pnr_flow/nv_flow/pscd/ipo9040/nbu_signoff` |  STA FCL PNR FE_DCT |
| **px** | NDQ | 2026/01/13 15:34:48 | aamsalem | `/home/scratch.aamsalem_vlsi/agur/px/PFNL/run_15_12_new_flow_dont_use/px_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_15_12_new_flow/pnr_flow/nv_flow/px/ipo1126/nbu_signoff` |  STA FCL |
| **ribs** | NDQ | 2026/01/13 10:18:36 | ynaim | `/home/scratch.ynaim_vlsi/agur/PFNL/ribs/ribs.ribs_rbv_2025_12_07_condb_int4_2025_12_04_1_PFNL_snap_DEC15` |  STA |
| **sma** | NDQ | 2026/01/13 13:13:57 | zbirman | `/home/scratch.shlomoc_vlsi/agur/sma/run_08_12_2025_sma_rbv_2025_12_07_pfnl_d/pnr_flow/nv_flow/sma/ipo1008/nbu_signoff` |  STA |
| **yu** | NDQ | 2026/01/17 22:10:11 | ashahock | `/home/scratch.ashahock_vlsi/agur/yu/yu_agur_rbv_2025_12_08_condb_int4_2025_12_04_1_PFNL_snap_ver3` |  STA PNR |
| **dqaa** | QNS | 2026/01/15 08:01:05 | hsajwan | `/home/scratch.siddharthasa_vlsi/agur/PFNL/dqaa/dqaa_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_POWER/pnr_flow/nv_flow/dqaa/ipo1010_vivid3_pa7/nbu_signoff` |  STA |
| **dqaci** | QNS | 2026/01/15 07:07:01 | gnarla | `/home/scratch.siddharthasa_vlsi/agur/PFNL/dqaci/dqaci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_dont_use/pnr_flow/nv_flow/dqaci/ipo3003_vivid_eco2/nbu_signoff` |  STA PNR |
| **dqaco** | QNS | 2026/01/15 08:13:24 | gnarla | `/home/scratch.gnarla_vlsi_1/agur/PFNL_official/dqaco/dqaco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_updated_flow_301225/pnr_flow/nv_flow/dqaco/ipo3006_vivid_eco2_PI_fixes/nbu_signoff` |  STA PNR |
| **dqai** | QNS | 2026/01/15 08:02:52 | mlanzerer | `/home/scratch.mlanzerer_vlsi/dqai_dir/power_exp/pnr_flow/nv_flow/dqai/ipo4002/nbu_signoff` |  STA |
| **dqamci** | QNS | 2026/01/15 08:03:42 | mlanzerer | `/home/scratch.mlanzerer_vlsi/dqamci_dir/dqamci_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/dqamci/ipo4002/nbu_signoff` |  STA |
| **dqamco** | QNS | 2026/01/15 08:00:20 | hsajwan | `/home/scratch.siddharthasa_vlsi/agur/PFNL/dqamco/dqamco_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_POWER/pnr_flow/nv_flow/dqamco/ipo1010_vivid3_ref7/nbu_signoff` |  STA |
| **dqamdi** | QNS | 2026/01/15 10:56:46 | seeman | `/home/scratch.seeman_vlsi_1/agur/pfnl/dqamdi/dqamdi_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snapnflow/pnr_flow/nv_flow/dqamdi/ipo5012_vivid_3_predrc/nbu_signoff` |  STA |
| **dqamdo** | QNS | 2026/01/16 09:49:36 | abarman | `/home/scratch.abarman_vlsi_2/agur/OFFICAL_APPROVED_PFNL/DQAMDO/run1/dqamdo_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_run1/pnr_flow/nv_flow/dqamdo/ipo1003_eco8/nbu_signoff` |  STA FCL PNR |
| **dqap** | QNS | 2026/01/15 09:34:36 | drazmizrahi | `/home/scratch.drazmizrahi_vlsi_1/dqap/pfnl_07_12/pnr_flow/nv_flow/dqap/ipo1070_on_1066_vivid_loop3/nbu_signoff` |  STA |
| **dqavi** | QNS | 2026/01/16 00:14:45 | tmazor | `/home/scratch.tmazor_vlsi/agur/dqavi_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap/pnr_flow/nv_flow/dqavi/ipo4000/nbu_signoff` |  STA |
| **dqavo** | QNS | 2026/01/15 09:33:45 | gnarla | `/home/scratch.gnarla_vlsi_1/agur/PFNL_official/dqavo/dqavo_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_PFNL_snap_power_aware/pnr_flow/nv_flow/dqavo/ipo3005_vivid_eco3_PI_fixes/nbu_signoff` |  STA PNR |
| **dqax** | QNS | 2026/01/15 09:22:08 | hmendelovich | `/home/scratch.hmendelovich_vlsi_1/dqax/dqax_2025_12_09_DEC11_PFNL_TAG/pnr_flow/nv_flow/dqax/ipo1080/nbu_signoff` |  STA |
| **dql** | QNS | 2026/01/15 09:59:45 | aazran | `/home/scratch.aazran_vlsi/dql/pfnl/071225_pfnl_v1/pnr_flow/nv_flow/dql/ipo1101/nbu_signoff` |  STA |
| **dqs** | QNS | 2026/01/15 11:10:53 | abarman | `/home/scratch.abarman_vlsi_2/agur/OFFICAL_APPROVED_PFNL/DQS/run1/dqs_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_run1/pnr_flow/nv_flow/dqs/ipo1001_eco8/nbu_signoff` |  STA PNR |
| **eds** | QNS | 2026/01/15 08:45:37 | nwasserman | `/home/scratch.nwasserman_vlsi/agur/eds/dec09_20251207_int4_202512041_PFNL_snap/pnr_flow/nv_flow/eds/ipo1080/nbu_signoff` |  STA |
| **qcorel** | QNS | 2026/01/15 09:42:08 | hmendelovich | `/home/scratch.hmendelovich_vlsi_1/qcorel/qcorel_2025_12_15_DEC11_PFNL_TAG_Previous_LibSnap/pnr_flow/nv_flow/qcorel/ipo1213/nbu_signoff` |  STA |
| **qcorer** | QNS | 2026/01/15 09:29:03 | hmendelovich | `/home/scratch.hmendelovich_vlsi_1/qcorer/qcorer_2025_12_23_DEC11_PFNL_TAG_Previous_LibSnap_NVISM_ROSC_FIX/pnr_flow/nv_flow/qcorer/ipo1308/nbu_signoff` |  STA |
| **tecorel** | QNS | 2026/01/15 02:15:04 | gnarla | `/home/scratch.gnarla_vlsi_1/agur/PFNL_official/tecorel/tecorel_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_new_flow/pnr_flow/nv_flow/tecorel/ipo3005_vivid_eco3/nbu_signoff` |  STA PNR |
| **tecorer** | QNS | 2026/01/15 07:48:05 | hsajwan | `/home/scratch.hsajwan_vlsi/agur/PFNL_Final/tecorer/tecorer_rbv_2025_12_07_condb_int4_2025_12_04_1_BE_PFNL_snap_pfnl_rerun/pnr_flow/nv_flow/tecorer/ipo4061_vivid3_eco6/nbu_signoff` |  STA |
| **tds** | QNS | 2026/01/15 07:47:47 | hsajwan | `/home/scratch.hsajwan_vlsi/agur/PFNL_Final/tds/tds_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_pfnl_rerun/pnr_flow/nv_flow/tds/ipo4083_vivid3_eco8/nbu_signoff` |  STA |
| **alm** | TCB | 2026/01/18 09:39:41 | tmazor | `/home/scratch.tmazor_vlsi/agur/alm_rbv_2025_12_09_agur_condb_int4_2025_12_04_1_BE_PFNL_snap_fp3/pnr_flow/nv_flow/alm/ipo4050/nbu_signoff` |  STA |
| **bta** | TCB | 2026/01/18 09:26:42 | vliberchuk | `/home/scratch.vliberchuk_vlsi_1/agur/1nl/bta/bta_2025_12_07_Dec08_PFNL/pnr_flow/nv_flow/bta/ipo1261_of1199_44_PI_CLK_DATA_ALL_CHIPLET_U8075_nv/nbu_signoff` |  STA |
| **eri** | TCB | 2026/01/17 17:09:20 | hsajwan | `/home/scratch.hsajwan_vlsi/agur/PFNL_Final/eri/eri_rbv_2025_12_07_agur_condb_int4_2025_12_04_1_PFNL_snap_pfnl_rerun/pnr_flow/nv_flow/eri/ipo4104_vivid4_eco10/nbu_signoff` |  STA |
| **hib** | TCB | 2026/01/18 09:40:34 | tmazor | `/home/scratch.tmazor_vlsi/agur/hib_rbv_2025_12_08_no_hbr_slcg_agur_condb_int4_2025_12_04_1_FPNL_snap/pnr_flow/nv_flow/hib/ipo4050/nbu_signoff` |  STA |
| **top_yc_clock** | TOP_YC | 2024/07/22 23:13:27 | abeinhorn | `/home/starling_backend_blockData/top_yc_clock/top_yc_clock_sunbird_rbv_2023_05_21_FNL` |  STA FCL PNR FULL |
| **top_yc_gpio** | TOP_YC | 2026/01/12 10:09:56 | momar | `/home/scratch.momar_vlsi/agur/top_yc_gpio/top_yc_gpio_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA PNR |
| **yc_clock_macro** | TOP_YC | 2025/11/25 14:56:04 | momar | `/home/scratch.momar_vlsi/agur/yc_clock_macro/top_yc_clock_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap` |  STA FCL PNR FULL |
| **yc_fuse** | TOP_YC | 2025/11/30 16:01:16 | lhaiby | `/home/scratch.lhaiby_vlsi/Agur/yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap` |  STA PNR |
| **yc_fuse_macro** | TOP_YC | 2026/01/15 15:39:55 | lhaiby | `/home/scratch.lhaiby_vlsi/Agur/yc_fuse_macro/yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap_12_11_arkady` |  STA PNR |
| **yu_mng** | TOP_YC | 2026/01/15 16:09:53 | yavital | `/home/scratch.yavital_vlsi/agur/yu_mng/PFNL_exp_01/pnr_flow/nv_flow/yu_mng/ipo1003/nbu_signoff` |  STA |

---

*Document Auto-Generated from Block Release Logs*  
*Generation Date: 2026-01-19 06:00:24*  
*Script: extract_agur_releases.sh*  
*Base Path: /home/agur_backend_blockRelease/block/*

## Notes

- All 5 CPORT units have both STA and FCL releases pointing to the same directory (combined release)
- Source workarea paths are extracted from the `db_source` line in block_release.log
- Flags indicate which types of files were included in each release
- Previous releases are tracked via `prev_last_sta_rel` symbolic links

