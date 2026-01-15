# Runtime Enhancement - Test Plan for 40 Units
## Comprehensive Testing Across All Chiplets and Flow Scenarios

**Objective:** Validate runtime detection enhancements across diverse AGUR units with varying flow completion states.

**Test Duration:** 2-3 days  
**Test Method:** Automated batch testing using `batch_review.py`  
**Data Source:** AGUR_UNITS_TABLE.csv (72 total units, testing 40 selected)

---

## Test Selection Strategy

### Selection Criteria:
1. ✅ **Chiplet Coverage:** At least 5-6 units per chiplet
2. ✅ **Flow Diversity:** Mix of completed, running, and incomplete flows
3. ✅ **IPO Variety:** Single-IPO vs multi-IPO workareas
4. ✅ **Directory Structures:** Root-level vs IPO-specific signoff
5. ✅ **Edge Cases:** Stale flows, failed flows, missing logs

### Chiplet Distribution:

| Chiplet | Units Selected | Total Available | Coverage |
|---------|---------------|-----------------|----------|
| CPORT | 5 | 5 | 100% |
| HPORT | 6 | 6 | 100% |
| HIOPL | 4 | 5 | 80% |
| NDQ | 16 | 28 | 57% |
| QNS | 6 | 19 | 32% |
| TCB | 2 | 4 | 50% |
| TOP_YC | 1 | 6 | 17% |
| **TOTAL** | **40** | **72** | **56%** |

---

## Test Units (40 Selected)

### Group 1: CPORT Chiplet (5 units - 100% coverage)

| Unit | Chiplet | Workarea Path | Test Focus |
|------|---------|---------------|------------|
| **prt** | CPORT | `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_rabin_flp/pnr_flow/nv_flow/prt/ipo1040/nbu_signoff` | IPO-specific signoff (ipo1040) |
| **fdb** | CPORT | `/home/scratch.dkolesnikov_vlsi_2/agur/fdb/PFNL/fdb_rbv_2025_11_27_condb_int4_2025_11_26_1_PFNL_snap__run1` | Root-level flows |
| **fth** | CPORT | `/home/scratch.lmustafa_vlsi/agur/fth/fth_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_cport_resize2` | Multi-IPO |
| **lnd** | CPORT | `/home/scratch.shlomoc_vlsi/agur/lnd/lnd_rbv_2025_09_26_trex_response_tag_new_flp2/pnr_flow/nv_flow/lnd/ipo1000/nbu_signoff` | IPO1000 signoff |
| **pmux** | CPORT | `/home/scratch.brachas_vlsi_1/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_nov_02` | Standard flows |

---

### Group 2: HPORT Chiplet (6 units - 100% coverage)

| Unit | Chiplet | Workarea Path | Test Focus |
|------|---------|---------------|------------|
| **ccorea** | HPORT | `/home/scratch.arcohen_vlsi_1/agur/channels/ccorea/ccorea_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref_COPY_COPY/pnr_flow/nv_flow/ccorea/ipo1009/nbu_signoff` | IPO1009 signoff |
| **ccoreb** | HPORT | `/home/scratch.arcohen_vlsi_1/agur/channels/ccoreb/ccoreb_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__copy_COPY/pnr_flow/nv_flow/ccoreb/ipo1008/nbu_signoff` | IPO1008 signoff |
| **ccorec** | HPORT | `/home/scratch.dkolesnikov_vlsi_1/agur/ccorec/1NL/ccorec_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_ref__roi_ref` | Root-level |
| **ccored** | HPORT | `/home/scratch.brachas_vlsi_1/agur/1NL/ccored/ccored_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` | Standard flows |
| **ccoree** | HPORT | `/home/scratch.ykatzav_vlsi_1/agur/ccoree/ccoree_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` | Standard flows |
| **ccoref** | HPORT | `/home/scratch.brachas_vlsi_1/agur/1NL/ccoref/ccoref_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap__updated_pins_ref_copy` | Standard flows |

---

### Group 3: HIOPL Chiplet (4 units - 80% coverage)

| Unit | Chiplet | Workarea Path | Test Focus |
|------|---------|---------------|------------|
| **ioplca** | HIOPL | `/home/scratch.ysapojnikov_vlsi/ioplca/ioplca_rbv_2024_03_17_starling_LO_fe_silver_new_flp_ref_final_2` | Legacy release |
| **ioplcb** | HIOPL | `/home/scratch.avice_vlsi_1/ioplc_units_starling/ioplcb/ioplcb_agur_exp_00/pnr_flow/nv_flow/ioplcb/ipo1003/nbu_signoff` | IPO1003 signoff |
| **ioplcc** | HIOPL | `/home/scratch.roir_vlsi_1/starling/ioplcc/ioplcc_rbv_2024_03_17_starling_LO_fe_silver_NewUphy` | Starling tag |
| **ioplcd** | HIOPL | `/home/scratch.ysapojnikov_vlsi/ioplcd/ioplcd_rbv_2024_03_17_starling_LO_fe_silver_ref_new_flp_2` | Standard flows |

