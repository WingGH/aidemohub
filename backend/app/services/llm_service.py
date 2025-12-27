"""LLM Service using OpenRouter with streaming support."""
from typing import List, Dict, Any, Optional, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.callbacks import AsyncIteratorCallbackHandler
import asyncio
from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_MODEL, FALLBACK_MODEL


class LLMService:
    """Service for interacting with LLMs through OpenRouter."""
    
    _instances: Dict[str, "LLMService"] = {}
    
    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
            temperature=temperature,
            streaming=True,
            default_headers={
                "HTTP-Referer": "https://aihub.demo",
                "X-Title": "AI Hub Demo"
            }
        )
        # Non-streaming version for fallback
        self.llm_sync = ChatOpenAI(
            model=model,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
            temperature=temperature,
            streaming=False,
            default_headers={
                "HTTP-Referer": "https://aihub.demo",
                "X-Title": "AI Hub Demo"
            }
        )
    
    @classmethod
    def get_instance(cls, model: str = DEFAULT_MODEL, temperature: float = 0.7) -> "LLMService":
        """Get or create a singleton instance for a specific model."""
        key = f"{model}_{temperature}"
        if key not in cls._instances:
            cls._instances[key] = cls(model, temperature)
        return cls._instances[key]
    
    def _build_messages(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None):
        """Build LangChain message objects from dict format."""
        langchain_messages = []
        
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
        
        return langchain_messages
    
    async def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        """Send a chat message and get a response (non-streaming)."""
        langchain_messages = self._build_messages(messages, system_prompt)
        
        try:
            response = await self.llm_sync.ainvoke(langchain_messages)
            return response.content
        except Exception as e:
            # Try fallback model if primary fails
            if self.model != FALLBACK_MODEL:
                print(f"Primary model failed ({e}), trying fallback...")
                fallback_llm = ChatOpenAI(
                    model=FALLBACK_MODEL,
                    openai_api_key=OPENROUTER_API_KEY,
                    openai_api_base=OPENROUTER_BASE_URL,
                    temperature=self.temperature,
                    streaming=False,
                    default_headers={
                        "HTTP-Referer": "https://aihub.demo",
                        "X-Title": "AI Hub Demo"
                    }
                )
                response = await fallback_llm.ainvoke(langchain_messages)
                return response.content
            raise
    
    async def chat_stream(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Send a chat message and stream the response."""
        langchain_messages = self._build_messages(messages, system_prompt)
        
        try:
            async for chunk in self.llm.astream(langchain_messages):
                if chunk.content:
                    yield chunk.content
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
    
    def get_llm(self) -> ChatOpenAI:
        """Get the underlying LangChain LLM instance."""
        return self.llm
