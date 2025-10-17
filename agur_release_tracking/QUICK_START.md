# Quick Start Guide - run_agur_regression.sh

## TL;DR - Just Want to Run It Fast?

```bash
# Fastest way to run all regressions on all units
./run_agur_regression.sh -j auto

# Fast formal verification on CPORT only
./run_agur_regression.sh -t formal -c CPORT -j 8
```

---

## 5-Minute Quick Start

### 1. Basic Usage (Sequential)
```bash
# Run all regression types (takes longest)
./run_agur_regression.sh

# Run specific type
./run_agur_regression.sh -t formal

# Run on specific chiplet
./run_agur_regression.sh -c CPORT
```

### 2. Fast Parallel Execution (Recommended)
```bash
# Let the script auto-detect CPU cores
./run_agur_regression.sh -j auto

# Or specify number of parallel jobs
./run_agur_regression.sh -j 8

# Combine with filters
./run_agur_regression.sh -t formal -c CPORT -j 8
```

### 3. Preview Before Running
```bash
# See what will be executed
./run_agur_regression.sh --dry-run -c CPORT
```

### 4. Resume Interrupted Run
```bash
# If a run was interrupted, resume it
./run_agur_regression.sh --resume .agur_regression_state_20251015_143022.txt
```

### 5. View Results
```bash
# Open the generated HTML dashboard
firefox agur_*_regression_dashboard_*.html

# Recommended: Use Firefox 118 or any modern browser
/home/utils/firefox-118.0.1/firefox agur_*_regression_dashboard_*.html
```

**Browser Compatibility Note:**
- ✅ **Recommended**: Firefox 118+ or Chrome/Chromium (any version)
- ✅ Works with any modern browser
- ⚠️ Some custom Firefox builds may have compatibility issues

---

## Common Use Cases

### Use Case 1: Daily CPORT Formal Check
```bash
./run_agur_regression.sh -t formal -c CPORT -j 8
```
**Time**: ~5 minutes (vs ~25 minutes sequential)

### Use Case 2: Full Regression on All Units
```bash
./run_agur_regression.sh -j auto
```
**Time**: ~45 minutes with 8 cores (vs ~350 minutes sequential)

### Use Case 3: Quick Single Unit Check
```bash
./run_agur_regression.sh -t timing -u prt
```
**Time**: ~5 minutes

### Use Case 4: Multi-Type Regression Dashboard
```bash
./run_agur_regression.sh -t formal,timing,pv -j 8
```
**Result**: Single HTML with tabs for each type

### Use Case 5: Debug a Specific Unit
```bash
./run_agur_regression.sh -t formal -u fdb -v
```
**Output**: Detailed verbose logging

---

## Command Cheat Sheet

| Want to... | Command |
|------------|---------|
| Run fast | `-j auto` or `-j 8` |
| Run specific type | `-t formal` |
| Multiple types | `-t formal,timing,pv` |
| Filter by chiplet | `-c CPORT` |
| Single unit only | `-u prt` |
| Preview first | `--dry-run` |
| Debug output | `-v` |
| Resume run | `--resume FILE` |
| Custom config | `--config FILE` |
| Show help | `-h` |

---

## Options Quick Reference

```
Usage: ./run_agur_regression.sh [-t TYPE[,TYPE2,...]] [options]

Regression Types:
  formal  - Formal verification (RTL vs PNR/Synthesis)
  timing  - PT signoff timing analysis
  pv      - Physical verification (DRC, LVS, Antenna)
  clock   - Clock tree analysis
  release - Block release status

Performance:
  -j N, --jobs N        Run N analyses in parallel
  -j auto               Auto-detect CPU cores
  
Filters:
  -c CHIP, --chiplet    Filter by chiplet (CPORT, CFAN, etc.)
  -u UNIT, --unit       Run for specific unit only
  
Execution:
  --dry-run             Preview without executing
  -v, --verbose         Enable debug logging
  --resume FILE         Resume interrupted run
  --config FILE         Use configuration file
  
Help:
  -h, --help            Show full help message
```

---

## Output Files

### HTML Dashboard
- **Single type**: `agur_formal_regression_dashboard_20251015_143022.html`
- **Multi type**: `agur_multi_regression_dashboard_20251015_143022.html`

