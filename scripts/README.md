# Cradle Setup Scripts

This directory contains setup and validation utilities for Cradle.

## Directory Structure

```
scripts/
├── common/              # Shared utilities
│   ├── api_keys.py     # API key management
│   ├── conda_env.py    # Environment setup
│   └── health_check.py # Health checks
│
└── games/               # Per-game validators
    ├── skylines_validator.py
    └── ... (more validators)
```

## Common Utilities

### api_keys.py
Manages API key configuration:
- Interactive prompts for OpenAI, Claude, Azure keys
- Validation of API keys
- .env file generation

Usage:
```bash
python scripts/common/api_keys.py
```

### conda_env.py
Manages Python environment:
- Checks Python version
- Creates/manages conda environment
- Installs dependencies
- Installs spaCy models

Usage:
```bash
python scripts/common/conda_env.py
```

### health_check.py
Validates Cradle setup:
- Checks directory structure
- Validates config files
- Checks dependencies
- Environment-specific validation

Usage:
```bash
python scripts/common/health_check.py
python scripts/common/health_check.py -v  # Verbose mode
```

## Game Validators

Per-game validation scripts check game-specific requirements.

### Example: Cities: Skylines

```bash
python scripts/games/skylines_validator.py
```

Checks:
- Game installation (Steam)
- Required skills defined
- Prompts configured
- Config files present

## Creating New Validators

To add validation for a new game:

1. Create `scripts/games/<game>_validator.py`
2. Implement `validate()` function
3. Check game-specific requirements:
   - Game installation
   - Skills configuration
   - Prompts
   - Config files

Example template:

```python
"""Game X specific validation."""

def validate() -> bool:
    """Run Game X validation."""
    print("\n🎮 Game X Validation")
    # Add your checks here
    return True

if __name__ == '__main__':
    import sys
    success = validate()
    sys.exit(0 if success else 1)
```

## Integration

These utilities are used by the main setup tools:

- `setup.py` - Uses all common utilities
- `validate.py` - Uses health_check and game validators
- `run.py` - References config paths

See the root directory for user-facing tools.
