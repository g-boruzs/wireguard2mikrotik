#!/bin/bash
# This script installs wireguard2mikrotik.py
#

if [[ ! -f  "/etc/wireguard/wg0.conf" ]]; then
    echo "Install wireguard first!"
    exit
fi

# Function to check if a package is installed on Debian-based systems
function is_package_installed_deb () {
    dpkg -s "$1" >/dev/null 2>&1
}

# Function to check if a package is installed on Red Hat-based systems
function is_package_installed_rpm () {
    rpm -q "$1" >/dev/null 2>&1
}

if is_package_installed_deb "python3"; then
    echo "python3 is already installed."
else
    echo "Installing python3..."
    if is_package_installed_rpm "yum"; then
        yum install -y python3
    elif is_package_installed_rpm "dnf"; then
        dnf install -y python3
    elif is_package_installed_deb "apt-get"; then
        apt-get update
        apt-get install -y python3
    else
        echo "Error: Package manager not found. Please install python3 manually."
        exit 1
    fi
fi

# Install python dependencies with pip
echo "Installing python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install argparse configparser urllib3 requests

# Download wireguard2mikrotik.py from GitHub
echo "Downloading wireguard2mikrotik.py..."
mkdir /opt/wireguard2mikrotik && wget https://github.com/g-boruzs/wireguard2mikrotik/raw/main/wireguard2mikrotik.py -O /opt/wireguard2mikrotik/wireguard2mikrotik.py

# Create systemd service files
cat <<'EOF' >> /etc/systemd/system/wireguard2mikrotik.path
[Unit]
Description=Watch /etc/wireguard/wg0.conf for changes

[Path]
PathModified=/etc/wireguard/wg0.conf

[Install]
WantedBy=multi-user.target
EOF

cat <<'EOF' >> /etc/systemd/system/wireguard2mikrotik.service
[Unit]
Description=Sync WireGuard to Mikrotik
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/python3 /opt/wireguard2mikrotik/wireguard2mikrotik.py

[Install]
RequiredBy=wgui.path
EOF

systemctl daemon-reload && systemctl enable --now wireguard2mikrotik.path && systemctl enable --now wireguard2mikrotik.service

echo "Installation completed!"
