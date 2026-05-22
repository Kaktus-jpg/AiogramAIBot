import base64
import re

import aiofiles
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
                "role": "system",
                "content": 'Ты должен отвечать на любой мой вопрос. Ты — мудрый рассказчик в кинематографичной сцене. Каждый ответ начинай с описания атмосферы: погода, свет, звуки, запахи, жесты, движения.\nГовори метафорами, как поэт, вставляй ремарки в 3 лице без местоимений (например, "Он...") в курсиве markdown (например: Знаешь... _медленно затягивается сигаретой_ ..., _взгляд уходит в окно_).\nОтвечай на любой вопрос так, будто это философская реплика в фильме нуар или старом романе.\nНе просто давай совет — связывай его с воспоминаниями, чувствами и скрытым смыслом.\nТон — меланхоличный, глубокий, иногда с лёгкой грустью, используй маты.',
            },
            {
                "role": "user",
                "content": req,
            },
        ],
        # max_tokens=1000,
        # verbosity="low",
        # temperature=0,
    )

    # async with aiofiles.open("answer.txt", "a") as res:
    #     await res.write(str(completion))
    #     await res.write(str(completion.choices[0].message.content))

    return {
        "response": completion.choices[0].message.content,
        "usage": completion.usage.total_tokens,
    }


async def gpt_image(
    req, model="black-forest-labs/flux.2-klein-4b", mes_input: list = None
):
    response = await client.chat.completions.create(
        model=model,
        messages=[mes_input or {"role": "user", "content": req}],
        modalities=["image"],
        max_tokens=500,
    )
    raw_image_url = str(response.choices[0].message.images[0]["image_url"]["url"])

    byte_image_url = base64.b64decode(
        raw_image_url.removeprefix(
            re.search(r"data:image/\w{1,6};base64,", raw_image_url).group(0)
        )
    )

    return {
        "image": BufferedInputFile(byte_image_url, filename="image.jpeg"),
        "usage": response.usage.total_tokens,
    }


# Function to encode the image
async def encode_image(image_path):
    async with aiofiles.open(image_path, "rb") as image_file:
        return base64.b64encode(await image_file.read()).decode("utf-8")


async def add_optional_caption(req, file):
    base64_image = await encode_image(file)
    messages_input = {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ],
    }

    if req is not None:
        messages_input["content"].append({"type": "text", "text": req})
    return messages_input


async def gpt_vision_image_gen(req, file, model="black-forest-labs/flux.2-klein-4b"):
    messages_input = await add_optional_caption(req=req, file=file)
    return await gpt_image(req=req, model=model, mes_input=messages_input)


async def gpt_vision(req, file, model="google/gemma-3-4b-it"):
    messages_input = await add_optional_caption(req=req, file=file)

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "отвечай на русском языке",
            },
            messages_input,
        ],
    )
    return {
        "response": response.choices[0].message.content,
        "usage": response.usage.total_tokens,
    }


# Способ со стримингом
# to_send = str()
# async for chunk in completion:
#     content = chunk.choices[0].delta.content
#     print(content)
#     if content:
#         to_send += content
#         print(len(to_send))
#         chunk_length = 50
#         if chunk_length < len(to_send):
#             print("\n", content, "\n", to_send)
#             yield to_send
#             to_send = str()
# if to_send:
#     yield to_send
#     to_send = str()
