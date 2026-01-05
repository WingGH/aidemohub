"""Customer Service Chatbot Agent - AI-powered customer support assistant."""
from typing import Dict, Any, List, Optional, AsyncGenerator
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState, get_llm_service
import json
import asyncio


# Mock customer data for demo
MOCK_CUSTOMERS = {
    "C001": {"name": "Alice Wong", "email": "alice@example.com", "tier": "Gold", "since": "2022"},
    "C002": {"name": "Bob Chen", "email": "bob@example.com", "tier": "Silver", "since": "2023"},
    "C003": {"name": "Carol Lee", "email": "carol@example.com", "tier": "Platinum", "since": "2021"},
}

MOCK_ORDERS = {
    "ORD-10001": {"customer_id": "C001", "status": "Delivered", "items": ["Wireless Headphones", "Phone Case"], "total": "$89.99", "date": "2024-01-15"},
    "ORD-10002": {"customer_id": "C001", "status": "In Transit", "items": ["Smart Watch"], "total": "$299.99", "date": "2024-01-20", "eta": "Jan 25"},
    "ORD-10003": {"customer_id": "C002", "status": "Processing", "items": ["Laptop Stand", "USB-C Hub"], "total": "$124.99", "date": "2024-01-22"},
    "ORD-10004": {"customer_id": "C003", "status": "Pending", "items": ["Bluetooth Speaker"], "total": "$79.99", "date": "2024-01-23"},
}

MOCK_PRODUCTS = {
    "WH-1000": {"name": "Wireless Headphones Pro", "price": "$149.99", "stock": "In Stock", "warranty": "2 years"},
    "SW-2000": {"name": "Smart Watch Elite", "price": "$299.99", "stock": "Low Stock", "warranty": "1 year"},
    "BS-3000": {"name": "Bluetooth Speaker Max", "price": "$79.99", "stock": "In Stock", "warranty": "1 year"},
    "LP-4000": {"name": "Laptop Stand Ergonomic", "price": "$59.99", "stock": "In Stock", "warranty": "6 months"},
}

FAQ_DATABASE = {
    "shipping": "Standard shipping takes 3-5 business days. Express shipping (1-2 days) is available for $9.99. Free shipping on orders over $50.",
    "returns": "We offer a 30-day return policy for unused items in original packaging. Refunds are processed within 5-7 business days after we receive the item.",
    "warranty": "Most products come with a 1-2 year manufacturer warranty. Extended warranty options are available at checkout.",
    "payment": "We accept all major credit cards (Visa, Mastercard, AMEX), PayPal, Apple Pay, and Google Pay. Installment plans available for orders over $200.",
    "tracking": "You can track your order using the tracking number sent to your email, or by logging into your account and viewing order history.",
    "cancel": "Orders can be cancelled within 1 hour of placement if not yet processed. Contact support immediately for cancellation requests.",
    "exchange": "Exchanges can be requested within 30 days. We'll ship the new item once we receive your return, or you can do an instant exchange with a card on file.",
    "contact": "You can reach us via this chat 24/7, by email at support@example.com, or by phone at 1-800-EXAMPLE (Mon-Fri 9AM-6PM EST).",
}


