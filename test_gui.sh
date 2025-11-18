#!/bin/bash
# GUI Testing Script for Omnix Gaming Companion
# This script sets up a virtual display and runs the application

set -e

echo "========================================="
echo "Omnix Gaming Companion - GUI Test Runner"
echo "========================================="
echo ""

# Set up virtual display
export DISPLAY=:99
echo "Starting virtual display on :99..."

# Kill any existing Xvfb on display :99
pkill -f "Xvfb :99" 2>/dev/null || true

# Start Xvfb in background
Xvfb :99 -screen 0 1920x1080x24 &
XVFB_PID=$!
echo "Xvfb started (PID: $XVFB_PID)"

# Wait for Xvfb to be ready
sleep 2

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up..."
    kill $XVFB_PID 2>/dev/null || true
    echo "Virtual display stopped"
}

trap cleanup EXIT

echo ""
echo "Virtual display ready!"
echo "Display: $DISPLAY"
echo "Resolution: 1920x1080x24"
echo ""
echo "Starting Omnix Gaming Companion..."
echo "========================================="
echo ""

# Run the application
cd /home/user/Omnix-All-knowing-gaming-companion
python main.py

# The cleanup trap will run when the script exits
