"""Local LLM server detection and management utilities."""

import requests
import subprocess
import shutil
import json
import os
from pathlib import Path
from typing import Tuple, List, Optional, Dict


def check_ollama_installed() -> bool:
    """Check if Ollama CLI is installed."""
    return shutil.which('ollama') is not None


def check_ollama_running(base_url: str = "http://localhost:11434") -> Tuple[bool, str]:
    """Check if Ollama server is running.

    Args:
        base_url: Ollama server URL

    Returns:
        Tuple of (is_running, message)
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            if models:
                return True, f"Running with {len(models)} model(s): {', '.join(models[:3])}"
            return True, "Running (no models loaded)"
        return False, "Server responded but returned error"
    except requests.exceptions.ConnectionError:
        return False, "Not running"
    except requests.exceptions.Timeout:
        return False, "Timeout (server may be starting)"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"


def list_ollama_models() -> List[str]:
    """List available Ollama models.

    Returns:
        List of model names
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except:
        return []


def pull_ollama_model(model_name: str) -> Tuple[bool, str]:
    """Pull an Ollama model.

    Args:
        model_name: Model to pull (e.g., "llama3.2-vision")

    Returns:
        Tuple of (success, message)
    """
    if not check_ollama_installed():
        return False, "Ollama CLI not installed"

    try:
        print(f"Pulling Ollama model: {model_name}")
        print("This may take several minutes...")

        result = subprocess.run(
            ['ollama', 'pull', model_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )

        if result.returncode == 0:
            return True, f"Successfully pulled {model_name}"
        else:
            return False, f"Failed: {result.stderr[:100]}"

    except subprocess.TimeoutExpired:
        return False, "Timeout (model too large or slow connection)"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def check_lmstudio_running(base_url: str = "http://localhost:1234") -> Tuple[bool, str]:
    """Check if LM Studio server is running.

    Args:
        base_url: LM Studio server URL

    Returns:
        Tuple of (is_running, message)
    """
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = [m['id'] for m in data.get('data', [])]
            if models:
                return True, f"Running with model(s): {', '.join(models)}"
            return True, "Running (no models loaded)"
        return False, "Server responded but returned error"
    except requests.exceptions.ConnectionError:
        return False, "Not running"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"


def get_lmstudio_models(base_url: str = "http://localhost:1234") -> List[str]:
    """Get list of loaded models in LM Studio.

    Args:
        base_url: LM Studio server URL

    Returns:
        List of model IDs
    """
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['id'] for model in data.get('data', [])]
        return []
    except:
        return []


def detect_local_llms() -> dict:
    """Detect all available local LLM servers.

    Returns:
        Dict with server status information
    """
    result = {
        'ollama': {
            'installed': check_ollama_installed(),
            'running': False,
            'message': '',
            'models': []
        },
        'lmstudio': {
            'running': False,
            'message': '',
            'models': []
        }
    }

    # Check Ollama
    if result['ollama']['installed']:
        running, msg = check_ollama_running()
        result['ollama']['running'] = running
        result['ollama']['message'] = msg
        if running:
            result['ollama']['models'] = list_ollama_models()

    # Check LM Studio
    running, msg = check_lmstudio_running()
    result['lmstudio']['running'] = running
    result['lmstudio']['message'] = msg
    if running:
        result['lmstudio']['models'] = get_lmstudio_models()

    return result


def interactive_ollama_setup() -> bool:
    """Interactive setup for Ollama.

    Returns:
        True if setup successful
    """
    print("\n🦙 Ollama Setup")
    print("=" * 60)

    # Check if installed
    if not check_ollama_installed():
        print("❌ Ollama is not installed")
        print("\nInstall Ollama:")
        print("  • Visit: https://ollama.com")
        print("  • Download and install for your OS")
        print("  • Server starts automatically after install")
        return False

    print("✓ Ollama is installed")

    # Check if running
    running, msg = check_ollama_running()
    print(f"  Status: {msg}")

    if not running:
        print("\n⚠️  Ollama server is not running")
        print("   Try: ollama serve")
        return False

    # Check models
    models = list_ollama_models()
    if not models:
        print("\n📦 No models installed")
        print("   Recommended models:")
        print("   • llama3.2-vision (11GB) - Vision support for games")
        print("   • llava (4.7GB) - Smaller vision model")
        print("   • mistral (4.1GB) - Fast text model")

        choice = input("\nPull llama3.2-vision now? (y/N): ").strip().lower()
        if choice == 'y':
            success, msg = pull_ollama_model("llama3.2-vision")
            print(f"\n{msg}")
            return success
        return False
    else:
        print(f"\n✓ {len(models)} model(s) available:")
        for model in models[:5]:
            print(f"   • {model}")

    return True


