"""Vision Service for image analysis using OpenRouter."""
import base64
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, VISION_MODEL, FALLBACK_MODEL


class VisionService:
    """Service for vision/multimodal AI tasks."""
    
    _instance: Optional["VisionService"] = None
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=VISION_MODEL,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
            temperature=0.3,
            max_tokens=4096,
            default_headers={
                "HTTP-Referer": "https://aihub.demo",
                "X-Title": "AI Hub Demo"
            }
        )
        # Fallback vision model
        self.fallback_llm = ChatOpenAI(
            model=FALLBACK_MODEL,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
            temperature=0.3,
            max_tokens=4096,
            default_headers={
                "HTTP-Referer": "https://aihub.demo",
                "X-Title": "AI Hub Demo"
            }
        )
    
    @classmethod
    def get_instance(cls) -> "VisionService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def analyze_image(self, image_base64: str, prompt: str, mime_type: str = "image/jpeg") -> str:
        """Analyze an image with a text prompt."""
        message = HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        )
        
        try:
            response = await self.llm.ainvoke([message])
            return response.content
        except Exception as e:
            print(f"Vision model failed ({e}), trying fallback...")
            response = await self.fallback_llm.ainvoke([message])
            return response.content
    
    async def analyze_image_from_url(self, image_url: str, prompt: str) -> str:
        """Analyze an image from a URL."""
        message = HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        )
        
        try:
            response = await self.llm.ainvoke([message])
            return response.content
        except Exception as e:
            print(f"Vision model failed ({e}), trying fallback...")
            response = await self.fallback_llm.ainvoke([message])
            return response.content
