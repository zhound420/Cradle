#!/usr/bin/env python3
"""
Interactive setup wizard for Cradle.

This script guides you through setting up Cradle:
1. Python environment setup (conda)
2. Dependency installation
3. API key configuration (OpenAI, Claude)
4. Local LLM provider configuration (Ollama, LM Studio, vLLM)
5. Health check validation

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

from common import api_keys, conda_env, health_check, local_llm


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
    print("  STEP 2: API Keys (API Providers)")
    print("█" * 60)

    # Check if keys already exist
    existing = api_keys.load_env_file()

    if args.quick:
        if existing:
            print("\n✓ Found existing API keys in .env")
            has_openai = 'OA_OPENAI_KEY' in existing or 'AZ_OPENAI_KEY' in existing
            has_claude = 'OA_CLAUDE_KEY' in existing or 'RF_CLAUDE_AK' in existing
            print(f"   OpenAI: {'✓' if has_openai else '✗'}")
            print(f"   Claude: {'✓' if has_claude else '✗'}")
        else:
            print("\n⏭️  No API keys found")
            print("   You can configure later or use local providers")
        return True
    else:
        # Interactive mode - always run setup
        print("\n💡 Configure API providers (OpenAI, Claude, Azure, AWS)")
        print("   Press Enter to skip any provider you don't want to use")
        print("   Local providers (Ollama, LM Studio, vLLM) are FREE alternatives")

        api_keys.interactive_setup()
        return True


def setup_step_local_providers(args):
    """Step 3: Create local LLM provider configs."""
    print("\n" + "█" * 60)
    print("  STEP 3: Local LLM Providers (FREE)")
    print("█" * 60)

    print("\n✓ Creating default configuration files for local providers...")
    print("  • Ollama (http://localhost:11434)")
    print("  • LM Studio (http://localhost:1234)")
    print("  • vLLM (http://localhost:8000)")

    # Create default configs for local providers
    from pathlib import Path
    import json

    conf_dir = Path("conf")
    conf_dir.mkdir(exist_ok=True)

    # Default configurations
    configs = {
        'ollama': {
            "base_url": "http://localhost:11434/v1",
            "comp_model": "llama3.2-vision",
            "emb_model": "nomic-embed-text"
        },
        'lmstudio': {
            "base_url": "http://localhost:1234/v1",
            "comp_model": "local-model",
            "emb_model": "nomic-embed-text"
        },
        'vllm': {
            "base_url": "http://localhost:8000/v1",
            "comp_model": "local-model",
            "emb_model": "nomic-embed-text"
        }
    }

    created_count = 0
    for provider, config_data in configs.items():
        config_file = conf_dir / f"{provider}_config.json"
        if not config_file.exists():
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
            created_count += 1

    if created_count > 0:
        print(f"\n  ✅ Created {created_count} configuration file(s)")
    else:
        print(f"\n  ✓ Configuration files already exist")

    print("\n  💡 To use a remote server, edit the config files:")
    print("     conf/ollama_config.json")
    print("     conf/lmstudio_config.json")
    print("     conf/vllm_config.json")
    print("\n  Or use: python providers.py --help")

    return True


def setup_step_health_check(args):
    """Step 4: Run health check."""
    print("\n" + "█" * 60)
    print("  STEP 4: Health Check")
    print("█" * 60)

    return health_check.run_health_check(verbose=True)


def print_next_steps():
    """Print next steps after setup."""
    print("""
╔══════════════════════════════════════════════════════════╗
║  ✅ Setup Complete!                                       ║
╚══════════════════════════════════════════════════════════╝

Next steps:

1️⃣  Manage LLM Providers:

   python providers.py --list        # See all providers
   python providers.py --select      # Choose default provider
   python providers.py --check ollama  # Test specific provider

2️⃣  Install a supported game or application:
   • Cities: Skylines (Recommended for beginners)
   • Stardew Valley
   • Red Dead Redemption 2
   • Microsoft Outlook
   • Google Chrome

3️⃣  Setup game-specific configuration (NEW!):

   python game-setup.py --list       # See all games
   python game-setup.py skylines     # Setup Cities: Skylines
   python game-setup.py rdr2         # Setup RDR2 (auto-installs dependencies)

   The game setup wizard will:
   • Detect game installation
   • Install save files automatically
   • Guide through in-game settings
   • Validate complete setup

4️⃣  Run Cradle with simplified command:

   python run.py skylines               # Use default provider
   python run.py skylines --llm ollama  # Use FREE local LLM

   Or see all options:

   python run.py --list

5️⃣  Validate your setup:

   python validate.py skylines

6️⃣  Read the documentation:

   • README.md - Overview and installation
   • CLAUDE.md - Detailed architecture guide
   • docs/GAME_SETUP_GUIDE.md - Game setup wizard guide (NEW!)
   • docs/envs/ - Game-specific setup guides
   • docs/PROVIDER_MANAGEMENT.md - LLM provider guide
   • docs/LOCAL_LLM_SETUP.md - Local LLM setup

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

        # Step 3: Local Providers
        if not setup_step_local_providers(args):
            print("\n❌ Local provider configuration failed")
            sys.exit(1)

        # Step 4: Health Check
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
