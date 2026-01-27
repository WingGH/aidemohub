"""Pharma Account Sales Agent - Chatbot for pharmaceutical salesmen to check account info and sales targets."""
from typing import Dict, Any, List, Optional, AsyncGenerator
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState, get_llm_service
import json
import asyncio


# Mock hospital accounts data
HOSPITAL_ACCOUNTS = {
    "HOS-001": {
        "name": "Queen Mary Hospital",
        "type": "Public Hospital",
        "location": "Pok Fu Lam, Hong Kong",
        "contact": "Dr. Sarah Wong",
        "phone": "+852 2255 3838",
        "tier": "Platinum",
        "salesman": "John Chen",
        "annual_target": 2500000,
        "ytd_sales": 1875000,
        "target_achievement": 75.0,
        "last_visit": "2026-01-20",
        "next_scheduled_visit": "2026-02-05",
        "notes": "Interested in new cardiac medications"
    },
    "HOS-002": {
        "name": "Prince of Wales Hospital",
        "type": "Public Hospital",
        "location": "Sha Tin, New Territories",
        "contact": "Dr. Michael Lau",
        "phone": "+852 2632 2211",
        "tier": "Gold",
        "salesman": "John Chen",
        "annual_target": 1800000,
        "ytd_sales": 1620000,
        "target_achievement": 90.0,
        "last_visit": "2026-01-15",
        "next_scheduled_visit": "2026-01-28",
        "notes": "Strong demand for oncology products"
    },
    "HOS-003": {
        "name": "Hong Kong Sanatorium & Hospital",
        "type": "Private Hospital",
        "location": "Happy Valley, Hong Kong",
        "contact": "Dr. Emily Cheung",
        "phone": "+852 2572 0211",
        "tier": "Platinum",
        "salesman": "Alice Wong",
        "annual_target": 3200000,
        "ytd_sales": 2880000,
        "target_achievement": 90.0,
        "last_visit": "2026-01-22",
        "next_scheduled_visit": "2026-02-01",
        "notes": "Premium product focus, interested in new diabetes treatment"
    },
    "HOS-004": {
        "name": "Matilda International Hospital",
        "type": "Private Hospital",
        "location": "The Peak, Hong Kong",
        "contact": "Dr. James Ho",
        "phone": "+852 2849 0111",
        "tier": "Gold",
        "salesman": "Alice Wong",
        "annual_target": 1500000,
        "ytd_sales": 975000,
        "target_achievement": 65.0,
        "last_visit": "2026-01-10",
        "next_scheduled_visit": "2026-01-30",
        "notes": "Needs competitive pricing for renewal"
    },
    "HOS-005": {
        "name": "Tuen Mun Hospital",
        "type": "Public Hospital",
        "location": "Tuen Mun, New Territories",
        "contact": "Dr. Peter Ng",
        "phone": "+852 2468 5111",
        "tier": "Silver",
        "salesman": "John Chen",
        "annual_target": 1200000,
        "ytd_sales": 840000,
        "target_achievement": 70.0,
        "last_visit": "2026-01-18",
        "next_scheduled_visit": "2026-02-10",
        "notes": "Budget constraints, focus on essential medications"
    }
}

