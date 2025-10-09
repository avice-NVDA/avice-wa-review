#!/usr/bin/env python3
#===============================================================================
#      +===+ +--+ +--+ +=+ +===+ +===+
#      |   | |  | |  | | | |     |    
#      |===| |  +-+  | | | |     |=== 
#      |   |  |     |  | | |     |    
#      |   |   +---+   +=+ +===+ +===+                                 
#            ~ Alon Vice Tools ~
# Copyright (c) 2025 Alon Vice (avice)
# All rights reserved.
# This script is the intellectual property of Alon Vice.
# For permissions and licensing, contact: avice@nvidia.com
#===============================================================================
# Script Name: avice_image_debug_report.py
# Purpose: Generate HTML debug report with most useful P&R images
#
# Description:
#   This script scans the IMAGES directory in a work area and generates an HTML
#   report containing the top 10 most useful pictures for P&R debug analysis.
#   It automatically detects available images and prioritizes them based on
#   their debug value (timing, clock tree, placement, routing issues, etc.)
#
# Usage:
#   python3 avice_image_debug_report.py <work_area_path> [ipo_name]
#
# Arguments:
#   work_area_path - Path to the design work area (required)
#   ipo_name       - Optional specific IPO to use (e.g., ipo2000, ipo1500)
#                    If not provided, uses first IPO found in .prc file
#
# Output:
#   - Generates {USER}_image_report_<unit>_<timestamp>.html
#   - Organizes images by category with top 6 most useful shown per subcategory
#   - 3-column grid layout (2 rows × 3 columns) for better viewing, click to expand images
#   - Postroute images get highest priority (final P&R stage)
#
# Examples:
#   python3 avice_image_debug_report.py /path/to/work/area
#   python3 avice_image_debug_report.py /path/to/work/area ipo2000
#===============================================================================

import os
import sys
import re
import glob
from datetime import datetime
from pathlib import Path


def extract_unit_name(wa_path):
    """Extract unit name from work area by reading unit_scripts/des_def.tcl"""
    des_def_path = os.path.join(wa_path, "unit_scripts", "des_def.tcl")
    
    if not os.path.exists(des_def_path):
        # Fallback: try to guess from directory structure
        # Look for common patterns in path
        path_parts = wa_path.split('/')
        for part in reversed(path_parts):
            if part and not part.startswith('agur_') and len(part) < 10:
                return part
        return "unknown_unit"
    
    try:
        with open(des_def_path, 'r') as f:
            for line in f:
                if 'bset top_hier' in line:
                    # Extract unit name from line like: bset top_hier prtm
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        return parts[2]
    except Exception as e:
        print(f"[Warning] Could not read {des_def_path}: {e}")
    
    return "unknown_unit"

def extract_ipo_name(wa_path, unit_name, user_specified_ipo=None):
    """Extract IPO directory name from .prc file"""
    prc_file = os.path.join(wa_path, "pnr_flow", "nv_flow", f"{unit_name}.prc")
    
    # If user specified an IPO and no .prc file, use the user's choice
    if not os.path.exists(prc_file):
        if user_specified_ipo:
            print(f"[Warning] PRC file not found: {prc_file}")
            print(f"[Info] Using user-specified IPO: {user_specified_ipo}")
            return user_specified_ipo
        else:
            print(f"[Warning] PRC file not found: {prc_file}")
            print("[Info] Falling back to default ipo1000")
            return "ipo1000"
    
    try:
        all_ipos = []
        with open(prc_file, 'r') as f:
            for line in f:
                # Look for lines starting with "  ipo"
                if line.startswith('  ipo') and ':' in line:
                    # Extract IPO name: "  ipo1000:" -> "ipo1000"
                    ipo_name = line.strip().replace('  ', '').replace(':', '').strip()
                    all_ipos.append(ipo_name)
        
        if not all_ipos:
            if user_specified_ipo:
                print(f"[Warning] No IPO configuration found in {prc_file}")
                print(f"[Info] Using user-specified IPO: {user_specified_ipo}")
                return user_specified_ipo
            else:
                print(f"[Warning] No IPO configuration found in {prc_file}")
                print("[Info] Falling back to default ipo1000")
                return "ipo1000"
        
        # If user specified an IPO, validate it exists
        if user_specified_ipo:
            if user_specified_ipo in all_ipos:
                print(f"[Info] Available IPOs: {', '.join(all_ipos)}")
                print(f"[Info] Using user-specified IPO: {user_specified_ipo}")
                return user_specified_ipo
            else:
                print(f"[Warning] User-specified IPO '{user_specified_ipo}' not found in {prc_file}")
                print(f"[Info] Available IPOs: {', '.join(all_ipos)}")
                print(f"[Info] Using first available IPO: {all_ipos[0]}")
                return all_ipos[0]
        
        # Use first IPO (like csh script does)
        selected_ipo = all_ipos[0]
        
        if len(all_ipos) > 1:
            print(f"[Info] Found multiple IPOs: {', '.join(all_ipos)}")
            print(f"[Info] Using: {selected_ipo} (first one found)")
            print(f"[Tip] To use a specific IPO, run: python3 {os.path.basename(sys.argv[0])} {sys.argv[1]} <ipo_name>")
        else:
            print(f"[Info] Found single IPO: {selected_ipo}")
            
        return selected_ipo
        
    except Exception as e:
        if user_specified_ipo:
            print(f"[Warning] Could not read PRC file {prc_file}: {e}")
            print(f"[Info] Using user-specified IPO: {user_specified_ipo}")
            return user_specified_ipo
        else:
            print(f"[Warning] Could not read PRC file {prc_file}: {e}")
            print("[Info] Falling back to default ipo1000")
            return "ipo1000"

