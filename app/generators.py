from openai import AsyncOpenAI
from config import AI_TOKEN

client = AsyncOpenAI(
    api_key=AI_TOKEN,
    base_url="https://routerai.ru/api/v1",
    # http_client=httpx.AsyncClient(
    #     proxies="http://{login}:{password}@{ip_address}:{http_port}",
    #     transport=httpx.HTTPTransport(local_address="0.0.0.0")
    # )
)


async def gpt_text(req, model="deepseek/deepseek-v4-flash"):
    completion = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": req}],  # stream=True
    )
    return completion.choises[0].message.content

    # async for chunk in completion:
    #     content = chunk.choices[0].delta.content
    #     if content:
    #         logging.info(f"Чанк {content}")
    #         yield content
