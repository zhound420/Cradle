#!/usr/bin/env python3
"""
Provider management CLI tool.

Easily manage and switch between LLM providers.

Usage:
    python providers.py                 # Show status of all providers
    python providers.py --list          # List available providers
    python providers.py --select        # Interactive provider selection
    python providers.py --check ollama  # Check specific provider
    python providers.py --set-default ollama  # Set default provider

Examples:
    # See what providers are available
    python providers.py --list

    # Pick a provider interactively
    python providers.py --select

    # Check if Ollama is running
    python providers.py --check ollama

    # Set LM Studio as default
    python providers.py --set-default lmstudio
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from common.provider_manager import ProviderManager


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Manage LLM providers for Cradle',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all providers with status'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show detailed provider status'
    )

    parser.add_argument(
        '--select',
        action='store_true',
        help='Interactive provider selection'
    )

    parser.add_argument(
        '--set-default',
        type=str,
        metavar='PROVIDER',
        help='Set default provider (openai, claude, ollama, lmstudio, vllm)'
    )

    parser.add_argument(
        '--check',
        type=str,
        metavar='PROVIDER',
        help='Check if specific provider is available'
    )

    parser.add_argument(
        '--estimate-cost',
        type=int,
        nargs=2,
        metavar=('PROVIDER', 'TOKENS'),
        help='Estimate cost for provider and token count'
    )

    parser.add_argument(
        '--configure-endpoint',
        type=str,
        metavar='PROVIDER',
        help='Configure custom endpoint for local provider (ollama, lmstudio, vllm)'
    )

    args = parser.parse_args()

    manager = ProviderManager()

    # If no arguments, show status
    if len(sys.argv) == 1:
        manager.print_status(verbose=False)
        sys.exit(0)

    # Handle arguments
    if args.list or args.status:
        manager.print_status(verbose=args.status)

    elif args.select:
        selected = manager.interactive_select_provider()
        if selected:
            manager.set_default_provider(selected)
            provider_name = manager.PROVIDERS[selected].name
            print(f"\n✅ Set {provider_name} as default provider")
            print(f"\nYou can now run:")
            print(f"  python run.py skylines  # Will use {provider_name}")
        else:
            print("\n❌ No provider selected")

    elif args.set_default:
        provider_key = args.set_default.lower()
        if provider_key in manager.PROVIDERS:
            manager.set_default_provider(provider_key)
            provider_name = manager.PROVIDERS[provider_key].name
            print(f"\n✅ Set {provider_name} as default provider")
        else:
            print(f"\n❌ Unknown provider: {provider_key}")
            print(f"Available: {', '.join(manager.PROVIDERS.keys())}")
            sys.exit(1)

    elif args.check:
        provider_key = args.check.lower()
        if provider_key in manager.PROVIDERS:
            provider = manager.PROVIDERS[provider_key]
            available, msg = manager.check_provider_available(provider_key)

            print(f"\n{'✅' if available else '❌'} {provider.name}")
            print(f"Status: {msg}")

            if not available:
                print(f"\nTo use {provider.name}:")
                if provider.requires_key:
                    print(f"  1. Get API key from provider")
                    print(f"  2. Add {provider.env_var} to .env file")
                    print(f"  3. Run 'python setup.py --keys-only'")
                else:
                    print(f"  1. Install {provider.name}")
                    print(f"  2. Start the server")
                    if provider.base_url:
                        print(f"  3. Server should run at {provider.base_url}")
        else:
            print(f"\n❌ Unknown provider: {provider_key}")
            print(f"Available: {', '.join(manager.PROVIDERS.keys())}")
            sys.exit(1)

    elif args.estimate_cost:
        provider_key = args.estimate_cost[0].lower()
        num_tokens = args.estimate_cost[1]

        if provider_key in manager.PROVIDERS:
            cost, description = manager.estimate_cost(provider_key, num_tokens)
            provider_name = manager.PROVIDERS[provider_key].name

            print(f"\n💰 Cost Estimate for {provider_name}")
            print(f"   {description}")

            if cost == 0:
                print(f"   ✅ FREE - running locally!")
            else:
                print(f"   ⚠️  This will cost real money")
        else:
            print(f"\n❌ Unknown provider: {provider_key}")
            sys.exit(1)

    elif args.configure_endpoint:
        from common.local_llm import (configure_provider_endpoint, save_provider_config,
                                      select_model_interactive, list_ollama_models,
                                      get_lmstudio_models, is_vision_model)
        import requests

        provider_key = args.configure_endpoint.lower()

        # Only allow local providers
        local_providers = {
            'ollama': ('Ollama', 'http://localhost:11434', 11434, '/api/tags', 'llama3.2-vision'),
            'lmstudio': ('LM Studio', 'http://localhost:1234', 1234, '/v1/models', 'local-model'),
            'vllm': ('vLLM', 'http://localhost:8000', 8000, '/v1/models', 'local-model')
        }

        if provider_key not in local_providers:
            print(f"\n❌ Can only configure local providers: {', '.join(local_providers.keys())}")
            sys.exit(1)

        name, default_url, default_port, endpoint, default_model = local_providers[provider_key]

        print(f"\n🔧 Configure {name} Endpoint")
        print("=" * 60)

        result = configure_provider_endpoint(
            provider_key=provider_key,
            provider_name=name,
            default_url=default_url,
            default_port=default_port,
            endpoint_check=endpoint
        )

        if result['configured']:
            base_url = result['base_url']

            # Try to detect available models
            available_models = []
            selected_model = default_model

            try:
                print(f"\n🔍 Detecting available models...")
                if provider_key == 'ollama':
                    # Ollama uses different endpoint for listing
                    available_models = list_ollama_models()
                elif provider_key == 'lmstudio' or provider_key == 'vllm':
                    available_models = get_lmstudio_models(base_url)

                if available_models:
                    print(f"   Found {len(available_models)} model(s)")
                    selected_model = select_model_interactive(name, available_models, default_model)
                else:
                    print(f"   No models detected, using default: {default_model}")

            except Exception as e:
                print(f"   Could not detect models: {str(e)[:50]}")
                print(f"   Using default: {default_model}")

            # Prepare config data based on provider
            if provider_key == 'ollama':
                config_data = {
                    "base_url": f"{base_url}/v1",
                    "comp_model": selected_model,
                    "emb_model": "nomic-embed-text"
                }
            elif provider_key == 'lmstudio':
                config_data = {
                    "base_url": f"{base_url}/v1",
                    "comp_model": selected_model,
                    "emb_model": "nomic-embed-text"
                }
            elif provider_key == 'vllm':
                config_data = {
                    "base_url": f"{base_url}/v1",
                    "comp_model": selected_model,
                    "emb_model": "nomic-embed-text"
                }

            save_provider_config(provider_key, config_data)

            # Show summary with vision warning
            print(f"\n✅ {name} configured successfully!")
            print(f"   Model: {selected_model}")

            if not is_vision_model(selected_model):
                print(f"\n   ⚠️  WARNING: This model may not support vision!")
                print(f"   Cradle requires vision models to process game screenshots")

            print(f"\n   Test with: python providers.py --check {provider_key}")
        else:
            print(f"\n   Configuration cancelled")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
