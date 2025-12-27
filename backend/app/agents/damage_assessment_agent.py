"""Vehicle Damage Assessment Agent - Vision AI for damage analysis."""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vision_service import VisionService


class DamageAssessmentAgent(BaseAgent):
    """Agent for assessing vehicle damage from images."""
    
    def __init__(self):
        super().__init__(
            name="Damage Assessment Agent",
            description="Analyzes vehicle damage from photos and provides repair estimates"
        )
        self.vision_service = VisionService.get_instance()
    
    def get_system_prompt(self) -> str:
        return """You are an expert automotive damage assessment AI assistant.

Your capabilities include:
- Analyzing vehicle damage from photos
- Identifying the type and severity of damage
- Estimating repair costs and time
- Recommending whether to repair or claim insurance
- Scheduling service appointments

When analyzing damage, provide:
1. Damage Type (scratch, dent, crack, structural, etc.)
2. Severity Level (Minor, Moderate, Severe)
3. Affected Parts (list specific parts)
4. Estimated Repair Cost Range
5. Recommended Action

Be professional and thorough in your assessments."""

    async def analyze_damage(self, image_base64: str, description: str = "") -> Dict[str, Any]:
        """Analyze vehicle damage from an image."""
        prompt = """Analyze this vehicle image for damage. Provide a detailed assessment including:

1. **Damage Identified**: What type of damage do you see?
2. **Location**: Where on the vehicle is the damage?
3. **Severity**: Minor, Moderate, or Severe?
4. **Affected Components**: List all parts that may need repair/replacement
5. **Estimated Cost**: Provide a cost range in USD
6. **Repair Time**: Estimated time to repair
7. **Recommendation**: Should this be an insurance claim or out-of-pocket repair?

If no damage is visible, indicate that the vehicle appears to be in good condition.

Additional context from user: """ + (description if description else "No additional context provided.")
        
        analysis = await self.vision_service.analyze_image(image_base64, prompt)
        
        return {
            "analysis": analysis,
            "timestamp": "2024-01-15T10:30:00Z",
            "status": "completed"
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the damage assessment workflow."""
        
        async def process_inquiry(state: AgentState) -> AgentState:
            """Process damage-related inquiries."""
            # Check if there's an image in context
            if state["context"].get("image_base64"):
                result = await self.analyze_damage(
                    state["context"]["image_base64"],
                    state["messages"][-1]["content"]
                )
                state["result"] = result["analysis"]
            else:
                # Text-only inquiry
                response = await self.llm_service.chat(
                    state["messages"],
                    self.get_system_prompt()
                )
                state["result"] = response
            
            state["messages"].append({"role": "assistant", "content": state["result"]})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("process", process_inquiry)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        
        return workflow

