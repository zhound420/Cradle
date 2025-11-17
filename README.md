# Cradle: Empowering Foundation Agents Towards General Computer Control

> **Enhanced Fork**: This fork includes an **automated game setup wizard**, FREE local LLM support (Ollama, LM Studio, vLLM), multi-host configuration, automatic vision model detection, and streamlined setup - making Cradle dramatically easier to use!

<div align="center">

[[Original Project]](https://baai-agents.github.io/Cradle/)
[[This Fork]](https://github.com/zhound420/Cradle)
[[arXiv]](https://arxiv.org/abs/2403.03186)
[[PDF]](https://arxiv.org/pdf/2403.03186)

[![Python Version](https://img.shields.io/badge/Python-3.10-blue.svg)]()
[![GitHub license](https://img.shields.io/badge/MIT-blue)]()

![](docs/images/cradle-intro-cr.png)

</div>

The Cradle framework empowers nascent foundation models to perform complex computer tasks
via the same unified interface humans use, i.e., screenshots as input and keyboard & mouse operations as output.

## 📢 Updates
- **2025-01-17**: 🎮 **Automated Game Setup Wizard!** New comprehensive setup system that makes configuring games dramatically easier:
  - Multi-platform game installation detection (Windows/macOS/Linux)
  - Automated save file installation to OS-specific locations with backups
  - Interactive checklists for in-game settings with progress tracking
  - Automatic dependency installation (GroundingDino, PyTorch for RDR2)
  - Complete validation before running
  - See [Game Setup Guide](docs/GAME_SETUP_GUIDE.md) for details
- **2024-11-15**: 🆓 **FREE Local LLM Support!** Added comprehensive support for local LLM providers (Ollama, LM Studio, vLLM) with:
  - Multi-host/remote server support
  - Automatic vision model detection and selection
  - Interactive setup wizard with provider management
  - Zero API costs - run everything locally!
- 2024-06-27: A major update! Cradle is extened to four games: [RDR2](https://www.rockstargames.com/reddeadredemption2), [Stardew Valley](https://www.stardewvalley.net/), [Cities: Skylines](https://www.paradoxinteractive.com/games/cities-skylines/about), and [Dealer's Life 2](https://abyteentertainment.com/dealers-life-2/) and various software, including but not limited to Chrome, Outlook, Capcut, Meitu and Feishu. We also release our latest [paper](https://arxiv.org/pdf/2403.03186). Check it out!

<div align="center">

![](docs/images/gcc.jpg)

</div>

## Latest Videos
<div align="center">
<a alt="Watch the video" href="https://www.youtube.com/watch?v=fkkSJw1iJJ8"><img src="./docs/envs/images/rdr2/RDR2_story_cover.jpg" width="33%" /></a>
&nbsp;&nbsp;
<a alt="Watch the video" href="https://www.youtube.com/watch?v=ay5gBqzPcDE"><img src="./docs/envs/images/rdr2/RDR2_openended_cover.jpg" width="33%" /></a>
&nbsp;&nbsp;
<a alt="Watch the video" href="https://www.youtube.com/watch?v=regULK_60_8"><img src="./docs/envs/images/skylines/cityskyline_video_cover.png" width="33%" /></a>
&nbsp;&nbsp;
<a alt="Watch the video" href="https://www.youtube.com/watch?v=Kaiz4yJieUk"><img src="./docs/envs/images/stardew/stardew_video_cover.png" width="33%" /></a>
&nbsp;&nbsp;
<a alt="Watch the video" href="https://www.youtube.com/watch?v=WZiL_0V880M"><img src="./docs/envs/images/dealers/dealer_video_cover.png" width="33%" /></a>
&nbsp;&nbsp;
<a alt="Watch the video" href="https://www.youtube.com/watch?v=uWgLnZmpVTM"><img src="./docs/envs/images/software/Software_cover.png" width="33%" /></a>
&nbsp;&nbsp;
</div>

Click on either of the video thumbnails above to watch them on YouTube.

## ✨ Key Features of This Fork

This enhanced fork makes Cradle significantly easier to set up and use:

| Feature | Description | Status |
|---------|-------------|--------|
| **🎮 Game Setup Wizard** | Automated game configuration with installation detection, save file management, and interactive checklists | ✅ NEW |
| **🆓 FREE Local LLMs** | Run with Ollama, LM Studio, or vLLM - no API costs | ✅ |
| **👁️ Vision Model Detection** | Automatic detection and selection of vision-capable models | ✅ |
| **🌐 Multi-Host Support** | Configure providers on localhost, LAN servers, or remote GPUs | ✅ |
| **⚡ Simplified Scripts** | `setup.py`, `run.py`, `game-setup.py` for easy execution | ✅ |
| **✓ Validation Tools** | Automated health checks and setup validation | ✅ |
| **📚 Enhanced Documentation** | Comprehensive guides for setup, providers, and games | ✅ |

**Quick comparison:**

- **Original**: Manual save file copying, complex setup, API-only, steep learning curve
- **This Fork**: Automated setup wizard, FREE local LLMs, one-command game setup, beginner-friendly

# 🚀 Quick Start (Recommended)

**This fork** provides simplified setup, FREE local LLM support, and automatic vision model detection!

### 1. Clone and Setup Environment
```bash
# Clone this enhanced fork
git clone https://github.com/zhound420/Cradle.git
cd Cradle

# Run interactive setup wizard
python setup.py
```

The setup wizard will guide you through:
- ✓ Python environment configuration
- ✓ Dependency installation
- ✓ API key setup (OpenAI, Claude, Azure, AWS) - *optional*
- ✓ Local provider configuration (Ollama, LM Studio, vLLM) - *automatic*
- ✓ Health check validation

**Note**: Setup auto-creates configs for local providers (localhost by default). You can skip API keys and use FREE local LLMs instead!

### 2. Setup a Specific Game

**NEW!** Use the automated game setup wizard:

```bash
# List available games
python game-setup.py --list

# Setup Cities: Skylines (recommended for beginners)
python game-setup.py skylines

# Setup Red Dead Redemption 2 (includes dependency installation)
python game-setup.py rdr2

# Quick setup with minimal prompts
python game-setup.py stardew --quick

# Check if game is properly configured
python game-setup.py skylines --check-only
```

The game setup wizard will:
- ✓ Detect game installation automatically
- ✓ Install save files to correct locations
- ✓ Guide through in-game settings with interactive checklists
- ✓ Install game-specific dependencies (e.g., GroundingDino for RDR2)
- ✓ Validate complete setup before running

See [Game Setup Guide](docs/GAME_SETUP_GUIDE.md) for detailed instructions.

### 3. Run a Game or Application

```bash
# List available games/apps
python run.py --list

# Run Cities: Skylines (recommended for beginners)
python run.py skylines

# Run with FREE local LLM (no API costs!)
python run.py skylines --llm ollama

# Run with Claude API
python run.py skylines --llm claude

# Other examples
python run.py rdr2-story
python run.py outlook
python run.py stardew-shopping
```

### 4. Validate Your Setup

```bash
# Validate specific game/app
python validate.py skylines

# General health check
python validate.py
```

That's it! The simplified scripts handle all the complex configuration automatically.

---

# 🤖 LLM Provider Management

Cradle supports multiple LLM providers - both API-based and local (FREE):

### Manage Providers

```bash
# See all available providers
python providers.py

# Interactive provider selection
python providers.py --select

# Check if a provider is ready
python providers.py --check ollama

# Configure custom endpoint (for remote servers)
python providers.py --configure-endpoint ollama
```

### Supported Providers

| Provider | Type | Cost | Vision Support | Command |
|----------|------|------|----------------|---------|
| **OpenAI** | API | Paid | ✅ GPT-4o | `--llm openai` |
| **Claude** | API | Paid | ✅ Claude 3.5 | `--llm claude` |
| **Ollama** 🆓 | Local | FREE | ✅ llama3.2-vision, llava | `--llm ollama` |
| **LM Studio** 🆓 | Local | FREE | ✅ llava, bakllava | `--llm lmstudio` |
| **vLLM** 🆓 | Local | FREE | ✅ configurable | `--llm vllm` |

**⚠️ Vision Model Requirement**: Cradle requires vision-capable models to process game screenshots. The setup automatically detects and guides you to select vision models.

### Using Local LLMs (FREE!)

**With Ollama** (Recommended):
```bash
# Install from https://ollama.com
ollama pull llama3.2-vision  # Vision model required!

# Run Cradle
python run.py skylines --llm ollama
```

**With LM Studio**:
```bash
# Download from https://lmstudio.ai
# Load a VISION model (llava, bakllava, etc.) → Start Server

# Configure with automatic model detection
python providers.py --configure-endpoint lmstudio

# Run Cradle
python run.py skylines --llm lmstudio
```

**With vLLM** (High throughput):
```bash
# Start vLLM server with a vision model
vllm serve llava-hf/llava-v1.6-mistral-7b-hf

# Configure endpoint
python providers.py --configure-endpoint vllm

# Run Cradle
python run.py skylines --llm vllm
```

### Multi-Host Support 🌐

Local providers can run on different hosts (localhost, LAN servers, remote GPU servers):

```bash
# Configure Ollama on remote server
python providers.py --configure-endpoint ollama
# Enter: 192.168.1.100:11434

# Configure LM Studio on LAN
python providers.py --configure-endpoint lmstudio
# Enter: http://gpu-server.local:1234

# Or manually edit config files
# conf/ollama_config.json, conf/lmstudio_config.json, conf/vllm_config.json
```

**Vision Model Detection**: When configuring providers, Cradle automatically:
- Detects available models from the server
- Categorizes vision vs text-only models
- Shows interactive selection menu
- Warns if non-vision model selected

See [Provider Management Guide](docs/PROVIDER_MANAGEMENT.md) and [Local LLM Setup](docs/LOCAL_LLM_SETUP.md) for details.

---

# 💾 Manual Installation (Advanced)

## Prepare the Environment File
We currently provide access to OpenAI's and Claude's API. Please create a `.env` file in the root of the repository to store the keys (one of them is enough).

Sample `.env` file containing private information:
```
OA_OPENAI_KEY = "abc123abc123abc123abc123abc123ab"
RF_CLAUDE_AK = "abc123abc123abc123abc123abc123ab" # Access Key for Claude
RF_CLAUDE_SK = "123abc123abc123abc123abc123abc12" # Secret Access Key for Claude
AZ_OPENAI_KEY = "123abc123abc123abc123abc123abc12"
AZ_BASE_URL = "https://abc123.openai.azure.com/"
RF_CLAUDE_AK = "abc123abc123abc123abc123abc123ab"
RF_CLAUDE_SK = "123abc123abc123abc123abc123abc12"
IDE_NAME = "Code"
```
OA_OPENAI_KEY is the OpenAI API key. You can get it from the [OpenAI](https://platform.openai.com/api-keys).

AZ_OPENAI_KEY is the Azure OpenAI API key. You can get it from the [Azure Portal](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.CognitiveServices%2Faccounts).

OA_CLAUDE_KEY is the Anthropic Claude API key. You can get it from the [Anthropic](https://console.anthropic.com/settings/keys).

RF_CLAUDE_AK and RF_CLAUDE_SK are AWS Restful API key and secret key for Claude API.

IDE_NAME refers to the IDE environment in which the repository's code runs, such as `PyCharm` or `Code` (VSCode). It is primarily used to enable automatic switching between the IDE and the target environment.


## Setup

### Python Environment
Please setup your python environment and install the required dependencies as:
```bash
# Clone this enhanced fork
git clone https://github.com/zhound420/Cradle.git
cd Cradle

# Create a new conda environment
conda create --name cradle-dev python=3.10
conda activate cradle-dev
pip install -r requirements.txt
```

**Note**: For most users, we recommend using `python setup.py` instead of manual installation.

### Install the OCR Tools
```
1. Option 1
# Download best-matching version of specific model for your spaCy installation
python -m spacy download en_core_web_lg

or

# pip install .tar.gz archive or .whl from path or URL
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1.tar.gz

2. Option 2
# Copy this url https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1.tar.gz
# Paste it in the browser and download the file to res/spacy/data
cd res/spacy/data
pip install en_core_web_lg-3.7.1.tar.gz
```

# 🚀 Get Started
Due to the vast differences between each game and software, we have provided the specific settings for each of them below.
1. [Red Dead Redemption 2](docs/envs/rdr2.md)
2. [Stardew Valley](docs/envs/stardew.md)
3. [Cities: Skylines](docs/envs/skylines.md)
4. [Dealer's Life 2](docs/envs/dealers.md)
5. [Software](docs/envs/software.md)

<div align="center">
<img src="./docs/images/games_wheel.png" height="365" /> <img src="./docs/images/applications_wheel.png" height="365" />
</div>

# 🌲 File Structure
Since some users may want to apply our framework to new games, this section primarily showcases the core directories and organizational structure of Cradle. We will highlight in "⭐⭐⭐" the modules related to migrating to new games, and provide detailed explanations later.
```
Cradle
├── cache # Cache the GroundingDino model and the bert-base-uncased model
├── conf # ⭐⭐⭐ The configuration files for the environment and the llm model
│   ├── env_config_dealers.json
│   ├── env_config_rdr2_main_storyline.json
│   ├── env_config_rdr2_open_ended_mission.json
│   ├── env_config_skylines.json
│   ├── env_config_stardew_cultivation.json
│   ├── env_config_stardew_farm_clearup.json
│   ├── env_config_stardew_shopping.json
│   ├── openai_config.json           # API providers
│   ├── claude_config.json
│   ├── restful_claude_config.json
│   ├── ollama_config.json            # Local providers (FREE)
│   ├── lmstudio_config.json
│   ├── vllm_config.json
│   └── ...
├── deps # The dependencies for the Cradle framework, ignore this folder
├── docs # The documentation for the Cradle framework, ignore this folder
├── res # The resources for the Cradle framework
│   ├── models # Ignore this folder
│   ├── tool # Subfinder for RDR2
│   ├── [game or software] # ⭐⭐⭐ The resources for game, exmpale: rdr2, dealers, skylines, stardew, outlook, chrome, capcut, meitu, feishu
│   │   ├── prompts # The prompts for the game
│   │   │   └── templates
│   │   │       ├── action_planning.prompt
│   │   │       ├── information_gathering.prompt
│   │   │       ├── self_reflection.prompt
│   │   │       └── task_inference.prompt
│   │   ├── skills # The skills json for the game, it will be generated automatically
│   │   ├── icons # The icons difficult for GPT-4 to recognize in the game can be replaced with text for better recognition using an icon replacer
│   │   └── saves # Save files in the game
│   └── ...
├── requirements.txt # The requirements for the Cradle framework
├── runner.py # The main entry for the Cradle framework
├── cradle # Cradle's core modules
│   ├── config # The configuration for the Cradle framework
│   ├── environment # The environment for the Cradle framework
│   │   ├── [game or software] # ⭐⭐⭐ The environment for the game, exmpale: rdr2, dealers, skylines, stardew, outlook, chrome, capcut, meitu, feishu
│   │   │   ├── __init__.py # The initialization file for the environment
│   │   │   ├── atomic_skills # Atomic skills in the game. Users should customise them to suit the needs of the game or software, e.g. character movement
│   │   │   ├── composite_skills # Combination skills for atomic skills in games or software
│   │   │   ├── skill_registry.py # The skill registry for the game. Will register all atomic skills and composite skills into the registry.
│   │   │   └── ui_control.py # The UI control for the game. Define functions to pause the game and switch to the game window
│   │   └── ...
│   ├── gameio # Interfaces that directly wrap the skill registry and ui control in the environment
│   ├── log # The log for the Cradle framework
│   ├── memory # The memory for the Cradle framework
│   ├── module # Currently there is only the skill execution module. Later will migrate action planning, self-reflection and other modules from planner and provider
│   ├── planner # The planner for the Cradle framework. Unified interface for action planning, self-reflection and other modules. This module will be deleted later and will be moved to the module module.
│   ├── runner # ⭐⭐⭐ The logical flow of execution for each game and software. All game and software processes will then be unified into a single runner
│   ├── utils # Defines some helper functions such as save json and load json
│   └── provider # The provider for the Cradle framework. We have semantically decomposed most of the execution flow in the runner into providers
│       ├── augment # Methods for image augmentation
│       ├── llm # Call for the LLM model, e.g. OpenAI's GPT-4o, Claude, etc.
│       ├── module # ⭐⭐⭐ The module for the Cradle framework. e.g., action planning, self-reflection and other modules. It will be migrated to the cradle/module later.
│       ├── object_detect # Methods for object detection
│       ├── process # ⭐⭐⭐ Methods for pre-processing and post-processing for action planning, self-reflection and other modules
│       ├── video # Methods for video processing
│       ├── others # Methods for other operations, e.g., save and load coordinates for skylines
│       ├── circle_detector.py # The circle detector for the rdr2
│       ├── icon_replacer.py # Methods for replacing icons with text
│       ├── sam_provider.py # Segment anything for software
│       └── ...
└── ...
```

# 📚 Migrate to New Game
Since each game's settings and the operating systems they are compatible with are different, Cradle cannot simply replace one game name to migrate to a new game. We suggest considering each game specifically. For example, RDR2, an independent AAA game, requires real-time combat, so we need to pause the game to wait for GPT-4o's response and then unpause the game to execute the actions. Stardew has the same issue. Other games like Dealer's Life 2 and Cities: Skylines do not have real-time requirements, so they do not need to pause. If the new game is similar to the latter, we recommend copying Cities: Skylines' implementation and following its implementation path to create the corresponding modules. Although each game may differ significantly, our Cradle framework can still achieve a unified adaptation for a game. Assuming the new game's name is **newgame**, the specific migration pipeline can be found [Migrate to New Game Guide](docs/envs/new_game.md). 

# 🤝 About This Fork

This is an enhanced fork of the original [Cradle project](https://github.com/BAAI-Agents/Cradle) with additional features:

- 🎮 **Automated Game Setup Wizard**: One-command game configuration with installation detection, save file management, and interactive checklists
- 🆓 **FREE Local LLM Support**: Ollama, LM Studio, vLLM - no API costs
- 🌐 **Multi-Host Configuration**: Run providers on localhost, LAN servers, or remote GPUs
- 👁️ **Vision Model Detection**: Automatic detection and selection of vision-capable models
- 🧙 **Interactive Setup Wizards**: `setup.py` and `game-setup.py` for streamlined installation
- 📊 **Provider Management**: Easy switching between providers with `providers.py`
- 🔍 **Health Checks**: Validate your setup before running with `validate.py`
- ⚡ **Simplified Execution**: `run.py` for easy game/app launching
- 📚 **Enhanced Documentation**: Comprehensive guides for all features

**Key Tools**:
- `python setup.py` - General environment setup
- `python game-setup.py <game>` - Game-specific configuration wizard
- `python run.py <game> --llm <provider>` - Run with any LLM provider
- `python validate.py <game>` - Validate setup
- `python providers.py` - Manage LLM providers

**Documentation**:
- [Game Setup Guide](docs/GAME_SETUP_GUIDE.md) - Complete game setup documentation
- [Provider Management](docs/PROVIDER_MANAGEMENT.md) - LLM provider configuration
- [Local LLM Setup](docs/LOCAL_LLM_SETUP.md) - FREE local LLM setup guide
- [CLAUDE.md](CLAUDE.md) - Detailed architecture and development guide

**Upstream Repository**: [BAAI-Agents/Cradle](https://github.com/BAAI-Agents/Cradle)

# Citation
If you find this work useful, please consider citing the original Cradle paper:
```
@article{tan2024cradle,
  title={Cradle: Empowering Foundation Agents towards General Computer Control},
  author={Weihao Tan and Wentao Zhang and Xinrun Xu and Haochong Xia and Ziluo Ding and Boyu Li and Bohan Zhou and Junpeng Yue and Jiechuan Jiang and Yewen Li and Ruyi An and Molei Qin and Chuqiao Zong and Longtao Zheng and Yujie Wu and Xiaoqiang Chai and Yifei Bi and Tianbao Xie and Pengjie Gu and Xiyun Li and Ceyao Zhang and Long Tian and Chaojie Wang and Xinrun Wang and Börje F. Karlsson and Bo An and Shuicheng Yan and Zongqing Lu},
  journal={arXiv preprint arXiv:2403.03186},
  year={2024}
}
```
[//]: # (```)
[//]: # (@article{weihao2024cradle,)
[//]: # (  title     = {{Cradle: Empowering Foundation Agents towards General Computer Control}},)
[//]: # (  author    = {Weihao Tan and Wentao Zhang and Xinrun Xu and Haochong Xia and Ziluo Ding and Boyu Li and Bohan Zhou and Junpeng Yue and Jiechuan Jiang and Yewen Li and Ruyi An and Molei Qin and Chuqiao Zong and Longtao Zheng and Yujie Wu and Xiaoqiang Chai and Yifei Bi and Tianbao Xie and Pengjie Gu and Xiyun Li and Ceyao Zhang and Long Tian and Chaojie Wang and Xinrun Wang and Börje F. Karlsson and Bo An and Shuicheng Yan and Zongqing Lu},)
[//]: # (  journal   = {arXiv:2403.03186},)
[//]: # (  month     = {March},)
[//]: # (  year      = {2024},)
[//]: # (  primaryClass={cs.AI})
[//]: # (})
[//]: # (```)
