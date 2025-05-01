#!/bin/bash

# Update and install Mosquitto and clients
sudo apt update
sudo apt install -y mosquitto mosquitto-clients net-tools

# Enable Mosquitto to start on boot
sudo systemctl enable mosquitto

# Modify Mosquitto configuration to allow external connections
CONF_FILE="/etc/mosquitto/mosquitto.conf"
if ! grep -q "listener 1883" "$CONF_FILE"; then
    echo -e "\nlistener 1883\nbind_address 0.0.0.0" | sudo tee -a "$CONF_FILE"
fi

# Restart Mosquitto to apply changes
sudo systemctl restart mosquitto

# Display WSL IP
WSL_IP=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
echo "WSL IP Address: $WSL_IP"
echo "Use this IP in the Windows script for port forwarding."