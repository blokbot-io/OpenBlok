# Design Flow

OpenBlok has been designed to operate in a modular fashion, the flow is a series of steps that need to be executed sequentially.

## Startup

1 | Pre-checks - Perform a series of checks to ensure the system is ready to run. The checks include:

- Verify dependencies are installed
- Ensure directories are created
- Check for available configuration files
- Ensure required peripherals are available

2 | Load Configuration - The system configuration file is read and settings are loaded.
