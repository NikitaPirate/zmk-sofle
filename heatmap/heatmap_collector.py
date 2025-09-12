#!/usr/bin/env python3
"""
ZMK Keyboard Heatmap Data Collector

Collects keypress statistics from ZMK firmware USB logging output
and saves aggregated data for heatmap visualization.
"""

import re
import json
import time
import serial
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import click

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZMKLogParser:
    """Parses ZMK USB logging output to extract keypress events."""
    
    # Regex pattern to match ZMK keypress events
    KEYPRESS_PATTERN = re.compile(
        r'\[(\d+:\d+:\d+\.\d+),\d+\] <dbg> zmk: zmk_physical_layouts_kscan_process_msgq: '
        r'Row: (\d+), col: (\d+), position: (\d+), pressed: (true|false)'
    )
    
    def __init__(self):
        self.keypress_stats = {}
        self.session_start = datetime.now()
    
    def parse_line(self, line: str) -> Optional[Tuple[int, int, int, bool]]:
        """
        Parse a single log line for keypress events.
        
        Returns:
            Tuple of (row, col, position, pressed) or None if no match
        """
        match = self.KEYPRESS_PATTERN.search(line)
        if match:
            timestamp, row, col, position, pressed = match.groups()
            return (
                int(row),
                int(col), 
                int(position),
                pressed == 'true'
            )
        return None
    
    def update_stats(self, row: int, col: int, position: int, pressed: bool):
        """Update keypress statistics."""
        if pressed:  # Only count key presses, not releases
            key = f"pos_{position}"
            if key not in self.keypress_stats:
                self.keypress_stats[key] = {
                    'count': 0,
                    'row': row,
                    'col': col,
                    'position': position,
                    'first_press': datetime.now().isoformat(),
                    'last_press': datetime.now().isoformat()
                }
            
            self.keypress_stats[key]['count'] += 1
            self.keypress_stats[key]['last_press'] = datetime.now().isoformat()
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        return {
            'session_start': self.session_start.isoformat(),
            'session_duration_minutes': (datetime.now() - self.session_start).total_seconds() / 60,
            'total_keypresses': sum(stats['count'] for stats in self.keypress_stats.values()),
            'unique_keys': len(self.keypress_stats),
            'keypress_data': self.keypress_stats
        }

class SerialCollector:
    """Collects data from ZMK USB logging serial device."""
    
    def __init__(self, device: str, baudrate: int = 115200):
        self.device = device
        self.baudrate = baudrate
        self.parser = ZMKLogParser()
        self.running = False
    
    def connect(self) -> bool:
        """Connect to serial device."""
        try:
            self.serial = serial.Serial(self.device, self.baudrate, timeout=1)
            logger.info(f"Connected to {self.device} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.device}: {e}")
            return False
    
    def collect(self, output_file: str, duration: Optional[int] = None):
        """
        Collect keypress data from serial device.
        
        Args:
            output_file: Path to save collected data
            duration: Collection duration in seconds (None for infinite)
        """
        if not self.connect():
            return
        
        self.running = True
        start_time = time.time()
        
        logger.info("Starting data collection. Press Ctrl+C to stop.")
        logger.info("Start typing on your keyboard to generate data...")
        
        try:
            while self.running:
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    logger.info(f"Collection time limit of {duration}s reached")
                    break
                
                # Read line from serial
                try:
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        # Parse for keypress events
                        result = self.parser.parse_line(line)
                        if result:
                            row, col, position, pressed = result
                            self.parser.update_stats(row, col, position, pressed)
                            if pressed:
                                logger.debug(f"Key press: pos={position} row={row} col={col}")
                
                except serial.SerialTimeoutException:
                    continue
                except UnicodeDecodeError:
                    continue
        
        except KeyboardInterrupt:
            logger.info("Collection stopped by user")
        
        finally:
            self.running = False
            self.serial.close()
            
            # Save collected data
            stats = self.parser.get_stats()
            self.save_data(stats, output_file)
            
            # Print summary
            logger.info(f"Collection complete!")
            logger.info(f"Total keypresses: {stats['total_keypresses']}")
            logger.info(f"Unique keys used: {stats['unique_keys']}")
            logger.info(f"Session duration: {stats['session_duration_minutes']:.1f} minutes")
            logger.info(f"Data saved to: {output_file}")
    
    def save_data(self, stats: Dict, output_file: str):
        """Save statistics to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)

@click.command()
@click.option('--device', '-d', default='/dev/ttyACM0', 
              help='Serial device path (e.g., /dev/ttyACM0 on Linux, COM3 on Windows)')
@click.option('--output', '-o', default='data/keypress_data.json',
              help='Output file path for collected data')
@click.option('--duration', '-t', type=int, default=None,
              help='Collection duration in seconds (default: infinite)')
@click.option('--baudrate', '-b', default=115200,
              help='Serial baudrate (default: 115200)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
def main(device, output, duration, baudrate, verbose):
    """
    ZMK Keyboard Heatmap Data Collector
    
    Collects keypress statistics from ZMK firmware USB logging output.
    Make sure your keyboard firmware is built with USB logging enabled.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if device exists
    if not Path(device).exists():
        logger.error(f"Device {device} not found. Make sure:")
        logger.error("1. Your keyboard is connected")
        logger.error("2. USB logging is enabled in firmware")
        logger.error("3. The device path is correct")
        return
    
    collector = SerialCollector(device, baudrate)
    collector.collect(output, duration)

if __name__ == '__main__':
    main()