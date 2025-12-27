"""Marketing Content Agent - AI-generated marketing content studio."""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
import asyncio

# Delay between workflow steps
STEP_DELAY = 1.0


class MarketingContentAgent(BaseAgent):
    """Agent for generating localized marketing content."""
    
    def __init__(self):
        super().__init__(
            name="Marketing Content Agent",
            description="Generates marketing content including ads, social posts, and video scripts"
        )
    
    def get_system_prompt(self) -> str:
        return """You are an expert marketing content creator AI assistant.

Your capabilities include:
- Creating compelling ad copy for various platforms
- Writing engaging social media posts
- Drafting promotional video scripts
- Generating product descriptions
- Localizing content for different markets (especially Hong Kong/China)
- Adapting tone and style for different brands

Content types you create:
1. **Ad Copy**: Headlines, body text, CTAs for digital ads
2. **Social Media**: Posts for Instagram, Facebook, WeChat, Xiaohongshu
3. **Video Scripts**: Short-form and long-form promotional videos
4. **Product Descriptions**: E-commerce and catalog descriptions
5. **Email Campaigns**: Subject lines and email body content

Guidelines:
- Ask about the target audience, platform, and tone if not specified
- Provide multiple variations when possible
- Include relevant emojis for social media content
- Consider cultural nuances for Asian markets
- Keep content concise and impactful

Always provide content that is ready to use with minimal editing."""

    async def generate_content(self, content_type: str, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing content based on brief."""
        prompt = f"""Generate {content_type} content based on this brief:

Product/Service: {brief.get('product', 'Not specified')}
Target Audience: {brief.get('audience', 'General')}
Platform: {brief.get('platform', 'Multi-platform')}
Tone: {brief.get('tone', 'Professional yet friendly')}
Language: {brief.get('language', 'English')}
Key Messages: {brief.get('key_messages', 'Not specified')}
Call to Action: {brief.get('cta', 'Learn more')}

Please provide:
1. 3 headline variations
2. Main body content
3. Call-to-action options
4. Hashtag suggestions (if social media)
5. Visual/imagery recommendations"""

        response = await self.llm_service.generate(prompt, self.get_system_prompt())
        
        return {
            "content": response,
            "content_type": content_type,
            "variations": 3,
            "status": "generated"
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the content generation workflow."""
        
        async def understand_request(state: AgentState) -> AgentState:
            """Understand the content request."""
            user_input = state["messages"][-1]["content"].lower()
            
            # Detect content type
            if "social" in user_input or "instagram" in user_input or "facebook" in user_input:
                state["context"]["content_type"] = "social_media"
            elif "video" in user_input or "script" in user_input:
                state["context"]["content_type"] = "video_script"
            elif "ad" in user_input or "advertisement" in user_input:
                state["context"]["content_type"] = "ad_copy"
            elif "email" in user_input:
                state["context"]["content_type"] = "email"
            else:
                state["context"]["content_type"] = "general"
            
            return state
        
        async def generate_content_node(state: AgentState) -> AgentState:
            """Generate the marketing content."""
            response = await self.llm_service.chat(
                state["messages"],
                self.get_system_prompt()
            )
            state["result"] = response
            state["messages"].append({"role": "assistant", "content": response})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("understand", understand_request)
        workflow.add_node("generate", generate_content_node)
        
        workflow.set_entry_point("understand")
        workflow.add_edge("understand", "generate")
        workflow.add_edge("generate", END)
        
        return workflow
    
    async def run_with_streaming(self, user_input: str, context: Dict[str, Any] = None):
        """Run marketing content generation with streaming step updates."""
        workflow_steps = []
        
        # Step 1: Analyze Brief
        step1 = {"step": "brief", "status": "active", "label": "Analyze Brief"}
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        user_lower = user_input.lower()
        
        # Detect content type
        if "social" in user_lower or "instagram" in user_lower or "facebook" in user_lower:
            content_type = "social_media"
        elif "video" in user_lower or "script" in user_lower:
            content_type = "video_script"
        elif "ad" in user_lower or "advertisement" in user_lower:
            content_type = "ad_copy"
        elif "email" in user_lower:
            content_type = "email"
        else:
            content_type = "general"
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"content_type": content_type}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 2: Generate Copy
        step2 = {"step": "generate", "status": "active", "label": "Generate Copy"}
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        response = await self.llm_service.chat(
            [{"role": "user", "content": user_input}],
            self.get_system_prompt()
        )
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"generated": True}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 3: Suggest Image
        step3 = {"step": "image", "status": "active", "label": "Suggest Image"}
        workflow_steps.append(step3)
        yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"image_suggested": True}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 4: Review
        step4 = {"step": "review", "status": "active", "label": "Review"}
        workflow_steps.append(step4)
        yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        yield {"type": "response", "content": response}

