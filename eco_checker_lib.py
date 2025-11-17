#!/usr/bin/env python3
"""
ECO Checker Library - Shared ECO Validation Functions

This library provides reusable ECO validation functions used by both:
  - eco_checker.py (standalone CLI tool)
  - avice_wa_review.py (integrated workarea review)

Author: Alon Vice (avice@nvidia.com)
Date: November 6, 2025
"""

import os
import re
import gzip
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict


class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    
    @classmethod
    def disable(cls):
        """Disable all colors (for --no-color option)"""
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ''
        cls.MAGENTA = cls.CYAN = cls.GRAY = cls.RESET = ''


class ECOCheckerLib:
    """Shared library for ECO file validation"""
    
    def __init__(self, workarea: Optional[str] = None, 
                 clock_tree_rpt: Optional[str] = None,
                 beflow_config: Optional[str] = None,
                 dont_use_patterns: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize ECO checker library
        
        Args:
            workarea: Workarea path for auto-discovery (optional)
            clock_tree_rpt: Explicit path to ClockTree.rpt (optional)
            beflow_config: Explicit path to beflow_config.yaml (optional)
            dont_use_patterns: Explicit path to dont_use patterns file (optional)
            verbose: Enable verbose output
        """
        self.workarea = workarea
        self.clock_tree_rpt = clock_tree_rpt
        self.beflow_config = beflow_config
        self.dont_use_patterns = dont_use_patterns
        self.verbose = verbose
        
        # Cached data
        self._clock_tree_instances = None
        self._allowed_clock_patterns = None
        self._dont_use_patterns_compiled = None
    
    def extract_unit_from_filename(self, eco_file: str) -> Optional[str]:
        """
        Extract unit name from ECO filename
        
        Strategy:
          1. Get list of known units from AGUR table
          2. Try to match known units in filename (longest match first)
          3. Fall back to generic pattern extraction
        
        Common patterns:
          pmux.ipo1000-1001.2025Nov04_03_43_11_Flow_Fixall.fixall.innovus.tcl -> pmux
          pmux_manual.innovus.tcl -> pmux
          ccorea.ipo1004-1005.*.tcl -> ccorea
        
        Args:
            eco_file: Path to ECO file
        
        Returns:
            Unit name or None if cannot extract
        """
        filename = os.path.basename(eco_file).lower()
        
        # Strategy 1: Try to match known units from AGUR table
        known_units = self._get_known_units()
        if known_units:
            # Sort by length descending to match longest first (e.g., 'top_yc_clock' before 'top')
            for unit in sorted(known_units, key=len, reverse=True):
                if unit in filename:
                    return unit
        
        # Strategy 2: Generic pattern extraction
        # Pattern: unit_name.ipo*.tcl or unit_name_*.tcl
        match = re.match(r'^([a-zA-Z0-9_]+)[\._]', filename)
        if match:
            candidate = match.group(1)
            # If candidate is in known units, use it
            if known_units and candidate in known_units:
                return candidate
            # Otherwise return it anyway (might be a new unit)
            return candidate
        
        # Try without extension
        basename = filename.replace('.tcl', '').replace('.gz', '')
        # Take first part before dot or underscore
        parts = re.split(r'[_.]', basename)
        if parts:
            return parts[0]
        
        return None
    
    def _get_known_units(self) -> Set[str]:
        """
        Get set of known unit names from AGUR_UNITS_TABLE
        
        Returns:
            Set of unit names (lowercase)
        """
        known_units = set()
        agur_table = os.path.join(os.path.dirname(__file__), 'agur_release_tracking', 'AGUR_UNITS_TABLE.csv')
        
        if not os.path.exists(agur_table):
            return known_units
        
        try:
            with open(agur_table, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('UNIT_NAME'):
                        continue
                    parts = line.split(',')
                    if parts:
                        unit_name = parts[0].strip().lower()
                        known_units.add(unit_name)
        except Exception:
            pass
        
        return known_units
    
    def lookup_unit_workarea(self, unit_name: str) -> Optional[str]:
        """
        Look up unit's latest released workarea from AGUR_UNITS_TABLE
        
        Args:
            unit_name: Unit name (e.g., "pmux", "ccorea")
        
        Returns:
            Workarea path or None if not found
        """
        agur_table_path = os.path.join(
            os.path.dirname(__file__),
            'agur_release_tracking',
            'AGUR_UNITS_TABLE.csv'
        )
        
        if not os.path.exists(agur_table_path):
            if self.verbose:
                print(f"  [INFO] AGUR_UNITS_TABLE not found at: {agur_table_path}")
            return None
        
        try:
            with open(agur_table_path, 'r') as f:
                for line in f:
                    # Skip header
                    if line.startswith('UNIT,'):
                        continue
                    
                    parts = line.strip().split(',')
                    if len(parts) < 3:
                        continue
                    
                    table_unit = parts[0].strip()
                    workarea = parts[2].strip()
                    
                    if table_unit.lower() == unit_name.lower():
                        if self.verbose:
                            print(f"  [INFO] Found unit '{unit_name}' in AGUR table")
                            print(f"  [INFO] Using released workarea: {workarea}")
                        return workarea
            
            if self.verbose:
                print(f"  [WARN] Unit '{unit_name}' not found in AGUR table")
            return None
            
        except Exception as e:
            if self.verbose:
                print(f"  [WARN] Error reading AGUR table: {e}")
            return None
    
    def detect_workarea_from_eco(self, eco_file: str) -> Optional[str]:
        """
        Auto-detect workarea root from ECO file location
        
        Strategy (PRIORITY ORDER):
          1. Extract unit name from filename and look up in AGUR_UNITS_TABLE (PRIMARY)
          2. If table lookup fails, try directory walking (FALLBACK)
        
        Rationale:
          - AGUR table contains latest released workareas with proper reference files
          - Directory walking might find incomplete/FC workareas without reference files
          - Example: pmux_manual.innovus.tcl -> "pmux" -> lookup in AGUR table
        
        Common patterns:
          pmux_manual.innovus.tcl -> Extract "pmux" -> Look up in AGUR table (DEFAULT)
          pmux.ipo1000-1001.*.tcl -> Extract "pmux" -> Look up in AGUR table (DEFAULT)
          
          Fallback (if table lookup fails):
          {workarea}/signoff_flow/auto_pt/work_*/eco.tcl         -> 3 levels up
          {workarea}/signoff_flow/auto_pt/eco.tcl                -> 2 levels up
          {workarea}/unit_scripts/unit_eco.tcl                   -> 1 level up
        
        Args:
            eco_file: Path to ECO file
        
        Returns:
            Workarea root path or None if not detected
        """
        eco_path = os.path.abspath(eco_file)
        
        # Strategy 1 (PRIMARY): Extract unit name and look up in AGUR table
        unit_name = self.extract_unit_from_filename(eco_file)
        if unit_name:
            workarea = self.lookup_unit_workarea(unit_name)
            if workarea:
                if self.verbose:
                    print(f"  Found unit '{unit_name}' workarea in AGUR table: {workarea}")
                return workarea
            elif self.verbose:
                print(f"  Unit '{unit_name}' extracted from filename, but not found in AGUR table")
        
        # Strategy 2 (FALLBACK): Walk up directory tree looking for workarea markers
        if self.verbose:
            print(f"  AGUR table lookup failed, trying directory walking...")
        
        current_dir = os.path.dirname(eco_path)
        temp_dir = current_dir
        for _ in range(5):
            # Check for workarea markers
            has_signoff = os.path.exists(os.path.join(temp_dir, "signoff_flow"))
            has_pnr = os.path.exists(os.path.join(temp_dir, "pnr_flow"))
            has_syn = os.path.exists(os.path.join(temp_dir, "syn_flow"))
            
            if has_signoff or (has_pnr and has_syn):
                if self.verbose:
                    print(f"  Auto-detected workarea from location: {temp_dir}")
                return temp_dir
            
            parent = os.path.dirname(temp_dir)
            if parent == temp_dir:  # Reached filesystem root
                break
            temp_dir = parent
        
        return None
    
    def discover_reference_files(self, eco_file: str, 
                                 workarea_override: Optional[str] = None) -> Dict[str, Optional[str]]:
        """
        Discover reference files with priority order:
          1. Explicit paths (self.clock_tree_rpt, etc.) - highest priority
          2. Workarea override parameter - medium priority
          3. Auto-detected workarea from ECO location - lowest priority
        
        Args:
            eco_file: ECO file path (for auto-detection)
            workarea_override: Override workarea path (optional)
        
        Returns:
            Dict with keys: 'clock_tree_rpt', 'beflow_config', 'dont_use_patterns', 'workarea'
        """
        result = {
            'clock_tree_rpt': self.clock_tree_rpt,
            'beflow_config': self.beflow_config,
            'dont_use_patterns': self.dont_use_patterns,
            'workarea': None
        }
        
        # Determine workarea (priority: explicit > override > auto-detect)
        if workarea_override:
            result['workarea'] = workarea_override
        elif self.workarea:
            result['workarea'] = self.workarea
        else:
            result['workarea'] = self.detect_workarea_from_eco(eco_file)
        
        # If we have a workarea, discover missing reference files
        if result['workarea']:
            wa = result['workarea']
            
            # Find ClockTree.rpt (if not explicitly provided)
            if not result['clock_tree_rpt']:
                for gl_dir in ["signoff_flow/gl-check", "signoff_flow/gl_check"]:
                    test_path = os.path.join(wa, gl_dir, "reports", "ClockTree.rpt")
                    if os.path.exists(test_path):
                        result['clock_tree_rpt'] = test_path
                        break
            
            # Find beflow_config.yaml (if not explicitly provided)
            if not result['beflow_config']:
                for gl_dir in ["signoff_flow/gl-check", "signoff_flow/gl_check"]:
                    test_path = os.path.join(wa, gl_dir, "beflow_config.yaml")
                    if os.path.exists(test_path):
                        result['beflow_config'] = test_path
                        break
            
            # Find dont_use patterns (if not explicitly provided)
            if not result['dont_use_patterns']:
                # Common locations for dont_use patterns file
                search_paths = [
                    "signoff_flow/gl-check/results/dont_use_cell_patterns.tcl",
                    "signoff_flow/gl-check/dont_use_cell_patterns.tcl",
                    "syn_flow/dc/results/dont_use_cell_patterns.tcl",
                    "signoff_flow/auto_pt/results/dont_use_cell_patterns.tcl",
                ]
                
                for path in search_paths:
                    test_path = os.path.join(wa, path)
                    if os.path.exists(test_path):
                        result['dont_use_patterns'] = test_path
                        break
                
                # Fallback: Search for gl-check.log in timestamped directories
                if not result['dont_use_patterns']:
                    gl_check_dir = os.path.join(wa, "signoff_flow/gl-check")
                    if os.path.isdir(gl_check_dir):
                        # Find most recent timestamped directory
                        timestamped_dirs = []
                        try:
                            for item in os.listdir(gl_check_dir):
                                item_path = os.path.join(gl_check_dir, item)
                                if os.path.isdir(item_path) and re.match(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}', item):
                                    timestamped_dirs.append((item, item_path))
                            
                            if timestamped_dirs:
                                # Sort by timestamp (newest first)
                                timestamped_dirs.sort(reverse=True)
                                for _, dir_path in timestamped_dirs:
                                    log_path = os.path.join(dir_path, "gl-check.log")
                                    if os.path.exists(log_path):
                                        result['dont_use_patterns'] = log_path
                                        break
                        except Exception:
                            pass
        
        return result
    
    def parse_clock_tree_cells(self, clock_tree_rpt: str) -> Set[str]:
        """
        Parse ClockTree.rpt to get set of all clock tree instance names
        
        Format: [design]:instance_path/pin(CELL_TYPE)
        
        Args:
            clock_tree_rpt: Path to ClockTree.rpt file
        
        Returns:
            Set of instance names that are part of the clock tree
        """
        clock_tree_instances = set()
        
        try:
            if not os.path.exists(clock_tree_rpt):
                return clock_tree_instances
            
            with open(clock_tree_rpt, 'r') as f:
                for line in f:
                    # Match pattern: [design]:instance_path/pin(CELL_TYPE)
                    match = re.match(r'\s*\[[^\]]+\]:([^/\(]+)', line)
                    if match:
                        instance_name = match.group(1).strip()
                        if instance_name:
                            clock_tree_instances.add(instance_name)
            
            if self.verbose:
                print(f"  Parsed {len(clock_tree_instances)} clock tree instances from ClockTree.rpt")
            
            return clock_tree_instances
            
        except Exception as e:
            if self.verbose:
                print(f"  Warning: Error parsing ClockTree.rpt: {e}")
            return clock_tree_instances
    
    def parse_allowed_clock_patterns(self, beflow_config: str) -> List[re.Pattern]:
        """
        Extract and compile allowed clock tree cell regex patterns from beflow_config.yaml
        
        Format: glc allowed_clktree_cells_rex(design): ['PATTERN1', 'PATTERN2', ...]
        
        Args:
            beflow_config: Path to beflow_config.yaml file
        
        Returns:
            List of compiled regex patterns for allowed clock tree cells
        """
        compiled_patterns = []
        
        try:
            if not os.path.exists(beflow_config):
                return compiled_patterns
            
            with open(beflow_config, 'r') as f:
                content = f.read()
            
            # Extract allowed_clktree_cells_rex
            for line in content.split('\n'):
                if 'allowed_clktree_cells_rex' in line:
                    match = re.search(r'\[(.*)\]', line)
                    if match:
                        cells_str = match.group(1)
                        patterns = [cell.strip().strip("'\"") for cell in re.findall(r"'([^']*)'", cells_str)]
                        
                        # Compile each pattern
                        for pattern in patterns:
                            if pattern:
                                try:
                                    compiled_patterns.append(re.compile(pattern))
                                except re.error:
                                    if self.verbose:
                                        print(f"  Warning: Invalid regex pattern: {pattern}")
                        break
            
            if self.verbose:
                print(f"  Parsed {len(compiled_patterns)} allowed clock cell patterns from beflow_config")
            
            return compiled_patterns
            
        except Exception as e:
            if self.verbose:
                print(f"  Warning: Error parsing beflow_config: {e}")
            return compiled_patterns
    
    def parse_dont_use_patterns(self, dont_use_file: str) -> List[re.Pattern]:
        """
        Parse dont_use cell patterns from dont_use_cell_patterns.tcl or gl-check.log
        
        Args:
            dont_use_file: Path to dont_use patterns file
        
        Returns:
            List of compiled regex patterns for dont_use cells
        """
        compiled_patterns = []
        
        try:
            if not os.path.exists(dont_use_file):
                return compiled_patterns
            
            with open(dont_use_file, 'r') as f:
                content = f.read()
            
            # Try to extract patterns from dont_use_cell_patterns.tcl format
            if 'dont_use_cell_patterns.tcl' in dont_use_file:
                # Format: set dont_use_cell_patterns {PATTERN1 PATTERN2 ...}
                match = re.search(r'set\s+dont_use_cell_patterns\s+\{([^}]+)\}', content)
                if match:
                    patterns_str = match.group(1)
                    patterns = patterns_str.split()
                else:
                    # Try newline-separated format
                    patterns = [line.strip() for line in content.split('\n') 
                               if line.strip() and not line.strip().startswith('#')]
            else:
                # Try gl-check.log format
                # Format: Checker: dont_use_cells ... Pattern: PATTERN
                patterns = re.findall(r'Pattern:\s*([^\s]+)', content)
            
            # Compile patterns
            for pattern in patterns:
                if pattern:
                    try:
                        # Convert glob pattern to regex if needed
                        regex_pattern = pattern.replace('*', '.*')
                        compiled_patterns.append(re.compile(regex_pattern))
                    except re.error:
                        if self.verbose:
                            print(f"  Warning: Invalid dont_use pattern: {pattern}")
            
            if self.verbose:
                print(f"  Parsed {len(compiled_patterns)} dont_use cell patterns")
            
            return compiled_patterns
            
        except Exception as e:
            if self.verbose:
                print(f"  Warning: Error parsing dont_use patterns: {e}")
            return compiled_patterns
    
    def parse_eco_file(self, eco_file: str) -> Tuple[List[str], Dict[str, int]]:
        """
        Parse ECO file and extract commands
        
        Args:
            eco_file: Path to ECO TCL file
        
        Returns:
            Tuple of (eco_commands_list, command_breakdown_dict)
        """
        eco_commands = []
        command_breakdown = defaultdict(int)
        
        try:
            # Handle gzipped files
            if eco_file.endswith('.gz'):
                with gzip.open(eco_file, 'rt', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            else:
                with open(eco_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                eco_commands.append(line)
                
                # Count command types
                if line.startswith('ecoChangeCell'):
                    command_breakdown['ecoChangeCell'] += 1
                elif line.startswith('ecoAddRepeater'):
                    command_breakdown['ecoAddRepeater'] += 1
                elif line.startswith('size_cell'):
                    command_breakdown['size_cell'] += 1
                elif line.startswith('insert_buffer'):
                    command_breakdown['insert_buffer'] += 1
                elif line.startswith('placeInstance'):
                    command_breakdown['placeInstance'] += 1
                elif line.startswith('set_cell_location'):
                    command_breakdown['set_cell_location'] += 1
                elif line.startswith('add_buffer_on_route'):
                    command_breakdown['add_buffer_on_route'] += 1
                else:
                    # Other commands
                    cmd = line.split()[0] if line.split() else 'unknown'
                    command_breakdown[cmd] += 1
            
            return eco_commands, dict(command_breakdown)
            
        except Exception as e:
            if self.verbose:
                print(f"  Error parsing ECO file {eco_file}: {e}")
            return [], {}
    
    def check_dont_use_cells(self, eco_commands: List[str], 
                            dont_use_patterns: Optional[List[re.Pattern]] = None) -> List[Dict]:
        """
        Check for dont_use cells in ECO commands
        
        Args:
            eco_commands: List of ECO command lines
            dont_use_patterns: Compiled dont_use patterns (optional, will use cached if None)
        
        Returns:
            List of violation dicts with keys: 'cell_type', 'instance', 'command'
        """
        if dont_use_patterns is None:
            dont_use_patterns = self._dont_use_patterns_compiled or []
        
        violations = []
        
        for command_line in eco_commands:
            # Extract cell type from command
            cell_type = None
            instance = None
            
            # Pattern 1: ecoChangeCell -inst {INSTANCE} -cell {CELLTYPE}
            match = re.search(r'ecoChangeCell\s+-inst\s+\{([^}]+)\}\s+-cell\s+\{([^}]+)\}', command_line)
            if match:
                instance = match.group(1)
                cell_type = match.group(2)
            
            # Pattern 2: ecoAddRepeater ... -cell {CELLTYPE} -name {INSTANCE}
            if not cell_type and 'ecoAddRepeater' in command_line:
                cell_match = re.search(r'-cell\s+\{([^}]+)\}', command_line)
                name_match = re.search(r'-name\s+\{([^}]+)\}', command_line)
                if cell_match and name_match:
                    cell_type = cell_match.group(1)
                    instance = name_match.group(1)
            
            # Pattern 3: size_cell INSTANCE CELLTYPE
            if not cell_type:
                match = re.match(r'size_cell\s+(\S+)\s+(\S+)', command_line)
                if match:
                    instance = match.group(1)
                    cell_type = match.group(2)
            
            # Pattern 4: insert_buffer NET CELLTYPE INSTANCE
            if not cell_type:
                match = re.match(r'insert_buffer\s+\S+\s+(\S+)\s+(\S+)', command_line)
                if match:
                    cell_type = match.group(1)
                    instance = match.group(2)
            
            # Check if cell type matches any dont_use pattern
            if cell_type:
                for pattern in dont_use_patterns:
                    if pattern.match(cell_type):
                        violations.append({
                            'cell_type': cell_type,
                            'instance': instance,
                            'command': command_line
                        })
                        break
        
        return violations
    
    def check_inst_not_allowed_on_clocks(self, eco_commands: List[str],
                                         clock_tree_instances: Optional[Set[str]] = None,
                                         allowed_patterns: Optional[List[re.Pattern]] = None) -> List[Dict]:
        """
        Check for non-allowed cells on clock network (instNotAllowedOnClocks)
        
        Enhanced logic for ecoAddRepeater:
          - Checks both NEW instance (-name) and PREVIOUS instance (-term)
          - If previous instance is on clock network, new buffer will be too
        
        Args:
            eco_commands: List of ECO command lines
            clock_tree_instances: Set of clock tree instances (optional, will use cached if None)
            allowed_patterns: Compiled allowed patterns (optional, will use cached if None)
        
        Returns:
            List of violation dicts with keys: 'instance', 'cell_type', 'command', 
                                               'prev_instance' (for ecoAddRepeater)
        """
        if clock_tree_instances is None:
            clock_tree_instances = self._clock_tree_instances or set()
        
        if allowed_patterns is None:
            allowed_patterns = self._allowed_clock_patterns or []
        
        violations = []
        
        for command_line in eco_commands:
            instance_name = None
            cell_type = None
            prev_instance = None
            
            # Pattern 1: ecoChangeCell -inst {INSTANCE} -cell {CELLTYPE}
            match = re.search(r'ecoChangeCell\s+-inst\s+\{([^}]+)\}\s+-cell\s+\{([^}]+)\}', command_line)
            if match:
                instance_name = match.group(1)
                cell_type = match.group(2)
            
            # Pattern 2: ecoAddRepeater ... -name {INSTANCE} ... -cell {CELLTYPE}
            # Special handling: Check PREVIOUS instance from -term parameter
            if not instance_name and 'ecoAddRepeater' in command_line:
                cell_match = re.search(r'-cell\s+\{([^}]+)\}', command_line)
                name_match = re.search(r'-name\s+\{([^}]+)\}', command_line)
                term_match = re.search(r'-term\s+\{([^}]+)\}', command_line)
                
                if cell_match and name_match and term_match:
                    cell_type = cell_match.group(1)
                    instance_name = name_match.group(1)
                    
                    # Extract previous instance from -term {PREV_INST/PIN}
                    term_path = term_match.group(1)
                    prev_instance = term_path.rsplit('/', 1)[0] if '/' in term_path else term_path
                    
                    # Check if PREVIOUS instance is in clock tree
                    if prev_instance in clock_tree_instances:
                        # New buffer connects to clock network
                        pass  # Continue to validation
                    elif instance_name not in clock_tree_instances:
                        # Neither new nor previous in clock tree - skip
                        instance_name = None
                        cell_type = None
            
            # Pattern 3: size_cell INSTANCE CELLTYPE
            if not instance_name:
                match = re.match(r'size_cell\s+(\S+)\s+(\S+)', command_line)
                if match:
                    instance_name = match.group(1)
                    cell_type = match.group(2)
            
            # If we found both instance and cell type, check for violations
            if instance_name and cell_type:
                # Check if instance is in clock tree (or prev_instance for ecoAddRepeater)
                on_clock_tree = (instance_name in clock_tree_instances or 
                                (prev_instance and prev_instance in clock_tree_instances))
                
                if on_clock_tree:
                    # Check if cell type matches any allowed pattern
                    is_allowed = False
                    for pattern in allowed_patterns:
                        if pattern.match(cell_type):
                            is_allowed = True
                            break
                    
                    if not is_allowed:
                        violations.append({
                            'instance': instance_name,
                            'cell_type': cell_type,
                            'command': command_line,
                            'prev_instance': prev_instance
                        })
        
        return violations
    
    def check_clock_cells_on_data(self, eco_commands: List[str],
                                  clock_tree_instances: Optional[Set[str]] = None,
                                  allowed_patterns: Optional[List[re.Pattern]] = None) -> List[Dict]:
        """
        Check for clock cells used on data paths (informational check)
        
        Args:
            eco_commands: List of ECO command lines
            clock_tree_instances: Set of clock tree instances (optional)
            allowed_patterns: Compiled allowed clock patterns (optional)
        
        Returns:
            List of info dicts with keys: 'instance', 'cell_type', 'command'
        """
        if clock_tree_instances is None:
            clock_tree_instances = self._clock_tree_instances or set()
        
        if allowed_patterns is None:
            allowed_patterns = self._allowed_clock_patterns or []
        
        clock_cells_on_data = []
        
        for command_line in eco_commands:
            instance_name = None
            cell_type = None
            prev_instance = None
            
            # Same parsing logic as instNotAllowedOnClocks
            match = re.search(r'ecoChangeCell\s+-inst\s+\{([^}]+)\}\s+-cell\s+\{([^}]+)\}', command_line)
            if match:
                instance_name = match.group(1)
                cell_type = match.group(2)
            
            if not instance_name and 'ecoAddRepeater' in command_line:
                cell_match = re.search(r'-cell\s+\{([^}]+)\}', command_line)
                name_match = re.search(r'-name\s+\{([^}]+)\}', command_line)
                term_match = re.search(r'-term\s+\{([^}]+)\}', command_line)
                
                if cell_match and name_match and term_match:
                    cell_type = cell_match.group(1)
                    instance_name = name_match.group(1)
                    term_path = term_match.group(1)
                    prev_instance = term_path.rsplit('/', 1)[0] if '/' in term_path else term_path
                    
                    if prev_instance in clock_tree_instances:
                        pass
                    elif instance_name not in clock_tree_instances:
                        instance_name = None
                        cell_type = None
            
            if not instance_name:
                match = re.match(r'size_cell\s+(\S+)\s+(\S+)', command_line)
                if match:
                    instance_name = match.group(1)
                    cell_type = match.group(2)
            
            # Check if cell type is a clock cell
            if instance_name and cell_type:
                is_clock_cell = False
                for pattern in allowed_patterns:
                    if pattern.match(cell_type):
                        is_clock_cell = True
                        break
                
                if is_clock_cell:
                    # Check if instance is NOT in clock tree (i.e., on data path)
                    on_clock_tree = (instance_name in clock_tree_instances or 
                                    (prev_instance and prev_instance in clock_tree_instances))
                    
                    if not on_clock_tree:
                        clock_cells_on_data.append({
                            'instance': instance_name,
                            'cell_type': cell_type,
                            'command': command_line
                        })
        
        return clock_cells_on_data

