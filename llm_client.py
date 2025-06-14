"""
llm_client.py - Centralized LLM (OpenAI) API interactions for Witmo
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional

class LLMClient:
    def __init__(self, api_key: str, model: str = "o3"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat_completion(self, messages: List[Dict[str, Any]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
        )
        content: Optional[str] = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from LLM response.")
        return content
