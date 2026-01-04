"""Automotive Sales Agent - Multi-Agent Architecture with Supervisor Pattern.

This demonstrates a true multi-agent system where:
- Supervisor Agent: Routes tasks to specialist agents
- Intent Analyzer Agent: Understands customer intent
- Inventory Specialist Agent: Searches and retrieves vehicle details  
- Finance Specialist Agent: Calculates financing options
- Service Advisor Agent: Handles service appointments

Each specialist is an independent agent with its own LLM calls and responsibilities.
"""
from typing import Dict, Any, List, TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent
from app.data.mock_data import MockDataStore
from app.tools.automotive_tools import AutomotiveTools
from app.services.llm_service import LLMService
import asyncio
import re

# Delay between workflow steps to simulate real processing
STEP_DELAY = 0.8  # seconds


class MultiAgentState(TypedDict):
    """Shared state for multi-agent automotive workflow."""
    messages: List[Dict[str, str]]
    conversation_history: List[Dict[str, str]]
    context: Dict[str, Any]
    user_input: str
    
    # Agent tracking
    current_agent: str
    agent_outputs: Dict[str, Any]
    agent_sequence: List[str]
    
    # Workflow state
    intent: Optional[str]
    vehicles_found: List[Dict[str, Any]]
    selected_vehicle: Optional[Dict[str, Any]]
    financing_info: Optional[Dict[str, Any]]
    appointment: Optional[Dict[str, Any]]
    workflow_steps: List[Dict[str, Any]]
    result: Optional[str]


# ============================================================================
# SPECIALIST AGENTS - Each has its own LLM and responsibilities
# ============================================================================

class IntentAnalyzerAgent:
    """Specialist agent for understanding customer intent."""
    
    def __init__(self):
        self.name = "Intent Analyzer"
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are an intent analysis specialist for an automotive dealership.
Your job is to classify customer messages into one of these intents:
- SEARCH: Customer wants to find/browse vehicles (price queries, brand mentions, "show me", "looking for")
- TEST_DRIVE: Customer wants to schedule a test drive
- FINANCING: Customer wants financing/payment information
- SERVICE: Customer needs service/repair/maintenance
- INQUIRY: General questions that don't fit above categories

Respond with ONLY the intent category (one word)."""

    async def analyze(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Analyze user intent using LLM."""
        
        # Build context from history
        history_context = ""
        if conversation_history:
            history_context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history[-3:]  # Last 3 messages for context
            ])
        
        prompt = f"""Conversation history:
{history_context}

Current user message: {user_message}

Classify the intent. Consider:
- Numbers like "$35000" or "below 35000" indicate SEARCH intent
- Keywords like "under", "budget", "looking for" indicate SEARCH
- "test drive", "schedule", "try" indicate TEST_DRIVE
- "finance", "monthly", "loan", "payment" indicate FINANCING
- "service", "repair", "oil change", "brake" indicate SERVICE

Respond with ONLY: SEARCH, TEST_DRIVE, FINANCING, SERVICE, or INQUIRY"""

        response = await self.llm_service.generate(prompt, self.get_system_prompt())
        
        # Parse response
        intent = response.strip().upper()
        if intent not in ["SEARCH", "TEST_DRIVE", "FINANCING", "SERVICE", "INQUIRY"]:
            # Fallback to keyword matching
            user_lower = user_message.lower()
            has_price = bool(re.search(r'\$?\d{2,6}', user_lower))
            
            if has_price or any(w in user_lower for w in ["show", "find", "looking", "under", "below", "cheaper"]):
                intent = "SEARCH"
            elif any(w in user_lower for w in ["test drive", "schedule", "try"]):
                intent = "TEST_DRIVE"
            elif any(w in user_lower for w in ["finance", "payment", "loan", "monthly"]):
                intent = "FINANCING"
            elif any(w in user_lower for w in ["service", "repair", "oil", "brake"]):
                intent = "SERVICE"
            else:
                intent = "INQUIRY"
        
        return {
            "agent": self.name,
            "intent": intent.lower(),
            "confidence": "high",
            "analysis": f"Classified as {intent} intent"
        }


