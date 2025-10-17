# Avice Workarea Review Tool - Agur Team Presentation
**Alon Vice (avice) - October 16, 2025**  
**Duration: 25 minutes**

---

## Slide 1: Title (1 min)

**Avice Workarea Review Tool**
- Comprehensive ASIC workarea analysis utility
- From RTL to GDSII - complete flow review
- Today: Live demo + practical usage

---

## Slide 2: Why This Tool? (2 min)

### The Problem
- Designers manually navigate complex workarea structures
- Checking multiple log files across different directories
- Manually parsing timing reports, runtime logs, formal results
- Time-consuming and error-prone process

### The Solution
- **One command** - complete workarea analysis
- **Automated extraction** of all key metrics
- **HTML reports** with clickable links
- **Quick status checks** without deep diving

---

## Slide 3: Tool Overview (2 min)

### What It Analyzes (13 Sections)
1. **Setup** - Design info, tags, configuration
2. **Synthesis (DC)** - QoR metrics, scenarios, timing groups
3. **Place & Route (PnR)** - Status, key parameters, utilization
4. **Clock Analysis** - Clock tree metrics
5. **Formal Verification** - Formal status and results
6. **Parasitic Extraction (Star)** - SPEF generation status
7. **Signoff Timing (PT)** - WNS/TNS/NVP, DSR skew
8. **Physical Verification (PV)** - LVS, DRC, antenna
9. **GL Check** - Gate-level check results
10. **ECO Analysis** - PT-ECO fixes
11. **NV Gate ECO** - NVIDIA Gate ECO
12. **Runtime** - Flow timing breakdown
13. **Block Release** - Release status

---

## Slide 4: How to Use It - Basic Commands (3 min)

### Recommended Usage (C-shell launcher)
```bash
# Basic review - all sections
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea

# Specific IPO
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea ipo1000

# Selective sections (faster)
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s setup dc pnr pt runtime

# Available sections:
# setup, runtime, synthesis (dc), pnr, clock, formal, star, pt, 
# pv, gl-check, eco, nv-gate-eco, block-release
```

### Why Use the Launcher?
- Handles Python path automatically
- Works from any directory
- No need to set up Python environment
- Just works!

---

## Slide 5: LIVE DEMO - Part 1 (5 min)

### Demo Command
```bash
# Using an Agur CPORT workarea
cd /home/avice/scripts/avice_wa_review

# Full analysis
/home/avice/scripts/avice_wa_review_launcher.csh \
  /home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap

# Quick check (runtime + PT only)
/home/avice/scripts/avice_wa_review_launcher.csh \
  /home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap \
  -s runtime pt formal
```

### What to Show
1. **Terminal output** - color-coded sections
2. **Key metrics** - timing, runtime, formal status
3. **HTML generation** - automatic report creation

---

## Slide 6: LIVE DEMO - Part 2 - HTML Reports (3 min)

### Opening HTML Reports
```bash
# Master Dashboard (comprehensive view)
/home/utils/firefox-118.0.1/firefox avice_MASTER_dashboard_*.html

# Individual reports
/home/utils/firefox-118.0.1/firefox avice_runtime_report_*.html
/home/utils/firefox-118.0.1/firefox avice_PT_timing_summary_*.html
```

### HTML Features to Demonstrate
- **Clickable links** to log files
- **Tablog integration** for log viewing
- **Expandable sections** in master dashboard
- **Detailed tables** with color coding
- **Portable** - works from any location

---

## Slide 7: Key Features & Advantages (3 min)

### ✅ Advantages

1. **Time Savings**
   - One command replaces 30+ manual checks
   - Instant status overview
   - No need to remember log file paths

2. **Comprehensive Coverage**
   - All flow stages in one report
   - Catches issues you might miss
   - Formal-to-netlist timestamp verification

3. **Professional HTML Reports**
   - Share with team members
   - Clickable links to all logs
   - Complete audit trail

4. **Portable & Easy**
   - Works from any directory
   - No setup required
   - Cross-user compatible

5. **Smart Analysis**
   - Auto-detects fast_dc flows
   - Tracks running vs completed flows
   - Calculates runtime breakdowns

---

## Slide 8: Known Issues & Limitations (3 min)

### ⚠️ DISADVANTAGES - IMPORTANT!

#### 1. **Directory Structure Knowledge Loss**
**The Big Risk**: Designers can become too dependent on the tool and lose familiarity with workarea structure.

**Real Impact**:
- Don't know where to find `gl-check.all.err` manually
- Forget the difference between `signoff_flow/auto_pt/` and `pnr_flow/`
- Can't troubleshoot when tool has bugs

