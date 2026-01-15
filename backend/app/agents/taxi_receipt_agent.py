"""HK Taxi Receipt Agent - Specialized for Hong Kong Taxi Receipt Claims.

This agent is specifically designed to process Hong Kong taxi receipts with:
1. OCR Agent - Extracts taxi receipt data (TAXI NO, fare, km, timestamps)
2. Validation Agent - Validates against taxi expense policies
3. Approval Agent - Supervisor approval checkpoint (Human-in-the-loop)
"""

from typing import Dict, Any, List, AsyncIterator, TypedDict, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime
import uuid
import asyncio
import json
import re

from .base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.services.vision_service import VisionService


# Store for pending approvals
TAXI_PENDING_APPROVALS = {}


class TaxiReceiptState(TypedDict):
    """State for taxi receipt claim workflow."""
    messages: List[Dict[str, str]]
    claim_id: str
    receipt_image: Optional[str]
    mime_type: Optional[str]
    taxi_data: Dict[str, Any]
    validation_result: Dict[str, Any]
    approval: Optional[Dict[str, Any]]
    current_step: str
    final_response: str
    agent_sequence: List[str]
    result: Optional[str]
    context: Dict[str, Any]


class TaxiOCRAgent:
    """Agent specialized for extracting data from HK taxi receipts."""
    
    def __init__(self):
        self.llm_service = LLMService.get_instance()
        self.vision_service = VisionService()
    
    def get_system_prompt(self) -> str:
        return """You are a specialized OCR agent for Hong Kong taxi receipts.

Hong Kong taxi receipts typically contain:
- 車号 (TAXI NO.) - The taxi registration number
- 上車 (START) - Start date and time
- 下車 (END) - End date and time  
- 总公里 (TOTAL KM) - Total kilometers
- 收费公里 (PAID KM) - Paid kilometers
- 收费分钟 (PAID MIN) - Paid minutes (waiting time)
- 附加費/附加费 (SURCHARGE) - Any surcharges
- 总车费/总車費 (TOTAL FARE) - Total fare in HK$

Extract all visible information accurately. The fare is usually shown as "HK$XX.XX"."""

    async def process(self, state: TaxiReceiptState) -> Dict[str, Any]:
        """Extract data from taxi receipt image using GPT-4o vision."""
        image_base64 = state.get("receipt_image")
        
        if image_base64:
            prompt = f"""{self.get_system_prompt()}

Analyze this Hong Kong taxi receipt image and extract all information.

IMPORTANT: Return your response as a valid JSON object with these exact fields:
{{
    "taxi_number": "the taxi registration number (車号/TAXI NO.)",
    "start_datetime": "start date and time (上車/START) in format YYYY-MM-DD HH:MM",
    "end_datetime": "end date and time (下車/END) in format YYYY-MM-DD HH:MM",
    "total_km": 0.00,
    "paid_km": 0.00,
    "paid_minutes": 0.00,
    "surcharge": 0.00,
    "total_fare": 0.00,
    "currency": "HKD"
}}

Look carefully for:
- TOTAL FARE or 总车费 - this is the main amount to claim
- Any surcharges (附加費/SURCHARGE)
- The taxi number (車号/TAXI NO.)

Return ONLY the JSON object, no other text."""

            mime_type = state.get("mime_type", "image/jpeg")
            if not mime_type or mime_type == "application/octet-stream":
                if image_base64.startswith("/9j/"):
                    mime_type = "image/jpeg"
                elif image_base64.startswith("iVBORw"):
                    mime_type = "image/png"
                else:
                    mime_type = "image/jpeg"
            
            print(f"[TaxiOCR] Calling vision API with mime_type: {mime_type}")
            print(f"[TaxiOCR] Image base64 length: {len(image_base64)}")
            
            analysis = await self.vision_service.analyze_image(
                image_base64,
                prompt,
                mime_type
            )
            
            print(f"[TaxiOCR] Vision API response: {analysis[:500]}...")
            
            taxi_data = self._parse_taxi_response(analysis)
            print(f"[TaxiOCR] Parsed: taxi={taxi_data.get('taxi_number')}, fare={taxi_data.get('total_fare')} {taxi_data.get('currency')}")
            
            taxi_data["raw_analysis"] = analysis
            taxi_data["extracted_at"] = datetime.now().isoformat()
            taxi_data["source"] = "vision_ai_gpt4o"
        else:
            taxi_data = self._simulate_taxi_extraction(state["messages"][-1]["content"])
        
        return {
            "taxi_data": taxi_data,
            "current_step": "validation",
            "agent_sequence": state.get("agent_sequence", []) + ["Taxi OCR Agent"]
        }
    
    def _parse_taxi_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from GPT-4o for taxi receipt."""
        try:
            # Try direct JSON parsing
            try:
                data = json.loads(response)
                return self._normalize_taxi_data(data)
            except json.JSONDecodeError:
                pass
            
            # Try to find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return self._normalize_taxi_data(data)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: manual parsing
            return self._parse_taxi_text(response)
            
        except Exception as e:
            print(f"[TaxiOCR] Error parsing response: {e}")
            return self._get_default_taxi_data()
    
    def _normalize_taxi_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate taxi data fields."""
        def parse_number(val, default=0.0):
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str):
                cleaned = re.sub(r'[^\d.]', '', val)
                try:
                    return float(cleaned) if cleaned else default
                except ValueError:
                    return default
            return default
        
        return {
            "taxi_number": str(data.get("taxi_number", data.get("taxi_no", "Unknown"))),
            "start_datetime": data.get("start_datetime", data.get("start", "Unknown")),
            "end_datetime": data.get("end_datetime", data.get("end", "Unknown")),
            "total_km": parse_number(data.get("total_km", 0)),
            "paid_km": parse_number(data.get("paid_km", 0)),
            "paid_minutes": parse_number(data.get("paid_minutes", data.get("paid_min", 0))),
            "surcharge": parse_number(data.get("surcharge", 0)),
            "total_fare": parse_number(data.get("total_fare", 0)),
            "currency": data.get("currency", "HKD")
        }
    
    def _parse_taxi_text(self, response: str) -> Dict[str, Any]:
        """Parse text response when JSON fails."""
        data = self._get_default_taxi_data()
        
        # Extract taxi number
        taxi_match = re.search(r'TAXI\s*NO\.?\s*[:\s]*([A-Z]?\d+)', response, re.IGNORECASE)
        if taxi_match:
            data["taxi_number"] = taxi_match.group(1)
        
        # Extract total fare - look for HK$ pattern
        fare_patterns = [
            r'TOTAL\s*FARE[:\s]*HK?\$?\s*([\d.]+)',
            r'总车费[:\s]*HK?\$?\s*([\d.]+)',
            r'HK\$\s*([\d.]+)',
            r'\$([\d.]+)'
        ]
        for pattern in fare_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    data["total_fare"] = float(match.group(1))
                    break
                except ValueError:
                    continue
        
        # Extract surcharge
        surcharge_match = re.search(r'SURCHARGE[:\s]*HK?\$?\s*([\d.]+)', response, re.IGNORECASE)
        if surcharge_match:
            try:
                data["surcharge"] = float(surcharge_match.group(1))
            except ValueError:
                pass
        
        # Extract KM
        km_match = re.search(r'TOTAL\s*KM[:\s]*([\d.]+)', response, re.IGNORECASE)
        if km_match:
            try:
                data["total_km"] = float(km_match.group(1))
            except ValueError:
                pass
        
        # Extract dates
        date_match = re.search(r'START[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})', response, re.IGNORECASE)
        if date_match:
            data["start_datetime"] = date_match.group(1)
        
        return data
    
    def _get_default_taxi_data(self) -> Dict[str, Any]:
        """Return default taxi data structure."""
        return {
            "taxi_number": "Unknown",
            "start_datetime": "Unknown",
            "end_datetime": "Unknown",
            "total_km": 0.0,
            "paid_km": 0.0,
            "paid_minutes": 0.0,
            "surcharge": 0.0,
            "total_fare": 0.0,
            "currency": "HKD"
        }
    
    def _simulate_taxi_extraction(self, message: str) -> Dict[str, Any]:
        """Simulate taxi receipt extraction for demo."""
        amounts = re.findall(r'\$?(\d+(?:\.\d{2})?)', message)
        amount = float(amounts[0]) if amounts else 58.10
        
        return {
            "taxi_number": f"M{uuid.uuid4().hex[:4].upper()}",
            "start_datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "end_datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_km": round(amount / 20, 2),  # Rough estimate
            "paid_km": round(amount / 20, 2),
            "paid_minutes": 0.0,
            "surcharge": 0.0,
            "total_fare": amount,
            "currency": "HKD",
            "extracted_at": datetime.now().isoformat(),
            "source": "demo_simulation"
        }


