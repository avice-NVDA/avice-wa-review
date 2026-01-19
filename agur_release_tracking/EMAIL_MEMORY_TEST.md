# Email Memory Feature - Test Guide

## Overview
The system now remembers which releases have already been emailed and prevents sending duplicate emails.

## Key Features

### 1. Email Tracking
- Each release that receives an email is tracked in the state file
- Tracks: timestamp, owner, unit, and test_mode status
- Persists across server restarts

### 2. Duplicate Prevention
- Automatically filters out releases that were already emailed
- Shows clear feedback: "X newly emailed (Y already emailed)"
- Prevents accidental duplicate emails to users

### 3. Dashboard Display
- New "Emailed" counter in the control panel
- Shows: `Total | Approved | Emailed | Pending`
- Updates in real-time after sending emails

## Test Scenarios

### Test 1: First Email Send
**Steps:**
1. Start server: `./agur_release_cleanup.py --interactive -c CPORT --test-mode`
2. Dashboard opens automatically
3. Approve 3 releases (check their checkboxes)
4. Click "Send Emails for Approved Releases"

**Expected Results:**
- ✅ Success message: "Emails sent for 3 releases"
- ✅ Dashboard shows: Approved: 3, Emailed: 3
- ✅ You receive 3 emails at avice@nvidia.com
- ✅ Server logs show 3 emails sent

**Verify:**
```bash
curl http://localhost:5000/api/status
# Should show: "approved_count": 3, "emailed_count": 3
```

---

### Test 2: Duplicate Prevention
**Steps:**
1. Keep the same server running (from Test 1)
2. Click "Send Emails for Approved Releases" button AGAIN

**Expected Results:**
- ✅ Error message: "All 3 approved releases have already been emailed. No new emails to send."
- ✅ Dashboard counters don't change: Approved: 3, Emailed: 3
- ✅ NO new emails are sent
- ✅ Server logs show: "Already emailed: 3, New releases to email: 0"

**Verify:**
```bash
curl http://localhost:5000/api/status
# Should still show: "approved_count": 3, "emailed_count": 3 (no change)
```

---

### Test 3: Incremental Email Send
**Steps:**
1. Keep the same server running
2. Approve 2 MORE releases (total 5 approved)
3. Click "Send Emails for Approved Releases"

**Expected Results:**
- ✅ Success message: "Emails sent for 2 releases (3 were already emailed)"
- ✅ Dashboard shows: Approved: 5, Emailed: 5
- ✅ You receive only 2 NEW emails (not duplicates of the first 3)
- ✅ Server logs show: "Already emailed: 3, New releases to email: 2"

**Verify:**
```bash
curl http://localhost:5000/api/status
# Should show: "approved_count": 5, "emailed_count": 5
```

---

### Test 4: Persistence Across Restarts
**Steps:**
1. Stop the server (Ctrl+C)
2. Start it again: `./agur_release_cleanup.py --interactive -c CPORT --test-mode`
3. Refresh the browser (dashboard should reload)
4. Observe the dashboard counters

**Expected Results:**
- ✅ Dashboard shows: Approved: 5, Emailed: 5 (state restored)
- ✅ All 5 previously approved releases are still checked
- ✅ Clicking "Send Emails" shows: "All 5 approved releases have already been emailed"

**Verify:**
```bash
curl http://localhost:5000/api/status
# Should show same state: "approved_count": 5, "emailed_count": 5
```

---

### Test 5: State File Inspection
**Steps:**
```bash
# Find the latest state file
ls -lt cleanup_reports/approval_state_*.json | head -1

# View the state file
cat cleanup_reports/approval_state_*.json | python3 -m json.tool
```

