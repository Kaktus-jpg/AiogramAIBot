from openai import AsyncOpenAI
from config import AI_TOKEN
# import asyncio

client = AsyncOpenAI(
    api_key=AI_TOKEN,
    base_url="https://routerai.ru/api/v1",
    # http_client=httpx.AsyncClient(
    #     proxies="http://{login}:{password}@{ip_address}:{http_port}",
    #     transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    # ),
)


async def gpt_text(req, model="deepseek/deepseek-v4-flash"):
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "developer",
                "content": "use markdown parse mode for telegram api and write as little as possible, at the end ask how to help, don't use # as headers. write up to 1000 characters",
            },
            {
                "role": "user",
                "content": req,
            },
        ],
        max_tokens=1000,
        verbosity="low",
        temperature=0,
    )
    # return completion.choices[0].message.content
    return {
        "response": completion.choices[0].message.content,
        "usage": completion.usage.total_tokens,
    }


# print(asyncio.run(gpt_text('можно ли создать машину времени? объясни как можно подробнее')))

# to_send = str()
# async for chunk in completion:
#     content = chunk.choices[0].delta.content
#     print(content)
#     if content:
#         to_send += content
#         print(len(to_send))
#         if 100 < len(to_send):
#             print("\n", content, "\n", to_send)
#             yield to_send
#             to_send = str()
# if to_send:
#     yield to_send
#     to_send = str()