class TaxiValidationAgent:
    """Agent for validating taxi expense claims."""
    
    def __init__(self):
        self.llm_service = LLMService.get_instance()
        # Taxi expense policies
        self.policies = {
            "max_single_trip": 500,  # HKD per trip
            "daily_limit": 1000,     # HKD per day
            "requires_receipt": True,
            "auto_approve_under": 100  # Auto-approve claims under HK$100
        }
    
    def get_system_prompt(self) -> str:
        return """You are a validation agent for taxi expense claims. Your job is to:
1. Verify taxi expenses against company policies
2. Check if fare amounts are reasonable for the distance
3. Flag any suspicious patterns
4. Provide clear validation status"""

    async def process(self, state: TaxiReceiptState) -> Dict[str, Any]:
        """Validate taxi claim against policies."""
        taxi_data = state.get("taxi_data", {})
        fare = taxi_data.get("total_fare", 0)
        
        # Validation checks
        is_within_limit = fare <= self.policies["max_single_trip"]
        can_auto_approve = fare <= self.policies["auto_approve_under"]
        
        violations = []
        warnings = []
        
        if not is_within_limit:
            violations.append(f"Fare HK${fare} exceeds single trip limit of HK${self.policies['max_single_trip']}")
        
        # Check if fare is reasonable for distance (rough HK taxi rate: ~$24 flag fall + $1.9/km)
        total_km = taxi_data.get("total_km", 0)
        if total_km > 0:
            expected_min = 24 + (total_km * 1.5)  # Minimum expected
            expected_max = 24 + (total_km * 3) + 50  # Max with surcharges
            if fare < expected_min * 0.5:
                warnings.append(f"Fare seems unusually low for {total_km}km")
            elif fare > expected_max:
                warnings.append(f"Fare seems high for {total_km}km - please verify")
        
        validation_result = {
            "validated_at": datetime.now().isoformat(),
            "fare_amount": fare,
            "currency": taxi_data.get("currency", "HKD"),
            "trip_km": total_km,
            "policy_limit": self.policies["max_single_trip"],
            "is_within_limit": is_within_limit,
            "can_auto_approve": can_auto_approve,
            "violations": violations,
            "warnings": warnings,
            "validation_status": "passed" if not violations else "flagged"
        }
        
        return {
            "validation_result": validation_result,
            "current_step": "approval",
            "agent_sequence": state.get("agent_sequence", []) + ["Validation Agent"]
        }


