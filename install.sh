#!/bin/bash

# Update package list and install prerequisites
sudo apt-get update
sudo apt-get install -y curl python3 python3-pip python3-venv

# Create a virtual environment
python3 -m venv /opt/ports_checker/venv

# Activate the virtual environment
source /opt/ports_checker/venv/bin/activate

# Install required Python packages
pip install --upgrade pip
pip install fastapi uvicorn

# Copy the application files (adjust paths as needed)
# Assuming the script is in the same directory as the source code
sudo mkdir -p /opt/ports_checker
sudo cp -r . /opt/ports_checker/

# Create a systemd service file
SERVICE_FILE=/etc/systemd/system/ports_checker.service

sudo tee $SERVICE_FILE > /dev/null <<EOL
[Unit]
Description=FastAPI service for ports_checker
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/ports_checker
ExecStart=/opt/ports_checker/venv/bin/uvicorn ports_checker:app --host 127.0.0.1 --port 54172
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl start ports_checker
sudo systemctl enable ports_checker

echo "Ports Checker application is now installed and running."
