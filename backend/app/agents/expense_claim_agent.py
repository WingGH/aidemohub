"""Expense Claim Agent - Multi-Agent Chain with Dual Approval Workflow.

This agent implements a multi-agent chain for expense claim processing:
1. OCR Agent - Extracts receipt data from uploaded images
2. Validation Agent - Validates claim data and checks policies
3. Manager Agent - Boss approval checkpoint (Human-in-the-loop)
4. Finance Agent - Finance team approval checkpoint (Human-in-the-loop)
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
from app.data.mock_data import MockDataStore


# Store for pending approvals (in production, use a proper database)
EXPENSE_PENDING_APPROVALS = {}


class ExpenseClaimState(TypedDict):
    """State for expense claim workflow."""
    messages: List[Dict[str, str]]
    claim_id: str
    receipt_image: Optional[str]  # Base64 encoded image
    mime_type: Optional[str]  # Image mime type
    ocr_data: Dict[str, Any]  # Extracted receipt data
    validation_result: Dict[str, Any]
    manager_approval: Optional[Dict[str, Any]]
    finance_approval: Optional[Dict[str, Any]]
    current_step: str
    final_response: str
    agent_sequence: List[str]  # Track agent handoffs
    approval_stage: str  # 'manager' or 'finance'
    result: Optional[str]  # Final result for BaseAgent compatibility
    context: Dict[str, Any]  # Context for BaseAgent compatibility
    

class OCRAgent:
    """Agent responsible for extracting data from receipt images."""
    
    def __init__(self):
        self.llm_service = LLMService.get_instance()
        self.vision_service = VisionService()
    
    def get_system_prompt(self) -> str:
        return """You are an OCR specialist agent for expense claims. Your job is to:
1. Extract all relevant information from receipt images
2. Identify: merchant name, date, total amount, currency, items purchased, payment method
3. Categorize the expense type (meals, travel, office supplies, accommodation, etc.)
4. Note any potential issues (unclear amounts, missing info)

Be thorough and accurate. Format your findings clearly."""

    async def process(self, state: ExpenseClaimState) -> Dict[str, Any]:
        """Extract data from receipt image using vision AI."""
        image_base64 = state.get("receipt_image")
        
        if image_base64:
            # Use vision AI to analyze the receipt with JSON output
            prompt = f"""{self.get_system_prompt()}

Analyze this receipt image carefully and extract all information.

IMPORTANT: Return your response as a valid JSON object with these exact fields:
{{
    "merchant": "store or vendor name",
    "date": "date of purchase (YYYY-MM-DD format if possible)",
    "total_amount": 0.00,
    "currency": "USD/HKD/EUR/etc",
    "expense_type": "meals/travel/accommodation/office_supplies/entertainment",
    "items": [
        {{"description": "item name", "amount": 0.00}}
    ],
    "payment_method": "cash/card/etc",
    "receipt_number": "receipt or invoice number if visible"
}}

