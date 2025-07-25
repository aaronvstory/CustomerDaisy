# CustomerDaisy CLI - Portable Export Package

This package contains everything needed to run the CustomerDaisy CLI application on any Windows PC.

## 🚨 **IMPORTANT - Use These Files:**
- **setup.bat** - Main setup script (FIXED VERSION)
- **launch.bat** - Main launcher (FIXED VERSION)

## What's Included

This export contains:
- ✅ Complete Python CLI application
- ✅ Pre-configured API keys (DaisySMS & MapQuest)
- ✅ All required dependencies via UV package manager
- ✅ Fixed setup and launch scripts
- ✅ Required directory structure
- ✅ 21 sample customer records

## Quick Start (New PC Setup)

1. **Copy this entire export folder** to your desired location (e.g., `C:\CustomerDaisy\`)
2. **Run `setup.bat`** - This will automatically:
   - Install UV package manager if needed
   - Create Python virtual environment
   - Install all dependencies
   - Create required directories
   - Test API connections
3. **Run `launch.bat`** - Starts the CustomerDaisy application
4. **Done!** The application should launch with all API keys working

## API Keys Already Configured

The following API keys are pre-configured in `config.ini`:
- **DaisySMS**: `0zkRwZsn4Ahm2KtMZ1Zl9nPxvnIg2Y` (Balance: $6.69)
- **MapQuest**: `FzB4PTf1mTlOhn6fajm5irPjsnavYGJn`
- **Mail.tm**: Uses free API (no key required)

## Directory Structure

```
export/
├── main.py              # Main application
├── config.ini           # Configuration with API keys
├── setup.bat           # One-time setup script (FIXED)
├── launch.bat          # Application launcher (FIXED)
├── pyproject.toml      # Python dependencies
├── uv.lock            # Dependency lock file
├── CLAUDE.md          # Development instructions
├── src/               # Python modules
│   ├── config_manager.py
│   ├── customer_db.py
│   ├── daisy_sms.py
│   ├── mail_tm.py
│   ├── mapquest_address.py
│   └── sms_monitor.py
├── customer_data/     # Database storage (21 sample customers)
├── logs/             # Application logs
├── backups/          # Automatic backups
└── exports/          # Data exports
```

## Requirements

- **Windows 10/11** (batch files are Windows-specific)
- **Internet connection** (for UV installation and API calls)
- **No Python installation required** (UV handles everything)

## Troubleshooting

### Setup Issues
- If `setup.bat` fails, try running as Administrator
- Ensure internet connection for UV installation
- Check Windows Defender/Antivirus isn't blocking downloads
- If UV installation fails, visit: https://docs.astral.sh/uv/getting-started/installation/

### API Issues
- Test DaisySMS balance: Check account at https://daisysms.com/
- MapQuest quota: Check usage at https://developer.mapquest.com/
- Config errors: Verify `config.ini` wasn't modified

### Application Issues  
- Run `launch.bat` from the export directory
- Check `logs/customer_daisy.log` for error details
- Ensure all directories exist (run `setup.bat` again if needed)

## Usage Instructions

Once launched, the application provides:
1. **Customer Creation** - Generate customers with phone verification
2. **SMS Monitoring** - Real-time SMS code reception
3. **Data Export** - Export customer data in multiple formats
4. **Analytics** - Customer statistics and reports

Follow the on-screen menus and prompts for all features.

## Production Status
✅ **FIXED**: Database sorting error resolved
✅ **TESTED**: All core functions working
✅ **VERIFIED**: API connections stable
✅ **READY**: Production deployment complete

## Sharing This Package

This export package can be freely shared and includes:
- All necessary API keys (pre-approved for sharing)
- Complete dependency management
- Automated setup process
- No additional configuration required
- Fixed batch scripts that work properly

Simply copy the entire export folder and follow the Quick Start guide!