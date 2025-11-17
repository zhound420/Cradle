"""Game installation detection utilities."""

import os
import platform
import winreg
from pathlib import Path
from typing import Optional, List


class GameDetector:
    """Detects game installations on the system."""

    # Common installation paths by game
    COMMON_PATHS = {
        'skylines': {
            'windows': [
                r'C:\Program Files (x86)\Steam\steamapps\common\Cities_Skylines',
                r'C:\Program Files\Steam\steamapps\common\Cities_Skylines',
                r'D:\SteamLibrary\steamapps\common\Cities_Skylines',
                r'E:\SteamLibrary\steamapps\common\Cities_Skylines',
            ],
            'darwin': [
                '~/Library/Application Support/Steam/steamapps/common/Cities_Skylines',
            ],
            'linux': [
                '~/.steam/steam/steamapps/common/Cities_Skylines',
                '~/.local/share/Steam/steamapps/common/Cities_Skylines',
            ],
        },
        'rdr2': {
            'windows': [
                r'C:\Program Files\Rockstar Games\Red Dead Redemption 2',
                r'C:\Program Files (x86)\Steam\steamapps\common\Red Dead Redemption 2',
                r'D:\SteamLibrary\steamapps\common\Red Dead Redemption 2',
                r'E:\SteamLibrary\steamapps\common\Red Dead Redemption 2',
            ],
        },
        'stardew': {
            'windows': [
                r'C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley',
                r'C:\Program Files\Steam\steamapps\common\Stardew Valley',
                r'D:\SteamLibrary\steamapps\common\Stardew Valley',
            ],
            'darwin': [
                '~/Library/Application Support/Steam/steamapps/common/Stardew Valley',
            ],
            'linux': [
                '~/.steam/steam/steamapps/common/Stardew Valley',
                '~/.local/share/Steam/steamapps/common/Stardew Valley',
            ],
        },
    }

    # Executable names to verify installation
    EXECUTABLES = {
        'skylines': ['Cities.exe', 'Cities_Data', 'Cities'],
        'rdr2': ['RDR2.exe', 'PlayRDR2.exe'],
        'stardew': ['Stardew Valley.exe', 'StardewValley.exe', 'StardewValley'],
        'dealers': ['Dealers Life 2.exe'],
    }

    def __init__(self, game_name: str):
        """Initialize detector for specific game."""
        self.game_name = game_name
        self.system = platform.system().lower()

    def find_installation(self) -> Optional[Path]:
        """
        Find game installation directory.

        Returns:
            Path to game installation or None if not found
        """
        # Check common paths
        paths = self._get_common_paths()

        for path_str in paths:
            path = Path(os.path.expanduser(path_str))
            if self._verify_installation(path):
                return path

        # Try Steam library detection
        steam_path = self._find_steam_installation()
        if steam_path:
            return steam_path

        return None

    def _get_common_paths(self) -> List[str]:
        """Get list of common paths for current game and OS."""
        if self.game_name not in self.COMMON_PATHS:
            return []

        game_paths = self.COMMON_PATHS[self.game_name]

        if self.system in game_paths:
            return game_paths[self.system]

        return []

    def _verify_installation(self, path: Path) -> bool:
        """
        Verify that path contains a valid game installation.

        Args:
            path: Path to check

        Returns:
            True if valid installation found
        """
        if not path.exists() or not path.is_dir():
            return False

        # Check for expected executables/directories
        if self.game_name not in self.EXECUTABLES:
            # If no executables defined, just check if directory exists
            return True

        expected_files = self.EXECUTABLES[self.game_name]

        for expected in expected_files:
            if (path / expected).exists():
                return True

        return False

    def _find_steam_installation(self) -> Optional[Path]:
        """Find game installation through Steam registry/config."""
        if self.system == 'windows':
            return self._find_steam_windows()
        elif self.system == 'darwin':
            return self._find_steam_macos()
        elif self.system == 'linux':
            return self._find_steam_linux()

        return None

    def _find_steam_windows(self) -> Optional[Path]:
        """Find Steam installation on Windows via registry."""
        try:
            # Open Steam registry key
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\WOW6432Node\Valve\Steam'
            )

            install_path = winreg.QueryValueEx(key, 'InstallPath')[0]
            winreg.CloseKey(key)

            # Parse libraryfolders.vdf to find all Steam libraries
            library_folders = self._parse_steam_libraries(Path(install_path))

            # Search for game in each library
            for library in library_folders:
                game_path = library / 'steamapps' / 'common' / self._get_steam_folder_name()
                if self._verify_installation(game_path):
                    return game_path

        except (OSError, FileNotFoundError):
            pass

        return None

    def _find_steam_macos(self) -> Optional[Path]:
        """Find Steam installation on macOS."""
        steam_path = Path.home() / 'Library' / 'Application Support' / 'Steam'

        if not steam_path.exists():
            return None

        library_folders = self._parse_steam_libraries(steam_path)

        for library in library_folders:
            game_path = library / 'steamapps' / 'common' / self._get_steam_folder_name()
            if self._verify_installation(game_path):
                return game_path

        return None

    def _find_steam_linux(self) -> Optional[Path]:
        """Find Steam installation on Linux."""
        possible_steam_paths = [
            Path.home() / '.steam' / 'steam',
            Path.home() / '.local' / 'share' / 'Steam',
        ]

        for steam_path in possible_steam_paths:
            if not steam_path.exists():
                continue

            library_folders = self._parse_steam_libraries(steam_path)

            for library in library_folders:
                game_path = library / 'steamapps' / 'common' / self._get_steam_folder_name()
                if self._verify_installation(game_path):
                    return game_path

        return None

    def _parse_steam_libraries(self, steam_path: Path) -> List[Path]:
        """Parse Steam's libraryfolders.vdf to find all library locations."""
        libraries = [steam_path]

        vdf_file = steam_path / 'steamapps' / 'libraryfolders.vdf'

        if not vdf_file.exists():
            return libraries

        try:
            with open(vdf_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple VDF parsing (extract paths)
            import re
            paths = re.findall(r'"path"\s+"([^"]+)"', content)

            for path_str in paths:
                path = Path(path_str)
                if path.exists() and path not in libraries:
                    libraries.append(path)

        except Exception:
            pass

        return libraries

    def _get_steam_folder_name(self) -> str:
        """Get Steam common folder name for the game."""
        folder_names = {
            'skylines': 'Cities_Skylines',
            'rdr2': 'Red Dead Redemption 2',
            'stardew': 'Stardew Valley',
            'dealers': "Dealer's Life 2",
        }

        return folder_names.get(self.game_name, self.game_name)

    def is_game_running(self) -> bool:
        """
        Check if game is currently running.

        Returns:
            True if game process detected
        """
        import psutil

        process_names = {
            'skylines': ['Cities.exe'],
            'rdr2': ['RDR2.exe'],
            'stardew': ['Stardew Valley.exe', 'StardewValley'],
            'dealers': ['Dealers Life 2.exe'],
        }

        if self.game_name not in process_names:
            return False

        expected = process_names[self.game_name]

        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in expected:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return False
