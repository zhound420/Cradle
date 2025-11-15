"""Provider management and configuration system.

Provides a unified interface for managing all LLM providers:
- OpenAI, Claude, Ollama, LM Studio, vLLM
- Health checks and availability testing
- Provider selection and configuration
- Cost estimation
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    name: str
    type: str  # 'api' or 'local'
    config_file: str
    requires_key: bool
    env_var: Optional[str] = None
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    cost_per_1k_tokens: float = 0.0  # For cost estimation
    supports_vision: bool = False


class ProviderManager:
    """Manages all LLM provider configurations and health checks."""

    # All available providers
    PROVIDERS = {
        'openai': ProviderConfig(
            name='OpenAI',
            type='api',
            config_file='conf/openai_config.json',
            requires_key=True,
            env_var='OA_OPENAI_KEY',
            default_model='gpt-4o-2024-05-13',
            cost_per_1k_tokens=0.015,  # Approximate
            supports_vision=True
        ),
        'claude': ProviderConfig(
            name='Claude (Anthropic)',
            type='api',
            config_file='conf/claude_config.json',
            requires_key=True,
            env_var='OA_CLAUDE_KEY',
            default_model='claude-3-5-sonnet-20241022',
            cost_per_1k_tokens=0.018,
            supports_vision=True
        ),
        'claude-aws': ProviderConfig(
            name='Claude (AWS Bedrock)',
            type='api',
            config_file='conf/restful_claude_config.json',
            requires_key=True,
            env_var='RF_CLAUDE_AK',
            default_model='claude-3-5-sonnet',
            cost_per_1k_tokens=0.018,
            supports_vision=True
        ),
        'ollama': ProviderConfig(
            name='Ollama (Local)',
            type='local',
            config_file='conf/ollama_config.json',
            requires_key=False,
            base_url='http://localhost:11434',
            default_model='llama3.2-vision',
            cost_per_1k_tokens=0.0,
            supports_vision=True
        ),
        'lmstudio': ProviderConfig(
            name='LM Studio (Local)',
            type='local',
            config_file='conf/lmstudio_config.json',
            requires_key=False,
            base_url='http://localhost:1234',
            default_model='local-model',
            cost_per_1k_tokens=0.0,
            supports_vision=True
        ),
        'vllm': ProviderConfig(
            name='vLLM (Local)',
            type='local',
            config_file='conf/vllm_config.json',
            requires_key=False,
            base_url='http://localhost:8000',
            default_model='local-model',
            cost_per_1k_tokens=0.0,
            supports_vision=True
        ),
    }

    def __init__(self):
        """Initialize provider manager."""
        self.config_dir = Path('conf')
        self.preferences_file = Path('.cradle_providers.json')
        self.preferences = self._load_preferences()


    def _load_preferences(self) -> dict:
        """Load user preferences for providers."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'default_provider': None, 'configured_providers': []}


    def _save_preferences(self):
        """Save user preferences."""
        with open(self.preferences_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)


    def get_default_provider(self) -> Optional[str]:
        """Get the default provider key."""
        return self.preferences.get('default_provider')


    def set_default_provider(self, provider_key: str):
        """Set the default provider."""
        if provider_key not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_key}")
        self.preferences['default_provider'] = provider_key
        if provider_key not in self.preferences['configured_providers']:
            self.preferences['configured_providers'].append(provider_key)
        self._save_preferences()


    def check_provider_configured(self, provider_key: str) -> Tuple[bool, str]:
        """Check if a provider is configured.

        Returns:
            (is_configured, message)
        """
        if provider_key not in self.PROVIDERS:
            return False, f"Unknown provider: {provider_key}"

        provider = self.PROVIDERS[provider_key]

        # Check config file exists
        if not Path(provider.config_file).exists():
            return False, f"Config file not found: {provider.config_file}"

        # Check API key if required
        if provider.requires_key and provider.env_var:
            key = os.getenv(provider.env_var)
            if not key:
                return False, f"API key not found: {provider.env_var}"
            return True, f"Configured with API key"

        return True, "Configuration found"


    def check_provider_available(self, provider_key: str) -> Tuple[bool, str]:
        """Check if a provider is available (can be used right now).

        Returns:
            (is_available, message)
        """
        if provider_key not in self.PROVIDERS:
            return False, f"Unknown provider: {provider_key}"

        provider = self.PROVIDERS[provider_key]

        # First check if configured
        configured, msg = self.check_provider_configured(provider_key)
        if not configured:
            return False, msg

        # For API providers, just check if key exists
        if provider.type == 'api':
            return True, "API key configured"

        # For local providers, check if server is running
        if provider.base_url:
            try:
                if 'ollama' in provider_key:
                    response = requests.get(f"{provider.base_url}/api/tags", timeout=2)
                elif 'lmstudio' in provider_key:
                    response = requests.get(f"{provider.base_url}/v1/models", timeout=2)
                elif 'vllm' in provider_key:
                    response = requests.get(f"{provider.base_url}/v1/models", timeout=2)
                else:
                    response = requests.get(provider.base_url, timeout=2)

                if response.status_code == 200:
                    return True, "Server running"
                return False, f"Server error: {response.status_code}"
            except requests.exceptions.ConnectionError:
                return False, "Server not running"
            except requests.exceptions.Timeout:
                return False, "Server timeout"
            except Exception as e:
                return False, f"Error: {str(e)[:50]}"

        return True, "Ready"


    def list_providers(self, show_all: bool = True) -> List[Tuple[str, ProviderConfig, bool, str]]:
        """List all providers with their status.

        Args:
            show_all: If False, only show configured providers

        Returns:
            List of (key, config, is_available, status_message)
        """
        results = []
        for key, config in self.PROVIDERS.items():
            if not show_all and key not in self.preferences.get('configured_providers', []):
                continue

            available, msg = self.check_provider_available(key)
            results.append((key, config, available, msg))

        return results


    def estimate_cost(self, provider_key: str, num_tokens: int) -> Tuple[float, str]:
        """Estimate cost for using a provider.

        Args:
            provider_key: Provider to estimate for
            num_tokens: Number of tokens to process

        Returns:
            (cost_usd, description)
        """
        if provider_key not in self.PROVIDERS:
            return 0.0, "Unknown provider"

        provider = self.PROVIDERS[provider_key]
        cost = (num_tokens / 1000) * provider.cost_per_1k_tokens

        if cost == 0:
            return 0.0, "Free (local)"
        else:
            return cost, f"${cost:.4f} for {num_tokens:,} tokens"


    def get_provider_info(self, provider_key: str) -> Optional[ProviderConfig]:
        """Get information about a provider."""
        return self.PROVIDERS.get(provider_key)


    def interactive_select_provider(self) -> Optional[str]:
        """Interactive provider selection.

        Returns:
            Selected provider key or None
        """
        print("\n" + "=" * 60)
        print("🤖 LLM Provider Selection")
        print("=" * 60)

        # Show all providers with status
        providers = self.list_providers(show_all=True)

        print("\n📋 Available Providers:\n")

        for i, (key, config, available, msg) in enumerate(providers, 1):
            status = "✓" if available else "✗"
            cost = "FREE" if config.cost_per_1k_tokens == 0 else f"~${config.cost_per_1k_tokens}/1K tokens"
            provider_type = "🌐 API" if config.type == 'api' else "💻 Local"

            print(f"{i}. [{status}] {config.name:25s} {provider_type:12s} {cost:20s}")
            print(f"     Status: {msg}")
            if not available and config.requires_key:
                print(f"     Setup: Add {config.env_var} to .env file")
            elif not available and config.type == 'local':
                print(f"     Setup: Install and run {config.name}")
            print()

        # Get selection
        while True:
            choice = input("Select provider (1-{}) or 'q' to quit: ".format(len(providers))).strip()

            if choice.lower() == 'q':
                return None

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(providers):
                    selected_key = providers[idx][0]
                    selected_config = providers[idx][1]
                    is_available = providers[idx][2]

                    if not is_available:
                        print(f"\n⚠️  {selected_config.name} is not currently available.")
                        cont = input("Select anyway? (y/N): ").strip().lower()
                        if cont != 'y':
                            continue

                    return selected_key
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number or 'q'.")


    def print_status(self, verbose: bool = False):
        """Print status of all providers."""
        print("\n" + "=" * 60)
        print("🤖 LLM Provider Status")
        print("=" * 60)

        default = self.get_default_provider()
        if default:
            print(f"\nDefault provider: {self.PROVIDERS[default].name}")
        else:
            print("\nNo default provider set")

        print("\n📋 All Providers:\n")

        providers = self.list_providers(show_all=True)

        for key, config, available, msg in providers:
            status_icon = "✓" if available else "✗"
            is_default = " (DEFAULT)" if key == default else ""

            print(f"{status_icon} {config.name:30s} {config.type.upper():8s}{is_default}")
            print(f"   Status: {msg}")

            if verbose:
                print(f"   Config: {config.config_file}")
                if config.default_model:
                    print(f"   Model:  {config.default_model}")
                if config.cost_per_1k_tokens > 0:
                    print(f"   Cost:   ~${config.cost_per_1k_tokens}/1K tokens")
                else:
                    print(f"   Cost:   FREE")
            print()


