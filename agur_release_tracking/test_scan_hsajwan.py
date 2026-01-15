import subprocess
import re
import os
import time
from datetime import datetime

def parse_size_to_bytes(size_str):
    size_str = size_str.strip().upper()
    multipliers = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
    try:
        match = re.match(r'^([\d.]+)([KMGTP]?)$', size_str)
        if match:
            num, unit = match.groups()
            return int(float(num) * multipliers.get(unit, 1))
    except:
        pass
    return 0

disk_path = "/home/scratch.hsajwan_vlsi"
age_days = 60

print(f"Simulating scan on: {disk_path}")
print("=" * 80)

# Find directories
cmd = f"""find {disk_path}/ -mindepth 3 -maxdepth 5 -type d -mtime +{age_days} 2>/dev/null | head -200"""
result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)

if result.returncode == 0 and result.stdout:
    excluded_path_segments = [
        '/COMMON/', '/common/', '/old/', '/backup/', '/samples/', 
        '/scripts/', '/sources/', '/reports/', '/logs/', '/temp/',
        '/my_backup/', '/.git/', '/hooks/', '/tmp/'
    ]
    
    excluded_subdirs = {
        'pnr_flow', 'signoff_flow', 'export', 'nbu_signoff', 'syn_flow', 
        'formal_flow', 'pv_flow', 'fe_reports', 'fe_results', 'rbv', 'flp',
        'fsub_scratchDir', 'logs', 'log', 'reports', 'scripts', 'src', 'temp',
        'cmd_log', 'last_run', '.git', 'task_scripts', 'umake_log', 'unit_scripts',
        'nv_gen_runset', 'fe_logs', 'hooks', 'tmp', 'run_logs', 'out', 'sources',
        'my_backup', 'backup', 'common_scripts', 'samples', 'COMMON', 'old',
        'fe_logs', 'data', 'cache'
    }
    
    subdir_patterns = [
        r'_scripts$', r'_backup$', r'_samples$', r'_common$', r'_inputs?$',
        r'_flow$', r'_results?$', r'_logs?$', r'_reports?$', r'^fe_', r'^nv_', r'_fix_',
    ]
    
    dir_paths = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
    print(f"Found {len(dir_paths)} directories before filtering")
    
    # Filter
    filtered_paths = []
    for dir_path in dir_paths:
        # Check path segments
        skip_path = False
        for segment in excluded_path_segments:
            if segment in dir_path:
                skip_path = True
                break
        if skip_path:
            continue
        
        dir_basename = os.path.basename(dir_path)
        
        if dir_basename.lower() in excluded_subdirs:
            continue
        if dir_basename.startswith('.') or dir_basename.startswith('work_'):
            continue
        if re.match(r'ipo\d+', dir_basename):
            continue
        
        is_subdir = False
        for pattern in subdir_patterns:
            if re.search(pattern, dir_basename, re.IGNORECASE):
                is_subdir = True
                break
        if is_subdir:
            continue
        
        if '_rbv_' in dir_basename:
            filtered_paths.append(dir_path)
    
    print(f"After filtering: {len(filtered_paths)} workarea directories")
    print("\nTop 3 by size:")
    
    entries = []
    for dir_path in filtered_paths[:10]:
        du_result = subprocess.run(['du', '-sh', dir_path], stdout=subprocess.PIPE, universal_newlines=True, timeout=10)
        if du_result.returncode == 0:
            size_str = du_result.stdout.split()[0]
            stat_result = subprocess.run(['stat', '-c', '%Y', dir_path], stdout=subprocess.PIPE, universal_newlines=True, timeout=2)
            if stat_result.returncode == 0:
                mtime_epoch = int(stat_result.stdout.strip())
                age_days_calc = int((time.time() - mtime_epoch) / 86400)
                last_modified = datetime.fromtimestamp(mtime_epoch).strftime('%b %d, %Y')
                entries.append({
                    'size': size_str,
                    'size_bytes': parse_size_to_bytes(size_str),
                    'path': dir_path,
                    'age_days': age_days_calc,
                    'last_modified': last_modified
                })
    
    entries.sort(key=lambda x: x['size_bytes'], reverse=True)
    for i, entry in enumerate(entries[:3], 1):
        print(f"{i}. {entry['size']:>6} - {entry['path']}")
        print(f"   Last modified: {entry['last_modified']} ({entry['age_days']} days ago)")
        print()
else:
    print("No directories found")
