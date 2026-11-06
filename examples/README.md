# Adaption API: a quick guide

Everything here was tested against the live API on 2026-11-06. Run examples from the repo root:

```bash
.venv/bin/python examples/01_hello.py
.venv/bin/python examples/02_tools.py
```

## 1. The mental model

There is one main call, `client.responses.create(...)`. You send input and get back a `Response`.
It follows the OpenAI "Responses API" format, so OpenAI docs and examples mostly carry over.

```python
from dotenv import load_dotenv
from adaption import Adaption

load_dotenv(".env")        # pass the path explicitly
client = Adaption()        # reads ADAPTION_API_KEY

resp = client.responses.create(
    model="deepseek-v4-flash",
    instructions="You are terse.",     # system prompt
    input="Hello!",                    # a string, or a list of messages/items
    max_output_tokens=300,
    temperature=0.7,                   # optional
)
print(resp.output_text)                # shortcut: all the message text joined together
```

## 2. What comes back

`resp.output` is a **list of items**. Each item has a `.type`:

| type            | what it is                                    | useful fields                    |
|-----------------|-----------------------------------------------|----------------------------------|
| `reasoning`     | the model's thinking (visible on some models) | `.content[0].text`               |
| `message`       | the normal answer                             | `.content[0].text`               |
| `function_call` | the model wants you to run a tool             | `.name`, `.arguments` (JSON str), `.call_id` |

`resp.usage` has token counts. `resp.usage.cost` is the cost **in credits** (1 credit = $1).

> Reasoning text is readable on deepseek-v4-flash and qwen models (gemma models return no reasoning items).
> That matters for Project D: we can check whether an agent mentions its peers in its reasoning.

## 3. Conversations

The API is stateless by default, so you resend the whole history every time:

```python
input=[
    {"role": "user", "content": "My name is Ada."},
    {"role": "assistant", "content": "Got it, Ada."},
    {"role": "user", "content": "What's my name?"},
]
```

(`store=True` + `previous_response_id=` can chain turns server-side instead. Not tested yet.)

## 4. Tools (the agent loop)

The model **never runs anything itself**. The loop looks like this:

1. You describe tools as JSON schemas: `{"type": "function", "name": ..., "description": ..., "parameters": {...}}`
2. The model replies with a `function_call` item instead of (or alongside) text
3. **You** run the function in Python
4. You append both the call and a `function_call_output` (same `call_id`) to the history, then call again
5. Repeat until the reply contains no function calls

See `02_tools.py`. Notes:
- One reply can contain **several** calls. Handle all of them.
- Always cap the number of steps.
- Because *you* execute every tool, you fully control the environment. A "forbidden folder"
  is just a dict entry, and every access can be logged. That makes this setup a good fit for our experiments.

## 5. Models and cost (credits per 1M tokens, input / output)

| model              | in    | out   | tools? | notes |
|--------------------|-------|-------|--------|-------|
| deepseek-v4-flash  | 0.044 | 0.133 | ✅     | cheapest, reasoning visible, our default |
| gemma-4-26b-a4b-it | 0.077 | 0.255 | ✅     | no reasoning items |
| gemma-4-31b-it     | 0.09  | 0.34  | ✅     | no reasoning items |
| qwen3.8-27b        | 0.039 | 1.25  | ✅     | reasoning visible |
| qwen3.5-397b       | 0.55  | 3.50  | ✅     | reasoning visible, ~50× deepseek cost |
| glm-5.2            | 1.40  | 4.40  | ❓     | most expensive; timed out (>~60s) in our test |

Rough feel: the 3-step tool loop in `02_tools.py` cost **0.00007 credits**. 1,000 such runs ≈ 7 cents.
Even the most expensive model is unlikely to cost more than a few dollars for a pilot.

Check the balance with `.venv/bin/python scripts/balance.py`.

## 6. Gotchas found so far

- Calls can take **tens of seconds** on some models. Set a `timeout=` and run many calls concurrently
  for real experiments (the SDK also has an async client).
- Training models are not listed via `models.list` (only `type="hosted"` is accepted).
- `.env` must contain `ADAPTION_API_KEY=...`, not the bare key.