**Recommendation**:
- Use tool for **quick reviews** and **sharing reports**
- Still navigate directories manually for **deep debugging**
- New team members should **learn directory structure first** before using tool

#### 2. **File Location Amnesia**
- Users forget where key files live:
  - PrimeTime reports: `signoff_flow/auto_pt/work_*/reports/`
  - PnR logs: `pnr_flow/nv_flow/prc.status`
  - Synthesis QoR: `syn_flow/dc/latest/results/*.qor`
  - Formal logs: `formal_flow/*/logs/`

**Solution**: Keep a cheat sheet of critical paths!

---

## Slide 9: Known Bugs (2 min)

### 🐛 Bug #1: Formal Status Misreporting

**Issue**: Tool shows "SUCCEEDED" but actual status is "INCONCLUSIVE"

**Example**:
```
Tool Output:  [OK] Formal verification SUCCEEDED
Real Status:  INCONCLUSIVE - need to check manually
```

**Root Cause**: Parsing logic checks for absence of "FAILED" keyword, not actual success indicators

**Workaround**: 
- Always **manually verify formal status** in critical releases
- Check formal log directly: `formal_flow/*/logs/*.log`
- Look for "All points proven" (real success)

**Status**: Fix in progress - will improve formal log parsing

### 🐛 Bug #2: Occasional Path Resolution Issues
- Some relative paths in HTML may break if workarea is moved
- **Fix**: Use absolute paths in HTML reports (partially implemented)

---

## Slide 10: Best Practices (2 min)

### ✅ Recommended Workflow

1. **Initial Check** - Use tool for quick status
   ```bash
   /home/avice/scripts/avice_wa_review_launcher.csh $workarea -s runtime pt formal pv
   ```

2. **Deep Dive** - Navigate directories manually for debugging
   ```bash
   cd signoff_flow/auto_pt/work_*/
   cat *.log
   ```

3. **Sharing Results** - Generate HTML report
   ```bash
   /home/avice/scripts/avice_wa_review_launcher.csh $workarea
   # Share the HTML with team
   ```

4. **Critical Releases** - Always verify formal manually
   ```bash
   cd formal_flow/*/logs/
   grep -i "inconclusive\|proven\|failed" *.log
   ```

### ⚠️ When NOT to Use
- **Deep debugging sessions** - use manual navigation
- **Learning a new design** - explore directories first
- **Critical formal verification** - always double-check logs

---

## Slide 11: Real-World Examples (2 min)

### Example 1: Quick Status Check Before Release
```bash
# Check if workarea is ready for block release
/home/avice/scripts/avice_wa_review_launcher.csh $workarea \
  -s formal pt pv gl-check

# Look for:
# - Formal: SUCCEEDED (but verify manually!)
# - PT: WNS/TNS passing
# - PV: LVS/DRC clean
# - GL Check: No errors
```

### Example 2: Debug Long Runtime
```bash
# Check which PnR stage is taking longest
/home/avice/scripts/avice_wa_review_launcher.csh $workarea -s runtime

# Output shows:
# - Total runtime: 45.2 hours
# - Longest stage: postroute (12.3 hours) <- Investigate this!
```

### Example 3: Compare Two Workareas
```bash
# Generate reports for both
/home/avice/scripts/avice_wa_review_launcher.csh $workarea1 -s pt
/home/avice/scripts/avice_wa_review_launcher.csh $workarea2 -s pt

# Compare HTML reports side-by-side in browser
```

---

## Slide 12: Advanced Features (1 min)

### Master Dashboard
- Single HTML with all 13 sections
- Expandable cards
- Quick navigation
- Statistics summary

### Selective Analysis
- Run only sections you need
- Much faster for targeted checks
- Reduces noise

### Tablog Integration
- Clickable "View in tablog" buttons
- Automatic command copy to clipboard
- Quick log file inspection

---

## Slide 13: Summary & Q&A (1 min)

### Key Takeaways

✅ **Use the tool for**:
- Quick status checks
- Generating reports for team
- First-pass analysis
- Runtime analysis

⚠️ **Don't forget**:
- Learn directory structure first
- Verify formal status manually
- Navigate directories for deep debugging
- Keep your manual skills sharp!

### Questions?

---

## DEMO SCRIPT - For Presenter

### Setup (Before Presentation)
```bash
cd /home/avice/scripts/avice_wa_review

# Clean up old HTML files
mv *.html html/ 2>/dev/null

# Choose a workarea for demo
export DEMO_WA="/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap"
```