def interactive_lmstudio_setup() -> bool:
    """Interactive setup for LM Studio.

    Returns:
        True if setup successful
    """
    print("\n🎨 LM Studio Setup")
    print("=" * 60)

    running, msg = check_lmstudio_running()

    if not running:
        print("❌ LM Studio server is not running")
        print("\nSetup LM Studio:")
        print("  1. Download from: https://lmstudio.ai")
        print("  2. Open LM Studio")
        print("  3. Download a model (e.g., LLaVA for vision)")
        print("  4. Go to Developer → Start Server")
        print("  5. Keep LM Studio running")
        return False

    print(f"✓ LM Studio is running: {msg}")

    # Check models
    models = get_lmstudio_models()
    if models:
        print(f"\n✓ Loaded model(s):")
        for model in models:
            print(f"   • {model}")
    else:
        print("\n⚠️  No models loaded")
        print("   Load a model in LM Studio GUI first")
        return False

    return True


def validate_base_url(base_url: str) -> str:
    """Validate and normalize a base URL.

    Args:
        base_url: URL to validate

    Returns:
        Normalized URL

    Raises:
        ValueError: If URL is invalid
    """
    base_url = base_url.strip()

    # Add http:// if no protocol specified
    if not base_url.startswith(('http://', 'https://')):
        base_url = f'http://{base_url}'

    # Remove trailing slash
    base_url = base_url.rstrip('/')

    # Basic validation
    if not base_url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")

    return base_url


def prompt_for_base_url(provider_name: str, default_url: str, endpoint_check: str = None) -> Optional[str]:
    """Prompt user for a provider's base URL.

    Args:
        provider_name: Name of the provider (e.g., "Ollama")
        default_url: Default URL (e.g., "http://localhost:11434")
        endpoint_check: Optional endpoint to test (e.g., "/api/tags")

    Returns:
        Base URL or None if user skips
    """
    print(f"\n📍 {provider_name} Server Location")
    print(f"   Default: {default_url}")
    print(f"   Examples:")
    print(f"     • localhost:11434 (local server)")
    print(f"     • 192.168.1.100:11434 (LAN server)")
    print(f"     • https://my-server.com:11434 (remote server)")

    while True:
        user_input = input(f"\n   Enter URL (or press Enter for default): ").strip()

        # Use default if empty
        if not user_input:
            base_url = default_url
            print(f"   Using default: {base_url}")
        else:
            try:
                base_url = validate_base_url(user_input)
                print(f"   Normalized to: {base_url}")
            except ValueError as e:
                print(f"   ❌ Invalid URL: {e}")
                continue

        # Test connection if endpoint provided
        if endpoint_check:
            print(f"   Testing connection...")
            try:
                test_url = f"{base_url}{endpoint_check}"
                response = requests.get(test_url, timeout=3)
                if response.status_code == 200:
                    print(f"   ✅ Connection successful!")
                    return base_url
                else:
                    print(f"   ⚠️  Server responded with status {response.status_code}")
                    retry = input("   Try a different URL? (y/N): ").strip().lower()
                    if retry != 'y':
                        return base_url
            except requests.exceptions.ConnectionError:
                print(f"   ❌ Could not connect to {base_url}")
                retry = input("   Try a different URL? (y/N): ").strip().lower()
                if retry != 'y':
                    return None
            except Exception as e:
                print(f"   ⚠️  Error testing connection: {str(e)[:50]}")
                use_anyway = input("   Use this URL anyway? (y/N): ").strip().lower()
                if use_anyway == 'y':
                    return base_url
        else:
            return base_url

    return None


def configure_provider_endpoint(provider_key: str, provider_name: str,
                                default_url: str, default_port: int,
                                endpoint_check: str = None) -> Dict[str, str]:
    """Configure a local provider's endpoint interactively.

    Args:
        provider_key: Provider key (e.g., "ollama")
        provider_name: Display name (e.g., "Ollama")
        default_url: Default base URL
        default_port: Default port number
        endpoint_check: Optional endpoint to test connectivity

    Returns:
        Dict with 'base_url' and 'configured' status
    """
    print(f"\n{'=' * 60}")
    print(f"Configure {provider_name}")
    print(f"{'=' * 60}")

    # Ask if they want to configure this provider
    print(f"\nDo you want to use {provider_name}?")
    print(f"   • Local inference (no API costs)")
    print(f"   • Default: {default_url}")

    configure = input(f"\nConfigure {provider_name}? (y/N): ").strip().lower()

    if configure != 'y':
        return {'configured': False, 'base_url': default_url}

    # Get base URL
    base_url = prompt_for_base_url(provider_name, default_url, endpoint_check)

    if base_url:
        return {'configured': True, 'base_url': base_url}
    else:
        print(f"   Skipping {provider_name} configuration")
        return {'configured': False, 'base_url': default_url}


