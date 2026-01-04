"""Order Fulfillment Agent - Multi-Agent Architecture with Sequential Chain Pattern.

This demonstrates a true multi-agent system where agents form a processing chain:
- Order Intake Agent: Receives and validates orders
- Inventory Agent: Checks and allocates stock across warehouses
- Warehouse Agent: Generates optimized pick lists
- Shipping Agent: Schedules delivery and tracking

Each agent processes the order and passes it to the next in the chain.
Human-in-the-loop approval is required between Inventory and Warehouse agents.
"""
from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent
from app.data.mock_data import MockDataStore
from app.tools.fulfillment_tools import FulfillmentTools
from app.services.llm_service import LLMService
import asyncio
import uuid

# Delay between workflow steps to simulate real processing
STEP_DELAY = 0.8  # seconds

# In-memory storage for pending approvals (in production, use Redis or database)
PENDING_APPROVALS: Dict[str, Dict[str, Any]] = {}


class FulfillmentChainState(TypedDict):
    """Shared state passed through the agent chain."""
    messages: List[Dict[str, str]]
    conversation_history: List[Dict[str, str]]
    context: Dict[str, Any]
    user_input: str
    
    # Agent tracking
    current_agent: str
    agent_outputs: Dict[str, Any]
    agent_chain: List[str]
    
    # Order state (passed through chain)
    order_id: Optional[str]
    items: List[Dict[str, Any]]
    inventory_results: List[Dict[str, Any]]
    allocations: List[Dict[str, Any]]
    pick_list: Optional[Dict[str, Any]]
    delivery_info: Optional[Dict[str, Any]]
    
    # Workflow state
    workflow_steps: List[Dict[str, Any]]
    result: Optional[str]


# ============================================================================
# CHAIN AGENTS - Each processes and passes to the next
# ============================================================================

class OrderIntakeAgent:
    """Agent responsible for receiving and validating orders."""
    
    def __init__(self):
        self.name = "Order Intake Agent"
        self.tools = FulfillmentTools()
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are an Order Intake specialist responsible for:
1. Receiving and logging incoming orders
2. Validating order items and quantities
3. Checking for any order anomalies
4. Passing validated orders to the Inventory Agent

Be thorough in validation and flag any potential issues."""

    async def process_order(self, user_input: str) -> Dict[str, Any]:
        """Receive and validate the order."""
        
        user_lower = user_input.lower()
        
        # Parse items from message
        items = []
        if "oat milk" in user_lower:
            items.append({"sku": "SKU001", "name": "Organic Oat Milk 1L", "quantity": 100})
        if "tteokbokki" in user_lower or "korean" in user_lower:
            items.append({"sku": "SKU002", "name": "Korean Rosé Tteokbokki", "quantity": 50})
        if "tea" in user_lower:
            items.append({"sku": "SKU003", "name": "Premium Green Tea", "quantity": 75})
        
        if not items:
            # Default demo order
            items = [{"sku": "SKU001", "name": "Organic Oat Milk 1L", "quantity": 100}]
        
        # Validate and create order
        order_result = self.tools.receive_order(items)
        
        # LLM validation check
        items_list = ", ".join([f"{i['name']} x{i['quantity']}" for i in items])
        validation_prompt = f"""Validate this order:
Items: {items_list}
Order ID: {order_result['order_id']}

Check for:
1. Reasonable quantities
2. Item compatibility
3. Any flags or concerns

