# AI Hub - Enterprise AI Demo Platform

A comprehensive demo platform showcasing 10 AI use cases built with LangGraph, FastAPI, and React. Features agentic workflows with real-time visualization, multi-modal AI (vision + text), and human-in-the-loop capabilities.

![AI Hub](https://img.shields.io/badge/AI-Hub-blue?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Framework-green?style=for-the-badge)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-purple?style=for-the-badge)

## ✨ Features

- **10 Enterprise AI Use Cases** - Ready-to-demo AI agents for various industries
- **Agentic Workflows** - Multi-step reasoning with real-time progress visualization
- **Vision AI** - Upload images for damage assessment, document processing, and more
- **Human-in-the-Loop** - Approval workflows with manager intervention
- **Streaming Responses** - Real-time AI responses with Server-Sent Events (SSE)
- **Modern UI** - Clean, responsive interface with TailwindCSS

## 🎯 Use Cases

| # | Use Case | Description | Technology |
|---|----------|-------------|------------|
| 1 | **Automotive Sales Agent** | End-to-end customer journey for vehicle sales, test drives, and financing | Agentic AI, Multi-step Reasoning |
| 2 | **Vehicle Damage Assessment** | Vision AI for analyzing vehicle damage from photos and estimating repairs | Vision AI, Multimodal Models |
| 3 | **Document Processing** | Intelligent extraction from shipping documents, invoices, customs forms | Document AI, OCR, Multilingual |
| 4 | **Marketing Content Studio** | AI-generated marketing content in multiple languages and styles | Generative AI, Localization |
| 5 | **Compliance Copilot** | Healthcare regulatory compliance analysis and SOP comparison | NLP, Document Understanding |
| 6 | **Sales Trainer** | Role-play training scenarios with AI-powered customer simulation | Conversational AI |
| 7 | **Trend Spotter** | Social media trend analysis and market insights for FMCG | Social Listening, Sentiment |
| 8 | **Warranty Claims** | Automated warranty claim processing with fraud detection | OCR, Fraud Detection AI |
| 9 | **Cross-Selling Intelligence** | Smart product recommendations and bundle pricing | Recommendation AI |
| 10 | **Order Fulfillment Agent** | Agentic order processing with human-in-the-loop approval | Agentic AI, Logistics |

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
│   │   │   ├── automotive_sales_agent.py
│   │   │   ├── damage_assessment_agent.py
│   │   │   └── ...
│   │   ├── services/          # Reusable services
│   │   │   ├── llm_service.py     # LangChain LLM wrapper
│   │   │   ├── openai_service.py  # Direct OpenRouter calls
│   │   │   └── vision_service.py  # Vision/multimodal support
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
    │   │   ├── WorkflowVisualizer.jsx  # Workflow progress
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

### Agentic Workflows (with Progress Bar)

These agents show step-by-step workflow visualization:

1. **Order Fulfillment Agent** - Includes human-in-the-loop approval
2. **Warranty Claims** - Fraud detection workflow
3. **Document Processing** - OCR and extraction steps
4. **Marketing Content Studio** - Content generation pipeline
5. **Automotive Sales Agent** - Customer journey flow
6. **Compliance Copilot** - Regulatory analysis workflow

### Vision AI Demos

Upload images to these agents:

1. **Vehicle Damage Assessment** - Upload damage photos
2. **Document Processing** - Upload invoices, shipping docs
3. **Warranty Claims** - Upload receipts and product images

### Human-in-the-Loop

The **Order Fulfillment Agent** demonstrates human approval:

1. Submit an order (e.g., "Process an order for 100 units of Oat Milk")
2. Watch the workflow progress
3. A "Manager Approval" dialog appears
4. Click Approve or Reject to continue

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
