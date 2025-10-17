# Q&A Backup Document
**Avice Workarea Review Tool Presentation**

---

## Expected Questions and Detailed Answers

### Installation & Access

**Q: How do I get access to this tool?**
```
A: No installation needed! The tool is already available at:
   /home/avice/scripts/avice_wa_review_launcher.csh
   
   Just run it with your workarea path:
   /home/avice/scripts/avice_wa_review_launcher.csh /path/to/your/workarea
   
   Works for everyone - no permissions needed.
```

**Q: Do I need Python installed?**
```
A: No! The launcher script handles everything. It uses:
   /home/utils/Python/builds/3.11.9-20250715/bin/python3
   
   You don't need to set up anything.
```

---

### Usage Questions

**Q: Can I run it on any workarea?**
```
A: Yes, it works on any standard Agur/ASIC workarea structure with:
   - syn_flow/dc/ (synthesis)
   - pnr_flow/ (place & route)
   - signoff_flow/auto_pt/ (PrimeTime)
   - formal_flow/ (formal verification)
   - pv_flow/ (physical verification)
   
   It gracefully handles missing directories.
```

**Q: How long does it take to run?**
```
A: Depends on what sections you run:
   - Full analysis: 30-60 seconds
   - Selective sections (-s runtime pt): 5-10 seconds
   - Just setup: < 1 second
   
   It's much faster than manual checking!
```

**Q: Can I run only specific sections?**
```
A: Absolutely! Use the -s or --sections flag:
   
   # Just runtime and PT
   /home/avice/scripts/avice_wa_review_launcher.csh $wa -s runtime pt
   
   # Just formal and PV
   /home/avice/scripts/avice_wa_review_launcher.csh $wa -s formal pv
   
   Available sections:
   setup, runtime, synthesis, pnr, clock, formal, star, pt,
   pv, gl-check, eco, nv-gate-eco, block-release
```

**Q: Where are the HTML reports saved?**
```
A: In your current working directory (where you run the command).
   
   Files are named with timestamp:
   - avice_MASTER_dashboard_prt_20251016_143022.html
   - avice_runtime_report_prt_20251016_143022.html
   - avice_PT_timing_summary_prt_20251016_143022.html
   
   You can copy these HTML files anywhere and they'll still work!
```

---

### Bug Questions

**Q: Will you fix the formal bug?**
```
A: Yes! Fix is already in progress. 

   Current issue:
   - Tool checks for absence of "FAILED" keyword
   - Doesn't validate actual success indicators
   
   Planned fix:
   - Parse for "All points proven" or "SUCCESSFUL"
   - Distinguish between SUCCEEDED, INCONCLUSIVE, FAILED
   - Add warning when status is ambiguous
   
   Expected completion: Next 1-2 weeks
```

**Q: Are there other known bugs?**
```
A: Minor issues:
   1. Some HTML paths may break if workarea is moved (rare)
      - Fix: Use absolute paths (partially implemented)
   
   2. Fast_dc detection sometimes misses non-standard setups
      - Workaround: Check manually if runtime seems wrong
   
   3. GL Check parsing occasionally misses custom error formats
      - Workaround: Check gl-check.all.err directly
   
   These are edge cases and don't affect normal usage.
```

**Q: How do I report bugs or request features?**
```
A: Contact me directly:
   Email: avice@nvidia.com
   
   Or submit an issue with:
   - Workarea path (if possible)
   - Command you ran
   - Expected vs actual behavior
   - Screenshots if helpful
```

---

### Workflow Questions

**Q: Should new team members use this tool?**
```
A: RECOMMENDED APPROACH:
   
   Week 1-2: Learn workarea structure manually
   - Navigate directories yourself
   - Understand where files are located
   - Know the purpose of each directory
   
   Week 3+: Start using tool for efficiency
   - Quick status checks
   - Generate reports for team
   - Save time on repetitive tasks
   
   But ALWAYS keep practicing manual navigation!
```

**Q: Can I use this for block releases?**
```
A: Yes, but with caution:
   
   ✅ DO:
   - Run full analysis before release
   - Generate HTML report for documentation
   - Check runtime, timing, PV status
   
   ⚠️ DON'T RELY ON:
   - Formal verification status (verify manually!)
   - Any critical go/no-go decisions
   
   ✅ ALWAYS:
   - Manually verify formal logs
   - Double-check PV clean results
   - Review GL Check errors in detail
```

**Q: How often should I use the tool vs manual checking?**
```
A: Suggested balance:
   
   USE TOOL FOR:
   - Daily status checks (quick overview)
   - Pre-meeting reports (show team)
   - Initial triage (what needs attention?)
   - Runtime analysis (where's the bottleneck?)
   
   USE MANUAL FOR:
   - Deep debugging (understanding root cause)
   - Learning new flows (building intuition)
   - Critical verification (formal, PV)
   - When tool output seems wrong
   
   RATIO: Maybe 70% tool, 30% manual navigation
```

---

### HTML Report Questions

**Q: Can I share HTML reports with others?**
```
A: Yes! HTML reports are fully portable.
   
   You can:
   - Email them
   - Copy to shared drives
   - Open from any location
   - View on any machine with Firefox/Chrome
   
   All file links use absolute paths, so they work from anywhere.
```

**Q: Can I customize the reports?**
```
A: Currently no customization options, but planned features:
   - Custom color themes
   - Selective section inclusion
   - Custom company branding
   
   For now, reports include:
   - AVICE branding
   - Professional styling
   - All standard sections
```

