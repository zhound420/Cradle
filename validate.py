#!/usr/bin/env python3
"""
Validate Cradle setup for specific game/application.

This script checks if everything is properly configured for a specific
game or application environment.

Usage:
    python validate.py                # General validation
    python validate.py skylines       # Validate Cities: Skylines setup
    python validate.py rdr2-story     # Validate RDR2 setup
    python validate.py outlook        # Validate Outlook setup
    python validate.py --list         # List available environments
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from common import health_check


# Map run.py game names to environment short names
GAME_ENV_MAP = {
    'skylines': 'skylines',
    'rdr2-story': 'rdr2',
    'rdr2-open': 'rdr2',
    'stardew-shopping': 'stardew',
    'stardew-farming': 'stardew',
    'stardew-cultivation': 'stardew',
    'dealers': 'dealers',
    'outlook': 'outlook',
    'chrome': 'chrome',
    'capcut': 'capcut',
    'feishu': 'feishu',
    'xiuxiu': 'xiuxiu',
}


def validate_general():
    """Run general health check."""
    print("\n🔍 Running General Validation")
    print("=" * 60)
    success = health_check.run_health_check(verbose=True)
    return success


def validate_specific_game(game_key: str):
    """Validate specific game/app setup."""
    env_name = GAME_ENV_MAP.get(game_key)

    if not env_name:
        print(f"❌ Unknown game/app: {game_key}")
        print("   Use --list to see available options")
        return False

    print(f"\n🔍 Validating: {game_key}")
    print("=" * 60)

    # Run general checks first
    print("\n📋 General Health Check")
    print("-" * 40)
    general_ok = health_check.run_health_check(verbose=False)

    # Run specific environment checks
    print(f"\n🎮 {game_key.upper()} Specific Checks")
    print("-" * 40)

    env_ok, issues = health_check.check_game_environment(env_name)

    if env_ok:
        print(f"   ✓ {game_key} environment is properly configured")
    else:
        print(f"   ✗ {game_key} environment has issues:")
        for issue in issues:
            print(f"      - {issue}")

    # Game-specific validation
    if env_name in ['skylines', 'rdr2', 'stardew', 'dealers']:
        print(f"\n🎲 Game Installation Check")
        print("-" * 40)
        print(f"   ⚠️  Please ensure {game_key} is installed and runnable")
        print("      This script cannot detect game installations automatically")

    elif env_name in ['outlook', 'chrome', 'capcut', 'feishu', 'xiuxiu']:
        print(f"\n📱 Application Check")
        print("-" * 40)
        print(f"   ⚠️  Please ensure {game_key} is installed")

    # Overall status
    print("\n" + "=" * 60)
    if general_ok and env_ok:
        print(f"✅ {game_key} is ready to use!")
        print(f"\nRun with: python run.py {game_key}")
    else:
        print(f"⚠️  {game_key} setup is incomplete")
        print("   Run 'python setup.py' to fix common issues")

    print("=" * 60 + "\n")

    return general_ok and env_ok


def list_available():
    """List all available game/app configurations."""
    print("\n📚 Available Environments")
    print("=" * 60)

    games = {}
    apps = {}

    # Categorize by type
    for key in GAME_ENV_MAP.keys():
        env_name = GAME_ENV_MAP[key]
        config_path = Path(f'cradle/environment/{env_name}')

        if config_path.exists():
            # Check if it's a game or app
            if env_name in ['skylines', 'rdr2', 'stardew', 'dealers']:
                if env_name not in games:
                    games[env_name] = []
                games[env_name].append(key)
            else:
                if env_name not in apps:
                    apps[env_name] = []
                apps[env_name].append(key)

    print("\n🎮 Games:")
    print("-" * 40)
    for env_name, keys in sorted(games.items()):
        for key in keys:
            print(f"   {key}")

    print("\n📱 Applications:")
    print("-" * 40)
    for env_name, keys in sorted(apps.items()):
        for key in keys:
            print(f"   {key}")

    print("\nUsage: python validate.py <environment>")
    print("Example: python validate.py skylines\n")


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description='Validate Cradle setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'game',
        nargs='?',
        choices=list(GAME_ENV_MAP.keys()),
        help='Game or application to validate'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available environments'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed error messages'
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        list_available()
        sys.exit(0)

    # Run appropriate validation
    try:
        if args.game:
            success = validate_specific_game(args.game)
        else:
            success = validate_general()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
