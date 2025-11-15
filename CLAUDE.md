# CLAUDE.md - AI Assistant Guide for Cradle Framework

## Project Overview

**Cradle** is a framework that empowers foundation models (LLMs like GPT-4, Claude) to perform complex computer tasks via a unified interface: screenshots as input and keyboard & mouse operations as output.

### Purpose
- Enable AI agents to control games and software applications autonomously
- Provide a modular, extensible architecture for adding new environments
- Support both real-time applications (games) and turn-based software
- Implement a reasoning loop: information gathering → reflection → planning → execution

### Supported Environments

**Games:**
- Red Dead Redemption 2 (RDR2)
- Stardew Valley
- Cities: Skylines
- Dealer's Life 2

**Software Applications:**
- Microsoft Outlook
- Google Chrome
- Capcut
- Meitu (xiuxiu)
- Feishu

---

## Core Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│ runner.py (Entry Point)                                 │
│  - Loads configs (LLM, embedding, environment)          │
│  - Dynamically imports appropriate runner               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Environment-Specific Runner                             │
│  (app_runner.py, rdr2_runner.py, etc.)                 │
│                                                          │
│  Main Loop:                                             │
│  1. Information Gathering (analyze screen)              │
│  2. Self Reflection (evaluate progress)                 │
│  3. Task Inference (determine subtasks)                 │
│  4. Skill Curation (select relevant skills)             │
│  5. Action Planning (decide next actions)               │
│  6. Skill Execution (execute via GameManager)           │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Providers│  │  Memory  │  │ GameIO   │
│ (Modules)│  │ (State)  │  │ (I/O)    │
└──────────┘  └──────────┘  └──────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
        ┌────────────────────────┐
        │  Skill Registry        │
        │  - Atomic Skills       │
        │  - Composite Skills    │
        └────────────────────────┘
```

---

## Key Concepts

### 1. Skills System

**Atomic Skills**: Basic, indivisible actions
- Mouse movements, clicks, drags
- Keyboard inputs
- Simple navigation

**Composite Skills**: Complex behaviors built from atomic skills
- Shopping workflows
- Combat sequences
- Navigation patterns

**Skill Registration**: Decorator-based auto-registration
```python
@register_skill("skill_name")
def skill_name(param1, param2):
    """
    Description for LLM.

    Parameters:
    - param1: Description. Type info.
    - param2: Description. Type info.
    """
    # Implementation
```

### 2. Provider Architecture

**Base Pattern**: All providers extend `BaseProvider` or `BaseModuleProvider`

**Types:**
- **LLM Providers**: Interface to OpenAI, Claude, Azure
- **Module Providers**: Core reasoning (ActionPlanning, SelfReflection, etc.)
- **Process Providers**: Pre/post-processing for each module
- **Augmentation Providers**: SAM (Segment Anything), SOM (Set-of-Marks), OCR
- **Object Detection**: GroundingDINO for visual object detection

### 3. Memory Management

**Working Area**: Central dictionary holding current execution state
- All modules read from and write to `memory.working_area`
- Provides context across reasoning steps
- Persisted to disk for recovery

**History**: Recent actions, observations, and results
- `add_recent_history_kv(key, value)`: Store
- `get_recent_history(key, k=N)`: Retrieve last N items

### 4. Factory Pattern

Dynamic environment loading via string references:
```python
# In config:
"skill_registry_name": "cradle.environment.outlook.skill_registry.OutlookSkillRegistry"

