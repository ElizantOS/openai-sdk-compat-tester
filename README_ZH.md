# OpenAI SDK Compat Tester

![OpenAI SDK Compat Tester 截图](./image.png)

这是一个可以独立发布的兼容性测试工具，用来验证某个接口是否真的兼容
OpenAI SDK Chat Completions 和 Responses API。

它更适合路由器作者、代理层维护者、网关团队和 SDK 集成方，用来做
“有证据的兼容性核验”，而不是临时手工点几次接口。

## 它验证什么

- `Effect`：应该真实生效、可观察的语义行为
- `Contract`：请求、响应、流式、错误 shape 是否兼容
- `Probe`：观测型检查，不作为硬失败依据
- `Acceptance-only`：只验证接口接受参数，不宣称语义完全等价

## 快速开始

使用 `uv`：

```bash
cd openai-sdk-compat-tester
uv sync --extra dev
```

或者使用 `venv` + `pip`：

```bash
cd openai-sdk-compat-tester
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

只测试 Chat Completions：

```bash
OPENAI_COMPAT_RUN_LIVE=1 \
OPENAI_COMPAT_BASE_URL=http://127.0.0.1:18080/v1 \
OPENAI_COMPAT_MODEL=gpt-5.4 \
uv run openai-sdk-compat run --api-mode chat
```

只测试 Responses API：

```bash
OPENAI_COMPAT_RUN_LIVE=1 \
OPENAI_COMPAT_BASE_URL=http://127.0.0.1:18080/compat/v1 \
OPENAI_COMPAT_MODEL=gpt-5.4 \
uv run openai-sdk-compat run --api-mode responses
```

同时测试两种 API：

```bash
OPENAI_COMPAT_RUN_LIVE=1 \
OPENAI_COMPAT_BASE_URL=http://127.0.0.1:18080/compat/v1 \
OPENAI_COMPAT_MODEL=gpt-5.4 \
uv run openai-sdk-compat run --api-mode all
```

## CLI

列出当前清单：

```bash
openai-sdk-compat list --api-mode all
```

运行一个测试语义分组，并显示实时状态面板：

```bash
OPENAI_COMPAT_RUN_LIVE=1 \
OPENAI_COMPAT_BASE_URL=http://127.0.0.1:18080/v1 \
OPENAI_COMPAT_MODEL=gpt-5.4 \
openai-sdk-compat run --api-mode chat --suite effect
```

用 `--api-mode chat`、`--api-mode responses` 或 `--api-mode all` 区分测试范围。
原生 OpenAI-compatible chat endpoint 通常用 `/v1`；测试本路由 compat endpoint
通常用 `/compat/v1`。

`run` 会在每个能力点开始和结束时实时输出进度，最后再打印完整矩阵清单。
如果 stdout 是 TTY，`run` 现在默认使用轻量的 `Rich Live` 状态面板，
而不是之前那种手写 ANSI 清屏渲染。
如果你想退回滚动输出，可以加 `--plain`。
live chat 场景会先通过 `/v1/models` 解析模型；如果
`OPENAI_COMPAT_MODEL` 没有设置，或者设置成了当前路由未暴露的模型，
tester 会自动回退到返回列表里的第一个模型。

Responses 场景同样使用 `OPENAI_COMPAT_BASE_URL`，测试本路由时通常应设为
`http://127.0.0.1:8080/compat/v1`。

## API 模式

- `chat`：OpenAI Chat Completions 兼容性。
- `responses`：OpenAI Responses API 兼容性。
- `all`：列出或运行所有已覆盖场景。

示例：

```bash
openai-sdk-compat list --api-mode responses
openai-sdk-compat run --api-mode responses --suite contract
openai-sdk-compat run --api-mode all --only-executed
```

按 slug 只跑某一个能力点：

```bash
OPENAI_COMPAT_RUN_LIVE=1 \
OPENAI_COMPAT_BASE_URL=http://127.0.0.1:18080/v1 \
OPENAI_COMPAT_MODEL=gpt-5.4 \
openai-sdk-compat run --api-mode chat --slug chat-logit-bias-semantic
```

输出机器可读报告：

```bash
OPENAI_COMPAT_RUN_LIVE=1 \
OPENAI_COMPAT_BASE_URL=http://127.0.0.1:18080/v1 \
openai-sdk-compat run --api-mode chat --suite contract --format json --output artifacts/report.json
```

