"""Configuration settings for the AI Hub backend."""
import os
from dotenv import load_dotenv

# Load .env file (for development)
# Create a .env file in the backend directory with your API key
load_dotenv()

# OpenRouter Configuration
# Get API key from environment variable - REQUIRED
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("⚠️  WARNING: OPENROUTER_API_KEY not set. Please create a .env file with your API key.")
    print("   See .env.example for the required format.")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model Configuration - Using GPT-4o via OpenRouter
DEFAULT_MODEL = "openai/gpt-4o"
VISION_MODEL = "openai/gpt-4o"

# Fallback to Claude if GPT-4o fails
FALLBACK_MODEL = "anthropic/claude-3.5-sonnet"

# LLM Provider: "langchain", "openai" (recommended), or "litellm"
# "openai" uses httpx to call OpenRouter directly - simpler and more reliable
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