# Runtime:
skill_registry = SkillRegistryFactory.create(env_name, ...)
```

### 5. Singleton Pattern

Used for shared resources:
- `Config()`: Global configuration
- `Logger()`: Centralized logging
- `IOEnvironment()`: Input/output interface
- Skill registries

---

## Directory Structure

```
Cradle/
├── runner.py                      # Main entry point
├── requirements.txt               # Python dependencies
├── .env                          # API keys (gitignored)
│
├── conf/                         # Configuration files
│   ├── env_config_*.json         # Environment configs
│   ├── openai_config.json        # OpenAI provider config
│   ├── claude_config.json        # Claude provider config
│   └── restful_claude_config.json
│
├── res/                          # Resources per environment
│   ├── {env_name}/
│   │   ├── prompts/
│   │   │   ├── inputs/           # JSON input examples
│   │   │   └── templates/        # Prompt templates (.prompt files)
│   │   ├── skills/               # Auto-generated skill libraries
│   │   ├── icons/                # Icon replacement images
│   │   └── saves/                # Game save files
│   ├── spacy/data/               # OCR model data
│   └── models/                   # Cached ML models
│
├── cache/                        # Model caching (GroundingDino, BERT)
├── docs/                         # Documentation
│   └── envs/                     # Environment-specific guides
│
└── cradle/                       # Core framework (167 Python files)
    ├── config/
    │   ├── config.py             # Singleton Config class
    │   └── constants.py          # Global constants
    │
    ├── environment/              # Environment-specific implementations
    │   ├── skill.py              # Skill dataclass
    │   ├── skill_registry.py     # Base SkillRegistry class
    │   ├── utils.py              # Skill serialization
    │   │
    │   ├── {env_name}/           # Per-environment structure
    │   │   ├── atomic_skills/
    │   │   │   ├── __init__.py
    │   │   │   └── *.py          # Skill definitions
    │   │   ├── composite_skills/ # (Optional)
    │   │   ├── skill_registry.py # Environment skill registry
    │   │   └── ui_control.py     # UI operations (pause, switch)
    │   │
    │   ├── rdr2/
    │   ├── stardew/
    │   ├── skylines/
    │   ├── dealers/
    │   ├── outlook/
    │   ├── chrome/
    │   ├── capcut/
    │   ├── feishu/
    │   └── xiuxiu/
    │
    ├── gameio/                   # Input/Output interface
    │   ├── io_env.py             # IOEnvironment (mouse, keyboard)
    │   └── game_manager.py       # GameManager (high-level control)
    │
    ├── provider/                 # Provider modules
    │   ├── llm/
    │   │   ├── openai_provider.py
    │   │   ├── claude_provider.py
    │   │   └── llm_factory.py
    │   ├── module/               # Core reasoning modules
    │   │   ├── action_planning_provider.py
    │   │   ├── information_gathering_provider.py
    │   │   ├── self_reflection_provider.py
    │   │   ├── task_inference_provider.py
    │   │   └── skill_curation_provider.py
    │   ├── process/              # Pre/post processing
    │   ├── augment/              # Image augmentation (SAM, SOM)
    │   ├── video/                # Video capture, OCR
    │   └── object_detect/        # GroundingDINO
    │
    ├── runner/                   # Execution runners
    │   ├── app_runner.py         # Shared runner for software
    │   ├── rdr2_runner.py        # Game-specific runners
    │   ├── stardew_runner.py
    │   ├── skylines_runner.py
    │   └── dealers_runner.py
    │
    ├── module/
    │   └── executor.py           # Skill execution orchestrator
    │
    ├── memory/                   # State management
    │   ├── base.py               # BaseMemory abstract class
    │   └── local_memory.py       # File-based implementation
    │
    ├── planner/                  # (Legacy, being migrated)
    │   └── planner.py
    │
    ├── log/
    │   └── logger.py             # Centralized logging
    │
    └── utils/                    # Utilities
        ├── json_utils.py
        ├── image_utils.py
        ├── file_utils.py
        ├── singleton.py
        └── ...
```

---

## Development Patterns

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Files | `snake_case.py` | `skill_registry.py` |
| Classes | `PascalCase` | `SkillRegistry` |
| Functions | `snake_case()` | `register_skill()` |
| Constants | `UPPER_CASE` | `SKILL_LIB_MODE_BASIC` |
| Private | `_leading_underscore` | `_check_input_keys()` |
| Environment short names | lowercase | `rdr2`, `outlook` |

### Import Organization

Follow this order:
```python
# 1. Standard library
import os
import time
from typing import Dict, Any