对 `/compat/v1/models` 暴露的所有模型跑完整矩阵：

```bash
mkdir -p artifacts/model-matrix
for model in $(curl -s http://127.0.0.1:18080/compat/v1/models | python3 -c 'import json,sys; print("\n".join(m["id"] for m in json.load(sys.stdin)["data"]))'); do
  OPENAI_COMPAT_RUN_LIVE=1 \
  OPENAI_COMPAT_BASE_URL=http://127.0.0.1:18080/compat/v1 \
  OPENAI_COMPAT_MODEL="$model" \
  openai-sdk-compat run --api-mode all --only-executed --format json \
    --output "artifacts/model-matrix/${model}.json" \
    > "artifacts/model-matrix/${model}.log" 2>&1 &
done
wait
```

模型矩阵产物会被 git 忽略。它们适合本地排查兼容性，但属于 live、账号相关的证据，
不应该提交到仓库。

## CI 示例

```yaml
- name: Install tester
  run: pip install openai-sdk-compat-tester

- name: Run contract suite
  env:
    OPENAI_COMPAT_RUN_LIVE: "1"
    OPENAI_COMPAT_BASE_URL: http://127.0.0.1:18080/v1
  run: openai-sdk-compat run --api-mode chat --suite contract --format json --output artifacts/report.json
```

## 环境变量

- `OPENAI_COMPAT_RUN_LIVE=1`
- `OPENAI_COMPAT_BASE_URL`
- `OPENAI_COMPAT_API_KEY`
- `OPENAI_COMPAT_MODEL`
  可选覆盖项。live 套件会先用 `/v1/models` 校验它；如果未设置或当前不可用，
  会自动回退到列表里的第一个模型。

## 结果语义

- `Effect`
  测稳定可观察的真实效果。失败就按“不支持该 OpenAI 兼容行为”处理。
- `Contract`
  测协议 shape、响应 shape、错误 shape、流式 shape。失败也按“不支持该 OpenAI 兼容行为”处理。
- `Probe`
  只做观测，不做硬失败。
- `Acceptance-only`
  很窄的例外，只在当前无法稳定做语义验证时使用。
  典型例子包括 chat `logit_bias` acceptance、chat 采样控制 acceptance、
  以及 Responses 可选字段 acceptance / compat-gap 检查。

## 非目标

- 不做模型质量 benchmark，也不做 provider 排名。
- 参数被接口接受，不等于自动宣称其语义完全等价。
- 不替代 provider 自己的端到端业务测试。

## 对话覆盖规则

- 普通通过型 case，默认要在同一个测试文件里同时覆盖单轮和多轮两种变体。
- 天然就是多轮语义的 case，不只补一小段历史，而是直接使用更长的上下文。
- 因此在 pytest 计数里，普通对话型覆盖通常会显示为 `2 passed` / `2 skipped`；
  但如果某个场景本身就直接编码了更长的多轮交互，也可能仍然只显示
  `1 passed` / `1 skipped`。
- 多轮上下文里默认混入英语、日语、中文三种语言。

## Prompt 稳定性约定

- `system` 消息只放角色、模式和长期行为约束。
- 具体事实、输出字段、精确文本、字段值放在 `user` 消息里。这样弱一些或更快的模型
  不容易把角色提示当成具体任务，同时仍能跟住当前 case。
- 如果一个场景要同时检查默认 prose 输出和 structured output，请为 baseline 与结构化
  调用使用两套 messages。不要让同一个 prompt 同时承载两个相反模式。
- 对 hidden reasoning token 容易波动的语义断言要留足余量。usage scaling 这类测试应请求
  明显更长的精确文本，而不是依赖很短的短语来产生更多 completion tokens。
- 工具结果 round trip 要明确说明最终回答应该输出 JSON 本身，还是解析 JSON 后输出某个字段。
  保持 tool result object 和最终 assistant text 的协议差异。

## 目录约定

- `src/openai_sdk_compat_tester/` 包与 CLI
- `tests/effect/` 真实效果测试
- `tests/contract/` 协议 / shape / 错误 / 流式契约测试
- `tests/probe/` 观测型测试
- `tests/acceptance/` 保留给极少数例外
- `tests/test_scenario_catalog.py` 清单一致性校验
- `.github/workflows/ci.yml` 独立项目的 CI 示例入口

## 当前已覆盖

### Effect

