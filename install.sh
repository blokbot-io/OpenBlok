#!/bin/bash

# Installer for OpenBlok

# ---------------------------------------------------------------------------- #
#                                   Defaults                                   #
# ---------------------------------------------------------------------------- #
URL="blokbot.io"
DEBUG=false

# ---------------------------------------------------------------------------- #
#                                 Dependencies                                 #
# ---------------------------------------------------------------------------- #

# -------------------------------- Python 3.11 ------------------------------- #
pytohn_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[0:2])))')
if [ "$pytohn_version" != "3.10" ]; then
    sudo apt install software-properties-common -y
    yes '' | sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get install python3.10 -y
else
    echo "Python 3.10 already installed"
fi

# ----------------------------------- unzip ---------------------------------- #
REQUIRED_PKG="unzip"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install unzip -y
else
    echo "unzip already installed, skipping..."
fi

# ------------------------------------ jq ------------------------------------ #
REQUIRED_PKG="jq"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install jq -y
else
    echo "jq already installed, skipping..."
fi


# ---------------------------------------------------------------------------- #
#                         Grab Latest OpenBlok Release                         #
# ---------------------------------------------------------------------------- #
cd /opt/
VERSION=$(wget -q -O- https://api.github.com/repos/blokbot-io/OpenBlok/releases/latest | jq -r '.name')
wget https://github.com/blokbot-io/OpenBlok/archive/refs/tags/${VERSION}.zip

unzip -qq ${VERSION}.zip -d /opt/OpenBlok
mv /opt/OpenBlok/OpenBlok-${VERSION}/* /opt/OpenBlok/
# ---------------------------------------------------------------------------- #
#                                  Environment                                 #
# ---------------------------------------------------------------------------- #

# ----------------------------- Setup Enviroment ----------------------------- #
REQUIRED_PKG="python3.10-venv"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install python3.10-venv -y
else
    echo "python3.10 -venv already installed, skipping..."
fi

if [ ! -d "/opt/OpenBlok/env" ]; then
    python3.10 -m venv /opt/OpenBlok/env
fi

. /opt/OpenBlok/env/bin/activate

# ------------------------ Install Python Dependencies ----------------------- #
cd /opt/OpenBlok/
pip install --no-input -U --upgrade-strategy only-if-needed -r /opt/OpenBlok/requirements.txt


# ---------------------------------------------------------------------------- #
#                                 System Files                                 #
# ---------------------------------------------------------------------------- #

# -------------------------------- system.json ------------------------------- #
if ! [ -f "/opt/OpenBlok/system.json" ]; then
    sudo touch /opt/OpenBlok/system.json
    serial_uuid=$(cat /proc/sys/kernel/random/uuid)
    echo '{
        "serial": "'$serial_uuid'",
        "timezone": "UTC",
        "url": "'$URL'",
        "version": "'$VERSION'",
        "debug": "'$DEBUG'",
        "models": {
            "location": {
                "version": 0
            },
            "e2e": {
                "version": 0
            }
        }
    }' > /opt/OpenBlok/system.json
fi

# ---------------------------------------------------------------------------- #
#                                 Housekeeping                                 #
# ---------------------------------------------------------------------------- #

# -------------------------------- Remove ZIPs ------------------------------- #
rm -rf /opt/${VERSION}.zip
rm -rf /opt/OpenBlok/OpenBlok-${VERSION}


# ---------------------------------------------------------------------------- #
echo "OpenBlok installed successfully"
