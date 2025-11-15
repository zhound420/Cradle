"""Ollama local LLM provider.

Ollama provides a local LLM server with OpenAI-compatible API.
- Default endpoint: http://localhost:11434
- Supports various models: llama3.2-vision, llava, mistral, etc.
- Free and runs locally
"""

import os
import requests
from typing import Any, Dict
from openai import OpenAI

from cradle.provider.llm.openai import OpenAIProvider
from cradle.config import Config
from cradle.log import Logger
from cradle.utils.json_utils import load_json
from cradle.utils.file_utils import assemble_project_path

config = Config()
logger = Logger()

# Ollama-specific config keys
PROVIDER_SETTING_BASE_URL = "base_url"
PROVIDER_SETTING_COMP_MODEL = "comp_model"
PROVIDER_SETTING_EMB_MODEL = "emb_model"


class OllamaProvider(OpenAIProvider):
    """Ollama provider using OpenAI-compatible API."""

    def __init__(self) -> None:
        """Initialize Ollama provider."""
        super().__init__()
        self.base_url = "http://localhost:11434/v1"  # Default Ollama endpoint
        self.provider_name = "Ollama"


    def init_provider(self, provider_cfg) -> None:
        """Initialize provider with config.

        Args:
            provider_cfg: Path to config file or dict
        """
        self.provider_cfg = self._parse_config(provider_cfg)


    def _parse_config(self, provider_cfg) -> dict:
        """Parse Ollama config.

        Config format:
        {
            "base_url": "http://localhost:11434/v1",  // Optional, defaults to localhost
            "comp_model": "llama3.2-vision",          // Model for completion
            "emb_model": "nomic-embed-text"           // Model for embeddings
        }
        """
        conf_dict = dict()

        if isinstance(provider_cfg, dict):
            conf_dict = provider_cfg
        else:
            path = assemble_project_path(provider_cfg)
            conf_dict = load_json(path)

        # Get base URL (default to localhost)
        self.base_url = conf_dict.get(PROVIDER_SETTING_BASE_URL, "http://localhost:11434/v1")

        # Get models
        self.llm_model = conf_dict.get(PROVIDER_SETTING_COMP_MODEL, "llama3.2-vision")
        self.embedding_model = conf_dict.get(PROVIDER_SETTING_EMB_MODEL, "nomic-embed-text")

        # Create OpenAI client pointing to Ollama
        # Ollama doesn't require API key, but OpenAI client needs one
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="ollama"  # Dummy key, Ollama ignores it
        )

        logger.write(f"Initialized Ollama provider:")
        logger.write(f"  Base URL: {self.base_url}")
        logger.write(f"  LLM Model: {self.llm_model}")
        logger.write(f"  Embedding Model: {self.embedding_model}")

        # Check if Ollama is running
        if not self._check_server_running():
            logger.warn(f"⚠️  Ollama server not detected at {self.base_url}")
            logger.warn("   Make sure Ollama is running:")
            logger.warn("   1. Install: https://ollama.com")
            logger.warn("   2. Pull model: ollama pull llama3.2-vision")
            logger.warn("   3. Server starts automatically")

        return conf_dict


    def _check_server_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            # Try to connect to Ollama API
            base = self.base_url.replace('/v1', '')
            response = requests.get(f"{base}/api/tags", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


    def list_models(self) -> list:
        """List available models in Ollama.

        Returns:
            List of model names
        """
        try:
            base = self.base_url.replace('/v1', '')
            response = requests.get(f"{base}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []


    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry.

        Args:
            model_name: Name of model to pull (e.g., "llama3.2-vision")

        Returns:
            True if successful
        """
        try:
            import subprocess
            logger.write(f"Pulling Ollama model: {model_name}")
            result = subprocess.run(
                ['ollama', 'pull', model_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
