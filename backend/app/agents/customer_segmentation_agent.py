"""Customer Segmentation Agent - ML-powered customer tagging and segmentation."""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.data.mock_data import MockDataStore
import asyncio
import math

# Delay between workflow steps
STEP_DELAY = 1.0


class CustomerSegmentationAgent(BaseAgent):
    """Agent for ML-based customer segmentation and tagging."""
    
    def __init__(self):
        super().__init__(
            name="Customer Segmentation Agent",
            description="Segments customers using ML models based on purchasing behavior"
        )
    
    def get_system_prompt(self) -> str:
        segments = self._get_segments_context()
        return f"""You are an expert customer analytics AI assistant specialized in RFM segmentation and behavioral analysis.

Your capabilities include:
- Analyzing customer purchasing behavior using RFM (Recency, Frequency, Monetary) analysis
- Segmenting customers into actionable groups
- Predicting customer lifetime value (LTV)
- Identifying churn risk and intervention opportunities
- Generating personalized marketing recommendations

Available Customer Segments:
{segments}

When analyzing customers, provide:
1. **RFM Scores**: Recency, Frequency, Monetary value scores
2. **Segment Assignment**: Best-fit customer segment
3. **Behavioral Insights**: Key patterns and preferences
4. **Churn Risk**: Probability of customer leaving
5. **Recommendations**: Specific actions to increase engagement
6. **Predicted LTV**: Expected lifetime value

Always explain the reasoning behind segment assignments and recommendations."""

    def _get_segments_context(self) -> str:
        """Get segment definitions as context."""
        lines = []
        for name, info in MockDataStore.CUSTOMER_SEGMENTS.items():
            lines.append(f"- **{name}**: {info['description']}")
        return "\n".join(lines)
    
    def calculate_rfm_scores(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate RFM scores for a customer (ML simulation)."""
        from datetime import datetime
        
        # Calculate days since last order
        last_order = datetime.strptime(customer["last_order_date"], "%Y-%m-%d")
        days_since = (datetime.now() - last_order).days
        
        # Recency score (1-5, 5 is most recent)
        if days_since <= 7:
            r_score = 5
        elif days_since <= 30:
            r_score = 4
        elif days_since <= 60:
            r_score = 3
        elif days_since <= 90:
            r_score = 2
        else:
            r_score = 1
        
        # Frequency score (1-5, based on order frequency)
        freq_days = customer["order_frequency_days"]
        if freq_days <= 7:
            f_score = 5
        elif freq_days <= 14:
            f_score = 4
        elif freq_days <= 30:
            f_score = 3
        elif freq_days <= 60:
            f_score = 2
        else:
            f_score = 1
        
        # Monetary score (1-5, based on total spend)
        spend = customer["total_spend"]
        if spend >= 20000:
            m_score = 5
        elif spend >= 10000:
            m_score = 4
        elif spend >= 5000:
            m_score = 3
        elif spend >= 1000:
            m_score = 2
        else:
            m_score = 1
        
        # Calculate composite score
        rfm_score = r_score * 100 + f_score * 10 + m_score
        
        return {
            "recency_score": r_score,
            "frequency_score": f_score,
            "monetary_score": m_score,
            "rfm_composite": rfm_score,
            "days_since_last_order": days_since
        }
    
    def predict_churn_risk(self, customer: Dict[str, Any], rfm: Dict[str, Any]) -> Dict[str, Any]:
        """Predict churn risk using simulated ML model."""
        # Simulated churn risk calculation
        risk_factors = []
        base_risk = 0.1
        
        # Factor 1: Recency
        if rfm["recency_score"] <= 2:
            base_risk += 0.25
            risk_factors.append("Long time since last purchase")
        
        # Factor 2: Declining frequency
        if rfm["frequency_score"] <= 2:
            base_risk += 0.15
            risk_factors.append("Low purchase frequency")
        
        # Factor 3: Low engagement
        if customer["email_open_rate"] < 0.2:
            base_risk += 0.1
            risk_factors.append("Low email engagement")
        
        # Factor 4: Returns
        if customer["returns_count"] > 2:
            base_risk += 0.1
            risk_factors.append("High return rate")
        
        # Factor 5: No reviews
        if customer["review_count"] == 0:
            base_risk += 0.05
            risk_factors.append("No product reviews")
        
        churn_prob = min(base_risk, 0.95)
        
        risk_level = "Low" if churn_prob < 0.3 else "Medium" if churn_prob < 0.6 else "High"
        
        return {
            "churn_probability": churn_prob,
            "risk_level": risk_level,
            "risk_factors": risk_factors
        }
    
    def generate_recommendations(self, customer: Dict[str, Any], segment: str, churn: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Segment-based recommendations
        segment_actions = MockDataStore.CUSTOMER_SEGMENTS.get(segment, {}).get("recommended_actions", [])
        recommendations.extend(segment_actions)
        
        # Churn-based recommendations
        if churn["risk_level"] == "High":
            recommendations.append("🚨 Immediate outreach with special retention offer")
            recommendations.append("Schedule personal call from account manager")
        elif churn["risk_level"] == "Medium":
            recommendations.append("Send personalized win-back email campaign")
        
        # Behavior-based recommendations
        if customer["promo_sensitivity"] == "high":
            recommendations.append("Include discount codes in all communications")
        
        if len(customer["categories_purchased"]) <= 2:
            recommendations.append("Cross-sell opportunity: introduce new categories")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def segment_customer(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Full customer segmentation analysis."""
        rfm = self.calculate_rfm_scores(customer)
        churn = self.predict_churn_risk(customer, rfm)
        
        # Determine segment based on RFM
        if rfm["rfm_composite"] >= 444:
            segment = "Champion"
        elif rfm["rfm_composite"] >= 333:
            segment = "VIP"
        elif rfm["rfm_composite"] >= 222 and rfm["recency_score"] >= 3:
            segment = "Growing"
        elif rfm["rfm_composite"] >= 222:
            segment = "Regular"
        elif rfm["recency_score"] <= 2 and rfm["frequency_score"] >= 3:
            segment = "At Risk"
        else:
            segment = "Declining"
        
        recommendations = self.generate_recommendations(customer, segment, churn)
        
        return {
            "customer_id": customer["customer_id"],
            "customer_name": customer["name"],
            "rfm_analysis": rfm,
            "segment": segment,
            "segment_info": MockDataStore.CUSTOMER_SEGMENTS.get(segment, {}),
            "churn_risk": churn,
            "predicted_ltv": customer["predicted_ltv"],
            "recommendations": recommendations
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the segmentation workflow."""
        
        async def analyze_customers(state: AgentState) -> AgentState:
            """Analyze and segment customers."""
            user_input = state["messages"][-1]["content"].lower()
            
            # Check for specific customer
            customer_id = None
            for customer in MockDataStore.CUSTOMER_BEHAVIOR:
                if customer["customer_id"].lower() in user_input or customer["name"].lower() in user_input:
                    customer_id = customer["customer_id"]
                    break
            
            # Check for segment filter
            segment_filter = None
            for seg in ["champion", "vip", "growing", "regular", "at risk", "declining"]:
                if seg in user_input:
                    segment_filter = seg.title()
                    break
            
            if "all customers" in user_input or "overview" in user_input or "dashboard" in user_input:
                # Show all customers segmentation
                customers = MockDataStore.get_customer_behavior()
                results = [self.segment_customer(c) for c in customers]
                
                # Group by segment
                segment_counts = {}
                total_ltv = 0
                for r in results:
                    seg = r["segment"]
                    segment_counts[seg] = segment_counts.get(seg, 0) + 1
                    total_ltv += r["predicted_ltv"]
                
                response_parts = [
                    "## 👥 Customer Segmentation Dashboard\n",
                    f"**Total Customers:** {len(customers)}",
                    f"**Total Predicted LTV:** ${total_ltv:,}\n",
                    "### Segment Distribution:\n"
                ]
                
                for seg, count in sorted(segment_counts.items(), key=lambda x: -x[1]):
                    info = MockDataStore.CUSTOMER_SEGMENTS.get(seg, {})
                    color_emoji = {"Champion": "🏆", "VIP": "⭐", "Growing": "📈", "Regular": "👤", "At Risk": "⚠️", "Declining": "📉"}.get(seg, "👤")
                    response_parts.append(f"{color_emoji} **{seg}**: {count} customers")
                
                response_parts.append("\n### Customer Details:\n")
                
                for r in results:
                    rfm = r["rfm_analysis"]
                    churn = r["churn_risk"]
                    risk_emoji = "🟢" if churn["risk_level"] == "Low" else "🟡" if churn["risk_level"] == "Medium" else "🔴"
                    response_parts.append(
                        f"**{r['customer_name']}** ({r['customer_id']}) - {r['segment']} | "
                        f"RFM: {rfm['recency_score']}{rfm['frequency_score']}{rfm['monetary_score']} | "
                        f"Risk: {risk_emoji} | LTV: ${r['predicted_ltv']:,}"
                    )
                
                state["result"] = "\n".join(response_parts)
            
            elif customer_id:
                # Analyze specific customer
                customers = MockDataStore.get_customer_behavior(customer_id)
                if customers:
                    customer = customers[0]
                    result = self.segment_customer(customer)
                    
                    rfm = result["rfm_analysis"]
                    churn = result["churn_risk"]
                    seg_info = result["segment_info"]
                    
                    risk_emoji = "🟢" if churn["risk_level"] == "Low" else "🟡" if churn["risk_level"] == "Medium" else "🔴"
                    seg_emoji = {"Champion": "🏆", "VIP": "⭐", "Growing": "📈", "Regular": "👤", "At Risk": "⚠️", "Declining": "📉"}.get(result["segment"], "👤")
                    
                    response_parts = [
                        f"## 👤 Customer Analysis: {customer['name']}\n",
                        f"**Customer ID:** {customer['customer_id']}",
                        f"**Member Since:** {customer['registration_date']}",
                        f"**Preferred Channel:** {customer['preferred_channel'].replace('_', ' ').title()}\n",
                        "### 📊 RFM Analysis:\n",
                        f"| Metric | Score | Details |",
                        f"|--------|-------|---------|",
                        f"| Recency | {'⭐' * rfm['recency_score']} ({rfm['recency_score']}/5) | {rfm['days_since_last_order']} days since last order |",
                        f"| Frequency | {'⭐' * rfm['frequency_score']} ({rfm['frequency_score']}/5) | Orders every {customer['order_frequency_days']} days |",
                        f"| Monetary | {'⭐' * rfm['monetary_score']} ({rfm['monetary_score']}/5) | ${customer['total_spend']:,} total spend |",
                        f"\n**RFM Composite Score:** {rfm['rfm_composite']}\n",
                        f"### {seg_emoji} Segment: **{result['segment']}**",
                        f"_{seg_info.get('description', '')}_\n",
                        f"### {risk_emoji} Churn Risk: **{churn['risk_level']}** ({churn['churn_probability']:.0%})\n"
                    ]
                    
                    if churn["risk_factors"]:
                        response_parts.append("**Risk Factors:**")
                        for factor in churn["risk_factors"]:
                            response_parts.append(f"- ⚠️ {factor}")
                    
                    response_parts.append(f"\n### 💰 Predicted Lifetime Value: **${result['predicted_ltv']:,}**\n")
                    
                    response_parts.append("### 🎯 Recommended Actions:")
                    for rec in result["recommendations"]:
                        response_parts.append(f"- {rec}")
                    
                    response_parts.append("\n### 📈 Behavior Summary:")
                    response_parts.append(f"- **Total Orders:** {customer['total_orders']}")
                    response_parts.append(f"- **Avg Order Value:** ${customer['avg_order_value']:.2f}")
                    response_parts.append(f"- **Email Open Rate:** {customer['email_open_rate']:.0%}")
                    response_parts.append(f"- **Categories:** {', '.join(customer['categories_purchased'])}")
                    
                    state["result"] = "\n".join(response_parts)
                else:
                    state["result"] = f"Customer not found in database."
            
            elif segment_filter:
                # Show customers in specific segment
                customers = MockDataStore.get_customer_behavior(segment=segment_filter)
                if customers:
                    results = [self.segment_customer(c) for c in customers]
                    seg_info = MockDataStore.CUSTOMER_SEGMENTS.get(segment_filter, {})
                    
                    response_parts = [
                        f"## 👥 {segment_filter} Segment Analysis\n",
                        f"_{seg_info.get('description', '')}_\n",
                        f"**Customers in Segment:** {len(customers)}",
                        f"**Recommended Actions:** {', '.join(seg_info.get('recommended_actions', []))}\n",
                        "### Customers:\n"
                    ]
                    
                    for r in results:
                        response_parts.append(f"- **{r['customer_name']}** - LTV: ${r['predicted_ltv']:,}")
                    
                    state["result"] = "\n".join(response_parts)
                else:
                    state["result"] = f"No customers found in {segment_filter} segment."
            
            else:
                # General inquiry - use LLM
                response = await self.llm_service.chat(
                    state["messages"],
                    self.get_system_prompt()
                )
                state["result"] = response
            
            state["messages"].append({"role": "assistant", "content": state["result"]})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("analyze", analyze_customers)
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", END)
        
        return workflow
    
    async def run_with_streaming(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ):
        """Run customer segmentation with streaming step updates."""
        workflow_steps = []
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        # Step 1: Load Customer Data
        step1 = {"step": "load", "status": "active", "label": "Load Data"}
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 2: Calculate RFM
        step2 = {"step": "rfm", "status": "active", "label": "Calculate RFM"}
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 3: ML Prediction
        step3 = {"step": "ml", "status": "active", "label": "ML Prediction"}
        workflow_steps.append(step3)
        yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 4: Generate Insights
        step4 = {"step": "insights", "status": "active", "label": "Generate Insights"}
        workflow_steps.append(step4)
        yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
        
        # Run the actual analysis
        result = await self.run(user_input, context, conversation_history)
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        yield {"type": "response", "content": result["response"]}