**Expected Results:**
```json
{
  "session_id": "20260118_HHMMSS",
  "created_at": "2026-01-18T...",
  "last_updated": "2026-01-18T...",
  "approvals": {
    "fdb_20250902_092825_dkolesnikov": {
      "approved": true,
      "approved_by": "browser_session",
      "approved_at": "2026-01-18T15:XX:XX"
    },
    ...5 total entries...
  },
  "emailed_releases": {
    "fdb_20250902_092825_dkolesnikov": {
      "emailed_at": "2026-01-18T15:XX:XX",
      "owner": "dkolesnikov@nvidia.com",
      "unit": "fdb",
      "test_mode": true
    },
    ...5 total entries...
  },
  "email_sent": true,
  "email_sent_at": "2026-01-18T15:XX:XX"
}
```

---

### Test 6: Mixed Workflow (Approve → Email → Unapprove → Approve New)
**Steps:**
1. Start fresh: Stop server, delete old state files, restart
2. Approve 2 releases
3. Send emails (2 emailed)
4. Uncheck those 2 releases (unapprove them)
5. Approve 2 DIFFERENT releases
6. Send emails again

**Expected Results:**
- ✅ Step 3: "Emails sent for 2 releases", Emailed: 2
- ✅ Step 4: Dashboard shows Approved: 0, Emailed: 2 (memory persists)
- ✅ Step 5: Dashboard shows Approved: 2, Emailed: 2
- ✅ Step 6: "Emails sent for 2 releases", Emailed: 4 (total)
- ✅ Original 2 releases won't be re-emailed even if you re-approve them

---

### Test 7: Multiple Chiplets
**Steps:**
1. Run: `./agur_release_cleanup.py --interactive -c CPORT,NDQ --test-mode`
2. Approve 2 from CPORT, 2 from NDQ (4 total)
3. Send emails
4. Verify emailed count: 4

**Expected Results:**
- ✅ Email memory works across chiplets
- ✅ State file contains releases from both chiplets
- ✅ Dashboard shows correct counts for multi-chiplet runs

---

## API Reference

### GET /api/status
Returns current approval and email status:
```json
{
  "success": true,
  "total_releases": 39,
  "approved_count": 5,
  "emailed_count": 5,
  "pending_count": 34,
  "email_sent": true,
  "email_sent_at": "2026-01-18T15:30:00"
}
```

### POST /api/send_emails
Sends emails for approved releases that haven't been emailed yet:
```json
{
  "success": true,
  "message": "Emails sent for 2 approved releases",
  "approved_count": 5,
  "newly_emailed": 2,
  "already_emailed": 3,
  "test_mode": true
}
```

Error response when all are emailed:
```json
{
  "success": false,
  "error": "All 5 approved releases have already been emailed. No new emails to send.",
  "already_emailed_count": 5,
  "approved_count": 5
}
```

---

## Troubleshooting

### Issue: Emailed count is 0 after sending
**Solution:** Refresh the page. The count updates automatically but may need a reload.

### Issue: "All releases already emailed" but I want to resend
**Solution:** This is by design to prevent duplicates. If you need to resend:
1. Stop the server
2. Delete or backup the state file: `mv cleanup_reports/approval_state_*.json cleanup_reports/backup/`
3. Restart the server - fresh state will be created

### Issue: State file not found
**Solution:** The state file is created after the first approval. Check:
```bash
ls -lt cleanup_reports/approval_state_*.json
```

---

## Production Workflow

### Daily Cleanup Review
1. Each chiplet manager runs: `./agur_release_cleanup.py --interactive -c THEIR_CHIPLET`
2. Reviews the dashboard
3. Approves releases for cleanup
4. Clicks "Send Emails"
5. Users receive cleanup instructions

### Weekly Re-scan
1. Stop server
2. Archive old state: `mv cleanup_reports/approval_state_*.json cleanup_reports/archive/`
3. Re-run scan with updated age threshold
4. Review new old releases
5. Approve and send

### Avoiding Duplicates
- The system automatically prevents duplicate emails
- Safe to click "Send Emails" multiple times
- Only NEW approvals will receive emails
- Emailed releases stay tracked even if you unapprove them

