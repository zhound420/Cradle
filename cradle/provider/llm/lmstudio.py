"""LM Studio local LLM provider.

LM Studio provides a local LLM server with GUI and OpenAI-compatible API.
- Default endpoint: http://localhost:1234/v1
- Supports various models loaded through GUI
- Free and runs locally with nice interface
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

# LM Studio-specific config keys
PROVIDER_SETTING_BASE_URL = "base_url"
PROVIDER_SETTING_COMP_MODEL = "comp_model"
PROVIDER_SETTING_EMB_MODEL = "emb_model"


class LMStudioProvider(OpenAIProvider):
    """LM Studio provider using OpenAI-compatible API."""

    def __init__(self) -> None:
        """Initialize LM Studio provider."""
        super().__init__()
        self.base_url = "http://localhost:1234/v1"  # Default LM Studio endpoint
        self.provider_name = "LM Studio"


    def init_provider(self, provider_cfg) -> None:
        """Initialize provider with config.

        Args:
            provider_cfg: Path to config file or dict
        """
        self.provider_cfg = self._parse_config(provider_cfg)


    def _parse_config(self, provider_cfg) -> dict:
        """Parse LM Studio config.

        Config format:
        {
            "base_url": "http://localhost:1234/v1",   // Optional, defaults to localhost
            "comp_model": "loaded-model",             // Model name (or leave auto-detect)
            "emb_model": "nomic-embed-text"           // Embedding model
        }
        """
        conf_dict = dict()

        if isinstance(provider_cfg, dict):
            conf_dict = provider_cfg
        else:
            path = assemble_project_path(provider_cfg)
            conf_dict = load_json(path)

        # Get base URL (default to localhost)
        self.base_url = conf_dict.get(PROVIDER_SETTING_BASE_URL, "http://localhost:1234/v1")

        # Get models (LM Studio auto-detects loaded model if not specified)
        self.llm_model = conf_dict.get(PROVIDER_SETTING_COMP_MODEL, "local-model")
        self.embedding_model = conf_dict.get(PROVIDER_SETTING_EMB_MODEL, "nomic-embed-text")

        # Create OpenAI client pointing to LM Studio
        # LM Studio doesn't require API key, but OpenAI client needs one
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="lm-studio"  # Dummy key, LM Studio ignores it
        )

        logger.write(f"Initialized LM Studio provider:")
        logger.write(f"  Base URL: {self.base_url}")
        logger.write(f"  LLM Model: {self.llm_model}")
        logger.write(f"  Embedding Model: {self.embedding_model}")

        # Check if LM Studio is running
        if not self._check_server_running():
            logger.warn(f"⚠️  LM Studio server not detected at {self.base_url}")
            logger.warn("   Make sure LM Studio is running:")
            logger.warn("   1. Download: https://lmstudio.ai")
            logger.warn("   2. Load a model in the GUI")
            logger.warn("   3. Start server (Developer → Local Server)")
        else:
            # Try to detect loaded model
            loaded_models = self._get_loaded_models()
            if loaded_models:
                logger.write(f"  Loaded models: {', '.join(loaded_models)}")
                # Use first loaded model if none specified
                if self.llm_model == "local-model" and loaded_models:
                    self.llm_model = loaded_models[0]
                    logger.write(f"  Auto-selected model: {self.llm_model}")

        return conf_dict


    def _check_server_running(self) -> bool:
        """Check if LM Studio server is running."""
        try:
            # Try to connect to LM Studio API
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


    def _get_loaded_models(self) -> list:
        """Get list of currently loaded models in LM Studio.

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
            logger.error(f"Failed to get loaded models: {e}")
            return []


    def list_models(self) -> list:
        """List available models in LM Studio.

        Returns:
            List of model names
        """
        return self._get_loaded_models()


    def get_server_info(self) -> dict:
        """Get LM Studio server information.

        Returns:
            Server info dict
        """
        try:
            # LM Studio may have a custom endpoint for server info
            response = requests.get(f"{self.base_url.replace('/v1', '')}/info", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Failed to get server info: {e}")
            return {}
