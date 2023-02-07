#!/bin/bash

# Installer for OpenBlok, for more information see https://github.com/blokbot-io/OpenBlok/blob/master/docs/installer.md

# ---------------------------------------------------------------------------- #
#                                     Help                                     #
# ---------------------------------------------------------------------------- #
Help()
{
    # Display Help
    echo "OpenBlok installation script."
    echo
    echo "h     Display this help"
    echo "u     Set custom URL for OpenBlok"
    echo "d     Enable debug mode"
}

# ---------------------------------------------------------------------------- #
#                                   Defaults                                   #
# ---------------------------------------------------------------------------- #
URL="blokbot.io"
DEBUG=false

# -------------------------------- Verify Root ------------------------------- #
if [ "$EUID" -ne 0 ]
  then echo "Please run as root with sudo."
  exit
fi

# -------------------------------- Verify User ------------------------------- #
if ! id blok &>/dev/null; then
    sudo adduser --disabled-password --gecos "" blok
    sudo usermod -aG sudo blok
fi

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


# --------------------------------- v4l-utils -------------------------------- #
REQUIRED_PKG="v4l-utils"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install v4l-utils -y
else
    echo "v4l-utils already installed, skipping..."
fi

# ---------------------------------- ffmpeg ---------------------------------- #
REQUIRED_PKG="ffmpeg"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install ffmpeg -y
else
    echo "ffmpeg already installed, skipping..."
fi

# ---------------------------------- libsm6 ---------------------------------- #
REQUIRED_PKG="libsm6"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install libsm6 -y
else
    echo "libsm6 already installed, skipping..."
fi

# --------------------------------- libxext6 --------------------------------- #
REQUIRED_PKG="libxext6"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install libxext6 -y
else
    echo "libxext6 already installed, skipping..."
fi

# ----------------------------------- Redis ---------------------------------- #
REQUIRED_PKG="redis"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install redis -y
else
    echo "redis already installed, skipping..."
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
        "debug": '$DEBUG',
        "models": {
            "location": {
                "version": null
            },
            "e2e": {
                "version": null
            }
        },
        "storage": {
            "local": {
                "path": "/opt/OpenBlok/images",
                "maxSizeGB": 10,
                "enabled": true
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "password": null
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

# --------------------------------- Permissions ------------------------------- #
chmod a+w /opt/OpenBlok/system.json
chmod a+w /opt/OpenBlok/modeled/models

# ---------------------------------------------------------------------------- #
echo "OpenBlok installed successfully"
