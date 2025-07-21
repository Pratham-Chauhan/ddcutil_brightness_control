#!/bin/bash

# Replace with your monitor's device name
MONITOR="dev:/dev/i2c-3"

# Get current brightness
current=$(sudo ddcutil getvcp 10 | grep -oP 'current value\s*=\s*\K\d+')

# Increase by 10, cap at 100
new=$((current + 10))
if [ $new -gt 100 ]; then
	new=100
fi

# Set new brightness
sudo ddcutil setvcp 10 $new

kdialog --title "Brightness" --passivepopup "$new%" 1

