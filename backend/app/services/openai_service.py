"""OpenAI Service - Direct OpenAI SDK integration with OpenRouter."""
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_MODEL, FALLBACK_MODEL


class OpenAIService:
    """Service for interacting with LLMs through OpenRouter using httpx."""
    
    _instances: Dict[str, "OpenAIService"] = {}
    
    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aihub.demo",
            "X-Title": "AI Hub Demo"
        }
    
    @classmethod
    def get_instance(cls, model: str = DEFAULT_MODEL, temperature: float = 0.7) -> "OpenAIService":
        """Get or create a singleton instance for a specific model."""
        key = f"{model}_{temperature}"
        if key not in cls._instances:
            cls._instances[key] = cls(model, temperature)
        return cls._instances[key]
    
    def _build_messages(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """Build message list with optional system prompt."""
        result = []
        
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        
        result.extend(messages)
        return result
    
    async def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        """Send a chat message and get a response (non-streaming)."""
        full_messages = self._build_messages(messages, system_prompt)
        
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": self.temperature,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                # Try fallback model if primary fails
                if self.model != FALLBACK_MODEL:
                    print(f"Primary model failed ({e}), trying fallback...")
                    payload["model"] = FALLBACK_MODEL
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                raise
    
    async def chat_stream(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Send a chat message and stream the response."""
        full_messages = self._build_messages(messages, system_prompt)
        
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": self.temperature,
            "stream": True,
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                import json
                                chunk = json.loads(data)
                                if chunk["choices"][0]["delta"].get("content"):
                                    yield chunk["choices"][0]["delta"]["content"]
                            except:
                                continue
            except Exception as e:
                # Fallback to non-streaming if streaming fails
                print(f"Streaming failed ({e}), falling back to non-streaming...")
                response = await self.chat(messages, system_prompt)
                yield response
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from a single prompt."""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, system_prompt)
    
    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Generate a streaming response from a single prompt."""
        messages = [{"role": "user", "content": prompt}]
        async for chunk in self.chat_stream(messages, system_prompt):
            yield chunk


# Quick test function
async def test_openai_service():
    """Test OpenAI Service connection to OpenRouter."""
    try:
        service = OpenAIService.get_instance()
        response = await service.chat([{"role": "user", "content": "Say 'Hello from OpenRouter!' and nothing else."}])
        print(f"✅ OpenAI Service Test Success: {response}")
        return True
    except Exception as e:
        print(f"❌ OpenAI Service Test Failed: {e}")
        return False

