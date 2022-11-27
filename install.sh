#!/bin/bash

# Installer for OpenBlok

# ---------------------------------------------------------------------------- #
#                                 Dependencies                                 #
# ---------------------------------------------------------------------------- #

# -------------------------------- Python 3.11 ------------------------------- #
pytohn_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[0:2])))')
if [ "$pytohn_version" != "3.11" ]; then
    sudo apt install software-properties-common -y
    yes '' | sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get --reinstall install python3.11 -y
else
    echo "Python 3.11 already installed"
fi
