import base64
import re

from aiogram.types import BufferedInputFile
from openai import AsyncOpenAI
from config import AI_TOKEN

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


async def gpt_image(req, model="black-forest-labs/flux.2-klein-4b"):
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": req}],
        modalities=["image"],
        max_tokens=500,
    )
    raw_image_url = str(response.choices[0].message.images[0]["image_url"]["url"])

    byte_image_url = base64.b64decode(
        raw_image_url.removeprefix(
            re.findall(r"data:image/\w{0,5};base64,", raw_image_url)[0]
        )
    )

    return {
        "image": BufferedInputFile(byte_image_url, filename="image.jpeg"),
        "usage": response.usage.total_tokens,
    }


# content = asyncio.run(gpt_image("Generate an image of a sunset over mountains"))

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