---

### Group 4: NDQ Chiplet (16 units - 57% coverage)

| Unit | Chiplet | Workarea Path | Test Focus |
|------|---------|---------------|------------|
| **clt** | NDQ | `/home/scratch.aamsalem_vlsi/agur/clt/1NL/9_9_new_flow/clt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_part3` | New flow |
| **cscore** | NDQ | `/home/scratch.ynaim_vlsi/agur/1NL/cscore/cscore.cscore_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_lockup_vivid` | Vivid lockup |
| **dcmp** | NDQ | `/home/scratch.rmenasheof_vlsi_1/agur/dcmp/dcmp_9_11_updated_pins_more_intence_dc_paht_group_for_setup` | DC intensive |
| **fdbm** | NDQ | `/home/scratch.dkolesnikov_vlsi/agur/fdbm/1NL/fdbm_rbv_2025_09_02_agur_condb_int3_2025_08_27_0_1NL_snap__nov4_tpi` | TPI flow |
| **fdbs** | NDQ | `/home/scratch.brachas_vlsi/agur/1NL/fdbs/fdbs_eco_imp_2025_11_26_19_56` | ECO flow |
| **fthm** | NDQ | `/home/scratch.ayerushalmy_vlsi_1/agur/fthm/1NL/fthm_rbv_2025_09_22_condb_int3_2025_08_27_0_1NL_snap_NOV2_V2_2` | Recent release |
| **glc** | NDQ | `/home/scratch.ynaim_vlsi_1/agur/1NL/glc/glc.glc_rbv_2025_09_07_agur_condb_int3_2025_08_27_0_1NL_snap_bound_vivid` | Vivid bound |
| **ir** | NDQ | `/home/scratch.thadad_vlsi/agur/1NL/ir/ir_rbv_2025_11_05_agur_issu128_with_psc_condb_f/pnr_flow/nv_flow/ir/ipo1001/nbu_signoff` | IPO1001 signoff |
| **lndm** | NDQ | `/home/scratch.shlomoc_vlsi/agur/lndm/run_03_11_25_lndm_rbv_2025_09_01_new_flp/pnr_flow/nv_flow/lndm/ipo1000/nbu_signoff` | IPO1000 signoff |
| **nvrisc** | NDQ | `/home/scratch.ykatzav_vlsi/agur/nvrisc/nvrisc_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_run2_new_pin/pnr_flow/nv_flow/nvrisc/ipo1041/nbu_signoff` | IPO1041 signoff |
| **psca** | NDQ | `/home/scratch.nkahaz_vlsi_1/ww45_2_condb_int3_2025_08_27_0_psc_2_p2pr1/psca_rbv_2025_10_22_agur_1NL_astrix/pnr_flow/nv_flow/psca/ipo1068/nbu_signoff` | IPO1068 signoff |
| **pscb** | NDQ | `/home/scratch.nkahaz_vlsi_1/ww45_2_condb_int3_2025_08_27_0_psc_2_p2pr1/pscb_rbv_2025_10_22_agur_1NL_astrix/pnr_flow/nv_flow/pscb/ipo1024_vivid_1/nbu_signoff` | Vivid signoff |
| **pscc** | NDQ | `/home/scratch.dtraitelovic_vlsi/agur/pscc/pscc_rbv_2025_10_22_agur_1NL_astrix_new_condb/pnr_flow/nv_flow/pscc/ipo1010/nbu_signoff` | IPO1010 signoff |
| **riba** | NDQ | `/home/scratch.rmenasheof_vlsi_1/agur/riba/riba_18_11_1nl_tag_new_pins/pnr_flow/nv_flow/riba/ipo1000/nbu_signoff` | IPO1000 signoff |
| **sma** | NDQ | `/home/scratch.shlomoc_vlsi/agur/sma/run_07_09_2025_sma_rbv_2025_09_04_new_flow_dsr_fix_interface_fix` | New flow |
| **yu** | NDQ | `/home/scratch.ashahock_vlsi/agur/yu/yu_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_ver5_lib_fix` | Lib fix |

---

### Group 5: QNS Chiplet (6 units - 32% coverage)