# Purchase history
PURCHASE_HISTORY = {
    "HOS-001": [
        {"date": "2026-01-15", "drug": "Cardiomax 100mg", "quantity": 500, "amount": 125000, "category": "Cardiovascular"},
        {"date": "2026-01-08", "drug": "Lipidol 20mg", "quantity": 800, "amount": 96000, "category": "Cardiovascular"},
        {"date": "2025-12-20", "drug": "Diabetix 500mg", "quantity": 600, "amount": 84000, "category": "Diabetes"},
        {"date": "2025-12-10", "drug": "Oncotab 50mg", "quantity": 200, "amount": 180000, "category": "Oncology"},
        {"date": "2025-11-25", "drug": "Painex 400mg", "quantity": 1000, "amount": 45000, "category": "Pain Management"},
    ],
    "HOS-002": [
        {"date": "2026-01-12", "drug": "Oncotab 50mg", "quantity": 300, "amount": 270000, "category": "Oncology"},
        {"date": "2026-01-05", "drug": "Immunoboost 250mg", "quantity": 400, "amount": 160000, "category": "Immunology"},
        {"date": "2025-12-18", "drug": "Cardiomax 100mg", "quantity": 400, "amount": 100000, "category": "Cardiovascular"},
        {"date": "2025-12-01", "drug": "Antibiox 500mg", "quantity": 1200, "amount": 72000, "category": "Antibiotics"},
    ],
    "HOS-003": [
        {"date": "2026-01-20", "drug": "Diabetix Premium 1000mg", "quantity": 400, "amount": 200000, "category": "Diabetes"},
        {"date": "2026-01-10", "drug": "Cardiomax Plus 200mg", "quantity": 300, "amount": 150000, "category": "Cardiovascular"},
        {"date": "2025-12-28", "drug": "Oncotab Premium 100mg", "quantity": 150, "amount": 300000, "category": "Oncology"},
        {"date": "2025-12-15", "drug": "Skincare Pro 50mg", "quantity": 500, "amount": 75000, "category": "Dermatology"},
    ],
    "HOS-004": [
        {"date": "2026-01-08", "drug": "Cardiomax 100mg", "quantity": 200, "amount": 50000, "category": "Cardiovascular"},
        {"date": "2025-12-22", "drug": "Painex 400mg", "quantity": 600, "amount": 27000, "category": "Pain Management"},
        {"date": "2025-12-05", "drug": "Antibiox 500mg", "quantity": 800, "amount": 48000, "category": "Antibiotics"},
    ],
    "HOS-005": [
        {"date": "2026-01-14", "drug": "Antibiox 500mg", "quantity": 1500, "amount": 90000, "category": "Antibiotics"},
        {"date": "2025-12-30", "drug": "Painex 400mg", "quantity": 1200, "amount": 54000, "category": "Pain Management"},
        {"date": "2025-12-12", "drug": "Diabetix 500mg", "quantity": 800, "amount": 112000, "category": "Diabetes"},
    ]
}

# FAQ database
FAQ_DATABASE = {
    "pricing": "Pricing is based on volume tiers: Standard (<500 units), Volume (500-2000 units) with 10% discount, Bulk (>2000 units) with 20% discount. Special pricing available for platinum accounts.",
    "delivery": "Standard delivery is 3-5 business days. Express delivery (next day) available for urgent orders at 15% surcharge. Cold chain medications have dedicated logistics.",
    "returns": "Returns accepted within 30 days for unopened products in original packaging. Expired products handled through our recall program. Credit issued within 5 business days.",
    "payment": "Standard payment terms are Net 30 for Gold/Platinum accounts, Net 15 for Silver accounts. Early payment discount of 2% available for payment within 10 days.",
    "ordering": "Orders can be placed through the online portal, mobile app, or directly through your sales representative. Minimum order value is HKD 10,000.",
    "samples": "Sample requests must be approved by the sales manager. Maximum 20 units per product per quarter. Educational samples available for new product launches.",
    "rebates": "Annual rebates calculated based on total purchase volume: 2% for meeting 80% of target, 5% for meeting 100%, 8% for exceeding 120%.",
    "compliance": "All products are GMP certified. Certificates of Analysis available on request. Cold chain products include temperature monitoring reports.",
    "training": "Product training sessions available for hospital staff. Schedule through your sales rep. CME-accredited programs for physicians."
}