def get_images_directory(wa_path, unit_name, ipo_name):
    """Construct path to images directory"""
    images_path = os.path.join(wa_path, "pnr_flow", "nv_flow", unit_name, ipo_name, "REPs", "IMAGES")
    return images_path

def scan_images(images_dir):
    """Scan images directory and return list of found images"""
    if not os.path.exists(images_dir):
        print(f"[Error] Images directory does not exist: {images_dir}")
        return []
    
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.svg']
    found_images = []
    
    for ext in image_extensions:
        pattern = os.path.join(images_dir, ext)
        found_images.extend(glob.glob(pattern))
        # Also search for files with uppercase extensions
        pattern = os.path.join(images_dir, ext.upper())
        found_images.extend(glob.glob(pattern))
    
    # Remove duplicates and sort
    found_images = list(set(found_images))
    found_images.sort()
    
    return found_images

def scan_all_images(wa_path, unit_name, ipo_name):
    """Scan all image directories in the work area and return categorized list"""
    all_images = []
    
    # Main IMAGES directory
    main_images_dir = get_images_directory(wa_path, unit_name, ipo_name)
    if os.path.exists(main_images_dir):
        main_images = scan_images(main_images_dir)
        for img in main_images:
            all_images.append(('main', img))
    
    # Additional image directories
    additional_dirs = [
        # Synthesis flow images
        (os.path.join(wa_path, "syn_flow", "dc", "reports", "color"), "synthesis"),
        # Clock tree visualizations in REPs
        (os.path.join(wa_path, "pnr_flow", "nv_flow", f"{unit_name}", ipo_name, "REPs"), "clock_viz"),
        # DRC snapshots
        (os.path.join(wa_path, "pnr_flow", "nv_flow", f"{unit_name}", ipo_name, "REPs", "drc_snapshots"), "drc_snapshots"),
        # ECO/Signoff images
        (os.path.join(wa_path, "signoff_flow", "nv_gate_eco", f"{unit_name}", ipo_name, "REPs"), "eco"),
        # Backup ECO images
        (os.path.join(wa_path, "signoff_flow", "nv_gate_eco.back", f"{unit_name}", ipo_name, "REPs"), "eco_backup"),
    ]
    
    for dir_path, category in additional_dirs:
        if os.path.exists(dir_path):
            images = scan_images(dir_path)
            for img in images:
                all_images.append((category, img))
    
    return all_images