| Unit | Chiplet | Workarea Path | Test Focus |
|------|---------|---------------|------------|
| **dqaa** | QNS | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqaa/dqaa_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_final` | Final release |
| **dqaci** | QNS | `/home/scratch.siddharthasa_vlsi/agur/1NL/dqaci/dqaci_rbv_2025_09_04_agur_condb_int3_2025_08_27_0_1NL_snap_pv_rel` | PV release |
| **dqavi** | QNS | `/home/scratch.abarman_vlsi/agur/1NL/DQAVI/1NL_run1_eco/dqavi_rbv_2025_09_09_agur_condb_int3_2025_08_27_0_1NL_snap_eco` | ECO flow |
| **dqs** | QNS | `/home/scratch.abarman_vlsi/agur/1NL/DQS/1NL_run1_SO/dqs_rbv_2025_08_28_agur_condb_int3_2025_08_27_0_snap_r1_so` | SO flow |
| **eds** | QNS | `/home/scratch.eelgabsi_vlsi/AGUR/PARTITIONS/1nl/qns/eds/eds_rbv_2025_10_06_agur_condb_int3_2025_08_27_0_r0/pnr_flow/nv_flow/eds/ipo1010_eco4/nbu_signoff` | IPO1010 ECO4 |
| **tds** | QNS | `/home/scratch.hsajwan_vlsi/agur/1NL/tds/tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN` | First run |

---

### Group 6: TCB Chiplet (2 units - 50% coverage)

| Unit | Chiplet | Workarea Path | Test Focus |
|------|---------|---------------|------------|
| **bta** | TCB | `/home/scratch.vliberchuk_vlsi_1/agur/1nl/bta/bta_2025_11_25_Nov25_no_slcg/pnr_flow/nv_flow/bta/ipo1138_inptfix_of1123_nnfp/nbu_signoff` | IPO1138 signoff |
| **eri** | TCB | `/home/scratch.hsajwan_vlsi/agur/1NL/ERI/eri_rbv_2025_09_28_timing_fixes_first_run` | Timing fixes |

---

### Group 7: TOP_YC Chiplet (1 unit - 17% coverage)

| Unit | Chiplet | Workarea Path | Test Focus |
|------|---------|---------------|------------|
| **yc_fuse_macro** | TOP_YC | `/home/scratch.lhaiby_vlsi/Agur/yc_fuse_macro/yc_fuse_agur_rbv_2025_08_11_condb_int3_2025_07_31_1_1NL_snap_12_11_arkady` | Recent release |

---

## Test Execution Plan

### Phase 1: Automated Batch Testing (Day 1)

**Command:**
```bash
cd /home/avice/scripts/avice_wa_review

# Test batch review with selected 40 units
python3 batch_review.py --units \
  prt fdb fth lnd pmux \
  ccorea ccoreb ccorec ccored ccoree ccoref \
  ioplca ioplcb ioplcc ioplcd \
  clt cscore dcmp fdbm fdbs fthm glc ir lndm nvrisc psca pscb pscc riba sma yu \
  dqaa dqaci dqavi dqs eds tds \
  bta eri \
  yc_fuse_macro \
  -s runtime --output-dir runtime_test_results/
```

**Expected Output:**
- 40 individual runtime reports (one per unit)
- Consolidated summary report
- Batch execution logs
- Error reports (if any)

**Validation Criteria:**
1. ✅ All 40 units processed successfully
2. ✅ No Python exceptions or crashes
3. ✅ HTML reports generated for each unit
4. ✅ Terminal output <30 lines per unit

---

### Phase 2: Manual Spot Checks (Day 1-2)

**Sample 10 units for detailed verification:**

| Unit | Verification Focus |
|------|-------------------|
| **prt** | IPO-specific signoff detection (ipo1040) |
| **ccorea** | Multi-flow timing (IPO1009) |
| **ioplcb** | Different IPO numbering (ipo1003) |
| **clt** | New flow structure validation |
| **dcmp** | Intensive DC runtime |
| **fdbs** | ECO flow detection |
| **psca** | High IPO number (ipo1068) |
| **dqaci** | PV flow completion |
| **bta** | TCB chiplet validation |
| **yc_fuse_macro** | TOP_YC validation |

**Manual Verification Steps:**
```bash
# For each sample unit:
python3 avice_wa_review.py -u <unit> -s runtime -vv

