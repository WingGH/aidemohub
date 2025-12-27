# Developer Guide: Adding New Use Cases

This guide explains how to add new AI use cases to the AI Hub platform.

## Table of Contents

1. [Overview](#overview)
2. [Backend: Creating an Agent](#backend-creating-an-agent)
3. [Backend: Adding Workflow Streaming](#backend-adding-workflow-streaming)
4. [Backend: Registering the Agent](#backend-registering-the-agent)
5. [Frontend: Adding to Navigation](#frontend-adding-to-navigation)
6. [Frontend: Workflow Visualization](#frontend-workflow-visualization)
7. [Frontend: Quick Prompts](#frontend-quick-prompts)
8. [Testing Your Agent](#testing-your-agent)

---

## Overview

Each use case consists of:

| Component | Location | Purpose |
|-----------|----------|---------|
| Agent Class | `backend/app/agents/` | AI logic and LangGraph workflow |
| API Route | `backend/app/api/routes.py` | HTTP endpoints |
| Frontend Entry | `frontend/src/api.js` | API client calls |
| UI Components | `frontend/src/components/` | Chat, workflow display |

---

## Backend: Creating an Agent

### Step 1: Create the Agent File

Create a new file in `backend/app/agents/`:

```python
# backend/app/agents/my_new_agent.py

"""My New Agent - Description of what it does."""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
import asyncio

# Delay between workflow steps (for visualization)
STEP_DELAY = 1.0


class MyNewAgent(BaseAgent):
    """Agent for [describe your use case]."""
    
    def __init__(self):
        super().__init__(
            name="My New Agent",
            description="What this agent does in one sentence"
        )
    
    def get_system_prompt(self) -> str:
        """Define the agent's personality and capabilities."""
        return """You are an expert assistant for [domain].

Your capabilities include:
- Capability 1
- Capability 2
- Capability 3

Guidelines:
- Be helpful and accurate
- Ask clarifying questions when needed
- Provide structured responses

Always maintain a professional tone."""

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        async def process_request(state: AgentState) -> AgentState:
            """Main processing node."""
            # Generate response using LLM
            response = await self.llm_service.chat(
                state["messages"],
                self.get_system_prompt()
            )
            state["result"] = response
            state["messages"].append({"role": "assistant", "content": response})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("process", process_request)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        
        return workflow
```

### Step 2: Add Mock Data (Optional)

If your agent needs business data, add it to `backend/app/data/mock_data.py`:

```python
# Add to MockDataStore class

MY_DATA = {
    "item1": {"name": "Item 1", "value": 100},
    "item2": {"name": "Item 2", "value": 200},
}
```

---

## Backend: Adding Workflow Streaming

For agents with multi-step workflows, add a `run_with_streaming` method:

```python
async def run_with_streaming(self, user_input: str, context: Dict[str, Any] = None):
    """Run the agent with streaming workflow updates."""
    workflow_steps = []
    
    # Step 1: Receive Request
    step1 = {"step": "receive", "status": "active", "label": "Receive Request"}
    workflow_steps.append(step1)
    yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
    
    # Simulate processing time
    await asyncio.sleep(STEP_DELAY)
    workflow_steps[-1]["status"] = "complete"
    yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
    
    # Step 2: Process
    step2 = {"step": "process", "status": "active", "label": "Process Data"}
    workflow_steps.append(step2)
    yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
    
    # Do actual processing
    response = await self.llm_service.chat(
        [{"role": "user", "content": user_input}],
        self.get_system_prompt()
    )
    
    await asyncio.sleep(STEP_DELAY)
    workflow_steps[-1]["status"] = "complete"
    yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
    
    # Step 3: Complete
    step3 = {"step": "complete", "status": "active", "label": "Complete"}
    workflow_steps.append(step3)
    yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
    
    await asyncio.sleep(STEP_DELAY)
    workflow_steps[-1]["status"] = "complete"
    yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
    
    # Final response
    yield {"type": "response", "content": response}
```

---

## Backend: Registering the Agent

### Step 1: Export from `__init__.py`

Edit `backend/app/agents/__init__.py`:

```python
from app.agents.my_new_agent import MyNewAgent

__all__ = [
    # ... existing agents
    "MyNewAgent",
]
```

### Step 2: Add to Routes

Edit `backend/app/api/routes.py`:

```python
# Add import
from app.agents import (
    # ... existing imports
    MyNewAgent,
)

# Add to agents dictionary
agents = {
    # ... existing agents
    "my_new_agent": MyNewAgent(),
}

# Add to /agents endpoint
@router.get("/agents")
async def list_agents():
    return [
        # ... existing entries
        {
            "id": "my_new_agent",
            "name": "My New Agent",
            "description": "What this agent does",
            "category": "Category Name",  # e.g., "Automotive", "Logistics", "Marketing"
            "icon": "icon_name",  # Lucide icon name
            "capabilities": ["vision"]  # Optional: add "vision" if supports images
        },
    ]
```

---

## Frontend: Adding to Navigation

The sidebar automatically picks up agents from the `/api/agents` endpoint, but you may want to customize:

### Adding Quick Prompts

Edit `frontend/src/components/ChatPanel.jsx`:

```javascript
const agentPrompts = {
  // ... existing agents
  my_new_agent: [
    "Example prompt 1",
    "Example prompt 2",
    "Example prompt 3",
  ]
}
```

---

## Frontend: Workflow Visualization

### Step 1: Add to WORKFLOW_AGENTS

Edit `frontend/src/hooks/useWorkflow.js`:

```javascript
export const WORKFLOW_AGENTS = [
  // ... existing agents
  'my_new_agent'
]
```

### Step 2: Define Workflow Steps

Edit `frontend/src/components/WorkflowVisualizer.jsx`:

```javascript
export const AGENT_WORKFLOWS = {
  // ... existing workflows
  my_new_agent: [
    { id: 'receive', label: 'Receive Request', icon: 'receive', status: 'pending' },
    { id: 'process', label: 'Process Data', icon: 'process', status: 'pending' },
    { id: 'complete', label: 'Complete', icon: 'complete', status: 'pending' },
  ],
}
```

### Step 3: Update ChatPanel WORKFLOW_AGENTS

Edit `frontend/src/components/ChatPanel.jsx`:

```javascript
const WORKFLOW_AGENTS = [
  // ... existing agents
  'my_new_agent'
]
```

### Available Icons

The workflow visualizer supports these icons:

| Icon Key | Description |
|----------|-------------|
| `receive` | Package icon - receiving input |
| `search` | Search icon - analyzing/finding |
| `check` | Clipboard check - validation |
| `verify` | Shield - verification |
| `process` | Loader - processing |
| `complete` | Check circle - completion |
| `deliver` | Truck - delivery/shipping |
| `extract` | File text - extracting data |
| `generate` | Sparkles - AI generation |
| `image` | Image - visual content |
| `review` | Message - review/feedback |
| `alert` | Alert triangle - warnings |
| `approval` | User check - human approval |

---

## Adding Vision Support

For agents that process images:

### Backend

```python
from app.services.vision_service import VisionService

class MyVisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Vision Agent", description="...")
        self.vision_service = VisionService.get_instance()
    
    async def analyze_image(self, image_base64: str, prompt: str) -> str:
        """Analyze an image using vision AI."""
        return await self.vision_service.analyze_image(image_base64, prompt)
```

### Frontend

Add `"vision"` to the agent's capabilities in routes.py, and the UI will automatically show the image upload button.

---

## Adding Human-in-the-Loop

For approval workflows, yield an `approval_required` event:

### Backend

```python
async def run_with_streaming(self, user_input: str, context: Dict[str, Any] = None):
    # ... previous steps ...
    
    # Approval step
    step = {"step": "approval", "status": "active", "label": "Manager Approval"}
    workflow_steps.append(step)
    yield {"type": "workflow_step", "step": step, "all_steps": workflow_steps.copy()}
    
    # Request approval
    yield {
        "type": "approval_required",
        "order_id": "12345",
        "items": [...],
        "estimated_value": 1000.00
    }
    # The frontend will pause here and show an approval dialog
```

### Handling Approval Response

Add a `continue_workflow_stream` method:

```python
async def continue_workflow_stream(self, data: Dict[str, Any]):
    """Continue workflow after human approval."""
    decision = data.get("decision")
    workflow_steps = data.get("workflow_steps", [])
    
    if decision == "approve":
        # Continue with approved workflow
        yield {"type": "workflow_step", ...}
        yield {"type": "response", "content": "Order approved!"}
    else:
        # Handle rejection
        yield {"type": "response", "content": "Order rejected."}
```

---

## Testing Your Agent

### 1. Restart the Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Check API Docs

Visit http://localhost:8000/docs and verify your agent appears in `/api/agents`.

### 3. Test via Frontend

1. Open http://localhost:5173
2. Find your agent in the sidebar
3. Test with various prompts
4. Verify workflow visualization (if applicable)

### 4. Test API Directly

```bash
# Simple chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my_new_agent", "message": "Hello"}'

# Streaming workflow
curl -X POST http://localhost:8000/api/chat/workflow-stream \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my_new_agent", "message": "Test"}'
```

---

## Best Practices

1. **System Prompts**: Be specific about capabilities and limitations
2. **Workflow Steps**: Keep to 4-6 steps for visual clarity
3. **Delays**: Use 1-second delays for demo visibility
4. **Error Handling**: Wrap LLM calls in try/except
5. **Mock Data**: Use realistic sample data for demos
6. **Testing**: Test both chat and streaming endpoints

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not showing | Check routes.py registration |
| Workflow not updating | Ensure agent is in WORKFLOW_AGENTS list |
| Import errors | Check `__init__.py` exports |
| Streaming not working | Verify `run_with_streaming` method exists |
| Vision not working | Add "vision" to capabilities |

---

For more help, check the existing agents in `backend/app/agents/` for reference implementations.

