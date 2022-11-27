<div align="center">

# blokbot.io | OpenBlok

[![Code Quality](https://github.com/blokbot-io/OpenBlok/actions/workflows/pylint.yml/badge.svg)](https://github.com/blokbot-io/OpenBlok/actions/workflows/pylint.yml)
&nbsp;
[![CI | Installer Build](https://github.com/blokbot-io/OpenBlok/actions/workflows/build-installer.yml/badge.svg)](https://github.com/blokbot-io/OpenBlok/actions/workflows/build-installer.yml)
</div>

## Table of Contents

- [blokbot.io | OpenBlok](#blokbotio--openblok)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Directory Structure](#directory-structure)
  - [Community and Contributing](#community-and-contributing)

OpenBlok is an open source Lego identification and sorting system using AI models developed by [blokbot.io](https://blokbot.io)

The identification system requires a specific camera setup that can be purchased from [blokbot.io](https://blokbot.io) or can be created by referencing our technical guide.

## Installation

OpenBlok has been developed and deigned to run on Ubuntu 22.04 LTS.

For custom installation options, please refer to the [installation guide](docs/installer.md). Otherwise, you can install OpenBlok using the following command:

```bash
sudo wget -qO- openblok.blokbot.io | bash /dev/stdin
```

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

<a target="_blank" href="https://discord.gg/jftVESxMPY">![Discord Banner 2](https://discordapp.com/api/guilds/1017172382336696451/widget.png?style=banner2)</a>

</div>
