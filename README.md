# DSL Agent — 多场景客服机器人 (示例)

本仓库实现了一个小型 DSL（脚本）驱动的客服机器人框架：
- `scenarios/*.dsl` 用于编写场景脚本（response 行为式 DSL）。
- 解析器：`dsl_agent/parser.py` -> AST。解释器：`dsl_agent/interpreter.py` 执行状态流。
- LLM 意图识别：`dsl_agent/LLM_integration.py` 支持测试用 `StubIntentService` 和 OpenAI 兼容客户端 `LLMIntentService`。

## 运行本地测试（默认，使用 stub）
安装依赖：

```bash
python -m pip install -r requirements.txt
```

运行测试：

```bash
python -m pytest -q
```

### 使用 `config.ini` 进行配置
`config.ini`（仓库根目录）包含示例配置（`api_base`、`api_key`、`model` 等）。请不要将包含真实 API Key 的 `config.ini` 提交到仓库。

CLI 也支持通过环境变量覆盖这些配置，例如 `DSL_API_BASE`、`DSL_API_KEY`、`DSL_MODEL` 等。
另外，可通过 `DSL_PROVIDER` 指定 LLM 提供商（可选值示例：`openai`, `aliyun`）。若使用阿里云或其他厂商提供的 OpenAI 兼容接口，把 `DSL_PROVIDER=aliyun` 并配置 `DSL_API_BASE`/`DSL_API_KEY`/`DSL_MODEL`。

CLI 还提供快速切换开关：`--use-real-llm`，用于在运行时强制使用真实 LLM（如果缺少配置会报错退出）。

示例：使用真实 LLM 运行 `flight_booking` 场景（请在环境或 `config.ini` 中设置 API 凭证）：

```bash
python main.py scenario/flight_booking.dsl --use-real-llm
```


## 运行真实 LLM 端到端测试（可选）
如果需要在本地或 CI 中运行真实 LLM 的端到端测试（不推荐在所有 CI runs 中启用，因为会消耗 API 费用），可以启用如下：

1. 在环境中设置如下变量（安全地通过 CI secrets/环境变量注入）：
   - `DSL_RUN_REAL_LLM=true`
   - `DSL_API_BASE`（例如 https://api.openai.com/v1）
   - `DSL_API_KEY`（实际密钥）
   - `DSL_MODEL`（如 `gpt-4o-mini` / `gpt-3.5-turbo` 等）

2. 运行仅 e2e 测试文件：

```bash
export DSL_RUN_REAL_LLM=true
export DSL_API_BASE=https://api.openai.com/v1
export DSL_API_KEY=sk-...
export DSL_MODEL=gpt-3.5-turbo
python -m pytest tests/test_e2e_llm.py -q
```

在 Windows PowerShell 中使用：

```powershell
$env:DSL_RUN_REAL_LLM='true'
$env:DSL_API_BASE='https://api.openai.com/v1'
$env:DSL_API_KEY='sk-...'
$env:DSL_MODEL='gpt-3.5-turbo'
python -m pytest tests/test_e2e_llm.py -q
```

注意：
- `tests/test_e2e_llm.py` 中的真实 LLM 测试带有 `@pytest.mark.skipif`，只有在 `DSL_RUN_REAL_LLM` 环境变量为真时才会运行。
- 使用真实 LLM 前，请确保你已了解并接受相关费用、配额与数据隐私政策。

## CI 配置示例（GitHub Actions）
下面是一个 GitHub Actions 的示例工作流，用于：
- 运行标准测试（使用 stub）。
- 可选地，当 CI secrets 中包含 LLM 凭证时，运行真实 LLM 的端到端测试。

创建 `.github/workflows/ci.yml`：

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: python -m pip install -r requirements.txt
      - name: Run tests (stub)
        run: python -m pytest -q

  e2e-llm:
    needs: test
    if: ${{ secrets.DSL_API_KEY != '' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: python -m pip install -r requirements.txt
      - name: Run E2E LLM tests
        env:
          DSL_RUN_REAL_LLM: 'true'
          DSL_API_BASE: ${{ secrets.DSL_API_BASE }}
          DSL_API_KEY: ${{ secrets.DSL_API_KEY }}
          DSL_MODEL: ${{ secrets.DSL_MODEL }}
        run: python -m pytest tests/test_e2e_llm.py -q
```

提示：
- 在 GitHub 项目设置中将 `DSL_API_KEY`、`DSL_API_BASE`、`DSL_MODEL` 添加为 Secrets（`Settings > Secrets and variables > Actions`）。
- 由于真实 LLM 测试会消耗费用且包含网络调用，在 PR/CD 的默认路径中建议禁用，并限制仅在需要（例如 nightly）或 protected branches 上运行。

## 日志与故障恢复说明
`LLMIntentService` 在 `LLM_integration.py` 中实现了基本重试/退避策略并会在失败时记录日志：
- 默认 `max_retries=1`，可在 `config.ini` 中修改 `max_retries` 并在 CLI/CI 中以环境变量覆盖。
- 当 LLM 服务失败或返回“none”时，`identify()` 返回 `None`（而不是抛出异常），上层 `Interpreter` 会回退到 `state.default` 转换以保证对话继续。

## 安全和隐私提示
- 请勿将包含 `DSL_API_KEY` 的 `config.ini` 提交到仓库；在 CI 中使用 Secrets。
- 若测试包含用户数据（PII），请在调用 LLM 时做脱敏或在日志中加以遮蔽。

## 参考
- `config.ini`：仓库根目录含详细配置模板。
- `dsl_agent/LLM_integration.py`：LLM 交互与意图分类的实现。

## 示例：在 DSL 中使用 `llm_generate`
DSL 支持在表达式中调用运行时函数；`llm_generate` 是一个新加入的内置函数，用于在脚本内调用 LLM 生成文本。

示例脚本（`scenario/llm_generate_demo.dsl`）:

```
response start.default: llm_generate("Please craft a short greeting for: " + user_input)
```

在运行时，`llm_generate` 会使用当前的 LLM 客户端（即 `LLMIntentService`）来生成文本；在 CI 或本地未配置 LLM 时，会回退到 stub 模式（若 `use_stub=true` 或 LLM 未配置）。

## Demo 与调试脚本
仓库提供 `demo/` 目录用于保存可运行的调试/示例脚本：
- `demo/debug_banking.py` — 演示 `banking_scenario` 的交互和 stub 模拟。
- `demo/debug_dynamic.py` — 演示 AST 动态执行以及调用 `intent()` 的行为。
可通过直接运行脚本来快速调试：

```bash
python demo/debug_banking.py
python demo/debug_dynamic.py
```

如果希望在 `main.py` 中运行示例场景，请使用 `python main.py scenario/llm_generate_demo.dsl` 或 `python main.py scenario/flight_booking.dsl`。

统一运行 demo 场景：

```bash
python demo/run_demo.py --scenario flight_booking
python demo/run_demo.py --scenario flight_booking --use-real-llm
支持额外参数：
- `--reset-each`：当设置时，演示会在每次处理用户输入后重置解释器（便于将每条输入当做独立请求运行）。
```

或使用 `main.py` 统一入口：

```bash
python main.py --demo flight_booking
python main.py --demo flight_booking --use-real-llm
```

`run_demo.py` 会尝试在 `demo/`、`scenario/`、或直接作为文件路径中找到场景 DSL 文件。可使用 `--config` 指定 config.ini，或通过 `--api-base`/`--api-key`/`--model` 覆盖 LLM 配置。

