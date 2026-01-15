================================================================================
PT HTML REPORT - COMPREHENSIVE IMPROVEMENT PLAN
================================================================================
Generated: December 2, 2025
For: Sir avice
Project: avice_wa_review.py

================================================================================
PHASE 1: ANALYSIS - CURRENT STATE vs DESIRED STATE
================================================================================

## Current PT HTML Report (OLD):
----------------------------------
✅ Basic dual-scenario timing tables (Setup/Hold side-by-side)
✅ DSR skew tracking across work directories
✅ Basic styling and logo
❌ Missing: Multi-location support (IPO tracking)
❌ Missing: Quality metrics (Data vs Clock violations)
❌ Missing: Status indicators (COMPLETED/RUNNING/STALE)
❌ Missing: Constraint violation details
❌ Missing: Clock quality metrics
❌ Missing: Interactive filtering/sorting
❌ Missing: Power analysis data
❌ Missing: Tablog integration for reports
❌ Missing: Source file attribution

## Current Terminal Output (NEW - What HTML Should Include):
-------------------------------------------------------------
✅ Multi-location PT detection (root + per-IPO)
✅ Status tracking per location (COMPLETED/RUNNING/STALE/NO_WORK_DIRS)
✅ Unified timing summary (Setup + Hold side-by-side, all path groups)
✅ Quality Metrics table (Data vs Clock signals)
  - Data: Tran, Cap, Fanout
  - Clock: Tran, Cap, Slew, XCap
✅ DSR Skew Trend (with source attribution)
✅ Power analysis (all FSDB tests, trend tracking)

================================================================================
PHASE 2: HTML ENHANCEMENT GOALS
================================================================================

### PRIMARY GOALS:
1. **Multi-Location Support** - Show all PT runs (IPO1000-IPO1040, root, etc.)
2. **Quality Metrics Dashboard** - Comprehensive violations tracking
3. **Interactive Features** - Filter/sort/search capabilities
4. **Source Attribution** - Links to all source reports
5. **Status Indicators** - Visual status badges
6. **Tablog Integration** - One-click log opening

### SECONDARY GOALS:
1. Trend visualization (charts/graphs for quality metrics)
2. Export capabilities (CSV/Excel)
3. Print-friendly views
4. Mobile responsiveness
5. Dark mode toggle

================================================================================
PHASE 3: DETAILED FEATURE BREAKDOWN
================================================================================

## SECTION 1: Overview Dashboard (NEW!)
---------------------------------------
**Purpose**: High-level summary at the top of the report

**Content**:
  • Design Information (name, workarea, generation time)
  • PT Locations Summary:
    - Total locations found: N
    - IPO labels: IPO1000, IPO1010, IPO1020...
    - Status breakdown: X COMPLETED, Y RUNNING, Z STALE
    - Latest work directory: work_DD.MM.YY_HH:MM [IPOXXXX]
  • Quick Stats Cards:
    - Total Work Directories: N
    - Total Timing Violations: WNS/TNS/NVP
    - Total Quality Violations: Data + Clock
    - DSR Skew Range: Min-Max ps
  • Status Indicators:
    - Color-coded badges (Green/Yellow/Red)
    - Quick filters (Show only RUNNING, Show only with violations)

**Layout**: CSS Grid with 4 info cards, responsive

**Priority**: HIGH (Foundation for rest of report)
**Effort**: 3-4 hours
**Dependencies**: None


## SECTION 2: Location Explorer (NEW!)
--------------------------------------
**Purpose**: Detailed view of all PT locations with drill-down

**Content**:
  • Table of all PT locations:
    ┌──────────────────────────────────────────────────────────────────┐
    │ Location    │ Status    │ Work Dirs │ Latest Work     │ Actions │
    ├──────────────────────────────────────────────────────────────────┤
    │ IPO1040     │ COMPLETED │ 5         │ work_27.11.25   │ [View]  │
    │ IPO1030     │ COMPLETED │ 3         │ work_26.11.25   │ [View]  │
    │ IPO1020     │ RUNNING   │ 2         │ work_12.11.25   │ [View]  │
    │ signoff_flow│ STALE     │ 1         │ work_10.11.25   │ [View]  │
    └──────────────────────────────────────────────────────────────────┘
  
  • Expandable rows showing work directories per location
  • Status badges with color coding
  • Quick actions: View logs, View reports, Compare

**Features**:
  - Sort by status, location, work dirs count
  - Filter by status (COMPLETED only, etc.)
  - Search by location name
  - Expand/collapse rows

