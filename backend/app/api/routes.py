"""API routes for AI Hub."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import base64
import json

from app.agents import (
    AutomotiveSalesAgent,
    DamageAssessmentAgent,
    DocumentProcessingAgent,
    MarketingContentAgent,
    ComplianceAgent,
    SalesTrainerAgent,
    TrendSpotterAgent,
    WarrantyClaimsAgent,
    CrossSellingAgent,
    OrderFulfillmentAgent,
)
from app.data.mock_data import MockDataStore
from app.services.llm_service import LLMService

router = APIRouter()

# Initialize agents (lazy loading would be better for production)
agents = {
    "automotive_sales": AutomotiveSalesAgent(),
    "damage_assessment": DamageAssessmentAgent(),
    "document_processing": DocumentProcessingAgent(),
    "marketing_content": MarketingContentAgent(),
    "compliance": ComplianceAgent(),
    "sales_trainer": SalesTrainerAgent(),
    "trend_spotter": TrendSpotterAgent(),
    "warranty_claims": WarrantyClaimsAgent(),
    "cross_selling": CrossSellingAgent(),
    "order_fulfillment": OrderFulfillmentAgent(),
}


class ChatRequest(BaseModel):
    message: str
    agent_id: str
    context: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    response: str
    agent_id: str
    context: Optional[Dict[str, Any]] = None
    workflow_steps: Optional[List[Dict[str, Any]]] = None


class OrderRequest(BaseModel):
    items: List[Dict[str, Any]]
    customer_id: Optional[str] = None


class CrossSellRequest(BaseModel):
    current_items: List[str]
    customer_id: Optional[str] = None
    domain: str = "auto"


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Hub API is running", "version": "1.0.0"}


@router.get("/agents")
async def list_agents():
    """List all available agents with their metadata."""
    agent_list = [
        {
            "id": "automotive_sales",
            "name": "Automotive Sales Agent",
            "description": "End-to-end customer journey for vehicle sales and service",
            "icon": "🚗",
            "category": "Automotive",
            "features": ["Sales Inquiry", "Test Drive Booking", "Financing Options", "Service Scheduling"]
        },
        {
            "id": "damage_assessment",
            "name": "Vehicle Damage Assessment",
            "description": "Vision AI for analyzing vehicle damage and repair estimates",
            "icon": "📸",
            "category": "Automotive",
            "features": ["Image Analysis", "Damage Detection", "Cost Estimation", "Service Booking"],
            "accepts_image": True
        },
        {
            "id": "document_processing",
            "name": "Document Processing",
            "description": "Intelligent extraction from shipping documents and invoices",
            "icon": "📄",
            "category": "Logistics",
            "features": ["OCR", "Multilingual", "Data Extraction", "Validation"],
            "accepts_image": True
        },
        {
            "id": "marketing_content",
            "name": "Marketing Content Studio",
            "description": "AI-generated marketing content in multiple languages and styles",
            "icon": "✨",
            "category": "Marketing",
            "features": ["Ad Copy", "Social Media", "Video Scripts", "Localization"]
        },
        {
            "id": "compliance",
            "name": "Compliance Copilot",
            "description": "Healthcare regulatory compliance and SOP comparison",
            "icon": "⚕️",
            "category": "Healthcare",
            "features": ["Document Analysis", "Gap Detection", "Risk Assessment", "Action Items"],
            "accepts_image": True
        },
        {
            "id": "sales_trainer",
            "name": "Sales Trainer",
            "description": "Role-play training scenarios for sales staff",
            "icon": "🎭",
            "category": "HR & Training",
            "features": ["Role-Play", "Scenarios", "Scoring", "Feedback"]
        },
        {
            "id": "trend_spotter",
            "name": "Trend Spotter",
            "description": "Social media trend analysis and market insights",
            "icon": "📈",
            "category": "Marketing",
            "features": ["Trend Analysis", "Sentiment", "Supplier Matching", "Insights"]
        },
        {
            "id": "warranty_claims",
            "name": "Warranty Claims",
            "description": "Automated warranty claim processing with fraud detection",
            "icon": "🛡️",
            "category": "Customer Service",
            "features": ["OCR", "Verification", "Fraud Detection", "Auto-Approval"],
            "accepts_image": True
        },
        {
            "id": "cross_selling",
            "name": "Cross-Selling Intelligence",
            "description": "Smart product recommendations and bundle offers",
            "icon": "🛒",
            "category": "Sales",
            "features": ["Recommendations", "Bundles", "Pricing", "Sales Pitches"]
        },
        {
            "id": "order_fulfillment",
            "name": "Order Fulfillment Agent",
            "description": "Agentic order processing and warehouse management",
            "icon": "📦",
            "category": "Logistics",
            "features": ["Order Processing", "Inventory Check", "Route Optimization", "Delivery Tracking"]
        },
    ]
    return {"agents": agent_list}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with a specific agent."""
    if request.agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")
    
    agent = agents[request.agent_id]
    
    # Build message history
    messages = request.conversation_history or []
    messages.append({"role": "user", "content": request.message})
    
    # Run the agent
    result = await agent.run(request.message, request.context or {})
    
    return ChatResponse(
        response=result["response"],
        agent_id=request.agent_id,
        context=result.get("context"),
        workflow_steps=result.get("workflow_steps")
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Chat with a specific agent using streaming response."""
    if request.agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")
    
    agent = agents[request.agent_id]
    
    # Build message history
    messages = request.conversation_history or []
    messages.append({"role": "user", "content": request.message})
    
    async def generate():
        """Generate streaming response."""
        try:
            llm_service = LLMService.get_instance()
            system_prompt = agent.get_system_prompt()
            
            async for chunk in llm_service.chat_stream(messages, system_prompt):
                # Send as SSE format
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            # On error, send error message
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'content': error_msg})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/chat/workflow-stream")
async def chat_workflow_stream(request: ChatRequest):
    """Chat with an agent using streaming workflow updates."""
    if request.agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")
    
    agent = agents[request.agent_id]
    
    async def generate():
        """Generate streaming response with workflow updates."""
        try:
            # Check if agent supports streaming workflow
            if hasattr(agent, 'run_with_streaming'):
                async for event in agent.run_with_streaming(request.message, request.context or {}):
                    yield f"data: {json.dumps(event)}\n\n"
            else:
                # Fall back to regular run
                result = await agent.run(request.message, request.context or {})
                
                # Send workflow steps one by one with delay simulation
                if result.get("workflow_steps"):
                    for step in result["workflow_steps"]:
                        yield f"data: {json.dumps({'type': 'workflow_step', 'step': step})}\n\n"
                
                # Send final response
                yield f"data: {json.dumps({'type': 'response', 'content': result.get('response', '')})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/chat-with-image")
async def chat_with_image(
    agent_id: str = Form(...),
    message: str = Form(...),
    image: UploadFile = File(...)
):
    """Chat with an agent including an image."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    
    # Read and encode image
    image_content = await image.read()
    image_base64 = base64.b64encode(image_content).decode("utf-8")
    
    agent = agents[agent_id]
    
    # Run agent with image context
    context = {"image_base64": image_base64, "mime_type": image.content_type}
    result = await agent.run(message, context)
    
    return {
        "response": result["response"],
        "agent_id": agent_id,
        "context": result.get("context"),
        "workflow_steps": result.get("workflow_steps")
    }


@router.post("/chat-with-image/stream")
async def chat_with_image_stream(
    agent_id: str = Form(...),
    message: str = Form(...),
    image: UploadFile = File(...)
):
    """Chat with an agent including an image, with streaming workflow updates."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    
    # Read and encode image
    image_content = await image.read()
    image_base64 = base64.b64encode(image_content).decode("utf-8")
    
    agent = agents[agent_id]
    context = {"image_base64": image_base64, "mime_type": image.content_type}
    
    async def generate():
        try:
            if hasattr(agent, 'run_with_streaming'):
                async for event in agent.run_with_streaming(message, context):
                    yield f"data: {json.dumps(event)}\n\n"
            else:
                # Fallback to regular run
                result = await agent.run(message, context)
                if result.get("workflow_steps"):
                    for step in result["workflow_steps"]:
                        yield f"data: {json.dumps({'type': 'workflow_step', 'step': step})}\n\n"
                yield f"data: {json.dumps({'type': 'response', 'content': result.get('response', '')})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/order/process")
async def process_order(request: OrderRequest):
    """Process an order through the fulfillment agent."""
    agent = agents["order_fulfillment"]
    
    order = {"items": request.items, "customer_id": request.customer_id}
    result = agent.process_order(order)
    
    return result


@router.post("/cross-sell/recommend")
async def get_cross_sell_recommendations(request: CrossSellRequest):
    """Get cross-sell recommendations."""
    agent = agents["cross_selling"]
    
    result = agent.get_recommendations(
        request.current_items,
        request.customer_id,
        request.domain
    )
    
    return result


@router.get("/trends/dashboard")
async def get_trends_dashboard():
    """Get trend spotter dashboard data."""
    agent = agents["trend_spotter"]
    return agent.get_dashboard_data()


@router.get("/inventory/{sku}")
async def check_inventory(sku: str):
    """Check inventory for a SKU."""
    return MockDataStore.check_inventory(sku)


@router.get("/vehicles")
async def list_vehicles(brand: Optional[str] = None):
    """List available vehicles."""
    return {"vehicles": MockDataStore.get_available_vehicles(brand)}


@router.get("/warranty/{serial_number}")
async def check_warranty(serial_number: str):
    """Check warranty status for a serial number."""
    return MockDataStore.check_warranty(serial_number)


@router.get("/training/scenarios")
async def list_training_scenarios():
    """List available training scenarios."""
    agent = agents["sales_trainer"]
    return {"scenarios": agent.SCENARIOS}


class ApprovalRequest(BaseModel):
    approval_id: str
    approved: bool


@router.post("/approval/submit")
async def submit_approval(request: ApprovalRequest):
    """Submit human approval decision for a pending workflow."""
    from app.agents.order_fulfillment_agent import PENDING_APPROVALS
    
    if request.approval_id not in PENDING_APPROVALS:
        raise HTTPException(status_code=404, detail="Approval not found or expired")
    
    return {"status": "received", "approval_id": request.approval_id, "approved": request.approved}


@router.post("/approval/continue-stream")
async def continue_approval_stream(request: ApprovalRequest):
    """Continue a workflow after approval with streaming updates."""
    agent = agents["order_fulfillment"]
    
    async def generate():
        context = {"approval_id": request.approval_id, "approved": request.approved}
        async for event in agent.run_with_streaming("", context):
            yield f"data: {json.dumps(event)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