def save_provider_config(provider_key: str, config_data: Dict, conf_dir: str = "./conf") -> bool:
    """Save provider configuration to JSON file.

    Args:
        provider_key: Provider key (e.g., "ollama")
        config_data: Configuration dictionary
        conf_dir: Configuration directory path

    Returns:
        True if successful
    """
    try:
        conf_path = Path(conf_dir)
        conf_path.mkdir(exist_ok=True)

        config_file = conf_path / f"{provider_key}_config.json"

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)

        print(f"   ✅ Saved configuration to {config_file}")
        return True

    except Exception as e:
        print(f"   ❌ Error saving config: {e}")
        return False


def configure_all_local_providers(conf_dir: str = "./conf") -> Dict[str, bool]:
    """Configure all local LLM providers interactively.

    Args:
        conf_dir: Configuration directory

    Returns:
        Dict mapping provider keys to configuration success status
    """
    print("\n" + "=" * 60)
    print("🔧 Local LLM Provider Configuration")
    print("=" * 60)
    print("\nConfigure endpoints for local LLM providers.")
    print("These can run on localhost or remote servers.")
    print("Press Ctrl+C to skip any provider.")

    results = {}

    # Ollama
    try:
        ollama_config = configure_provider_endpoint(
            provider_key="ollama",
            provider_name="Ollama",
            default_url="http://localhost:11434",
            default_port=11434,
            endpoint_check="/api/tags"
        )

        if ollama_config['configured']:
            config_data = {
                "base_url": f"{ollama_config['base_url']}/v1",
                "comp_model": "llama3.2-vision",
                "emb_model": "nomic-embed-text"
            }
            results['ollama'] = save_provider_config("ollama", config_data, conf_dir)
        else:
            results['ollama'] = False

    except KeyboardInterrupt:
        print("\n   Skipping Ollama")
        results['ollama'] = False

    # LM Studio
    try:
        lmstudio_config = configure_provider_endpoint(
            provider_key="lmstudio",
            provider_name="LM Studio",
            default_url="http://localhost:1234",
            default_port=1234,
            endpoint_check="/v1/models"
        )

        if lmstudio_config['configured']:
            config_data = {
                "base_url": f"{lmstudio_config['base_url']}/v1",
                "comp_model": "local-model",
                "emb_model": "nomic-embed-text"
            }
            results['lmstudio'] = save_provider_config("lmstudio", config_data, conf_dir)
        else:
            results['lmstudio'] = False

    except KeyboardInterrupt:
        print("\n   Skipping LM Studio")
        results['lmstudio'] = False

    # vLLM
    try:
        vllm_config = configure_provider_endpoint(
            provider_key="vllm",
            provider_name="vLLM",
            default_url="http://localhost:8000",
            default_port=8000,
            endpoint_check="/v1/models"
        )

        if vllm_config['configured']:
            config_data = {
                "base_url": f"{vllm_config['base_url']}/v1",
                "comp_model": "local-model",
                "emb_model": "nomic-embed-text"
            }
            results['vllm'] = save_provider_config("vllm", config_data, conf_dir)
        else:
            results['vllm'] = False

    except KeyboardInterrupt:
        print("\n   Skipping vLLM")
        results['vllm'] = False

    # Summary
    print("\n" + "=" * 60)
    print("Configuration Summary")
    print("=" * 60)
    configured_count = sum(1 for v in results.values() if v)
    print(f"\n✅ Configured {configured_count}/{len(results)} local providers")

    for provider, success in results.items():
        status = "✅ Configured" if success else "⏭️  Skipped"
        print(f"   {provider:12s} - {status}")

    return results


if __name__ == '__main__':
    # Test detection
    print("Detecting local LLM servers...")
    servers = detect_local_llms()

    print("\n" + "=" * 60)
    print("Local LLM Server Status")
    print("=" * 60)

    print("\nOllama:")
    print(f"  Installed: {servers['ollama']['installed']}")
    print(f"  Running: {servers['ollama']['running']}")
    print(f"  Message: {servers['ollama']['message']}")
    if servers['ollama']['models']:
        print(f"  Models: {', '.join(servers['ollama']['models'])}")

    print("\nLM Studio:")
    print(f"  Running: {servers['lmstudio']['running']}")
    print(f"  Message: {servers['lmstudio']['message']}")
    if servers['lmstudio']['models']:
        print(f"  Models: {', '.join(servers['lmstudio']['models'])}")