class PharmaAccountAgent(BaseAgent):
    """Pharma Account Sales Agent for checking hospital accounts, sales targets, and FAQs."""
    
    def __init__(self):
        super().__init__(
            name="Pharma Account Sales",
            description="AI assistant for pharmaceutical salesmen to check hospital account info, sales performance, and FAQs"
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for pharma account interactions."""
        return """You are a helpful AI assistant for pharmaceutical sales representatives. Your role is to help salesmen quickly access information about their hospital accounts, track sales performance against targets, and answer FAQs about company policies.

## Your Capabilities
1. **Account Information**: Provide details about hospital accounts including contact info, tier status, and visit schedules
2. **Sales Performance**: Show current sales vs. annual targets, achievement percentages, and trends
3. **Purchase History**: Review past orders, top-selling products, and purchase patterns
4. **FAQ & Policies**: Answer questions about pricing, delivery, returns, payment terms, and compliance

## Response Guidelines
- Be concise and professional
- Use currency format HKD for Hong Kong Dollars
- Format numbers with thousand separators for readability
- Highlight key metrics (achievement %, remaining target)
- When showing lists, use bullet points or tables
- Proactively suggest relevant follow-up actions

## Account Data Available
You have access to hospital accounts including:
- Queen Mary Hospital (HOS-001) - Platinum tier
- Prince of Wales Hospital (HOS-002) - Gold tier
- Hong Kong Sanatorium & Hospital (HOS-003) - Platinum tier
- Matilda International Hospital (HOS-004) - Gold tier
- Tuen Mun Hospital (HOS-005) - Silver tier

## Example Interactions

**Account Status Query:**
User: "How is Queen Mary Hospital doing?"
Response: "📊 **Queen Mary Hospital (HOS-001)** - Platinum Tier

**Sales Performance:**
- Annual Target: HKD 2,500,000
- YTD Sales: HKD 1,875,000
- Achievement: 75% ✅
- Remaining: HKD 625,000

**Contact:** Dr. Sarah Wong | +852 2255 3838
**Last Visit:** Jan 20, 2026
**Next Visit:** Feb 5, 2026

💡 Note: Account is interested in new cardiac medications. Consider presenting our Cardiomax Plus line during next visit."

**Purchase History Query:**
User: "What did Prince of Wales buy recently?"
Response: "📦 **Recent Purchases - Prince of Wales Hospital**

| Date | Product | Qty | Amount |
|------|---------|-----|--------|
| Jan 12 | Oncotab 50mg | 300 | HKD 270,000 |
| Jan 5 | Immunoboost 250mg | 400 | HKD 160,000 |
| Dec 18 | Cardiomax 100mg | 400 | HKD 100,000 |

**Top Category:** Oncology (63% of purchases)
💡 Strong demand for oncology products - consider cross-selling related support medications."

Always be helpful and provide actionable insights for the sales representative."""

    def _build_graph(self) -> StateGraph:
        """Build the conversation workflow graph."""
        
        async def analyze_intent(state: AgentState) -> AgentState:
            """Analyze the salesman's intent from their message."""
            messages = state["messages"]
            last_message = messages[-1]["content"] if messages else ""
            
            intent = self._detect_intent(last_message)
            state["context"]["intent"] = intent
            state["current_step"] = "process"
            return state
        
        async def process_request(state: AgentState) -> AgentState:
            """Process the request and generate response."""
            messages = state["messages"]
            context = state["context"]
            intent = context.get("intent", "general")
            
            # Enrich context with relevant data
            enriched_context = self._enrich_context(messages[-1]["content"] if messages else "", intent)
            context.update(enriched_context)
            
            # Generate response
            system_prompt = self.get_system_prompt()
            if enriched_context:
                context_info = f"\n\n## Relevant Data Found:\n{json.dumps(enriched_context, indent=2, ensure_ascii=False)}"
                system_prompt += context_info
            
            response = await self.llm_service.chat(messages, system_prompt)
            
            state["result"] = response
            state["current_step"] = "complete"
            return state
        
        graph = StateGraph(AgentState)
        graph.add_node("analyze", analyze_intent)
        graph.add_node("process", process_request)
        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "process")
        graph.add_edge("process", END)
        
        return graph
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["target", "sales", "performance", "achievement", "ytd", "how is", "how's", "doing"]):
            return "sales_performance"
        elif any(word in message_lower for word in ["purchase", "order", "buy", "bought", "history", "recent"]):
            return "purchase_history"
        elif any(word in message_lower for word in ["account", "hospital", "info", "contact", "details", "visit"]):
            return "account_info"
        elif any(word in message_lower for word in ["pricing", "price", "discount", "delivery", "return", "payment", "rebate", "policy", "compliance", "sample", "training"]):
            return "faq"
        elif any(word in message_lower for word in ["all accounts", "my accounts", "list", "summary", "overview"]):
            return "accounts_overview"
        else:
            return "general"
    
    def _enrich_context(self, message: str, intent: str) -> Dict[str, Any]:
        """Enrich context with relevant data based on intent."""
        context = {}
        message_lower = message.lower()
        
        # Find mentioned account
        account_found = None
        for acc_id, acc_data in HOSPITAL_ACCOUNTS.items():
            if acc_id.lower() in message_lower or acc_data["name"].lower() in message_lower:
                account_found = acc_id
                context["account_info"] = {acc_id: acc_data}
                break
        
        # Also check for partial matches
        if not account_found:
            for acc_id, acc_data in HOSPITAL_ACCOUNTS.items():
                name_parts = acc_data["name"].lower().split()
                if any(part in message_lower for part in name_parts if len(part) > 3):
                    account_found = acc_id
                    context["account_info"] = {acc_id: acc_data}
                    break
        
        # Add purchase history if relevant
        if intent in ["purchase_history", "sales_performance"] and account_found:
            if account_found in PURCHASE_HISTORY:
                context["purchase_history"] = PURCHASE_HISTORY[account_found]
        
        # Add all accounts for overview
        if intent == "accounts_overview":
            context["all_accounts"] = HOSPITAL_ACCOUNTS
        
        # Add FAQ info
        if intent == "faq":
            for faq_key, faq_answer in FAQ_DATABASE.items():
                if faq_key in message_lower:
                    context["faq_info"] = {faq_key: faq_answer}
                    break
            # If no specific FAQ found, include all relevant ones
            if "faq_info" not in context:
                relevant_faqs = {k: v for k, v in FAQ_DATABASE.items() if k in message_lower or any(word in message_lower for word in k.split())}
                if relevant_faqs:
                    context["faq_info"] = relevant_faqs
        
        return context
    
    async def run_with_streaming(
        self, 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run the agent with streaming workflow updates."""
        
        # Step 1: Receiving message
        yield {
            "type": "workflow_step",
            "step": {"step": "receive", "label": "Receiving Query", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "active"},
                {"step": "analyze", "label": "Analyzing Request", "status": "pending"},
                {"step": "lookup", "label": "Looking Up Account Data", "status": "pending"},
                {"step": "respond", "label": "Generating Response", "status": "pending"},
            ]
        }
        await asyncio.sleep(0.3)
        
        # Step 2: Analyzing
        yield {
            "type": "workflow_step",
            "step": {"step": "analyze", "label": "Analyzing Request", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "completed"},
                {"step": "analyze", "label": "Analyzing Request", "status": "active"},
                {"step": "lookup", "label": "Looking Up Account Data", "status": "pending"},
                {"step": "respond", "label": "Generating Response", "status": "pending"},
            ]
        }
        
        intent = self._detect_intent(user_input)
        await asyncio.sleep(0.4)
        
        # Step 3: Looking up data
        yield {
            "type": "workflow_step",
            "step": {"step": "lookup", "label": "Looking Up Account Data", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "completed"},
                {"step": "analyze", "label": "Analyzing Request", "status": "completed"},
                {"step": "lookup", "label": "Looking Up Account Data", "status": "active"},
                {"step": "respond", "label": "Generating Response", "status": "pending"},
            ]
        }
        
        enriched_context = self._enrich_context(user_input, intent)
        await asyncio.sleep(0.5)
        
        # Step 4: Generating response
        yield {
            "type": "workflow_step",
            "step": {"step": "respond", "label": "Generating Response", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "completed"},
                {"step": "analyze", "label": "Analyzing Request", "status": "completed"},
                {"step": "lookup", "label": "Looking Up Account Data", "status": "completed"},
                {"step": "respond", "label": "Generating Response", "status": "active"},
            ]
        }
        
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        system_prompt = self.get_system_prompt()
        if enriched_context:
            context_info = f"\n\n## Relevant Data Found:\n{json.dumps(enriched_context, indent=2, ensure_ascii=False)}"
            system_prompt += context_info
        
        response = await self.llm_service.chat(messages, system_prompt)
        
        yield {
            "type": "workflow_step",
            "step": {"step": "respond", "label": "Generating Response", "status": "completed"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Query", "status": "completed"},
                {"step": "analyze", "label": "Analyzing Request", "status": "completed"},
                {"step": "lookup", "label": "Looking Up Account Data", "status": "completed"},
                {"step": "respond", "label": "Generating Response", "status": "completed"},
            ]
        }
        
        yield {
            "type": "response",
            "content": response
        }
    
    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account by ID."""
        return HOSPITAL_ACCOUNTS.get(account_id.upper())
    
    def get_purchase_history(self, account_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get purchase history for an account."""
        return PURCHASE_HISTORY.get(account_id.upper())
    
    def get_faq(self, topic: str) -> Optional[str]:
        """Get FAQ answer for a topic."""
        return FAQ_DATABASE.get(topic.lower())