def categorize_images(image_list):
    """Categorize and prioritize images based on debug usefulness"""
    
    # Define comprehensive categories and subcategories with patterns
    image_categories = {
        'Synthesis Flow': {
            'RTL-to-Gate Analysis': [
                (r'rtl2gate_layout', 95, 'RTL-to-gate layout visualization'),
                (r'rtl2gate_glbroutecongestion', 90, 'Global routing congestion from synthesis'),
                (r'rtl2gate_traces.*clock.*color', 85, 'Clock trace analysis from synthesis'),
                (r'rtl2gate_traces.*color', 80, 'Signal trace analysis from synthesis'),
            ],
            'Clock Trace Analysis': [
                (r'rtl2gate_traces_i1_clk_color', 90, 'i1 clock trace analysis'),
                (r'rtl2gate_traces_i2_clk_color', 90, 'i2 clock trace analysis'),
                (r'rtl2gate_traces_m1_clk_color', 85, 'm1 clock trace analysis'),
                (r'rtl2gate_traces_clkgate_color', 80, 'Clock gating trace analysis'),
            ],
            'Signal Trace Analysis': [
                (r'rtl2gate_traces_regin_color', 75, 'Register input trace analysis'),
                (r'rtl2gate_traces_regout_color', 75, 'Register output trace analysis'),
                (r'rtl2gate_traces_feedthrough_color', 70, 'Feedthrough trace analysis'),
                (r'rtl2gate_traces_wrapper_path_color', 70, 'Wrapper path trace analysis'),
            ]
        },
        
        'Clock Tree Visualization': {
            'FHCTS Clock Grids': [
                (r'fhcts.*grid', 95, 'FHCTS clock grid visualization'),
                (r'fhcts_i1_clk_grid', 90, 'i1 clock grid visualization'),
                (r'fhcts_i2_clk.*grid', 90, 'i2 clock grid visualization'),
            ],
            'FHCTS Clock Trees': [
                (r'fhcts.*tree', 95, 'FHCTS clock tree topology'),
                (r'fhcts_i1_clk_tree', 90, 'i1 clock tree topology'),
                (r'fhcts_i2_clk.*tree', 90, 'i2 clock tree topology'),
            ]
        },
        
        'DRC Violation Snapshots': {
            'Metal Short Violations': [
                (r'.*metal_short.*zoom', 95, 'Metal short violation snapshot'),
                (r'.*metal_short', 90, 'Metal short violation'),
            ],
            'End of Line Keepout Violations': [
                (r'.*endofline_keepout.*zoom', 95, 'End of line keepout violation snapshot'),
                (r'.*endofline_keepout', 90, 'End of line keepout violation'),
            ],
            'Via Stack Violations': [
                (r'maxviastack.*v3s', 90, 'Via stack violation V3S layer'),
                (r'maxviastack.*v4t', 90, 'Via stack violation V4T layer'),
                (r'maxviastack', 85, 'Via stack violations'),
            ],
            'Spacing Violations': [
                (r'parallel_run_length_spacing', 85, 'Parallel run length spacing violation'),
                (r'spacing.*violation', 80, 'Spacing violations'),
            ],
            'General DRC Snapshots': [
                (r'.*zoom.*\.png$', 80, 'DRC violation snapshot'),
                (r'.*drc.*snapshot', 75, 'DRC snapshot'),
                (r'.*violation.*zoom', 70, 'Violation snapshot'),
            ]
        },
        
        'ECO/Signoff Analysis': {
            'ECO Impact Analysis': [
                (r'eco.*images.*eco_in', 90, 'ECO input analysis'),
                (r'cell_displacement.*eco_in', 85, 'Cell displacement ECO analysis'),
                (r'cell_displacement', 80, 'Cell displacement analysis'),
                (r'eco_summary.*drc', 85, 'ECO DRC summary'),
            ],
            'Legalization Issues': [
                (r'bad_legalizations', 80, 'Bad legalization cases'),
                (r'legalization.*issue', 75, 'Legalization issues'),
            ]
        },
        'Timing': {
            'Hold Violations': [
                (r'timing\.hold\.external\.(input|output)\.worst.*failed.*paths', 100, 'Critical hold timing violations'),
                (r'timing\.hold\.external\.(input|output)\.path_slack_heatmap', 95, 'Hold timing slack heatmap'),
                (r'timing\.hold\.internal\.(input|output)\.worst.*failed.*paths', 90, 'Internal hold violations'),
                (r'timing\.hold\..*violations', 85, 'Hold timing violations'),
                (r'timing\.hold', 80, 'General hold timing analysis'),
            ],
            'Setup Violations': [
                (r'timing\.setup\.external\.(input|output)\.worst.*failed.*paths', 100, 'Critical setup timing violations'),
                (r'timing\.setup\.external\.(input|output)\.path_slack_heatmap', 95, 'Setup timing slack heatmap'),
                (r'timing\.setup\.internal\.(input|output)\.worst.*failed.*paths', 90, 'Internal setup violations'),
                (r'timing\.setup\..*violations', 85, 'Setup timing violations'),
                (r'timing\.setup', 80, 'General setup timing analysis'),
            ],
            'Input/Output Timing': [
                (r'timing\..*external\.input', 85, 'Input timing analysis'),
                (r'timing\..*external\.output', 85, 'Output timing analysis'),
                (r'timing\..*io.*constraints', 75, 'I/O timing constraints'),
                (r'timing\..*external', 70, 'External timing analysis'),
            ],
            'General Timing': [
                (r'timing\..*slack.*histogram', 85, 'Timing slack distribution'),
                (r'timing\..*summary', 80, 'Overall timing summary'),
                (r'timing\..*paths', 75, 'Critical path analysis'),
                (r'timing\..*report', 70, 'General timing report'),
                (r'timing\.', 65, 'Timing analysis'),
            ]
        },
        
        'DRC/DRV': {
            'Design Rule Violations': [
                (r'drc.*violations', 90, 'Design rule check violations'),
                (r'drv.*violations', 90, 'Design rule violations'),
                (r'drc.*summary', 85, 'DRC summary report'),
                (r'spacing.*violations', 80, 'Metal spacing violations'),
                (r'width.*violations', 80, 'Wire width violations'),
            ],
            'Layer Violations': [
                (r'metal.*drc', 75, 'Metal layer DRC issues'),
                (r'via.*drc', 75, 'Via DRC issues'),
                (r'cut.*violations', 70, 'Cut layer violations'),
            ]
        },
        
        'Clock Tree': {
            'Clock Tree Topology': [
                (r'clock_tree\.topology_spine\.all_clocks', 100, 'Clock tree spine topology - all clocks overview'),
                (r'clock_tree\.common_tap_endpoint_groups', 95, 'Clock tree endpoint grouping'),
                (r'clock_tree\.endpoint_density', 90, 'Clock endpoint density map'),
                (r'clock_tree\..*topology', 85, 'Clock tree topology'),
                (r'clock_tree\..*structure', 80, 'Clock tree structure'),
            ],
            'Clock Timing': [
                (r'clock_tree\.insertion_delay_from_clock_source.*\.(hold|setup)', 95, 'Clock insertion delay timing'),
                (r'clock_tree\.endpoint_manhattan_distance_from_clock_source', 90, 'Clock source distance analysis'),
                (r'clock_tree\.endpoint_manhattan_distance_from_clock_tap', 85, 'Clock tap distance analysis'),
                (r'clock.*skew', 80, 'Clock skew analysis'),
                (r'clock.*latency', 75, 'Clock latency distribution'),
            ],
            'CTS Stage Analysis': [
                (r'\.cts\.custom\.', 75, 'Clock Tree Synthesis stage'),
                (r'clock.*buffer.*insertion', 80, 'Clock buffer insertion'),
                (r'clock.*gating', 75, 'Clock gating analysis'),
                (r'clock.*tree.*synthesis', 75, 'Clock tree synthesis'),
                (r'clock_tree\.', 70, 'General clock tree visualization'),
            ]
        },
        
        'Power': {
            'Power Density Analysis': [
                (r'power_density\.total', 95, 'Total power density heatmap'),
                (r'power_density\.switching', 90, 'Switching power density'),
                (r'power_density\.leakage', 85, 'Leakage power density'),
                (r'power_density\.internal', 80, 'Internal power density'),
                (r'power_density\.', 75, 'Power density analysis'),
            ],
            'IR Drop Analysis': [
                (r'power.*rail.*voltage.*drop', 90, 'Power rail IR drop analysis'),
                (r'power.*ir.*drop', 85, 'IR drop heatmap'),
                (r'voltage.*drop', 80, 'Voltage drop analysis'),
                (r'power.*integrity', 75, 'Power integrity analysis'),
            ],
            'Power Distribution': [
                (r'power.*grid', 75, 'Power grid visualization'),
                (r'power.*rail', 70, 'Power rail analysis'),
                (r'power.*distribution', 65, 'Power distribution network'),
            ]
        },
        
        'Placement': {
            'Placement Density': [
                (r'placement.*density', 85, 'Placement density heatmap'),
                (r'placement.*congestion', 80, 'Placement congestion analysis'),
                (r'utilization.*map', 75, 'Cell utilization map'),
            ],
            'Placement Quality': [
                (r'placement.*legalization', 70, 'Placement legalization'),
                (r'placement.*optimization', 65, 'Placement optimization'),
                (r'placement.*analysis', 60, 'General placement analysis'),
            ]
        },
        
        'Routing': {
            'Route Length Analysis': [
                (r'routing\.route_length\.net_type\.total', 90, 'Total route length analysis'),
                (r'routing\.route_length\.net_type\.clock', 85, 'Clock net route length'),
                (r'routing\.route_length\.net_type\.signal', 80, 'Signal net route length'),
                (r'routing\.route_length\.net_type\.scan', 75, 'Scan net route length'),
                (r'routing\.route_length', 70, 'Route length analysis'),
            ],
            'Routing Stage Analysis': [
                (r'\.route\.custom\.', 75, 'Routing stage analysis'),
                (r'routing.*congestion', 85, 'Routing congestion analysis'),
                (r'congestion.*map', 80, 'Congestion heatmap'),
                (r'routing.*overflow', 75, 'Routing overflow analysis'),
            ],
            'Layer Usage': [
                (r'routing.*layer.*usage', 75, 'Metal layer usage'),
                (r'metal.*density', 70, 'Metal density per layer'),
                (r'via.*usage', 70, 'Via usage analysis'),
            ]
        },
        
        'Signal Integrity': {
            'Crosstalk Analysis': [
                (r'crosstalk.*analysis', 70, 'Crosstalk analysis'),
                (r'noise.*analysis', 65, 'Signal noise analysis'),
                (r'signal.*integrity', 60, 'General signal integrity'),
            ],
            'EMI/EMC': [
                (r'emi.*analysis', 60, 'EMI analysis'),
                (r'emc.*analysis', 60, 'EMC analysis'),
                (r'reflection.*analysis', 55, 'Signal reflection analysis'),
            ]
        },
        
        'Floorplan/Layout': {
            'Floorplan Stage': [
                (r'\.plan\.custom\.', 70, 'Floorplanning stage analysis'),
                (r'floorplan.*overview', 65, 'Chip floorplan overview'),
                (r'floorplan.*analysis', 60, 'Floorplan analysis'),
                (r'blockage.*map', 55, 'Routing blockage map'),
            ],
            'Placement Stage': [
                (r'\.place\.custom\.', 65, 'Placement stage analysis'),
                (r'placement.*overview', 60, 'Placement overview'),
                (r'placement.*analysis', 55, 'Placement analysis'),
            ],
            'General Layout': [
                (r'layout.*overview', 50, 'General layout view'),
                (r'metal.*layers', 45, 'Metal layer visualization'),
                (r'layout.*analysis', 40, 'Layout analysis'),
            ]
        }
    }
    
    categorized_images = {}
    
    # Initialize categories
    for category in image_categories:
        categorized_images[category] = {}
        for subcategory in image_categories[category]:
            categorized_images[category][subcategory] = []
    
    # Add "Other" category for uncategorized images
    categorized_images['Other'] = {'Uncategorized': []}
    
    # Categorize each image
    for image_item in image_list:
        # Handle both old format (string) and new format (tuple)
        if isinstance(image_item, tuple):
            image_category, image_path = image_item
        else:
            image_category = 'main'
            image_path = image_item
            
        image_name = os.path.basename(image_path).lower()
        best_match = None
        best_score = 0
        best_category = 'Other'
        best_subcategory = 'Uncategorized'
        best_description = 'Debug image'
        
        # Check against all patterns
        for category, subcategories in image_categories.items():
            for subcategory, patterns in subcategories.items():
                for pattern, score, description in patterns:
                    if re.search(pattern, image_name) and score > best_score:
                        best_score = score
                        best_category = category
                        best_subcategory = subcategory
                        best_description = description
        
        # P&R FLOW STAGE PRIORITY BOOSTS - highest priority for later stages
        flow_stage_boosts = {
            'postroute': 50,  # Highest priority - final P&R stage
            'route': 30,      # High priority - routing stage  
            'cts': 20,        # Medium-high priority - clock tree synthesis
            'place': 10,      # Medium priority - placement stage
            'plan': 5         # Lower priority - floorplanning stage
        }
        
        flow_stage_names = {
            'postroute': 'Post-route (Final P&R)',
            'route': 'Routing',
            'cts': 'Clock Tree Synthesis', 
            'place': 'Placement',
            'plan': 'Floorplanning'
        }
        
        for stage, boost in flow_stage_boosts.items():
            if re.search(rf'\.{stage}\.custom\.', image_name):
                best_score += boost
                best_description += f' ({flow_stage_names[stage]} stage)'
                break
        
        # Add source category information
        if image_category != 'main':
            best_description += f' (from {image_category})'
        
        # Default score for uncategorized images
        if best_score == 0:
            best_score = 10
        
        # Add to appropriate category
        categorized_images[best_category][best_subcategory].append({
            'path': image_path,
            'name': os.path.basename(image_path),
            'score': best_score,
            'description': best_description,
            'source': image_category
        })
    
    # Sort images within each subcategory by score (descending)
    for category in categorized_images:
        for subcategory in categorized_images[category]:
            categorized_images[category][subcategory].sort(key=lambda x: x['score'], reverse=True)
    
    return categorized_images


