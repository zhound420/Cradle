#!/usr/bin/env python3
"""
Game-specific setup wizard for Cradle.

This script helps configure individual games and applications for use with Cradle:
1. Detects game installation
2. Installs save files automatically
3. Guides through manual settings configuration
4. Checks dependencies
5. Validates setup before running

Usage:
    python game-setup.py skylines              # Full interactive setup
    python game-setup.py rdr2 --quick          # Quick setup with defaults
    python game-setup.py stardew --check-only  # Only validate existing setup
    python game-setup.py --list                # List all available games
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from game_setup import (
    SaveFileInstaller,
    InteractiveChecklist,
    DependencyManager,
    GameDetector,
    load_game_config,
    list_available_games,
)
from game_setup.config_loader import create_checklist_from_config


def print_welcome(game_name: str):
    """Print welcome banner for specific game."""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎮  Game Setup Wizard: {game_name.upper():<30}  ║
║                                                          ║
║   Automated setup for Cradle framework                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")


def setup_step_detection(config: dict, args) -> bool:
    """Step 1: Detect game installation."""
    game_name = config['short_name']

    print("\n" + "█" * 60)
    print("  STEP 1: Game Detection")
    print("█" * 60 + "\n")

    detector = GameDetector(game_name)
    install_path = detector.find_installation()

    if install_path:
        print(f"✓ Found {config['display_name']} installation:")
        print(f"  {install_path}\n")
        return True
    else:
        print(f"⚠️  Could not automatically detect {config['display_name']}")
        print(f"   Please ensure the game is installed before proceeding.\n")

        if config['type'] == 'game':
            print("   Common installation locations:")
            from game_setup.game_detector import GameDetector
            common_paths = GameDetector(game_name)._get_common_paths()
            for path in common_paths[:3]:
                print(f"   - {path}")
            print()

        if not args.skip_prompts:
            response = input("Continue anyway? (y/n): ").lower().strip()
            return response in ['y', 'yes']

        return True


def setup_step_dependencies(config: dict, args) -> bool:
    """Step 2: Check and install dependencies."""
    game_name = config['short_name']
    dependencies = config.get('dependencies', [])

    if not dependencies:
        return True

    print("\n" + "█" * 60)
    print("  STEP 2: Dependencies")
    print("█" * 60 + "\n")

    dep_manager = DependencyManager(game_name)
    dep_results = dep_manager.check_game_dependencies()

    all_satisfied = True

    for dep_name, satisfied, message in dep_results:
        status = "✓" if satisfied else "✗"
        print(f"  [{status}] {dep_name}: {message}")

        if not satisfied:
            all_satisfied = False

    print()

    if all_satisfied:
        print("✓ All dependencies satisfied\n")
        return True

    # Offer to install missing dependencies
    if args.check_only:
        print("⚠️  Some dependencies are missing (check-only mode, skipping installation)\n")
        return False

    if args.quick or args.auto_install:
        print("📦 Installing missing dependencies automatically...\n")
        success, errors = dep_manager.install_missing_dependencies(auto_install=True)
    else:
        print("Some dependencies are missing.")
        response = input("\nInstall missing dependencies now? (y/n): ").lower().strip()

        if response in ['y', 'yes']:
            success, errors = dep_manager.install_missing_dependencies(auto_install=False)
        else:
            success = False
            errors = ["Installation skipped by user"]

    if errors:
        print("\n⚠️  Dependency issues:")
        for error in errors:
            print(f"   {error}")
        print()

    return success or args.skip_prompts


def setup_step_save_files(config: dict, args) -> bool:
    """Step 3: Install save files."""
    game_name = config['short_name']
    save_config = config.get('save_files', {})

    if not save_config.get('enabled', False):
        return True

    print("\n" + "█" * 60)
    print("  STEP 3: Save Files")
    print("█" * 60 + "\n")

    installer = SaveFileInstaller(game_name)

    # Check if save files exist in source
    source_files = installer.get_source_save_files()

    if not source_files:
        print(f"ℹ️  No save files found in res/{game_name}/saves")
        if save_config.get('notes'):
            print(f"   Note: {save_config['notes']}")
        print()
        return True

    print(f"Found {len(source_files)} save file(s) to install:")
    for f in source_files:
        print(f"  - {f.name}")
    print()

    # Check if already installed
    is_installed, install_msg = installer.verify_installation()

    if is_installed and not args.force_reinstall:
        print(f"✓ Save files already installed")
        print(f"  {install_msg}\n")

        if not args.quick and not args.skip_prompts:
            response = input("Reinstall save files? (y/n): ").lower().strip()
            if response not in ['y', 'yes']:
                return True
        else:
            return True

    # Install save files
    if args.check_only:
        print("ℹ️  Check-only mode: skipping installation\n")
        return is_installed

    print("📁 Installing save files...")

    success, message = installer.install_save_files(backup=True)

    if success:
        print(f"  ✓ {message}\n")
        return True
    else:
        print(f"  ✗ {message}\n")
        return False


def setup_step_manual_config(config: dict, args) -> bool:
    """Step 4: Guide through manual configuration."""
    game_name = config['short_name']
    checklist_data = config.get('checklist', [])

    if not checklist_data:
        return True

    print("\n" + "█" * 60)
    print("  STEP 4: Game Configuration")
    print("█" * 60 + "\n")

    print(f"The following settings must be configured manually in {config['display_name']}:\n")

    # Create checklist
    checklist_items = create_checklist_from_config(config)
    checklist = InteractiveChecklist(config['display_name'], checklist_items)

    # Load previous progress if exists
    progress_file = Path(f".cradle_setup_{game_name}.json")
    if progress_file.exists():
        checklist.load_progress(str(progress_file))

    if args.check_only or args.display_only:
        # Just display checklist
        checklist.run_display_only()
        return True

    # Run interactive checklist
    success = checklist.run_interactive(skip_completed=not args.force_reinstall)

    # Save progress
    checklist.save_progress(str(progress_file))

    return success


def setup_step_validation(config: dict, args) -> bool:
    """Step 5: Validate complete setup."""
    game_name = config['short_name']
    validation_config = config.get('validation', {})

    if not validation_config:
        return True

    print("\n" + "█" * 60)
    print("  STEP 5: Validation")
    print("█" * 60 + "\n")

    print("🔍 Validating setup...\n")

    all_passed = True

    # Check dependencies
    if validation_config.get('check_dependencies', False):
        dep_manager = DependencyManager(game_name)
        dep_results = dep_manager.check_game_dependencies()

        for dep_name, satisfied, message in dep_results:
            status = "✓" if satisfied else "✗"
            print(f"  [{status}] {dep_name}: {message}")
            if not satisfied:
                all_passed = False

    # Check save files
    if config.get('save_files', {}).get('enabled', False):
        installer = SaveFileInstaller(game_name)
        is_installed, msg = installer.verify_installation()

        status = "✓" if is_installed else "✗"
        print(f"  [{status}] Save files: {msg}")

        if not is_installed:
            all_passed = False

    # Check game installation
    detector = GameDetector(game_name)
    install_path = detector.find_installation()

    if install_path:
        print(f"  [✓] Game installation: Found at {install_path}")
    else:
        print(f"  [⚠️] Game installation: Not auto-detected (manual check needed)")

    print()

    if all_passed:
        print("✅ All automated checks passed!\n")
    else:
        print("⚠️  Some checks failed. Please review and fix issues.\n")

    return all_passed


def print_next_steps(config: dict):
    """Print next steps after setup."""
    game_name = config['short_name']
    quick_start = config.get('quick_start', {})

    print("""
