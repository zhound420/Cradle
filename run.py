#!/usr/bin/env python3
"""
Simplified Cradle runner.

Usage:
    python run.py skylines
    python run.py skylines --task-id 2
    python run.py rdr2-story
    python run.py rdr2-open
    python run.py stardew-shopping
    python run.py outlook --llm claude

Examples:
    # Run Cities: Skylines with default OpenAI config
    python run.py skylines

    # Run RDR2 story mode with specific task
    python run.py rdr2-story --task-id 1

    # Run Outlook with Claude instead of OpenAI
    python run.py outlook --llm claude

    # List all available games/apps
    python run.py --list
"""

import argparse
import sys
import os
from pathlib import Path

# Game/App configurations
CONFIGS = {
    # Cities: Skylines
    'skylines': {
        'name': 'Cities: Skylines',
        'env': './conf/env_config_skylines.json',
        'type': 'game'
    },

    # Red Dead Redemption 2
    'rdr2-story': {
        'name': 'RDR2 - Main Storyline',
        'env': './conf/env_config_rdr2_main_storyline.json',
        'type': 'game'
    },
    'rdr2-open': {
        'name': 'RDR2 - Open Ended Mission',
        'env': './conf/env_config_rdr2_open_ended_mission.json',
        'type': 'game'
    },

    # Stardew Valley
    'stardew-shopping': {
        'name': 'Stardew Valley - Shopping',
        'env': './conf/env_config_stardew_shopping.json',
        'type': 'game'
    },
    'stardew-farming': {
        'name': 'Stardew Valley - Farm Clearup',
        'env': './conf/env_config_stardew_farm_clearup.json',
        'type': 'game'
    },
    'stardew-cultivation': {
        'name': 'Stardew Valley - Cultivation',
        'env': './conf/env_config_stardew_cultivation.json',
        'type': 'game'
    },

    # Dealer's Life 2
    'dealers': {
        'name': "Dealer's Life 2",
        'env': './conf/env_config_dealers.json',
        'type': 'game'
    },

    # Software Applications
    'outlook': {
        'name': 'Microsoft Outlook',
        'env': './conf/env_config_outlook.json',
        'type': 'app'
    },
    'chrome': {
        'name': 'Google Chrome',
        'env': './conf/env_config_chrome.json',
        'type': 'app'
    },
    'capcut': {
        'name': 'Capcut',
        'env': './conf/env_config_capcut.json',
        'type': 'app'
    },
    'feishu': {
        'name': 'Feishu',
        'env': './conf/env_config_feishu.json',
        'type': 'app'
    },
    'xiuxiu': {
        'name': 'Meitu Xiuxiu',
        'env': './conf/env_config_xiuxiu.json',
        'type': 'app'
    }
}

# LLM provider configurations
LLM_CONFIGS = {
    'openai': {
        'llm': './conf/openai_config.json',
        'embed': './conf/openai_config.json'
    },
    'claude': {
        'llm': './conf/claude_config.json',
        'embed': './conf/openai_config.json'  # Still use OpenAI for embeddings
    },
    'claude-aws': {
        'llm': './conf/restful_claude_config.json',
        'embed': './conf/openai_config.json'
    }
}


def list_available_configs():
    """List all available game/app configurations."""
    print("\n🎮 Available Games:")
    print("=" * 50)
    for key, config in CONFIGS.items():
        if config['type'] == 'game':
            print(f"  {key:20s} - {config['name']}")

    print("\n📱 Available Applications:")
    print("=" * 50)
    for key, config in CONFIGS.items():
        if config['type'] == 'app':
            print(f"  {key:20s} - {config['name']}")

    print("\n💡 LLM Providers:")
    print("=" * 50)
    for key in LLM_CONFIGS.keys():
        print(f"  {key}")

    print("\nUsage: python run.py <game/app> [--llm <provider>]")
    print("Example: python run.py skylines --llm openai\n")


def validate_config_files(llm_config, embed_config, env_config):
    """Validate that all config files exist."""
    missing = []

    if not os.path.exists(llm_config):
        missing.append(f"LLM config: {llm_config}")
    if not os.path.exists(embed_config):
        missing.append(f"Embedding config: {embed_config}")
    if not os.path.exists(env_config):
        missing.append(f"Environment config: {env_config}")

    if missing:
        print("❌ Missing configuration files:")
        for m in missing:
            print(f"   - {m}")
        print("\n💡 Tip: Run 'python setup.py' to set up your environment")
        sys.exit(1)


def validate_env_file():
    """Check if .env file exists with API keys."""
    if not os.path.exists('.env'):
        print("⚠️  Warning: No .env file found!")
        print("   API keys are required to run Cradle.")
        print("   Run 'python setup.py' to configure your API keys.\n")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Simplified Cradle runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'game',
        nargs='?',
        choices=list(CONFIGS.keys()),
        help='Game or application to run'
    )

    parser.add_argument(
        '--llm',
        choices=list(LLM_CONFIGS.keys()),
        default='openai',
        help='LLM provider to use (default: openai)'
    )

    parser.add_argument(
        '--task-id',
        type=int,
        help='Specific task ID to run (from environment config)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available games and applications'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print the command that would be executed without running it'
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        list_available_configs()
        sys.exit(0)

    # Require game argument if not listing
    if not args.game:
        parser.print_help()
        print("\n" + "=" * 50)
        list_available_configs()
        sys.exit(1)

    # Get configurations
    game_config = CONFIGS[args.game]
    llm_config = LLM_CONFIGS[args.llm]

    llm_provider_config = llm_config['llm']
    embed_provider_config = llm_config['embed']
    env_config = game_config['env']

    # Validate files exist
    validate_config_files(llm_provider_config, embed_provider_config, env_config)
    validate_env_file()

    # Build command
    cmd_parts = [
        'python',
        'runner.py',
        '--llmProviderConfig', llm_provider_config,
        '--embedProviderConfig', embed_provider_config,
        '--envConfig', env_config
    ]

    # Print info
    print("\n" + "=" * 60)
    print(f"🚀 Launching Cradle")
    print("=" * 60)
    print(f"Environment:  {game_config['name']}")
    print(f"LLM Provider: {args.llm}")
    print(f"Config:       {env_config}")
    if args.task_id:
        print(f"Task ID:      {args.task_id}")
    print("=" * 60 + "\n")

    if args.dry_run:
        print("Dry run - would execute:")
        print(" ".join(cmd_parts))
        sys.exit(0)

    # Import and run
    try:
        from cradle.config import Config
        from cradle.log import Logger

        config = Config()
        logger = Logger()

        # Load environment config
        config.load_env_config(env_config)
        config.set_fixed_seed()

        # Import the main function
        from runner import main as runner_main

        # Create args object for runner
        class RunnerArgs:
            def __init__(self):
                self.llmProviderConfig = llm_provider_config
                self.embedProviderConfig = embed_provider_config
                self.envConfig = env_config

        runner_args = RunnerArgs()

        # Run!
        runner_main(runner_args)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
