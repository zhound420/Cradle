# Game Setup Guide

This guide explains how to set up individual games and applications for use with Cradle using the automated game setup wizard.

## Overview

The `game-setup.py` script provides an **automated, interactive wizard** that:

✅ Detects game installations automatically
✅ Installs save files to correct OS-specific locations
✅ Guides through manual settings configuration with checklists
✅ Checks and installs game-specific dependencies
✅ Validates complete setup before running

## Quick Start

### 1. List Available Games

```bash
python game-setup.py --list
```

This shows all supported games and applications with their platform support.

### 2. Run Setup for a Game

**Interactive Mode** (recommended for first-time setup):
```bash
python game-setup.py skylines        # Cities: Skylines
python game-setup.py rdr2            # Red Dead Redemption 2
python game-setup.py stardew         # Stardew Valley
python game-setup.py outlook         # Microsoft Outlook
```

**Quick Mode** (automated with minimal prompts):
```bash
python game-setup.py skylines --quick
```

**Check-Only Mode** (validate existing setup):
```bash
python game-setup.py skylines --check-only
```

## Setup Process

The wizard guides you through 5 steps:

### Step 1: Game Detection
- Automatically searches common installation paths
- Checks Steam libraries on Windows, macOS, and Linux
- Prompts to continue if game not auto-detected

### Step 2: Dependencies
- Checks for game-specific requirements (e.g., GroundingDino for RDR2)
- Offers to install missing dependencies automatically
- Shows manual installation instructions when needed

### Step 3: Save Files
- Automatically copies save files to correct OS-specific locations
- Creates backups of existing saves
- Handles both file-based and folder-based save systems

### Step 4: Manual Configuration
- Interactive checklist for in-game settings
- Shows step-by-step instructions with reference images
- Saves progress so you can resume later
- Distinguishes between required and optional settings

### Step 5: Validation
- Verifies all dependencies are satisfied
- Checks save files are properly installed
- Confirms game installation detected
- Reports any issues found

## Game-Specific Setup

### Cities: Skylines

**Requirements:**
- Resolution: 1920x1080 (16:9 aspect ratio)
- Window Mode: Fullscreen
- Edge scrolling: OFF
- Day/night cycle: OFF

**Setup Command:**
```bash
python game-setup.py skylines
```

**Key Steps:**
1. Set resolution to 1920x1080, aspect ratio 16:9
2. Disable edge scrolling in gameplay settings
3. Disable day/night cycle
4. Load the `skylines_initial` save file

**Platform Notes:**
- **Windows**: Set monitor to 1920x1080
- **macOS**: Requires M1+ chip with external monitor at low resolution 1920x1080
- **Linux**: Set display to 1920x1080

### Red Dead Redemption 2

**Requirements:**
- Resolution: 1920x1080, 2560x1440, or 3840x2160 (16:9 only)
- Window Mode: Windowed Borderless
- Mouse: DirectInput mode
- Dependencies: GroundingDino, VideoSubFinder, PyTorch

**Setup Command:**
```bash
python game-setup.py rdr2
```

**Key Steps:**
1. Install GroundingDino (wizard can do this automatically)
2. Manually download VideoSubFinder (instructions provided)
3. Change mouse mode to DirectInput
4. Enable tap-and-hold speed control
5. Set resolution and window mode
6. Enlarge minimap icons
7. Enable speaker names in subtitles

**Platform Notes:**
- **Windows only** - not available on macOS or Linux

### Stardew Valley

**Requirements:**
- Resolution: 1920x1080
- Window Mode: Windowed
- Zoom: 100%

**Setup Command:**
```bash
python game-setup.py stardew
```

**Available Scenarios:**
- `stardew-shopping` - Shopping scenario
- `stardew-farming` - Farming scenario
- `stardew-cultivation` - Cultivation scenario

### Microsoft Outlook

**Requirements:**
- Outlook 2016 or later
- Signed in with Microsoft account

**Setup Command:**
```bash
python game-setup.py outlook
```

**Key Steps:**
1. Install Microsoft Office or Outlook standalone
2. Complete initial setup and sign in
3. Set window to standard size
4. Ensure inbox view is visible

## Command-Line Options

### Basic Options

```bash
--list                  # List all available games
--quick                 # Quick setup with minimal prompts
--check-only            # Only validate, don't modify anything
--display-only          # Show checklist without interaction
```

### Advanced Options

```bash
--auto-install          # Auto-install dependencies without prompting
--force-reinstall       # Reinstall save files and re-run all checks
--skip-prompts          # Skip all prompts, continue with best effort
```

### Examples

**Quick setup for Cities: Skylines:**
```bash
python game-setup.py skylines --quick
```

**Check if RDR2 is properly configured:**
```bash
python game-setup.py rdr2 --check-only
```

**Force reinstall save files:**
```bash
python game-setup.py skylines --force-reinstall
```

**Auto-install all dependencies for RDR2:**
```bash
python game-setup.py rdr2 --auto-install
```

## Save File Management

### Automatic Installation

Save files are automatically installed to OS-specific locations:

**Cities: Skylines:**
- Windows: `C:\Users\<username>\AppData\Local\Colossal Order\Cities_Skylines\Saves`
- macOS: `/Users/<username>/Library/Application Support/Colossal Order/Cities_Skylines/Saves`
- Linux: `/home/<username>/.local/share/Colossal Order/Cities_Skylines/Saves`