╔══════════════════════════════════════════════════════════╗
║  ✅ Setup Complete!                                       ║
╚══════════════════════════════════════════════════════════╝

Next steps:

1️⃣  Launch the game and verify all settings are correct

2️⃣  Load the appropriate save file (if applicable)

3️⃣  Run Cradle with the game:
""")

    if 'command' in quick_start:
        print(f"   {quick_start['command']}")

    if 'with_ollama' in quick_start:
        print(f"   {quick_start['with_ollama']}  # FREE local LLM")

    for key, cmd in quick_start.items():
        if key not in ['command', 'with_ollama']:
            print(f"   {cmd}  # {key}")

    print(f"""
4️⃣  Monitor execution:
   - Watch console output
   - Check logs/ directory for detailed logs
   - Use Ctrl+C to stop

5️⃣  If issues occur:
   - Re-run this setup: python game-setup.py {game_name}
   - Check documentation: docs/envs/{game_name}.md
   - Validate setup: python validate.py {game_name}

═══════════════════════════════════════════════════════════

Happy gaming! 🎮
""")


def list_games():
    """List all available games."""
    print("\n📚 Available Games and Applications")
    print("=" * 70)

    games_list = list_available_games()

    # Group by type
    games = [g for g in games_list if g['type'] == 'game']
    apps = [g for g in games_list if g['type'] == 'application']

    print("\n🎮 Games:")
    print("-" * 70)
    for game in games:
        platform = game.get('platform', 'multi')
        platform_str = f"({platform})" if platform != 'multi' else "(multi-platform)"
        print(f"   {game['short_name']:<15} - {game['display_name']:<30} {platform_str}")

    print("\n📱 Applications:")
    print("-" * 70)
    for app in apps:
        platform = app.get('platform', 'multi')
        platform_str = f"({platform})" if platform != 'multi' else "(multi-platform)"
        print(f"   {app['short_name']:<15} - {app['display_name']:<30} {platform_str}")

    print("\nUsage: python game-setup.py <game_name>")
    print("Example: python game-setup.py skylines\n")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description='Game-specific setup wizard for Cradle',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'game',
        nargs='?',
        help='Game or application short name (e.g., skylines, rdr2, stardew)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available games and applications'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick setup: use defaults, minimal prompts'
    )

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only validate existing setup, do not modify anything'
    )

    parser.add_argument(
        '--display-only',
        action='store_true',
        help='Display checklist without interaction'
    )

    parser.add_argument(
        '--auto-install',
        action='store_true',
        help='Automatically install dependencies without prompting'
    )

    parser.add_argument(
        '--force-reinstall',
        action='store_true',
        help='Force reinstall of save files and re-run all checklist items'
    )

    parser.add_argument(
        '--skip-prompts',
        action='store_true',
        help='Skip all prompts and continue with best effort'
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        list_games()
        sys.exit(0)

    # Require game name
    if not args.game:
        parser.print_help()
        print("\nError: Please specify a game name or use --list to see available games")
        sys.exit(1)

    # Load game config
    config = load_game_config(args.game)

    if config is None:
        print(f"\n❌ Unknown game: {args.game}")
        print("   Use --list to see available games\n")
        sys.exit(1)

    # Welcome
    print_welcome(config['display_name'])

    if args.quick:
        print("⚡ Running in QUICK mode")
        print("   Using defaults, minimal prompts\n")
    elif args.check_only:
        print("🔍 Running in CHECK-ONLY mode")
        print("   Validating existing setup only\n")

    # Run setup steps
    try:
        steps = [
            ("Detection", setup_step_detection),
            ("Dependencies", setup_step_dependencies),
            ("Save Files", setup_step_save_files),
            ("Manual Configuration", setup_step_manual_config),
            ("Validation", setup_step_validation),
        ]

        results = {}

        for step_name, step_func in steps:
            success = step_func(config, args)
            results[step_name] = success

        # Print summary
        print("\n" + "=" * 60)
        print("  Setup Summary")
        print("=" * 60 + "\n")

        for step_name, success in results.items():
            if success:
                print(f"  [✓] {step_name}: Passed")
            else:
                print(f"  [✗] {step_name}: Failed or incomplete")

        print()

        # Check if all required steps passed
        all_passed = all(results.values())

        if all_passed:
            print_next_steps(config)
            sys.exit(0)
        else:
            print("⚠️  Setup incomplete. Please review the issues above.\n")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
