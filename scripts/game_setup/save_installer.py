"""Save file installation utilities."""

import os
import shutil
import platform
from pathlib import Path
from typing import Optional, Tuple


class SaveFileInstaller:
    """Handles installation of game save files."""

    # Default save file locations by game and OS
    SAVE_LOCATIONS = {
        'skylines': {
            'windows': r'C:\Users\{username}\AppData\Local\Colossal Order\Cities_Skylines\Saves',
            'darwin': '/Users/{username}/Library/Application Support/Colossal Order/Cities_Skylines/Saves',
            'linux': '/home/{username}/.local/share/Colossal Order/Cities_Skylines/Saves',
        },
        'rdr2': {
            'windows': r'C:\Users\{username}\Documents\Rockstar Games\Red Dead Redemption 2\Profiles',
            'windows_alt': r'C:\Users\{username}\AppData\Roaming\Goldberg SocialClub Emu Saves\RDR2',
        },
        'stardew': {
            'windows': r'C:\Users\{username}\AppData\Roaming\StardewValley\Saves',
            'darwin': '/Users/{username}/.config/StardewValley/Saves',
            'linux': '/home/{username}/.config/StardewValley/Saves',
        },
        'dealers': {
            'windows': r'C:\Users\{username}\AppData\LocalLow\Abyte Entertainment\Dealer\'s Life 2',
        },
    }

    def __init__(self, game_name: str):
        """Initialize installer for specific game."""
        self.game_name = game_name
        self.system = platform.system().lower()
        if self.system == 'darwin':
            self.system = 'darwin'  # macOS

        self.username = os.environ.get('USER') or os.environ.get('USERNAME')

    def get_save_directory(self) -> Optional[Path]:
        """Get the game's save directory for current OS."""
        if self.game_name not in self.SAVE_LOCATIONS:
            return None

        locations = self.SAVE_LOCATIONS[self.game_name]

        # Try primary location for OS
        if self.system in locations:
            path_template = locations[self.system]
            path_str = path_template.format(username=self.username)
            return Path(path_str)

        # Try alternate locations
        for key in locations:
            if key.startswith(self.system):
                path_template = locations[key]
                path_str = path_template.format(username=self.username)
                path = Path(path_str)
                if path.exists():
                    return path

        return None

    def find_all_save_locations(self) -> list[Path]:
        """Find all possible save locations that exist."""
        if self.game_name not in self.SAVE_LOCATIONS:
            return []

        locations = self.SAVE_LOCATIONS[self.game_name]
        existing = []

        for key, path_template in locations.items():
            if not key.startswith(self.system):
                continue

            path_str = path_template.format(username=self.username)
            path = Path(path_str)

            if path.exists():
                existing.append(path)

        return existing

    def get_source_save_files(self) -> list[Path]:
        """Get list of save files provided with Cradle."""
        save_dir = Path('res') / self.game_name / 'saves'

        if not save_dir.exists():
            return []

        # Common save file extensions
        extensions = ['.crp', '.sav', '.save', '.dat', '.xml']

        save_files = []
        for ext in extensions:
            save_files.extend(save_dir.glob(f'*{ext}'))

        # Also check for directories (some games use folder-based saves)
        for item in save_dir.iterdir():
            if item.is_dir():
                save_files.append(item)

        return save_files

    def install_save_files(self, backup: bool = True) -> Tuple[bool, str]:
        """
        Install save files to game directory.

        Args:
            backup: Whether to backup existing saves first

        Returns:
            Tuple of (success, message)
        """
        # Get source files
        source_files = self.get_source_save_files()

        if not source_files:
            return False, f"No save files found in res/{self.game_name}/saves"

        # Get destination directory
        dest_dir = self.get_save_directory()

        if dest_dir is None:
            # Try to find any existing location
            existing = self.find_all_save_locations()
            if existing:
                dest_dir = existing[0]
            else:
                return False, f"Could not find save directory for {self.game_name} on {self.system}"

        # Create destination if it doesn't exist
        if not dest_dir.exists():
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Could not create save directory: {e}"

        # Backup existing saves if requested
        if backup and any(dest_dir.iterdir()):
            backup_dir = dest_dir.parent / f"{dest_dir.name}_backup"
            try:
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
                shutil.copytree(dest_dir, backup_dir)
            except Exception as e:
                return False, f"Failed to backup existing saves: {e}"

        # Copy save files
        installed = []
        errors = []

        for source_file in source_files:
            try:
                dest_file = dest_dir / source_file.name

                if source_file.is_dir():
                    if dest_file.exists():
                        shutil.rmtree(dest_file)
                    shutil.copytree(source_file, dest_file)
                else:
                    shutil.copy2(source_file, dest_file)

                installed.append(source_file.name)
            except Exception as e:
                errors.append(f"{source_file.name}: {e}")

        if errors:
            return False, f"Installed {len(installed)} files, but had errors: {', '.join(errors)}"

        if not installed:
            return False, "No files were installed"

        return True, f"Successfully installed {len(installed)} save file(s) to {dest_dir}"

    def verify_installation(self) -> Tuple[bool, str]:
        """Verify that save files are properly installed."""
        dest_dir = self.get_save_directory()

        if dest_dir is None:
            return False, "Could not find save directory"

        if not dest_dir.exists():
            return False, f"Save directory does not exist: {dest_dir}"

        # Check if directory has any save files
        save_files = list(dest_dir.iterdir())

        if not save_files:
            return False, f"No save files found in {dest_dir}"

        return True, f"Found {len(save_files)} save file(s) in {dest_dir}"
