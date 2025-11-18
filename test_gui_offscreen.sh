#!/bin/bash
# GUI Testing Script for Omnix Gaming Companion (Offscreen Mode)
# This script uses Qt's offscreen platform for headless GUI testing

set -e

echo "========================================="
echo "Omnix Gaming Companion - GUI Test Runner"
echo "         (Offscreen Platform)           "
echo "========================================="
echo ""

# Set up offscreen rendering
export QT_QPA_PLATFORM=offscreen

# Optional: Suppress Qt debug messages
export QT_LOGGING_RULES='*.debug=false;qt.qpa.*=false'

echo "Platform: Offscreen (headless)"
echo "Working directory: $(pwd)"
echo ""
echo "Starting Omnix Gaming Companion..."
echo "========================================="
echo ""

# Run the application
cd /home/user/Omnix-All-knowing-gaming-companion
python main.py

echo ""
echo "========================================="
echo "Application exited"
echo "========================================="
