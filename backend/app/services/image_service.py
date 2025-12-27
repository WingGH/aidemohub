"""Image Generation Service using OpenRouter."""
import httpx
from typing import Optional, Dict, Any
from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL


class ImageService:
    """Service for generating images via AI."""
    
    _instance: Optional["ImageService"] = None
    
    # Sample generated image URLs for demo (since actual generation may be slow)
    DEMO_IMAGES = {
        "car": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800",
        "food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
        "product": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800",
        "sale": "https://images.unsplash.com/photo-1607083206869-4c7672e72a8a?w=800",
        "luxury": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800",
        "technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
        "health": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71?w=800",
        "organic": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=800",
        "korean": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=800",
        "default": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800",
    }
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
    
    @classmethod
    def get_instance(cls) -> "ImageService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_demo_image(self, prompt: str) -> str:
        """Get a relevant demo image based on prompt keywords."""
        prompt_lower = prompt.lower()
        
        for keyword, url in self.DEMO_IMAGES.items():
            if keyword in prompt_lower:
                return url
        
        return self.DEMO_IMAGES["default"]
    
    async def generate_image_prompt(self, content_brief: Dict[str, Any]) -> str:
        """Generate an image prompt based on marketing content brief."""
        product = content_brief.get("product", "product")
        audience = content_brief.get("audience", "general audience")
        tone = content_brief.get("tone", "professional")
        
        return f"Professional marketing photo for {product}, targeting {audience}, {tone} style, high quality, commercial photography"
    
    async def get_suggested_image(self, content_type: str, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Get a suggested image for marketing content."""
        prompt = await self.generate_image_prompt(brief)
        image_url = self.get_demo_image(brief.get("product", ""))
        
        return {
            "url": image_url,
            "prompt": prompt,
            "alt_text": f"Marketing image for {brief.get('product', 'product')}",
            "suggested_placement": "hero" if content_type == "social_media" else "banner"
        }


# Promotion templates
PROMOTION_TEMPLATES = [
    {
        "id": "summer_sale",
        "name": "Summer Sale Campaign",
        "description": "Hot summer deals with urgency messaging",
        "discount": "Up to 30% off",
        "duration": "Limited time",
        "channels": ["Instagram", "Facebook", "Email"],
        "tone": "Exciting and urgent",
        "cta": "Shop Now",
        "colors": ["#FF6B35", "#F7C59F", "#EFEFEF"]
    },
    {
        "id": "new_arrival",
        "name": "New Arrival Launch",
        "description": "Exclusive first-look at new products",
        "discount": "Early bird 15% off",
        "duration": "First 48 hours",
        "channels": ["Instagram Stories", "WeChat", "SMS"],
        "tone": "Exclusive and premium",
        "cta": "Be First",
        "colors": ["#2D3047", "#93B7BE", "#E0CA3C"]
    },
    {
        "id": "flash_sale",
        "name": "Flash Sale",
        "description": "24-hour mega savings event",
        "discount": "50% off selected items",
        "duration": "24 hours only",
        "channels": ["Push Notification", "Email", "Social"],
        "tone": "Urgent and exciting",
        "cta": "Grab It Now",
        "colors": ["#E63946", "#F1FAEE", "#1D3557"]
    },
    {
        "id": "loyalty_reward",
        "name": "Loyalty Member Exclusive",
        "description": "Special rewards for loyal customers",
        "discount": "Double points + 20% off",
        "duration": "Member week",
        "channels": ["App", "Email", "SMS"],
        "tone": "Appreciative and exclusive",
        "cta": "Claim Reward",
        "colors": ["#6B2D5C", "#F0A202", "#FFFFFF"]
    },
    {
        "id": "seasonal_korean",
        "name": "K-Food Festival",
        "description": "Korean food trends celebration",
        "discount": "Buy 2 Get 1 Free",
        "duration": "This weekend",
        "channels": ["Instagram", "Xiaohongshu", "TikTok"],
        "tone": "Fun and trendy",
        "cta": "Join the Trend",
        "colors": ["#E94560", "#0F3460", "#16213E"]
    }
]


def get_promotion_templates():
    """Get all promotion templates."""
    return PROMOTION_TEMPLATES


def get_promotion_by_id(promo_id: str):
    """Get a specific promotion template."""
    for promo in PROMOTION_TEMPLATES:
        if promo["id"] == promo_id:
            return promo
    return None

