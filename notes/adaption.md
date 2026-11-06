# Adaption Labs platform (https://docs.adaptionlabs.ai)

Data optimization + fine-tuning platform.
- **Adaptive Data**: upload a dataset, then adapt / augment / translate / localize / extend-trajectories / evaluate it. `invent` generates synthetic data from scratch.
- **AutoScientist**: optimizes data and training together. Recommends hyperparameters, fine-tunes (SFT, LoRA or full), lets you download the model.
- **Responses API**: OpenAI-style `/api/v1/responses` with hosted models and MCP tools.

## Access
- SDK: `pip install adaption` (v0.19.0 is in `.venv`; `uv` is at `~/.local/bin/uv`).
- `from adaption import Adaption; client = Adaption()` reads `ADAPTION_API_KEY` (stored in `.env`).
- Base URL `https://api.prod.adaptionlabs.ai`, header `Authorization: Bearer <key>`.

## Models (2026-11-05)
- Inference: glm-5.2, qwen3.5-397b, gemma-4-26b-a4b-it, qwen3.8-27b, deepseek-v4-flash, gemma-4-31b-it
- Training: gemma-3-4b-pt, gemma-4-31B-it(-VLM), gpt-oss-20b/120b, Llama-3.3-70B, Llama-4-Scout, Mixtral-8x7B,
  Nemotron-3 Nano/Super, Qwen3-4B-Base, Qwen3.5 2B/4B/9B/122B-A10B, Qwen3.6-35B-A3B

## Credits
- No balance endpoint is documented. Balance is visible at https://adaptionlabs.ai/app (settings/billing).
- The only API field with the team balance is `availableCredits` from
  `GET /api/v1/datasets/{id}/preprocessing-credits`, and that needs an existing dataset.
- Get cost estimates without spending credits: `datasets.adapt(..., estimate=True)`, and likewise `extend-trajectories`.
- Pricing is per output row (e.g. "10 credits per 100 output rows" for multimodal). Unused credits roll over; new credits are added monthly.

## Responses API pricing (docs, /inference-stacks/models, read 2026-11-05)
Credits per 1M tokens, input (cached) / output:
- gemma-4-31b-it 0.09 (0.05) / 0.34
- glm-5.2 1.40 (0.26) / 4.40
- qwen3.5-397b 0.55 (0.225) / 3.50
- gemma-4-26b-a4b-it 0.0765 (0.0425) / 0.255
- qwen3.8-27b 0.039 (0.0039) / 1.25
- deepseek-v4-flash 0.04444 (0.001414) / 0.13332
- glm-53-flash is listed in the docs, but `models.list(type="hosted")` does not return it for our key.
Unverified: how many dollars one credit is worth. Also unverified whether `{"type":"function"}` tools work
(the docs say other OpenAI-style tools are "forwarded to the model provider"). Responses include `usage` with reasoning_tokens.
- Verified 2026-11-05: `{"type":"function"}` tools work on deepseek-v4-flash. It returned a `function_call` item with JSON
  args and a call_id, plus `reasoning` and `message` items. `usage.cost` gives credits per call (one call: 432 tokens = 1.4e-5 credits).
- Balance on 2026-11-05: 1999.999985 credits (2000 minus the ~1.4e-5 smoke-test call). Check it with `.venv/bin/python scripts/balance.py`,
  which uses the kept dummy PDF dataset 29abb22d-2e86-4f50-b2e0-9db8373daedc. Never launch extraction on it, because that costs 1 credit.
  `.txt` uploads are NOT treated as document datasets (400 error); a PDF works.
- Budget (dashboard, 2026-11-05): 2000 credits, 1 credit = $1, credits never expire. Builder plan granted until 2027-02-05.