Be accurate with the total amount - look for words like "Total", "Amount Due", "Grand Total", "Total Fare".
For currency, look for symbols like $, HK$, €, £ or currency codes.
For taxi/transport receipts, the fare is the total amount.
Return ONLY the JSON object, no other text."""

            # Get mime type from state or detect from base64
            mime_type = state.get("mime_type", "image/jpeg")
            if not mime_type or mime_type == "application/octet-stream":
                # Fallback detection from base64 prefix
                if image_base64.startswith("/9j/"):
                    mime_type = "image/jpeg"
                elif image_base64.startswith("iVBORw"):
                    mime_type = "image/png"
                elif image_base64.startswith("R0lGOD"):
                    mime_type = "image/gif"
                else:
                    mime_type = "image/jpeg"
            
            print(f"[OCR] Calling vision API with mime_type: {mime_type}")
            print(f"[OCR] Image base64 length: {len(image_base64)}")
            
            analysis = await self.vision_service.analyze_image(
                image_base64,
                prompt,
                mime_type
            )
            
            print(f"[OCR] Vision API response: {analysis[:500]}...")
            
            # Parse the JSON response from GPT-4o
            ocr_data = self._parse_vision_response(analysis)
            print(f"[OCR] Parsed data: merchant={ocr_data.get('merchant')}, amount={ocr_data.get('total_amount')}, currency={ocr_data.get('currency')}")
            ocr_data["raw_analysis"] = analysis
            ocr_data["extracted_at"] = datetime.now().isoformat()
            ocr_data["confidence"] = "high"
            ocr_data["source"] = "vision_ai_gpt4o"
        else:
            # Demo mode - simulate OCR extraction
            ocr_data = self._simulate_ocr_extraction(state["messages"][-1]["content"])
        
        return {
            "ocr_data": ocr_data,
            "current_step": "validation",
            "agent_sequence": state.get("agent_sequence", []) + ["OCR Agent"]
        }
    
    def _parse_vision_response(self, response: str) -> Dict[str, Any]:
        """Parse the JSON response from GPT-4o vision model."""
        try:
            # Try to extract JSON from the response
            # First, try direct JSON parsing
            try:
                data = json.loads(response)
                return self._normalize_ocr_data(data)
            except json.JSONDecodeError:
                pass
            
            # Try to find JSON block in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return self._normalize_ocr_data(data)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Parse text response manually
            return self._parse_text_response(response)
            
        except Exception as e:
            print(f"Error parsing vision response: {e}")
            return self._get_default_ocr_data()
    
    def _normalize_ocr_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate OCR data fields."""
        # Ensure total_amount is a float
        total_amount = data.get("total_amount", 0)
        if isinstance(total_amount, str):
            # Remove currency symbols and parse
            total_amount = re.sub(r'[^\d.]', '', total_amount)
            try:
                total_amount = float(total_amount) if total_amount else 0
            except ValueError:
                total_amount = 0
        
        # Determine expense type if not provided
        expense_type = data.get("expense_type", "")
        merchant = str(data.get("merchant", "")).lower()
        if not expense_type:
            if any(word in merchant for word in ["taxi", "uber", "lyft", "airline", "transport"]):
                expense_type = "travel"
            elif any(word in merchant for word in ["hotel", "inn", "resort", "airbnb"]):
                expense_type = "accommodation"
            elif any(word in merchant for word in ["restaurant", "cafe", "food", "coffee"]):
                expense_type = "meals"
            else:
                expense_type = "office_supplies"
        
        return {
            "merchant": data.get("merchant", "Unknown Merchant"),
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "total_amount": total_amount,
            "currency": data.get("currency", "USD"),
            "expense_type": expense_type,
            "items": data.get("items", []),
            "payment_method": data.get("payment_method", "Unknown"),
            "receipt_number": data.get("receipt_number", f"REC-{uuid.uuid4().hex[:8].upper()}")
        }
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse a text response when JSON parsing fails."""
        data = self._get_default_ocr_data()
        
        # Try to extract merchant name (usually first line or after "Merchant:")
        merchant_match = re.search(r'[Mm]erchant[:\s]+([^\n,]+)', response)
        if merchant_match:
            data["merchant"] = merchant_match.group(1).strip()
        else:
            # Try first capitalized words
            first_line = response.split('\n')[0].strip()
            if first_line and len(first_line) < 100:
                data["merchant"] = first_line
        
        # Extract total amount - look for various patterns
        amount_patterns = [
            r'[Tt]otal[:\s]*\$?([\d,]+\.?\d*)',
            r'[Aa]mount[:\s]*\$?([\d,]+\.?\d*)',
            r'[Ff]are[:\s]*(?:HK)?\$?([\d,]+\.?\d*)',
            r'[Gg]rand [Tt]otal[:\s]*\$?([\d,]+\.?\d*)',
            r'\$\s*([\d,]+\.?\d*)'
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, response)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    data["total_amount"] = float(amount_str)
                    break
                except ValueError:
                    continue
        
        # Extract currency
        if 'HK$' in response or 'HKD' in response:
            data["currency"] = "HKD"
        elif '€' in response or 'EUR' in response:
            data["currency"] = "EUR"
        elif '£' in response or 'GBP' in response:
            data["currency"] = "GBP"
        else:
            data["currency"] = "USD"
        
        # Extract date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, response)
            if match:
                data["date"] = match.group(1)
                break
        
        # Determine expense type
        response_lower = response.lower()
        if any(word in response_lower for word in ["taxi", "uber", "fare", "transport"]):
            data["expense_type"] = "travel"
        elif any(word in response_lower for word in ["hotel", "accommodation"]):
            data["expense_type"] = "accommodation"
        elif any(word in response_lower for word in ["restaurant", "cafe", "food", "meal"]):
            data["expense_type"] = "meals"
        
        return data
    
    def _get_default_ocr_data(self) -> Dict[str, Any]:
        """Return default OCR data structure."""
        return {
            "merchant": "Unknown Merchant",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": 0,
            "currency": "USD",
            "expense_type": "office_supplies",
            "items": [],
            "payment_method": "Unknown",
            "receipt_number": f"REC-{uuid.uuid4().hex[:8].upper()}"
        }
    
    def _simulate_ocr_extraction(self, message: str) -> Dict[str, Any]:
        """Simulate OCR extraction for demo purposes."""
        # Parse any amounts mentioned in the message
        amounts = re.findall(r'\$?(\d+(?:\.\d{2})?)', message)
        amount = float(amounts[0]) if amounts else 125.50
        
        # Determine expense type from message
        expense_type = "meals"
        if any(word in message.lower() for word in ["flight", "travel", "taxi", "uber"]):
            expense_type = "travel"
        elif any(word in message.lower() for word in ["hotel", "accommodation"]):
            expense_type = "accommodation"
        elif any(word in message.lower() for word in ["office", "supplies", "equipment"]):
            expense_type = "office_supplies"
        
        return {
            "merchant": "Demo Merchant Ltd.",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": amount,
            "currency": "HKD",
            "expense_type": expense_type,
            "items": [
                {"description": "Business expense item", "amount": amount}
            ],
            "payment_method": "Corporate Card",
            "receipt_number": f"REC-{uuid.uuid4().hex[:8].upper()}",
            "extracted_at": datetime.now().isoformat(),
            "confidence": "simulated",
            "source": "demo_simulation"
        }


class ValidationAgent:
    """Agent responsible for validating expense claims against company policy."""
    
    def __init__(self):
        self.llm_service = LLMService.get_instance()
        
        # Company expense policies (in production, load from database)
        self.policies = {
            "meals": {"daily_limit": 500, "requires_receipt": True},
            "travel": {"daily_limit": 2000, "requires_receipt": True, "requires_pre_approval": False},
            "accommodation": {"daily_limit": 1500, "requires_receipt": True},
            "office_supplies": {"daily_limit": 1000, "requires_receipt": True},
            "entertainment": {"daily_limit": 800, "requires_receipt": True, "requires_manager_approval": True},
            "default": {"daily_limit": 500, "requires_receipt": True}
        }
    
    def get_system_prompt(self) -> str:
        return """You are a validation specialist agent for expense claims. Your job is to:
1. Verify expense claims against company policies
2. Check if amounts are within allowed limits
3. Identify any policy violations or concerns
4. Provide clear validation status and recommendations

Be fair but thorough in checking compliance."""

    async def process(self, state: ExpenseClaimState) -> Dict[str, Any]:
        """Validate the expense claim against company policies."""
        ocr_data = state.get("ocr_data", {})
        
        expense_type = ocr_data.get("expense_type", "default")
        policy = self.policies.get(expense_type, self.policies["default"])
        amount = ocr_data.get("total_amount", 0)
        
        # Check against policy limits
        is_within_limit = amount <= policy["daily_limit"]
        violations = []
        warnings = []
        
        if not is_within_limit:
            violations.append(f"Amount ${amount} exceeds daily limit of ${policy['daily_limit']} for {expense_type}")
        
        if amount > policy["daily_limit"] * 0.8:
            warnings.append(f"Amount is above 80% of daily limit for {expense_type}")
        
        # Determine approval routing
        requires_finance_only = amount <= 200 and is_within_limit
        
        validation_result = {
            "validated_at": datetime.now().isoformat(),
            "expense_type": expense_type,
            "amount": amount,
            "currency": ocr_data.get("currency", "HKD"),
            "policy_limit": policy["daily_limit"],
            "is_within_limit": is_within_limit,
            "violations": violations,
            "warnings": warnings,
            "requires_receipt": policy.get("requires_receipt", True),
            "approval_path": "finance_only" if requires_finance_only else "manager_then_finance",
            "validation_status": "passed" if not violations else "flagged"
        }
        
        # Generate LLM summary
        summary_prompt = f"""Based on this expense validation result, provide a brief summary:
- Amount: ${amount} {ocr_data.get('currency', 'HKD')}
- Type: {expense_type}
- Within limit: {is_within_limit}
- Violations: {violations if violations else 'None'}
- Warnings: {warnings if warnings else 'None'}

Summarize the validation status in 2-3 sentences."""

        messages = [{"role": "user", "content": summary_prompt}]
        summary = await self.llm_service.chat(messages, self.get_system_prompt())
        validation_result["llm_summary"] = summary
        
        return {
            "validation_result": validation_result,
            "current_step": "manager_approval" if not requires_finance_only else "finance_approval",
            "approval_stage": "finance" if requires_finance_only else "manager",
            "agent_sequence": state.get("agent_sequence", []) + ["Validation Agent"]
        }


class ManagerApprovalAgent:
    """Agent responsible for manager/boss approval checkpoint."""
    
    def get_system_prompt(self) -> str:
        return """You are a manager approval agent. Your job is to:
1. Review expense claims for appropriateness
2. Check if expenses align with business needs
3. Approve or request additional information
4. Provide clear reasoning for decisions"""

    async def process(self, state: ExpenseClaimState, approved: bool = None) -> Dict[str, Any]:
        """Process manager approval."""
        ocr_data = state.get("ocr_data", {})
        validation_result = state.get("validation_result", {})
        
        if approved is None:
            # Waiting for approval - return approval request
            return {
                "current_step": "awaiting_manager_approval",
                "manager_approval": {
                    "status": "pending",
                    "requested_at": datetime.now().isoformat(),
                    "claim_summary": {
                        "amount": ocr_data.get("total_amount", 0),
                        "currency": ocr_data.get("currency", "HKD"),
                        "type": ocr_data.get("expense_type", "unknown"),
                        "merchant": ocr_data.get("merchant", "Unknown"),
                        "date": ocr_data.get("date", "Unknown")
                    }
                },
                "agent_sequence": state.get("agent_sequence", []) + ["Manager Agent"]
            }
        
        # Process the approval decision
        return {
            "manager_approval": {
                "status": "approved" if approved else "rejected",
                "decided_at": datetime.now().isoformat(),
                "approved_by": "Department Manager"
            },
            "current_step": "finance_approval" if approved else "rejected",
            "approval_stage": "finance" if approved else "rejected",
            "agent_sequence": state.get("agent_sequence", []) + ["Manager Agent"]
        }


class FinanceApprovalAgent:
    """Agent responsible for finance team approval checkpoint."""
    
    def get_system_prompt(self) -> str:
        return """You are a finance approval agent. Your job is to:
1. Final review of expense claims
2. Verify budget allocation and cost center
3. Ensure proper documentation
4. Process payment upon approval"""

    async def process(self, state: ExpenseClaimState, approved: bool = None) -> Dict[str, Any]:
        """Process finance approval."""
        ocr_data = state.get("ocr_data", {})
        validation_result = state.get("validation_result", {})
        manager_approval = state.get("manager_approval", {})
        
        if approved is None:
            # Waiting for approval - return approval request
            return {
                "current_step": "awaiting_finance_approval",
                "finance_approval": {
                    "status": "pending",
                    "requested_at": datetime.now().isoformat(),
                    "claim_summary": {
                        "amount": ocr_data.get("total_amount", 0),
                        "currency": ocr_data.get("currency", "HKD"),
                        "type": ocr_data.get("expense_type", "unknown"),
                        "merchant": ocr_data.get("merchant", "Unknown"),
                        "manager_approved": manager_approval.get("status") == "approved" if manager_approval else "N/A"
                    }
                },
                "agent_sequence": state.get("agent_sequence", []) + ["Finance Agent"]
            }
        
        # Process the approval decision
        if approved:
            payment_ref = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            return {
                "finance_approval": {
                    "status": "approved",
                    "decided_at": datetime.now().isoformat(),
                    "approved_by": "Finance Team",
                    "payment_reference": payment_ref,
                    "payment_status": "scheduled"
                },
                "current_step": "complete",
                "agent_sequence": state.get("agent_sequence", []) + ["Finance Agent"]
            }
        else:
            return {
                "finance_approval": {
                    "status": "rejected",
                    "decided_at": datetime.now().isoformat(),
                    "rejected_by": "Finance Team"
                },
                "current_step": "rejected",
                "agent_sequence": state.get("agent_sequence", []) + ["Finance Agent"]
            }


class ExpenseClaimAgent(BaseAgent):
    """Multi-Agent Chain for Expense Claim Processing.
    
    Workflow:
    1. OCR Agent - Extract receipt data
    2. Validation Agent - Check against policies
    3. Manager Approval - Human-in-the-loop (if amount > $200)
    4. Finance Approval - Human-in-the-loop
    """
    
    def __init__(self):
        self.ocr_agent = OCRAgent()
        self.validation_agent = ValidationAgent()
        self.manager_agent = ManagerApprovalAgent()
        self.finance_agent = FinanceApprovalAgent()
        super().__init__(
            name="Expense Claim Agent",
            description="Multi-agent expense claim processing with dual approval workflow"
        )
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for expense claim processing."""
        workflow = StateGraph(ExpenseClaimState)
        
        # Define nodes
        async def ocr_node(state: ExpenseClaimState) -> Dict[str, Any]:
            result = await self.ocr_agent.process(state)
            return {**state, **result}
        
        async def validation_node(state: ExpenseClaimState) -> Dict[str, Any]:
            result = await self.validation_agent.process(state)
            return {**state, **result}
        
        async def respond_node(state: ExpenseClaimState) -> Dict[str, Any]:
            response = self._generate_initial_response(state)
            return {**state, "final_response": response, "result": response}
        
        # Add nodes
        workflow.add_node("ocr", ocr_node)
        workflow.add_node("validation", validation_node)
        workflow.add_node("respond", respond_node)
        
        # Add edges
        workflow.set_entry_point("ocr")
        workflow.add_edge("ocr", "validation")
        workflow.add_edge("validation", "respond")
        workflow.add_edge("respond", END)
        
        return workflow
    
    def get_system_prompt(self) -> str:
        return """You are an Expense Claim Processing System orchestrator. You coordinate multiple specialized agents:

1. **OCR Agent** - Extracts data from receipt images
2. **Validation Agent** - Checks claims against company policies  
3. **Manager Agent** - Handles boss approval for claims > $200
4. **Finance Agent** - Final approval and payment processing

Guide users through the expense claim process professionally and efficiently.
For demo purposes, users can describe their expense and optionally upload a receipt image.

Always explain what's happening at each step of the multi-agent workflow."""

    async def run(self, message: str, context: Dict[str, Any] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run the expense claim workflow."""
        context = context or {}
        
        # Check if this is an approval continuation
        if "approval_id" in context:
            return await self._continue_approval(context)
        
        # Initialize state
        claim_id = f"EXP-{uuid.uuid4().hex[:8].upper()}"
        state = ExpenseClaimState(
            messages=self._build_messages_with_history(message, conversation_history),
            claim_id=claim_id,
            receipt_image=context.get("image_base64"),
            mime_type=context.get("mime_type", "image/jpeg"),
            ocr_data={},
            validation_result={},
            manager_approval=None,
            finance_approval=None,
            current_step="ocr",
            final_response="",
            agent_sequence=[],
            approval_stage="",
            result=None,
            context=context
        )
        
        # Run the workflow
        result = await self._execute_workflow(state)
        return result
    
    async def run_with_streaming(self, message: str, context: Dict[str, Any] = None, conversation_history: List[Dict[str, str]] = None) -> AsyncIterator[Dict[str, Any]]:
        """Run expense claim workflow with streaming updates."""
        context = context or {}
        
        # Check if this is an approval continuation
        if "approval_id" in context:
            async for event in self._continue_approval_streaming(context):
                yield event
            return
        
        # Initialize workflow steps
        workflow_steps = [
            {"step": "ocr", "label": "Extract Receipt", "status": "pending", "agent_id": "ocr_agent", "agent_name": "OCR Agent"},
            {"step": "validation", "label": "Validate Claim", "status": "pending", "agent_id": "validation_agent", "agent_name": "Validation Agent"},
            {"step": "manager_approval", "label": "Manager Approval", "status": "pending", "agent_id": "manager_agent", "agent_name": "Manager"},
            {"step": "finance_approval", "label": "Finance Approval", "status": "pending", "agent_id": "finance_agent", "agent_name": "Finance"},
        ]
        
        # Helper to yield step updates in correct format
        def step_event(steps):
            return {
                "type": "workflow_step",
                "all_steps": steps,
                "step": steps[-1] if steps else {}
            }
        
        # Initial step update
        yield step_event(workflow_steps)
        
        # Initialize state
        claim_id = f"EXP-{uuid.uuid4().hex[:8].upper()}"
        state = ExpenseClaimState(
            messages=self._build_messages_with_history(message, conversation_history),
            claim_id=claim_id,
            receipt_image=context.get("image_base64"),
            mime_type=context.get("mime_type", "image/jpeg"),
            ocr_data={},
            validation_result={},
            manager_approval=None,
            finance_approval=None,
            current_step="ocr",
            final_response="",
            agent_sequence=[],
            approval_stage="",
            result=None,
            context=context
        )
        
        # Step 1: OCR Agent
        workflow_steps[0]["status"] = "active"
        yield step_event(workflow_steps)
        await asyncio.sleep(0.5)
        
        ocr_result = await self.ocr_agent.process(state)
        state.update(ocr_result)
        workflow_steps[0]["status"] = "complete"
        yield step_event(workflow_steps)
        
        # Step 2: Validation Agent
        workflow_steps[1]["status"] = "active"
        yield step_event(workflow_steps)
        await asyncio.sleep(0.5)
        
        validation_result = await self.validation_agent.process(state)
        state.update(validation_result)
        workflow_steps[1]["status"] = "complete"
        yield step_event(workflow_steps)
        
        # Determine approval path
        approval_path = state["validation_result"].get("approval_path", "manager_then_finance")
        
        if approval_path == "manager_then_finance":
            # Step 3: Manager Approval
            workflow_steps[2]["status"] = "active"
            yield step_event(workflow_steps)
            
            manager_result = await self.manager_agent.process(state)
            state.update(manager_result)
            
            # Store pending approval for human-in-the-loop
            approval_id = f"MGR-{uuid.uuid4().hex[:8]}"
            EXPENSE_PENDING_APPROVALS[approval_id] = {
                "state": state,
                "stage": "manager",
                "workflow_steps": workflow_steps
            }
            
            # Request human approval
            yield {
                "type": "approval_required",
                "approval_id": approval_id,
                "title": "🧑‍💼 Manager Approval Required",
                "message": f"Please review this expense claim for approval.",
                "details": {
                    "claim_id": state["claim_id"],
                    "amount": f"${state['ocr_data'].get('total_amount', 0)} {state['ocr_data'].get('currency', 'HKD')}",
                    "type": state['ocr_data'].get('expense_type', 'Unknown'),
                    "merchant": state['ocr_data'].get('merchant', 'Unknown'),
                    "date": state['ocr_data'].get('date', 'Unknown'),
                    "validation_status": state['validation_result'].get('validation_status', 'unknown')
                },
                "all_steps": workflow_steps
            }
            return
        else:
            # Skip manager approval for small amounts
            workflow_steps[2]["status"] = "complete"
            workflow_steps[2]["label"] = "Manager (Skipped)"
            yield step_event(workflow_steps)
        
        # Step 4: Finance Approval
        workflow_steps[3]["status"] = "active"
        yield step_event(workflow_steps)
        
        finance_result = await self.finance_agent.process(state)
        state.update(finance_result)
        
        # Store pending approval for human-in-the-loop
        approval_id = f"FIN-{uuid.uuid4().hex[:8]}"
        EXPENSE_PENDING_APPROVALS[approval_id] = {
            "state": state,
            "stage": "finance",
            "workflow_steps": workflow_steps
        }
        
        # Request human approval
        yield {
            "type": "approval_required",
            "approval_id": approval_id,
            "title": "💰 Finance Approval Required",
            "message": f"Please review this expense claim for final approval and payment processing.",
            "details": {
                "claim_id": state["claim_id"],
                "amount": f"${state['ocr_data'].get('total_amount', 0)} {state['ocr_data'].get('currency', 'HKD')}",
                "type": state['ocr_data'].get('expense_type', 'Unknown'),
                "merchant": state['ocr_data'].get('merchant', 'Unknown'),
                "manager_status": state['manager_approval'].get('status', 'N/A') if state.get('manager_approval') else "Skipped"
            },
            "all_steps": workflow_steps
        }
    
    async def _continue_approval_streaming(self, context: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Continue workflow after approval decision."""
        approval_id = context.get("approval_id")
        approved = context.get("approved", False)
        
        if approval_id not in EXPENSE_PENDING_APPROVALS:
            yield {
                "type": "response",
                "content": "❌ Approval session expired or not found. Please start a new expense claim."
            }
            return
        
        pending = EXPENSE_PENDING_APPROVALS.pop(approval_id)
        state = pending["state"]
        stage = pending["stage"]
        workflow_steps = pending["workflow_steps"]
        
        if stage == "manager":
            # Process manager decision
            if approved:
                workflow_steps[2]["status"] = "complete"
                yield {"type": "workflow_step", "all_steps": workflow_steps, "step": workflow_steps[2]}
                
                # Update state with manager approval
                state["manager_approval"] = {
                    "status": "approved",
                    "decided_at": datetime.now().isoformat(),
                    "approved_by": "Department Manager"
                }
                
                # Move to finance approval
                workflow_steps[3]["status"] = "active"
                yield {"type": "workflow_step", "all_steps": workflow_steps, "step": workflow_steps[3]}
                
                finance_result = await self.finance_agent.process(state)
                state.update(finance_result)
                
                # Store for finance approval
                finance_approval_id = f"FIN-{uuid.uuid4().hex[:8]}"
                EXPENSE_PENDING_APPROVALS[finance_approval_id] = {
                    "state": state,
                    "stage": "finance",
                    "workflow_steps": workflow_steps
                }
                
                yield {
                    "type": "approval_required",
                    "approval_id": finance_approval_id,
                    "title": "💰 Finance Approval Required",
                    "message": "Manager approved. Please review for final finance approval.",
                    "details": {
                        "claim_id": state["claim_id"],
                        "amount": f"${state['ocr_data'].get('total_amount', 0)} {state['ocr_data'].get('currency', 'HKD')}",
                        "type": state['ocr_data'].get('expense_type', 'Unknown'),
                        "manager_status": "✅ Approved"
                    },
                    "all_steps": workflow_steps
                }
            else:
                # Manager rejected
                workflow_steps[2]["status"] = "rejected"
                workflow_steps[3]["status"] = "rejected"
                yield {"type": "workflow_step", "all_steps": workflow_steps, "step": workflow_steps[2]}
                
                response = self._generate_rejection_response(state, "manager")
                yield {"type": "response", "content": response}
        
        elif stage == "finance":
            # Process finance decision
            if approved:
                workflow_steps[3]["status"] = "complete"
                yield {"type": "workflow_step", "all_steps": workflow_steps, "step": workflow_steps[3]}
                
                # Generate payment reference
                payment_ref = f"PAY-{uuid.uuid4().hex[:8].upper()}"
                state["finance_approval"] = {
                    "status": "approved",
                    "decided_at": datetime.now().isoformat(),
                    "approved_by": "Finance Team",
                    "payment_reference": payment_ref
                }
                
                response = self._generate_approval_response(state, payment_ref)
                yield {"type": "response", "content": response}
            else:
                # Finance rejected
                workflow_steps[3]["status"] = "rejected"
                yield {"type": "workflow_step", "all_steps": workflow_steps, "step": workflow_steps[3]}
                
                response = self._generate_rejection_response(state, "finance")
                yield {"type": "response", "content": response}
    
    async def _execute_workflow(self, state: ExpenseClaimState) -> Dict[str, Any]:
        """Execute the full workflow synchronously."""
        # OCR
        ocr_result = await self.ocr_agent.process(state)
        state.update(ocr_result)
        
        # Validation
        validation_result = await self.validation_agent.process(state)
        state.update(validation_result)
        
        # For non-streaming, just return the state for approval
        return {
            "response": self._generate_initial_response(state),
            "context": {
                "claim_id": state["claim_id"],
                "ocr_data": state["ocr_data"],
                "validation_result": state["validation_result"]
            }
        }
    
    async def _continue_approval(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Continue workflow after approval (non-streaming)."""
        # Simplified for non-streaming mode
        return {
            "response": "Please use the streaming endpoint for full approval workflow.",
            "context": context
        }
    
    def _generate_initial_response(self, state: ExpenseClaimState) -> str:
        """Generate response after initial processing."""
        ocr_data = state.get("ocr_data", {})
        validation = state.get("validation_result", {})
        
        return f"""## 📋 Expense Claim Submitted

**Claim ID:** {state['claim_id']}

### Receipt Details (Extracted)
- **Merchant:** {ocr_data.get('merchant', 'Unknown')}
- **Date:** {ocr_data.get('date', 'Unknown')}
- **Amount:** ${ocr_data.get('total_amount', 0)} {ocr_data.get('currency', 'HKD')}
- **Type:** {ocr_data.get('expense_type', 'Unknown')}

### Validation Status
- **Status:** {validation.get('validation_status', 'Pending').upper()}
- **Policy Limit:** ${validation.get('policy_limit', 'N/A')}
- **Within Limit:** {'✅ Yes' if validation.get('is_within_limit') else '❌ No'}

### Agent Workflow
{' → '.join(state.get('agent_sequence', []))}

*Awaiting approval...*"""

    def _generate_approval_response(self, state: ExpenseClaimState, payment_ref: str) -> str:
        """Generate response after full approval."""
        ocr_data = state.get("ocr_data", {})
        
        return f"""## ✅ Expense Claim Approved!

**Claim ID:** {state['claim_id']}
**Payment Reference:** {payment_ref}

### Claim Summary
- **Amount:** ${ocr_data.get('total_amount', 0)} {ocr_data.get('currency', 'HKD')}
- **Merchant:** {ocr_data.get('merchant', 'Unknown')}
- **Type:** {ocr_data.get('expense_type', 'Unknown').replace('_', ' ').title()}

### Approval Chain
1. 🔍 **OCR Agent** - Receipt data extracted
2. ✅ **Validation Agent** - Policy check passed
3. ✅ **Manager** - Approved
4. ✅ **Finance** - Approved & payment scheduled

### Payment Status
💳 Payment has been scheduled for processing. Expect reimbursement within 3-5 business days.

---
*Multi-agent workflow completed successfully!*"""

    def _generate_rejection_response(self, state: ExpenseClaimState, rejected_by: str) -> str:
        """Generate response after rejection."""
        ocr_data = state.get("ocr_data", {})
        
        return f"""## ❌ Expense Claim Rejected

**Claim ID:** {state['claim_id']}

### Claim Summary
- **Amount:** ${ocr_data.get('total_amount', 0)} {ocr_data.get('currency', 'HKD')}
- **Merchant:** {ocr_data.get('merchant', 'Unknown')}
- **Type:** {ocr_data.get('expense_type', 'Unknown').replace('_', ' ').title()}

### Rejection Details
- **Rejected By:** {rejected_by.title()}
- **Stage:** {'Manager Approval' if rejected_by == 'manager' else 'Finance Approval'}

### Next Steps
1. Review the claim details and ensure all documentation is complete
2. Contact {rejected_by.title()} for specific feedback
3. Submit a new claim with corrections if applicable

---
*Please contact finance@company.com for questions.*"""