### State File (for resume)
- **Format**: `.agur_regression_state_20251015_143022.txt`
- **Location**: Current directory

---

## Dashboard Features

Once the HTML is generated, you can:

1. **🔍 Search** - Type in the search box to filter units by name
2. **🎯 Filter** - Click buttons to filter by status (All/Passed/Failed/Warnings)
3. **📄 Export CSV** - Download results as CSV file
4. **🖨️ Print** - Get printer-friendly view
5. **📋 Copy Paths** - Click copy buttons to copy workareas to clipboard

---

## Performance Tips

### For Maximum Speed
```bash
# Use auto-detect for optimal parallelism
./run_agur_regression.sh -j auto

# Or manually tune based on available cores
nproc  # Check available cores
./run_agur_regression.sh -j $(nproc)
```

### For Reliability
```bash
# Use verbose mode to track progress
./run_agur_regression.sh -v -j 8

# Use dry-run first to verify
./run_agur_regression.sh --dry-run -c CPORT
./run_agur_regression.sh -c CPORT -j 8
```

### For Large Regressions
```bash
# Start with resume capability in mind
./run_agur_regression.sh -j auto 2>&1 | tee regression.log

# If interrupted, resume
./run_agur_regression.sh --resume .agur_regression_state_*.txt
```

---

## Troubleshooting

### Problem: Script is slow
**Solution**: Use parallel execution
```bash
./run_agur_regression.sh -j auto
```

### Problem: Don't know what will run
**Solution**: Use dry-run mode
```bash
./run_agur_regression.sh --dry-run
```

### Problem: Script was interrupted
**Solution**: Resume from state file
```bash
ls .agur_regression_state_*.txt
./run_agur_regression.sh --resume .agur_regression_state_20251015_143022.txt
```

### Problem: Need to debug failures
**Solution**: Use verbose mode
```bash
./run_agur_regression.sh -v
```

### Problem: Dashboard too many units
**Solution**: Use filters in the HTML
- Use search box to find specific units
- Click status filter buttons to show only passed/failed
- Export filtered results to CSV

---

## Examples by Experience Level

### Beginner
```bash
# Simple: Run on one unit
./run_agur_regression.sh -u prt
```

### Intermediate
```bash
# Better: Run on chiplet with parallelism
./run_agur_regression.sh -c CPORT -j 4
```

### Advanced
```bash
# Best: Custom config with optimal settings
cat > fast.conf << EOF
PARALLEL_JOBS=8
MAX_RETRIES=3
EOF

./run_agur_regression.sh --config fast.conf -t formal,pv -c CPORT
```

### Expert
```bash
# Preview, then run with full features
./run_agur_regression.sh --dry-run -v -j auto -t formal,timing,pv

# Actually run
./run_agur_regression.sh -v -j auto -t formal,timing,pv 2>&1 | tee full_regression.log
```

---

## Time Estimates

Based on average unit analysis time:

| Setup | Units | Parallel Jobs | Estimated Time |
|-------|-------|---------------|----------------|
| Single unit | 1 | 1 | ~5 min |
| CPORT | 5 | 1 | ~25 min |
| CPORT | 5 | 4 | ~7 min |
| CPORT | 5 | 8 | ~4 min |
| All units | 70 | 1 | ~350 min |
| All units | 70 | 8 | ~45 min |
| All units | 70 | 16 | ~25 min |

*Actual times vary based on analysis type and system load*

---

## Need More Help?

- **Full Documentation**: See `IMPROVEMENTS.md`
- **Changelog**: See `CHANGELOG.md`
- **Configuration**: See `agur_regression.conf.example`
- **Help Command**: `./run_agur_regression.sh -h`
- **Contact**: avice@nvidia.com

---

## Quick Tips

💡 **Tip 1**: Always use `-j auto` for best performance  
💡 **Tip 2**: Use `--dry-run` before long regressions  
💡 **Tip 3**: Enable `-v` when debugging issues  
💡 **Tip 4**: Resume capability saves time on interruptions  
💡 **Tip 5**: HTML dashboard has powerful search/filter features  

---

**Ready to go?** Try this now:
```bash
./run_agur_regression.sh -t formal -c CPORT -j auto
```

Happy testing! 🚀

