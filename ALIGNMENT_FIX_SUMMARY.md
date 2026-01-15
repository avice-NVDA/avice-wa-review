===============================================================================
       IPO SIGNOFF ALIGNMENT FIX + BOTTLENECK COLOR CLARIFICATION
===============================================================================

ISSUE 1: POSTROUTE ORANGE/YELLOW COLOR
---------------------------------------

Question: Why is Postroute showing in orange/yellow?

Answer: ✅ **It's the BOTTLENECK indicator**

The yellow color (Color.YELLOW) is applied to the longest-running stage/flow:
- Postroute (ipo1000): 20.99h (22% of total runtime)
- This is the longest single stage in the entire flow
- The "*" symbol and percentage "(22%)" confirm it's the bottleneck
- This helps identify optimization targets immediately

Color coding:
- 🟢 GREEN: Normal completed stages
- 🟡 YELLOW: Bottleneck (longest runtime) with "%" and "*"
- 🔵 CYAN: Currently RUNNING with "⚡"

Example output:
```
PnR    Postroute (ipo1000)  20.99h (22%) [12/01 21:08 -> 12/02 18:08] [OK] *
       ↑                      ↑      ↑                                    ↑
    Yellow color          Runtime  %    Standard timeline              Bottleneck
```

ISSUE 2: SIGNOFF ALIGNMENT BROKEN BY "(ipo*)" SUFFIX
-----------------------------------------------------

Problem:
```
Signoff      Star (ipo1000)       0.69h      [12/4 10:01 -> 12/4 10:36] [OK]
Signoff      Formal_Rtl_Pnr (ipo1000) 2.31h  [12/06 18:24 -> 12/06 20:43] [OK]
Signoff      Formal_Bbox (ipo1000) 3.61h     [12/06 18:25 -> 12/06 22:02] [OK]
             ↑
      Flow names have different lengths → columns misaligned
```

Solution: ✅ **IPO HEADERS instead of suffixes**

NEW FORMAT (Multi-IPO workareas):
```
Signoff      [IPO1000]
Signoff      Star                 0.44h      [11/12 21:22 -> 11/12 21:45] [OK]
Signoff      Auto_Pt              6.14h      [11/13 08:42 -> 11/13 14:50] [OK]
Signoff      Auto_Pt_Fix          0.85h      [11/14 10:52 -> 11/14 11:43] [OK]
             IPO1000 Signoff Subtotal: 7.43h    [11/12 21:22 -> 11/14 11:43]

Signoff      [IPO1001]
Signoff      Star                 0.49h      [11/12 21:23 -> 11/12 21:49] [OK]
Signoff      Auto_Pt              5.65h      [11/18 14:58 -> 11/18 20:37] [OK]
...
             IPO1001 Signoff Subtotal: 16.65h    [11/12 21:23 -> 11/19 20:12]

Signoff      [ROOT]
Signoff      Star                 0.46h      [11/26 08:02 -> 11/26 08:27] [OK]
...
```

Benefits:
1. ✅ **Perfect Alignment**: All flow names start at same column
2. ✅ **Clear Grouping**: Cyan headers separate IPO sections visually
3. ✅ **Cleaner Display**: No redundant "(ipo1000)" on every line
4. ✅ **Scalable**: Works for 1-20 IPOs without breaking alignment

SINGLE-IPO FORMAT (Unchanged):
```
Signoff      Star                 0.69h      [12/4 10:01 -> 12/4 10:36] [OK]
Signoff      Formal_Rtl_Pnr       2.31h      [12/06 18:24 -> 12/06 20:43] [OK]
Signoff      Formal_Bbox          3.61h      [12/06 18:25 -> 12/06 22:02] [OK]
```

No header needed for single IPO - cleaner output.

TECHNICAL IMPLEMENTATION
------------------------

Changed code in `_print_unified_flow_timeline_table()`:

OLD APPROACH:
```python
# Add IPO suffix to every flow name
flow_with_ipo['name'] = f"{flow['name']} ({ipo})"
```

NEW APPROACH:
```python
# Print IPO header once before flows
if len(signoff_by_ipo) > 1:
    ipo_label = ipo.upper() if ipo != 'root' else 'ROOT'
    print(f"{Color.CYAN}Signoff      [{ipo_label}]{Color.RESET}")

# Print flows WITHOUT suffix
for flow in flows:
    self._print_flow_row(flow, bottleneck_flow, grand_total_hours)
```

TEST RESULTS
------------

1. lnd (Single IPO) ✅
   - No IPO headers (clean single-IPO view)
   - Perfect alignment maintained
   - All flow names uniform length

2. pmux (4 IPOs: ipo1000, ipo1001, ipo1002, root) ✅
   - Cyan headers for each IPO section
   - Perfect alignment across all 18 signoff flows
   - Clear visual separation between IPOs
   - Subtotals work correctly

COLUMN ALIGNMENT COMPARISON
----------------------------

BEFORE (Broken):
```
Signoff      Star (ipo1000)       0.44h      [11/12 21:22 -> 21:45] [OK]
Signoff      Auto_Pt (ipo1000)    6.14h      [11/13 08:42 -> 14:50] [OK]
Signoff      Auto_Pt_Fix (ipo1000) 0.85h     [11/14 10:52 -> 11:43] [OK]
             ↑
        Misaligned due to different name lengths
```

AFTER (Fixed):
```
Signoff      [IPO1000]
Signoff      Star                 0.44h      [11/12 21:22 -> 21:45] [OK]
Signoff      Auto_Pt              6.14h      [11/13 08:42 -> 14:50] [OK]
Signoff      Auto_Pt_Fix          0.85h      [11/14 10:52 -> 11:43] [OK]
             ↑
        Perfect alignment - all names uniform
```

BENEFITS SUMMARY
----------------

✅ **Visual Clarity**: Headers separate IPO sections clearly
✅ **Perfect Alignment**: All columns properly aligned
✅ **Cleaner Output**: No redundant text on every line
✅ **Easy Scanning**: Cyan headers make sections stand out
✅ **Scalable**: Works for any number of IPOs
✅ **Smart Display**: Single IPO doesn't show headers (cleaner)

STATUS: ✅ BOTH ISSUES RESOLVED AND TESTED

===============================================================================