**Red Dead Redemption 2:**
- Windows: `C:\Users\<username>\Documents\Rockstar Games\Red Dead Redemption 2\Profiles`
- Or: `C:\Users\<username>\AppData\Roaming\Goldberg SocialClub Emu Saves\RDR2`

**Stardew Valley:**
- Windows: `C:\Users\<username>\AppData\Roaming\StardewValley\Saves`
- macOS: `/Users/<username>/.config/StardewValley/Saves`
- Linux: `/home/<username>/.config/StardewValley/Saves`

### Backup

The wizard automatically backs up existing save files before installing new ones:
- Backup location: `<save_directory>_backup`
- Original saves are preserved
- Safe to reinstall without data loss

## Dependency Management

### Automatic Dependencies

Some dependencies can be installed automatically:

**GroundingDino** (for RDR2):
- PyTorch with CUDA support
- GroundingDino model weights
- BERT model from Hugging Face
- Automatic compilation and installation

### Manual Dependencies

Some dependencies require manual installation:

**VideoSubFinder** (for RDR2):
1. Download from https://sourceforge.net/projects/videosubfinder/
2. Extract to `res/tool/subfinder/`
3. Copy `res/tool/general.cfg` to `res/tool/subfinder/settings/general.cfg`

## Checklist Progress

The wizard saves your checklist progress so you can resume later:

**Progress Files:**
- `.cradle_setup_<game_name>.json` in project root
- Tracks which checklist items you've completed
- Automatically loaded on subsequent runs

**Resume Setup:**
```bash
# Progress is automatically loaded
python game-setup.py skylines

# Or force restart from beginning
python game-setup.py skylines --force-reinstall
```

## Troubleshooting

### Game Not Detected

If the wizard can't detect your game:
- **Check installation**: Ensure game is actually installed
- **Custom location**: Game might be in non-standard location
- **Continue anyway**: Wizard will prompt to continue manual setup

### Save Files Not Installing

If save file installation fails:
- **Check permissions**: Ensure you have write access to save directory
- **Check path**: Verify save directory exists for your game
- **Manual copy**: Copy files manually from `res/<game>/saves/`

### Dependencies Fail to Install

If automatic dependency installation fails:
- **Check internet**: GroundingDino requires downloading large files
- **Check disk space**: Model files can be several GB
- **Manual install**: Follow instructions in `docs/envs/<game>.md`

### Checklist Items Unclear

If setup instructions are unclear:
- **Check images**: Reference images are in `docs/envs/images/<game>/`
- **Check docs**: Full documentation in `docs/envs/<game>.md`
- **Skip optional**: Optional items can be skipped

## Integration with Validation

The game setup wizard is integrated with Cradle's validation system:

**After Setup:**
```bash
# Validate complete setup
python validate.py skylines
```

**Quick Check:**
```bash
# Use check-only mode
python game-setup.py skylines --check-only
```

## Adding New Games

To add support for a new game:

1. **Create configuration file:**
   - `scripts/game_setup/configs/<game_name>.json`
   - See existing configs for examples

2. **Add save file locations:**
   - Update `SaveFileInstaller.SAVE_LOCATIONS` in `save_installer.py`

3. **Add installation paths:**
   - Update `GameDetector.COMMON_PATHS` in `game_detector.py`

4. **Add dependencies:**
   - Add checks to `DependencyManager` if needed

5. **Test:**
   - Run setup wizard
   - Verify all steps work correctly

## Best Practices

### First-Time Setup

1. **Run full interactive setup** (not quick mode)
2. **Read all instructions** carefully
3. **Check reference images** when available
4. **Validate after setup** with `python validate.py <game>`
5. **Test with Cradle** to ensure everything works

### Updating Setup

1. **Use check-only mode** first: `--check-only`
2. **Force reinstall if needed**: `--force-reinstall`
3. **Backup custom saves** before reinstalling

### Multiple Computers

1. **Run setup on each computer** (save locations differ by OS)
2. **Use quick mode** on subsequent machines: `--quick`
3. **Copy progress files** if desired: `.cradle_setup_*.json`

## Next Steps

After successful setup:

1. **Verify game launches** and loads save file
2. **Check all settings** match requirements
3. **Run Cradle** with the game:
   ```bash
   python run.py skylines              # Default provider
   python run.py skylines --llm ollama # With local LLM
   ```
4. **Monitor execution** and check logs
5. **Report issues** if problems occur

## Related Documentation

- **General Setup**: `README.md`
- **Game-Specific Guides**: `docs/envs/<game>.md`
- **Provider Setup**: `docs/PROVIDER_MANAGEMENT.md`
- **Local LLM Setup**: `docs/LOCAL_LLM_SETUP.md`
- **Validation**: Run `python validate.py --help`

## Getting Help

If you encounter issues:

1. **Check logs**: Detailed error messages in console
2. **Check documentation**: `docs/envs/<game>.md`
3. **Validate setup**: `python validate.py <game>`
4. **Re-run wizard**: `python game-setup.py <game>`
5. **Report issue**: GitHub issues with error details

---

**Happy Gaming! 🎮**
