#!/usr/bin/env python3
"""
Interactive setup wizard for Cradle.

This script guides you through setting up Cradle:
1. Python environment setup (conda)
2. Dependency installation
3. API key configuration
4. Health check validation

Usage:
    python setup.py           # Full interactive setup
    python setup.py --quick   # Skip prompts, use defaults
    python setup.py --keys-only  # Only configure API keys
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from common import api_keys, conda_env, health_check


def print_welcome():
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎮  Cradle Setup Wizard                                ║
║                                                          ║
║   Empowering Foundation Agents Towards                   ║
║   General Computer Control                               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")


def setup_step_environment(args):
    """Step 1: Setup Python environment."""
    if args.keys_only:
        return True

    print("\n" + "█" * 60)
    print("  STEP 1: Python Environment")
    print("█" * 60)

    if args.quick:
        print("\n⚡ Quick mode: Installing dependencies...")
        success = conda_env.install_requirements()
        success = conda_env.install_spacy_model() and success
        return success
    else:
        return conda_env.setup_environment()


def setup_step_api_keys(args):
    """Step 2: Configure API keys."""
    print("\n" + "█" * 60)
    print("  STEP 2: API Keys")
    print("█" * 60)

    if args.quick:
        # Check if keys already exist
        existing = api_keys.load_env_file()
        if existing:
            print("\n✓ Found existing API keys in .env")
            return True
        else:
            print("\n⚠️  No API keys found!")
            print("   Cannot continue in quick mode without API keys.")
            print("   Run without --quick to configure keys interactively.")
            return False
    else:
        api_keys.interactive_setup()
        return True


def setup_step_health_check(args):
    """Step 3: Run health check."""
    print("\n" + "█" * 60)
    print("  STEP 3: Health Check")
    print("█" * 60)

    return health_check.run_health_check(verbose=True)


def print_next_steps():
    """Print next steps after setup."""
    print("""
╔══════════════════════════════════════════════════════════╗
║  ✅ Setup Complete!                                       ║
╚══════════════════════════════════════════════════════════╝

Next steps:

1️⃣  Install a supported game or application:
   • Cities: Skylines (Recommended for beginners)
   • Stardew Valley
   • Red Dead Redemption 2
   • Microsoft Outlook
   • Google Chrome

2️⃣  Run Cradle with simplified command:

   python run.py skylines

   Or see all options:

   python run.py --list

3️⃣  Validate your setup:

   python validate.py skylines

4️⃣  Read the documentation:

   • README.md - Overview and installation
   • CLAUDE.md - Detailed architecture guide
   • docs/envs/ - Game-specific setup guides

═══════════════════════════════════════════════════════════

Need help?
• GitHub: https://github.com/BAAI-Agents/Cradle
• Paper: https://arxiv.org/abs/2403.03186

Happy gaming! 🎮
""")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description='Interactive Cradle setup wizard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick setup: skip prompts, use defaults'
    )

    parser.add_argument(
        '--keys-only',
        action='store_true',
        help='Only configure API keys (skip environment setup)'
    )

    parser.add_argument(
        '--no-health-check',
        action='store_true',
        help='Skip health check at the end'
    )

    args = parser.parse_args()

    # Welcome
    print_welcome()

    if args.quick:
        print("⚡ Running in QUICK mode")
        print("   Using defaults where possible\n")
    elif args.keys_only:
        print("🔑 Running in KEYS-ONLY mode")
        print("   Will only configure API keys\n")

    # Run setup steps
    try:
        # Step 1: Environment
        if not setup_step_environment(args):
            print("\n❌ Environment setup failed")
            sys.exit(1)

        # Step 2: API Keys
        if not setup_step_api_keys(args):
            print("\n❌ API key configuration failed")
            sys.exit(1)

        # Step 3: Health Check
        if not args.no_health_check:
            setup_step_health_check(args)
            # Don't fail on health check issues, just warn

        # Success!
        print_next_steps()

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