def generate_html_report(unit_name, images_dir, categorized_images, output_file):
    """Generate HTML debug report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AVICE P&R Debug Report - {unit_name}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background-color: #1e1e1e;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 2px solid #00ff00;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .logo {{
            text-align: center;
            margin-bottom: 10px;
        }}
        
        .logo img {{
            max-height: 120px;
            max-width: 400px;
            height: auto;
            width: auto;
            cursor: pointer;
            transition: transform 0.2s ease;
            border-radius: 6px;
        }}
        
        .logo img:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
        }}
        
        .title {{
            color: #00ff00;
            font-size: 24px;
            font-weight: bold;
        }}
        
        .info {{
            color: #cccccc;
            font-size: 14px;
            margin: 10px 0;
        }}
        
        .category-container {{
            margin: 20px 0;
            border: 2px solid #333;
            border-radius: 10px;
            background-color: #2d2d2d;
        }}
        
        .category-header {{
            background-color: #333;
            color: #00ff00;
            padding: 15px 20px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 8px 8px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .category-header:hover {{
            background-color: #444;
        }}
        
        .category-toggle {{
            font-size: 16px;
            color: #00ff00;
        }}
        
        .subcategory-container {{
            margin: 10px 20px;
            border: 1px solid #444;
            border-radius: 8px;
            background-color: #1e1e1e;
        }}
        
        .subcategory-header {{
            background-color: #444;
            color: #cccccc;
            padding: 10px 15px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 6px 6px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .subcategory-header:hover {{
            background-color: #555;
        }}
        
        .images-grid {{
            /* Multiple fallback approaches for maximum compatibility */
            margin: 15px 0;
            padding: 0;
            width: 100%;
            
            /* Method 1: Float-based layout (most compatible) */
            overflow: hidden;
            zoom: 1; /* IE hasLayout trigger */
        }}
        
        .images-grid:after {{
            content: "";
            display: table;
            clear: both;
        }}
        
        /* Try CSS Grid first for modern browsers */
        @supports (display: grid) {{
            .images-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                grid-gap: 15px;
                margin: 15px;
                overflow: visible;
            }}
        }}
        
        /* Flexbox fallback for semi-modern browsers */
        @supports (display: flex) and (not (display: grid)) {{
            .images-grid {{
                display: flex;
                flex-wrap: wrap;
                margin: 15px -7.5px;
                overflow: visible;
            }}
        }}
        
        /* Table layout fallback for very old browsers */
        @supports (not (display: flex)) and (not (display: grid)) {{
            .images-grid {{
                display: table;
                width: calc(100% - 30px);
                margin: 15px;
                table-layout: fixed;
                border-spacing: 15px 0;
            }}
        }}
        
        .image-container {{
            border: 1px solid #555;
            border-radius: 6px;
            padding: 12px;
            background-color: #2d2d2d;
            box-sizing: border-box;
            
            /* Default: Float-based 3-column layout (most compatible) */
            float: left;
            width: calc(33.33% - 10px);
            margin: 0 5px 15px 5px;
            
            /* Inner content layout */
            display: block;
        }}
        
        /* CSS Grid support */
        @supports (display: grid) {{
            .image-container {{
                float: none;
                width: auto;
                margin: 0;
            }}
        }}
        
        /* Flexbox support (but not Grid) */
        @supports (display: flex) and (not (display: grid)) {{
            .image-container {{
                float: none;
                width: calc(33.33% - 10px);
                margin: 5px;
                display: flex;
                flex-direction: column;
            }}
        }}
        
        /* Table layout support (very old browsers) */
        @supports (not (display: flex)) and (not (display: grid)) {{
            .image-container {{
                float: none;
                display: table-cell;
                width: 33.33%;
                margin: 0;
                vertical-align: top;
            }}
        }}
        
        /* Ensure proper clearing for floated elements - every 3rd item */
        .image-container:nth-child(3n+1) {{
            clear: left;
        }}
        
        .image-title {{
            color: #00ff00;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 6px;
            line-height: 1.2;
        }}
        
        .image-description {{
            color: #cccccc;
            margin-bottom: 8px;
            font-size: 12px;
            line-height: 1.3;
        }}
        
        .image-path {{
            color: #888;
            font-size: 10px;
            margin-bottom: 8px;
            word-break: break-all;
            line-height: 1.2;
        }}
        
        .image-source {{
            color: #00ff00;
            font-size: 10px;
            margin-bottom: 8px;
            font-weight: bold;
            background-color: #333;
            padding: 2px 6px;
            border-radius: 3px;
            display: inline-block;
        }}
        
        .image {{
            width: 100%;
            max-width: none;
            max-height: 250px;
            height: auto;
            object-fit: contain;
            border: 2px solid #555;
            border-radius: 4px;
            cursor: pointer;
            transition: transform 0.2s ease;
            display: block;
        }}
        
        .image:hover {{
            transform: scale(1.02);
            border-color: #00ff00;
        }}
        
        .image-expanded {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        
        .image-expanded img {{
            max-width: 90%;
            max-height: 90%;
            border: 3px solid #00ff00;
        }}
        
        @media (max-width: 768px) {{
            /* Mobile: 2-column layout for better mobile experience */
            .image-container {{
                float: left;
                width: calc(50% - 7.5px);
                margin: 0 7.5px 15px 7.5px;
            }}
            
            .image-container:nth-child(3n+1) {{
                clear: none;
            }}
            
            .image-container:nth-child(odd) {{
                clear: left;
            }}
            
            /* CSS Grid mobile */
            @supports (display: grid) {{
                .images-grid {{
                    grid-template-columns: 1fr 1fr;
                }}
                
                .hidden-images.show {{
                    grid-template-columns: 1fr 1fr;
                }}
                
                .image-container {{
                    width: auto;
                    margin: 0;
                    float: none;
                }}
                
                .image-container:nth-child(odd) {{
                    clear: none;
                }}
            }}
            
            /* Flexbox mobile */
            @supports (display: flex) and (not (display: grid)) {{
                .image-container {{
                    width: calc(50% - 10px);
                    margin: 5px;
                }}
            }}
            
            /* Table layout mobile */
            @supports (not (display: flex)) and (not (display: grid)) {{
                .images-grid {{
                    display: table;
                    table-layout: fixed;
                }}
                
                .hidden-images.show {{
                    display: table;
                    table-layout: fixed;
                }}
                
                .image-container {{
                    display: table-cell;
                    width: 50%;
                    float: none;
                }}
            }}
        }}
        
        @media (max-width: 480px) {{
            /* Very small screens: Single column */
            .image-container {{
                float: none;
                width: calc(100% - 15px);
                margin: 7.5px;
                clear: both;
            }}
            
            .image-container:nth-child(odd) {{
                clear: both;
            }}
            
            @supports (display: grid) {{
                .images-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .hidden-images.show {{
                    grid-template-columns: 1fr;
                }}
            }}
            
            @supports (display: flex) and (not (display: grid)) {{
                .image-container {{
                    width: calc(100% - 10px);
                }}
            }}
            
            @supports (not (display: flex)) and (not (display: grid)) {{
                .image-container {{
                    display: block;
                    width: calc(100% - 15px);
                }}
            }}
        }}
        
        .priority {{
            background-color: #333;
            color: #00ff00;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }}
        
        .image-count {{
            background-color: #555;
            color: #ffffff;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
        }}
        
        .no-images {{
            text-align: center;
            color: #ff6666;
            font-size: 18px;
            margin: 50px 0;
        }}
        
        
        .category-content {{
            display: none;
        }}
        
        .category-content.expanded {{
            display: block;
        }}
        
        .subcategory-content {{
            display: none;
        }}
        
        .subcategory-content.expanded {{
            display: block;
        }}
        
        .show-more-btn {{
            background-color: #444;
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin: 10px auto;
            display: block;
            font-size: 12px;
            transition: background-color 0.2s ease;
        }}
        
        .show-more-btn:hover {{
            background-color: #555;
        }}
        
        .hidden-images {{
            display: none;
        }}
        
        .hidden-images.show {{
            /* Use the same layout approach as .images-grid */
            margin: 15px 0;
            padding: 0;
            width: 100%;
            overflow: hidden;
            zoom: 1;
        }}
        
        .hidden-images.show:after {{
            content: "";
            display: table;
            clear: both;
        }}
        
        /* CSS Grid support for hidden images */
        @supports (display: grid) {{
            .hidden-images.show {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                grid-gap: 15px;
                margin: 15px;
                overflow: visible;
            }}
        }}
        
        /* Flexbox support for hidden images */
        @supports (display: flex) and (not (display: grid)) {{
            .hidden-images.show {{
                display: flex;
                flex-wrap: wrap;
                margin: 15px -7.5px;
                overflow: visible;
            }}
        }}
        
        /* Table layout support for hidden images */
        @supports (not (display: flex)) and (not (display: grid)) {{
            .hidden-images.show {{
                display: table;
                width: calc(100% - 30px);
                margin: 15px;
                table-layout: fixed;
                border-spacing: 15px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <img src="/home/avice/scripts/avice_wa_review/images/avice_logo.png" alt="AVICE Logo" style="max-height: 120px; margin-bottom: 10px; cursor: pointer;" onclick="expandImage(this)">
        </div>
        <div class="title">P&R Debug Report</div>
        <div class="info">Unit: {unit_name} | Generated: {timestamp}</div>
        <div class="info">Images Directory: {images_dir}</div>
    </div>
"""
    
    # Count total images
    total_images = sum(len(subcategories[subcategory]) 
                      for subcategories in categorized_images.values() 
                      for subcategory in subcategories)
    
    if total_images == 0:
        html_content += """
    <div class="no-images">
        No images found in the specified directory.<br>
        Please check that the work area path is correct and contains P&R results.
    </div>
"""
    else:
        html_content += f"""
    <div class="info">Found {total_images} images organized by category. Click categories to expand:</div>
"""
        
        # Generate categorized content
        category_priority = ['Synthesis Flow', 'Clock Tree Visualization', 'Timing', 'DRC/DRV', 'Clock Tree', 'Power', 'Placement', 'Routing', 'Signal Integrity', 'Floorplan/Layout', 'DRC Violation Snapshots', 'ECO/Signoff Analysis', 'Other']
        
        for category in category_priority:
            if category not in categorized_images:
                continue
                
            # Count images in this category
            category_image_count = sum(len(categorized_images[category][subcategory]) 
                                     for subcategory in categorized_images[category])
            
            if category_image_count == 0:
                continue
                
            html_content += f"""
    <div class="category-container">
        <div class="category-header" onclick="toggleCategory('{category.replace(' ', '_').replace('/', '_')}')">            <span>{category}</span>
            <span><span class="image-count">{category_image_count} images</span> <span class="category-toggle" id="toggle_{category.replace(' ', '_').replace('/', '_')}">▼</span></span>
        </div>
        <div class="category-content" id="content_{category.replace(' ', '_').replace('/', '_')}">
"""
            
            # Generate subcategories
            for subcategory in categorized_images[category]:
                images = categorized_images[category][subcategory]
                if not images:
                    continue
                    
                subcategory_id = f"{category.replace(' ', '_').replace('/', '_')}_{subcategory.replace(' ', '_').replace('/', '_')}"
                
                html_content += f"""
            <div class="subcategory-container">
                <div class="subcategory-header" onclick="toggleSubcategory('{subcategory_id}')">
                    <span>{subcategory}</span>
                    <span><span class="image-count">{len(images)} images</span> <span class="category-toggle" id="toggle_{subcategory_id}">▼</span></span>
                </div>
                <div class="subcategory-content" id="content_{subcategory_id}">
"""
                
                # Generate images in subcategory - show top 6 first, then "Show More"
                html_content += '<div class="images-grid">\n'
                
                # Show top 6 images
                top_images = images[:6]
                remaining_images = images[6:]
                
                for img in top_images:
                    relative_path = os.path.relpath(img['path'], os.path.dirname(output_file))
                    
                    html_content += f"""
                        <div class="image-container">
                            <div class="image-title">{img['name']} <span class="priority">Score: {img['score']}</span></div>
                            <div class="image-description">{img['description']}</div>
                            <div class="image-path">{img['path']}</div>
                            <div class="image-source">Source: {img.get('source', 'main')}</div>
                            <img src="{relative_path}" alt="{img['name']}" class="image" 
                                 onclick="expandImage(this)"
                                 onerror="this.style.display='none'; this.nextSibling.style.display='block';">
                            <div style="display:none; color:#ff6666; padding:20px; text-align:center;">
                                Image not accessible: {relative_path}
                            </div>
                        </div>
"""
                
                # Add remaining images in hidden container
                if remaining_images:
                    html_content += f'</div>\n'  # Close first grid
                    html_content += f'<button class="show-more-btn" onclick="showMoreImages(\'{subcategory_id}\', this)">Show {len(remaining_images)} More Images</button>\n'
                    html_content += f'<div class="images-grid hidden-images" id="hidden_{subcategory_id}">\n'
                    
                    for img in remaining_images:
                        relative_path = os.path.relpath(img['path'], os.path.dirname(output_file))
                        
                        html_content += f"""
                        <div class="image-container">
                            <div class="image-title">{img['name']} <span class="priority">Score: {img['score']}</span></div>
                            <div class="image-description">{img['description']}</div>
                            <div class="image-path">{img['path']}</div>
                            <div class="image-source">Source: {img.get('source', 'main')}</div>
                            <img src="{relative_path}" alt="{img['name']}" class="image"
                                 onclick="expandImage(this)" 
                                 onerror="this.style.display='none'; this.nextSibling.style.display='block';">
                            <div style="display:none; color:#ff6666; padding:20px; text-align:center;">
                                Image not accessible: {relative_path}
                            </div>
                        </div>
"""
                
                html_content += '</div>\n'  # Close images grid
                
                html_content += """
                </div>
            </div>
"""
            
            html_content += """
        </div>
    </div>
"""
    
    
    html_content += """
    <script>
        // Cross-browser compatible class manipulation
        function hasClass(element, className) {
            if (element.classList) {
                return element.classList.contains(className);
            } else {
                return element.className.indexOf(className) > -1;
            }
        }
        
        function addClass(element, className) {
            if (element.classList) {
                element.classList.add(className);
            } else {
                if (!hasClass(element, className)) {
                    element.className += ' ' + className;
                }
            }
        }
        
        function removeClass(element, className) {
            if (element.classList) {
                element.classList.remove(className);
            } else {
                element.className = element.className.replace(new RegExp('(^|\\\\s)' + className + '(\\\\s|$)', 'g'), ' ').replace(/\\\\s+/g, ' ').trim();
            }
        }
        
        function toggleCategory(categoryId) {
            var content = document.getElementById('content_' + categoryId);
            var toggle = document.getElementById('toggle_' + categoryId);
            
            if (!content || !toggle) return;
            
            if (hasClass(content, 'expanded')) {
                removeClass(content, 'expanded');
                toggle.innerHTML = '▼';
            } else {
                addClass(content, 'expanded');
                toggle.innerHTML = '▲';
            }
        }
        
        function toggleSubcategory(subcategoryId) {
            var content = document.getElementById('content_' + subcategoryId);
            var toggle = document.getElementById('toggle_' + subcategoryId);
            
            if (!content || !toggle) return;
            
            if (hasClass(content, 'expanded')) {
                removeClass(content, 'expanded');
                toggle.innerHTML = '▼';
            } else {
                addClass(content, 'expanded');
                toggle.innerHTML = '▲';
            }
        }
        
        function showMoreImages(subcategoryId, buttonElement) {
            var hiddenContainer = document.getElementById('hidden_' + subcategoryId);
            
            if (!hiddenContainer) {
                if (console && console.error) {
                    console.error('Hidden container not found:', 'hidden_' + subcategoryId);
                }
                return;
            }
            
            if (hasClass(hiddenContainer, 'show')) {
                removeClass(hiddenContainer, 'show');
                buttonElement.innerHTML = buttonElement.innerHTML.replace('Hide', 'Show');
            } else {
                addClass(hiddenContainer, 'show');
                buttonElement.innerHTML = buttonElement.innerHTML.replace('Show', 'Hide');
            }
        }
        
        
        function expandImage(imgElement) {
            // Create overlay
            var overlay = document.createElement('div');
            overlay.className = 'image-expanded';
            
            // Create expanded image
            var expandedImg = document.createElement('img');
            expandedImg.src = imgElement.src;
            expandedImg.alt = imgElement.alt;
            
            overlay.appendChild(expandedImg);
            document.body.appendChild(overlay);
            
            // Close on click
            overlay.onclick = function() {
                if (document.body.contains(overlay)) {
                    document.body.removeChild(overlay);
                }
            };
            
            // Close on escape key
            function escapeHandler(e) {
                e = e || window.event;
                if ((e.keyCode || e.which) === 27) {
                    if (document.body.contains(overlay)) {
                        document.body.removeChild(overlay);
                        if (document.removeEventListener) {
                            document.removeEventListener('keydown', escapeHandler);
                        } else if (document.detachEvent) {
                            document.detachEvent('onkeydown', escapeHandler);
                        }
                    }
                }
            }
            
            if (document.addEventListener) {
                document.addEventListener('keydown', escapeHandler);
            } else if (document.attachEvent) {
                document.attachEvent('onkeydown', escapeHandler);
            }
        }
        
        // Cross-browser DOM ready function
        function domReady(fn) {
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                setTimeout(fn, 1);
            } else if (document.addEventListener) {
                document.addEventListener('DOMContentLoaded', fn);
            } else if (document.attachEvent) {
                document.attachEvent('onreadystatechange', function() {
                    if (document.readyState === 'complete') fn();
                });
            }
        }
        
        // Categories start collapsed by default
    </script>
</body>
</html>"""
    
    try:
        with open(output_file, 'w') as f:
            f.write(html_content)
        print(f"[Success] HTML report generated: {output_file}")
        return True
    except Exception as e:
        print(f"[Error] Could not write HTML file: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 avice_image_debug_report.py <work_area_path> [ipo_name]")
        print("Examples:")
        print("  python3 avice_image_debug_report.py /home/scratch.avice_vlsi/agur/SFNL/prtm/work_area")
        print("  python3 avice_image_debug_report.py /home/scratch.avice_vlsi/agur/SFNL/prtm/work_area ipo2000")
        sys.exit(1)
    
    wa_path = sys.argv[1]
    user_specified_ipo = sys.argv[2] if len(sys.argv) == 3 else None
    
    # Validate work area path
    if not os.path.exists(wa_path):
        print(f"[Error] Work area path does not exist: {wa_path}")
        sys.exit(1)
    
    print(f"[Info] Processing work area: {wa_path}")
    
    # Extract unit name
    unit_name = extract_unit_name(wa_path)
    print(f"[Info] Detected unit name: {unit_name}")
    
    # Extract IPO name from .prc file
    ipo_name = extract_ipo_name(wa_path, unit_name, user_specified_ipo)
    print(f"[Info] Selected IPO name: {ipo_name}")
    
    # Get images directory
    images_dir = get_images_directory(wa_path, unit_name, ipo_name)
    print(f"[Info] Looking for images in: {images_dir}")
    
    # Scan for images from all directories
    all_images = scan_all_images(wa_path, unit_name, ipo_name)
    
    # Count images by source
    image_counts = {}
    for source, img_path in all_images:
        image_counts[source] = image_counts.get(source, 0) + 1
    
    total_images = len(all_images)
    print(f"[Info] Found {total_images} total images")
    
    # Show image counts by source
    for source, count in image_counts.items():
        print(f"[Info]   {source}: {count} images")
    
    if all_images:
        # Show first few found images
        print("[Info] Sample images found:")
        for i, (source, img_path) in enumerate(all_images[:5]):
            print(f"  {i+1}. {os.path.basename(img_path)} (from {source})")
        if len(all_images) > 5:
            print(f"  ... and {len(all_images) - 5} more")
    
    # Categorize images
    categorized_images = categorize_images(all_images)
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{os.environ.get('USER', 'avice')}_image_report_{unit_name}_{timestamp}.html"
    
    # Generate HTML report
    success = generate_html_report(unit_name, images_dir, categorized_images, output_file)
    
    if success:
        print(f"[Success] Debug report generated successfully!")
        print(f"[Info] Open the report: {os.path.abspath(output_file)}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