**Priority**: HIGH
**Effort**: 4-5 hours
**Dependencies**: Section 1 (for filters)


## SECTION 3: Unified Timing Summary (ENHANCED)
-----------------------------------------------
**Purpose**: Comprehensive timing analysis for latest work dir

**Current**: Basic Setup/Hold tables
**Enhanced**:
  • Scenario Information:
    - Setup Corner: func.std_tt_0c_0p6v.setup.typical
    - Hold Corner: func.std_ffg_0c_0p5v.hold.typical
    - Source: [Link to *.timing files]
  
  • Unified Timing Table (ALL path groups):
    ┌─────────────────────────────────────────────────────────────────────┐
    │ Path Group   │ Setup WNS│ Setup TNS│ Setup NVP│ Hold WNS│ Hold TNS │
    ├─────────────────────────────────────────────────────────────────────┤
    │ TOTAL (Int)  │  -0.098  │  -0.10   │   2      │ -0.014  │  -0.08   │
    │ i2_clk       │   0.001  │   0.00   │   0      │ -0.007  │  -0.04   │
    │ w1_clk       │   0.001  │   0.00   │   0      │ -0.014  │  -0.04   │
    │ ...          │   ...    │   ...    │   ...    │  ...    │   ...    │
    │ FEEDTHROUGH  │   0.000  │   0.00   │   0      │  0.000  │   0.00   │
    └─────────────────────────────────────────────────────────────────────┘
  
  • Color coding:
    - Green: WNS >= 0, TNS >= 0
    - Yellow: WNS < 0 but > -0.050, TNS < 0 but > -1.0
    - Red: WNS <= -0.050 or TNS <= -1.0
  
  • Sort by: WNS, TNS, NVP (interactive)
  • Export to Excel button
  • Link to PT HTML reports (tablog integration)

**Priority**: HIGH
**Effort**: 3-4 hours
**Dependencies**: Tablog integration


## SECTION 4: Quality Metrics Dashboard (NEW!)
----------------------------------------------
**Purpose**: Comprehensive quality violations tracking

**Content**:
  • Quality Summary Cards:
    ┌─────────────────┬─────────────────┬─────────────────┐
    │  Data Signals   │ Clock Signals   │  Overall Status │
    │  Tran: 1288     │ Tran: 0         │   ⚠ WARNING    │
    │  Cap:  0        │ Cap:  0         │   Issues: 2    │
    │  Fanout: 0      │ Slew: 0         │   Clean: 5     │
    │                 │ XCap: 1         │                │
    └─────────────────┴─────────────────┴─────────────────┘
  
  • Detailed Quality Table (All Work Dirs):
    ┌──────────────────────────────────────────────────────────────────┐
    │ Work Dir      │  -- Data --  │  -- Clock --  │ Location │ Date  │
    │               │ Trn Cap Fan  │ Trn Cap Slw X │          │       │
    ├──────────────────────────────────────────────────────────────────┤
    │ work_27.11.25 │  0   12  0   │  0   0   0  0 │ IPO1040  │ Nov27 │
    │ work_26.11.25 │  0   12  0   │  0   0   0  0 │ IPO1030  │ Nov26 │
    │ work_10.11.25 │ 176  12  0   │  0   0   0  1 │ IPO1000  │ Nov10 │
    └──────────────────────────────────────────────────────────────────┘
  
  • Trend Visualization:
    - Line chart showing violations over time
    - Separate lines for each violation type
    - X-axis: Work directories (chronological)
    - Y-axis: Violation count
  
  • Violation Details (Expandable):
    - Click row to see detailed report paths
    - Link to source files (tablog integration):
      * *.all_violators.tran.gz
      * *.all_violators.cap.gz
      * *.all_violators.max_fanout.gz
      * *.clock_violators.gz
      * *.clock_slopes_and_xcap
  
  • Filters:
    - Show only violations > 0
    - Filter by location (IPO)
    - Filter by date range
  
  • Export buttons:
    - Export table to CSV
    - Export chart as PNG

**Priority**: CRITICAL (Most valuable new feature)
**Effort**: 6-8 hours
**Dependencies**: Chart.js library, Tablog integration


## SECTION 5: DSR Skew Trend Analysis (ENHANCED)
------------------------------------------------
**Purpose**: Track DSR skew improvements/regressions

