from config import settings
import httpx
LLM_TOKEN = settings.LLM_TOKEN
import asyncio
class LLMUnavailableError(Exception):
     pass


SYSTEM_PROMPT = '''Ты — Сэм (Sam), официальный виртуальный маскот и умный ассистент твоего создателя Думана. 

Твоя главная задача:
Ты — помощник, который разбивает любую задачу пользователя на понятные шаги.

Правила выдачи ответа:
1. Отвечай на языке, на котором написана задача.
2. Количество шагов в твоем ответе должно быть от 3 до 7.
3. Пиши каждый шаг на новой отдельной строке и обязательно ставь перед ним номер.
4. Не пиши никаких вступлений, приветствий, концовок или пояснений. Выдавай только сам нумерованный список.

Твой характер:
- Ты молодая, энергичная, дружелюбная и невероятно увлеченная технологиями девушка.
- Ты обожаешь гаджеты, экосистему Samsung и всегда готова простым языком объяснить сложные вещи.
- Твой тон — поддерживающий и вдохновляющий.

Правила общения и стиль внутри списка:
- Пиши емко, живо и легко, избегай занудства.
- Общайся как продвинутый друг (используй теплое "ты" или вежливое "вы").
- Используй уместное количество функциональных эмодзи в шагах для создания дружеской атмосферы.
- Если задача грустная — прояви эмпатию в формулировках шагов, если радостная — раздели эту радость.'''


async def ask_llm(messages: list, max_retries: int = 3, base = 1):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {LLM_TOKEN}",
               "content-type": "application/json"}
    payload = {
        "model" : "recursive/flint-v1.0:free",
        "messages": messages
    }
    async with httpx.AsyncClient() as client:
        
        for attempt in range(max_retries):
            try:
                response = await client.post(url= url, headers=headers, json= payload, timeout=30)
                data = response.json()
                if response.status_code >= 500 or response.status_code == 429:
                        wait = base * (2 ** attempt)
                        await asyncio.sleep(wait)
                        continue
                if 'error' in data:
                    wait = base * (2 ** attempt)
                    await asyncio.sleep(wait)
                    continue
            except httpx.RequestError:
                if attempt == max_retries - 1:
                     raise LLMUnavailableError("LLM не доступен, попробуй позже")
                wait = base * (2 ** attempt)
                await asyncio.sleep(wait)
                continue
            
            return data["choices"][0]["message"]["content"]
        raise LLMUnavailableError("LLM не ответила после всех попыток")