# 2. Third-party
import numpy as np
import cv2

# 3. Cradle framework
from cradle.config import Config
from cradle.log import Logger
from cradle import constants

# 4. Local/environment-specific
from cradle.environment.{env}.atomic_skills import ...
```

### Singleton Access Pattern

```python
from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment

config = Config()      # Module-level singleton instances
logger = Logger()
io_env = IOEnvironment()
```

### Skill Definition Pattern

**File**: `cradle/environment/{env}/atomic_skills/{category}.py`

```python
from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment import post_skill_wait
from cradle.environment.{env}.skill_registry import register_skill

config = Config()
logger = Logger()
io_env = IOEnvironment()

@register_skill("skill_name")
def skill_name(param1: type, param2: type):
    """
    Clear description of what the skill does (LLM reads this).

    Parameters:
    - param1: Description of param1. Type and constraints.
    - param2: Description of param2. Type and constraints.
    """
    # Implementation
    io_env.mouse_move_normalized(x, y)  # Coords in 0-1 range
    io_env.keyboard_type(text)
    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)
```

**Critical Requirements:**
1. **Decorator**: Must use `@register_skill("name")`
2. **Docstring**: Required (used by LLM for skill selection)
3. **Parameter docs**: Format `- param: description.` (period required)
4. **Normalized coords**: Mouse positions must be 0-1 range
5. **Post-action wait**: Always include wait after actions

### Provider Pattern

```python
from cradle.provider.base import BaseModuleProvider

class MyProvider(BaseModuleProvider):

    def __init__(self, template_path, llm_provider, **kwargs):
        super().__init__(template_path=template_path, **kwargs)
        self.llm_provider = llm_provider
        self.memory = LocalMemory()

    @BaseModuleProvider.debug
    @BaseModuleProvider.error
    @BaseModuleProvider.write
    def __call__(self, *args, **kwargs):
        # 1. Get params from memory
        params = deepcopy(self.memory.working_area)
        self._check_input_keys(params)

        # 2. Process
        response = self.llm_provider.create_completion(
            messages=...,
            temperature=...,
            max_tokens=...
        )

        # 3. Validate and return
        self._check_output_keys(response)
        del params
        return response
```

### Factory Registration

**In `__init__.py` or registry:**
```python
factory.register_builder(
    key="outlook",
    builder_path="cradle.environment.outlook.skill_registry.OutlookSkillRegistry"
)
```

**Usage:**
```python
instance = factory.create(key="outlook", **kwargs)
```

---

## Configuration System

### Environment Configuration

**File**: `conf/env_config_{env_name}.json`

```json
{
  "env_name": "Microsoft Outlook",
  "win_name_pattern": "Outlook$",           // Regex for window title
  "sub_path": "outlook",                    // Resource subdirectory
  "env_short_name": "outlook",              // Internal identifier
  "is_game": false,                         // Game vs software
  "shared_runner": "app",                   // Use app_runner.py

  "skill_registry_name": "cradle.environment.outlook.skill_registry.OutlookSkillRegistry",
  "ui_control_name": "cradle.environment.software.ui_control.SoftwareUIControl",

  "provider_configs": {
    "sam2som_config": {
      "plot_bbox_multi_color": true,
      "disable_close_app_icon": true
    }
  },

  "task_description_list": [
    {
      "id": 1,
      "task_description": "Create an email to user@example.com",
      "sub_task_description_list": []
    }
  ],

  "planner_params": {
    "prompt_paths": {
      "inputs": {
        "action_planning": "./res/outlook/prompts/inputs/action_planning.json"
      },
      "templates": {
        "action_planning": "./res/outlook/prompts/templates/action_planning.prompt"
      }
    }
  },

  "skill_configs": {
    "skill_mode": "Basic",                  // Basic, Full, or None
    "skill_names_basic": [                  // Allowed skills in Basic mode
      "click_at_position",
      "type_text",
      "press_key"
    ],
    "skill_names_deny": [],                 // Blocked skills
    "skill_names_allow": []                 // Force-allowed skills
  }
}
```

### LLM Provider Configuration

**File**: `conf/openai_config.json`
```json
{
  "key_var": "OA_OPENAI_KEY",              // Environment variable name
  "emb_model": "text-embedding-ada-002",
  "comp_model": "gpt-4o-2024-05-13",
  "is_azure": false
}
```

**File**: `conf/claude_config.json`
```json
{
  "key_var": "OA_CLAUDE_KEY",
  "comp_model": "claude-3-5-sonnet-20241022"
}
```

### Environment Variables

**File**: `.env` (in repo root, gitignored)
```bash
# OpenAI
OA_OPENAI_KEY=sk-...