**Q: How do I view log files from HTML reports?**
```
A: Two options:
   
   1. Click "View in tablog" button
      - Copies tablog command to clipboard
      - Paste in terminal to open with tablog viewer
      - Best for large log files
   
   2. Click raw file link (📄 icon)
      - Opens file:// URL in browser
      - Good for quick viewing
      - May be slow for large files
```

---

### Technical Questions

**Q: What Python version is required?**
```
A: Python 3.6 or newer.
   
   The launcher uses Python 3.11.9:
   /home/utils/Python/builds/3.11.9-20250715/bin/python3
   
   No external dependencies - uses only standard library.
```

**Q: Does it modify my workarea?**
```
A: NO! The tool is read-only.
   
   It NEVER:
   - Modifies any files in your workarea
   - Changes permissions
   - Deletes anything
   - Runs any commands that alter state
   
   It ONLY:
   - Reads log files
   - Parses reports
   - Generates HTML in YOUR current directory (not workarea)
```

**Q: Can I run it on multiple workareas at once?**
```
A: Yes! Create a simple loop:
   
   # Bash/csh loop
   foreach wa ( /path/to/wa1 /path/to/wa2 /path/to/wa3 )
       /home/avice/scripts/avice_wa_review_launcher.csh $wa
   end
   
   Or use the AGUR release tracking integration:
   - See AGUR_CPORT_RELEASES.md for batch examples
   - Run regression testing on multiple units
```

**Q: Does it work for non-Agur projects?**
```
A: Yes! It works on any ASIC workarea with standard structure:
   - Works for any project using Innovus, PrimeTime, ICC2
   - Handles Synopsys standard directory layouts
   - Gracefully skips missing directories
   
   Tested on:
   - Agur project (all chiplets)
   - Other NVIDIA projects (with minor modifications)
   - Standard ASIC design flows
```

---

### Performance Questions

**Q: Does it slow down if workarea is large?**
```
A: Minimal impact:
   - Uses efficient file parsing (doesn't load entire files)
   - Caches frequently accessed data
   - Parallel processing where possible
   
   Even with 100+ GB workareas, runtime is < 60 seconds.
```

**Q: Can I cancel if it's taking too long?**
```
A: Yes! Press Ctrl+C to cancel.
   
   The tool will:
   - Stop immediately
   - Clean up partially generated files
   - Not corrupt any workarea files (read-only)
```

---

### Comparison with Other Tools

**Q: How is this different from checking PRC status?**
```
A: Much more comprehensive:
   
   PRC status shows:
   - PnR flow progress (BEGIN/END markers)
   
   This tool shows:
   - PnR progress PLUS
   - Timing results (WNS/TNS/NVP)
   - Runtime breakdown per stage
   - Formal verification results
   - Physical verification status
   - GL Check errors
   - Synthesis QoR metrics
   - And 6 more sections!
   
   Think of it as: PRC status on steroids + 12 other analyses.
```

**Q: Is this a replacement for detailed log review?**
```
A: No - it's a COMPLEMENT, not a replacement.
   
   Tool gives you:
   - Quick overview (what's the status?)
   - Entry points (which logs to check?)
   - Red flags (what needs attention?)
   
   You still need to:
   - Review detailed logs for root cause
   - Understand timing violations
   - Debug complex issues
   
   It's like: Tool = X-ray, Manual review = Surgery
```

---

### Future Plans

**Q: What features are coming next?**
```
A: Planned for next releases:
   
   Phase 1 (Next month):
   - Fix formal status bug
   - Improve error detection
   - Add more timing metrics
   
   Phase 2 (Q1 2026):
   - Workarea comparison reports
   - Trend analysis (track metrics over time)
   - Custom report templates
   
   Phase 3 (Future):
   - Web-based dashboard
   - Real-time monitoring
   - Integration with notification systems
   
   Suggestions welcome!
```

---

## Troubleshooting During Demo

### If Demo Command Fails

**Symptom**: Command doesn't run or errors out

**Quick Fixes**:
1. Check workarea path exists:
   ```bash
   ls -ld /home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_*
   ```

2. Try backup workarea:
   ```bash
   export DEMO_WA="/home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10"
   /home/avice/scripts/avice_wa_review_launcher.csh $DEMO_WA -s runtime pt
   ```

3. Show pre-generated HTML instead:
   ```bash
   cd /home/avice/scripts/avice_wa_review/html/
   /home/utils/firefox-118.0.1/firefox avice_MASTER_dashboard_*.html
   ```

### If Firefox Won't Open

**Quick Fixes**:
1. Try different Firefox version:
   ```bash
   which firefox
   firefox avice_MASTER_dashboard_*.html &
   ```

2. Use terminal pager:
   ```bash
   less avice_MASTER_dashboard_*.html
   ```

3. Show screenshots instead (have backup ready!)

### If Terminal Output is Garbled

**Quick Fixes**:
1. Reset terminal:
   ```bash
   reset
   ```

2. Use simpler command:
   ```bash
   /home/avice/scripts/avice_wa_review_launcher.csh $DEMO_WA --no-logo -s setup
   ```

---

## Key Messages to Reinforce

Throughout the Q&A, emphasize these points:

1. **Balance is Key**
   - Tool for efficiency, manual for deep understanding
   - Don't become dependent, keep skills sharp

2. **Known Limitations**
   - Formal bug is acknowledged and being fixed
   - Always verify critical results manually
   - Trust but verify

3. **It's a Helper, Not a Replacement**
   - Augments your workflow
   - Saves time on repetitive tasks
   - You're still the expert

4. **Feedback Welcome**
   - Tool is actively maintained
   - Feature requests considered
   - Bug reports appreciated

5. **Easy to Start**
   - No installation required
   - Works from anywhere
   - Try it today!

---

**End of Q&A Backup Document**