class TaxiApprovalAgent:
    """Agent for handling taxi claim approvals."""
    
    def get_system_prompt(self) -> str:
        return """You are an approval agent for taxi expenses. Review claims and approve or reject based on policy compliance."""

    async def process(self, state: TaxiReceiptState, approved: bool = None) -> Dict[str, Any]:
        """Process approval decision."""
        taxi_data = state.get("taxi_data", {})
        validation = state.get("validation_result", {})
        
        if approved is None:
            return {
                "current_step": "awaiting_approval",
                "approval": {
                    "status": "pending",
                    "requested_at": datetime.now().isoformat(),
                    "claim_summary": {
                        "taxi_number": taxi_data.get("taxi_number", "Unknown"),
                        "fare": taxi_data.get("total_fare", 0),
                        "currency": taxi_data.get("currency", "HKD"),
                        "distance": taxi_data.get("total_km", 0),
                        "date": taxi_data.get("start_datetime", "Unknown")
                    }
                },
                "agent_sequence": state.get("agent_sequence", []) + ["Approval Agent"]
            }
        
        if approved:
            payment_ref = f"TAXI-{uuid.uuid4().hex[:8].upper()}"
            return {
                "approval": {
                    "status": "approved",
                    "decided_at": datetime.now().isoformat(),
                    "approved_by": "Supervisor",
                    "payment_reference": payment_ref
                },
                "current_step": "complete",
                "agent_sequence": state.get("agent_sequence", []) + ["Approval Agent"]
            }
        else:
            return {
                "approval": {
                    "status": "rejected",
                    "decided_at": datetime.now().isoformat(),
                    "rejected_by": "Supervisor"
                },
                "current_step": "rejected",
                "agent_sequence": state.get("agent_sequence", []) + ["Approval Agent"]
            }