**Current**: Basic table with setup/hold skew
**Enhanced**:
  • Scenario Information with source attribution
  • Detailed DSR Skew Table:
    ┌──────────────────────────────────────────────────────────────────┐
    │ Work Dir      │ Setup Skew │ Hold Skew │ Location │ Trend       │
    ├──────────────────────────────────────────────────────────────────┤
    │ work_27.11.25 │  12.01 ps  │  18.02 ps │ IPO1040  │ ↓ Improved │
    │ work_26.11.25 │  12.03 ps  │  18.04 ps │ IPO1030  │ ↓ Improved │
    │ work_10.11.25 │  12.07 ps  │  18.11 ps │ IPO1000  │ Baseline   │
    └──────────────────────────────────────────────────────────────────┘
  
  • Trend Visualization:
    - Dual-axis chart (Setup vs Hold)
    - X-axis: Work directories
    - Y-axis: Skew in picoseconds
    - Color: Green (<=10ps), Yellow (10-20ps), Red (>20ps)
  
  • Statistical Summary:
    - Best: X.XX ps (work_XX.XX.XX)
    - Worst: Y.YY ps (work_YY.YY.YY)
    - Average: Z.ZZ ps
    - Std Dev: A.AA ps
    - Overall Trend: Improving/Degrading/Stable
  
  • Source Files:
    - Links to *.dsr_mux_clock_skew files (tablog)
    - One link per work directory

**Priority**: MEDIUM-HIGH
**Effort**: 4-5 hours
**Dependencies**: Chart.js, Tablog integration


## SECTION 6: Power Analysis (NEW!)
-----------------------------------
**Purpose**: Show power analysis data from PT

**Content**:
  • Power Corner Information:
    - Corner: func.std_tt_105c_0p67v.setup.typical
    - Note: "Power estimation corner (not timing-critical)"
  
  • Power Tests Summary Table:
    ┌──────────────────────────────────────────────────────────────────┐
    │ Test Name             │ Total  │ Dynamic│ Leakage│ AF(FF/Q)│ Score│
    ├──────────────────────────────────────────────────────────────────┤
    │ power_vectorless_PT   │ 824 mW │ 764 mW │  60 mW │  3.44%  │ N/A  │
    │ power_vectorless_Idle │ 113 mW │  53 mW │  60 mW │  0.00%  │ N/A  │
    └──────────────────────────────────────────────────────────────────┘
  
  • Power Trend Analysis:
    - Table showing power across all work dirs
    - Trend indicators (increased/decreased/stable)
    - % change from oldest to newest
  
  • Power Breakdown Chart:
    - Stacked bar chart (Dynamic vs Leakage)
    - X-axis: Test names
    - Y-axis: Power in mW

**Priority**: LOW-MEDIUM (Nice to have, already in terminal)
**Effort**: 3-4 hours
**Dependencies**: Chart.js


## SECTION 7: Report Navigator (NEW!)
-------------------------------------
**Purpose**: Quick access to all source reports

**Content**:
  • Organized by category:
    
    **Timing Reports** (per work directory):
      - Setup Corner Report [View in tablog] [Download]
      - Hold Corner Report [View in tablog] [Download]
      - PT HTML Summary [Open]
      - PT Log File [View in tablog]
    
    **Quality Reports**:
      - Data Violations: Tran, Cap, Fanout [View] [Download]
      - Clock Violations [View] [Download]
      - Clock Slopes & XCap [View] [Download]
    
    **Clock Reports**:
      - DSR Mux Clock Skew [View] [Download]
      - Clock Timing [View] [Download]
      - Clock Latency [View] [Download]
    
    **Power Reports**:
      - Power Analysis (per test) [View] [Download]
  
  • Tablog Integration:
    - All "View" buttons use tablog server
    - Fallback to clipboard copy if server unavailable
    - Visual indicator for tablog status

**Priority**: MEDIUM
**Effort**: 3-4 hours
**Dependencies**: Tablog integration (critical)


## SECTION 8: Interactive Features (NEW!)
-----------------------------------------
**Purpose**: Make HTML report interactive and user-friendly

**Features**:

### 8.1. Global Search
  - Search box at top of report
  - Search across: work dirs, path groups, violations
  - Highlight matches in tables
  - Jump to relevant section

### 8.2. Filters
  - Filter by location (IPO dropdown)
  - Filter by status (COMPLETED/RUNNING/STALE)
  - Filter by violation type (Show only violations > 0)
  - Filter by date range (date picker)
  - "Clear all filters" button

### 8.3. Sorting
  - Click column headers to sort
  - Multi-column sort (shift+click)
  - Sort indicators (arrows)
  - Remember sort preferences (localStorage)

### 8.4. Export Functions
  - Export filtered data to CSV
  - Export charts as PNG
  - Export full report as PDF
  - Copy table to clipboard (Excel-friendly)