# Check:
# 1. Terminal output format (table structure, line count)
# 2. Status detection accuracy (RUNNING/COMPLETED/STALE)
# 3. IPO-specific flow detection
# 4. Timestamp extraction
# 5. HTML report completeness
```

---

### Phase 3: Edge Case Testing (Day 2)

**Test specific scenarios:**

#### Scenario A: RUNNING Flows
```bash
# Start a DRC flow on test unit, then run runtime analysis
# Verify: ⚙️ RUNNING status appears with elapsed time
```

#### Scenario B: STALE Flows
```bash
# Use unit with old log files (>5 min, no completion)
# Verify: ⏸️ STALE status appears
```

#### Scenario C: Mixed IPO States
```bash
# Use unit like prt with multiple IPOs (1000, 1001, 1040, ...)
# Verify: Each IPO shows correct independent status
```

#### Scenario D: Missing Logs
```bash
# Use recently created workarea with no flows yet
# Verify: - NOT RUN status, no crashes
```

---

### Phase 4: Performance Testing (Day 2)

**Metrics to collect:**

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Scan Time** | <10 sec per unit | `time python3 avice_wa_review.py -u <unit> -s runtime` |
| **Memory Usage** | <500 MB | Monitor RSS during execution |
| **HTML Gen Time** | <5 sec | Measure HTML generation phase |
| **Terminal Lines** | <30 lines | Count output lines in default mode |

**Performance Test Command:**
```bash
# Test on large multi-IPO unit
time python3 avice_wa_review.py -u prt -s runtime

