from bot.services.llm import ask_llm, SYSTEM_PROMPT
import asyncio

text = 'Разобраться с делами'

messages = [{
    "role": "system",
    "content": SYSTEM_PROMPT
    },
    {
        "role": "user",
        "content": text
    }]

print(asyncio.run(ask_llm(messages=messages)))