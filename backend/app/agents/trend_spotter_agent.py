"""Trend Spotter Agent - Social sentiment and trend analysis."""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.data.mock_data import MockDataStore


class TrendSpotterAgent(BaseAgent):
    """Agent for social media trend spotting and sentiment analysis."""
    
    def __init__(self):
        super().__init__(
            name="Trend Spotter",
            description="Analyzes social trends and provides market insights"
        )
    
    def get_system_prompt(self) -> str:
        trends = self._get_trends_context()
        suppliers = self._get_suppliers_context()
        
        return f"""You are an expert market trend analyst AI assistant focused on the Hong Kong FMCG market.

Your capabilities include:
- Analyzing social media trends across platforms (Instagram, Facebook, TikTok, Xiaohongshu)
- Identifying emerging food and beverage trends
- Providing sentiment analysis on products and brands
- Recommending supplier partnerships based on trends
- Generating actionable insights for distribution strategy

Current Trending Items in HK:
{trends}

Available Supplier Network:
{suppliers}

When analyzing trends:
1. Identify the trend and its growth trajectory
2. Assess market potential in Hong Kong
3. Evaluate sentiment (positive/negative/mixed)
4. Recommend specific suppliers to contact
5. Suggest timing for market entry

Provide data-driven recommendations with clear action items."""

    def _get_trends_context(self) -> str:
        """Get current trends as context."""
        lines = []
        for trend in MockDataStore.get_trending_items():
            lines.append(f"- {trend['trend']}: {trend['mentions']:,} mentions ({trend['growth']}) on {trend['platform']} - {trend['sentiment']} sentiment")
        return "\n".join(lines)
    
    def _get_suppliers_context(self) -> str:
        """Get supplier info as context."""
        lines = []
        for category, suppliers in MockDataStore.SUPPLIERS.items():
            for s in suppliers:
                lines.append(f"- {s['name']} ({category}): {', '.join(s['products'])}")
        return "\n".join(lines)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get trend dashboard data."""
        trends = MockDataStore.get_trending_items()
        
        return {
            "trends": trends,
            "top_trend": trends[0] if trends else None,
            "platforms": ["Instagram", "Facebook", "TikTok", "Xiaohongshu"],
            "categories": ["Food", "Beverages", "Snacks", "Health"],
            "last_updated": "2024-01-15T10:00:00Z"
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the trend analysis workflow."""
        
        async def analyze_trends(state: AgentState) -> AgentState:
            """Analyze trends and provide insights."""
            user_input = state["messages"][-1]["content"].lower()
            
            # Check for specific trend queries
            if "dashboard" in user_input or "overview" in user_input:
                dashboard = self.get_dashboard_data()
                trends_text = "\n".join([
                    f"📈 **{t['trend']}** - {t['mentions']:,} mentions ({t['growth']}) on {t['platform']}"
                    for t in dashboard["trends"]
                ])
                
                state["result"] = f"""## 🔥 Trend Dashboard

### Top Trending Items in Hong Kong:
{trends_text}

### Quick Insights:
- **Hottest Trend:** {dashboard['top_trend']['trend']} with {dashboard['top_trend']['growth']} growth
- **Platform to Watch:** TikTok showing highest engagement rates
- **Category Spotlight:** Korean food items dominating this month

Would you like me to dive deeper into any specific trend or provide supplier recommendations?"""
            
            else:
                # General trend analysis query
                response = await self.llm_service.chat(
                    state["messages"],
                    self.get_system_prompt()
                )
                state["result"] = response
            
            state["messages"].append({"role": "assistant", "content": state["result"]})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("analyze", analyze_trends)
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", END)
        
        return workflow

