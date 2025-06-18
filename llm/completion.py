from loguru import logger
from image import Image
from .history import History
from .openai_client import openai_client

def generate_completion(
    question: str,
    *,
    image: Image | None = None,
    history: History | None = None,
    SYSTEM_PROMPT,
    model: str = "o3",
) -> str:
    """
    Handles message marshalling for both text and image+text completions, calls LLM, updates history.
    """
    logger.info(f"Sending message to LLM... (image={'yes' if image else 'no'})")
    logger.info(f"Request: {question}")

    system_message = SYSTEM_PROMPT
    messages = [{"role": "system", "content": system_message}]

    if history:
        messages.extend(history.last(10))

    # Prepare user message:
    if image:
        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image.to_base64()}"},
                },
            ],
        }
    else:
        user_message = {"role": "user", "content": question}

    messages.append(user_message)

    # Call OpenAI model:
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,  # type: ignore
    )
    content = response.choices[0].message.content
    if not content:
        logger.error("Received empty response from LLM.")
        content = "<<no response>>"

    if history is not None:
        logger.debug(f"Adding interaction to history")
        history.append(user_message)
        history.append({"role": "assistant", "content": content})
    else:
        logger.debug("No history provided, skipping history update.")

    return content
