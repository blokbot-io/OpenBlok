## Installer Options

## Installer Operations

The installer runs through a serious of operations to install OpenBlok. The operations are listed below:

1. Install Dependencies
   - Python 3.10
   - Package unzip
   - Package jq
2. Get OpenBlok
   - Get latest release version number
   - Download OpenBlok Zip from GitHub
   - unzip OpenBlok Zip
3. Create Environment
   - Create virtual environment
   - Install Python dependencies
4. Create System Files
   - /opt/OpenBlok/system.json
5. Housekeeping
   - Remove temp zip file