- 基础对话
  `tests/effect/test_chat_basic_non_stream_live.py`
  `tests/effect/test_chat_basic_stream_live.py`
- 工具调用
  `tests/effect/test_chat_tools_non_stream_live.py`
  `tests/effect/test_chat_tools_stream_live.py`
  `tests/effect/test_chat_tools_round_trip_live.py`
  `tests/effect/test_chat_tools_named_choice_multi_live.py`
  `tests/effect/test_chat_parallel_tool_calls_live.py`
  `tests/effect/test_tool_streaming_delta_arguments_live.py`
- 结构化输出
  `tests/effect/test_chat_response_format_json_object_live.py`
  `tests/effect/test_chat_response_format_json_schema_live.py`
- 采样与确定性行为
  `tests/effect/test_stop_effect_live.py`
  `tests/effect/test_chat_seed_consistency_live.py`
  `tests/effect/test_chat_n_completions_live.py`
- 多模态与内容语义
  `tests/effect/test_vision_base64_live.py`
  `tests/effect/test_vision_generated_text_ocr_live.py`
  `tests/effect/test_vision_remote_url_live.py`
  `tests/effect/test_chat_input_audio_live.py`
  `tests/effect/test_content_mixed_parts_order_live.py`
  `tests/effect/test_content_assistant_array_output_live.py`
- 对话语义
  `tests/effect/test_history_assistant_priority_live.py`
  `tests/effect/test_role_developer_system_priority_live.py`
  `tests/effect/test_role_tool_roundtrip_complex_live.py`
- 缓存与并发语义
  `tests/effect/test_prompt_cache_hit_consistency_live.py`
  `tests/effect/test_concurrent_seed_consistency_live.py`
- Responses API
  `tests/effect/test_responses_*_live.py`

### Contract

- 模型与请求面
  `tests/contract/test_models_live.py`
  `tests/contract/test_chat_prompt_cache_key_live.py`
  `tests/contract/test_chat_stop_sequences_live.py`
  `tests/contract/test_chat_reasoning_effort_live.py`
- 响应与流式契约
  `tests/contract/test_chat_logprobs_live.py`
  `tests/contract/test_chat_stream_include_usage_live.py`
  `tests/contract/test_finish_reason_length_live.py`
  `tests/contract/test_finish_reason_error_state_live.py`
  `tests/contract/test_stream_first_chunk_role_live.py`
  `tests/contract/test_stream_chunk_order_live.py`
  `tests/contract/test_stream_terminal_chunk_shape_live.py`
  `tests/contract/test_stream_interruption_retry_live.py`
- 错误契约
  `tests/contract/test_error_invalid_model_live.py`
  `tests/contract/test_error_empty_messages_live.py`
  `tests/contract/test_error_invalid_role_live.py`
  `tests/contract/test_error_invalid_tool_schema_live.py`
  `tests/contract/test_error_invalid_response_schema_live.py`
  `tests/contract/test_error_timeout_runtime_shape_live.py`
- service_tier 与 usage 契约
  `tests/contract/test_service_tier_roundtrip_live.py`
  `tests/contract/test_usage_token_arithmetic_live.py`
  `tests/contract/test_usage_content_scale_live.py`
- Responses API
  `tests/contract/test_responses_*_live.py`

### Probe

- Prompt cache 可观测性
  `tests/probe/test_prompt_cache_latency_usage_live.py`
- service_tier 延迟探针
  `tests/probe/test_service_tier_latency_probe_live.py`
- finish_reason content_filter 观测
  `tests/probe/test_finish_reason_content_filter_live.py`

### Acceptance-only

- `logit_bias`
  `tests/acceptance/test_chat_logit_bias_live.py`
  只验证参数可接受、请求不报协议错、响应 shape 正常，不验证语义是否生效
- Chat 采样控制
  `tests/acceptance/test_chat_frequency_presence_penalty_live.py`
  `tests/acceptance/test_chat_temperature_live.py`
  只验证参数可接受和响应 shape 正常，不验证采样语义是否完全等价
- Responses 可选字段
  `tests/acceptance/test_responses_*_live.py`
  验证可选字段 acceptance 以及当前 compat-gap 错误 shape

## 开源化说明

- License: MIT
- Python: `>=3.9`
- 本地开发说明见 [CONTRIBUTING.md](./CONTRIBUTING.md)
- CI 模板见 [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)
