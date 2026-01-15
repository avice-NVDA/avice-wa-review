#!/usr/bin/env python3
"""
Generate a sample disk alert email for testing the new cleanup sections
"""

import os
import sys
import base64
from datetime import datetime

# Add parent directory to path to import agur_disk_monitor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the send_consolidated_email function to write HTML to file instead
def generate_sample_email():
    """Generate sample email HTML for review"""
    
    # Load logo
    logo_path = '/home/avice/scripts/avice_wa_review/presentation/avice_logo.png'
    try:
        with open(logo_path, 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        logo_data = ''
    
    # Sample data for email
    units = [
        {
            'unit': 'tecorer',
            'chiplet': 'QNS',
            'usage_pct': 92,
            'size': '9.8T',
            'avail': '692G',
            'workarea': '/home/scratch.hsajwan_vlsi/agur/1NL/tecorer/tecorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_higher_effort'
        },
        {
            'unit': 'tds',
            'chiplet': 'QNS',
            'usage_pct': 92,
            'size': '9.8T',
            'avail': '692G',
            'workarea': '/home/scratch.hsajwan_vlsi/agur/1NL/tds/tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN'
        }
    ]
    
    # Sample disk summary
    disk_summary = {
        '/home/scratch.hsajwan_vlsi': {
            'usage_pct': 92,
            'size': '9.8T',
            'used': '8.3T',
            'avail': '692G',
            'status': 'CRITICAL'
        }
    }
    
    # Sample old workareas
    old_workareas = {
        '/home/scratch.hsajwan_vlsi': [
            {
                'size': '343G',
                'path': '/home/scratch.hsajwan_vlsi/agur/1NL/tecorer/tecorer_rbv_2025_09_02_rbv_2025_08_27_agur_condb_int3_2025_08_27_0_1NL_snap_higher_effort',
                'age_days': 110,
                'last_modified': 'Sep 02, 2025'
            },
            {
                'size': '287G',
                'path': '/home/scratch.hsajwan_vlsi/agur/1NL/tds/tds_rbv_2025_09_03_agur_condb_int3_2025_08_27_0_1NL_snap_FIRST_RUN',
                'age_days': 109,
                'last_modified': 'Sep 03, 2025'
            },
            {
                'size': '156G',
                'path': '/home/scratch.hsajwan_vlsi/agur/1NL/eri/eri_rbv_2025_08_15_agur_condb_int3_2025_08_14_0_1NL_snap',
                'age_days': 128,
                'last_modified': 'Aug 15, 2025'
            }
        ]
    }
    
    # Generate email HTML (copy-paste from agur_disk_monitor.py send_consolidated_email)
    from_email = "avice@nvidia.com"
    to_email = "hsajwan@nvidia.com"
    cc_emails = ['avice@nvidia.com', 'ohamama@nvidia.com']  # avice + QNS manager
    subject = "[TEST] Critical Disk Usage Alert: 92%"
    
    display_name = "Hsajwan"
    max_usage = 92
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Build disk summary HTML
    disk_summary_html = ''
    if disk_summary and len(disk_summary) > 0:
        disk_word = "disk" if len(disk_summary) == 1 else "disks"
        levels_text = ""
        if len(disk_summary) > 1:
            levels = sorted([d['usage_pct'] for d in disk_summary.values()], reverse=True)
            levels_text = f" with varying usage levels ({levels[0]}%, {levels[1]}%"
            if len(levels) > 2:
                levels_text += f", {levels[2]}%"
            levels_text += ")"
        
        disk_rows = ''
        balance_needed = len(disk_summary) > 1 and (max([d['usage_pct'] for d in disk_summary.values()]) - min([d['usage_pct'] for d in disk_summary.values()])) >= 10
        
        for disk_path, disk_info in sorted(disk_summary.items()):
            status_color = '#c0392b' if disk_info['usage_pct'] >= 95 else ('#e74c3c' if disk_info['usage_pct'] >= 90 else '#27ae60')
            status_text = '[CRITICAL]' if disk_info['usage_pct'] >= 90 else '[OK]'
            disk_rows += f"""
                <tr style="{'background: #ffebee;' if disk_info['usage_pct'] >= 90 else ''}">
                    <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; word-break: break-all; font-size: 12px;">{disk_path}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; text-align: center; font-weight: bold; color: {status_color}; font-size: 18px;">{disk_info['usage_pct']}%</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; text-align: center;">{disk_info['size']}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; text-align: center; font-weight: bold; color: {status_color}; font-size: 16px;">{disk_info['avail']}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; text-align: center; font-weight: bold; color: {status_color};">{status_text}</td>
                </tr>"""
        
        balance_notice = ''
        if balance_needed:
            balance_notice = """
            <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <p style="margin: 0; font-weight: bold; color: #e65100;">⚖️ Storage Balancing Recommended</p>
                <p style="margin: 5px 0 0 0; color: #e65100;">Your disks are unbalanced. Consider moving data from high-usage disks to lower-usage disks to optimize storage.</p>
            </div>"""
        
        disk_summary_html = f"""
        <div style="background: #e3f2fd; border-left: 4px solid #1565c0; padding: 15px; margin: 15px;">
            <h3 style="color: #1565c0; margin-top: 0;">📊 Your Disk Utilization Summary</h3>
            <p style="margin: 5px 0; color: #1565c0;">You have {len(disk_summary)} scratch {disk_word}{levels_text}:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <tr style="background: #1565c0; color: white;">
                    <th style="padding: 10px; text-align: left;">Disk Path</th>
                    <th style="padding: 10px; text-align: left;">Usage</th>
                    <th style="padding: 10px; text-align: left;">Total Size</th>
                    <th style="padding: 10px; text-align: left;">Available</th>
                    <th style="padding: 10px; text-align: left;">Status</th>
                </tr>
                {disk_rows}
            </table>
            {balance_notice}
        </div>"""
    
    # Build escalation notice
    escalation_notice = f"""
        <div style="background: #ffebee; border-left: 4px solid #f44336; padding: 12px 15px; margin: 15px;">
            <p style="margin: 0; font-weight: bold; color: #c62828;">🚨 Management Escalation Notice</p>
            <p style="margin: 5px 0 0 0; color: #c62828;">Due to high (>=90%) disk usage, your QNS chiplet manager has been notified (CC'd) to assist with storage management and prioritization.</p>
        </div>"""
    
    # Build old workareas section
    old_workareas_html = ''
    for disk_path, workareas in old_workareas.items():
        workarea_rows = ''
        for i, wa in enumerate(workareas, 1):
            workarea_rows += f"""
                <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; margin: 8px 0;">
                    <div style="font-weight: bold; color: #c62828; font-size: 16px;">{i}. {wa['size']} - {wa['path']}</div>
                    <div style="color: #666; font-size: 13px; margin-top: 3px;">Last modified: {wa['last_modified']} ({wa['age_days']} days ago)</div>
                </div>"""
        
        old_workareas_html += f"""
        <div style="background: #fff3e1; border-left: 4px solid #ff9800; padding: 15px; margin: 15px;">
            <h3 style="color: #e65100; margin-top: 0;">💾 {disk_path} - Top Cleanup Candidates</h3>
            <p style="margin: 5px 0; color: #e65100;">These workareas are <strong>>45 days old</strong> and consuming significant space:</p>
            {workarea_rows}
            <p style="margin: 10px 0 0 0; color: #e65100; font-size: 13px;"><strong>Tip:</strong> Consider archiving or removing these old workareas to free up space.</p>
        </div>"""
    
    # Build units table
    units_rows = ''
    for unit in units:
        units_rows += f"""
                <tr>
                    <td><span style="font-size: 14px !important;">{unit['unit']}</span></td>
                    <td><span style="font-size: 14px !important;">{unit['chiplet']}</span></td>
                    <td><span style="color: #e74c3c !important; font-weight: bold !important; font-size: 26px !important;">{unit['usage_pct']}%</span></td>
                    <td><span style="font-size: 14px !important;">{unit['size']}</span></td>
                    <td><span style="color: #e74c3c !important; font-weight: bold !important; font-size: 18px !important;">{unit['avail']}</span></td>
                    <td><span style="word-break: break-all; font-size: 11px !important;">{unit['workarea']}</span></td>
                </tr>"""
    
    # Generate full HTML
    html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 0 15px 10px 15px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            font-size: 24px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .greeting {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px 15px;
            margin: 15px;
        }}
        .section {{
            padding: 15px;
        }}
        .section h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin-top: 0;
        }}
        .units-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        .units-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-size: 14px;
        }}
        .units-table td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .cleanup-list {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 15px;
        }}
        .cleanup-list ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .cleanup-list li {{
            margin: 8px 0;
            color: #2e7d32;
        }}
        .footer {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 12px;
        }}
        .footer a {{
            color: #a8ff78;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CRITICAL DISK USAGE ALERT</h1>
            <p style="margin: 3px 0 3px 0; font-size: 14px;">Multiple Units Require Immediate Action</p>
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0;">
                <tr>
                    <td width="54" style="padding-right: 10px; vertical-align: middle;">
                        <img src="data:image/png;base64,{logo_data}" alt="Avice Logo" width="54" height="54" style="display: block; border-radius: 6px;">
                    </td>
                    <td style="padding-left: 10px; vertical-align: middle;">
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #c0392b; border: 2px solid #fff; border-radius: 6px; height: 50px;">
                            <tr>
                                <td style="text-align: center; vertical-align: middle; width: 50%;">
                                    <div style="font-size: 28px; font-weight: bold; color: #fff; line-height: 1; margin: 0;">{max_usage}%</div>
                                    <div style="font-size: 9px; color: #fff; margin-top: 2px; letter-spacing: 0.5px;">MAX DISK USAGE</div>
                                </td>
                                <td style="text-align: center; vertical-align: middle; width: 50%; border-left: 1px solid rgba(255,255,255,0.3);">
                                    <div style="font-size: 28px; font-weight: bold; color: #fff; line-height: 1; margin: 0;">{len(units)}</div>
                                    <div style="font-size: 9px; color: #fff; margin-top: 2px; letter-spacing: 0.5px;">UNITS</div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </div>
        
        <div class="greeting">
            <p>Hello <strong>{display_name}</strong>,</p>
            <p style="margin-top: 3px;">You have {len(units)} AGUR units with critical disk usage (>=90%). Multiple workareas require immediate attention!</p>
        </div>
        
        <div style="background: #fff3cd; border-left: 4px solid #ff9800; padding: 12px 15px; margin: 15px;">
            <p style="margin: 0; font-weight: bold; color: #e65100;">⚠ Daily Alert Notice</p>
            <p style="margin: 5px 0 0 0; color: #e65100;">You will continue to receive this email <strong>daily at 8:00 AM</strong> until your disk usage drops <strong>below 90%</strong>. Please take action to free up disk space to stop these alerts.</p>
        </div>
        
        {escalation_notice}
        
        {disk_summary_html}
        
        {old_workareas_html}
        
        <div class="section">
            <h3>Critical Units</h3>
            <table class="units-table">
                <tr>
                    <th>Unit</th>
                    <th>Chiplet</th>
                    <th>Usage</th>
                    <th>Total Size</th>
                    <th>Available</th>
                    <th>Workarea Path</th>
                </tr>
                {units_rows}
            </table>
        </div>
        
        <div class="cleanup-list">
            <h3 style="color: #2e7d32; margin-top: 0;">Recommended Cleanup Actions</h3>
            <p style="color: #2e7d32; margin: 5px 0;">Apply these cleanup strategies to <strong>each workarea listed above</strong> (especially the old ones shown in cleanup candidates):</p>
            <ol style="margin: 10px 0; padding-left: 20px;">
                <li style="margin: 12px 0; color: #2e7d32;">
                    <strong>Remove old PnR work directories:</strong>
                    <pre style="background: #263238; color: #aed581; padding: 8px; border-radius: 4px; margin: 5px 0; font-size: 11px;">cd [workarea_path]/pnr_flow
ls -ltd */work_* | tail -n +3   # Show all except latest 2
rm -rf [old_work_dirs]          # Delete after review</pre>
                </li>
                <li style="margin: 12px 0; color: #2e7d32;">
                    <strong>Delete old PT timing sessions:</strong>
                    <pre style="background: #263238; color: #aed581; padding: 8px; border-radius: 4px; margin: 5px 0; font-size: 11px;">cd [workarea_path]/signoff_flow/auto_pt
ls -ltd work_* | tail -n +4     # Show all except latest 3
rm -rf [old_work_dirs]          # Delete after review</pre>
                </li>
                <li style="margin: 12px 0; color: #2e7d32;">
                    <strong>Clean up old Star SPEF files:</strong>
                    <pre style="background: #263238; color: #aed581; padding: 8px; border-radius: 4px; margin: 5px 0; font-size: 11px;">cd [workarea_path]/signoff_flow/star
du -sh work_*/spef              # Check sizes
rm -rf work_*/spef/*.gz         # Delete old SPEFs</pre>
                </li>
                <li style="margin: 12px 0; color: #2e7d32;">
                    <strong>Archive or remove entire old workareas:</strong>
                    <pre style="background: #263238; color: #aed581; padding: 8px; border-radius: 4px; margin: 5px 0; font-size: 11px;"># Focus on workareas shown in "Top Cleanup Candidates" above
# These are >45 days old and consuming significant space
tar -czf [workarea_name].tar.gz [workarea_path]  # Archive
# OR
rm -rf [workarea_path]          # Delete (after backup!)</pre>
                </li>
            </ol>
            <div style="background: #ffebee; border: 1px solid #ef5350; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <p style="margin: 0; font-weight: bold; color: #c62828;">⚠ Safety Warning:</p>
                <p style="margin: 5px 0 0 0; color: #c62828;">Always verify with <code>ls</code> before running <code>rm -rf</code>! Consider archiving important data to tape first.</p>
            </div>
            <p style="color: #2e7d32; margin: 10px 0 0 0;"><strong>Note:</strong> Replace <code>[workarea_path]</code> with actual paths from the workareas listed in this email.</p>
        </div>
        
        <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 15px;">
            <h3 style="color: #1565c0; margin-top: 0;">Quick Disk Analysis Commands (CSH/TCSH Compatible)</h3>
            <p style="margin: 5px 0; color: #1565c0;">Copy-paste these commands to analyze disk usage. Run from workarea root directory.</p>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find top 10 largest directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">du -sk * |& grep -v '^du:' | sort -rn | head -10</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">Shows size in KB for each directory, sorted largest first</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Count and size of PnR work directories:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find pnr_flow/*/work_* -maxdepth 0 -type d |& wc -l
find pnr_flow/*/work_* -maxdepth 0 -type d -exec du -sk {{}} \; |& sort -rn | head -5</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">First line: total count. Second line: top 5 largest work dirs</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Count and size of PT timing sessions:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find signoff_flow/auto_pt/work_* -maxdepth 0 -type d |& wc -l
find signoff_flow/auto_pt/work_* -maxdepth 0 -type d -exec du -sk {{}} \; |& sort -rn | head -5</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">First line: total count. Second line: top 5 largest PT sessions</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find large log files (>100MB):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find . -name "*.log" -type f -size +102400 -exec ls -lh {{}} \; |& awk '{{print $5, $9}}' | head -10</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">Shows file size and path for logs >100MB (102400 blocks = 100MB)</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Find old work directories (>60 days):</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find pnr_flow/*/work_* signoff_flow/*/work_* -maxdepth 0 -type d -mtime +60 |& grep -v '^find:'</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">Lists all work directories older than 60 days (prime cleanup candidates)</p>
            </div>
            
            <div style="margin: 10px 0;">
                <strong style="color: #0d47a1;">Star SPEF files disk usage:</strong>
                <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto; margin: 5px 0; font-size: 12px;">find signoff_flow/star/work_*/spef -type f -name "*.spef.gz" -exec du -sk {{}} \; |& sort -rn | head -10</pre>
                <p style="font-size: 11px; color: #666; margin: 2px 0;">Shows largest SPEF files in KB (old corners can often be deleted)</p>
            </div>
            
            <div style="background: #fff3e1; border: 1px solid #ff9800; border-radius: 4px; padding: 10px; margin: 10px 0;">
                <p style="margin: 0; font-weight: bold; color: #e65100;">💡 Pro Tips:</p>
                <ul style="margin: 5px 0; padding-left: 20px; color: #e65100;">
                    <li><code>|&</code> redirects both stdout and stderr (csh/tcsh syntax)</li>
                    <li><code>grep -v '^find:'</code> filters error messages</li>
                    <li>All commands use relative paths from workarea root</li>
                    <li><code>sort -rn</code> = reverse numeric sort (largest first)</li>
                </ul>
            </div>
            
            <p style="margin: 10px 0 0 0; color: #1565c0; font-size: 12px;"><strong>Tip:</strong> <code>cd</code> to each workarea listed above, then run these commands to identify cleanup targets.</p>
        </div>
        
        <div class="footer">
            <strong>AGUR Disk Monitor</strong><br>
            Copyright (c) 2025 Alon Vice (avice)<br>
            Contact: <a href="mailto:avice@nvidia.com">avice@nvidia.com</a>
        </div>
    </div>
</body>
</html>"""
    
    # Write to file
    output_file = f'/home/scratch.avice_vlsi/cursor/avice_wa_review/agur_release_tracking/sample_disk_alert_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    with open(output_file, 'w') as f:
        f.write(html_body)
    
    print(f"\n✅ Sample email HTML generated: {output_file}")
    print(f"\nOpen in browser:")
    print(f"firefox {output_file}")
    print(f"\nOr view with:")
    print(f"cat {output_file}")

if __name__ == '__main__':
    generate_sample_email()

