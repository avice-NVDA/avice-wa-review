# Presentation Materials - README

## Overview

Complete presentation package for introducing the **Avice Workarea Review Tool** to the Agur physical design team.

**Target Duration**: 25 minutes (core presentation) + 5 minutes Q&A  
**Date**: October 16, 2025  
**Audience**: Agur project physical designers

---

## What's Included

### 📊 Main Presentation Documents

1. **AGUR_PRESENTATION_avice_wa_review.md** (Primary Resource)
   - Complete 13-slide presentation script
   - Detailed talking points for each slide
   - Demo script with step-by-step instructions
   - Timing breakdown (24 minutes core + 6 min buffer)
   - Backup slides for extra time

2. **AGUR_PRESENTATION_SLIDES.html** (Visual Presentation)
   - Professional HTML slide deck
   - Modern, clean design with blue/green theme
   - Keyboard navigation (arrow keys, space bar)
   - 13 slides covering all key topics
   - Can be projected or shared on screen

### 📋 Quick Reference Materials

3. **PRESENTATION_QUICK_REF.txt** (Keep This Handy!)
   - One-page cheat sheet
   - Copy-paste ready demo commands
   - Key talking points summarized
   - Expected Q&A brief answers
   - Emergency backup plans

4. **PRESENTATION_CHECKLIST.txt** (Day-of-Presentation Guide)
   - Pre-presentation setup checklist (30 min before)
   - During-presentation flow guide
   - Timing reminders
   - Backup plans for common issues
   - Post-presentation tasks

### 💬 Q&A Support

5. **PRESENTATION_QA_BACKUP.md** (Detailed Answers)
   - Comprehensive Q&A database
   - Technical deep-dives
   - Troubleshooting scenarios
   - Future roadmap discussion
   - Comparison with other tools

---

## How to Use These Materials

### Before the Meeting (30 minutes setup)

1. **Read the checklist first**
   ```bash
   less PRESENTATION_CHECKLIST.txt
   ```

2. **Test your demo workarea**
   ```bash
   cd /home/avice/scripts/avice_wa_review
   export DEMO_WA="/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap"
   /home/avice/scripts/avice_wa_review_launcher.csh $DEMO_WA -s setup
   ```

3. **Open the HTML slides**
   ```bash
   /home/utils/firefox-118.0.1/firefox /home/avice/scripts/avice_wa_review/presentation/AGUR_PRESENTATION_SLIDES.html
   ```

4. **Print or have open**:
   - PRESENTATION_QUICK_REF.txt (for quick lookups)
   - PRESENTATION_QA_BACKUP.md (for detailed Q&A)

### During the Meeting

1. **Display the HTML slides** (AGUR_PRESENTATION_SLIDES.html)
   - Use arrow keys to navigate
   - Space bar also moves forward
   - Home/End keys jump to first/last slide

2. **Follow the script** (AGUR_PRESENTATION_avice_wa_review.md)
   - Each slide has detailed talking points
   - Demo commands are provided
   - Timing guidance included

3. **Reference the quick ref card** (PRESENTATION_QUICK_REF.txt)
   - Copy-paste demo commands
   - Quick reminders of key points

4. **Use Q&A backup** (PRESENTATION_QA_BACKUP.md)
   - Detailed answers to expected questions
   - Technical explanations
   - Troubleshooting tips

### After the Meeting

Follow post-presentation tasks in PRESENTATION_CHECKLIST.txt:
- Send follow-up email
- Collect feedback
- Clean up demo files
- Update documentation as needed

---

## Presentation Structure

### Part 1: Introduction (5 minutes)
- **Slide 1**: Title and context
- **Slide 2**: Problem statement (why this tool exists)
- **Slide 3**: Tool overview (13 sections)

### Part 2: How to Use (8 minutes)
- **Slide 4**: Basic commands and usage
- **Slide 5-6**: Live demo (terminal + HTML)

### Part 3: Critical Discussion (7 minutes)
- **Slide 7**: Advantages (time savings, comprehensive)
- **Slide 8**: Disadvantages ⚠️ (directory structure knowledge loss)
- **Slide 9**: Known bugs (formal status misreporting)

### Part 4: Best Practices (5 minutes)
- **Slide 10**: Recommended workflow
- **Slide 11**: When NOT to use the tool
- **Slide 12**: Real-world examples

### Part 5: Closing (5+ minutes)
- **Slide 13**: Summary and Q&A
- Open discussion

---

## Key Messages (Emphasize Throughout)

### ✅ Advantages
1. **One command replaces 30+ manual checks**
2. **Comprehensive coverage** - all flow stages
3. **Professional HTML reports** - shareable
4. **Easy to use** - no installation needed

### ⚠️ Disadvantages (IMPORTANT!)
1. **Users can lose connection to directory structure**
   - Forget where files are located
   - Can't troubleshoot without the tool
   - **Solution**: Learn structure FIRST, tool SECOND

2. **File location amnesia**
   - Don't know where to find specific logs
   - **Solution**: Keep practicing manual navigation

### 🐛 Known Bugs (Be Transparent!)
1. **Formal status misreporting**
   - Shows "SUCCEEDED" when actual status is "INCONCLUSIVE"
   - **Workaround**: Always verify formal manually
   - **Status**: Fix in progress

---

## Demo Plan

### Demo 1: Terminal Output (3 minutes)
```bash
/home/avice/scripts/avice_wa_review_launcher.csh $DEMO_WA -s runtime pt formal
```
**Show**: Color-coded output, key metrics extraction, section headers

### Demo 2: HTML Report (2 minutes)
```bash
/home/utils/firefox-118.0.1/firefox avice_runtime_report_*.html
```
**Show**: Clickable links, tablog integration, detailed tables

