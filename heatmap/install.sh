#!/bin/bash
# ZMK Heatmap Installation Script

echo "=== ZMK Keyboard Heatmap System Installation ==="
echo

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or newer."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Check pip
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install pip."
    exit 1
fi

# Install requirements
echo "📦 Installing Python packages..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo "❌ Failed to install packages. Try installing manually:"
    echo "   pip install pyserial matplotlib numpy plotly click"
    exit 1
fi

echo "✓ Packages installed successfully"

# Generate layout configuration
echo "🗺️  Generating keyboard layout configuration..."
python3 keymap_parser.py ../config/eyelash_sofle.keymap

if [ $? -ne 0 ]; then
    echo "⚠️  Layout config generation failed, but demo will still work"
fi

# Create data directories
mkdir -p data/heatmaps
echo "✓ Created data directories"

# Run demo
echo
echo "🚀 Running demo..."
python3 demo.py

if [ $? -eq 0 ]; then
    echo
    echo "✅ Installation complete!"
    echo
    echo "Next steps:"
    echo "1. Copy build_heatmap.yaml to ../build.yaml (optional)"
    echo "2. Build firmware with USB logging"
    echo "3. Flash left half of keyboard" 
    echo "4. Run: python3 heatmap_collector.py --device /dev/ttyACM0"
    echo "5. Type on keyboard to generate data"
    echo "6. Run: python3 heatmap_visualizer.py --data your_data.json"
    echo
else
    echo "❌ Demo failed. Check the error messages above."
    exit 1
fi