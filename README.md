# AI Hub - Enterprise AI Demo Platform

A comprehensive demo platform showcasing 12 AI use cases built with LangGraph, FastAPI, and React. Features **multi-agent systems**, agentic workflows with real-time visualization, multi-modal AI (vision + text), and human-in-the-loop capabilities.

![AI Hub](https://img.shields.io/badge/AI-Hub-blue?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Framework-green?style=for-the-badge)
![Multi-Agent](https://img.shields.io/badge/Multi--Agent-Systems-orange?style=for-the-badge)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-purple?style=for-the-badge)

## ✨ Features

- **12 Enterprise AI Use Cases** - Ready-to-demo AI agents for various industries
- **Multi-Agent Systems** - True agent-to-agent collaboration with handoffs
- **Agentic Workflows** - Multi-step reasoning with real-time progress visualization
- **Vision AI** - Upload images for damage assessment, document processing, and more
- **Human-in-the-Loop** - Approval workflows with manager intervention
- **ML + LLM Integration** - Customer segmentation combining traditional ML with LLM insights
- **Streaming Responses** - Real-time AI responses with Server-Sent Events (SSE)
- **Modern UI** - Clean, responsive interface with TailwindCSS

## 🤖 Multi-Agent Architecture

This platform demonstrates **two multi-agent patterns**:

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

## 🎯 Use Cases

| # | Use Case | Description | Technology |
|---|----------|-------------|------------|
| 1 | **Automotive Sales Agent** ⭐ | Multi-agent system with Supervisor + 5 specialist agents | **Multi-Agent**, Supervisor Pattern |
| 2 | **Order Fulfillment Agent** ⭐ | Multi-agent chain with human-in-the-loop approval | **Multi-Agent**, Chain Pattern |
| 3 | **Vehicle Damage Assessment** | Vision AI for analyzing vehicle damage from photos | Vision AI, Multimodal Models |
| 4 | **Document Processing** | Intelligent extraction from shipping documents, invoices | Document AI, OCR, Multilingual |
| 5 | **Marketing Content Studio** | AI-generated marketing content in multiple languages | Generative AI, Localization |
| 6 | **Compliance Copilot** | Healthcare regulatory compliance analysis and SOP comparison | NLP, Document Understanding |
| 7 | **Sales Trainer** | Role-play training scenarios with AI customer simulation | Conversational AI |
| 8 | **Trend Spotter** | Social media trend analysis and market insights for FMCG | Social Listening, Sentiment |
| 9 | **Warranty Claims** | Automated warranty claim processing with fraud detection | OCR, Fraud Detection AI |
| 10 | **Cross-Selling Intelligence** | Smart product recommendations and bundle pricing | Recommendation AI |
| 11 | **Voice Analytics** 🆕 | Customer service call sentiment analysis | Speech-to-Text, NLP |
| 12 | **Customer Segmentation** 🆕 | ML-powered RFM analysis with LLM insights | ML + LLM, Churn Prediction |

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

## 🏗️ Architecture

```
aihub/
├── backend/                    # FastAPI + LangGraph Backend
│   ├── app/
│   │   ├── agents/            # AI Agents (one per use case)
│   │   │   ├── base_agent.py  # Abstract base agent class
│   │   │   ├── automotive_sales_agent.py  # 🤖 Multi-Agent (Supervisor)
│   │   │   ├── order_fulfillment_agent.py # 🤖 Multi-Agent (Chain)
│   │   │   ├── voice_analytics_agent.py   # 🆕 Voice analysis
│   │   │   ├── customer_segmentation_agent.py # 🆕 ML + LLM
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

### Agentic Workflows (with Progress Bar)

These agents show step-by-step workflow visualization:

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

## 🤝 Contributing

See [DEVELOPER.md](./DEVELOPER.md) for instructions on adding new use cases.

## 📄 License

MIT License - feel free to use and modify for your demos.

---

Built with ❤️ for enterprise AI demonstrations