class InventorySpecialistAgent:
    """Specialist agent for vehicle inventory operations."""
    
    def __init__(self):
        self.name = "Inventory Specialist"
        self.tools = AutomotiveTools()
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are a vehicle inventory specialist at an automotive dealership.
You help customers find the perfect vehicle by:
1. Understanding their preferences (budget, brand, features)
2. Searching inventory for matching vehicles
3. Providing detailed information about vehicles
4. Making personalized recommendations

Be helpful, knowledgeable about cars, and focus on matching customer needs."""

    async def search_and_recommend(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search inventory and provide recommendations."""
        
        user_lower = user_message.lower()
        
        # Parse price limit
        max_price = None
        if any(word in user_lower for word in ["under", "below", "less", "cheaper", "budget"]):
            prices = re.findall(r'\$?([\d,]+)', user_lower)
            if prices:
                max_price = float(prices[0].replace(',', ''))
        elif re.search(r'\$?\d{2,6}', user_lower):
            # Just a number mentioned - treat as max price
            prices = re.findall(r'\$?([\d,]+)', user_lower)
            if prices:
                max_price = float(prices[0].replace(',', ''))
        
        # Parse brand
        brand = None
        for b in ["toyota", "honda", "bmw", "mercedes", "lexus"]:
            if b in user_lower:
                brand = b.title()
                break
        
        # Search using tools
        result = self.tools.search_vehicles(max_price=max_price, brand=brand)
        vehicles = result["vehicles"]
        
        # Get details for best match
        selected_vehicle = None
        if vehicles:
            details = self.tools.get_vehicle_details(vehicles[0]["id"])
            selected_vehicle = details.get("vehicle", vehicles[0])
        
        # Generate LLM recommendation
        if vehicles:
            vehicle_list = "\n".join([
                f"- {v['year']} {v['brand']} {v['model']} ({v['color']}) - ${v['price']:,}"
                for v in vehicles
            ])
            
            prompt = f"""Customer query: {user_message}

Available vehicles matching their criteria:
{vehicle_list}

Provide a brief, personalized recommendation (2-3 sentences) highlighting why these vehicles match their needs."""

            recommendation = await self.llm_service.generate(prompt, self.get_system_prompt())
        else:
            recommendation = "I couldn't find vehicles matching your exact criteria, but let me show you some alternatives."
        
        return {
            "agent": self.name,
            "vehicles_found": vehicles,
            "count": len(vehicles),
            "selected_vehicle": selected_vehicle,
            "recommendation": recommendation,
            "search_params": {"max_price": max_price, "brand": brand}
        }


class FinanceSpecialistAgent:
    """Specialist agent for financing calculations and options."""
    
    def __init__(self):
        self.name = "Finance Specialist"
        self.tools = AutomotiveTools()
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are a finance specialist at an automotive dealership.
You help customers understand:
1. Monthly payment options for different terms
2. Interest rates and total loan costs
3. Down payment strategies
4. Trade-in considerations

Be clear about numbers and help customers make informed financial decisions."""

    async def calculate_options(self, user_message: str, vehicle_price: float = 40000) -> Dict[str, Any]:
        """Calculate financing options."""
        
        user_lower = user_message.lower()
        
        # Determine term
        term = 60  # Default
        if "3 year" in user_lower or "36" in user_lower:
            term = 36
        elif "4 year" in user_lower or "48" in user_lower:
            term = 48
        elif "6 year" in user_lower or "72" in user_lower:
            term = 72
        
        # Calculate using tool
        financing = self.tools.calculate_financing(
            vehicle_price=vehicle_price,
            down_payment=5000,
            term_months=term
        )
        
        # Generate LLM advice
        prompt = f"""Customer asked about financing: {user_message}

Calculated financing details:
- Vehicle Price: ${financing['vehicle_price']:,}
- Down Payment: ${financing['down_payment']:,}
- Loan Amount: ${financing['loan_amount']:,}
- Term: {financing['term_months']} months
- Interest Rate: {financing['interest_rate']}%
- Monthly Payment: ${financing['monthly_payment']:.2f}

