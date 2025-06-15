from loguru import logger
from history import History
from image import Image


def generate_completion(
    question: str,
    *,
    image: Image | None = None,
    history: History | None = None,
    llm_client,
    SYSTEM_PROMPT,
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
    ai_response = llm_client.chat_completion(messages)

    if history:
        history.append(user_message)
        history.append({"role": "assistant", "content": ai_response})

    return ai_response
