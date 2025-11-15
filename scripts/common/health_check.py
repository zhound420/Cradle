"""Health check utilities for validating Cradle setup."""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple


def check_config_file(config_path: str) -> Tuple[bool, str]:
    """Check if a config file exists and is valid JSON."""
    path = Path(config_path)

    if not path.exists():
        return False, f"File not found: {config_path}"

    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return True, f"Valid JSON ({len(data)} keys)"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def check_env_file() -> Tuple[bool, str]:
    """Check if .env file exists and has required keys."""
    env_path = Path('.env')

    if not env_path.exists():
        return False, ".env file not found"

    # Read env file
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    # Check for at least one LLM provider
    has_openai = 'OA_OPENAI_KEY' in env_vars
    has_azure = 'AZ_OPENAI_KEY' in env_vars
    has_claude = 'OA_CLAUDE_KEY' in env_vars
    has_aws_claude = 'RF_CLAUDE_AK' in env_vars and 'RF_CLAUDE_SK' in env_vars

    providers = []
    if has_openai:
        providers.append('OpenAI')
    if has_azure:
        providers.append('Azure OpenAI')
    if has_claude:
        providers.append('Claude')
    if has_aws_claude:
        providers.append('AWS Claude')

    if not providers:
        return False, "No LLM provider keys found"

    return True, f"Providers: {', '.join(providers)}"


def check_directory_structure() -> List[Tuple[str, bool, str]]:
    """Check if required directories exist."""
    required_dirs = [
        ('conf', 'Configuration files'),
        ('res', 'Resources'),
        ('cradle', 'Core framework'),
        ('cradle/environment', 'Environment modules'),
        ('cradle/provider', 'Provider modules'),
        ('cradle/runner', 'Runner modules'),
    ]

    results = []
    for dir_path, description in required_dirs:
        path = Path(dir_path)
        exists = path.exists() and path.is_dir()
        results.append((dir_path, exists, description))

    return results


def check_game_environment(env_name: str) -> Tuple[bool, List[str]]:
    """Check if a specific game/app environment is properly set up."""
    issues = []

    # Check environment directory
    env_dir = Path(f'cradle/environment/{env_name}')
    if not env_dir.exists():
        issues.append(f"Environment directory not found: {env_dir}")
        return False, issues

    # Check skill_registry.py
    skill_registry = env_dir / 'skill_registry.py'
    if not skill_registry.exists():
        issues.append(f"skill_registry.py not found")

    # Check atomic_skills directory
    atomic_skills = env_dir / 'atomic_skills'
    if not atomic_skills.exists():
        issues.append(f"atomic_skills/ directory not found")
    else:
        skill_files = list(atomic_skills.glob('*.py'))
        if len(skill_files) <= 1:  # Only __init__.py
            issues.append(f"No skill files found in atomic_skills/")

    # Check config file
    config_file = Path(f'conf/env_config_{env_name}.json')
    if not config_file.exists():
        # Try alternative naming
        if env_name == 'rdr2':
            config_file = Path('conf/env_config_rdr2_main_storyline.json')
        if not config_file.exists():
            issues.append(f"Config file not found: {config_file}")

    # Check prompts
    prompts_dir = Path(f'res/{env_name}/prompts/templates')
    if not prompts_dir.exists():
        issues.append(f"Prompts directory not found: {prompts_dir}")
    else:
        required_prompts = [
            'action_planning.prompt',
            'information_gathering.prompt',
            'self_reflection.prompt',
            'task_inference.prompt'
        ]
        for prompt_file in required_prompts:
            if not (prompts_dir / prompt_file).exists():
                issues.append(f"Missing prompt: {prompt_file}")

    return len(issues) == 0, issues


def run_health_check(verbose: bool = False) -> bool:
    """Run comprehensive health check."""
    print("\n🏥 Cradle Health Check")
    print("=" * 60)

    all_passed = True

    # Check Python version
    print("\n1️⃣  Python Environment")
    print("-" * 40)
    version = sys.version.split()[0]
    python_ok = sys.version_info.major == 3 and sys.version_info.minor == 10
    status = "✓" if python_ok else "⚠️"
    print(f"   {status} Python version: {version}")
    if not python_ok:
        print("      Recommended: Python 3.10")
        all_passed = False

    # Check .env file
    print("\n2️⃣  API Keys (.env)")
    print("-" * 40)
    env_ok, env_msg = check_env_file()
    status = "✓" if env_ok else "✗"
    print(f"   {status} {env_msg}")
    if not env_ok:
        all_passed = False

    # Check directory structure
    print("\n3️⃣  Directory Structure")
    print("-" * 40)
    dir_results = check_directory_structure()
    for dir_path, exists, description in dir_results:
        status = "✓" if exists else "✗"
        print(f"   {status} {dir_path:30s} - {description}")
        if not exists:
            all_passed = False

    # Check config files
    print("\n4️⃣  Configuration Files")
    print("-" * 40)
    config_files = [
        './conf/openai_config.json',
        './conf/claude_config.json',
    ]
    for config_path in config_files:
        config_ok, config_msg = check_config_file(config_path)
        status = "✓" if config_ok else "✗"
        print(f"   {status} {os.path.basename(config_path):25s} - {config_msg}")
        if not config_ok and verbose:
            all_passed = False

    # Check environments (sample)
    print("\n5️⃣  Environment Setup (Sample)")
    print("-" * 40)
    sample_envs = ['skylines', 'outlook', 'rdr2']
    for env_name in sample_envs:
        env_ok, issues = check_game_environment(env_name)
        status = "✓" if env_ok else "✗"
        print(f"   {status} {env_name}")
        if not env_ok and verbose:
            for issue in issues:
                print(f"      - {issue}")

    # Check dependencies
    print("\n6️⃣  Critical Dependencies")
    print("-" * 40)
    critical_packages = [
        'openai', 'anthropic', 'numpy', 'cv2', 'PIL', 'spacy'
    ]
    for package in critical_packages:
        try:
            __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} - NOT INSTALLED")
            all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Health check PASSED - Cradle is ready to use!")
    else:
        print("⚠️  Health check found some issues")
        print("   Run 'python setup.py' to fix common problems")

    print("=" * 60 + "\n")

    return all_passed


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run Cradle health check')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed error messages')
    args = parser.parse_args()

    success = run_health_check(verbose=args.verbose)
    sys.exit(0 if success else 1)
