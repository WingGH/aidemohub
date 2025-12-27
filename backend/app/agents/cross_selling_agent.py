"""Cross-Selling Agent - Intelligent product recommendations."""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.data.mock_data import MockDataStore


class CrossSellingAgent(BaseAgent):
    """Agent for cross-selling recommendations across product categories."""
    
    def __init__(self):
        super().__init__(
            name="Cross-Selling Intelligence",
            description="Provides intelligent cross-sell recommendations for automotive and FMCG"
        )
    
    def get_system_prompt(self) -> str:
        parts = self._get_parts_context()
        products = self._get_product_context()
        
        return f"""You are an expert cross-selling AI assistant for both automotive parts and FMCG products.

Your capabilities include:
- Analyzing customer purchase history and current orders
- Recommending complementary products
- Creating bundled offers with attractive pricing
- Generating sales pitches for account managers
- Identifying upselling opportunities

AUTOMOTIVE PARTS INVENTORY:
{parts}

FMCG PRODUCT CATEGORIES:
{products}

Cross-selling strategies:
1. **Complementary Products**: Items that go naturally together
2. **Maintenance Bundles**: Group related service items
3. **Upgrade Opportunities**: Premium versions of purchased items
4. **Seasonal Relevance**: Time-appropriate recommendations
5. **Customer Profile Match**: Based on similar customer behavior

When making recommendations:
- Explain WHY these items go together
- Provide bundled pricing with discount
- Generate a brief sales pitch
- Show potential margin/revenue impact"""

    def _get_parts_context(self) -> str:
        """Get parts inventory context."""
        lines = []
        for part in MockDataStore.PARTS:
            lines.append(f"- {part['name']}: ${part['price']} (Stock: {part['stock']})")
        return "\n".join(lines)
    
    def _get_product_context(self) -> str:
        """Get FMCG product context."""
        categories = set()
        for wh in MockDataStore.WAREHOUSES.values():
            for sku, item in wh["inventory"].items():
                categories.add(item["name"])
        return "\n".join([f"- {c}" for c in categories])
    
    def get_recommendations(self, current_items: List[str], customer_id: str = None, domain: str = "auto") -> Dict[str, Any]:
        """Get cross-sell recommendations."""
        recommendations = []
        
        if domain == "auto":
            # Automotive cross-selling
            current_lower = [item.lower() for item in current_items]
            
            if any("brake pad" in item for item in current_lower):
                recommendations.append({
                    "bundle_name": "Complete Brake Service Bundle",
                    "items": [
                        {"name": "Brake Fluid", "price": 25, "reason": "Essential for brake system"},
                        {"name": "Brake Rotors", "price": 180, "reason": "Often worn with pads"},
                        {"name": "Brake Sensors", "price": 65, "reason": "Ensure proper warning system"}
                    ],
                    "bundle_price": 245,
                    "regular_price": 270,
                    "savings": 25,
                    "pitch": "Since you're replacing brake pads, ensure complete brake system health with our service bundle - includes fluid flush, rotor inspection, and sensor check at 10% off."
                })
            
            if any("oil" in item for item in current_lower):
                recommendations.append({
                    "bundle_name": "Engine Care Package",
                    "items": [
                        {"name": "Oil Filter", "price": 15, "reason": "Replace with every oil change"},
                        {"name": "Air Filter", "price": 35, "reason": "Improve engine performance"}
                    ],
                    "bundle_price": 45,
                    "regular_price": 50,
                    "savings": 5,
                    "pitch": "Complete your oil change with fresh filters - our Engine Care Package saves you a return trip and 10% on parts."
                })
        
        else:
            # FMCG cross-selling
            customer = MockDataStore.CUSTOMERS.get(customer_id, {})
            current_purchases = customer.get("purchase_history", [])
            
            fmcg_recs = MockDataStore.get_cross_sell_recommendations(current_purchases, customer_id)
            for rec in fmcg_recs:
                recommendations.append({
                    "category": rec["category"],
                    "items": rec["items"],
                    "reason": rec["reason"],
                    "pitch": f"Based on purchase patterns, customers like you also love our {rec['category']} selection. {rec['reason']}."
                })
        
        return {
            "current_items": current_items,
            "recommendations": recommendations,
            "domain": domain
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the cross-selling workflow."""
        
        async def analyze_and_recommend(state: AgentState) -> AgentState:
            """Analyze context and provide recommendations."""
            context = state["context"]
            
            # Check for specific cross-sell request
            if context.get("current_items"):
                recs = self.get_recommendations(
                    context["current_items"],
                    context.get("customer_id"),
                    context.get("domain", "auto")
                )
                
                # Format response
                response_parts = ["## 🛒 Cross-Sell Recommendations\n"]
                response_parts.append(f"**Based on current selection:** {', '.join(recs['current_items'])}\n")
                
                for i, rec in enumerate(recs["recommendations"], 1):
                    response_parts.append(f"### Recommendation {i}: {rec.get('bundle_name', rec.get('category', 'Suggested Items'))}")
                    
                    if "items" in rec and isinstance(rec["items"], list):
                        if isinstance(rec["items"][0], dict):
                            for item in rec["items"]:
                                response_parts.append(f"- **{item['name']}** (${item.get('price', 'N/A')}) - {item.get('reason', '')}")
                        else:
                            for item in rec["items"]:
                                response_parts.append(f"- {item}")
                    
                    if rec.get("bundle_price"):
                        response_parts.append(f"\n💰 **Bundle Price:** ${rec['bundle_price']} (Save ${rec['savings']})")
                    
                    response_parts.append(f"\n📢 **Sales Pitch:** \"{rec['pitch']}\"\n")
                
                state["result"] = "\n".join(response_parts)
            else:
                # General cross-selling inquiry
                response = await self.llm_service.chat(
                    state["messages"],
                    self.get_system_prompt()
                )
                state["result"] = response
            
            state["messages"].append({"role": "assistant", "content": state["result"]})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("recommend", analyze_and_recommend)
        workflow.set_entry_point("recommend")
        workflow.add_edge("recommend", END)
        
        return workflow