# Azure OpenAI
AZ_OPENAI_KEY=...
AZ_BASE_URL=https://....openai.azure.com/

# Claude
OA_CLAUDE_KEY=sk-ant-...
RF_CLAUDE_AK=...  # AWS access key
RF_CLAUDE_SK=...  # AWS secret key

# Development
IDE_NAME=Code     # "Code" for VSCode, "PyCharm", etc.
```

---

## Adding a New Environment

### Step-by-Step Guide

Assume new environment name is `newapp`.

#### 1. Create Configuration
`conf/env_config_newapp.json`
```json
{
  "env_name": "New Application",
  "win_name_pattern": "NewApp",
  "sub_path": "newapp",
  "env_short_name": "newapp",
  "is_game": false,
  "shared_runner": "app",  // Use app_runner for software
  "skill_registry_name": "cradle.environment.newapp.skill_registry.NewAppSkillRegistry",
  "ui_control_name": "cradle.environment.software.ui_control.SoftwareUIControl",
  // ... (copy from similar environment)
}
```

#### 2. Create Environment Structure
```bash
mkdir -p cradle/environment/newapp/atomic_skills
mkdir -p cradle/environment/newapp/composite_skills  # Optional
```

#### 3. Create Skill Registry
`cradle/environment/newapp/skill_registry.py`
```python
from cradle.environment.skill_registry import SkillRegistry, register_skill

# Import atomic skills (triggers @register_skill decorators)
from cradle.environment.newapp.atomic_skills import *

class NewAppSkillRegistry(SkillRegistry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
```

#### 4. Create UI Control
`cradle/environment/newapp/ui_control.py`
```python
from cradle.environment.software.ui_control import SoftwareUIControl

class NewAppUIControl(SoftwareUIControl):
    def __init__(self):
        super().__init__()

    # Override if needed:
    # def pause_game(self): ...
    # def unpause_game(self): ...
```

#### 5. Create Atomic Skills
`cradle/environment/newapp/atomic_skills/__init__.py`
```python
from .interact import *
```

`cradle/environment/newapp/atomic_skills/interact.py`
```python
from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment import post_skill_wait
from cradle.environment.newapp.skill_registry import register_skill

config = Config()
logger = Logger()
io_env = IOEnvironment()

@register_skill("click_button")
def click_button(x, y):
    """
    Clicks a button at specified position.

    Parameters:
    - x: Normalized x-coordinate (0-1).
    - y: Normalized y-coordinate (0-1).
    """
    io_env.mouse_move_normalized(x, y)
    io_env.mouse_click_button("left")
    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)
```

#### 6. Create Prompt Templates
```bash
mkdir -p res/newapp/prompts/templates
mkdir -p res/newapp/prompts/inputs
```

Copy templates from similar environment (e.g., `outlook`):
- `action_planning.prompt`
- `information_gathering.prompt`
- `self_reflection.prompt`
- `task_inference.prompt`

#### 7. Run the Agent
```bash
python runner.py \
  --llmProviderConfig ./conf/openai_config.json \
  --embedProviderConfig ./conf/openai_config.json \
  --envConfig ./conf/env_config_newapp.json
