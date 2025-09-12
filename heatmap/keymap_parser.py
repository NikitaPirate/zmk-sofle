#!/usr/bin/env python3
"""
ZMK Keymap Parser

Extracts layout information from ZMK .keymap files to understand
the physical positioning of keys for heatmap visualization.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class KeymapParser:
    """Parser for ZMK .keymap files to extract layout information."""
    
    def __init__(self, keymap_path: str):
        self.keymap_path = Path(keymap_path)
        self.layout_info = None
        self.layers = {}
    
    def parse(self) -> Dict:
        """
        Parse the keymap file and extract layout information.
        
        Returns:
            Dictionary containing layout and layer information
        """
        if not self.keymap_path.exists():
            raise FileNotFoundError(f"Keymap file not found: {self.keymap_path}")
        
        content = self.keymap_path.read_text()
        
        # Extract layers
        self.layers = self._extract_layers(content)
        
        # Generate layout info based on Sofle keyboard
        self.layout_info = self._generate_sofle_layout()
        
        return {
            'layout': self.layout_info,
            'layers': self.layers,
            'total_keys': len(self.layout_info['positions'])
        }
    
    def _extract_layers(self, content: str) -> Dict[str, List[str]]:
        """Extract layer definitions from keymap content."""
        layers = {}
        
        # Pattern to match layer definitions
        layer_pattern = re.compile(
            r'(\w+)\s*{\s*bindings\s*=\s*<([^>]+)>', 
            re.MULTILINE | re.DOTALL
        )
        
        for match in layer_pattern.finditer(content):
            layer_name = match.group(1)
            bindings_content = match.group(2)
            
            # Extract individual bindings
            bindings = self._parse_bindings(bindings_content)
            layers[layer_name] = bindings
        
        return layers
    
    def _parse_bindings(self, bindings_content: str) -> List[str]:
        """Parse bindings from layer content."""
        # Clean up the content
        cleaned = re.sub(r'//.*$', '', bindings_content, flags=re.MULTILINE)  # Remove comments
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
        
        # Split by ampersand to get individual bindings
        bindings = []
        parts = cleaned.split('&')
        
        for part in parts:
            part = part.strip()
            if part:
                # Take the first word as the binding
                binding = '&' + part.split()[0] if part.split() else ''
                if binding != '&':
                    bindings.append(binding)
        
        return bindings
    
    def _generate_sofle_layout(self) -> Dict:
        """
        Generate layout information for Sofle keyboard.
        
        Sofle is a 6x4 + 5 thumb keys split keyboard (58 keys total).
        """
        layout = {
            'name': 'Sofle',
            'type': 'split',
            'rows': 5,
            'cols_per_half': 6,
            'total_keys': 58,
            'positions': {}
        }
        
        # Define physical positions for Sofle layout
        # Left half (positions 0-28)
        left_positions = [
            # Row 0 (top)
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
            # Row 1
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
            # Row 2  
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
            # Row 3
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
            # Row 4 (thumb cluster)
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)
        ]
        
        # Right half (positions 29-57)
        right_positions = [
            # Row 0 (top)
            (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12),
            # Row 1
            (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12),
            # Row 2
            (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (2, 12),
            # Row 3
            (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12),
            # Row 4 (thumb cluster)
            (4, 8), (4, 9), (4, 10), (4, 11), (4, 12)
        ]
        
        # Combine positions
        all_positions = left_positions + right_positions
        
        # Create position mapping
        for i, (row, col) in enumerate(all_positions):
            layout['positions'][i] = {
                'row': row,
                'col': col,
                'side': 'left' if i < 29 else 'right',
                'physical_row': row,
                'physical_col': col
            }
        
        return layout
    
    def save_layout_config(self, output_path: str):
        """Save parsed layout to configuration file."""
        if not self.layout_info:
            raise ValueError("Layout not parsed yet. Call parse() first.")
        
        config = {
            'layout': self.layout_info,
            'layers': self.layers,
            'metadata': {
                'source_file': str(self.keymap_path),
                'keyboard': 'eyelash_sofle',
                'total_keys': len(self.layout_info['positions'])
            }
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)

def main():
    """Example usage of KeymapParser."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python keymap_parser.py <keymap_file>")
        sys.exit(1)
    
    keymap_file = sys.argv[1]
    parser = KeymapParser(keymap_file)
    
    try:
        layout_data = parser.parse()
        print(f"Parsed layout for {layout_data['layout']['name']}")
        print(f"Total keys: {layout_data['total_keys']}")
        print(f"Layers found: {list(layout_data['layers'].keys())}")
        
        # Save to config
        parser.save_layout_config('config/eyelash_sofle_layout.json')
        print("Layout saved to config/eyelash_sofle_layout.json")
        
    except Exception as e:
        print(f"Error parsing keymap: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()