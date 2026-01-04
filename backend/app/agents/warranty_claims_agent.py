"""Warranty Claims Agent - Real multi-step workflow with fraud detection."""
from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent
from app.services.vision_service import VisionService
from app.data.mock_data import MockDataStore
from app.tools.warranty_tools import WarrantyTools
import asyncio

# Delay between workflow steps to simulate real processing
STEP_DELAY = 1.0  # seconds


class WarrantyState(TypedDict):
    """State for warranty claims workflow."""
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    current_step: str
    claim_id: Optional[str]
    serial_number: Optional[str]
    receipt_data: Optional[Dict[str, Any]]
    warranty_info: Optional[Dict[str, Any]]
    fraud_check: Optional[Dict[str, Any]]
    decision: Optional[Dict[str, Any]]
    workflow_steps: List[Dict[str, Any]]
    result: Optional[str]


class WarrantyClaimsAgent(BaseAgent):
    """Agent for processing warranty claims with real multi-step workflow."""
    
    def __init__(self):
        self.tools = WarrantyTools()
        self.vision_service = VisionService.get_instance()
        super().__init__(
            name="Warranty Claims Processor",
            description="Processes warranty claims with OCR and fraud detection"
        )
    
    def get_system_prompt(self) -> str:
        return """You are an expert warranty claims processing AI agent.

You execute a multi-step workflow to process claims:
1. RECEIVE CLAIM - Log the incoming claim with customer and product details
2. EXTRACT DATA - Use OCR to extract receipt/document information
3. VERIFY WARRANTY - Check if product is under warranty
4. FRAUD CHECK - Analyze for fraud indicators
5. MAKE DECISION - Approve, reject, or escalate the claim

When processing claims:
- Always verify the serial number against our database
- Check for previous claims on the same serial number
- Look for fraud indicators like altered documents
- Provide clear explanations for decisions

Known serial numbers in our system:
- SN-12345678: Smart Air Purifier (Valid warranty until 2026-06-15)
- SN-87654321: Robot Vacuum (Valid until 2025-12-01, has 1 previous claim)
- SN-11111111: Electric Kettle (Warranty EXPIRED 2024-01-10)"""

    def _build_graph(self) -> StateGraph:
        """Build the warranty claims workflow."""
        
        async def receive_claim(state: WarrantyState) -> WarrantyState:
            """Step 1: Receive and log the claim."""
            state["workflow_steps"].append({
                "step": "receive",
                "status": "active",
                "label": "Receive Claim"
            })
            
            user_message = state["messages"][-1]["content"]
            
            # Extract serial number from message
            serial_number = None
            import re
            sn_match = re.search(r'SN-\d+', user_message, re.IGNORECASE)
            if sn_match:
                serial_number = sn_match.group().upper()
            elif "12345678" in user_message:
                serial_number = "SN-12345678"
            elif "87654321" in user_message:
                serial_number = "SN-87654321"
            elif "11111111" in user_message:
                serial_number = "SN-11111111"
            
            state["serial_number"] = serial_number or "SN-12345678"
            
            claim_result = self.tools.receive_claim(
                serial_number=state["serial_number"],
                customer_name="Valued Customer",
                issue_description=user_message
            )
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            
            state["claim_id"] = claim_result["claim_id"]
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {"claim_id": claim_result["claim_id"]}
            
            return state
        
        async def extract_data(state: WarrantyState) -> WarrantyState:
            """Step 2: Extract receipt data."""
            state["workflow_steps"].append({
                "step": "extract",
                "status": "active",
                "label": "Extract Data"
            })
            
            # Check for image in context
            if state["context"].get("image_base64"):
                # Use vision to extract
                extraction_prompt = "Extract all information from this receipt: store name, date, product, price, serial number."
                extracted_text = await self.vision_service.analyze_image(
                    state["context"]["image_base64"],
                    extraction_prompt
                )
                state["receipt_data"] = {"raw_text": extracted_text, "source": "ocr"}
            else:
                # Simulate extraction
                result = self.tools.extract_receipt_data("Simulated receipt")
                await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
                state["receipt_data"] = result["extracted_data"]
            
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {"fields_extracted": 6}
            
            return state
        
        async def verify_warranty(state: WarrantyState) -> WarrantyState:
            """Step 3: Verify warranty status."""
            state["workflow_steps"].append({
                "step": "verify",
                "status": "active",
                "label": "Verify Warranty"
            })
            
            result = self.tools.verify_warranty(state["serial_number"])
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            
            state["warranty_info"] = result
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "valid": result["warranty_valid"],
                "product": result.get("product")
            }
            
            return state
        
        async def check_fraud(state: WarrantyState) -> WarrantyState:
            """Step 4: Check for fraud indicators."""
            state["workflow_steps"].append({
                "step": "fraud",
                "status": "active",
                "label": "Fraud Check"
            })
            
            warranty_info = state["warranty_info"] or {}
            
            result = self.tools.check_fraud_indicators(
                serial_number=state["serial_number"],
                claim_history=warranty_info.get("previous_claims", 0),
                purchase_date=warranty_info.get("purchase_date")
            )
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            
            state["fraud_check"] = result
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "risk_level": result["risk_level"],
                "flags": len(result["fraud_flags"])
            }
            
            return state
        
        async def make_decision(state: WarrantyState) -> WarrantyState:
            """Step 5: Make final decision."""
            state["workflow_steps"].append({
                "step": "decide",
                "status": "active",
                "label": "Decision"
            })
            
            warranty_info = state["warranty_info"] or {}
            fraud_check = state["fraud_check"] or {}
            
            result = self.tools.make_decision(
                claim_id=state["claim_id"],
                warranty_valid=warranty_info.get("warranty_valid", False),
                fraud_risk=fraud_check.get("risk_level", "low"),
                issue_description=state["messages"][-1]["content"]
            )
            await asyncio.sleep(STEP_DELAY)  # Simulate tool execution time
            
            state["decision"] = result
            state["workflow_steps"][-1]["status"] = "complete"
            state["workflow_steps"][-1]["result"] = {
                "decision": result["decision"]
            }
            
            return state
        
        async def generate_response(state: WarrantyState) -> WarrantyState:
            """Generate final response."""
            
            response_parts = [
                "## 🛡️ Warranty Claim Processing Complete\n",
                f"**Claim ID:** {state['claim_id']}",
                f"**Serial Number:** {state['serial_number']}\n",
                "### Workflow Executed:"
            ]
            
            for step in state["workflow_steps"]:
                emoji = "✅" if step["status"] == "complete" else "⏳"
                response_parts.append(f"{emoji} **{step['label']}**")
            
            # Warranty verification
            if state["warranty_info"]:
                wi = state["warranty_info"]
                response_parts.append(f"\n### Warranty Verification:")
                response_parts.append(f"- **Product:** {wi.get('product', 'Unknown')}")
                response_parts.append(f"- **Valid:** {'✅ Yes' if wi.get('warranty_valid') else '❌ No'}")
                if wi.get("purchase_date"):
                    response_parts.append(f"- **Purchase Date:** {wi['purchase_date']}")
                if wi.get("warranty_end"):
                    response_parts.append(f"- **Warranty Ends:** {wi['warranty_end']}")
                response_parts.append(f"- **Previous Claims:** {wi.get('previous_claims', 0)}")
            
            # Fraud check
            if state["fraud_check"]:
                fc = state["fraud_check"]
                risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(fc["risk_level"], "⚪")
                response_parts.append(f"\n### Fraud Analysis:")
                response_parts.append(f"- **Risk Level:** {risk_emoji} {fc['risk_level'].upper()}")
                response_parts.append(f"- **Risk Score:** {fc['risk_score']}/100")
                if fc["fraud_flags"]:
                    response_parts.append("- **Flags Detected:**")
                    for flag in fc["fraud_flags"]:
                        response_parts.append(f"  - ⚠️ {flag['indicator']}: {flag['details']}")
            
            # Decision
            if state["decision"]:
                d = state["decision"]
                decision_emoji = {
                    "approved": "✅",
                    "approved_with_review": "✅",
                    "rejected": "❌",
                    "review_required": "⚠️"
                }.get(d["decision"], "❓")
                
                response_parts.append(f"\n### Final Decision: {decision_emoji} **{d['decision'].upper().replace('_', ' ')}**")
                response_parts.append(f"- **Reason:** {d['reason']}")
                response_parts.append(f"- **Action:** {d['action']}")
                response_parts.append(f"- **Reference:** {d['reference_number']}")
            
            state["result"] = "\n".join(response_parts)
            state["messages"].append({"role": "assistant", "content": state["result"]})
            
            return state
        
        async def handle_general_query(state: WarrantyState) -> WarrantyState:
            """Handle general queries."""
            response = await self.llm_service.chat(
                state["messages"],
                self.get_system_prompt()
            )
            state["result"] = response
            state["messages"].append({"role": "assistant", "content": response})
            return state
        
        def should_process_claim(state: WarrantyState) -> str:
            """Determine if this is a claim to process."""
            user_message = state["messages"][-1]["content"].lower()
            claim_keywords = ["claim", "warranty", "serial", "sn-", "process", "broken", "defect", "return"]
            
            if any(kw in user_message for kw in claim_keywords):
                return "receive"
            return "general"
        
        # Build graph
        workflow = StateGraph(WarrantyState)
        
        workflow.add_node("router", lambda state: state)  # Pass-through router node
        workflow.add_node("receive", receive_claim)
        workflow.add_node("extract", extract_data)
        workflow.add_node("verify", verify_warranty)
        workflow.add_node("fraud", check_fraud)
        workflow.add_node("decide", make_decision)
        workflow.add_node("respond", generate_response)
        workflow.add_node("general", handle_general_query)
        
        workflow.set_entry_point("router")
        workflow.add_conditional_edges(
            "router",
            should_process_claim,
            {
                "receive": "receive",
                "general": "general"
            }
        )
        
        workflow.add_edge("receive", "extract")
        workflow.add_edge("extract", "verify")
        workflow.add_edge("verify", "fraud")
        workflow.add_edge("fraud", "decide")
        workflow.add_edge("decide", "respond")
        workflow.add_edge("respond", END)
        workflow.add_edge("general", END)
        
        return workflow
    
    async def run(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Run the warranty claims workflow."""
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        initial_state: WarrantyState = {
            "messages": messages,
            "context": context or {},
            "current_step": "start",
            "claim_id": None,
            "serial_number": None,
            "receipt_data": None,
            "warranty_info": None,
            "fraud_check": None,
            "decision": None,
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
    
    async def run_with_streaming(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ):
        """Run the warranty claims workflow with streaming step updates."""
        import re
        
        user_message = user_input.lower()
        claim_keywords = ["claim", "warranty", "serial", "sn-", "process", "broken", "defect", "return"]
        
        # Build full messages list for LLM calls
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        # Check if this is a claim or general query
        if not any(kw in user_message for kw in claim_keywords):
            response = await self.llm_service.chat(
                messages,
                self.get_system_prompt()
            )
            yield {"type": "response", "content": response}
            return
        
        workflow_steps = []
        ctx = context or {}
        
        # Extract serial number
        sn_match = re.search(r'SN-\d+', user_input, re.IGNORECASE)
        if sn_match:
            serial_number = sn_match.group().upper()
        elif "12345678" in user_input:
            serial_number = "SN-12345678"
        elif "87654321" in user_input:
            serial_number = "SN-87654321"
        elif "11111111" in user_input:
            serial_number = "SN-11111111"
        else:
            serial_number = "SN-12345678"
        
        # Step 1: Receive Claim
        step1 = {"step": "receive", "status": "active", "label": "Receive Claim"}
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        claim_result = self.tools.receive_claim(serial_number, "Valued Customer", user_input)
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"claim_id": claim_result["claim_id"]}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 2: Extract Data
        step2 = {"step": "extract", "status": "active", "label": "Extract Data"}
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        if ctx.get("image_base64"):
            extracted_text = await self.vision_service.analyze_image(
                ctx["image_base64"],
                "Extract all information from this receipt."
            )
            receipt_data = {"raw_text": extracted_text, "source": "ocr"}
        else:
            result = self.tools.extract_receipt_data("Simulated receipt")
            await asyncio.sleep(STEP_DELAY)
            receipt_data = result["extracted_data"]
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"fields_extracted": 6}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 3: Verify Warranty
        step3 = {"step": "verify", "status": "active", "label": "Verify Warranty"}
        workflow_steps.append(step3)
        yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
        
        warranty_info = self.tools.verify_warranty(serial_number)
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"valid": warranty_info["warranty_valid"]}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 4: Fraud Check
        step4 = {"step": "fraud", "status": "active", "label": "Fraud Check"}
        workflow_steps.append(step4)
        yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
        
        fraud_check = self.tools.check_fraud_indicators(
            serial_number,
            warranty_info.get("previous_claims", 0),
            warranty_info.get("purchase_date")
        )
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"risk_level": fraud_check["risk_level"]}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 5: Make Decision
        step5 = {"step": "decide", "status": "active", "label": "Decision"}
        workflow_steps.append(step5)
        yield {"type": "workflow_step", "step": step5, "all_steps": workflow_steps.copy()}
        
        decision = self.tools.make_decision(
            claim_result["claim_id"],
            warranty_info.get("warranty_valid", False),
            fraud_check.get("risk_level", "low"),
            user_input
        )
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"decision": decision["decision"]}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Generate response
        response_parts = [
            f"## 🛡️ Warranty Claim Processed\n",
            f"**Claim ID:** {claim_result['claim_id']}\n",
            f"**Serial Number:** {serial_number}\n"
        ]
        
        response_parts.append("### Workflow Executed:")
        for step in workflow_steps:
            emoji = "✅" if step["status"] == "complete" else "⏳"
            response_parts.append(f"{emoji} **{step['label']}**")
        
        response_parts.append(f"\n### Warranty Status:")
        if warranty_info["warranty_valid"]:
            response_parts.append(f"✅ Product under warranty until {warranty_info.get('warranty_end')}")
        else:
            response_parts.append(f"❌ Warranty expired on {warranty_info.get('warranty_end')}")
        
        response_parts.append(f"\n### Fraud Analysis:")
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(fraud_check["risk_level"], "⚪")
        response_parts.append(f"- **Risk Level:** {risk_emoji} {fraud_check['risk_level'].upper()}")
        
        decision_emoji = {"approved": "✅", "rejected": "❌", "escalated": "⚠️"}.get(decision["decision"], "❓")
        response_parts.append(f"\n### Final Decision: {decision_emoji} **{decision['decision'].upper()}**")
        response_parts.append(f"- **Reason:** {decision['reason']}")
        response_parts.append(f"- **Action:** {decision['action']}")
        response_parts.append(f"- **Reference:** {decision['reference_number']}")
        
        yield {"type": "response", "content": "\n".join(response_parts)}