### Demo Step 1: Basic Usage (Terminal)
```bash
# Show help first
/home/avice/scripts/avice_wa_review_launcher.csh --help | head -50

# Run basic analysis (runtime + PT only for speed)
/home/avice/scripts/avice_wa_review_launcher.csh $DEMO_WA -s runtime pt
```

**Talk while running**:
- "Tool extracts runtime breakdown from PRC status"
- "Shows PrimeTime timing results - WNS, TNS, NVP"
- "Color-coded output for quick scanning"

### Demo Step 2: HTML Report (Browser)
```bash
# Open generated HTML
/home/utils/firefox-118.0.1/firefox avice_runtime_report_*.html &
```

**Show in browser**:
1. Click "View in tablog" button → copies command
2. Show detailed tables
3. Click on a log file link → opens in new tab
4. Scroll to show footer (copyright)

### Demo Step 3: Show Known Bug (Formal)
```bash
# Run formal section
/home/avice/scripts/avice_wa_review_launcher.csh $DEMO_WA -s formal

# Then show actual log
cd $DEMO_WA/formal_flow/
ls -la
cat */logs/*.log | grep -i "inconclusive\|proven"
```

**Point out**: "See how tool shows success, but log says inconclusive? This is the bug!"

### Cleanup After Demo
```bash
cd /home/avice/scripts/avice_wa_review
mv *.html html/
```

---

## PRESENTATION TIMING BREAKDOWN

| Slide | Topic | Time | Cumulative |
|-------|-------|------|------------|
| 1 | Title | 1 min | 1 min |
| 2 | Why This Tool? | 2 min | 3 min |
| 3 | Tool Overview | 2 min | 5 min |
| 4 | How to Use It | 3 min | 8 min |
| 5 | Live Demo Part 1 | 5 min | 13 min |
| 6 | Live Demo Part 2 | 3 min | 16 min |
| 7 | Advantages | 3 min | 19 min |
| 8 | Disadvantages | 3 min | 22 min |
| 9 | Known Bugs | 2 min | 24 min |
| 10 | Best Practices | 2 min | 26 min |
| 11 | Real-World Examples | 2 min | 28 min |
| 12 | Advanced Features | 1 min | 29 min |
| 13 | Summary & Q&A | Variable | 30 min |

**Core Presentation**: 24 minutes  
**Buffer for Q&A**: 6 minutes  
**Total**: 30 minutes (fits 25-minute target with Q&A)

---

## TALKING POINTS - Quick Reference

### Opening (Strong Hook)
"How many times have you spent 30 minutes navigating through workarea directories, checking logs, parsing timing reports? Today I'll show you a tool that does all of this in one command."

### Advantages (Emphasize)
- Time savings: "One command replaces 30+ manual checks"
- Comprehensive: "Catches issues you might miss"
- Professional reports: "Share with team, management"

### Disadvantages (Be Honest)
- "**This is important** - don't become dependent on tools"
- "You need to know where files are for debugging"
- "New designers: learn the structure FIRST, tool SECOND"

### Bug Disclosure (Build Trust)
- "I want to be transparent about a known issue"
- "Formal status can show SUCCEEDED when it's INCONCLUSIVE"
- "Always verify formal manually for releases"
- "Fix is in progress"

### Closing (Call to Action)
"Use the tool smartly - for quick checks and reports, but keep your manual skills sharp. Questions?"

---

## BACKUP SLIDES - If Time Permits

### Backup: AGUR Release Tracking
- Separate utility for tracking block releases
- Automated extraction of release metadata
- Interactive dashboard with regression testing
- Not integrated with main tool (standalone)

### Backup: Installation & Setup
```bash
# Tool location
/home/avice/scripts/avice_wa_review/

# Launcher script
/home/avice/scripts/avice_wa_review_launcher.csh

# No installation needed - just run!
```

### Backup: Future Roadmap
- Fix formal status parsing bug
- Add more flow stages (if requested)
- Improve HTML report features
- Better error detection and warnings

---

**End of Presentation Document**

---

## PRESENTER CHECKLIST

- [ ] Test demo workarea path is accessible
- [ ] Clean up old HTML files before demo
- [ ] Verify Firefox 118 is available
- [ ] Practice demo commands
- [ ] Prepare terminal window with large font
- [ ] Have backup workarea path ready
- [ ] Print this document for reference
- [ ] Time yourself - aim for 24 minutes
- [ ] Prepare answers for expected questions
- [ ] Have example HTML reports ready to show

**Good luck with your presentation!**

