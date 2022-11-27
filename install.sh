#!/bin/bash

# Installer for OpenBlok

# ---------------------------------------------------------------------------- #
#                                 Dependencies                                 #
# ---------------------------------------------------------------------------- #

# -------------------------------- Python 3.11 ------------------------------- #
pytohn_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[0:2])))')
if [ "$pytohn_version" != "3.10" ]; then
    sudo apt install software-properties-common -y
    yes '' | sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get --reinstall install python3.10.8 -y
else
    echo "Python 3.11 already installed"
fi

# ----------------------------- Setup Enviroment ----------------------------- #
REQUIRED_PKG="python3.10.8 -venv"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG..."
    sudo apt-get install python3.10.8-venv -y
else
    echo "python3.10.8-venv already installed, skipping..."
fi

if [ ! -d "/opt/blok/env" ]; then
    python3.10.8 -m venv /opt/OpenBlok/env
fi

. /opt/OpenBlok/env/bin/activate
