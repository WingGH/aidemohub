"""Automotive Sales Agent - Real multi-step agentic workflow with tools."""
from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent
from app.data.mock_data import MockDataStore
from app.tools.automotive_tools import AutomotiveTools
import asyncio

# Delay between workflow steps to simulate real processing
STEP_DELAY = 1.0  # seconds


class AutomotiveState(TypedDict):
    """State for automotive sales workflow."""
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    current_step: str
    intent: Optional[str]
    vehicles_found: List[Dict[str, Any]]
    selected_vehicle: Optional[Dict[str, Any]]
    financing_info: Optional[Dict[str, Any]]
    appointment: Optional[Dict[str, Any]]
    workflow_steps: List[Dict[str, Any]]
    result: Optional[str]


class AutomotiveSalesAgent(BaseAgent):
    """Agent for handling automotive sales with real tool-based workflow."""
    
    def __init__(self):
        self.tools = AutomotiveTools()
        super().__init__(
            name="Automotive Sales Agent",
            description="Handles end-to-end customer journeys for vehicle sales and service"
        )
    
    def get_system_prompt(self) -> str:
        return """You are an expert automotive sales and service AI assistant.

You execute a multi-step workflow based on customer intent:
1. UNDERSTAND - Identify what the customer needs
2. SEARCH/RECOMMEND - Find matching vehicles or services
3. DETAILS - Provide detailed information
4. ACTION - Schedule test drives, calculate financing, or book service

Available vehicles in inventory:
""" + self._get_inventory_context() + """

Guidelines:
- Be professional, friendly, and knowledgeable
- Use tools to search vehicles and check availability
- Provide specific pricing and financing calculations
- Always aim to move toward a positive outcome"""

    def _get_inventory_context(self) -> str:
        vehicles = MockDataStore.get_available_vehicles()
        lines = []
        for v in vehicles:
            lines.append(f"- {v['year']} {v['brand']} {v['model']} ({v['color']}) - ${v['price']:,}")
        return "\n".join(lines)
    
    def _build_graph(self) -> StateGraph:
        """Build the automotive sales workflow."""
        
        async def understand_intent(state: AutomotiveState) -> AutomotiveState:
            """Step 1: Understand customer intent."""
            state["workflow_steps"].append({
                "step": "understand",
                "status": "active",
                "label": "Understanding Request"
            })
            
            user_message = state["messages"][-1]["content"].lower()
            
            if any(word in user_message for word in ["test drive", "schedule", "try"]):
                state["intent"] = "test_drive"
            elif any(word in user_message for word in ["finance", "payment", "loan", "monthly"]):
                state["intent"] = "financing"
            elif any(word in user_message for word in ["service", "repair", "maintenance", "brake", "oil"]):
                state["intent"] = "service"
            elif any(word in user_message for word in ["show", "available", "looking", "want", "find", "under"]):
                state["intent"] = "search"
            else:
                state["intent"] = "inquiry"
            
            await asyncio.sleep(STEP_DELAY)  # Simulate intent analysis time
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {"intent": state["intent"]}
            
            return state
        
        async def search_vehicles(state: AutomotiveState) -> AutomotiveState:
            """Step 2: Search for vehicles."""
            state["workflow_steps"].append({
                "step": "search",
                "status": "active",
                "label": "Searching Inventory"
            })
            
            user_message = state["messages"][-1]["content"].lower()
            
            # Parse price limit
            max_price = None
            if "under" in user_message:
                import re
                prices = re.findall(r'\$?([\d,]+)', user_message)
                if prices:
                    max_price = float(prices[0].replace(',', ''))
            
            # Parse brand
            brand = None
            for b in ["toyota", "honda", "bmw", "mercedes", "lexus"]:
                if b in user_message:
                    brand = b.title()
                    break
            
            result = self.tools.search_vehicles(max_price=max_price, brand=brand)
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            state["vehicles_found"] = result["vehicles"]
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {"count": result["count"]}
            
            return state
        
        async def provide_details(state: AutomotiveState) -> AutomotiveState:
            """Step 3: Provide vehicle details."""
            state["workflow_steps"].append({
                "step": "details",
                "status": "active",
                "label": "Getting Details"
            })
            
            # Select best match or first vehicle
            if state["vehicles_found"]:
                vehicle = state["vehicles_found"][0]
                details = self.tools.get_vehicle_details(vehicle["id"])
                await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
                state["selected_vehicle"] = details.get("vehicle", vehicle)
            
            state["workflow_steps"][-1]["status"] = "complete"
            
            return state
        
        async def schedule_test_drive(state: AutomotiveState) -> AutomotiveState:
            """Schedule a test drive."""
            state["workflow_steps"].append({
                "step": "schedule",
                "status": "active",
                "label": "Scheduling Test Drive"
            })
            
            user_message = state["messages"][-1]["content"].lower()
            
            # Find mentioned vehicle
            vehicle_id = None
            for v in MockDataStore.VEHICLES:
                if v["brand"].lower() in user_message or v["model"].lower() in user_message:
                    vehicle_id = v["id"]
                    break
            
            if not vehicle_id and state["vehicles_found"]:
                vehicle_id = state["vehicles_found"][0]["id"]
            
            if vehicle_id:
                result = self.tools.schedule_test_drive(
                    vehicle_id=vehicle_id,
                    customer_name="Valued Customer"
                )
                await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
                state["appointment"] = result
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = state["appointment"]
            
            return state
        
        async def calculate_financing(state: AutomotiveState) -> AutomotiveState:
            """Calculate financing options."""
            state["workflow_steps"].append({
                "step": "finance",
                "status": "active",
                "label": "Calculating Financing"
            })
            
            vehicle_price = 40000  # Default
            if state["selected_vehicle"]:
                vehicle_price = state["selected_vehicle"].get("price", 40000)
            elif state["vehicles_found"]:
                vehicle_price = state["vehicles_found"][0].get("price", 40000)
            
            # Check for term in message
            user_message = state["messages"][-1]["content"].lower()
            term = 60
            if "3 year" in user_message or "36" in user_message:
                term = 36
            elif "4 year" in user_message or "48" in user_message:
                term = 48
            elif "6 year" in user_message or "72" in user_message:
                term = 72
            
            result = self.tools.calculate_financing(
                vehicle_price=vehicle_price,
                down_payment=5000,
                term_months=term
            )
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            state["financing_info"] = result
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = result
            
            return state
        
        async def book_service(state: AutomotiveState) -> AutomotiveState:
            """Book a service appointment."""
            state["workflow_steps"].append({
                "step": "service",
                "status": "active",
                "label": "Booking Service"
            })
            
            user_message = state["messages"][-1]["content"]
            
            # Determine service type
            service_type = "General inspection"
            if "brake" in user_message.lower():
                service_type = "Brake service"
            elif "oil" in user_message.lower():
                service_type = "Oil change"
            elif "tire" in user_message.lower():
                service_type = "Tire service"
            
            result = self.tools.book_service_appointment(
                vehicle_info="Customer's vehicle",
                service_type=service_type
            )
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            state["appointment"] = result
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = result
            
            return state
        
        async def generate_response(state: AutomotiveState) -> AutomotiveState:
            """Generate final response based on workflow results."""
            
            response_parts = ["## 🚗 Automotive Sales Assistant\n"]
            
            # Show workflow steps
            response_parts.append("### Workflow:")
            for step in state["workflow_steps"]:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']}")
            
            response_parts.append("")
            
            # Show results based on intent
            if state["intent"] == "search" and state["vehicles_found"]:
                response_parts.append(f"### Found {len(state['vehicles_found'])} Vehicles:\n")
                for v in state["vehicles_found"]:
                    response_parts.append(f"**{v['year']} {v['brand']} {v['model']}**")
                    response_parts.append(f"- Color: {v['color']}")
                    response_parts.append(f"- Price: ${v['price']:,}")
                    response_parts.append(f"- Status: {v['status'].title()}\n")
            
            if state["intent"] == "test_drive" and state["appointment"]:
                apt = state["appointment"]
                response_parts.append("### ✅ Test Drive Scheduled!\n")
                response_parts.append(f"- **Confirmation:** {apt.get('confirmation_id')}")
                response_parts.append(f"- **Vehicle:** {apt.get('vehicle')}")
                response_parts.append(f"- **Date:** {apt.get('scheduled_date')}")
                response_parts.append(f"- **Time:** {apt.get('scheduled_time')}")
                response_parts.append(f"- **Location:** {apt.get('location')}")
            
            if state["intent"] == "financing" and state["financing_info"]:
                fin = state["financing_info"]
                response_parts.append("### 💰 Financing Options:\n")
                response_parts.append(f"- **Vehicle Price:** ${fin['vehicle_price']:,}")
                response_parts.append(f"- **Down Payment:** ${fin['down_payment']:,}")
                response_parts.append(f"- **Loan Amount:** ${fin['loan_amount']:,}")
                response_parts.append(f"- **Term:** {fin['term_months']} months")
                response_parts.append(f"- **Interest Rate:** {fin['interest_rate']}%")
                response_parts.append(f"- **Monthly Payment:** **${fin['monthly_payment']:,.2f}**")
            
            if state["intent"] == "service" and state["appointment"]:
                apt = state["appointment"]
                response_parts.append("### 🔧 Service Appointment Booked!\n")
                response_parts.append(f"- **Confirmation:** {apt.get('confirmation_id')}")
                response_parts.append(f"- **Service:** {apt.get('service_type')}")
                response_parts.append(f"- **Date:** {apt.get('scheduled_date')}")
                response_parts.append(f"- **Estimated Cost:** {apt.get('estimated_cost')}")
            
            if state["intent"] == "inquiry":
                # Use LLM for general inquiries
                llm_response = await self.llm_service.chat(
                    state["messages"],
                    self.get_system_prompt()
                )
                response_parts.append(llm_response)
            
            state["result"] = "\n".join(response_parts)
            state["messages"].append({"role": "assistant", "content": state["result"]})
            
            return state
        
        def route_by_intent(state: AutomotiveState) -> str:
            """Route to appropriate handler based on intent."""
            intent = state.get("intent", "inquiry")
            if intent == "search":
                return "search"
            elif intent == "test_drive":
                return "test_drive"
            elif intent == "financing":
                return "financing"
            elif intent == "service":
                return "service"
            return "respond"
        
        # Build graph
        workflow = StateGraph(AutomotiveState)
        
        workflow.add_node("understand", understand_intent)
        workflow.add_node("search", search_vehicles)
        workflow.add_node("details", provide_details)
        workflow.add_node("test_drive", schedule_test_drive)
        workflow.add_node("financing", calculate_financing)
        workflow.add_node("service", book_service)
        workflow.add_node("respond", generate_response)
        
        workflow.set_entry_point("understand")
        
        workflow.add_conditional_edges(
            "understand",
            route_by_intent,
            {
                "search": "search",
                "test_drive": "test_drive",
                "financing": "financing",
                "service": "service",
                "respond": "respond"
            }
        )
        
        workflow.add_edge("search", "details")
        workflow.add_edge("details", "respond")
        workflow.add_edge("test_drive", "respond")
        workflow.add_edge("financing", "respond")
        workflow.add_edge("service", "respond")
        workflow.add_edge("respond", END)
        
        return workflow
    
    async def run(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the automotive sales workflow."""
        initial_state: AutomotiveState = {
            "messages": [{"role": "user", "content": user_input}],
            "context": context or {},
            "current_step": "start",
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
            "workflow_steps": final_state.get("workflow_steps", [])
        }
    
    async def run_with_streaming(self, user_input: str, context: Dict[str, Any] = None):
        """Run the automotive sales workflow with streaming step updates."""
        import re
        
        user_message = user_input.lower()
        workflow_steps = []
        
        # Step 1: Understand Intent
        step1 = {"step": "understand", "status": "active", "label": "Understanding Request"}
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        # Determine intent
        if any(word in user_message for word in ["test drive", "schedule", "try"]):
            intent = "test_drive"
        elif any(word in user_message for word in ["finance", "payment", "loan", "monthly"]):
            intent = "financing"
        elif any(word in user_message for word in ["service", "repair", "maintenance", "brake", "oil"]):
            intent = "service"
        elif any(word in user_message for word in ["show", "available", "looking", "want", "find", "under"]):
            intent = "search"
        else:
            intent = "inquiry"
        
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"intent": intent}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Handle based on intent
        if intent == "search":
            # Step 2: Search Inventory
            step2 = {"step": "search", "status": "active", "label": "Searching Inventory"}
            workflow_steps.append(step2)
            yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
            
            max_price = None
            if "under" in user_message:
                prices = re.findall(r'\$?([\d,]+)', user_message)
                if prices:
                    max_price = float(prices[0].replace(',', ''))
            
            brand = None
            for b in ["toyota", "honda", "bmw", "mercedes", "lexus"]:
                if b in user_message:
                    brand = b.title()
                    break
            
            result = self.tools.search_vehicles(max_price=max_price, brand=brand)
            await asyncio.sleep(STEP_DELAY)
            
            vehicles_found = result["vehicles"]
            workflow_steps[-1]["status"] = "complete"
            workflow_steps[-1]["result"] = {"count": result["count"]}
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Step 3: Get Details
            step3 = {"step": "details", "status": "active", "label": "Getting Details"}
            workflow_steps.append(step3)
            yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
            
            selected_vehicle = None
            if vehicles_found:
                details = self.tools.get_vehicle_details(vehicles_found[0]["id"])
                await asyncio.sleep(STEP_DELAY)
                selected_vehicle = details.get("vehicle", vehicles_found[0])
            
            workflow_steps[-1]["status"] = "complete"
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Generate response
            response_parts = ["## 🚗 Automotive Sales Assistant\n", "### Workflow:"]
            for step in workflow_steps:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']}")
            
            response_parts.append(f"\n### Found {len(vehicles_found)} Vehicles:\n")
            for v in vehicles_found:
                response_parts.append(f"**{v['year']} {v['brand']} {v['model']}**")
                response_parts.append(f"- Color: {v['color']}")
                response_parts.append(f"- Price: ${v['price']:,}")
                response_parts.append(f"- Status: {v['status'].title()}\n")
            
            yield {"type": "response", "content": "\n".join(response_parts)}
            
        elif intent == "test_drive":
            # Step 2: Schedule Test Drive
            step2 = {"step": "schedule", "status": "active", "label": "Scheduling Test Drive"}
            workflow_steps.append(step2)
            yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
            
            vehicle_id = None
            for v in MockDataStore.VEHICLES:
                if v["brand"].lower() in user_message or v["model"].lower() in user_message:
                    vehicle_id = v["id"]
                    break
            
            if not vehicle_id:
                vehicle_id = MockDataStore.VEHICLES[0]["id"]
            
            appointment = self.tools.schedule_test_drive(vehicle_id, "Valued Customer")
            await asyncio.sleep(STEP_DELAY)
            
            workflow_steps[-1]["status"] = "complete"
            workflow_steps[-1]["result"] = appointment
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Generate response
            response_parts = ["## 🚗 Automotive Sales Assistant\n", "### Workflow:"]
            for step in workflow_steps:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']}")
            
            response_parts.append("\n### ✅ Test Drive Scheduled!\n")
            response_parts.append(f"- **Confirmation:** {appointment.get('confirmation_id')}")
            response_parts.append(f"- **Vehicle:** {appointment.get('vehicle')}")
            response_parts.append(f"- **Date:** {appointment.get('scheduled_date')}")
            response_parts.append(f"- **Time:** {appointment.get('scheduled_time')}")
            response_parts.append(f"- **Location:** {appointment.get('location')}")
            
            yield {"type": "response", "content": "\n".join(response_parts)}
            
        elif intent == "financing":
            # Step 2: Calculate Financing
            step2 = {"step": "finance", "status": "active", "label": "Calculating Financing"}
            workflow_steps.append(step2)
            yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
            
            vehicle_price = 40000
            term = 60
            if "3 year" in user_message or "36" in user_message:
                term = 36
            elif "4 year" in user_message or "48" in user_message:
                term = 48
            elif "6 year" in user_message or "72" in user_message:
                term = 72
            
            financing_info = self.tools.calculate_financing(vehicle_price, 5000, term)
            await asyncio.sleep(STEP_DELAY)
            
            workflow_steps[-1]["status"] = "complete"
            workflow_steps[-1]["result"] = financing_info
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Generate response
            response_parts = ["## 🚗 Automotive Sales Assistant\n", "### Workflow:"]
            for step in workflow_steps:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']}")
            
            response_parts.append("\n### 💰 Financing Options:\n")
            response_parts.append(f"- **Vehicle Price:** ${financing_info['vehicle_price']:,}")
            response_parts.append(f"- **Down Payment:** ${financing_info['down_payment']:,}")
            response_parts.append(f"- **Loan Amount:** ${financing_info['loan_amount']:,}")
            response_parts.append(f"- **Term:** {financing_info['term_months']} months")
            response_parts.append(f"- **Interest Rate:** {financing_info['interest_rate']}%")
            response_parts.append(f"- **Monthly Payment:** **${financing_info['monthly_payment']:,.2f}**")
            
            yield {"type": "response", "content": "\n".join(response_parts)}
            
        elif intent == "service":
            # Step 2: Book Service
            step2 = {"step": "service", "status": "active", "label": "Booking Service"}
            workflow_steps.append(step2)
            yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
            
            service_type = "General inspection"
            if "brake" in user_message:
                service_type = "Brake service"
            elif "oil" in user_message:
                service_type = "Oil change"
            elif "tire" in user_message:
                service_type = "Tire service"
            
            appointment = self.tools.book_service_appointment("Customer's vehicle", service_type)
            await asyncio.sleep(STEP_DELAY)
            
            workflow_steps[-1]["status"] = "complete"
            workflow_steps[-1]["result"] = appointment
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Generate response
            response_parts = ["## 🚗 Automotive Sales Assistant\n", "### Workflow:"]
            for step in workflow_steps:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} {step['label']}")
            
            response_parts.append("\n### 🔧 Service Appointment Booked!\n")
            response_parts.append(f"- **Confirmation:** {appointment.get('confirmation_id')}")
            response_parts.append(f"- **Service:** {appointment.get('service_type')}")
            response_parts.append(f"- **Date:** {appointment.get('scheduled_date')}")
            response_parts.append(f"- **Estimated Cost:** {appointment.get('estimated_cost')}")
            
            yield {"type": "response", "content": "\n".join(response_parts)}
            
        else:
            # General inquiry - use LLM
            response = await self.llm_service.chat(
                [{"role": "user", "content": user_input}],
                self.get_system_prompt()
            )
            yield {"type": "response", "content": response}