class CSChatbotAgent(BaseAgent):
    """Customer Service Chatbot Agent for handling support inquiries."""
    
    def __init__(self):
        super().__init__(
            name="CS Chatbot",
            description="AI-powered customer service assistant for handling inquiries, orders, and support"
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for customer service interactions."""
        return """You are a friendly, professional, and helpful Customer Service AI Assistant. Your role is to assist customers with their inquiries in a warm and efficient manner.

## Your Personality
- **Friendly & Warm**: Use a conversational tone, greet customers warmly
- **Professional**: Maintain professionalism while being approachable
- **Empathetic**: Show understanding when customers have issues
- **Solution-Oriented**: Focus on resolving problems quickly
- **Patient**: Never show frustration, always remain calm and helpful

## Your Capabilities
1. **Order Support**: Track orders, check status, help with cancellations
2. **Product Information**: Answer questions about products, availability, pricing
3. **Returns & Refunds**: Guide customers through return process, explain policies
4. **Account Help**: Assist with account-related questions
5. **General FAQs**: Answer common questions about shipping, payment, warranties
6. **Complaint Handling**: Listen to complaints, empathize, and offer solutions

## Response Guidelines
- Keep responses concise but complete (2-4 sentences for simple queries)
- Use bullet points or numbered lists for multi-step instructions
- Always confirm understanding before providing solutions
- If you can't help with something, clearly explain why and offer alternatives
- End conversations by asking if there's anything else you can help with

## Sample Data Available
You have access to mock data for demonstration:
- **Customers**: C001 (Alice Wong - Gold), C002 (Bob Chen - Silver), C003 (Carol Lee - Platinum)
- **Orders**: ORD-10001 through ORD-10004 with various statuses
- **Products**: Wireless Headphones, Smart Watch, Bluetooth Speaker, Laptop Stand

## Example Interactions

**Order Status Query:**
Customer: "Where is my order ORD-10002?"
Response: "Hi! Let me check on order ORD-10002 for you. 📦 Your Smart Watch is currently **In Transit** and expected to arrive by **January 25th**. You can track it using your confirmation email. Is there anything else I can help you with?"

**Return Request:**
Customer: "I want to return my headphones"
Response: "I'd be happy to help you with that return! 🔄 Our policy allows returns within 30 days for unused items in original packaging. Could you please provide your order number so I can process this for you?"

**General Question:**
Customer: "What payment methods do you accept?"
Response: "Great question! 💳 We accept Visa, Mastercard, AMEX, PayPal, Apple Pay, and Google Pay. For orders over $200, we also offer installment payment plans. Would you like more details about any of these options?"

Remember: Always be helpful, never make up information you don't have, and maintain a positive, supportive tone throughout the conversation."""

    def _build_graph(self) -> StateGraph:
        """Build the conversation workflow graph."""
        
        async def analyze_intent(state: AgentState) -> AgentState:
            """Analyze the customer's intent from their message."""
            messages = state["messages"]
            last_message = messages[-1]["content"] if messages else ""
            
            # Detect intent based on keywords
            intent = self._detect_intent(last_message)
            
            state["context"]["intent"] = intent
            state["current_step"] = "process"
            return state
        
        async def process_request(state: AgentState) -> AgentState:
            """Process the customer request and generate response."""
            messages = state["messages"]
            context = state["context"]
            intent = context.get("intent", "general")
            
            # Enrich context with relevant data based on intent
            enriched_context = self._enrich_context(messages[-1]["content"] if messages else "", intent)
            context.update(enriched_context)
            
            # Generate response using LLM
            system_prompt = self.get_system_prompt()
            
            # Add context information to help the LLM
            if enriched_context:
                context_info = f"\n\n## Relevant Data Found:\n{json.dumps(enriched_context, indent=2)}"
                system_prompt += context_info
            
            response = await self.llm_service.chat(messages, system_prompt)
            
            state["result"] = response
            state["current_step"] = "complete"
            return state
        
        # Build the graph
        graph = StateGraph(AgentState)
        
        graph.add_node("analyze", analyze_intent)
        graph.add_node("process", process_request)
        
        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "process")
        graph.add_edge("process", END)
        
        return graph
    
    def _detect_intent(self, message: str) -> str:
        """Detect customer intent from message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["order", "track", "status", "where", "delivery", "shipping"]):
            return "order_status"
        elif any(word in message_lower for word in ["return", "refund", "money back", "exchange"]):
            return "returns"
        elif any(word in message_lower for word in ["cancel", "cancellation"]):
            return "cancellation"
        elif any(word in message_lower for word in ["product", "price", "stock", "available", "warranty"]):
            return "product_info"
        elif any(word in message_lower for word in ["payment", "pay", "credit card", "paypal"]):
            return "payment"
        elif any(word in message_lower for word in ["complaint", "unhappy", "disappointed", "angry", "terrible", "worst"]):
            return "complaint"
        elif any(word in message_lower for word in ["account", "login", "password", "profile"]):
            return "account"
        elif any(word in message_lower for word in ["help", "support", "contact", "speak", "human", "agent"]):
            return "escalation"
        else:
            return "general"
    
    def _enrich_context(self, message: str, intent: str) -> Dict[str, Any]:
        """Enrich context with relevant data based on intent."""
        context = {}
        message_lower = message.lower()
        
        # Look for order IDs
        for order_id, order_data in MOCK_ORDERS.items():
            if order_id.lower() in message_lower or order_id.replace("-", "").lower() in message_lower:
                context["order_found"] = {order_id: order_data}
                # Also get customer info
                customer_id = order_data.get("customer_id")
                if customer_id in MOCK_CUSTOMERS:
                    context["customer_info"] = MOCK_CUSTOMERS[customer_id]
                break
        
        # Look for customer IDs or names
        for cust_id, cust_data in MOCK_CUSTOMERS.items():
            if cust_id.lower() in message_lower or cust_data["name"].lower() in message_lower:
                context["customer_info"] = {cust_id: cust_data}
                # Get their orders
                customer_orders = {k: v for k, v in MOCK_ORDERS.items() if v["customer_id"] == cust_id}
                if customer_orders:
                    context["customer_orders"] = customer_orders
                break
        
        # Look for product keywords
        for prod_id, prod_data in MOCK_PRODUCTS.items():
            if any(word in message_lower for word in prod_data["name"].lower().split()):
                context["product_info"] = {prod_id: prod_data}
                break
        
        # Add relevant FAQ info
        if intent in ["returns", "payment", "general"]:
            for faq_key, faq_answer in FAQ_DATABASE.items():
                if faq_key in message_lower or intent == faq_key:
                    context["faq_info"] = {faq_key: faq_answer}
                    break
        
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
            "step": {"step": "receive", "label": "Receiving Message", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Message", "status": "active"},
                {"step": "analyze", "label": "Analyzing Intent", "status": "pending"},
                {"step": "lookup", "label": "Looking Up Data", "status": "pending"},
                {"step": "respond", "label": "Generating Response", "status": "pending"},
            ]
        }
        await asyncio.sleep(0.3)
        
        # Step 2: Analyzing intent
        yield {
            "type": "workflow_step",
            "step": {"step": "analyze", "label": "Analyzing Intent", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Message", "status": "completed"},
                {"step": "analyze", "label": "Analyzing Intent", "status": "active"},
                {"step": "lookup", "label": "Looking Up Data", "status": "pending"},
                {"step": "respond", "label": "Generating Response", "status": "pending"},
            ]
        }
        
        intent = self._detect_intent(user_input)
        await asyncio.sleep(0.4)
        
        # Step 3: Looking up data
        yield {
            "type": "workflow_step",
            "step": {"step": "lookup", "label": "Looking Up Data", "status": "active"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Message", "status": "completed"},
                {"step": "analyze", "label": "Analyzing Intent", "status": "completed"},
                {"step": "lookup", "label": "Looking Up Data", "status": "active"},
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
                {"step": "receive", "label": "Receiving Message", "status": "completed"},
                {"step": "analyze", "label": "Analyzing Intent", "status": "completed"},
                {"step": "lookup", "label": "Looking Up Data", "status": "completed"},
                {"step": "respond", "label": "Generating Response", "status": "active"},
            ]
        }
        
        # Build messages with history
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        # Generate response
        system_prompt = self.get_system_prompt()
        if enriched_context:
            context_info = f"\n\n## Relevant Data Found:\n{json.dumps(enriched_context, indent=2)}"
            system_prompt += context_info
        
        response = await self.llm_service.chat(messages, system_prompt)
        
        # Final step complete
        yield {
            "type": "workflow_step",
            "step": {"step": "respond", "label": "Generating Response", "status": "completed"},
            "all_steps": [
                {"step": "receive", "label": "Receiving Message", "status": "completed"},
                {"step": "analyze", "label": "Analyzing Intent", "status": "completed"},
                {"step": "lookup", "label": "Looking Up Data", "status": "completed"},
                {"step": "respond", "label": "Generating Response", "status": "completed"},
            ]
        }
        
        # Send the response
        yield {
            "type": "response",
            "content": response
        }
    
    def get_faq(self, topic: str) -> Optional[str]:
        """Get FAQ answer for a specific topic."""
        return FAQ_DATABASE.get(topic.lower())
    
    def lookup_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Look up order by ID."""
        return MOCK_ORDERS.get(order_id.upper())
    
    def lookup_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Look up customer by ID."""
        return MOCK_CUSTOMERS.get(customer_id.upper())
    
    def get_product_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product information by ID."""
        return MOCK_PRODUCTS.get(product_id.upper())