Provide a brief, helpful explanation of these terms and any suggestions (2-3 sentences)."""

        advice = await self.llm_service.generate(prompt, self.get_system_prompt())
        
        return {
            "agent": self.name,
            "financing_info": financing,
            "advice": advice
        }


class ServiceAdvisorAgent:
    """Specialist agent for service appointments and maintenance."""
    
    def __init__(self):
        self.name = "Service Advisor"
        self.tools = AutomotiveTools()
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are a service advisor at an automotive dealership.
You help customers with:
1. Scheduling service appointments
2. Diagnosing potential issues from symptoms
3. Explaining maintenance needs
4. Providing cost estimates

Be helpful and explain technical concepts in simple terms."""

    async def handle_service_request(self, user_message: str) -> Dict[str, Any]:
        """Handle service-related requests."""
        
        user_lower = user_message.lower()
        
        # Determine service type
        service_type = "General inspection"
        if "brake" in user_lower:
            service_type = "Brake service"
        elif "oil" in user_lower:
            service_type = "Oil change"
        elif "tire" in user_lower:
            service_type = "Tire service"
        elif "battery" in user_lower:
            service_type = "Battery check"
        
        # Book appointment
        appointment = self.tools.book_service_appointment(
            vehicle_info="Customer's vehicle",
            service_type=service_type
        )
        
        # Generate LLM advice
        prompt = f"""Customer service request: {user_message}

Appointment booked:
- Service Type: {service_type}
- Date: {appointment['scheduled_date']}
- Estimated Cost: {appointment['estimated_cost']}

Provide brief, helpful advice about this service (2-3 sentences)."""

        advice = await self.llm_service.generate(prompt, self.get_system_prompt())
        
        return {
            "agent": self.name,
            "appointment": appointment,
            "service_type": service_type,
            "advice": advice
        }


class TestDriveCoordinatorAgent:
    """Specialist agent for scheduling test drives."""
    
    def __init__(self):
        self.name = "Test Drive Coordinator"
        self.tools = AutomotiveTools()
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are a test drive coordinator at an automotive dealership.
You help customers:
1. Schedule test drive appointments
2. Select vehicles to test
3. Prepare for their visit
4. Answer questions about the test drive process"""

    async def schedule_test_drive(self, user_message: str, vehicles: List[Dict] = None) -> Dict[str, Any]:
        """Schedule a test drive."""
        
        user_lower = user_message.lower()
        
        # Find mentioned vehicle
        vehicle_id = None
        vehicle_name = None
        
        for v in MockDataStore.VEHICLES:
            if v["brand"].lower() in user_lower or v["model"].lower() in user_lower:
                vehicle_id = v["id"]
                vehicle_name = f"{v['year']} {v['brand']} {v['model']}"
                break
        
        if not vehicle_id:
            # Use first available or from previous search
            if vehicles:
                vehicle_id = vehicles[0]["id"]
                v = vehicles[0]
                vehicle_name = f"{v['year']} {v['brand']} {v['model']}"
            else:
                v = MockDataStore.VEHICLES[0]
                vehicle_id = v["id"]
                vehicle_name = f"{v['year']} {v['brand']} {v['model']}"
        
        # Schedule
        appointment = self.tools.schedule_test_drive(vehicle_id, "Valued Customer")
        
        return {
            "agent": self.name,
            "appointment": appointment,
            "vehicle_name": vehicle_name
        }


# ============================================================================
# SUPERVISOR AGENT - Orchestrates the specialist agents
# ============================================================================

class AutomotiveSalesAgent(BaseAgent):
    """
    Multi-Agent Supervisor for Automotive Sales.
    
    Coordinates between specialist agents:
    - Intent Analyzer: Understands what the customer needs
    - Inventory Specialist: Finds and recommends vehicles
    - Finance Specialist: Handles financing questions
    - Service Advisor: Manages service requests
    - Test Drive Coordinator: Schedules test drives
    """
    
    def __init__(self):
        # Initialize specialist agents
        self.intent_agent = IntentAnalyzerAgent()
        self.inventory_agent = InventorySpecialistAgent()
        self.finance_agent = FinanceSpecialistAgent()
        self.service_agent = ServiceAdvisorAgent()
        self.test_drive_agent = TestDriveCoordinatorAgent()
        self.tools = AutomotiveTools()
        
        super().__init__(
            name="Automotive Sales Supervisor",
            description="Multi-agent system for end-to-end automotive sales with specialized agents"
        )
    
    def get_system_prompt(self) -> str:
        return """You are the supervisor of a multi-agent automotive sales system.

