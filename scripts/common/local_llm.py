"""Local LLM server detection and management utilities."""

import requests
import subprocess
import shutil
from typing import Tuple, List, Optional


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