Respond with: VALID or NEEDS_REVIEW and a brief reason."""

        validation = await self.llm_service.generate(validation_prompt, self.get_system_prompt())
        
        return {
            "agent": self.name,
            "order_id": order_result["order_id"],
            "items": order_result["items"],
            "validation": validation.strip(),
            "status": "validated",
            "handoff_to": "Inventory Agent"
        }


class InventoryAgent:
    """Agent responsible for inventory checking and allocation."""
    
    def __init__(self):
        self.name = "Inventory Agent"
        self.tools = FulfillmentTools()
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are an Inventory Management specialist responsible for:
1. Checking stock levels across all warehouses
2. Identifying optimal warehouse locations for fulfillment
3. Allocating inventory to orders
4. Flagging any stock shortages

Optimize for minimal shipping distance and stock availability."""

    async def check_and_allocate(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check inventory and allocate stock."""
        
        items = order_data["items"]
        
        # Check inventory for each item
        inventory_results = []
        for item in items:
            result = self.tools.check_inventory(item["sku"])
            result["item_name"] = item["name"]
            result["quantity_needed"] = item["quantity"]
            inventory_results.append(result)
        
        # Allocate from warehouses
        allocations = []
        for inv_result in inventory_results:
            allocation = self.tools.allocate_inventory(
                inv_result["sku"],
                inv_result["quantity_needed"],
                inv_result.get("warehouses", [])
            )
            allocation["item_name"] = inv_result["item_name"]
            allocations.append(allocation)
        
        # LLM optimization analysis
        warehouses_used = list(set(
            a.get("warehouse_name", "Unknown")
            for alloc in allocations
            for a in alloc.get("allocations", [])
        ))
        
        analysis_prompt = f"""Analyze this inventory allocation:
Order ID: {order_data['order_id']}
Items: {len(items)}
Warehouses Used: {', '.join(warehouses_used)}

Provide a brief optimization note (1-2 sentences) about this allocation strategy."""

        analysis = await self.llm_service.generate(analysis_prompt, self.get_system_prompt())
        
        return {
            "agent": self.name,
            "inventory_results": inventory_results,
            "allocations": allocations,
            "warehouses_used": warehouses_used,
            "optimization_note": analysis.strip(),
            "handoff_to": "Warehouse Agent (requires approval)"
        }


class WarehouseAgent:
    """Agent responsible for warehouse operations and pick lists."""
    
    def __init__(self):
        self.name = "Warehouse Agent"
        self.tools = FulfillmentTools()
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are a Warehouse Operations specialist responsible for:
1. Generating optimized pick lists
2. Organizing picks by zone for efficiency
3. Estimating pick times
4. Coordinating warehouse workers

Optimize pick routes for minimal travel time."""

    async def generate_picks(self, allocation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized pick list from allocations."""
        
        allocations = allocation_data["allocations"]
        
        # Flatten allocations for pick list
        all_picks = []
        for alloc in allocations:
            for pick in alloc.get("allocations", []):
                pick["sku"] = alloc["sku"]
                all_picks.append(pick)
        
        # Generate pick list
        pick_list = self.tools.generate_pick_list(all_picks)
        
        # LLM route optimization
        zones = list(set(p.get("zone", "A") for p in all_picks))
        
        route_prompt = f"""Optimize pick route for:
Pick List ID: {pick_list['pick_list_id']}
Zones: {', '.join(zones)}
Total Picks: {len(all_picks)}

Provide a brief route recommendation (1-2 sentences)."""

        route_advice = await self.llm_service.generate(route_prompt, self.get_system_prompt())
        
        return {
            "agent": self.name,
            "pick_list": pick_list,
            "zones_involved": zones,
            "route_advice": route_advice.strip(),
            "handoff_to": "Shipping Agent"
        }


class ShippingAgent:
    """Agent responsible for delivery scheduling and tracking."""
    
    def __init__(self):
        self.name = "Shipping Agent"
        self.tools = FulfillmentTools()
        self.llm_service = LLMService()
    
    def get_system_prompt(self) -> str:
        return """You are a Shipping and Logistics specialist responsible for:
1. Scheduling deliveries
2. Selecting optimal carriers
3. Generating tracking information
4. Providing delivery ETAs

Optimize for cost and delivery speed."""

    async def schedule_delivery(self, order_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Schedule delivery for the order."""
        
        # Schedule with carrier
        delivery = self.tools.schedule_delivery(order_id, items)
        
        # LLM shipping analysis
        total_items = sum(item["quantity"] for item in items)
        
        shipping_prompt = f"""Analyze shipping for:
Order ID: {order_id}
Total Items: {total_items}
Carrier: {delivery['carrier']}
Delivery Date: {delivery['delivery_date']}

Provide a brief shipping note (1-2 sentences)."""

        shipping_note = await self.llm_service.generate(shipping_prompt, self.get_system_prompt())
        
        return {
            "agent": self.name,
            "delivery_info": delivery,
            "shipping_note": shipping_note.strip(),
            "status": "completed"
        }


# ============================================================================
# SUPERVISOR/CHAIN COORDINATOR
# ============================================================================

class OrderFulfillmentAgent(BaseAgent):
    """
    Multi-Agent Chain Coordinator for Order Fulfillment.
    
    Coordinates a sequential chain of specialist agents:
    Order Intake → Inventory → [Human Approval] → Warehouse → Shipping
    
    Each agent processes and hands off to the next in the chain.
    """
    
    def __init__(self):
        # Initialize chain agents
        self.intake_agent = OrderIntakeAgent()
        self.inventory_agent = InventoryAgent()
        self.warehouse_agent = WarehouseAgent()
        self.shipping_agent = ShippingAgent()
        self.tools = FulfillmentTools()
        
        super().__init__(
            name="Order Fulfillment Chain Coordinator",
            description="Multi-agent chain for end-to-end order fulfillment with human-in-the-loop"
        )
    
    def get_system_prompt(self) -> str:
        warehouses = self._get_warehouse_context()
        
        return f"""You are the coordinator of a multi-agent order fulfillment chain.

Agent Chain:
📥 Order Intake Agent → Receives and validates orders
📦 Inventory Agent → Checks stock and allocates inventory
👤 Human Approval → Manager reviews allocation
🏭 Warehouse Agent → Generates pick lists
🚚 Shipping Agent → Schedules delivery

WAREHOUSE NETWORK:
{warehouses}

Your role is to:
1. Coordinate the agent chain
2. Ensure smooth handoffs between agents
3. Pause for human approval when required
4. Aggregate final results"""

    def _get_warehouse_context(self) -> str:
        lines = []
        for wh_id, wh in MockDataStore.WAREHOUSES.items():
            lines.append(f"\n**{wh['name']}** ({wh_id})")
            lines.append(f"Location: {wh['location']}")
            for sku, item in wh["inventory"].items():
                lines.append(f"  - {sku}: {item['name']} (Qty: {item['quantity']})")
        return "\n".join(lines)
    
    def _build_graph(self) -> StateGraph:
        """Build the multi-agent chain workflow."""
        
        async def intake_node(state: FulfillmentChainState) -> FulfillmentChainState:
            """Order Intake Agent processes the order."""
            state["workflow_steps"].append({
                "step": "intake",
                "status": "active",
                "label": "📥 Order Intake Agent",
                "agent": "Order Intake"
            })
            state["current_agent"] = "Order Intake Agent"
            
            result = await self.intake_agent.process_order(state["user_input"])
            
            state["order_id"] = result["order_id"]
            state["items"] = result["items"]
            state["agent_outputs"]["order_intake"] = result
            state["agent_chain"].append("Order Intake")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "order_id": result["order_id"],
                "items": len(result["items"]),
                "handoff": result["handoff_to"]
            }
            
            return state
        
        async def inventory_node(state: FulfillmentChainState) -> FulfillmentChainState:
            """Inventory Agent checks and allocates stock."""
            state["workflow_steps"].append({
                "step": "inventory",
                "status": "active",
                "label": "📦 Inventory Agent",
                "agent": "Inventory"
            })
            state["current_agent"] = "Inventory Agent"
            
            order_data = {
                "order_id": state["order_id"],
                "items": state["items"]
            }
            
            result = await self.inventory_agent.check_and_allocate(order_data)
            
            state["inventory_results"] = result["inventory_results"]
            state["allocations"] = result["allocations"]
            state["agent_outputs"]["inventory"] = result
            state["agent_chain"].append("Inventory")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "warehouses": result["warehouses_used"],
                "handoff": result["handoff_to"]
            }
            
            return state
        
        async def warehouse_node(state: FulfillmentChainState) -> FulfillmentChainState:
            """Warehouse Agent generates pick lists."""
            state["workflow_steps"].append({
                "step": "warehouse",
                "status": "active",
                "label": "🏭 Warehouse Agent",
                "agent": "Warehouse"
            })
            state["current_agent"] = "Warehouse Agent"
            
            allocation_data = {
                "allocations": state["allocations"]
            }
            
            result = await self.warehouse_agent.generate_picks(allocation_data)
            
            state["pick_list"] = result["pick_list"]
            state["agent_outputs"]["warehouse"] = result
            state["agent_chain"].append("Warehouse")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "pick_list_id": result["pick_list"]["pick_list_id"],
                "handoff": result["handoff_to"]
            }
            
            return state
        
        async def shipping_node(state: FulfillmentChainState) -> FulfillmentChainState:
            """Shipping Agent schedules delivery."""
            state["workflow_steps"].append({
                "step": "shipping",
                "status": "active",
                "label": "🚚 Shipping Agent",
                "agent": "Shipping"
            })
            state["current_agent"] = "Shipping Agent"
            
            result = await self.shipping_agent.schedule_delivery(
                state["order_id"],
                state["items"]
            )
            
            state["delivery_info"] = result["delivery_info"]
            state["agent_outputs"]["shipping"] = result
            state["agent_chain"].append("Shipping")
            
            await asyncio.sleep(STEP_DELAY)
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "tracking": result["delivery_info"]["tracking_number"]
            }
            
            return state
        
        async def generate_response(state: FulfillmentChainState) -> FulfillmentChainState:
            """Generate final response aggregating all agent outputs."""
            
            response_parts = [
                f"## 📦 Order Fulfillment Complete\n",
                f"**Order ID:** {state['order_id']}\n",
                f"### Multi-Agent Chain:",
                f"*{' → '.join(state['agent_chain'])}*\n"
            ]
            
            for step in state["workflow_steps"]:
                if step["status"] == "complete":
                    emoji = "✅"
                elif step["status"] == "rejected":
                    emoji = "❌"
                else:
                    emoji = "⏳"
                response_parts.append(f"{emoji} **{step['label']}**")
            
            # Add agent-specific insights
            response_parts.append(f"\n### 📥 Order Intake:")
            intake = state["agent_outputs"].get("order_intake", {})
            response_parts.append(f"- Validation: {intake.get('validation', 'OK')[:50]}...")
            
            response_parts.append(f"\n### 📦 Inventory Allocation:")
            inv = state["agent_outputs"].get("inventory", {})
            for alloc in state["allocations"]:
                status = "✅ Allocated" if alloc["status"] == "success" else "⚠️ Partial"
                response_parts.append(f"- **{alloc.get('item_name', alloc['sku'])}**: {status}")
                for a in alloc.get("allocations", []):
                    response_parts.append(f"  - {a['warehouse_name']}: {a['quantity']} units (Zone {a['zone']})")
            if inv.get("optimization_note"):
                response_parts.append(f"- *{inv['optimization_note'][:100]}*")
            
            response_parts.append(f"\n### 🏭 Warehouse Operations:")
            wh = state["agent_outputs"].get("warehouse", {})
            if state["pick_list"]:
                response_parts.append(f"- **Pick List:** {state['pick_list']['pick_list_id']}")
                response_parts.append(f"- **Est. Pick Time:** {state['pick_list']['estimated_pick_time']}")
            if wh.get("route_advice"):
                response_parts.append(f"- *{wh['route_advice'][:100]}*")
            
            response_parts.append(f"\n### 🚚 Shipping:")
            ship = state["agent_outputs"].get("shipping", {})
            if state["delivery_info"]:
                response_parts.append(f"- **Tracking:** {state['delivery_info']['tracking_number']}")
                response_parts.append(f"- **Carrier:** {state['delivery_info']['carrier']}")
                response_parts.append(f"- **Delivery Date:** {state['delivery_info']['delivery_date']}")
            if ship.get("shipping_note"):
                response_parts.append(f"- *{ship['shipping_note'][:100]}*")
            
            state["result"] = "\n".join(response_parts)
            state["messages"].append({"role": "assistant", "content": state["result"]})
            
            return state
        
        async def handle_general_query(state: FulfillmentChainState) -> FulfillmentChainState:
            """Handle general queries about fulfillment."""
            response = await self.llm_service.chat(
                state["messages"],
                self.get_system_prompt()
            )
            state["result"] = response
            state["messages"].append({"role": "assistant", "content": response})
            return state
        
        def should_process_order(state: FulfillmentChainState) -> str:
            """Determine if this is an order to process or general query."""
            user_message = state["messages"][-1]["content"].lower()
            order_keywords = ["process", "order", "fulfill", "ship", "deliver", "units", "quantity"]
            
            if any(kw in user_message for kw in order_keywords):
                return "intake"
            return "general"
        
        # Build the graph
        workflow = StateGraph(FulfillmentChainState)
        
        # Add nodes
        workflow.add_node("router", lambda state: state)
        workflow.add_node("intake", intake_node)
        workflow.add_node("inventory", inventory_node)
        workflow.add_node("warehouse", warehouse_node)
        workflow.add_node("shipping", shipping_node)
        workflow.add_node("respond", generate_response)
        workflow.add_node("general", handle_general_query)
        
        # Set entry point with routing
        workflow.set_entry_point("router")
        workflow.add_conditional_edges(
            "router",
            should_process_order,
            {
                "intake": "intake",
                "general": "general"
            }
        )
        
        # Chain edges: Intake → Inventory → Warehouse → Shipping → Respond
        workflow.add_edge("intake", "inventory")
        workflow.add_edge("inventory", "warehouse")
        workflow.add_edge("warehouse", "shipping")
        workflow.add_edge("shipping", "respond")
        workflow.add_edge("respond", END)
        workflow.add_edge("general", END)
        
        return workflow
    
    async def run(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Run the multi-agent fulfillment chain."""
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        initial_state: FulfillmentChainState = {
            "messages": messages,
            "conversation_history": conversation_history or [],
            "context": context or {},
            "user_input": user_input,
            "current_agent": "Coordinator",
            "agent_outputs": {},
            "agent_chain": [],
            "order_id": None,
            "items": [],
            "inventory_results": [],
            "allocations": [],
            "pick_list": None,
            "delivery_info": None,
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
            "agent_chain": final_state.get("agent_chain", [])
        }
    
    async def run_with_streaming(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ):
        """Run the multi-agent chain with streaming and human-in-the-loop."""
        
        user_message = user_input.lower()
        ctx = context or {}
        
        # Build full messages list for LLM calls
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        # Check if this is an approval response
        if ctx.get("approval_id"):
            async for event in self._continue_after_approval(ctx["approval_id"], ctx.get("approved", False)):
                yield event
            return
        
        order_keywords = ["process", "order", "fulfill", "ship", "deliver", "units", "quantity"]
        
        # Check if this is an order or general query
        if not any(kw in user_message for kw in order_keywords):
            response = await self.llm_service.chat(messages, self.get_system_prompt())
            yield {"type": "response", "content": response}
            return
        
        # Process order with streaming agent chain
        workflow_steps = []
        agent_chain = []
        agent_outputs = {}
        
        # ========================================
        # Agent 1: Order Intake Agent
        # ========================================
        step1 = {
            "step": "intake",
            "status": "active",
            "label": "📥 Order Intake Agent",
            "agent": "Order Intake"
        }
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        intake_result = await self.intake_agent.process_order(user_input)
        agent_chain.append("Order Intake")
        agent_outputs["order_intake"] = intake_result
        
        order_id = intake_result["order_id"]
        items = intake_result["items"]
        
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {
            "order_id": order_id,
            "items": len(items),
            "handoff": "Inventory Agent"
        }
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # ========================================
        # Agent 2: Inventory Agent
        # ========================================
        step2 = {
            "step": "inventory",
            "status": "active",
            "label": "📦 Inventory Agent",
            "agent": "Inventory"
        }
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        inv_result = await self.inventory_agent.check_and_allocate({
            "order_id": order_id,
            "items": items
        })
        agent_chain.append("Inventory")
        agent_outputs["inventory"] = inv_result
        
        allocations = inv_result["allocations"]
        
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {
            "warehouses": inv_result["warehouses_used"],
            "handoff": "Human Approval"
        }
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # ========================================
        # Human-in-the-Loop: Manager Approval
        # ========================================
        step3 = {
            "step": "approval",
            "status": "active",
            "label": "👤 Manager Approval",
            "agent": "Human"
        }
        workflow_steps.append(step3)
        yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
        
        # Generate approval ID and store state
        approval_id = str(uuid.uuid4())[:8]
        
        total_items = sum(item["quantity"] for item in items)
        total_value = total_items * 15  # Simulated value
        
        approval_data = {
            "order_id": order_id,
            "items": items,
            "allocations": allocations,
            "inventory_results": inv_result["inventory_results"],
            "total_items": total_items,
            "estimated_value": f"${total_value:,}",
            "workflow_steps": workflow_steps.copy(),
            "agent_chain": agent_chain.copy(),
            "agent_outputs": agent_outputs.copy()
        }
        
        PENDING_APPROVALS[approval_id] = approval_data
        
        # Yield approval required event
        yield {
            "type": "approval_required",
            "approval_id": approval_id,
            "title": "Manager Approval Required",
            "message": f"Order {order_id} requires manager approval before Warehouse Agent can proceed.",
            "details": {
                "order_id": order_id,
                "total_items": total_items,
                "estimated_value": f"${total_value:,}",
                "items_summary": [f"{item['name']} x{item['quantity']}" for item in items],
                "warehouses_involved": inv_result["warehouses_used"],
                "agents_completed": agent_chain
            },
            "all_steps": workflow_steps.copy()
        }
    
    async def _continue_after_approval(self, approval_id: str, approved: bool):
        """Continue the agent chain after human approval."""
        
        if approval_id not in PENDING_APPROVALS:
            yield {"type": "error", "content": f"Approval {approval_id} not found or expired."}
            return
        
        data = PENDING_APPROVALS.pop(approval_id)
        workflow_steps = data["workflow_steps"]
        agent_chain = data["agent_chain"]
        agent_outputs = data["agent_outputs"]
        
        if not approved:
            workflow_steps[-1]["status"] = "rejected"
            workflow_steps[-1]["result"] = {"decision": "rejected"}
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            yield {
                "type": "response",
                "content": f"## ❌ Order Rejected\n\n**Order ID:** {data['order_id']}\n\n*Agent Chain: {' → '.join(agent_chain)} → ❌ Rejected*\n\nThe order was rejected by the manager. Warehouse and Shipping agents will not process this order."
            }
            return
        
        # Approval granted
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"decision": "approved", "approver": "Manager"}
        agent_chain.append("Human Approval")
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        
        # ========================================
        # Agent 3: Warehouse Agent
        # ========================================
        step4 = {
            "step": "warehouse",
            "status": "active",
            "label": "🏭 Warehouse Agent",
            "agent": "Warehouse"
        }
        workflow_steps.append(step4)
        yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
        
        wh_result = await self.warehouse_agent.generate_picks({
            "allocations": data["allocations"]
        })
        agent_chain.append("Warehouse")
        agent_outputs["warehouse"] = wh_result
        
        pick_list = wh_result["pick_list"]
        
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {
            "pick_list_id": pick_list["pick_list_id"],
            "handoff": "Shipping Agent"
        }
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # ========================================
        # Agent 4: Shipping Agent
        # ========================================
        step5 = {
            "step": "shipping",
            "status": "active",
            "label": "🚚 Shipping Agent",
            "agent": "Shipping"
        }
        workflow_steps.append(step5)
        yield {"type": "workflow_step", "step": step5, "all_steps": workflow_steps.copy()}
        
        ship_result = await self.shipping_agent.schedule_delivery(
            data["order_id"],
            data["items"]
        )
        agent_chain.append("Shipping")
        agent_outputs["shipping"] = ship_result
        
        delivery = ship_result["delivery_info"]
        
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"tracking": delivery["tracking_number"]}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # ========================================
        # Generate Final Response
        # ========================================
        items = data["items"]
        allocations = data["allocations"]
        
        response_parts = [
            f"## 📦 Order Fulfillment Complete\n",
            f"**Order ID:** {data['order_id']}\n",
            f"### Multi-Agent Chain:",
            f"*{' → '.join(agent_chain)}*\n"
        ]
        
        for step in workflow_steps:
            if step["status"] == "complete":
                emoji = "✅"
            elif step["status"] == "rejected":
                emoji = "❌"
            else:
                emoji = "⏳"
            response_parts.append(f"{emoji} **{step['label']}** [{step.get('agent', 'System')}]")
        
        # Intake summary
        response_parts.append(f"\n### 📥 Order Intake Agent:")
        intake = agent_outputs.get("order_intake", {})
        response_parts.append(f"- Validation: {intake.get('validation', 'OK')[:80]}...")
        
        # Inventory summary
        response_parts.append(f"\n### 📦 Inventory Agent:")
        inv = agent_outputs.get("inventory", {})
        for alloc in allocations:
            status = "✅ Allocated" if alloc["status"] == "success" else "⚠️ Partial"
            response_parts.append(f"- **{alloc.get('item_name', alloc['sku'])}**: {status}")
            for a in alloc.get("allocations", []):
                response_parts.append(f"  - {a['warehouse_name']}: {a['quantity']} units (Zone {a['zone']})")
        if inv.get("optimization_note"):
            response_parts.append(f"- 💡 *{inv['optimization_note'][:100]}*")
        
        # Warehouse summary
        response_parts.append(f"\n### 🏭 Warehouse Agent:")
        wh = agent_outputs.get("warehouse", {})
        response_parts.append(f"- **Pick List:** {pick_list['pick_list_id']}")
        response_parts.append(f"- **Est. Pick Time:** {pick_list['estimated_pick_time']}")
        if wh.get("route_advice"):
            response_parts.append(f"- 💡 *{wh['route_advice'][:100]}*")
        
        # Shipping summary
        response_parts.append(f"\n### 🚚 Shipping Agent:")
        ship = agent_outputs.get("shipping", {})
        response_parts.append(f"- **Tracking:** {delivery['tracking_number']}")
        response_parts.append(f"- **Carrier:** {delivery['carrier']}")
        response_parts.append(f"- **Delivery Date:** {delivery['delivery_date']}")
        if ship.get("shipping_note"):
            response_parts.append(f"- 💡 *{ship['shipping_note'][:100]}*")
        
        yield {"type": "response", "content": "\n".join(response_parts)}
