#!/usr/bin/env python3
"""
ZMK Heatmap Demo Script

Demonstrates the complete heatmap workflow with example data.
"""

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

def generate_demo_data(output_path: str, num_keypresses: int = 1000):
    """
    Generate demo keypress data for testing visualization.
    
    Args:
        output_path: Path to save demo data
        num_keypresses: Number of simulated keypresses
    """
    print(f"Generating demo data with {num_keypresses} keypresses...")
    
    # Sofle keyboard has 58 keys (positions 0-57)
    total_positions = 58
    
    # Create weighted distribution (some keys more likely than others)
    # Home row keys (ASDF, JKL;) should be more frequent
    home_row_positions = [12, 13, 14, 15, 41, 42, 43, 44]  # Approximate home row
    vowel_positions = [12, 20, 16, 39, 37]  # A, E, I, O, U positions (approximate)
    common_positions = home_row_positions + vowel_positions + [44, 32]  # Space, Enter
    
    weights = []
    for i in range(total_positions):
        if i in common_positions:
            weights.append(5.0)  # High frequency keys
        elif i < 50:  # Regular letter keys
            weights.append(1.0)
        else:  # Function/modifier keys
            weights.append(0.2)
    
    # Generate keypress events
    keypress_stats = {}
    session_start = datetime.now() - timedelta(minutes=30)
    
    for _ in range(num_keypresses):
        # Choose random position based on weights
        position = random.choices(range(total_positions), weights=weights)[0]
        
        # Calculate matrix position (approximate for demo)
        row = position // 12
        col = position % 12
        
        key = f"pos_{position}"
        
        if key not in keypress_stats:
            keypress_stats[key] = {
                'count': 0,
                'row': row,
                'col': col,
                'position': position,
                'first_press': session_start.isoformat(),
                'last_press': session_start.isoformat()
            }
        
        keypress_stats[key]['count'] += 1
        keypress_stats[key]['last_press'] = (session_start + timedelta(
            seconds=random.randint(0, 1800))).isoformat()
    
    # Create complete data structure
    demo_data = {
        'session_start': session_start.isoformat(),
        'session_duration_minutes': 30.0,
        'total_keypresses': num_keypresses,
        'unique_keys': len(keypress_stats),
        'keypress_data': keypress_stats
    }
    
    # Save data
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    print(f"Demo data saved to: {output_file}")
    return output_file

def run_demo():
    """Run complete demo workflow."""
    print("=== ZMK Keyboard Heatmap Demo ===\n")
    
    # Step 1: Generate demo data
    demo_data_path = "data/demo_keypress_data.json"
    generate_demo_data(demo_data_path, 1500)
    print()
    
    # Step 2: Create heatmap visualization
    print("Creating heatmap visualization...")
    from heatmap_visualizer import HeatmapVisualizer
    
    try:
        config_path = "config/eyelash_sofle_layout.json"
        if not Path(config_path).exists():
            print(f"Layout config not found at {config_path}")
            print("Run: python keymap_parser.py ../config/eyelash_sofle.keymap")
            return
        
        visualizer = HeatmapVisualizer(config_path)
        output_path = "data/heatmaps/demo_heatmap.png"
        
        visualizer.create_heatmap(
            demo_data_path, 
            output_path,
            title="Demo Keyboard Heatmap - Simulated Data"
        )
        
        print(f"Demo heatmap created: {output_path}")
        print()
        
        # Step 3: Show statistics
        with open(demo_data_path, 'r') as f:
            data = json.load(f)
        
        print("=== Demo Statistics ===")
        print(f"Total keypresses: {data['total_keypresses']}")
        print(f"Unique keys used: {data['unique_keys']}")
        print(f"Session duration: {data['session_duration_minutes']} minutes")
        
        # Find top 5 most used keys
        top_keys = sorted(
            data['keypress_data'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:5]
        
        print("\nTop 5 most used keys:")
        for i, (pos_key, stats) in enumerate(top_keys, 1):
            print(f"  {i}. Position {stats['position']}: {stats['count']} presses")
        
        print("\n=== Demo Complete ===")
        print("To collect real data:")
        print("1. Build firmware with USB logging (use build_heatmap.yaml)")
        print("2. Flash the firmware to your keyboard")
        print("3. Run: python heatmap_collector.py --device /dev/ttyACM0")
        print("4. Type on your keyboard to generate data")
        print("5. Run: python heatmap_visualizer.py --data your_data.json")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"Error creating visualization: {e}")

if __name__ == '__main__':
    run_demo()