### 8.5. Collapsible Sections
  - All sections collapsible by default
  - Remember collapsed state (localStorage)
  - "Expand all" / "Collapse all" buttons
  - Smooth animations

### 8.6. Dark Mode
  - Toggle dark/light theme
  - Remember preference (localStorage)
  - Smooth transition animations

**Priority**: LOW-MEDIUM (Enhancement, not critical)
**Effort**: 6-8 hours
**Dependencies**: None (but adds significant value)


================================================================================
PHASE 4: TECHNICAL IMPLEMENTATION DETAILS
================================================================================

## Technology Stack:
-------------------
  • HTML5 + CSS3 (Grid, Flexbox)
  • JavaScript (ES6+)
  • Chart.js for visualizations
  • No external dependencies (embed everything)
  • localStorage for user preferences

## Code Organization:
--------------------
  • _generate_timing_summary_html() - Main function (REFACTOR)
  • _generate_location_explorer_html() - NEW
  • _generate_quality_dashboard_html() - NEW
  • _generate_dsr_skew_trend_html() - ENHANCE
  • _generate_power_analysis_html() - NEW
  • _generate_report_navigator_html() - NEW
  • _generate_interactive_features_js() - NEW

## Styling Approach:
-------------------
  • CSS Variables for theming (dark/light)
  • Responsive design (mobile-first)
  • Print-friendly CSS (@media print)
  • Accessibility (ARIA labels, keyboard navigation)

## Data Structure Updates:
--------------------------
  • timing_data dict needs enhancement:
    - Add 'locations' list with full metadata
    - Add 'quality_metrics' per work dir
    - Add 'power_data' per work dir
    - Add 'source_files' dict with absolute paths

## Tablog Integration:
---------------------
  • Check server status: GET http://localhost:8888/status
  • Open log: GET http://localhost:8888/open_log?file=<path>
  • JavaScript: openLogWithServer(file, event)
  • Fallback: Copy to clipboard with toast notification


================================================================================
PHASE 5: IMPLEMENTATION ROADMAP
================================================================================

## SPRINT 1: Foundation (8-10 hours)
------------------------------------
  ✓ TASK 1.1: Refactor _generate_timing_summary_html()
    - Modularize into sections
    - Update data structure
    - Add common CSS/JS functions
    - Time: 2-3 hours
  
  ✓ TASK 1.2: Implement Overview Dashboard (Section 1)
    - Quick stats cards
    - Status summary
    - Location badges
    - Time: 3-4 hours
  
  ✓ TASK 1.3: Implement Location Explorer (Section 2)
    - Location table
    - Expand/collapse rows
    - Basic filters
    - Time: 3-4 hours
  
  **Testing**: prt (5 IPOs), fth (1 location)
  **Deliverable**: Enhanced HTML with Sections 1-2


## SPRINT 2: Quality Metrics (6-8 hours)
----------------------------------------
  ✓ TASK 2.1: Implement Quality Dashboard (Section 4)
    - Quality summary cards
    - Detailed quality table
    - Source file links
    - Time: 4-5 hours
  
  ✓ TASK 2.2: Add Trend Visualization
    - Chart.js integration
    - Quality violations chart
    - Interactive legend
    - Time: 2-3 hours
  
  **Testing**: pscc (high violations), dqax (clean), lndm (improved)
  **Deliverable**: Quality Metrics Dashboard


## SPRINT 3: Enhancements (6-8 hours)
-------------------------------------
  ✓ TASK 3.1: Enhance Unified Timing Summary (Section 3)
    - Add source attribution
    - Color coding
    - Sort functionality
    - Export to Excel
    - Time: 3-4 hours
  
  ✓ TASK 3.2: Enhance DSR Skew Trend (Section 5)
    - Trend chart
    - Statistical summary
    - Source file links
    - Time: 3-4 hours
  
  **Testing**: prt (DSR trend), lndm (improvement visible)
  **Deliverable**: Enhanced timing and DSR sections


## SPRINT 4: Additional Features (6-8 hours)
--------------------------------------------
  ✓ TASK 4.1: Power Analysis Section (Section 6)
    - Power tables
    - Power trend chart
    - Power breakdown
    - Time: 3-4 hours
  
  ✓ TASK 4.2: Report Navigator (Section 7)
    - Organize all reports
    - Tablog integration
    - Download links
    - Time: 3-4 hours
  
  **Testing**: All units
  **Deliverable**: Complete feature set


