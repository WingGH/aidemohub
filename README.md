# AI Hub - Enterprise AI Demo Platform

A comprehensive demo platform showcasing 13 AI use cases built with LangGraph, FastAPI, and React. Features **multi-agent systems**, agentic workflows with real-time visualization, multi-modal AI (vision + text), and human-in-the-loop capabilities.

![AI Hub](https://img.shields.io/badge/AI-Hub-blue?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Framework-green?style=for-the-badge)
![Multi-Agent](https://img.shields.io/badge/Multi--Agent-Systems-orange?style=for-the-badge)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-purple?style=for-the-badge)

## ✨ Features

- **13 Enterprise AI Use Cases** - Ready-to-demo AI agents for various industries
- **Multi-Agent Systems** - True agent-to-agent collaboration with handoffs
- **Agentic Workflows** - Multi-step reasoning with real-time progress visualization
- **Vision AI** - Upload images for damage assessment, document processing, and more
- **Human-in-the-Loop** - Approval workflows with dual manager + finance checkpoints
- **ML + LLM Integration** - Customer segmentation combining traditional ML with LLM insights
- **Streaming Responses** - Real-time AI responses with Server-Sent Events (SSE)
- **Modern UI** - Clean, responsive interface with TailwindCSS

## 🤖 Multi-Agent Architecture

This platform demonstrates **three multi-agent patterns**:

### Supervisor Pattern (Automotive Sales)
```
┌─────────────────────────────────────────────┐
│           🎯 Supervisor Agent               │
│      (Routes to appropriate specialist)     │
└──────────────┬──────────────────────────────┘
               │
   ┌───────────┼───────────┬───────────┬───────────┐
   ▼           ▼           ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│🧠Intent│ │🚗Inventory│ │💰Finance│ │🔧Service│ │🎯TestDrive│
│Analyzer│ │Specialist│ │Specialist│ │ Advisor │ │Coordinator│
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

### Chain Pattern (Order Fulfillment)
```
📥 Order Intake → 📦 Inventory → 👤 Human Approval → 🏭 Warehouse → 🚚 Shipping
     Agent           Agent          (Manager)          Agent         Agent
```

### Dual Approval Chain (Expense Claims) 🆕
```
📷 OCR Agent → ✅ Validation → 🧑‍💼 Manager Approval → 💰 Finance Approval
  (Vision AI)      Agent         (Human-in-Loop)       (Human-in-Loop)
```

## 🎯 Use Cases

| # | Use Case | Description | Technology |
|---|----------|-------------|------------|
| 1 | **Automotive Sales Agent** ⭐ | Multi-agent system with Supervisor + 5 specialist agents | **Multi-Agent**, Supervisor Pattern |
| 2 | **Order Fulfillment Agent** ⭐ | Multi-agent chain with human-in-the-loop approval | **Multi-Agent**, Chain Pattern |
| 3 | **Expense Claim** ⭐🆕 | Multi-agent chain with dual approval (Manager → Finance) | **Multi-Agent**, Dual Approval, Vision AI |
| 4 | **Vehicle Damage Assessment** | Vision AI for analyzing vehicle damage from photos | Vision AI, Multimodal Models |
| 5 | **Document Processing** | Intelligent extraction from shipping documents, invoices | Document AI, OCR, Multilingual |
| 6 | **Marketing Content Studio** | AI-generated marketing content in multiple languages | Generative AI, Localization |
| 7 | **Compliance Copilot** | Healthcare regulatory compliance analysis and SOP comparison | NLP, Document Understanding |
| 8 | **Sales Trainer** | Role-play training scenarios with AI customer simulation | Conversational AI |
| 9 | **Trend Spotter** | Social media trend analysis and market insights for FMCG | Social Listening, Sentiment |
| 10 | **Warranty Claims** | Automated warranty claim processing with fraud detection | OCR, Fraud Detection AI |
| 11 | **Cross-Selling Intelligence** | Smart product recommendations and bundle pricing | Recommendation AI |
| 12 | **Voice Analytics** | Customer service call sentiment analysis | Speech-to-Text, NLP |
| 13 | **Customer Segmentation** | ML-powered RFM analysis with LLM insights | ML + LLM, Churn Prediction |

⭐ = Multi-Agent System | 🆕 = New

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenRouter API key ([Get one here](https://openrouter.ai/keys))

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/aihub.git
cd aihub
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your OpenRouter API key

# Run the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

## ☁️ AWS EC2 Deployment

### Prerequisites

- AWS Account with EC2 access
- Domain name (optional, for HTTPS)
- SSH key pair for EC2

### Step 1: Launch EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance

2. **Choose AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)

3. **Instance Type**: 
   - Development/Demo: `t3.medium` (2 vCPU, 4GB RAM)
   - Production: `t3.large` or higher

4. **Configure Security Group** (Inbound Rules):
   | Type | Port | Source |
   |------|------|--------|
   | SSH | 22 | Your IP |
   | HTTP | 80 | 0.0.0.0/0 |
   | HTTPS | 443 | 0.0.0.0/0 |
   | Custom TCP | 8000 | 0.0.0.0/0 |
   | Custom TCP | 5173 | 0.0.0.0/0 |

5. **Storage**: 20GB gp3 (minimum)

6. **Launch** and download the key pair (.pem file)

### Step 2: Connect to EC2

```bash
# Set permissions on key file
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install nginx (reverse proxy)
sudo apt install -y nginx

# Install Git
sudo apt install -y git
```

### Step 4: Clone and Setup Backend

```bash
# Clone repository
cd /home/ubuntu
git clone https://github.com/your-username/aihub.git
cd aihub/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
nano .env  # Add your OPENROUTER_API_KEY
```

### Step 5: Setup Backend Service (systemd)

```bash
# Create service file
sudo nano /etc/systemd/system/aihub-backend.service
```

Add the following content:

```ini
[Unit]
Description=AI Hub Backend
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/aihub/backend
Environment="PATH=/home/ubuntu/aihub/backend/venv/bin"
ExecStart=/home/ubuntu/aihub/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aihub-backend
sudo systemctl start aihub-backend

# Check status
sudo systemctl status aihub-backend
```

### Step 6: Build and Deploy Frontend

```bash
cd /home/ubuntu/aihub/frontend

# Install dependencies
npm install

# Update API URL for production
nano src/api.js
# Change: const API_BASE_URL = 'http://<EC2-PUBLIC-IP>:8000'

# Build for production
npm run build

# Copy build to nginx
sudo cp -r dist/* /var/www/html/
```

### Step 7: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/default
```

Replace with:

```nginx
server {
    listen 80;
    server_name _;

    # Frontend (React)
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
        
        # SSE support
        proxy_buffering off;
        proxy_read_timeout 86400;
    }
}
```

```bash
# Test and restart nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: Update Frontend API URL

For the nginx proxy setup, update `frontend/src/api.js`:

```javascript
// Change from localhost to relative path (uses nginx proxy)
const API_BASE_URL = '/api'
```

Then rebuild:

```bash
cd /home/ubuntu/aihub/frontend
npm run build
sudo cp -r dist/* /var/www/html/
```

### Step 9: Access Your Application

- **Frontend**: `http://<EC2-PUBLIC-IP>`
- **Backend API**: `http://<EC2-PUBLIC-IP>/api`
- **API Docs**: `http://<EC2-PUBLIC-IP>/api/docs`

### Optional: Setup HTTPS with Let's Encrypt

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (requires domain pointing to EC2)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Useful Commands

```bash
# View backend logs
sudo journalctl -u aihub-backend -f

# Restart backend
sudo systemctl restart aihub-backend

# Restart nginx
sudo systemctl restart nginx

# Update code
cd /home/ubuntu/aihub
git pull
sudo systemctl restart aihub-backend
cd frontend && npm run build && sudo cp -r dist/* /var/www/html/
```

## 🏗️ Architecture

```
aihub/
├── backend/                    # FastAPI + LangGraph Backend
│   ├── app/
│   │   ├── agents/            # AI Agents (one per use case)
│   │   │   ├── base_agent.py  # Abstract base agent class
│   │   │   ├── automotive_sales_agent.py  # 🤖 Multi-Agent (Supervisor)
│   │   │   ├── order_fulfillment_agent.py # 🤖 Multi-Agent (Chain)
│   │   │   ├── expense_claim_agent.py     # 🤖 Multi-Agent (Dual Approval) 🆕
│   │   │   ├── voice_analytics_agent.py   # Voice analysis
│   │   │   ├── customer_segmentation_agent.py # ML + LLM
│   │   │   └── ...
│   │   ├── services/          # Reusable services
│   │   │   ├── llm_service.py     # LangChain LLM wrapper
│   │   │   ├── openai_service.py  # Direct OpenRouter calls
│   │   │   └── vision_service.py  # Vision/multimodal support
│   │   ├── tools/             # Agent tools
│   │   │   ├── automotive_tools.py
│   │   │   ├── fulfillment_tools.py
│   │   │   └── warranty_tools.py
│   │   ├── data/              # Mock data and stores
│   │   │   └── mock_data.py   # Simulated business data
│   │   ├── api/               # API routes
│   │   │   └── routes.py      # FastAPI endpoints
│   │   ├── config.py          # Configuration
│   │   └── main.py            # Application entry
│   ├── requirements.txt
│   ├── .env.example           # Environment template
│   └── .env                   # Your local config (git-ignored)
│
└── frontend/                   # React + Vite Frontend
    ├── src/
    │   ├── components/        # UI Components
    │   │   ├── Sidebar.jsx    # Navigation sidebar
    │   │   ├── ChatPanel.jsx  # Chat interface
    │   │   ├── WorkflowVisualizer.jsx  # Multi-agent workflow progress
    │   │   ├── UseCaseDetail.jsx  # Use case descriptions + sample data
    │   │   └── ...
    │   ├── hooks/             # Reusable hooks
    │   │   └── useWorkflow.js # Workflow state management
    │   ├── api.js             # API client
    │   └── App.jsx            # Main app
    ├── package.json
    └── tailwind.config.js
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional
LLM_PROVIDER=openai  # Options: "openai" (default) or "langchain"
```

### LLM Models

The platform uses these models via OpenRouter:

| Model | Purpose |
|-------|---------|
| `openai/gpt-4o` | Primary model for chat and reasoning |
| `openai/gpt-4o` | Vision model for image analysis |
| `anthropic/claude-3.5-sonnet` | Fallback model |

## 💡 Demo Guide

### Multi-Agent Demos ⭐

Best demonstrations of multi-agent architecture:

1. **Automotive Sales Agent** (Supervisor Pattern)
   - Try: "Show me vehicles under $35,000"
   - Watch: Supervisor → Intent Analyzer → Inventory Specialist with agent labels
   - Each specialist agent has its own LLM and provides specialized insights

2. **Order Fulfillment Agent** (Chain Pattern)
   - Try: "Process an order for 100 units of Oat Milk"
   - Watch: Order Intake → Inventory → Human Approval → Warehouse → Shipping
   - Includes human-in-the-loop approval checkpoint

3. **Expense Claim** (Dual Approval Chain) 🆕
   - Try: "Submit an expense claim for $850 client dinner" (or upload a receipt image)
   - Watch: OCR Agent → Validation → Manager Approval → Finance Approval
   - Features **two human-in-the-loop** checkpoints (Manager + Finance)
   - Supports Vision AI for receipt image extraction

### Agentic Workflows (with Progress Bar)

These agents show step-by-step workflow visualization:

- **Expense Claim** - Receipt OCR → Validation → Dual Approval
- **Warranty Claims** - Fraud detection workflow
- **Document Processing** - OCR and extraction steps
- **Marketing Content Studio** - Content generation pipeline
- **Compliance Copilot** - Regulatory analysis workflow
- **Voice Analytics** - Transcription → Sentiment → Insights
- **Customer Segmentation** - Data → RFM → ML → LLM Insights

### Vision AI Demos

Upload images to these agents:

1. **Vehicle Damage Assessment** - Upload damage photos
2. **Document Processing** - Upload invoices, shipping docs
3. **Warranty Claims** - Upload receipts and product images
4. **Expense Claim** 🆕 - Upload receipt images for automatic extraction

### ML + LLM Integration

The **Customer Segmentation** agent demonstrates combining:
- Traditional ML (RFM scoring, churn prediction)
- LLM analysis (insights generation, recommendations)

## 🔧 Multi-Agent Implementation Details

### Automotive Sales - Supervisor Pattern

```python
# 5 Specialist Agents, each with its own LLM
class IntentAnalyzerAgent:      # 🧠 Classifies customer intent
class InventorySpecialistAgent: # 🚗 Searches vehicles, recommends
class FinanceSpecialistAgent:   # 💰 Calculates financing, advises
class ServiceAdvisorAgent:      # 🔧 Handles service requests
class TestDriveCoordinatorAgent: # 🎯 Schedules test drives

class AutomotiveSalesAgent:     # 🎯 Supervisor - routes to specialists
```

### Order Fulfillment - Chain Pattern

```python
# 4 Chain Agents that process sequentially
class OrderIntakeAgent:    # 📥 Validates orders
class InventoryAgent:      # 📦 Checks & allocates stock
class WarehouseAgent:      # 🏭 Generates pick lists
class ShippingAgent:       # 🚚 Schedules delivery

# Human-in-the-loop between Inventory and Warehouse
```

### Expense Claim - Dual Approval Chain 🆕

```python
# 4 Agents with TWO human checkpoints
class OCRAgent:            # 📷 Vision AI receipt extraction
class ValidationAgent:     # ✅ Policy checking & compliance
class ManagerApprovalAgent: # 🧑‍💼 Boss approval (claims > $200)
class FinanceApprovalAgent: # 💰 Final approval & payment

# Human-in-the-loop at Manager AND Finance stages
```

## 📚 Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **LangGraph** - Agent workflow orchestration
- **LangChain** - LLM application framework
- **OpenRouter** - Multi-model LLM gateway
- **httpx** - Async HTTP client

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Lucide React** - Icons
- **React Markdown** - Message rendering

## 🛠️ Developer Guide: Adding New Use Cases

This section explains how to add a new AI use case to the platform.

### Files to Update

| # | File | Required | Purpose |
|---|------|----------|---------|
| 1 | `backend/app/agents/<new>_agent.py` | ✅ | Create the agent logic |
| 2 | `backend/app/agents/__init__.py` | ✅ | Export the new agent |
| 3 | `backend/app/api/routes.py` | ✅ | Register API endpoints |
| 4 | `backend/app/data/mock_data.py` | Optional | Add sample data |
| 5 | `frontend/src/components/UseCaseDetail.jsx` | ✅ | Add description & prompts |
| 6 | `frontend/src/components/Sidebar.jsx` | Optional | Add new category |
| 7 | `frontend/src/hooks/useWorkflow.js` | If workflow | Enable workflow visualization |
| 8 | `frontend/src/components/WorkflowVisualizer.jsx` | If workflow | Define workflow steps |
| 9 | `frontend/src/components/ChatPanel.jsx` | Optional | Add sample prompts |

### Step 1: Create the Agent (Backend)

Create `backend/app/agents/my_new_agent.py`:

```python
"""My New Agent - Description of what it does."""
from typing import Dict, Any, List, AsyncIterator
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState


class MyNewAgent(BaseAgent):
    """Agent for handling specific use case."""
    
    def __init__(self):
        super().__init__(
            name="My New Agent",
            description="Description shown in the sidebar"
        )
    
    def get_system_prompt(self) -> str:
        return """You are an expert AI assistant for [domain].
        
Your capabilities include:
- Capability 1
- Capability 2

Always be helpful and professional."""
    
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph."""
        
        async def process_request(state: AgentState) -> AgentState:
            # Get user message
            user_message = state["messages"][-1]["content"]
            
            # Process with LLM
            response = await self.llm_service.chat(
                state["messages"],
                self.get_system_prompt()
            )
            
            state["result"] = response
            state["messages"].append({"role": "assistant", "content": response})
            return state
        
        # Build workflow
        workflow = StateGraph(AgentState)
        workflow.add_node("process", process_request)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        
        return workflow
    
    # Optional: Add streaming support for workflow visualization
    async def run_with_streaming(self, message: str, context: Dict = None, 
                                  conversation_history: List = None) -> AsyncIterator[Dict]:
        """Stream workflow updates and response."""
        # Yield workflow steps as they complete
        yield {"type": "workflow_step", "all_steps": [...], "step": {...}}
        
        # Yield final response
        yield {"type": "response", "content": "Final response here"}
```

### Step 2: Export the Agent

Add to `backend/app/agents/__init__.py`:

```python
from .my_new_agent import MyNewAgent

__all__ = [
    # ... existing agents ...
    "MyNewAgent",
]
```

### Step 3: Register API Routes

Update `backend/app/api/routes.py`:

```python
from app.agents import MyNewAgent

# Add to agents dictionary (around line 20)
agents = {
    # ... existing agents ...
    "my_new_agent": MyNewAgent(),
}

# Add to agent listing (in list_agents function)
{
    "id": "my_new_agent",
    "name": "My New Agent",
    "description": "What this agent does",
    "category": "Category Name",  # e.g., "Operations", "Sales", "Finance"
    "icon": "icon-name",  # Lucide icon name
    "features": ["Feature 1", "Feature 2"],
    "has_vision": False,  # True if supports image upload
    "has_workflow": True,  # True if has step-by-step workflow
}
```

### Step 4: Add Mock Data (Optional)

If your agent needs sample data, add to `backend/app/data/mock_data.py`:

```python
MY_SAMPLE_DATA = [
    {"id": "1", "name": "Sample Item 1", ...},
    {"id": "2", "name": "Sample Item 2", ...},
]

# Add getter method to MockDataStore class
@staticmethod
def get_my_sample_data():
    return MY_SAMPLE_DATA
```

### Step 5: Add Frontend Description

Update `frontend/src/components/UseCaseDetail.jsx`:

```javascript
const useCaseDetails = {
  // ... existing cases ...
  
  my_new_agent: {
    title: "My New Agent",
    description: "What this agent does and why it's useful.",
    howItWorks: [
      "Step 1 of how it works",
      "Step 2 of how it works",
      "Step 3 of how it works"
    ],
    tryPrompts: [
      "Example prompt 1",
      "Example prompt 2"
    ],
    technologies: ["LangGraph", "GPT-4o", "Custom Tech"],
    businessValue: [
      "Business benefit 1",
      "Business benefit 2"
    ],
    architecture: [
      { name: "LLM", type: "llm" },
      { name: "Agent Framework", type: "agent" },
      { name: "Your Data Source", type: "data" }
    ],
    sampleData: {
      title: "Sample Data",
      description: "Example data used by this agent",
      items: [
        { id: "1", title: "Item 1", subtitle: "Description" },
        { id: "2", title: "Item 2", subtitle: "Description" }
      ]
    }
  }
}
```

### Step 6: Enable Workflow Visualization (If Applicable)

If your agent has a multi-step workflow:

**A. Add to `frontend/src/hooks/useWorkflow.js`:**

```javascript
export const WORKFLOW_AGENTS = [
  // ... existing agents ...
  'my_new_agent',
]
```

**B. Add workflow definition to `frontend/src/components/WorkflowVisualizer.jsx`:**

```javascript
export const AGENT_WORKFLOWS = {
  // ... existing workflows ...
  
  my_new_agent: [
    { id: 'step1', label: 'Step 1 Name', icon: 'FileSearch' },
    { id: 'step2', label: 'Step 2 Name', icon: 'CheckCircle' },
    { id: 'step3', label: 'Step 3 Name', icon: 'Send' },
  ],
}
```

### Step 7: Add Sample Prompts (Optional)

Add to `frontend/src/components/ChatPanel.jsx` in `samplePrompts`:

```javascript
const samplePrompts = {
  // ... existing prompts ...
  
  my_new_agent: [
    "Sample prompt 1 for quick testing",
    "Sample prompt 2 for another scenario"
  ]
}
```

### Adding Vision Support

For agents that accept image uploads:

1. Set `has_vision: True` in routes.py agent listing
2. Access image in your agent:

```python
async def run(self, message: str, context: Dict = None, ...):
    if context and context.get("image_base64"):
        # Process image with vision service
        analysis = await self.vision_service.analyze_image(
            context["image_base64"],
            "Your prompt here",
            context.get("mime_type", "image/jpeg")
        )
```

### Adding Human-in-the-Loop

For agents requiring human approval:

```python
# In your streaming method, yield approval request:
yield {
    "type": "approval_required",
    "approval_id": f"MYAGENT-{uuid.uuid4().hex[:8]}",
    "title": "Approval Required",
    "message": "Please review and approve.",
    "details": {
        "field1": "value1",
        "field2": "value2"
    },
    "all_steps": workflow_steps
}
```

### Testing Your New Agent

1. **Backend**: Restart uvicorn server
2. **Frontend**: Refresh browser (hot reload should work)
3. **Verify**: Check API docs at `http://localhost:8000/docs`
4. **Test**: Select your agent in the sidebar and try the prompts

## 📄 License

MIT License - feel free to use and modify for your demos.

---

Built with ❤️ for enterprise AI demonstrations
