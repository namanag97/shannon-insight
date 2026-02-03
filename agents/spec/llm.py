from openai import OpenAI
from config import GLM_API_KEY, GLM_BASE_URL, GLM_MODEL

# GLM uses OpenAI-compatible API
client = OpenAI(
    api_key=GLM_API_KEY,
    base_url=GLM_BASE_URL
)

def chat(messages: list, temperature: float = 0.7) -> str:
    """
    Send messages to GLM and get response.

    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature (0.0-1.0)

    Returns:
        Response content as string
    """
    response = client.chat.completions.create(
        model=GLM_MODEL,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content
