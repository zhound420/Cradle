"""Dependency management for game-specific requirements."""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Tuple, Optional


class DependencyManager:
    """Manages game-specific dependencies."""

    def __init__(self, game_name: str):
        """Initialize dependency manager for specific game."""
        self.game_name = game_name
        self.system = platform.system().lower()

    def check_groundingdino(self) -> Tuple[bool, str]:
        """Check if GroundingDino is installed (required for RDR2)."""
        try:
            import groundingdino
            return True, "GroundingDino is installed"
        except ImportError:
            return False, "GroundingDino not installed"

    def check_videosubfinder(self) -> Tuple[bool, str]:
        """Check if videosubfinder is available (required for RDR2)."""
        subfinder_path = Path('res/tool/subfinder/VideoSubFinderWXW.exe')

        if subfinder_path.exists():
            return True, f"VideoSubFinder found at {subfinder_path}"
        else:
            return False, f"VideoSubFinder not found at {subfinder_path}"

    def check_torch(self) -> Tuple[bool, str]:
        """Check if PyTorch is installed with CUDA support."""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            version = torch.__version__

            if cuda_available:
                return True, f"PyTorch {version} with CUDA support"
            else:
                return True, f"PyTorch {version} (CPU only - GPU recommended)"
        except ImportError:
            return False, "PyTorch not installed"

    def install_groundingdino(self, verbose: bool = True) -> Tuple[bool, str]:
        """
        Install GroundingDino with dependencies.

        Returns:
            Tuple of (success, message)
        """
        if verbose:
            print("\n📦 Installing GroundingDino...")
            print("   This may take several minutes...\n")

        steps = [
            ("Installing PyTorch with CUDA", [
                sys.executable, '-m', 'pip', 'install',
                'torch==2.1.1+cu118',
                'torchvision==0.16.1+cu118',
                '-f', 'https://download.pytorch.org/whl/torch_stable.html'
            ]),
            ("Downloading GroundingDino weights", self._download_groundingdino_weights),
            ("Downloading BERT model", self._download_bert_model),
            ("Installing GroundingDino", self._install_groundingdino_from_source),
        ]

        for step_name, step_action in steps:
            if verbose:
                print(f"⏳ {step_name}...")

            try:
                if callable(step_action):
                    success, msg = step_action()
                    if not success:
                        return False, f"Failed at '{step_name}': {msg}"
                else:
                    result = subprocess.run(
                        step_action,
                        capture_output=True,
                        text=True,
                        check=True
                    )

                if verbose:
                    print(f"   ✓ {step_name} completed")

            except subprocess.CalledProcessError as e:
                return False, f"Failed at '{step_name}': {e.stderr}"
            except Exception as e:
                return False, f"Failed at '{step_name}': {str(e)}"

        return True, "GroundingDino installed successfully"

    def _download_groundingdino_weights(self) -> Tuple[bool, str]:
        """Download GroundingDino model weights."""
        cache_dir = Path('cache')
        cache_dir.mkdir(exist_ok=True)

        weights_file = cache_dir / 'groundingdino_swinb_cogcoor.pth'

        if weights_file.exists():
            return True, "Weights already downloaded"

        url = "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha2/groundingdino_swinb_cogcoor.pth"

        try:
            import urllib.request
            urllib.request.urlretrieve(url, weights_file)
            return True, "Weights downloaded"
        except Exception as e:
            return False, str(e)

    def _download_bert_model(self) -> Tuple[bool, str]:
        """Download BERT model from Hugging Face."""
        hf_dir = Path('hf')
        hf_dir.mkdir(exist_ok=True)

        try:
            subprocess.run([
                'huggingface-cli', 'download',
                'bert-base-uncased',
                'config.json', 'tokenizer.json', 'vocab.txt',
                'tokenizer_config.json', 'model.safetensors',
                '--cache-dir', str(hf_dir)
            ], check=True, capture_output=True)

            return True, "BERT model downloaded"
        except subprocess.CalledProcessError:
            return False, "Failed to download BERT model (is huggingface-cli installed?)"
        except FileNotFoundError:
            return False, "huggingface-cli not found"

    def _install_groundingdino_from_source(self) -> Tuple[bool, str]:
        """Clone and install GroundingDino from source."""
        parent_dir = Path('..').resolve()
        grounding_dir = parent_dir / 'GroundingDINO'

        # Clone if not exists
        if not grounding_dir.exists():
            try:
                subprocess.run([
                    'git', 'clone',
                    'https://github.com/IDEA-Research/GroundingDINO.git',
                    str(grounding_dir)
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                return False, "Failed to clone GroundingDino repository"

        # Install dependencies
        try:
            requirements_file = grounding_dir / 'requirements.txt'
            if requirements_file.exists():
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    '-r', str(requirements_file)
                ], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            return False, "Failed to install GroundingDino requirements"

        # Install package
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                str(grounding_dir)
            ], check=True, capture_output=True, cwd=str(grounding_dir))
        except subprocess.CalledProcessError:
            return False, "Failed to install GroundingDino package"

        return True, "GroundingDino installed from source"

    def download_videosubfinder(self) -> Tuple[bool, str]:
        """Provide instructions for downloading VideoSubFinder."""
        tool_dir = Path('res/tool/subfinder')
        tool_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy test.srt if it doesn't exist
        test_srt = tool_dir / 'test.srt'
        if not test_srt.exists():
            test_srt.write_text("")

        instructions = f"""
VideoSubFinder must be downloaded manually:

1. Visit: https://sourceforge.net/projects/videosubfinder/
2. Download the latest Windows version
3. Extract all files to: {tool_dir.absolute()}
4. Ensure VideoSubFinderWXW.exe is in the folder

After extraction, copy res/tool/general.cfg to:
  {tool_dir.absolute()}/settings/general.cfg

This will override the default settings with optimized values for game scenarios.
"""

        return False, instructions

    def check_game_dependencies(self) -> List[Tuple[str, bool, str]]:
        """
        Check all dependencies for the current game.

        Returns:
            List of (dependency_name, is_satisfied, message) tuples
        """
        dependencies = []

        if self.game_name in ['rdr2', 'rdr2-story', 'rdr2-open']:
            # RDR2 specific dependencies
            dependencies.append(('PyTorch', *self.check_torch()))
            dependencies.append(('GroundingDino', *self.check_groundingdino()))
            dependencies.append(('VideoSubFinder', *self.check_videosubfinder()))

        # All games need basic dependencies (checked elsewhere)

        return dependencies

    def install_missing_dependencies(self, auto_install: bool = False) -> Tuple[bool, List[str]]:
        """
        Install missing dependencies.

        Args:
            auto_install: If True, install without prompting

        Returns:
            Tuple of (all_installed, error_messages)
        """
        deps = self.check_game_dependencies()
        missing = [(name, msg) for name, satisfied, msg in deps if not satisfied]

        if not missing:
            return True, []

        errors = []

        for dep_name, msg in missing:
            if dep_name == 'GroundingDino':
                if auto_install or self._prompt_install(dep_name):
                    success, install_msg = self.install_groundingdino()
                    if not success:
                        errors.append(f"GroundingDino: {install_msg}")
                else:
                    errors.append(f"GroundingDino: Installation skipped by user")

            elif dep_name == 'VideoSubFinder':
                success, instructions = self.download_videosubfinder()
                errors.append(f"VideoSubFinder: Manual installation required\n{instructions}")

            elif dep_name == 'PyTorch':
                errors.append("PyTorch: Please install manually (see docs/envs/rdr2.md)")

        return len(errors) == 0, errors

    def _prompt_install(self, dep_name: str) -> bool:
        """Prompt user to install a dependency."""
        response = input(f"\n{dep_name} is required. Install now? (y/n): ").lower().strip()
        return response in ['y', 'yes']
