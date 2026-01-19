# Two Critical Fixes - January 18, 2026

## Issue Reports

### Issue 1: Visual Indicator Request
**User Request**: "Is it also possible to mark in green release areas (under 'By unit' tab table) that already received a mail"

**Problem**: No visual distinction between releases that have been emailed and those that haven't.

**Impact**: Chiplet managers couldn't easily see which releases already had cleanup emails sent to owners.

---

### Issue 2: Counter Persistence Bug
**User Report**: "I might found small Persistent issue. i run cport + ndq chiplet and marked 2 releases under cport and 2 under ndq (total is 4). then i closed the server and the html and re-run cport chiplet only and now i see 4 approved while table contain only 2 marked checkboxes"

**Problem**: Approval counter showed ALL approved releases from the state file, even when filtering to a specific chiplet.

**Impact**: Confusing user experience - counter didn't match visible releases, making it unclear how many releases in the current view were approved.

---

## Solutions Implemented

### Fix 1: Green Highlighting for Emailed Releases

#### Visual Changes
- **Background**: Light green (#d4edda) for emailed release rows
- **Border**: 4px green left border (#28a745) for visual emphasis
- **Badge**: "✓ EMAILED" badge appears next to unit name in green

#### Implementation
1. Added CSS classes:
   - `.emailed-release` - Row styling
   - `.emailed-badge` - Badge styling

2. Modified `generate_dashboard_report()`:
   - Loads approval state at dashboard creation time
   - Checks `emailed_releases` dict for each release
   - Applies CSS class and badge to emailed rows

3. HTML row generation (line ~737):
   ```python
   is_emailed = release_id in emailed_releases
   row_class = ' class="emailed-release"' if is_emailed else ''
   emailed_badge = '<span class="emailed-badge">✓ EMAILED</span>' if is_emailed else ''
   ```

#### Files Modified
- `agur_release_cleanup.py` (lines ~1114-1129, ~650-658, ~726-752)

---

### Fix 2: Counter Shows Only Visible Releases

#### Behavior Changes
**Before**:
- Counter showed total approved releases across ALL chiplets in state file
- Example: CPORT (2 approved) + NDQ (2 approved) = Shows "4" even when viewing CPORT only

**After**:
- Counter shows ONLY releases visible in current dashboard
- Example: CPORT only view = Shows "2" (only CPORT approvals count)

#### Implementation
1. Modified `updateApprovalStats()` JavaScript function:
   - Counts checkboxes visible in DOM (`document.querySelectorAll('.approval-checkbox')`)
   - Fetches approval/emailed state from `/api/releases`
   - Filters state to match visible release IDs
   - Updates counters with filtered counts

2. Updated `/api/releases` endpoint:
   - Added `'emailed': is_emailed` field to each release
   - JavaScript can now determine both approved and emailed status

3. Counter calculation logic:
   ```javascript
   const allCheckboxes = Array.from(document.querySelectorAll('.approval-checkbox'));
   const visibleReleaseIds = new Set(allCheckboxes.map(cb => cb.dataset.releaseId));
   
   // Count only visible releases
   stateData.releases.forEach(release => {
       if (visibleReleaseIds.has(release.id)) {
           if (release.approved) visibleApprovedCount++;
           if (release.emailed) visibleEmailedCount++;
       }
   });
   ```

#### Files Modified
- `agur_release_cleanup.py` (lines ~1360-1400, ~2463-2491)

---

## Testing Scenarios

### Test 1: Green Highlighting
```bash
./agur_release_cleanup.py --interactive -c CPORT --test-mode
```

1. Approve 3 releases
2. Send emails
3. Go to "By Unit" tab
4. **Expected**: 3 releases have green background and "✓ EMAILED" badge

### Test 2: Counter Fix (Original Bug)
```bash
# Step 1
./agur_release_cleanup.py --interactive -c CPORT,NDQ --test-mode
# Approve 2 from CPORT, 2 from NDQ (counter shows 4)
# Stop server

# Step 2
./agur_release_cleanup.py --interactive -c CPORT --test-mode
```

**Expected**: Counter shows "Approved: 2" (not 4!)

### Test 3: Mixed State
```bash
./agur_release_cleanup.py --interactive -c CPORT --test-mode
```

1. Approve 3 releases, send emails (3 emailed)
2. Approve 2 MORE releases (5 approved, 3 emailed)
3. **Expected**: 
   - Counter: "Approved: 5, Emailed: 3"
   - Visual: First 3 rows green, last 2 normal

---

## Technical Details

### State File Structure
No changes to `approval_state_*.json` format. Both fixes use existing data:
- `approvals` dict - for approval status
- `emailed_releases` dict - for emailed status

### Performance Impact
- **Minimal**: Dashboard generation adds one `load_approval_state()` call
- **JavaScript**: Two API calls on page load (`/api/status` and `/api/releases`)
- **No server-side impact**: All filtering happens client-side in JavaScript

### Backwards Compatibility
- ✅ Works with old state files (missing `emailed_releases` key defaults to empty dict)
- ✅ No breaking changes to existing workflows
- ✅ All previous functionality preserved

---

## Visual Comparison

### "By Unit" Tab - Before vs After

**BEFORE** (No visual distinction):
```
Approve | Unit | Owner              | Release Dir         | Age | Symlinks | Size
--------|------|-------------------|---------------------|-----|----------|------
  [✓]   | fdb  | dkolesnikov@...   | 20250902_092825     | 137d| None     | 125GB
  [✓]   | fth  | miancu@...        | 20250313_110000     | 310d| link1... | 89GB
  [ ]   | lnd  | tsadiel@...       | 20250615_140000     | 217d| None     | 45GB
```

**AFTER** (Green highlighting for emailed):
```
Approve | Unit              | Owner              | Release Dir         | Age | Symlinks | Size
--------|-------------------|-------------------|---------------------|-----|----------|------
┃ [✓]  ┃ fdb ✓ EMAILED     | dkolesnikov@...   | 20250902_092825     | 137d| None     | 125GB  ┃
┃ [✓]  ┃ fth ✓ EMAILED     | miancu@...        | 20250313_110000     | 310d| link1... | 89GB   ┃
  [ ]   | lnd               | tsadiel@...       | 20250615_140000     | 217d| None     | 45GB
        └─ Green background, border, and badge for emailed releases
```

### Counter - Before vs After

**Scenario**: Previously approved 2 CPORT + 2 NDQ, now viewing CPORT only

**BEFORE** (Bug):
```
Total: 39 | Approved: 4 | Emailed: 0 | Pending: 35
                     ↑ Wrong! Shows all chiplets
```

**AFTER** (Fixed):
```
Total: 39 | Approved: 2 | Emailed: 0 | Pending: 37
                     ↑ Correct! Shows only CPORT
```

---

## Files Changed

### agur_release_cleanup.py
**Sections Modified**:
1. CSS (lines ~1114-1129): Added `.emailed-release` and `.emailed-badge` classes
2. `generate_dashboard_report()` (lines ~650-658): Load approval state
3. HTML generation (lines ~726-752): Apply green styling to emailed rows
4. JavaScript (lines ~1360-1400): Count only visible releases
5. API endpoint (lines ~2463-2491): Include `emailed` field

**Total Changes**: ~100 lines modified/added

---

## Verification Commands

```bash
# Check if release is marked as emailed in state
python3 -c "
import json
from pathlib import Path
state = max(Path('cleanup_reports').glob('approval_state_*.json'))
with open(state) as f:
    data = json.load(f)
    print(f'Emailed releases: {len(data.get(\"emailed_releases\", {}))}')
    print('Release IDs:', list(data.get('emailed_releases', {}).keys())[:3])
"

# While server is running, check visible release count
curl http://localhost:5000/api/releases | python3 -m json.tool | grep '"id"' | wc -l

# Check approval stats
curl http://localhost:5000/api/status | python3 -m json.tool
```

---

## Summary

✅ **Fix 1**: Green highlighting makes emailed releases instantly recognizable
✅ **Fix 2**: Counters now accurately reflect only visible releases in current view

Both fixes enhance user experience:
- **Visual clarity**: Managers can see at a glance which releases have been emailed
- **Accurate metrics**: Counters match what's on screen, avoiding confusion
- **No breaking changes**: All existing functionality preserved

**Status**: Ready for production use. Both fixes tested and working correctly.

---

## Related Documentation
- `EMAIL_MEMORY_TEST.md` - Email tracking feature tests
- `EMAIL_MEMORY_IMPLEMENTATION.md` - Email memory technical details
- `README_RELEASE_CLEANUP.md` - Full user guide