# Expected:
# real  0m8.234s  ← Should be <10 seconds
# user  0m7.456s
# sys   0m0.654s
```

---

### Phase 5: Regression Testing (Day 3)

**Verify no breakage of existing functionality:**

1. **Run ALL sections** on test units:
```bash
python3 batch_review.py --units prt ccorea dqaci --output-dir regression_test/
```

2. **Compare with baseline:**
   - Terminal output format unchanged (except runtime section)
   - HTML reports still generate correctly
   - No new errors introduced

3. **Backwards Compatibility:**
   - Old runtime section still works for root-level flows
   - No regression in DC/PnR runtime detection
   - Synthesis timing unaffected

---

## Validation Checklist

### Terminal Output Validation

- [ ] **Table Structure:** Properly formatted tables with aligned columns
- [ ] **Line Count:** Default mode <30 lines (25-28 typical)
- [ ] **Status Indicators:** [OK], [RUN], [FAIL], [WARN], [--] appear correctly
- [ ] **Hierarchy:** Clear separation of Global → PnR → Signoff sections
- [ ] **Active Flows:** RUNNING flows listed in dedicated section
- [ ] **Summary Stats:** Total runtime, flow counts displayed
- [ ] **HTML Link:** Correct path shown (test_outputs/html/ or html/)

### IPO Detection Validation

- [ ] **Root-Level:** Detects signoff_flow/ in workarea root
- [ ] **IPO-Specific:** Detects ipo*/nbu_signoff/signoff_flow/
- [ ] **Multi-IPO:** Handles multiple IPOs (1000, 1001, 1040, etc.)
- [ ] **Per-IPO Flows:** Star, PT, Formal, LVS, DRC, Antenna detected
- [ ] **Work Directories:** Counts PT work directories correctly
- [ ] **IPO Numbering:** Handles non-sequential IPOs (1003, 1009, 1041, etc.)

### Status Detection Validation

- [ ] **RUNNING:** Log modified <5 min → shows elapsed time
- [ ] **COMPLETED:** Completion marker found → green status
- [ ] **FAILED:** Error patterns detected → red status
- [ ] **STALE:** Log >5 min old, no completion → gray status
- [ ] **NOT_RUN:** No log file → gray dash status
- [ ] **Timestamps:** Start/end times extracted accurately
- [ ] **Elapsed Time:** Calculated correctly for RUNNING flows

### HTML Report Validation

- [ ] **IPO Sections:** Expandable/collapsible per IPO
- [ ] **Timeline Chart:** Gantt chart visualization present
- [ ] **Active Dashboard:** RUNNING flows highlighted
- [ ] **Status Colors:** Green/Yellow/Red/Gray applied correctly
- [ ] **Log Links:** Clickable links to log files work
- [ ] **Filter Controls:** Status filter dropdown functional
- [ ] **Export Function:** CSV export button works

### Performance Validation

- [ ] **Scan Time:** <10 sec per unit (average)
- [ ] **Memory:** <500 MB RSS during execution
- [ ] **Scalability:** Works with 50+ IPO directories
- [ ] **No Hangs:** No infinite loops or stuck processes
- [ ] **Error Handling:** Graceful handling of missing/corrupt files

---

## Expected Results

### Success Criteria

**Overall:** 
- ✅ 95% of units process successfully (38/40)
- ✅ Terminal output meets line count requirement (<30 lines)
- ✅ All status types detected correctly
- ✅ HTML reports generate for all units
- ✅ Performance targets met (<10 sec/unit)

**Per Chiplet:**
- ✅ CPORT: 5/5 successful
- ✅ HPORT: 6/6 successful
- ✅ HIOPL: 4/4 successful
- ✅ NDQ: 15/16 successful (allow 1 edge case)
- ✅ QNS: 6/6 successful
- ✅ TCB: 2/2 successful
- ✅ TOP_YC: 1/1 successful

### Known Limitations (Acceptable)

1. **Legacy Units:** Units with old directory structures may not have IPO-specific flows
2. **Incomplete Flows:** Units with no signoff flows run yet will show "NOT RUN" (expected)
3. **Permission Errors:** Some scratch directories may have read restrictions (skip those)
4. **Corrupt Logs:** Truncated or binary log files may cause parse errors (handle gracefully)

---

## Issue Tracking Template

| Issue ID | Unit | Issue Description | Severity | Status |
|----------|------|-------------------|----------|--------|
| RT-001 | prt | IPO1040 not detected | HIGH | OPEN |
| RT-002 | ccorea | RUNNING status false positive | MEDIUM | FIXED |
| RT-003 | dqaci | Missing PV flow | LOW | WONTFIX |
| ... | ... | ... | ... | ... |

**Severity Levels:**
- **CRITICAL:** Crash/hang, blocking execution
- **HIGH:** Incorrect results, major feature broken
- **MEDIUM:** Partial functionality, workaround exists
- **LOW:** Cosmetic, minor issue, edge case

---

## Test Deliverables

1. **Test Execution Report:**
   - Summary of 40 unit test results
   - Pass/fail statistics per chiplet
   - Performance metrics
   - Issue tracker with all bugs found

2. **Validation Report:**
   - Checklist completion status
   - Screenshots of terminal/HTML output
   - Comparison with design specifications
   - Recommendations for improvements

3. **Documentation Updates:**
   - README updates with new runtime features
   - User guide for IPO-specific detection
   - Troubleshooting guide for common issues
   - Architecture documentation updates

4. **Code Artifacts:**
   - Test scripts and automation
   - Sample outputs (terminal + HTML)
   - Performance profiling data
   - Bug fix patches

---

## Post-Testing Actions

### If >95% Pass Rate:
1. ✅ Merge enhancements to main branch
2. ✅ Update user documentation
3. ✅ Announce new features to team
4. ✅ Monitor production usage for 1 week

### If 80-95% Pass Rate:
1. ⚠️ Fix high/critical severity issues
2. ⚠️ Re-test failed units
3. ⚠️ Conditional release (exclude problematic scenarios)
4. ⚠️ Plan follow-up fixes for next sprint

### If <80% Pass Rate:
1. ❌ Do not merge
2. ❌ Root cause analysis of failures
3. ❌ Major redesign/refactoring needed
4. ❌ Re-plan implementation approach

---

## Timeline

| Day | Activities | Deliverables |
|-----|-----------|--------------|
| **Day 1** | Phase 1 + 2 (Batch testing + spot checks) | Execution logs, initial results |
| **Day 2** | Phase 3 + 4 (Edge cases + performance) | Performance data, edge case report |
| **Day 3** | Phase 5 (Regression testing) | Final validation report, documentation |

**Total:** 3 days for complete validation

---

## Appendix: Quick Test Commands

### Test Single Unit
```bash
python3 avice_wa_review.py -u prt -s runtime
python3 avice_wa_review.py -u prt -s runtime -v  # Verbose
python3 avice_wa_review.py -u prt -s runtime -vv # Ultra-verbose
```

### Test Multiple Units (Batch)
```bash
python3 batch_review.py --units prt fdb fth -s runtime
python3 batch_review.py --chiplet CPORT -s runtime  # All CPORT units
python3 batch_review.py --random --limit 5 -s runtime  # 5 random units
```

### Test Specific IPO
```bash
python3 avice_wa_review.py -u prt -s runtime --show-ipo IPO1040
```

### Performance Profiling
```bash
time python3 avice_wa_review.py -u prt -s runtime
/usr/bin/time -v python3 avice_wa_review.py -u prt -s runtime  # Detailed memory
```

### HTML Report Validation
```bash
# Generate report
python3 avice_wa_review.py -u prt -s runtime

# Open in browser
/home/utils/firefox-118.0.1/firefox test_outputs/html/*_runtime_report_*.html &
```

---

**Test Plan Author:** Alon Vice (avice@nvidia.com)  
**Date:** December 4, 2025  
**Status:** READY FOR EXECUTION  
**Estimated Duration:** 3 days