class TaxiReceiptAgent(BaseAgent):
    """Specialized Agent for Hong Kong Taxi Receipt Claims.
    
    Workflow:
    1. Taxi OCR Agent - Extract HK taxi receipt data
    2. Validation Agent - Check against taxi policies
    3. Approval Agent - Supervisor approval (Human-in-the-loop)
    """
    
    def __init__(self):
        self.ocr_agent = TaxiOCRAgent()
        self.validation_agent = TaxiValidationAgent()
        self.approval_agent = TaxiApprovalAgent()
        super().__init__(
            name="HK Taxi Receipt Agent",
            description="Specialized agent for Hong Kong taxi receipt claims"
        )
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(TaxiReceiptState)
        
        async def ocr_node(state: TaxiReceiptState) -> Dict[str, Any]:
            result = await self.ocr_agent.process(state)
            return {**state, **result}
        
        async def validation_node(state: TaxiReceiptState) -> Dict[str, Any]:
            result = await self.validation_agent.process(state)
            return {**state, **result}
        
        async def respond_node(state: TaxiReceiptState) -> Dict[str, Any]:
            response = self._generate_initial_response(state)
            return {**state, "final_response": response, "result": response}
        
        workflow.add_node("ocr", ocr_node)
        workflow.add_node("validation", validation_node)
        workflow.add_node("respond", respond_node)
        
        workflow.set_entry_point("ocr")
        workflow.add_edge("ocr", "validation")
        workflow.add_edge("validation", "respond")
        workflow.add_edge("respond", END)
        
        return workflow
    
    def get_system_prompt(self) -> str:
        return """You are a Hong Kong Taxi Receipt Claim Processing System.

You specialize in processing Hong Kong taxi receipts which contain:
- 車号 (TAXI NO.) - Taxi registration number
- 总车费 (TOTAL FARE) - The fare amount in HK$
- Trip details (distance, time, surcharges)

Guide users through submitting their taxi receipts for reimbursement.
The workflow: OCR extraction → Policy validation → Supervisor approval → Payment."""

    async def run(self, message: str, context: Dict[str, Any] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run the taxi receipt workflow."""
        context = context or {}
        
        if "approval_id" in context:
            return await self._continue_approval(context)
        
        claim_id = f"TAXI-{uuid.uuid4().hex[:8].upper()}"
        state = TaxiReceiptState(
            messages=self._build_messages_with_history(message, conversation_history),
            claim_id=claim_id,
            receipt_image=context.get("image_base64"),
            mime_type=context.get("mime_type", "image/jpeg"),
            taxi_data={},
            validation_result={},
            approval=None,
            current_step="ocr",
            final_response="",
            agent_sequence=[],
            result=None,
            context=context
        )
        
        result = await self._execute_workflow(state)
        return result
    
    async def run_with_streaming(self, message: str, context: Dict[str, Any] = None, conversation_history: List[Dict[str, str]] = None) -> AsyncIterator[Dict[str, Any]]:
        """Run taxi receipt workflow with streaming updates."""
        context = context or {}
        
        if "approval_id" in context:
            async for event in self._continue_approval_streaming(context):
                yield event
            return
        
        workflow_steps = [
            {"step": "ocr", "label": "Scan Receipt", "status": "pending", "agent_id": "taxi_ocr", "agent_name": "Taxi OCR"},
            {"step": "validation", "label": "Validate Fare", "status": "pending", "agent_id": "validation", "agent_name": "Validator"},
            {"step": "approval", "label": "Approval", "status": "pending", "agent_id": "approval", "agent_name": "Supervisor"},
        ]
        
        def step_event(steps):
            return {"type": "workflow_step", "all_steps": steps, "step": steps[-1] if steps else {}}
        
        yield step_event(workflow_steps)
        
        claim_id = f"TAXI-{uuid.uuid4().hex[:8].upper()}"
        state = TaxiReceiptState(
            messages=self._build_messages_with_history(message, conversation_history),
            claim_id=claim_id,
            receipt_image=context.get("image_base64"),
            mime_type=context.get("mime_type", "image/jpeg"),
            taxi_data={},
            validation_result={},
            approval=None,
            current_step="ocr",
            final_response="",
            agent_sequence=[],
            result=None,
            context=context
        )
        
        # Step 1: OCR
        workflow_steps[0]["status"] = "active"
        yield step_event(workflow_steps)
        await asyncio.sleep(0.5)
        
        ocr_result = await self.ocr_agent.process(state)
        state.update(ocr_result)
        workflow_steps[0]["status"] = "complete"
        yield step_event(workflow_steps)
        
        # Step 2: Validation
        workflow_steps[1]["status"] = "active"
        yield step_event(workflow_steps)
        await asyncio.sleep(0.3)
        
        validation_result = await self.validation_agent.process(state)
        state.update(validation_result)
        workflow_steps[1]["status"] = "complete"
        yield step_event(workflow_steps)
        
        # Check if can auto-approve
        can_auto = state["validation_result"].get("can_auto_approve", False)
        
        if can_auto and not state["validation_result"].get("violations"):
            # Auto-approve small claims
            workflow_steps[2]["status"] = "complete"
            workflow_steps[2]["label"] = "Auto-Approved"
            yield step_event(workflow_steps)
            
            payment_ref = f"TAXI-{uuid.uuid4().hex[:8].upper()}"
            state["approval"] = {
                "status": "approved",
                "decided_at": datetime.now().isoformat(),
                "approved_by": "Auto-Approval System",
                "payment_reference": payment_ref
            }
            
            response = self._generate_approval_response(state, payment_ref)
            yield {"type": "response", "content": response}
        else:
            # Require manual approval
            workflow_steps[2]["status"] = "active"
            yield step_event(workflow_steps)
            
            approval_result = await self.approval_agent.process(state)
            state.update(approval_result)
            
            approval_id = f"TAXI-{uuid.uuid4().hex[:8]}"
            TAXI_PENDING_APPROVALS[approval_id] = {
                "state": state,
                "workflow_steps": workflow_steps
            }
            
            yield {
                "type": "approval_required",
                "approval_id": approval_id,
                "title": "🚕 Taxi Claim Approval Required",
                "message": "Please review this taxi expense claim for approval.",
                "details": {
                    "claim_id": state["claim_id"],
                    "taxi_number": state["taxi_data"].get("taxi_number", "Unknown"),
                    "fare": f"HK${state['taxi_data'].get('total_fare', 0):.2f}",
                    "distance": f"{state['taxi_data'].get('total_km', 0):.2f} km",
                    "date": state["taxi_data"].get("start_datetime", "Unknown"),
                    "validation": state["validation_result"].get("validation_status", "unknown")
                },
                "all_steps": workflow_steps
            }
    
    async def _continue_approval_streaming(self, context: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Continue workflow after approval decision."""
        approval_id = context.get("approval_id")
        approved = context.get("approved", False)
        
        if approval_id not in TAXI_PENDING_APPROVALS:
            yield {"type": "response", "content": "❌ Approval session expired. Please submit a new taxi claim."}
            return
        
        pending = TAXI_PENDING_APPROVALS.pop(approval_id)
        state = pending["state"]
        workflow_steps = pending["workflow_steps"]
        
        if approved:
            workflow_steps[2]["status"] = "complete"
            yield {"type": "workflow_step", "all_steps": workflow_steps, "step": workflow_steps[2]}
            
            payment_ref = f"TAXI-{uuid.uuid4().hex[:8].upper()}"
            state["approval"] = {
                "status": "approved",
                "decided_at": datetime.now().isoformat(),
                "approved_by": "Supervisor",
                "payment_reference": payment_ref
            }
            
            response = self._generate_approval_response(state, payment_ref)
            yield {"type": "response", "content": response}
        else:
            workflow_steps[2]["status"] = "rejected"
            yield {"type": "workflow_step", "all_steps": workflow_steps, "step": workflow_steps[2]}
            
            response = self._generate_rejection_response(state)
            yield {"type": "response", "content": response}
    
    async def _execute_workflow(self, state: TaxiReceiptState) -> Dict[str, Any]:
        """Execute workflow synchronously."""
        ocr_result = await self.ocr_agent.process(state)
        state.update(ocr_result)
        
        validation_result = await self.validation_agent.process(state)
        state.update(validation_result)
        
        return {
            "response": self._generate_initial_response(state),
            "context": {
                "claim_id": state["claim_id"],
                "taxi_data": state["taxi_data"],
                "validation_result": state["validation_result"]
            }
        }
    
    async def _continue_approval(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Continue workflow after approval (non-streaming)."""
        return {"response": "Please use the streaming endpoint for the approval workflow.", "context": context}
    
    def _generate_initial_response(self, state: TaxiReceiptState) -> str:
        """Generate response after initial processing."""
        taxi = state.get("taxi_data", {})
        validation = state.get("validation_result", {})
        
        return f"""## 🚕 Taxi Receipt Claim Submitted

**Claim ID:** {state['claim_id']}

### Receipt Details
| Field | Value |
|-------|-------|
| Taxi No. | {taxi.get('taxi_number', 'Unknown')} |
| Date | {taxi.get('start_datetime', 'Unknown')} |
| Distance | {taxi.get('total_km', 0):.2f} km |
| Fare | HK${taxi.get('total_fare', 0):.2f} |
| Surcharge | HK${taxi.get('surcharge', 0):.2f} |

### Validation Status
- **Status:** {validation.get('validation_status', 'Pending').upper()}
- **Policy Limit:** HK${validation.get('policy_limit', 500)}
- **Within Limit:** {'✅ Yes' if validation.get('is_within_limit') else '❌ No'}

### Agent Workflow
{' → '.join(state.get('agent_sequence', []))}

*Awaiting approval...*"""

    def _generate_approval_response(self, state: TaxiReceiptState, payment_ref: str) -> str:
        """Generate response after approval."""
        taxi = state.get("taxi_data", {})
        
        return f"""## ✅ Taxi Claim Approved!

**Claim ID:** {state['claim_id']}
**Payment Reference:** {payment_ref}

### Claim Summary
| Field | Value |
|-------|-------|
| Taxi No. | {taxi.get('taxi_number', 'Unknown')} |
| Fare | HK${taxi.get('total_fare', 0):.2f} |
| Distance | {taxi.get('total_km', 0):.2f} km |
| Date | {taxi.get('start_datetime', 'Unknown')} |

### Approval Chain
1. 🔍 **Taxi OCR** - Receipt scanned
2. ✅ **Validation** - Policy check passed
3. ✅ **Approval** - Approved by {state.get('approval', {}).get('approved_by', 'Supervisor')}

### Payment Status
💳 Reimbursement scheduled for processing. Expect payment within 3-5 business days.

---
*Taxi claim workflow completed!* 🎉"""

    def _generate_rejection_response(self, state: TaxiReceiptState) -> str:
        """Generate response after rejection."""
        taxi = state.get("taxi_data", {})
        
        return f"""## ❌ Taxi Claim Rejected

**Claim ID:** {state['claim_id']}

### Claim Summary
| Field | Value |
|-------|-------|
| Taxi No. | {taxi.get('taxi_number', 'Unknown')} |
| Fare | HK${taxi.get('total_fare', 0):.2f} |
| Distance | {taxi.get('total_km', 0):.2f} km |

### Next Steps
1. Review the claim details
2. Contact your supervisor for feedback
3. Submit a new claim with corrections if needed

---
*Please contact finance@company.com for questions.*"""

