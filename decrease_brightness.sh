#!/bin/bash

# Replace with your monitor's device name
MONITOR="dev:/dev/i2c-3"

# Get current brightness
current=$(sudo ddcutil getvcp 10 | grep -oP 'current value\s*=\s*\K\d+')

# Decrease by 10, floor at 0
new=$((current - 5))
if [ $new -lt 0 ]; then
  new=0
fi

# Set new brightness
sudo ddcutil setvcp 10 $new

kdialog --title "Brightness" --passivepopup "$new%" 1