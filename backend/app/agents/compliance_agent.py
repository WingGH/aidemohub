"""Compliance Copilot Agent - Healthcare regulatory compliance."""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.data.mock_data import MockDataStore
from app.services.vision_service import VisionService
import asyncio

# Delay between workflow steps
STEP_DELAY = 1.0


class ComplianceAgent(BaseAgent):
    """Agent for healthcare distribution compliance analysis."""
    
    def __init__(self):
        super().__init__(
            name="Compliance Copilot",
            description="Analyzes regulatory documents and identifies compliance gaps"
        )
        self.vision_service = VisionService.get_instance()
    
    def get_system_prompt(self) -> str:
        sops = self._get_sop_context()
        return f"""You are an expert healthcare regulatory compliance AI assistant.

Your capabilities include:
- Analyzing new regulatory documents from health authorities
- Comparing regulations against internal Standard Operating Procedures (SOPs)
- Identifying compliance gaps and required updates
- Prioritizing compliance actions by risk level
- Generating compliance action items

Current Internal SOPs:
{sops}

When analyzing a new regulation:
1. Summarize the key requirements
2. Compare against each relevant SOP
3. Identify specific gaps or conflicts
4. Recommend action items with priority levels
5. Estimate implementation timeline

Risk Levels:
- CRITICAL: Immediate action required, potential legal/safety issues
- HIGH: Action needed within 30 days
- MEDIUM: Action needed within 90 days
- LOW: Improvement opportunity, no immediate risk

Always be thorough and err on the side of caution for healthcare compliance."""

    def _get_sop_context(self) -> str:
        """Get current SOPs as context."""
        lines = []
        for sop_id, sop in MockDataStore.COMPLIANCE_SOPS.items():
            lines.append(f"\n{sop_id}: {sop['title']} (v{sop['version']})")
            for section in sop['sections']:
                lines.append(f"  - {section}")
        return "\n".join(lines)
    
    async def analyze_regulation(self, document_text: str = None, image_base64: str = None) -> Dict[str, Any]:
        """Analyze a regulatory document for compliance gaps."""
        if image_base64:
            # Extract text from document image first
            extraction_prompt = """Extract all text from this regulatory/compliance document. 
            Preserve the structure including headers, sections, and bullet points.
            This appears to be a healthcare or pharmaceutical regulation document."""
            
            document_text = await self.vision_service.analyze_image(image_base64, extraction_prompt)
        
        analysis_prompt = f"""Analyze this new regulatory document and compare it against our current SOPs:

NEW REGULATION:
{document_text}

CURRENT SOPs:
{self._get_sop_context()}

Provide a compliance gap analysis with:
1. **Summary of New Requirements**: Key points from the new regulation
2. **Affected SOPs**: Which internal procedures need updating
3. **Gap Analysis**: Specific items that are non-compliant or need changes
4. **Action Items**: Prioritized list of required changes
5. **Risk Assessment**: Overall compliance risk if not addressed

Format each action item as:
[PRIORITY] Description - Affected SOP - Deadline"""

        response = await self.llm_service.generate(analysis_prompt, self.get_system_prompt())
        
        return {
            "analysis": response,
            "sops_reviewed": list(MockDataStore.COMPLIANCE_SOPS.keys()),
            "status": "analyzed"
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the compliance analysis workflow."""
        
        async def process_compliance(state: AgentState) -> AgentState:
            """Process compliance inquiry or document."""
            if state["context"].get("image_base64"):
                result = await self.analyze_regulation(
                    image_base64=state["context"]["image_base64"]
                )
                state["result"] = result["analysis"]
            elif state["context"].get("document_text"):
                result = await self.analyze_regulation(
                    document_text=state["context"]["document_text"]
                )
                state["result"] = result["analysis"]
            else:
                response = await self.llm_service.chat(
                    state["messages"],
                    self.get_system_prompt()
                )
                state["result"] = response
            
            state["messages"].append({"role": "assistant", "content": state["result"]})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("process", process_compliance)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        
        return workflow
    
    async def run_with_streaming(self, user_input: str, context: Dict[str, Any] = None):
        """Run compliance analysis with streaming step updates."""
        ctx = context or {}
        workflow_steps = []
        has_document = ctx.get("image_base64") or ctx.get("document_text")
        
        if not has_document:
            # General query - still show workflow steps
            # Step 1: Receive Query
            step1 = {"step": "receive", "status": "active", "label": "Receive Doc"}
            workflow_steps.append(step1)
            yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
            
            await asyncio.sleep(STEP_DELAY)
            workflow_steps[-1]["status"] = "complete"
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Step 2: Extract Rules (analyzing query)
            step2 = {"step": "extract", "status": "active", "label": "Extract Rules"}
            workflow_steps.append(step2)
            yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
            
            await asyncio.sleep(STEP_DELAY)
            workflow_steps[-1]["status"] = "complete"
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Step 3: Compare SOPs
            step3 = {"step": "compare", "status": "active", "label": "Compare SOPs"}
            workflow_steps.append(step3)
            yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
            
            # Generate response
            response = await self.llm_service.chat(
                [{"role": "user", "content": user_input}],
                self.get_system_prompt()
            )
            
            await asyncio.sleep(STEP_DELAY)
            workflow_steps[-1]["status"] = "complete"
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Step 4: Find Gaps
            step4 = {"step": "gaps", "status": "active", "label": "Find Gaps"}
            workflow_steps.append(step4)
            yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
            
            await asyncio.sleep(STEP_DELAY)
            workflow_steps[-1]["status"] = "complete"
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            # Step 5: Generate Report
            step5 = {"step": "report", "status": "active", "label": "Report"}
            workflow_steps.append(step5)
            yield {"type": "workflow_step", "step": step5, "all_steps": workflow_steps.copy()}
            
            await asyncio.sleep(STEP_DELAY)
            workflow_steps[-1]["status"] = "complete"
            yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
            
            yield {"type": "response", "content": response}
            return
        
        # Step 1: Receive Document
        step1 = {"step": "receive", "status": "active", "label": "Receive Doc"}
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 2: Extract Rules
        step2 = {"step": "extract", "status": "active", "label": "Extract Rules"}
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        document_text = ctx.get("document_text")
        if ctx.get("image_base64"):
            extraction_prompt = "Extract all text from this regulatory/compliance document."
            document_text = await self.vision_service.analyze_image(ctx["image_base64"], extraction_prompt)
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 3: Compare SOPs
        step3 = {"step": "compare", "status": "active", "label": "Compare SOPs"}
        workflow_steps.append(step3)
        yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 4: Find Gaps
        step4 = {"step": "gaps", "status": "active", "label": "Find Gaps"}
        workflow_steps.append(step4)
        yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
        
        result = await self.analyze_regulation(document_text=document_text)
        await asyncio.sleep(STEP_DELAY)
        
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 5: Generate Report
        step5 = {"step": "report", "status": "active", "label": "Report"}
        workflow_steps.append(step5)
        yield {"type": "workflow_step", "step": step5, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        yield {"type": "response", "content": result["analysis"]}

