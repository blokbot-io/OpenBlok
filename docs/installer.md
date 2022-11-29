## Installer Options

## Installer Operations

The installer runs through a serious of operations to install OpenBlok. The operations are listed below:

1. Verify the installer is running as root
2. Verify the user "blok" exists
3. Install Dependencies
   - Python 3.10
   - Package unzip
   - Package jq
   - Package v4l-utils (for audio generation)
   - cv2 required packages ffmpeg libsm6 libxext6
4. Get OpenBlok
   - Get latest release version number
   - Download OpenBlok Zip from GitHub
   - unzip OpenBlok Zip
5. Create Environment
   - Create virtual environment
   - Install Python dependencies
6. Create System Files
   - /opt/OpenBlok/system.json
7. Housekeeping
   - Remove temp zip file
   - Set permissions