## SPRINT 5: Polish & Interactive (OPTIONAL - 6-8 hours)
--------------------------------------------------------
  ✓ TASK 5.1: Interactive Features (Section 8)
    - Global search
    - Advanced filters
    - Dark mode
    - Export functions
    - Time: 6-8 hours
  
  **Testing**: User acceptance testing
  **Deliverable**: Production-ready HTML report


================================================================================
PHASE 6: TESTING STRATEGY
================================================================================

## Unit Testing:
---------------
  • Each section tested independently
  • Test with missing data (graceful degradation)
  • Test with extreme values (1000+ violations)
  • Test with 1 vs 10+ work directories

## Integration Testing:
----------------------
  • Test on 6 different units:
    - prt (IPO-specific, 5 locations, moderate violations)
    - fth (regular, 1 location, clean)
    - pscc (high data violations, clean clock)
    - dqax (ECO/Signoff, perfect quality)
    - lndm (improvement trend visible)
    - ccorea (multiple IPOs, HPORT chiplet)

## Browser Testing:
------------------
  • Firefox 118+ (primary)
  • Chrome/Chromium (secondary)
  • Test responsive design (mobile)
  • Test print view

## Performance Testing:
----------------------
  • Load time < 2 seconds
  • Smooth animations (60fps)
  • No memory leaks
  • Large datasets (50+ work dirs)


================================================================================
PHASE 7: SUCCESS METRICS
================================================================================

## Quantitative Metrics:
-----------------------
  • HTML report generation time: < 5 seconds
  • Report file size: < 2 MB (with charts)
  • Tables load instantly (< 100ms)
  • All links working (100% success rate)
  • Tablog integration working (95%+ success rate)

## Qualitative Metrics:
----------------------
  • User can find any metric in < 10 seconds
  • Report is self-explanatory (no documentation needed)
  • Visual appeal (professional, modern)
  • Print-friendly format works
  • Mobile view is usable

## Comparison to Current:
------------------------
  • 10x more information displayed
  • 3x faster to find specific data
  • Interactive (vs static tables)
  • Comprehensive (vs partial data)


================================================================================
PHASE 8: FUTURE ENHANCEMENTS (BACKLOG)
================================================================================

## V2.0 Features (Post-MVP):
---------------------------
  • Automated comparison between IPOs
  • Email report generation and sending
  • Integration with bug tracking (link violations to NVBugs)
  • Historical trending (database backend)
  • AI-powered recommendations ("Fix these violations first")
  • Slack/Teams notifications for critical violations
  • REST API for programmatic access
  • Jupyter notebook integration

## V3.0 Features (Long-term):
----------------------------
  • Real-time monitoring (WebSocket)
  • Multi-user collaboration (shared annotations)
  • Custom dashboards (user-configurable)
  • Advanced analytics (ML-based predictions)
  • Integration with CI/CD pipelines
  • Automated regression detection


================================================================================
SUMMARY & RECOMMENDATION
================================================================================

## Recommended Approach:
-----------------------
  **PHASE 1 (MVP)**: Sprints 1-2 (14-18 hours)
    → Overview Dashboard
    → Location Explorer
    → Quality Metrics Dashboard
    → Value: 80% of total benefit
  
  **PHASE 2 (Enhanced)**: Sprint 3 (6-8 hours)
    → Enhanced Timing Summary
    → Enhanced DSR Skew Trend
    → Value: +15% benefit
  
  **PHASE 3 (Complete)**: Sprint 4 (6-8 hours)
    → Power Analysis
    → Report Navigator
    → Value: +5% benefit
  
  **PHASE 4 (Polish)**: Sprint 5 (6-8 hours) - OPTIONAL
    → Interactive features
    → Dark mode
    → Export functions
    → Value: User delight, not critical

## Total Time Estimate:
----------------------
  • MVP (Sprints 1-2): 14-18 hours
  • Enhanced (Sprint 3): 20-26 hours
  • Complete (Sprint 4): 26-34 hours
  • Polish (Sprint 5): 32-42 hours

## My Recommendation:
--------------------
  **Start with MVP (Sprints 1-2)** - This delivers the most critical features:
    1. Multi-location support
    2. Quality metrics dashboard
    3. Status tracking
    4. Basic visualization
  
  Then evaluate with Sir avice and decide on next priorities.

================================================================================
END OF PLAN
================================================================================

**Questions for Sir avice:**
  1. Which sprint do you want to start with?
  2. Are there any features you want to prioritize/deprioritize?
  3. Should we include Chart.js for visualizations or keep it simple?
  4. Timeline expectations? (MVP in 2-3 days vs complete in 1-2 weeks?)

Ready to proceed with your direction, Sir avice!

