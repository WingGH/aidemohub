"""Order Fulfillment Agent - Real multi-step agentic workflow with Human-in-the-Loop."""
from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent
from app.data.mock_data import MockDataStore
from app.tools.fulfillment_tools import FulfillmentTools
import json
import asyncio
import uuid

# Delay between workflow steps to simulate real processing
STEP_DELAY = 1.0  # seconds

# In-memory storage for pending approvals (in production, use Redis or database)
PENDING_APPROVALS: Dict[str, Dict[str, Any]] = {}


class FulfillmentState(TypedDict):
    """State for fulfillment workflow."""
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    current_step: str
    order_id: Optional[str]
    items: List[Dict[str, Any]]
    inventory_results: List[Dict[str, Any]]
    allocations: List[Dict[str, Any]]
    pick_list: Optional[Dict[str, Any]]
    delivery_info: Optional[Dict[str, Any]]
    workflow_steps: List[Dict[str, Any]]
    result: Optional[str]


class OrderFulfillmentAgent(BaseAgent):
    """Agent for agentic order fulfillment with real multi-step workflow."""
    
    def __init__(self):
        self.tools = FulfillmentTools()
        super().__init__(
            name="Order Fulfillment Agent",
            description="Manages order fulfillment, inventory, and delivery coordination"
        )
    
    def get_system_prompt(self) -> str:
        warehouses = self._get_warehouse_context()
        
        return f"""You are an expert logistics and order fulfillment AI agent.

You execute a multi-step workflow to process orders:
1. RECEIVE ORDER - Validate and log the incoming order
2. CHECK INVENTORY - Verify stock across all warehouses  
3. ALLOCATE INVENTORY - Assign items from optimal warehouse locations
4. GENERATE PICK LIST - Create optimized picking routes for warehouse workers
5. SCHEDULE DELIVERY - Arrange shipping and provide tracking

WAREHOUSE NETWORK:
{warehouses}

When processing orders:
- Always verify stock before confirming
- Allocate from warehouses with highest stock first
- Optimize picking routes by zone
- Provide clear status updates at each step

Respond with a summary of each step taken and the final order status."""

    def _get_warehouse_context(self) -> str:
        lines = []
        for wh_id, wh in MockDataStore.WAREHOUSES.items():
            lines.append(f"\n**{wh['name']}** ({wh_id})")
            lines.append(f"Location: {wh['location']}")
            for sku, item in wh["inventory"].items():
                lines.append(f"  - {sku}: {item['name']} (Qty: {item['quantity']})")
        return "\n".join(lines)
    
    def _build_graph(self) -> StateGraph:
        """Build the multi-step fulfillment workflow."""
        
        async def receive_order(state: FulfillmentState) -> FulfillmentState:
            """Step 1: Receive and validate order."""
            state["workflow_steps"].append({
                "step": "receive",
                "status": "active",
                "label": "Receive Order"
            })
            
            # Parse order from message
            user_message = state["messages"][-1]["content"]
            
            # Extract items (simplified parsing)
            items = []
            if "oat milk" in user_message.lower():
                items.append({"sku": "SKU001", "name": "Organic Oat Milk 1L", "quantity": 100})
            if "tteokbokki" in user_message.lower() or "korean" in user_message.lower():
                items.append({"sku": "SKU002", "name": "Korean Rosé Tteokbokki", "quantity": 50})
            if "tea" in user_message.lower():
                items.append({"sku": "SKU003", "name": "Premium Green Tea", "quantity": 75})
            
            if not items:
                # Default demo order
                items = [{"sku": "SKU001", "name": "Organic Oat Milk 1L", "quantity": 100}]
            
            order_result = self.tools.receive_order(items)
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            
            state["order_id"] = order_result["order_id"]
            state["items"] = order_result["items"]
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = order_result
            
            return state
        
        async def check_inventory(state: FulfillmentState) -> FulfillmentState:
            """Step 2: Check inventory across warehouses."""
            state["workflow_steps"].append({
                "step": "check",
                "status": "active",
                "label": "Check Inventory"
            })
            
            inventory_results = []
            for item in state["items"]:
                result = self.tools.check_inventory(item["sku"])
                await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time per item
                result["item_name"] = item["name"]
                result["quantity_needed"] = item["quantity"]
                inventory_results.append(result)
            
            state["inventory_results"] = inventory_results
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {"items_checked": len(inventory_results)}
            
            return state
        
        async def allocate_inventory(state: FulfillmentState) -> FulfillmentState:
            """Step 3: Allocate inventory from warehouses."""
            state["workflow_steps"].append({
                "step": "allocate",
                "status": "active",
                "label": "Allocate Stock"
            })
            
            all_allocations = []
            for inv_result in state["inventory_results"]:
                allocation = self.tools.allocate_inventory(
                    inv_result["sku"],
                    inv_result["quantity_needed"],
                    inv_result.get("warehouses", [])
                )
                await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time per item
                allocation["item_name"] = inv_result["item_name"]
                all_allocations.append(allocation)
            
            state["allocations"] = all_allocations
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {"allocations": len(all_allocations)}
            
            return state
        
        async def generate_pick_list(state: FulfillmentState) -> FulfillmentState:
            """Step 4: Generate optimized pick list."""
            state["workflow_steps"].append({
                "step": "pick",
                "status": "active",
                "label": "Generate Pick List"
            })
            
            # Flatten allocations for pick list
            all_picks = []
            for alloc in state["allocations"]:
                for pick in alloc.get("allocations", []):
                    pick["sku"] = alloc["sku"]
                    all_picks.append(pick)
            
            pick_list = self.tools.generate_pick_list(all_picks)
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            
            state["pick_list"] = pick_list
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {"pick_list_id": pick_list["pick_list_id"]}
            
            return state
        
        async def schedule_delivery(state: FulfillmentState) -> FulfillmentState:
            """Step 5: Schedule delivery."""
            state["workflow_steps"].append({
                "step": "deliver",
                "status": "active",
                "label": "Schedule Delivery"
            })
            
            delivery = self.tools.schedule_delivery(
                state["order_id"],
                state["items"]
            )
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            
            state["delivery_info"] = delivery
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = delivery
            
            return state
        
        async def generate_response(state: FulfillmentState) -> FulfillmentState:
            """Generate final response summarizing the workflow."""
            
            response_parts = [
                f"## 📦 Order Fulfillment Complete\n",
                f"**Order ID:** {state['order_id']}\n",
                f"### Workflow Executed:\n"
            ]
            
            for step in state["workflow_steps"]:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} **{step['label']}**")
            
            response_parts.append(f"\n### Items Processed:")
            for item in state["items"]:
                response_parts.append(f"- {item['name']} x{item['quantity']}")
            
            response_parts.append(f"\n### Inventory Allocation:")
            for alloc in state["allocations"]:
                status = "✅ Allocated" if alloc["status"] == "success" else "⚠️ Partial"
                response_parts.append(f"- **{alloc.get('item_name', alloc['sku'])}**: {status}")
                for a in alloc.get("allocations", []):
                    response_parts.append(f"  - {a['warehouse_name']}: {a['quantity']} units (Zone {a['zone']})")
            
            if state["pick_list"]:
                response_parts.append(f"\n### Pick List: {state['pick_list']['pick_list_id']}")
                response_parts.append(f"- Estimated pick time: {state['pick_list']['estimated_pick_time']}")
            
            if state["delivery_info"]:
                response_parts.append(f"\n### Delivery Scheduled:")
                response_parts.append(f"- **Tracking:** {state['delivery_info']['tracking_number']}")
                response_parts.append(f"- **Carrier:** {state['delivery_info']['carrier']}")
                response_parts.append(f"- **Delivery Date:** {state['delivery_info']['delivery_date']}")
            
            state["result"] = "\n".join(response_parts)
            state["messages"].append({"role": "assistant", "content": state["result"]})
            
            return state
        
        async def handle_general_query(state: FulfillmentState) -> FulfillmentState:
            """Handle general queries about fulfillment."""
            response = await self.llm_service.chat(
                state["messages"],
                self.get_system_prompt()
            )
            state["result"] = response
            state["messages"].append({"role": "assistant", "content": response})
            return state
        
        def should_process_order(state: FulfillmentState) -> str:
            """Determine if this is an order to process or general query."""
            user_message = state["messages"][-1]["content"].lower()
            order_keywords = ["process", "order", "fulfill", "ship", "deliver", "units", "quantity"]
            
            if any(kw in user_message for kw in order_keywords):
                return "receive_order"
            return "general_query"
        
        # Build the graph
        workflow = StateGraph(FulfillmentState)
        
        # Add nodes
        workflow.add_node("router", lambda state: state)  # Pass-through router node
        workflow.add_node("receive_order", receive_order)
        workflow.add_node("check_inventory", check_inventory)
        workflow.add_node("allocate_inventory", allocate_inventory)
        workflow.add_node("generate_pick_list", generate_pick_list)
        workflow.add_node("schedule_delivery", schedule_delivery)
        workflow.add_node("generate_response", generate_response)
        workflow.add_node("general_query", handle_general_query)
        
        # Set entry point with conditional routing
        workflow.set_entry_point("router")
        workflow.add_conditional_edges(
            "router",
            should_process_order,
            {
                "receive_order": "receive_order",
                "general_query": "general_query"
            }
        )
        
        # Add edges for the workflow chain
        workflow.add_edge("receive_order", "check_inventory")
        workflow.add_edge("check_inventory", "allocate_inventory")
        workflow.add_edge("allocate_inventory", "generate_pick_list")
        workflow.add_edge("generate_pick_list", "schedule_delivery")
        workflow.add_edge("schedule_delivery", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("general_query", END)
        
        return workflow
    
    async def run(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the fulfillment workflow."""
        initial_state: FulfillmentState = {
            "messages": [{"role": "user", "content": user_input}],
            "context": context or {},
            "current_step": "start",
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
            "workflow_steps": final_state.get("workflow_steps", [])
        }
    
    async def run_with_streaming(self, user_input: str, context: Dict[str, Any] = None):
        """Run the fulfillment workflow with streaming step updates and human-in-the-loop."""
        
        user_message = user_input.lower()
        ctx = context or {}
        
        # Check if this is an approval response
        if ctx.get("approval_id"):
            async for event in self._continue_after_approval(ctx["approval_id"], ctx.get("approved", False)):
                yield event
            return
        
        order_keywords = ["process", "order", "fulfill", "ship", "deliver", "units", "quantity"]
        
        # Check if this is an order or general query
        if not any(kw in user_message for kw in order_keywords):
            # General query - just use LLM
            response = await self.llm_service.chat(
                [{"role": "user", "content": user_input}],
                self.get_system_prompt()
            )
            yield {"type": "response", "content": response}
            return
        
        # Process order with streaming steps
        workflow_steps = []
        
        # Step 1: Receive Order
        step1 = {"step": "receive", "status": "active", "label": "Receive Order"}
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        items = []
        if "oat milk" in user_message:
            items.append({"sku": "SKU001", "name": "Organic Oat Milk 1L", "quantity": 100})
        if "tteokbokki" in user_message or "korean" in user_message:
            items.append({"sku": "SKU002", "name": "Korean Rosé Tteokbokki", "quantity": 50})
        if "tea" in user_message:
            items.append({"sku": "SKU003", "name": "Premium Green Tea", "quantity": 75})
        if not items:
            items = [{"sku": "SKU001", "name": "Organic Oat Milk 1L", "quantity": 100}]
        
        order_result = self.tools.receive_order(items)
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = order_result
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 2: Check Inventory
        step2 = {"step": "check", "status": "active", "label": "Check Inventory"}
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        inventory_results = []
        for item in items:
            result = self.tools.check_inventory(item["sku"])
            await asyncio.sleep(STEP_DELAY)
            result["item_name"] = item["name"]
            result["quantity_needed"] = item["quantity"]
            inventory_results.append(result)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"items_checked": len(inventory_results)}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 3: Allocate Inventory
        step3 = {"step": "allocate", "status": "active", "label": "Allocate Stock"}
        workflow_steps.append(step3)
        yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
        
        allocations = []
        for inv_result in inventory_results:
            allocation = self.tools.allocate_inventory(
                inv_result["sku"],
                inv_result["quantity_needed"],
                inv_result.get("warehouses", [])
            )
            await asyncio.sleep(STEP_DELAY)
            allocation["item_name"] = inv_result["item_name"]
            allocations.append(allocation)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"allocations": len(allocations)}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 4: Human Approval Required 🧑‍💼
        step4 = {"step": "approval", "status": "active", "label": "Manager Approval"}
        workflow_steps.append(step4)
        yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
        
        # Generate approval ID and store state
        approval_id = str(uuid.uuid4())[:8]
        
        # Build approval summary
        total_items = sum(item["quantity"] for item in items)
        total_value = total_items * 15  # Simulated value
        
        approval_data = {
            "order_id": order_result["order_id"],
            "items": items,
            "allocations": allocations,
            "inventory_results": inventory_results,
            "total_items": total_items,
            "estimated_value": f"${total_value:,}",
            "workflow_steps": workflow_steps.copy()
        }
        
        # Store for later continuation
        PENDING_APPROVALS[approval_id] = approval_data
        
        # Yield approval required event - this pauses the workflow
        yield {
            "type": "approval_required",
            "approval_id": approval_id,
            "title": "Manager Approval Required",
            "message": f"Order {order_result['order_id']} requires manager approval before proceeding.",
            "details": {
                "order_id": order_result["order_id"],
                "total_items": total_items,
                "estimated_value": f"${total_value:,}",
                "items_summary": [f"{item['name']} x{item['quantity']}" for item in items],
                "warehouses_involved": list(set(
                    a.get("warehouse_name", "Unknown") 
                    for alloc in allocations 
                    for a in alloc.get("allocations", [])
                ))
            },
            "all_steps": workflow_steps.copy()
        }
    
    async def _continue_after_approval(self, approval_id: str, approved: bool):
        """Continue the workflow after human approval."""
        
        if approval_id not in PENDING_APPROVALS:
            yield {"type": "error", "content": f"Approval {approval_id} not found or expired."}
            return
        
        data = PENDING_APPROVALS.pop(approval_id)
        workflow_steps = data["workflow_steps"]
        
        if not approved:
            # Mark approval as rejected
            workflow_steps[-1]["status"] = "rejected"
            workflow_steps[-1]["result"] = {"decision": "rejected"}
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            yield {
                "type": "response", 
                "content": f"## ❌ Order Rejected\n\n**Order ID:** {data['order_id']}\n\nThe order was rejected by the manager and will not be processed."
            }
            return
        
        # Approval granted - continue workflow
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"decision": "approved", "approver": "Manager"}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        
        # Step 5: Generate Pick List
        step5 = {"step": "pick", "status": "active", "label": "Generate Pick List"}
        workflow_steps.append(step5)
        yield {"type": "workflow_step", "step": step5, "all_steps": workflow_steps.copy()}
        
        all_picks = []
        for alloc in data["allocations"]:
            for pick in alloc.get("allocations", []):
                pick["sku"] = alloc["sku"]
                all_picks.append(pick)
        
        pick_list = self.tools.generate_pick_list(all_picks)
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"pick_list_id": pick_list["pick_list_id"]}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 6: Schedule Delivery
        step6 = {"step": "deliver", "status": "active", "label": "Schedule Delivery"}
        workflow_steps.append(step6)
        yield {"type": "workflow_step", "step": step6, "all_steps": workflow_steps.copy()}
        
        delivery = self.tools.schedule_delivery(data["order_id"], data["items"])
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = delivery
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Generate response
        items = data["items"]
        allocations = data["allocations"]
        
        response_parts = [
            f"## 📦 Order Fulfillment Complete\n",
            f"**Order ID:** {data['order_id']}\n",
            f"### Workflow Executed:\n"
        ]
        
        for step in workflow_steps:
            if step["status"] == "complete":
                emoji = "✅"
            elif step["status"] == "rejected":
                emoji = "❌"
            else:
                emoji = "⏳"
            response_parts.append(f"{emoji} **{step['label']}**")
        
        response_parts.append(f"\n### Items Processed:")
        for item in items:
            response_parts.append(f"- {item['name']} x{item['quantity']}")
        
        response_parts.append(f"\n### Inventory Allocation:")
        for alloc in allocations:
            status = "✅ Allocated" if alloc["status"] == "success" else "⚠️ Partial"
            response_parts.append(f"- **{alloc.get('item_name', alloc['sku'])}**: {status}")
            for a in alloc.get("allocations", []):
                response_parts.append(f"  - {a['warehouse_name']}: {a['quantity']} units (Zone {a['zone']})")
        
        response_parts.append(f"\n### Pick List: {pick_list['pick_list_id']}")
        response_parts.append(f"- Estimated pick time: {pick_list['estimated_pick_time']}")
        
        response_parts.append(f"\n### Delivery Scheduled:")
        response_parts.append(f"- **Tracking:** {delivery['tracking_number']}")
        response_parts.append(f"- **Carrier:** {delivery['carrier']}")
        response_parts.append(f"- **Delivery Date:** {delivery['delivery_date']}")
        
        yield {"type": "response", "content": "\n".join(response_parts)}
