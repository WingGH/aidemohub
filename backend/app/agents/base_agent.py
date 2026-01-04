"""Base Agent class for all AI agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from app.config import LLM_PROVIDER


def get_llm_service():
    """Get the appropriate LLM service based on configuration."""
    if LLM_PROVIDER == "openai":
        # Recommended: Direct httpx calls to OpenRouter - simpler and reliable
        from app.services.openai_service import OpenAIService
        return OpenAIService.get_instance()
    else:
        # Alternative: LangChain wrapper
        from app.services.llm_service import LLMService
        return LLMService.get_instance()


class AgentState(TypedDict):
    """Base state for agent workflows."""
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    current_step: str
    result: Optional[str]


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm_service = get_llm_service()
        self.graph = self._build_graph()
    
    @abstractmethod
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for this agent."""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    def _build_messages_with_history(
        self, 
        user_input: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build messages list including conversation history."""
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_input})
        return messages
    
    async def run(
        self, 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Run the agent with user input and optional conversation history."""
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        initial_state: AgentState = {
            "messages": messages,
            "context": context or {},
            "current_step": "start",
            "result": None
        }
        
        # Compile and run the graph
        app = self.graph.compile()
        final_state = await app.ainvoke(initial_state)
        
        return {
            "response": final_state.get("result", ""),
            "messages": final_state.get("messages", []),
            "context": final_state.get("context", {})
        }
    
    async def chat(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> str:
        """Simple chat interface without full workflow."""
        return await self.llm_service.chat(messages, self.get_system_prompt())

