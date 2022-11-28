<div align="center">

# blokbot.io | OpenBlok

[![CI | Pylint](https://github.com/blokbot-io/OpenBlok/actions/workflows/pylint.yml/badge.svg)](https://github.com/blokbot-io/OpenBlok/actions/workflows/pylint.yml)
&nbsp;
[![CI | Installer Build](https://github.com/blokbot-io/OpenBlok/actions/workflows/build-installer.yml/badge.svg)](https://github.com/blokbot-io/OpenBlok/actions/workflows/build-installer.yml)
&nbsp;
[![CD | Release](https://github.com/blokbot-io/OpenBlok/actions/workflows/auto-release.yml/badge.svg)](https://github.com/blokbot-io/OpenBlok/actions/workflows/auto-release.yml)

</div>

## Table of Contents

- [blokbot.io | OpenBlok](#blokbotio--openblok)
  - [Table of Contents](#table-of-contents)
  - [Hardware Requirements](#hardware-requirements)
  - [Installation](#installation)
  - [Directory Structure](#directory-structure)
  - [Community and Contributing](#community-and-contributing)

OpenBlok is an open source Lego identification and sorting system using AI models developed by [blokbot.io](https://blokbot.io)

The identification system requires a specific camera setup that can be purchased from [blokbot.io](https://blokbot.io) or can be created by referencing our technical guide.

## Hardware Requirements

There are several AI models that provide flexibility to the configuration of OpenBlok. Please refer to our standards guide for more information. Additionally, you may purchase the desktop dev kit for a quick start.

A camera stream is required to use OpenBlok, if no input device is found, OpenBlok will download a sample video stream to use as a test. The following cameras have been tested and are known to work:

- [MOKOSE 4K HD USB](https://www.amazon.com/gp/product/B08FHBRKSK/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) with [Arducam 8-50mm C-Mount Zoom Lens](https://www.amazon.com/gp/product/B08PYMBX9T/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)

To achieve higher frame rates, the use of a graphics card or other AI model accelerator can be used.

## Installation

OpenBlok has been developed and deigned to run on *Ubuntu 22.04 LTS. It is recommended to run `apt-get update` and `apt-get upgrade` before installing OpenBlok.

For custom installation options, please refer to the [installation guide](docs/installer.md). Otherwise, you can install OpenBlok using the following command:

```bash
sudo wget -qO- openblok.blokbot.io | bash /dev/stdin
```

**\* Only tested using desktop version, PR welcome for minimum GUI installation version.**

## Directory Structure

``` bash
.
├── docs                # Documentation
└── bloks               # System Functions
    ├── modules         # Modules
    └── utils           # Supporting Utilities
├── display             # Visualization
├── peripherals         # Peripherals
└── modeled             # AI model implementation
    └── models          # AI model files
```

## Community and Contributing

OpenBlock is developed by [Blok Bot](https://blokbot.io/) and by users like you. We welcome both pull requests and issues on [GitHub](https://github.com/blokbot-io/OpenBlok). Bug fixes and new features are encouraged.

<div align="center">

<a target="_blank" href="https://discord.gg/nBpAGg69JD">![Discord Banner 2](https://discordapp.com/api/guilds/1017172382336696451/widget.png?style=banner2)</a>

</div>
