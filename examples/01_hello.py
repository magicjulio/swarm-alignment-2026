"""Example 1: one plain call. Shows the response shape and what it cost."""
from dotenv import load_dotenv
from adaption import Adaption

load_dotenv("../.env")
client = Adaption()

resp = client.responses.create(
    model="deepseek-v4-flash",
    instructions="You are a terse assistant.",   # = system prompt
    input="In one or two sentences: what is a split attack in multi-agent AI safety?",
    max_output_tokens=500,
)

# A response holds a list of output items: "reasoning", "message", "function_call", ...
for item in resp.output:
    print(f"[{item.type}]")
    if item.type == "message":
        for part in item.content:
            print("  ", part.text)
    if item.type == "reasoning":
        for part in item.content:
            print("  ", part.text)

print("\nusage:", resp.usage)