```

---

## Key Files Reference

### Entry Points

#### `runner.py` (45 lines)
Main entry point. Parses arguments, loads config, dynamically imports runner.

**Usage:**
```bash
python runner.py \
  --llmProviderConfig ./conf/openai_config.json \
  --embedProviderConfig ./conf/openai_config.json \
  --envConfig ./conf/env_config_outlook.json
```

### Configuration

#### `cradle/config/config.py`
Singleton configuration class. Loads from:
- Environment config JSON
- LLM provider config JSON
- `.env` file for API keys

**Key methods:**
- `load_env_config(path)`: Load environment configuration
- `set_fixed_seed()`: Set random seeds for reproducibility

**Key attributes:**
- `env_short_name`: Environment identifier
- `env_shared_runner`: Runner to use ("app", or None for env-specific)
- `skill_configs`: Skill mode and allowed/denied skills
- `task_description_list`: Task definitions

#### `cradle/config/constants.py`
Global constants for configuration keys, module names, skill modes.

### Core Classes

#### `cradle/environment/skill_registry.py`
Base `SkillRegistry` class and `@register_skill()` decorator.

**Key methods:**
- `load_skills_from_file()`: Load persisted skills with embeddings
- `load_skills_from_scripts()`: Load skills from Python files
- `filter_skills()`: Apply Basic/Full/None mode filtering
- `register_skill_from_code()`: Dynamic skill registration from LLM-generated code
- `execute_skill()`: Parse parameters and execute skill function
- `retrieve_skills()`: Semantic search for relevant skills

#### `cradle/environment/skill.py`
`Skill` dataclass with:
- `skill_name`: String identifier
- `skill_function`: Callable
- `skill_embedding`: NumPy array (for retrieval)
- `skill_code`: Source code string
- `skill_code_base64`: Hash for change detection

#### `cradle/gameio/io_env.py`
`IOEnvironment` singleton for input/output operations.

**Mouse methods:**
- `mouse_move_normalized(x, y)`: Move to normalized coords (0-1)
- `mouse_click_button(button)`: Click "left", "right", or "middle"
- `mouse_hold_button(button)`: Press and hold
- `mouse_release_button(button)`: Release held button
- `mouse_scroll(direction, amount)`: Scroll wheel

**Keyboard methods:**
- `keyboard_type(text)`: Type string
- `keyboard_press(key)`: Single key press
- `keyboard_hold(key)`: Press and hold
- `keyboard_release(key)`: Release held key
- `keyboard_combo(keys)`: Key combination (e.g., ["ctrl", "c"])

**Special:**
- All mouse coords normalized to 0-1 range (converted based on window resolution)
- Tracks held inputs with expiration counters

#### `cradle/gameio/game_manager.py`
`GameManager` singleton for high-level game control.

**Key methods:**
- `pause_game()`: Pause (for real-time games)
- `unpause_game()`: Resume
- `switch_to_game()`: Focus game window
- `switch_to_ide()`: Focus IDE window
- `take_screenshot()`: Capture current screen
- `execute_actions(skill_sequence)`: Run skill sequence

#### `cradle/memory/local_memory.py`
`LocalMemory` class for state management.

**Key methods:**
- `add_recent_history_kv(key, value)`: Store key-value
- `get_recent_history(key, k=N)`: Get last N values
- `update_info_history(dict)`: Update multiple values
- `working_area`: Dict property holding current state
- `save()` / `load()`: Persist to disk

### Providers

#### `cradle/provider/llm/llm_factory.py`
`LLMFactory` creates appropriate provider based on config.

**Supported:**
- OpenAI (including Azure)
- Claude (Anthropic API)
- RestfulClaude (AWS Bedrock)

#### `cradle/provider/module/action_planning_provider.py`
Determines next actions based on current state and task.

**Input:** Current screen, task description, available skills
**Output:** Sequence of skill calls with parameters

#### `cradle/provider/module/information_gathering_provider.py`
Analyzes screenshots to extract state information.

**Input:** Screenshot (optionally with SAM/SOM augmentation)
**Output:** Structured description of screen contents

#### `cradle/provider/module/self_reflection_provider.py`
Evaluates progress toward goal and past action quality.

**Input:** Recent history, current state, task
**Output:** Assessment of success/failure, suggested corrections

#### `cradle/provider/module/task_inference_provider.py`
Decomposes high-level tasks into subtasks.

**Input:** Overall task description
**Output:** List of subtasks with priorities

---

## Common Workflows

### Running an Experiment

1. **Ensure environment is set up:**
   ```bash
   conda activate cradle-dev
   ```

2. **Configure API keys in `.env`:**
   ```bash
   echo 'OA_OPENAI_KEY=sk-...' >> .env
   ```

3. **Run with specific task:**
   ```bash
   python runner.py \
     --llmProviderConfig ./conf/openai_config.json \
     --embedProviderConfig ./conf/openai_config.json \
     --envConfig ./conf/env_config_outlook.json
   ```

4. **Monitor logs:**
   - Console output shows progress
   - Detailed logs in `logs/` directory
   - Screenshots saved during execution

### Adding a New Skill

1. **Identify environment:** e.g., `outlook`

2. **Create/edit skill file:**
   `cradle/environment/outlook/atomic_skills/new_skills.py`

3. **Define skill:**
   ```python
   @register_skill("new_skill_name")
   def new_skill_name(param1, param2):
       """
       Description.

       Parameters:
       - param1: Description.
       - param2: Description.
       """
       # Implementation
   ```

4. **Import in `__init__.py`:**
   ```python
   from .new_skills import *
   ```

5. **Add to Basic mode (if desired):**
   Edit `conf/env_config_outlook.json`:
   ```json
   "skill_names_basic": [
       "existing_skill",
       "new_skill_name"
   ]
   ```

6. **Regenerate embeddings:**
   - Delete existing skill library: `rm res/outlook/skills/*.json`
   - Run agent: Skills will be re-embedded automatically

### Debugging a Failed Task

1. **Check logs:**
   - Look for error messages in console
   - Review detailed logs in `logs/`

2. **Review screenshots:**
   - Saved during execution
   - Check if agent correctly identified UI elements

3. **Verify skill execution:**
   - Check if skills are being called with correct parameters
   - Look for parameter parsing errors

4. **Adjust prompts:**
   - Edit templates in `res/{env}/prompts/templates/`
   - Provide more context or examples

5. **Test skills manually:**
   ```python
   from cradle.environment.outlook.atomic_skills import click_button
   click_button(0.5, 0.5)  # Test skill directly
   ```

### Modifying Prompts

1. **Locate template:**
   `res/{env}/prompts/templates/action_planning.prompt`

2. **Edit template:**
   - Use `{placeholder}` syntax for variables
   - Variables filled from `memory.working_area`

3. **Test changes:**
   - Run agent with modified prompt
   - Monitor output quality

4. **Iterate:**
   - Refine based on agent behavior
   - Add examples if needed

---

## Testing and Debugging

### Current Approach

**No formal test suite** (no pytest, unittest files found).

**Testing is primarily:**
1. **Task-based validation**: Define tasks in `task_description_list`
2. **Manual execution**: Run agent and observe behavior
3. **Log analysis**: Review detailed logs for errors
4. **Screenshot review**: Verify visual understanding

### Debugging Tools

#### Logger Usage
```python
from cradle.log import Logger
logger = Logger()

logger.write("Info message")     # Normal logging
logger.debug("Debug details")    # Debug level
logger.warn("Warning message")   # Warnings
logger.error("Error occurred")   # Errors
```

#### Memory Inspection
```python
from cradle.memory import LocalMemory
memory = LocalMemory()

# View current state
print(memory.working_area)

# Check recent history
print(memory.get_recent_history("actions", k=5))
```

#### Skill Execution Tracing
- Each skill logs execution start/end
- Parameters logged before execution
- Errors caught and logged

### Common Issues

#### Issue: Skills not found
**Cause:** Not registered or filtered out
**Fix:**
1. Check `@register_skill()` decorator present
2. Verify import in `__init__.py`
3. Check skill mode in config (Basic vs Full)

#### Issue: Incorrect coordinates
**Cause:** Using absolute instead of normalized coords
**Fix:** Ensure coords in 0-1 range

#### Issue: Window focus lost
**Cause:** Game/app window not active
**Fix:** Check `win_name_pattern` in config matches window title

#### Issue: LLM API errors
**Cause:** Invalid API key or rate limits
**Fix:**
1. Verify `.env` has correct keys
2. Check API quota/rate limits
3. Review provider config

---

## Important Conventions

### Code Style

1. **Type hints encouraged** but not strictly enforced
2. **Docstrings required** for skills (LLM reads them)
3. **Constants in UPPER_CASE** from `constants.py`
4. **No hardcoded paths**: Use `config` for paths

### Coordinate System

**Always use normalized coordinates (0-1 range):**
- `(0, 0)` = top-left corner
- `(1, 1)` = bottom-right corner
- `(0.5, 0.5)` = center

**Conversion handled by `IOEnvironment`** based on window resolution.

### Skill Documentation Format

**Critical for LLM understanding:**

```python
@register_skill("skill_name")
def skill_name(param1, param2):
    """
    Single-sentence summary of what skill does.

    Parameters:
    - param1: Description with type and constraints.
    - param2: Another parameter description.
    """
```

**Requirements:**
- First line: Brief summary
- Blank line
- `Parameters:` section
- Format: `- param_name: description.` (note the dash and period)

### Pause/Unpause for Real-Time Games

**Games requiring pause (RDR2, Stardew):**
- Pause before LLM reasoning (prevents state changes)
- Unpause before skill execution
- Re-pause after execution

**Software (Outlook, Chrome):**
- No pause needed (not real-time)

### Error Handling

**Providers use decorators:**
```python
@BaseModuleProvider.debug  # Log debug info
@BaseModuleProvider.error  # Catch and log errors
@BaseModuleProvider.write  # Log normal execution
def __call__(self, *args, **kwargs):
    # Implementation
```

**Skills should handle errors gracefully:**
```python
try:
    io_env.mouse_click_button("left")
except Exception as e:
    logger.error(f"Click failed: {e}")
    return False
return True
```

---

## Dependencies

### Core Libraries

```
Python 3.10 (required)

# LLM Providers
openai==1.2.3
anthropic
tiktoken==0.5.1

# Computer Vision
opencv-python==4.8.1.78
opencv-contrib-python==4.8.1.78
pillow>=10.3.0
easyocr==1.7.1
spacy==3.7.2
supervision==0.21.0
segment-anything (from GitHub)

# Automation
ahk==1.7.6                           # AutoHotKey (Windows)
pyautogui==0.9.54
pydirectinput==1.0.4                 # Windows only
mss==9.0.1                           # Screenshot capture
pywin32                              # Windows only
pyobjc-framework-Quartz==10.0       # macOS only
pyobjc-framework-Cocoa==10.0        # macOS only

# Utilities
numpy==1.24.3
python-dotenv==1.0.0
colorama
matplotlib==3.9.1
dataclass_wizard==0.22.3
dill==0.3.8                          # Function serialization
```

### Platform-Specific

- **Windows**: `pywin32`, `pydirectinput`, `ahk`
- **macOS**: `pyobjc-framework-Quartz`, `pyobjc-framework-Cocoa`
- **Linux**: Most dependencies available via pip

---

## Special Patterns and Quirks

### 1. Skill Code Hashing
- Skills stored with base64-encoded source code
- If code changes, embedding regenerated automatically
- Prevents stale embeddings after code modifications

### 2. Icon Replacement
- Some game icons hard to recognize by LLM
- Icon replacer overlays text labels on icons
- Improves LLM understanding of UI elements

### 3. Held Input Tracking
- Tracks held keys/buttons with expiration counters
- Prevents stuck inputs
- Auto-release after timeout

### 4. Template Matching for Navigation
- Minimap template matching for spatial navigation
- Used in RDR2, Stardew Valley
- Finds player position on map

### 5. SAM2SOM Pipeline
- Segment Anything Model (SAM) segments image
- Set-of-Marks (SOM) labels segments with numbers
- LLM references segments by number in actions

### 6. Close Icon Detection
- Prevents accidentally clicking window close button
- Disableable via config: `"disable_close_app_icon": true`

### 7. Video Frame Capture
- Parallel video recording during execution
- Enables post-hoc analysis
- Frame extraction for training data

### 8. Skill Retrieval
- Embedding-based semantic search
- Retrieves relevant skills for current task
- Reduces token usage by filtering skill library

---

## Migration Notes

### From Previous Versions

- **Planner → Provider**: Planner module being migrated to provider architecture
- **Unified Runner**: Moving toward single runner for all environments
- Environment-specific runners still exist but will be deprecated

### When Updating Existing Environments

1. **Check skill mode**: Ensure `skill_names_basic` contains required skills
2. **Regenerate embeddings**: Delete skill library JSON to force regeneration
3. **Update prompt templates**: May need adjustments for new LLM versions
4. **Test thoroughly**: Task success rates may change with framework updates

---

## Best Practices for AI Assistants

### When Reading Code

1. **Check singleton instances** at module level
2. **Follow factory patterns** for environment-specific code
3. **Understand memory flow**: What goes in `working_area`
4. **Read prompt templates**: Understand LLM context

### When Writing Code

1. **Follow naming conventions** strictly
2. **Use normalized coordinates** always
3. **Document skills thoroughly** (LLM depends on it)
4. **Include wait times** after actions
5. **Test with actual environment** (no unit tests available)

### When Debugging

1. **Check logs first**: Extensive logging available
2. **Review screenshots**: Visual confirmation of state
3. **Trace memory updates**: Verify state propagation
4. **Test skills individually**: Isolate failures

### When Adding Features

1. **Start with existing similar environment**: Copy and modify
2. **Iterate on prompts**: Most behavior controlled by prompts
3. **Use Basic skill mode initially**: Limit skill set during development
4. **Expand gradually**: Add skills as needed

---

## Quick Reference

### Common File Locations

| Purpose | Path |
|---------|------|
| Main entry | `runner.py` |
| Environment config | `conf/env_config_{env}.json` |
| LLM config | `conf/{provider}_config.json` |
| Skill registry | `cradle/environment/{env}/skill_registry.py` |
| Atomic skills | `cradle/environment/{env}/atomic_skills/*.py` |
| Prompt templates | `res/{env}/prompts/templates/*.prompt` |
| Skill library | `res/{env}/skills/*.json` |
| Logs | `logs/` |

### Common Commands

```bash
# Setup environment
conda create -n cradle-dev python=3.10
conda activate cradle-dev
pip install -r requirements.txt

# Install OCR
python -m spacy download en_core_web_lg

# Run agent
python runner.py \
  --llmProviderConfig ./conf/openai_config.json \
  --embedProviderConfig ./conf/openai_config.json \
  --envConfig ./conf/env_config_outlook.json
```

### Common Imports

```python
from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.memory import LocalMemory
from cradle.environment import post_skill_wait
from cradle.environment.{env}.skill_registry import register_skill
```

---

## Contact and Resources

- **Repository**: https://github.com/BAAI-Agents/Cradle
- **Paper**: https://arxiv.org/abs/2403.03186
- **Website**: https://baai-agents.github.io/Cradle/

For specific environment setup, see:
- `docs/envs/rdr2.md`
- `docs/envs/stardew.md`
- `docs/envs/skylines.md`
- `docs/envs/dealers.md`
- `docs/envs/software.md`

For migrating to new environments:
- `docs/envs/new_game.md`

---

*Last updated: 2025-11-15*
*Framework version: Based on commit d7752fc*
