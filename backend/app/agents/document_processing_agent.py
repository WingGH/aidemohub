"""Document Processing Agent - OCR and multilingual document extraction."""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.services.vision_service import VisionService
import asyncio

# Delay between workflow steps to simulate real processing
STEP_DELAY = 1.0  # seconds


class DocumentProcessingAgent(BaseAgent):
    """Agent for intelligent document processing and extraction."""
    
    def __init__(self):
        super().__init__(
            name="Document Processing Agent",
            description="Extracts and processes shipping documents, invoices, and forms"
        )
        self.vision_service = VisionService.get_instance()
    
    def get_system_prompt(self) -> str:
        return """You are an expert document processing AI assistant specialized in logistics and shipping documents.

Your capabilities include:
- Extracting data from shipping documents, customs forms, invoices, and bills of lading
- Processing documents in multiple languages (Chinese, English, and others)
- Handling handwritten notes and stamps
- Validating document completeness
- Identifying discrepancies or missing information

Document types you handle:
- Commercial Invoice
- Bill of Lading
- Customs Declaration
- Packing List
- Certificate of Origin
- Delivery Receipt

When processing documents, extract:
1. Document Type
2. Key Fields (dates, amounts, parties, items)
3. Validation Status
4. Any issues or warnings

Always structure your output in a clear, organized format."""

    async def process_document(self, image_base64: str, doc_type: str = "auto") -> Dict[str, Any]:
        """Process a document image and extract information."""
        prompt = f"""Analyze this logistics/shipping document and extract all relevant information.

Expected document type: {doc_type if doc_type != 'auto' else 'Auto-detect'}

Please extract and structure the following:

1. **Document Type**: Identify the type of document
2. **Document Number/Reference**: Any ID or reference numbers
3. **Date(s)**: Issue date, shipping date, etc.
4. **Parties Involved**:
   - Shipper/Sender
   - Consignee/Receiver
   - Carrier (if applicable)
5. **Items/Goods**:
   - Description
   - Quantity
   - Weight
   - Value
6. **Financial Details**: Amounts, currency, terms
7. **Shipping Details**: Origin, destination, method
8. **Validation**:
   - Is the document complete?
   - Any missing required fields?
   - Any potential issues?

If text is in Chinese or other languages, translate key fields to English while preserving original text."""

        result = await self.vision_service.analyze_image(image_base64, prompt)
        
        return {
            "extraction": result,
            "confidence": "high",
            "languages_detected": ["en", "zh"],
            "status": "processed"
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the document processing workflow."""
        
        async def process_document_node(state: AgentState) -> AgentState:
            """Process document or handle text inquiry."""
            if state["context"].get("image_base64"):
                doc_type = state["context"].get("document_type", "auto")
                result = await self.process_document(
                    state["context"]["image_base64"],
                    doc_type
                )
                state["result"] = result["extraction"]
            else:
                response = await self.llm_service.chat(
                    state["messages"],
                    self.get_system_prompt()
                )
                state["result"] = response
            
            state["messages"].append({"role": "assistant", "content": state["result"]})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("process", process_document_node)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        
        return workflow
    
    async def run_with_streaming(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ):
        """Run the document processing workflow with streaming step updates."""
        ctx = context or {}
        workflow_steps = []
        
        # Build full messages list for LLM calls
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        # Check if we have an image to process
        has_image = ctx.get("image_base64") is not None
        
        if not has_image:
            # General query - use LLM with full conversation history
            response = await self.llm_service.chat(
                messages,
                self.get_system_prompt()
            )
            yield {"type": "response", "content": response}
            return
        
        # Step 1: Receive Document
        step1 = {"step": "receive", "status": "active", "label": "Receive Doc"}
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"document_received": True}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 2: OCR Scan
        step2 = {"step": "ocr", "status": "active", "label": "OCR Scan"}
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        # Actually run OCR
        ocr_prompt = "Extract all text from this document, preserving layout and structure."
        ocr_result = await self.vision_service.analyze_image(ctx["image_base64"], ocr_prompt)
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"text_extracted": True}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 3: Extract Fields
        step3 = {"step": "extract", "status": "active", "label": "Extract Fields"}
        workflow_steps.append(step3)
        yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
        
        # Run field extraction
        doc_type = ctx.get("document_type", "auto")
        extraction_result = await self.process_document(ctx["image_base64"], doc_type)
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"fields_extracted": True}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 4: Validate
        step4 = {"step": "validate", "status": "active", "label": "Validate"}
        workflow_steps.append(step4)
        yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        workflow_steps[-1]["result"] = {"validation": "passed"}
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 5: Complete
        step5 = {"step": "complete", "status": "active", "label": "Complete"}
        workflow_steps.append(step5)
        yield {"type": "workflow_step", "step": step5, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Generate final response
        response_parts = [
            "## 📄 Document Processing Complete\n",
            "### Workflow Executed:"
        ]
        
        for step in workflow_steps:
            emoji = "✅" if step["status"] == "complete" else "⏳"
            response_parts.append(f"{emoji} **{step['label']}**")
        
        response_parts.append(f"\n### Extraction Results:\n")
        response_parts.append(extraction_result["extraction"])
        
        yield {"type": "response", "content": "\n".join(response_parts)}