def main():
    """CLI for provider management."""
    import argparse

    parser = argparse.ArgumentParser(description='Manage LLM providers')
    parser.add_argument('--list', action='store_true', help='List all providers')
    parser.add_argument('--status', action='store_true', help='Show detailed status')
    parser.add_argument('--select', action='store_true', help='Interactive provider selection')
    parser.add_argument('--set-default', type=str, help='Set default provider')
    parser.add_argument('--check', type=str, help='Check specific provider')

    args = parser.parse_args()

    manager = ProviderManager()

    if args.list or args.status:
        manager.print_status(verbose=args.status)
    elif args.select:
        selected = manager.interactive_select_provider()
        if selected:
            manager.set_default_provider(selected)
            print(f"\n✓ Set {manager.PROVIDERS[selected].name} as default provider")
    elif args.set_default:
        if args.set_default in manager.PROVIDERS:
            manager.set_default_provider(args.set_default)
            print(f"\n✓ Set {manager.PROVIDERS[args.set_default].name} as default")
        else:
            print(f"\n✗ Unknown provider: {args.set_default}")
    elif args.check:
        if args.check in manager.PROVIDERS:
            available, msg = manager.check_provider_available(args.check)
            status = "✓ Available" if available else "✗ Not available"
            print(f"\n{status}: {msg}")
        else:
            print(f"\n✗ Unknown provider: {args.check}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