### Demo 3: Bug Example (Optional, 1 minute)
Show the formal status bug in action if time permits

---

## Backup Plans

### If Demo Fails
1. Use backup workarea (pmux instead of prt)
2. Show pre-generated HTML from `html/` folder
3. Continue with slides (content is strong without demo)

### If Running Out of Time
- Skip slides 11-12 (examples)
- Go straight to summary (slide 13)
- Quick Q&A

### If Extra Time
- Show master dashboard
- Discuss AGUR release tracking integration
- More detailed HTML features
- Future roadmap

---

## Expected Questions (Top 10)

1. **How do I get access?**
   → No installation needed, just run the launcher

2. **How long does it take?**
   → 30-60 seconds full analysis, 5-10 seconds selective

3. **Can I run only specific sections?**
   → Yes, use `-s` flag with section names

4. **Will you fix the formal bug?**
   → Yes, fix in progress (1-2 weeks)

5. **Should new designers use this?**
   → Learn directory structure FIRST, then use tool

6. **Can I use for block releases?**
   → Yes, but always verify formal manually

7. **Where are HTML reports saved?**
   → Current working directory (portable)

8. **Can I share HTML reports?**
   → Yes, fully portable with absolute paths

9. **Does it modify my workarea?**
   → No, completely read-only

10. **How do I report bugs?**
    → Contact avice@nvidia.com

See PRESENTATION_QA_BACKUP.md for detailed answers.

---

## Technical Requirements

### Environment
- Terminal with reasonable font size (for visibility)
- Firefox 118+ for HTML slides and reports
- Access to demo workarea

### Demo Workarea
- **Primary**: `/home/scratch.ykatzav_vlsi/agur/prt/prt_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap`
- **Backup**: `/home/scratch.brachas_vlsi/agur/1NL/pmux/pmux_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_sep10`

### Files to Have Open
1. Terminal (left side of screen)
2. Firefox with slides (right side of screen)
3. PRESENTATION_QUICK_REF.txt (another window/screen)

---

## Presentation Tips

### Before You Start
- Test all demo commands
- Verify workarea access
- Position windows for visibility
- Deep breath - you've got this!

### During Presentation
- **Speak clearly** - not too fast
- **Make eye contact** - engage the audience
- **Pause after key points** - let them sink in
- **Ask questions** - "Any questions so far?"
- **Show enthusiasm** - you built something useful!
- **Be honest** - about bugs and limitations (builds trust)

### Handling Questions
- **Listen fully** before answering
- **Acknowledge good questions** - "Great question!"
- **Be honest** if you don't know - "Let me investigate and get back to you"
- **Reference documentation** - "That's covered in detail in the Q&A doc"

### Time Management
- **5 min mark**: Should be at Slide 3
- **10 min mark**: Should be starting demo
- **15 min mark**: Should be at advantages
- **20 min mark**: Should be at best practices
- **24 min mark**: Should be at summary

---

## Key Takeaways for Audience

What you want them to remember:

1. ✅ **Tool exists and is easy to use**
   - No installation, just run the launcher
   - Works from any directory

2. ⚠️ **Use it wisely**
   - Quick checks: YES
   - Deep debugging: Manual navigation
   - Formal verification: ALWAYS verify manually

3. 🎯 **Balance is key**
   - Tool for efficiency
   - Manual skills for expertise
   - Learn structure first, tool second

4. 📧 **Feedback welcome**
   - Contact avice@nvidia.com
   - Bug reports appreciated
   - Feature requests considered

---

## Post-Presentation Follow-Up

### Email Template
```
Subject: Avice Workarea Review Tool - Quick Start

Hi Agur Team,

Thanks for attending today's presentation! Here's how to get started:

BASIC USAGE:
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/your/workarea

SELECTIVE SECTIONS (faster):
/home/avice/scripts/avice_wa_review_launcher.csh /path/to/workarea -s runtime pt

HELP:
/home/avice/scripts/avice_wa_review_launcher.csh --help

IMPORTANT REMINDERS:
- Always verify formal status manually (known bug)
- Use tool for quick checks, not deep debugging
- Keep practicing manual navigation to maintain your skills

DOCUMENTATION:
/home/avice/scripts/avice_wa_review/README_avice_wa_review.md

Questions or feedback? Contact me: avice@nvidia.com

Best,
Alon
```

---

## File Locations

All presentation materials are located in:
```
/home/avice/scripts/avice_wa_review/presentation/
```

Files:
- AGUR_PRESENTATION_avice_wa_review.md
- AGUR_PRESENTATION_SLIDES.html
- PRESENTATION_QUICK_REF.txt
- PRESENTATION_CHECKLIST.txt
- PRESENTATION_QA_BACKUP.md
- PRESENTATION_README.md (this file)

---

## Final Checklist

Before the meeting:
- [ ] Read this README
- [ ] Review AGUR_PRESENTATION_avice_wa_review.md
- [ ] Test demo commands
- [ ] Open AGUR_PRESENTATION_SLIDES.html in Firefox
- [ ] Print or open PRESENTATION_QUICK_REF.txt
- [ ] Review PRESENTATION_QA_BACKUP.md
- [ ] Set up terminal and browser windows
- [ ] Take a deep breath!

---

## Good Luck!

You've prepared thoroughly. The content is strong. The tool is genuinely useful. The team will appreciate your honesty about limitations.

Remember: **The goal is to help the team work efficiently while maintaining their core skills.**

Trust your preparation and enjoy presenting!

---

**Questions about the presentation materials?**  
Contact: avice@nvidia.com

**Presentation Date**: October 16, 2025  
**Created**: October 16, 2025  
**Version**: 1.0