You coordinate between specialist agents:
🧠 Intent Analyzer - Understands customer needs
🚗 Inventory Specialist - Searches vehicles
💰 Finance Specialist - Calculates financing
🔧 Service Advisor - Handles service requests
🎯 Test Drive Coordinator - Schedules test drives

Your role is to:
1. Route customer queries to the appropriate specialist
2. Combine outputs from multiple agents when needed
3. Ensure a smooth, cohesive customer experience"""

    def _get_inventory_context(self) -> str:
        vehicles = MockDataStore.get_available_vehicles()
        lines = []
        for v in vehicles:
            lines.append(f"- {v['year']} {v['brand']} {v['model']} ({v['color']}) - ${v['price']:,}")
        return "\n".join(lines)
    
    def _build_graph(self) -> StateGraph:
        """Build the multi-agent workflow graph."""
        
        async def supervisor_route(state: MultiAgentState) -> MultiAgentState:
            """Supervisor decides which agent to invoke."""
            state["workflow_steps"].append({
                "step": "supervisor",
                "status": "active",
                "label": "🎯 Supervisor Routing",
                "agent": "Supervisor"
            })
            
            # Get intent from Intent Analyzer Agent
            intent_result = await self.intent_agent.analyze(
                state["user_input"],
                state.get("conversation_history", [])
            )
            
            state["intent"] = intent_result["intent"]
            state["agent_outputs"]["intent_analyzer"] = intent_result
            state["agent_sequence"].append("Intent Analyzer")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "intent": state["intent"],
                "next_agent": self._get_next_agent_name(state["intent"])
            }
            
            return state
        
        async def inventory_agent_node(state: MultiAgentState) -> MultiAgentState:
            """Invoke Inventory Specialist Agent."""
            state["workflow_steps"].append({
                "step": "inventory_agent",
                "status": "active",
                "label": "🚗 Inventory Specialist",
                "agent": "Inventory Specialist"
            })
            state["current_agent"] = "Inventory Specialist"
            
            result = await self.inventory_agent.search_and_recommend(
                state["user_input"],
                state["context"]
            )
            
            state["vehicles_found"] = result["vehicles_found"]
            state["selected_vehicle"] = result.get("selected_vehicle")
            state["agent_outputs"]["inventory_specialist"] = result
            state["agent_sequence"].append("Inventory Specialist")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {"vehicles_found": len(result["vehicles_found"])}
            
            return state
        
        async def finance_agent_node(state: MultiAgentState) -> MultiAgentState:
            """Invoke Finance Specialist Agent."""
            state["workflow_steps"].append({
                "step": "finance_agent",
                "status": "active",
                "label": "💰 Finance Specialist",
                "agent": "Finance Specialist"
            })
            state["current_agent"] = "Finance Specialist"
            
            # Get vehicle price from context or previous search
            vehicle_price = 40000
            if state["selected_vehicle"]:
                vehicle_price = state["selected_vehicle"].get("price", 40000)
            elif state["vehicles_found"]:
                vehicle_price = state["vehicles_found"][0].get("price", 40000)
            
            result = await self.finance_agent.calculate_options(
                state["user_input"],
                vehicle_price
            )
            
            state["financing_info"] = result["financing_info"]
            state["agent_outputs"]["finance_specialist"] = result
            state["agent_sequence"].append("Finance Specialist")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "monthly_payment": result["financing_info"]["monthly_payment"]
            }
            
            return state
        
        async def service_agent_node(state: MultiAgentState) -> MultiAgentState:
            """Invoke Service Advisor Agent."""
            state["workflow_steps"].append({
                "step": "service_agent",
                "status": "active",
                "label": "🔧 Service Advisor",
                "agent": "Service Advisor"
            })
            state["current_agent"] = "Service Advisor"
            
            result = await self.service_agent.handle_service_request(state["user_input"])
            
            state["appointment"] = result["appointment"]
            state["agent_outputs"]["service_advisor"] = result
            state["agent_sequence"].append("Service Advisor")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "service_type": result["service_type"]
            }
            
            return state
        
        async def test_drive_agent_node(state: MultiAgentState) -> MultiAgentState:
            """Invoke Test Drive Coordinator Agent."""
            state["workflow_steps"].append({
                "step": "test_drive_agent",
                "status": "active",
                "label": "🎯 Test Drive Coordinator",
                "agent": "Test Drive Coordinator"
            })
            state["current_agent"] = "Test Drive Coordinator"
            
            result = await self.test_drive_agent.schedule_test_drive(
                state["user_input"],
                state["vehicles_found"]
            )
            
            state["appointment"] = result["appointment"]
            state["agent_outputs"]["test_drive_coordinator"] = result
            state["agent_sequence"].append("Test Drive Coordinator")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "vehicle": result.get("vehicle_name")
            }
            
            return state
        
        async def general_inquiry_node(state: MultiAgentState) -> MultiAgentState:
            """Handle general inquiries using supervisor LLM."""
            state["workflow_steps"].append({
                "step": "inquiry",
                "status": "active",
                "label": "💬 General Inquiry",
                "agent": "Supervisor"
            })
            
            response = await self.llm_service.chat(
                state["messages"],
                self.get_system_prompt() + "\n\nAvailable Vehicles:\n" + self._get_inventory_context()
            )
            
            state["result"] = response
            state["agent_sequence"].append("Supervisor (Inquiry)")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            
            return state
        
        async def generate_response(state: MultiAgentState) -> MultiAgentState:
            """Generate final response combining agent outputs."""
            
            response_parts = ["## 🚗 Automotive Sales Assistant\n"]
            response_parts.append("### Multi-Agent Workflow:")
            response_parts.append(f"*Agents involved: {' → '.join(state['agent_sequence'])}*\n")
            
            for step in state["workflow_steps"]:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                agent_tag = f" [{step.get('agent', 'System')}]" if step.get('agent') else ""
                response_parts.append(f"{emoji} {step['label']}{agent_tag}")
            
            response_parts.append("")
            
            # Add results based on what agents were invoked
            if state["intent"] == "search" and state["vehicles_found"]:
                inv_output = state["agent_outputs"].get("inventory_specialist", {})
                
                response_parts.append(f"### 🚗 Found {len(state['vehicles_found'])} Vehicles:\n")
                for v in state["vehicles_found"]:
                    response_parts.append(f"**{v['year']} {v['brand']} {v['model']}**")
                    response_parts.append(f"- Color: {v['color']}")
                    response_parts.append(f"- Price: ${v['price']:,}")
                    response_parts.append(f"- Status: {v['status'].title()}\n")
                
                if inv_output.get("recommendation"):
                    response_parts.append(f"### 💡 Recommendation:\n{inv_output['recommendation']}")
            
            elif state["intent"] == "financing" and state["financing_info"]:
                fin = state["financing_info"]
                fin_output = state["agent_outputs"].get("finance_specialist", {})
                
                response_parts.append("### 💰 Financing Options:\n")
                response_parts.append(f"- **Vehicle Price:** ${fin['vehicle_price']:,}")
                response_parts.append(f"- **Down Payment:** ${fin['down_payment']:,}")
                response_parts.append(f"- **Loan Amount:** ${fin['loan_amount']:,}")
                response_parts.append(f"- **Term:** {fin['term_months']} months")
                response_parts.append(f"- **Interest Rate:** {fin['interest_rate']}%")
                response_parts.append(f"- **Monthly Payment:** **${fin['monthly_payment']:,.2f}**\n")
                
                if fin_output.get("advice"):
                    response_parts.append(f"### 💡 Finance Advice:\n{fin_output['advice']}")
            
            elif state["intent"] == "test_drive" and state["appointment"]:
                apt = state["appointment"]
                td_output = state["agent_outputs"].get("test_drive_coordinator", {})
                
                response_parts.append("### ✅ Test Drive Scheduled!\n")
                response_parts.append(f"- **Confirmation:** {apt.get('confirmation_id')}")
                response_parts.append(f"- **Vehicle:** {td_output.get('vehicle_name', apt.get('vehicle'))}")
                response_parts.append(f"- **Date:** {apt.get('scheduled_date')}")
                response_parts.append(f"- **Time:** {apt.get('scheduled_time')}")
                response_parts.append(f"- **Location:** {apt.get('location')}")
            
            elif state["intent"] == "service" and state["appointment"]:
                apt = state["appointment"]
                svc_output = state["agent_outputs"].get("service_advisor", {})
                
                response_parts.append("### 🔧 Service Appointment Booked!\n")
                response_parts.append(f"- **Confirmation:** {apt.get('confirmation_id')}")
                response_parts.append(f"- **Service:** {apt.get('service_type')}")
                response_parts.append(f"- **Date:** {apt.get('scheduled_date')}")
                response_parts.append(f"- **Estimated Cost:** {apt.get('estimated_cost')}\n")
                
                if svc_output.get("advice"):
                    response_parts.append(f"### 💡 Service Advice:\n{svc_output['advice']}")
            
            elif state["result"]:
                response_parts.append(state["result"])
            
            state["result"] = "\n".join(response_parts)
            state["messages"].append({"role": "assistant", "content": state["result"]})
            
            return state
        
        def route_to_specialist(state: MultiAgentState) -> str:
            """Route to appropriate specialist agent based on intent."""
            intent = state.get("intent", "inquiry")
            if intent == "search":
                return "inventory"
            elif intent == "test_drive":
                return "test_drive"
            elif intent == "financing":
                return "finance"
            elif intent == "service":
                return "service"
            return "inquiry"
        
        # Build graph
        workflow = StateGraph(MultiAgentState)
        
        # Add nodes
        workflow.add_node("supervisor", supervisor_route)
        workflow.add_node("inventory", inventory_agent_node)
        workflow.add_node("finance", finance_agent_node)
        workflow.add_node("service", service_agent_node)
        workflow.add_node("test_drive", test_drive_agent_node)
        workflow.add_node("inquiry", general_inquiry_node)
        workflow.add_node("respond", generate_response)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "supervisor",
            route_to_specialist,
            {
                "inventory": "inventory",
                "finance": "finance",
                "service": "service",
                "test_drive": "test_drive",
                "inquiry": "inquiry"
            }
        )
        
        # All specialists route to response
        workflow.add_edge("inventory", "respond")
        workflow.add_edge("finance", "respond")
        workflow.add_edge("service", "respond")
        workflow.add_edge("test_drive", "respond")
        workflow.add_edge("inquiry", "respond")
        workflow.add_edge("respond", END)
        
        return workflow
    
    def _get_next_agent_name(self, intent: str) -> str:
        """Get the name of the next agent based on intent."""
        mapping = {
            "search": "Inventory Specialist",
            "test_drive": "Test Drive Coordinator",
            "financing": "Finance Specialist",
            "service": "Service Advisor",
            "inquiry": "Supervisor"
        }
        return mapping.get(intent, "Supervisor")
    
    async def run(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Run the multi-agent automotive sales workflow."""
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        initial_state: MultiAgentState = {
            "messages": messages,
            "conversation_history": conversation_history or [],
            "context": context or {},
            "user_input": user_input,
            "current_agent": "Supervisor",
            "agent_outputs": {},
            "agent_sequence": [],
            "intent": None,
            "vehicles_found": [],
            "selected_vehicle": None,
            "financing_info": None,
            "appointment": None,
            "workflow_steps": [],
            "result": None
        }
        
        app = self.graph.compile()
        final_state = await app.ainvoke(initial_state)
        
        return {
            "response": final_state.get("result", ""),
            "messages": final_state.get("messages", []),
            "context": final_state.get("context", {}),
            "workflow_steps": final_state.get("workflow_steps", []),
            "agent_sequence": final_state.get("agent_sequence", [])
        }
    
    async def run_with_streaming(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ):
        """Run the multi-agent workflow with streaming step updates."""
        
        user_message = user_input.lower()
        workflow_steps = []
        agent_sequence = []
        agent_outputs = {}
        
        # Build full messages list for LLM calls
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        # ========================================
        # Step 1: Supervisor Agent - Route Request
        # ========================================
        step1 = {
            "step": "supervisor",
            "status": "active",
            "label": "🎯 Supervisor Routing",
            "agent": "Supervisor"
        }
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        # ========================================
        # Step 2: Intent Analyzer Agent
        # ========================================
        step2 = {
            "step": "intent_analyzer",
            "status": "active",
            "label": "🧠 Intent Analyzer",
            "agent": "Intent Analyzer"
        }
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        # Call Intent Analyzer Agent
        intent_result = await self.intent_agent.analyze(user_input, conversation_history)
        intent = intent_result["intent"]
        agent_sequence.append("Intent Analyzer")
        agent_outputs["intent_analyzer"] = intent_result
        
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"intent": intent}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Complete supervisor routing
        workflow_steps[0]["status"] = "complete"
        workflow_steps[0]["result"] = {"routed_to": self._get_next_agent_name(intent)}
        yield {"type": "workflow_step", "step": workflow_steps[0], "all_steps": workflow_steps.copy()}
        
        # ========================================
        # Route to Specialist Agent
        # ========================================
        
        if intent == "search":
            # Inventory Specialist Agent
            step3 = {
                "step": "inventory_agent",
                "status": "active",
                "label": "🚗 Inventory Specialist",
                "agent": "Inventory Specialist"
            }
            workflow_steps.append(step3)
            yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
            
            inv_result = await self.inventory_agent.search_and_recommend(user_input, context)
            agent_sequence.append("Inventory Specialist")
            agent_outputs["inventory_specialist"] = inv_result
            
            await asyncio.sleep(STEP_DELAY)
            
            workflow_steps[-1]["status"] = "complete"
            workflow_steps[-1]["result"] = {"vehicles_found": len(inv_result["vehicles_found"])}
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Generate response
            response_parts = ["## 🚗 Automotive Sales Assistant\n"]
            response_parts.append("### Multi-Agent Workflow:")
            response_parts.append(f"*Agents: {' → '.join(agent_sequence)}*\n")
            
            for step in workflow_steps:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']} [{step.get('agent', 'System')}]")
            
            response_parts.append(f"\n### 🚗 Found {len(inv_result['vehicles_found'])} Vehicles:\n")
            for v in inv_result["vehicles_found"]:
                response_parts.append(f"**{v['year']} {v['brand']} {v['model']}**")
                response_parts.append(f"- Color: {v['color']}")
                response_parts.append(f"- Price: ${v['price']:,}")
                response_parts.append(f"- Status: {v['status'].title()}\n")
            
            if inv_result.get("recommendation"):
                response_parts.append(f"### 💡 Recommendation:\n{inv_result['recommendation']}")
            
            yield {"type": "response", "content": "\n".join(response_parts)}
            
        elif intent == "test_drive":
            # Test Drive Coordinator Agent
            step3 = {
                "step": "test_drive_agent",
                "status": "active",
                "label": "🎯 Test Drive Coordinator",
                "agent": "Test Drive Coordinator"
            }
            workflow_steps.append(step3)
            yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
            
            td_result = await self.test_drive_agent.schedule_test_drive(user_input)
            agent_sequence.append("Test Drive Coordinator")
            
            await asyncio.sleep(STEP_DELAY)
            
            workflow_steps[-1]["status"] = "complete"
            workflow_steps[-1]["result"] = {"vehicle": td_result.get("vehicle_name")}
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            apt = td_result["appointment"]
            response_parts = ["## 🚗 Automotive Sales Assistant\n"]
            response_parts.append("### Multi-Agent Workflow:")
            response_parts.append(f"*Agents: {' → '.join(agent_sequence)}*\n")
            
            for step in workflow_steps:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']} [{step.get('agent', 'System')}]")
            
            response_parts.append("\n### ✅ Test Drive Scheduled!\n")
            response_parts.append(f"- **Confirmation:** {apt.get('confirmation_id')}")
            response_parts.append(f"- **Vehicle:** {td_result.get('vehicle_name', apt.get('vehicle'))}")
            response_parts.append(f"- **Date:** {apt.get('scheduled_date')}")
            response_parts.append(f"- **Time:** {apt.get('scheduled_time')}")
            response_parts.append(f"- **Location:** {apt.get('location')}")
            
            yield {"type": "response", "content": "\n".join(response_parts)}
            
        elif intent == "financing":
            # Finance Specialist Agent
            step3 = {
                "step": "finance_agent",
                "status": "active",
                "label": "💰 Finance Specialist",
                "agent": "Finance Specialist"
            }
            workflow_steps.append(step3)
            yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
            
            fin_result = await self.finance_agent.calculate_options(user_input)
            agent_sequence.append("Finance Specialist")
            
            await asyncio.sleep(STEP_DELAY)
            
            workflow_steps[-1]["status"] = "complete"
            workflow_steps[-1]["result"] = {"monthly_payment": fin_result["financing_info"]["monthly_payment"]}
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            fin = fin_result["financing_info"]
            response_parts = ["## 🚗 Automotive Sales Assistant\n"]
            response_parts.append("### Multi-Agent Workflow:")
            response_parts.append(f"*Agents: {' → '.join(agent_sequence)}*\n")
            
            for step in workflow_steps:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']} [{step.get('agent', 'System')}]")
            
            response_parts.append("\n### 💰 Financing Options:\n")
            response_parts.append(f"- **Vehicle Price:** ${fin['vehicle_price']:,}")
            response_parts.append(f"- **Down Payment:** ${fin['down_payment']:,}")
            response_parts.append(f"- **Loan Amount:** ${fin['loan_amount']:,}")
            response_parts.append(f"- **Term:** {fin['term_months']} months")
            response_parts.append(f"- **Interest Rate:** {fin['interest_rate']}%")
            response_parts.append(f"- **Monthly Payment:** **${fin['monthly_payment']:,.2f}**\n")
            
            if fin_result.get("advice"):
                response_parts.append(f"### 💡 Finance Advice:\n{fin_result['advice']}")
            
            yield {"type": "response", "content": "\n".join(response_parts)}
            
        elif intent == "service":
            # Service Advisor Agent
            step3 = {
                "step": "service_agent",
                "status": "active",
                "label": "🔧 Service Advisor",
                "agent": "Service Advisor"
            }
            workflow_steps.append(step3)
            yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
            
            svc_result = await self.service_agent.handle_service_request(user_input)
            agent_sequence.append("Service Advisor")
            
            await asyncio.sleep(STEP_DELAY)
            
            workflow_steps[-1]["status"] = "complete"
            workflow_steps[-1]["result"] = {"service_type": svc_result["service_type"]}
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            apt = svc_result["appointment"]
            response_parts = ["## 🚗 Automotive Sales Assistant\n"]
            response_parts.append("### Multi-Agent Workflow:")
            response_parts.append(f"*Agents: {' → '.join(agent_sequence)}*\n")
            
            for step in workflow_steps:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']} [{step.get('agent', 'System')}]")
            
            response_parts.append("\n### 🔧 Service Appointment Booked!\n")
            response_parts.append(f"- **Confirmation:** {apt.get('confirmation_id')}")
            response_parts.append(f"- **Service:** {apt.get('service_type')}")
            response_parts.append(f"- **Date:** {apt.get('scheduled_date')}")
            response_parts.append(f"- **Estimated Cost:** {apt.get('estimated_cost')}\n")
            
            if svc_result.get("advice"):
                response_parts.append(f"### 💡 Service Advice:\n{svc_result['advice']}")
            
            yield {"type": "response", "content": "\n".join(response_parts)}
            
        else:
            # General inquiry - use supervisor LLM
            agent_sequence.append("Supervisor")
            response = await self.llm_service.chat(
                messages,
                self.get_system_prompt() + "\n\nAvailable Vehicles:\n" + self._get_inventory_context()
            )
            yield {"type": "response", "content": response}
