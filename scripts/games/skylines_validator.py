"""Cities: Skylines specific validation."""

import sys
import platform
from pathlib import Path
from typing import Tuple, List


def find_steam_path() -> Path:
    """Try to find Steam installation path."""
    system = platform.system()

    if system == "Windows":
        possible_paths = [
            Path("C:/Program Files (x86)/Steam"),
            Path("C:/Program Files/Steam"),
            Path.home() / "Steam",
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            Path.home() / "Library/Application Support/Steam",
        ]
    else:  # Linux
        possible_paths = [
            Path.home() / ".steam/steam",
            Path.home() / ".local/share/Steam",
        ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def check_game_installed() -> Tuple[bool, str]:
    """Check if Cities: Skylines is installed."""
    steam_path = find_steam_path()

    if not steam_path:
        return False, "Steam not found"

    # Common Steam library locations
    library_paths = [
        steam_path / "steamapps/common/Cities_Skylines",
    ]

    # Check for additional library folders
    library_folders = steam_path / "steamapps/libraryfolders.vdf"
    # Could parse this file to find additional library locations

    for lib_path in library_paths:
        if lib_path.exists():
            return True, f"Found at {lib_path}"

    return False, "Game not found in Steam library"


def check_required_skills() -> List[str]:
    """Check if required skills are defined."""
    skills_path = Path("cradle/environment/skylines/atomic_skills")

    if not skills_path.exists():
        return ["Skills directory not found"]

    skill_files = list(skills_path.glob("*.py"))
    if len(skill_files) <= 1:  # Just __init__.py
        return ["No skill files found"]

    return []


def validate() -> bool:
    """Run Cities: Skylines specific validation."""
    print("\n🏙️  Cities: Skylines Validation")
    print("=" * 60)

    all_ok = True

    # Check game installation
    print("\n1️⃣  Game Installation")
    print("-" * 40)
    game_ok, game_msg = check_game_installed()
    status = "✓" if game_ok else "⚠️"
    print(f"   {status} {game_msg}")
    if not game_ok:
        print("      Install from: https://store.steampowered.com/app/255710")

    # Check skills
    print("\n2️⃣  Skills Configuration")
    print("-" * 40)
    skill_issues = check_required_skills()
    if not skill_issues:
        print("   ✓ Skills are configured")
    else:
        print("   ✗ Skill issues found:")
        for issue in skill_issues:
            print(f"      - {issue}")
        all_ok = False

    # Check prompts
    print("\n3️⃣  Prompts")
    print("-" * 40)
    prompts_path = Path("res/skylines/prompts/templates")
    if prompts_path.exists():
        prompt_files = list(prompts_path.glob("*.prompt"))
        print(f"   ✓ {len(prompt_files)} prompt templates found")
    else:
        print("   ✗ Prompts directory not found")
        all_ok = False

    # Check config
    print("\n4️⃣  Configuration")
    print("-" * 40)
    config_path = Path("conf/env_config_skylines.json")
    if config_path.exists():
        print(f"   ✓ Configuration file exists")
    else:
        print(f"   ✗ Configuration file missing")
        all_ok = False

    # Summary
    print("\n" + "=" * 60)
    if all_ok and game_ok:
        print("✅ Cities: Skylines is ready!")
        print("\nRun with: python run.py skylines")
    elif all_ok:
        print("⚠️  Cradle is configured, but game may not be installed")
        print("   You can still test other features")
    else:
        print("❌ Some components are missing")
        print("   Run 'python setup.py' to configure")

    print("=" * 60 + "\n")

    return all_ok


if __name__ == '__main__':
    success = validate()
    sys.exit(0 if success else 1)
