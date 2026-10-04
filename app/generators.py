import base64
import uuid
import logging

import aiofiles
from aiogram.types import BufferedInputFile
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
)
from .texts import deep_prompt

from config import AI_TOKEN

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


client = AsyncOpenAI(
    api_key=AI_TOKEN,
    base_url="https://routerai.ru/api/v1",
    # http_client=httpx.AsyncClient(
    #     proxies="http://{login}:{password}@{ip_address}:{http_port}",
    #     transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    # ),
)


async def gen_text(req, model="deepseek/deepseek-v4-flash"):
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": deep_prompt,  # base_prompt
            },
            {
                "role": "user",
                "content": req,
            },
        ],
        # verbosity="low",
        # temperature=0,
    )

    logger.debug(str(completion))

    file_name = uuid.uuid4()

    async with aiofiles.open(f"{file_name}.md", "w") as res:
        await res.write(str(completion.choices[0].message.content))

    return {
        "response": completion.choices[0].message.content,
        "usage": completion.usage.total_tokens,
    }


async def gen_image(
    req,
    model="recraft/recraft-v4.1-flash",
    reference: dict[str, str | dict[str, str]] | None = None,
):
    # response = await client.chat.completions.create(
    #     model=model,
    #     messages=[mes_input or {"role": "user", "content": req}],
    #     modalities=["image"],
    #     max_tokens=500,
    # )
    # raw_image_url = str(response.choices[0].message.images[0]["image_url"]["url"])
    #
    # byte_image_url = base64.b64decode(
    #     raw_image_url.removeprefix(
    #         re.search(r"data:image/\w{1,6};base64,", raw_image_url).group(0)
    #     )
    # )
    #
    # return {
    #     "image": BufferedInputFile(byte_image_url, filename="image.jpeg"),
    #     "usage": response.usage.total_tokens,
    # }

    extra_body = {"aspect_ratio": "1:1", "seed": 42}

    if reference:
        extra_body["input_references"] = [reference]

    response = await client.images.generate(
        model=model,
        prompt=req,
        n=1,
        extra_body=extra_body,
    )

    image_urls = []

    # Изображения возвращаются в base64 (data[].b64_json)
    for i, image in enumerate(response.data):
        image_url = base64.b64decode(image.b64_json)
        image_urls.append(image_url)
        with open(f"generated_image_{i}.png", "wb") as photo:
            photo.write(image_url)
        logger.debug(f"Image saved to generated_image_{i}.png")

    logger.debug(str(image_urls))

    for image in image_urls:
        byte_image_url = base64.b64decode(image.b64_json)

    return {
        "image": BufferedInputFile(byte_image_url, filename="image.jpeg"),
        "usage": response.usage.total_tokens,
    }


# Function to encode the image
async def encode_image(image_path):
    async with aiofiles.open(image_path, "rb") as image_file:
        return base64.b64encode(await image_file.read()).decode("utf-8")


async def get_image_url(file):
    base64_image = await encode_image(file)
    image_url = {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
    }

    # if req is not None:
    #     messages_input["content"].append({"type": "text", "text": req})
    return image_url


async def gen_vision_image(req, file, model="bytedance-seed/seedream-5-0-flash"):
    reference = await get_image_url(file=file)
    return await gen_image(req=req, model=model, reference=reference)


async def gen_vision(req, file, model="deepseek/deepseek-v4.1-flash"):
    try:
        image = await get_image_url(file=file)

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": deep_prompt,
                },
                {"role": "user", "content": [image]},
            ],
        )

        # Не даём коду упасть на response.choices[0].
        if not response.choices:
            logger.error(
                "RouterAI returned empty choices | model=%s | response=%r",
                model,
                response,
            )
            raise ValueError("API вернул ответ без choices")

        if not response.choices[0].message:
            logger.error(
                "RouterAI returned choice without message | model=%s | response=%r",
                model,
                response,
            )
            raise ValueError("API вернул choice без message")

        if response.choices[0].message.content is None:
            logger.error(
                "RouterAI returned choice without content | model=%s | response=%r",
                model,
                response,
            )
            raise ValueError("API вернул message без content")

        # Успешный ответ: оставляем твой исходный формат.
        return {
            "response": response.choices[0].message.content,
            "usage": response.usage.total_tokens if response.usage else 0,
        }

    except APIStatusError as error:
        logger.exception(
            "RouterAI API error | model=%s | status=%s | request_id=%s | body=%r",
            model,
            error.status_code,
            error.request_id,
            error.body,
        )
        raise

    except (APITimeoutError, APIConnectionError) as error:
        logger.exception(
            "RouterAI connection error | model=%s | error=%r",
            model,
            error,
        )
        raise

    except Exception as error:
        logger.exception(
            "gpt_vision error | model=%s | type=%s | error=%r",
            model,
            type(error),
            error,
        )
        raise


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
