"""Game-specific setup utilities for Cradle."""

from .save_installer import SaveFileInstaller
from .checklist import InteractiveChecklist
from .dependency_manager import DependencyManager
from .game_detector import GameDetector
from .config_loader import load_game_config, list_available_games

__all__ = [
    'SaveFileInstaller',
    'InteractiveChecklist',
    'DependencyManager',
    'GameDetector',
    'load_game_config',
    'list_available_games',
]
