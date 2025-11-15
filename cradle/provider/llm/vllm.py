"""vLLM local LLM provider.

vLLM is a high-throughput inference engine with OpenAI-compatible API.
- Default endpoint: http://localhost:8000
- Excellent for serving local models at scale
- Optimized for throughput and low latency
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

# vLLM-specific config keys
PROVIDER_SETTING_BASE_URL = "base_url"
PROVIDER_SETTING_COMP_MODEL = "comp_model"
PROVIDER_SETTING_EMB_MODEL = "emb_model"


class VLLMProvider(OpenAIProvider):
    """vLLM provider using OpenAI-compatible API."""

    def __init__(self) -> None:
        """Initialize vLLM provider."""
        super().__init__()
        self.base_url = "http://localhost:8000/v1"  # Default vLLM endpoint
        self.provider_name = "vLLM"


    def init_provider(self, provider_cfg) -> None:
        """Initialize provider with config.

        Args:
            provider_cfg: Path to config file or dict
        """
        self.provider_cfg = self._parse_config(provider_cfg)


    def _parse_config(self, provider_cfg) -> dict:
        """Parse vLLM config.

        Config format:
        {
            "base_url": "http://localhost:8000/v1",  // Optional, defaults to localhost
            "comp_model": "llama-3.2-vision",        // Model name
            "emb_model": "nomic-embed-text"          // Embedding model
        }
        """
        conf_dict = dict()

        if isinstance(provider_cfg, dict):
            conf_dict = provider_cfg
        else:
            path = assemble_project_path(provider_cfg)
            conf_dict = load_json(path)

        # Get base URL (default to localhost)
        self.base_url = conf_dict.get(PROVIDER_SETTING_BASE_URL, "http://localhost:8000/v1")

        # Get models
        self.llm_model = conf_dict.get(PROVIDER_SETTING_COMP_MODEL, "local-model")
        self.embedding_model = conf_dict.get(PROVIDER_SETTING_EMB_MODEL, "nomic-embed-text")

        # Create OpenAI client pointing to vLLM
        # vLLM doesn't require API key, but OpenAI client needs one
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="vllm"  # Dummy key, vLLM ignores it
        )

        logger.write(f"Initialized vLLM provider:")
        logger.write(f"  Base URL: {self.base_url}")
        logger.write(f"  LLM Model: {self.llm_model}")
        logger.write(f"  Embedding Model: {self.embedding_model}")

        # Check if vLLM is running
        if not self._check_server_running():
            logger.warn(f"⚠️  vLLM server not detected at {self.base_url}")
            logger.warn("   Make sure vLLM is running:")
            logger.warn("   1. Install: pip install vllm")
            logger.warn("   2. Start server:")
            logger.warn("      vllm serve <model-name> --api-key token-abc123")
            logger.warn("   3. Or with specific settings:")
            logger.warn("      python -m vllm.entrypoints.openai.api_server \\")
            logger.warn("        --model facebook/opt-125m \\")
            logger.warn("        --port 8000")

        return conf_dict


    def _check_server_running(self) -> bool:
        """Check if vLLM server is running."""
        try:
            # Try to connect to vLLM API
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


    def list_models(self) -> list:
        """List available models in vLLM.

        Returns:
            List of model IDs
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['id'] for model in data.get('data', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list vLLM models: {e}")
            return []


    def get_server_info(self) -> dict:
        """Get vLLM server information.

        Returns:
            Server info dict
        """
        try:
            # vLLM has a health endpoint
            health_url = self.base_url.replace('/v1', '/health')
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                return response.json()

            # Fallback to models endpoint
            models = self.list_models()
            if models:
                return {
                    'status': 'healthy',
                    'loaded_models': models
                }

            return {}
        except Exception as e:
            logger.error(f"Failed to get server info: {e}")
            return {}
