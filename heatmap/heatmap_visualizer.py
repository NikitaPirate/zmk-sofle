#!/usr/bin/env python3
"""
ZMK Keyboard Heatmap Visualizer

Creates heatmap visualizations from collected keypress data.
Supports multiple output formats and keyboard layouts.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import click

class HeatmapVisualizer:
    """Creates heatmap visualizations from keypress statistics."""
    
    def __init__(self, layout_config_path: str):
        """
        Initialize visualizer with keyboard layout configuration.
        
        Args:
            layout_config_path: Path to layout configuration JSON file
        """
        with open(layout_config_path, 'r') as f:
            self.config = json.load(f)
        
        self.layout = self.config['layout']
        self.positions = self.layout['positions']
    
    def load_data(self, data_path: str) -> Dict:
        """Load keypress data from JSON file."""
        with open(data_path, 'r') as f:
            return json.load(f)
    
    def create_heatmap(self, data_path: str, output_path: str, 
                      colormap: str = 'YlOrRd', title: Optional[str] = None):
        """
        Create a heatmap visualization from keypress data.
        
        Args:
            data_path: Path to keypress data JSON file
            output_path: Path to save the heatmap image
            colormap: Matplotlib colormap name
            title: Custom title for the heatmap
        """
        # Load data
        data = self.load_data(data_path)
        keypress_data = data['keypress_data']
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Determine grid size
        max_row = max(pos['row'] for pos in self.positions.values()) + 1
        max_col = max(pos['col'] for pos in self.positions.values()) + 1
        
        # Create heat matrix
        heat_matrix = np.zeros((max_row, max_col))
        max_count = 0
        
        # Fill heat matrix with keypress counts
        for pos_key, stats in keypress_data.items():
            position = stats['position']
            count = stats['count']
            
            if str(position) in self.positions:
                pos_info = self.positions[str(position)]
                row, col = pos_info['row'], pos_info['col']
                heat_matrix[row, col] = count
                max_count = max(max_count, count)
        
        # Normalize values for better visualization
        if max_count > 0:
            heat_matrix = heat_matrix / max_count
        
        # Create custom colormap
        colors = ['#000033', '#000055', '#000088', '#0000BB', '#0033FF', 
                 '#3366FF', '#6699FF', '#99CCFF', '#CCDDFF', '#FFFFFF',
                 '#FFCCCC', '#FF9999', '#FF6666', '#FF3333', '#FF0000']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('keyboard_heat', colors, N=n_bins)
        
        # Draw keyboard layout
        self._draw_keyboard_layout(ax, heat_matrix, cmap, keypress_data)
        
        # Set title
        if title is None:
            total_presses = data['total_keypresses']
            duration = data['session_duration_minutes']
            title = f'Keyboard Heatmap - {total_presses} keypresses in {duration:.1f} minutes'
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Add colorbar
        cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap), ax=ax, 
                           shrink=0.8, aspect=30)
        cbar.set_label('Keypress Intensity', fontsize=12)
        
        # Remove axis
        ax.set_xlim(0, max_col)
        ax.set_ylim(0, max_row)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add statistics text
        stats_text = self._generate_stats_text(data)
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Save figure
        plt.tight_layout()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Heatmap saved to: {output_file}")
    
    def _draw_keyboard_layout(self, ax, heat_matrix, cmap, keypress_data):
        """Draw the keyboard layout with heatmap colors."""
        key_size = 0.8
        key_spacing = 1.0
        
        for pos_str, pos_info in self.positions.items():
            row, col = pos_info['row'], pos_info['col']
            
            # Get heat value
            heat_value = heat_matrix[row, col] if heat_matrix[row, col] > 0 else 0
            
            # Calculate position (flip row for correct orientation)
            x = col * key_spacing
            y = (len(heat_matrix) - row - 1) * key_spacing
            
            # Choose color based on heat value
            if heat_value > 0:
                color = cmap(heat_value)
            else:
                color = '#f0f0f0'  # Light gray for unused keys
            
            # Draw key rectangle
            rect = patches.Rectangle((x, y), key_size, key_size,
                                   linewidth=1, edgecolor='black',
                                   facecolor=color)
            ax.add_patch(rect)
            
            # Add count text if there are keypresses
            pos_key = f"pos_{pos_str}"
            if pos_key in keypress_data:
                count = keypress_data[pos_key]['count']
                if count > 0:
                    ax.text(x + key_size/2, y + key_size/2, str(count),
                           ha='center', va='center', fontsize=8, fontweight='bold',
                           color='white' if heat_value > 0.5 else 'black')
    
    def _generate_stats_text(self, data: Dict) -> str:
        """Generate statistics text for the heatmap."""
        total_presses = data['total_keypresses']
        unique_keys = data['unique_keys']
        duration = data['session_duration_minutes']
        
        # Find most used key
        most_used_key = None
        max_count = 0
        for pos_key, stats in data['keypress_data'].items():
            if stats['count'] > max_count:
                max_count = stats['count']
                most_used_key = f"Position {stats['position']}"
        
        # Calculate typing rate
        typing_rate = total_presses / duration if duration > 0 else 0
        
        stats = [
            f"Total Keypresses: {total_presses}",
            f"Unique Keys Used: {unique_keys}",
            f"Session Duration: {duration:.1f} min",
            f"Average Rate: {typing_rate:.1f} keys/min",
            f"Most Used Key: {most_used_key} ({max_count} times)"
        ]
        
        return '\n'.join(stats)
    
    def create_layer_heatmap(self, data_path: str, output_dir: str, layer_name: str = 'layer0'):
        """Create heatmap for a specific layer."""
        # This is a placeholder for layer-specific heatmaps
        # Would require enhanced data collection to track layer usage
        output_path = f"{output_dir}/heatmap_{layer_name}.png"
        self.create_heatmap(data_path, output_path, title=f"Heatmap - {layer_name.upper()}")
    
    def create_time_series_heatmap(self, data_path: str, output_dir: str):
        """Create time-based heatmap analysis."""
        # Placeholder for future enhancement
        # Would show heatmap changes over time periods
        pass

def generate_layout_config(keymap_path: str, output_path: str):
    """Generate layout configuration from keymap file."""
    from keymap_parser import KeymapParser
    
    parser = KeymapParser(keymap_path)
    parser.parse()
    parser.save_layout_config(output_path)
    print(f"Layout configuration generated: {output_path}")

@click.command()
@click.option('--data', '-d', required=True,
              help='Path to keypress data JSON file')
@click.option('--output', '-o', default='data/heatmaps/heatmap.png',
              help='Output path for heatmap image')
@click.option('--config', '-c', default='config/eyelash_sofle_layout.json',
              help='Path to keyboard layout configuration')
@click.option('--colormap', default='YlOrRd',
              help='Matplotlib colormap (YlOrRd, viridis, plasma, etc.)')
@click.option('--title', default=None,
              help='Custom title for the heatmap')
@click.option('--generate-config', is_flag=True,
              help='Generate layout config from keymap file')
@click.option('--keymap', default='../config/eyelash_sofle.keymap',
              help='Path to keymap file (for --generate-config)')
def main(data, output, config, colormap, title, generate_config, keymap):
    """
    ZMK Keyboard Heatmap Visualizer
    
    Creates beautiful heatmap visualizations from collected keypress data.
    """
    # Generate layout config if requested
    if generate_config:
        generate_layout_config(keymap, config)
        return
    
    # Check if config exists
    if not Path(config).exists():
        print(f"Layout config not found: {config}")
        print("Generate it first with: --generate-config")
        return
    
    # Check if data exists
    if not Path(data).exists():
        print(f"Data file not found: {data}")
        print("Collect data first with heatmap_collector.py")
        return
    
    # Create visualizer and generate heatmap
    visualizer = HeatmapVisualizer(config)
    visualizer.create_heatmap(data, output, colormap, title)

if __name__ == '__main__':
    main()