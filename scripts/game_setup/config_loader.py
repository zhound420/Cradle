"""Game configuration loader for setup wizard."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from .checklist import ChecklistItem


def load_game_config(game_name: str) -> Optional[Dict]:
    """
    Load game-specific setup configuration.

    Args:
        game_name: Short name of the game (e.g., 'skylines', 'rdr2')

    Returns:
        Configuration dict or None if not found
    """
    config_path = Path(__file__).parent / 'configs' / f'{game_name}.json'

    if not config_path.exists():
        return None

    with open(config_path, 'r') as f:
        return json.load(f)


def create_checklist_from_config(config: Dict) -> List[ChecklistItem]:
    """
    Create checklist items from configuration.

    Args:
        config: Game configuration dict

    Returns:
        List of ChecklistItem objects
    """
    items = []

    for item_data in config.get('checklist', []):
        item = ChecklistItem(
            id=item_data['id'],
            title=item_data['title'],
            description=item_data.get('description', ''),
            instructions=item_data.get('instructions', []),
            optional=item_data.get('optional', False),
            image_path=item_data.get('image_path'),
        )
        items.append(item)

    return items


def list_available_games() -> List[Dict[str, str]]:
    """
    List all available game configurations.

    Returns:
        List of dicts with game info
    """
    configs_dir = Path(__file__).parent / 'configs'

    if not configs_dir.exists():
        return []

    games = []

    for config_file in configs_dir.glob('*.json'):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            games.append({
                'short_name': config_file.stem,
                'display_name': config.get('display_name', config_file.stem),
                'type': config.get('type', 'game'),
                'platform': config.get('platform', 'multi'),
            })
        except Exception:
            continue

    return sorted(games, key=lambda x: x['display_name'])
