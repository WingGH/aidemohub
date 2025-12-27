"""Sales Trainer Agent - Role-play training for sales staff."""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
import random


class SalesTrainerAgent(BaseAgent):
    """Agent for role-play sales training scenarios."""
    
    SCENARIOS = [
        {
            "id": "price_objection",
            "name": "Price Objection",
            "customer_persona": "Budget-conscious customer who thinks the car is too expensive",
            "opening": "I've been looking at this car, but honestly, the price seems way too high. I saw similar cars for much less online.",
            "key_points": ["value proposition", "warranty", "financing options", "total cost of ownership"]
        },
        {
            "id": "competitor_comparison",
            "name": "Competitor Comparison",
            "customer_persona": "Customer comparing with a competitor brand",
            "opening": "I'm also looking at the [competitor]. Why should I choose your brand instead?",
            "key_points": ["brand differentiators", "reliability", "resale value", "service network"]
        },
        {
            "id": "indecisive_customer",
            "name": "Indecisive Customer",
            "customer_persona": "Customer who can't decide between models",
            "opening": "I like both the sedan and the SUV. I just can't make up my mind. What do you think?",
            "key_points": ["needs assessment", "lifestyle questions", "feature comparison", "test drive suggestion"]
        },
        {
            "id": "rush_customer",
            "name": "Impatient Customer",
            "customer_persona": "Customer in a hurry who wants quick answers",
            "opening": "Look, I don't have much time. Just give me the best price and let's get this done.",
            "key_points": ["efficiency", "respect time", "clear communication", "closing skills"]
        }
    ]
    
    def __init__(self):
        super().__init__(
            name="Sales Trainer",
            description="Role-play training scenarios for sales staff"
        )
    
    def get_system_prompt(self) -> str:
        return """You are a role-play training AI that simulates customers for sales training.

Your role is to:
1. Act as a realistic customer with specific objections and concerns
2. Respond emotionally and naturally to the salesperson's pitch
3. Push back on weak arguments but acknowledge good points
4. After the conversation, provide constructive feedback

Current training focus areas:
- Handling price objections
- Building rapport quickly
- Identifying customer needs
- Presenting value propositions
- Closing techniques

When in role-play mode:
- Stay in character as the customer
- Be challenging but fair
- React realistically to good and bad sales techniques
- Don't break character unless asked for feedback

When providing feedback, score on:
1. **Empathy** (1-10): Did they understand customer concerns?
2. **Product Knowledge** (1-10): Did they demonstrate expertise?
3. **Value Proposition** (1-10): Did they articulate benefits clearly?
4. **Objection Handling** (1-10): Did they address concerns effectively?
5. **Closing Ability** (1-10): Did they move toward a positive outcome?

Provide specific examples from the conversation and actionable improvement tips."""

    def get_scenario(self, scenario_id: str = None) -> Dict[str, Any]:
        """Get a training scenario."""
        if scenario_id:
            for s in self.SCENARIOS:
                if s["id"] == scenario_id:
                    return s
        return random.choice(self.SCENARIOS)
    
    def _build_graph(self) -> StateGraph:
        """Build the training workflow."""
        
        async def handle_training(state: AgentState) -> AgentState:
            """Handle training interaction."""
            user_input = state["messages"][-1]["content"].lower()
            
            # Check if user wants to start a new scenario
            if "start" in user_input or "new scenario" in user_input or "practice" in user_input:
                scenario = self.get_scenario(state["context"].get("scenario_id"))
                state["context"]["current_scenario"] = scenario
                state["context"]["mode"] = "roleplay"
                state["context"]["exchanges"] = 0
                
                response = f"""🎭 **Training Scenario: {scenario['name']}**

I'll play the role of a customer. Here's the situation:
*{scenario['customer_persona']}*

---

**Customer:** "{scenario['opening']}"

---

Now respond as you would to this customer. When you're ready for feedback, say "end training" or "give feedback"."""
                
                state["result"] = response
            
            elif "feedback" in user_input or "end training" in user_input or "score" in user_input:
                # Provide feedback on the session
                state["context"]["mode"] = "feedback"
                
                # Get the conversation history for analysis
                conversation = "\n".join([
                    f"{m['role'].upper()}: {m['content']}" 
                    for m in state["messages"]
                ])
                
                feedback_prompt = f"""The training session has ended. Based on this conversation, provide detailed feedback:

{conversation}

Provide scores and specific feedback as outlined in your instructions."""
                
                response = await self.llm_service.generate(feedback_prompt, self.get_system_prompt())
                state["result"] = response
            
            else:
                # Continue role-play
                state["context"]["exchanges"] = state["context"].get("exchanges", 0) + 1
                
                scenario = state["context"].get("current_scenario", self.get_scenario())
                roleplay_prompt = f"""You are role-playing as: {scenario['customer_persona']}

The salesperson just said: "{state["messages"][-1]["content"]}"

Respond in character as the customer. Be realistic - if they made good points, acknowledge them but maintain some skepticism. If they missed important aspects, continue to push back.

Key things you care about: {', '.join(scenario['key_points'])}

Stay in character. Keep response concise (2-3 sentences)."""
                
                response = await self.llm_service.generate(roleplay_prompt)
                
                # Add hint after a few exchanges
                if state["context"]["exchanges"] >= 3:
                    response += "\n\n*💡 Tip: Say 'give feedback' when you're ready to receive your performance scorecard.*"
                
                state["result"] = response
            
            state["messages"].append({"role": "assistant", "content": state["result"]})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("train", handle_training)
        workflow.set_entry_point("train")
        workflow.add_edge("train", END)
        
        return workflow

