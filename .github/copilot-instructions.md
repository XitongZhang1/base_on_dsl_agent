# Copilot / AI Agent Instructions for this Repository

Short, actionable notes to help an AI coding agent be immediately productive working on this DSL-based assistant project.

1. Big picture
- **Purpose:** This repository implements a small DSL-driven conversational agent framework: DSL scripts in `scenarios/` describe flows; `dsl_agent/parser.py` parses DSL → AST; `dsl_agent/interpreter.py` runs a `Scenario` using an intent service to map user text to intents; `dsl_agent/LLM_integration.py` provides pluggable intent classifiers (stub for tests, LLM-backed for production).
- **Data flow:** `scenarios/*.dsl` → parser → AST (`dsl_agent/ast_nodes.py`) → `Interpreter` → uses `IntentService` → produces responses and transitions states.

2. Key files to inspect first
- `dsl_agent/parser.py` — simple line-oriented parser; look here to understand DSL syntax handling and limitations (string literals, simple expressions, function calls).
- `dsl_agent/LLM_integration.py` — contains `StubIntentService` and `LLMIntentService` (OpenAI-compatible client). Important: LLM calls expect a single label or `none` and perform normalization.
- `dsl_agent/interpreter.py` — state machine runner; checks `state.intents`, calls `IntentService.identify`, updates `current_state`, and formats responses.
- `scenarios/*.dsl` — canonical examples (e.g. `scenarios/banking_scenario.dsl`) show supported DSL constructs (WHEN/THEN/SAY/CALL/IF/WHILE/SET/END etc.). Use these when adding features or tests.

3. Project-specific conventions and patterns
- **Intent service contract:** `identify(text, state, intents)` must return a single intent label (string) or `None`. If asynchronous, implementations may be awaited by the interpreter. Prefer returning `None` for uncertain cases rather than raising.
- **Testing stubs:** Use `StubIntentService` (in `LLM_integration.py`) with `mapping` for deterministic tests — tests in `tests/` rely on this pattern.
- **Parser limitations:** The parser is intentionally minimal (line-based, simple token rules). When extending, add unit tests in `tests/test_parser.py` showing exact input → expected AST mapping.
- **No heavy dependency injection framework:** configuration is passed directly into constructor args (e.g., `LLMIntentService(api_base, api_key, model, ...)`). Keep changes explicit and small.

4. Build / run / test workflows
- **Run main app:** `python main.py` (calls `dsl_agent.logic.run_logic()` as entrypoint). See [main.py](main.py) for behavior.
- **Run tests:** project uses plain Python tests in `tests/`. Run with `pytest` from repo root (if `pytest` is not installed, `pip install pytest`). Example:

```bash
python -m pytest -q
```

- **LLM local testing:** For offline tests, prefer `StubIntentService` instead of `LLMIntentService`. To run the LLM-backed service you must provide `api_base`, `api_key`, and `model`. Follow the `LLMIntentService` constructor parameters.

5. Safe code-change guidance (for AI edits)
- **When modifying DSL semantics:** update `scenarios/*.dsl` examples and corresponding parser tests in `tests/test_parser.py` to document new syntax. Keep parser changes minimal and add explicit examples demonstrating both valid and invalid inputs.
- **When changing intent classification:** ensure `LLMIntentService._build_prompt` remains constrained — production expects exactly one label or `none`. Update normalization logic in `_normalize_result` if labels change.
- **Logging and errors:** interpreter uses `logging`; prefer adding tests for error states rather than letting exceptions bubble into interactive flows.

6. Quick examples (copyable)
- Create a deterministic test using `StubIntentService`:

```python
from dsl_agent.LLM_integration import StubIntentService
from dsl_agent.interpreter import Interpreter

# make a scenario (or load parsed scenario)
# intent mapping: state -> {trigger_text: intent_label}
stub = StubIntentService(mapping={'initial': {'查询余额': 'check_balance'}}, default_intent=None)
interp = Interpreter(scenario, stub)
reply = interp.process_input('查询余额')
```

7. Where to look for follow-ups
- Parser AST definitions: `dsl_agent/ast_nodes.py` — change here if you add new AST node types.
- Logic orchestration: `dsl_agent/logic.py` — contains runtime wiring and helpers used by `main.py`.

If any section is ambiguous or you'd like more examples (e.g., more tests, sample config for LLM credentials), tell me which part to expand and I'll iterate.
