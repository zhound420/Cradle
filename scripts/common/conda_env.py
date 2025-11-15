"""Conda environment management utilities."""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version() -> bool:
    """Check if Python version is 3.10."""
    version = sys.version_info
    if version.major == 3 and version.minor == 10:
        return True
    return False


def is_conda_available() -> bool:
    """Check if conda is available in the system."""
    return shutil.which('conda') is not None


def is_in_conda_env() -> bool:
    """Check if currently in a conda environment."""
    return os.environ.get('CONDA_DEFAULT_ENV') is not None


def get_current_env_name() -> str:
    """Get the name of the current conda environment."""
    return os.environ.get('CONDA_DEFAULT_ENV', 'base')


def check_cradle_env_exists() -> bool:
    """Check if cradle-dev environment exists."""
    if not is_conda_available():
        return False

    try:
        result = subprocess.run(
            ['conda', 'env', 'list'],
            capture_output=True,
            text=True,
            check=True
        )
        return 'cradle-dev' in result.stdout
    except subprocess.CalledProcessError:
        return False


def create_conda_env():
    """Create cradle-dev conda environment."""
    print("\n📦 Creating conda environment: cradle-dev")
    print("-" * 60)

    try:
        subprocess.run(
            ['conda', 'create', '--name', 'cradle-dev', 'python=3.10', '-y'],
            check=True
        )
        print("✓ Environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create environment: {e}")
        return False


def install_requirements():
    """Install requirements.txt in current environment."""
    print("\n📚 Installing dependencies")
    print("-" * 60)

    requirements_file = Path(__file__).parent.parent.parent / 'requirements.txt'

    if not requirements_file.exists():
        print(f"✗ requirements.txt not found at {requirements_file}")
        return False

    try:
        # Use pip to install requirements
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            check=True
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def install_spacy_model():
    """Install spaCy language model for OCR."""
    print("\n🔤 Installing spaCy language model")
    print("-" * 60)

    try:
        # Try downloading via spacy command
        subprocess.run(
            [sys.executable, '-m', 'spacy', 'download', 'en_core_web_lg'],
            check=True
        )
        print("✓ spaCy model installed successfully")
        return True
    except subprocess.CalledProcessError:
        # Fallback to pip install
        try:
            print("   Trying alternative installation method...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install',
                 'https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1.tar.gz'],
                check=True
            )
            print("✓ spaCy model installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install spaCy model: {e}")
            return False


def check_dependencies():
    """Check if critical dependencies are installed."""
    print("\n🔍 Checking dependencies")
    print("-" * 60)

    critical_packages = [
        ('openai', 'OpenAI API client'),
        ('anthropic', 'Claude API client'),
        ('numpy', 'NumPy'),
        ('cv2', 'OpenCV (opencv-python)'),
        ('PIL', 'Pillow'),
        ('spacy', 'spaCy'),
        ('dotenv', 'python-dotenv'),
    ]

    missing = []
    for package, name in critical_packages:
        try:
            __import__(package)
            print(f"   ✓ {name}")
        except ImportError:
            print(f"   ✗ {name} - NOT INSTALLED")
            missing.append(name)

    if missing:
        print(f"\n⚠️  Missing {len(missing)} package(s)")
        return False

    print("\n✓ All critical dependencies installed")
    return True


def setup_environment():
    """Interactive environment setup."""
    print("\n🐍 Python Environment Setup")
    print("=" * 60)

    # Check Python version
    print(f"\nPython version: {sys.version.split()[0]}")
    if not check_python_version():
        print("⚠️  Warning: Cradle requires Python 3.10")
        print("   Current version:", sys.version.split()[0])
        cont = input("\nContinue anyway? (y/N): ").strip().lower()
        if cont != 'y':
            return False
    else:
        print("✓ Python 3.10 detected")

    # Check conda
    if not is_conda_available():
        print("\n⚠️  Conda not found in system")
        print("   You can install dependencies manually with:")
        print("   pip install -r requirements.txt")
        cont = input("\nContinue without conda? (y/N): ").strip().lower()
        if cont != 'y':
            return False

        # Install without conda
        return install_requirements() and install_spacy_model()

    # Check if in correct environment
    if is_in_conda_env():
        current = get_current_env_name()
        print(f"\n✓ Currently in conda environment: {current}")

        if current != 'cradle-dev':
            print("⚠️  You are not in the 'cradle-dev' environment")
            print("   It's recommended to use: conda activate cradle-dev")
    else:
        print("\n⚠️  Not in a conda environment")

    # Check if cradle-dev exists
    if check_cradle_env_exists():
        print("✓ cradle-dev environment exists")
    else:
        print("✗ cradle-dev environment does not exist")
        create = input("\nCreate cradle-dev environment? (Y/n): ").strip().lower()
        if create != 'n':
            if not create_conda_env():
                return False

    # Install dependencies
    install = input("\nInstall/update dependencies? (Y/n): ").strip().lower()
    if install != 'n':
        if not install_requirements():
            return False

        if not install_spacy_model():
            return False

    # Final check
    return check_dependencies()


if __name__ == '__main__':
    success = setup_environment()
    if success:
        print("\n✅ Environment setup complete!")
    else:
        print("\n❌ Environment setup incomplete")
        sys.exit(1)
