# Repository Guidelines

## Project Structure & Module Organization
`runner.py` is the universal entry point; it loads a scenario-specific runner from `cradle/runner` based on the active config. Core logic lives under `cradle/`, where `environment/<game_or_app>` defines atomic and composite skills plus UI controls, `provider/` wraps perception, LLM, and process helpers, and `module/` hosts execution pipelines. Operational settings (`conf/env_config_*.json`, LLM configs) sit in `conf/`. Visual and prompt assets belong in `res/<env>/` (prompts, icons, generated skills, save files). Reference guides reside in `docs/`, while cached weights and checkpoints stay under `cache/` and `deps/`.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` — install the Python 3.10 runtime stack used across runners.
- `python -m spacy download en_core_web_lg` (or install the provided wheel into `res/spacy/data`) — prepares the OCR model required by the perception modules.
- `python runner.py --envConfig ./conf/env_config_rdr2_main_storyline.json --llmProviderConfig ./conf/openai_config.json --embedProviderConfig ./conf/openai_config.json` — launches the AAA RDR2 workflow; swap the env config to target Stardew, Cities, Dealer’s Life, or software runners as documented under `docs/envs/`.
- `python runner.py --envConfig ./conf/env_config_skylines.json --llmProviderConfig ./conf/restful_claude_config.json` — quick smoke-test for a non–real-time scenario.

## Coding Style & Naming Conventions
Follow standard PEP 8 with 4-space indentation, descriptive `snake_case` functions, and PascalCase classes (e.g., `GameManager`). Use type hints on public interfaces in `cradle/*` modules and keep side-effecting helpers inside `utils/`. Configuration files follow `env_config_<scenario>.json`; resources mirror the same slug inside `res/<scenario>/...`. Keep prompts self-contained and favor docstrings for modules that orchestrate skills or providers.

## Testing Guidelines
There is no standalone pytest suite—validation happens through scenario runs. For regressions, execute `python runner.py --envConfig ./conf/env_config_stardew_cultivation.json ...` and verify the generated logs under `log/` plus any saved frames in `res/<env>/`. When touching prompts or skills, capture before/after screenshots or recordings referenced in the PR and ensure the relevant `docs/envs/<env>.md` steps still succeed end-to-end.

## Commit & Pull Request Guidelines
Commits in this repo use short, imperative subjects with optional issue references (e.g., `Fix incorrect duration check on Windows (#91)`). Group logically related changes; config tweaks should mention the impacted env slug. Pull requests must summarize the scenario, list reproduction commands, link tracking issues, and attach media for UI-facing updates. Include notes about required `.env` keys or resource refresh steps so downstream agents can rehydrate their workspace without guesswork.

## Security & Configuration Tips
Store API keys and IDE hints only in the untracked `.env`. Review `conf/*` before committing to ensure no tenant-specific endpoints or cookies leak. Large assets in `res/<env>/saves` should stay anonymized; scrub personal data from captured screenshots and prefer synthetic examples when documenting new workflows.
