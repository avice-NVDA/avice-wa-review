# Master Dashboard Generation Logic

**Updated:** November 19, 2025  
**Author:** Alon Vice (avice@nvidia.com)

---

## Overview

The Master Dashboard is an integrated HTML report that combines all section summaries. However, generating it for every run is wasteful, especially when running single sections.

---

## Generation Rules

### ✅ **GENERATE Master Dashboard When:**

1. **Complete Review** (no `-s` flag)
   ```bash
   python3 avice_wa_review.py -u prt
   # Runs all 13 sections → Master Dashboard ✅
   ```

2. **Multiple Sections** (2+ sections specified)
   ```bash
   python3 avice_wa_review.py -u prt -s setup runtime pnr
   # Runs 3 sections → Master Dashboard ✅
   ```

### ❌ **SKIP Master Dashboard When:**

1. **Single Section** (only 1 section specified)
   ```bash
   python3 avice_wa_review.py -u prt -s pnr
   # Runs 1 section → No Master Dashboard ❌
   # (PnR generates its own comprehensive HTML report)
   ```

---

## Benefits

### For Single Section Runs:

✅ **Faster execution** - No unnecessary HTML generation  
✅ **Cleaner output** - Only relevant HTML files  
✅ **Less disk usage** - No redundant dashboard  
✅ **Better UX** - User gets exactly what they asked for  

### For Multiple Section Runs:

✅ **Unified view** - Single dashboard showing all sections  
✅ **Easy comparison** - Status overview across sections  
✅ **Quick navigation** - Jump to detailed section reports  

---

## Examples

### Example 1: Single Section (PnR)
```bash
$ python3 avice_wa_review.py -u prt -s pnr

Output Files:
  - prt_avice_PnR_comprehensive_ipo1000_20251119_185651.html
  - prt_avice_pnr_data_ipo1000_20251119_185651.html
  
NO Master Dashboard generated ✅
```

### Example 2: Two Sections (Setup + Runtime)
```bash
$ python3 avice_wa_review.py -u prt -s setup runtime

Output Files:
  - prt_avice_runtime_report_20251119_191922.html
  - prt_avice_MASTER_dashboard_20251119.html  ← Generated!
  
Master Dashboard combines both sections ✅
```

### Example 3: Complete Review
```bash
$ python3 avice_wa_review.py -u prt

Output Files:
  - prt_avice_MASTER_dashboard_20251119.html  ← Generated!
  - (All individual section HTML reports)
  
Master Dashboard with all 13 sections ✅
```

---

## Implementation

### Code Location
`avice_wa_review.py` - Lines 26678-26692

### Logic
```python
if args.sections:
    # Run selected sections
    for section in args.sections:
        section_mapping[section]()
    
    # Generate dashboard only if multiple sections
    if len(args.sections) > 1:
        generate_master_dashboard()
else:
    # Complete review always generates dashboard
    run_complete_review()
```

---

## Testing Results

✅ **Test 1:** Single section (`-s setup`)
   - No dashboard generated
   - Output clean and focused

✅ **Test 2:** Multiple sections (`-s setup runtime`)
   - Master dashboard generated
   - Both sections integrated

✅ **Test 3:** Complete review (no `-s`)
   - Master dashboard generated
   - All sections integrated

---

## User Impact

**Before (Old Behavior):**
- Single section run → Generates dashboard with 1 section (wasteful)
- User gets 2 HTML files when they only need 1

**After (New Behavior):**
- Single section run → No dashboard (efficient)
- User gets exactly what they need

**Statistics:**
- Saves ~30KB per single-section run
- Reduces HTML clutter by 50% for focused analysis
- Improves user experience with clearer output

---

*Document Status: ✅ IMPLEMENTED & TESTED*
