import React, { useState } from 'react'
import { 
  ArrowLeft, 
  MessageSquare, 
  Image, 
  FileText, 
  Zap,
  CheckCircle2,
  PlayCircle,
  Server,
  Database,
  Cpu,
  Layers,
  Cloud,
  Eye,
  Brain,
  GitBranch,
  Table,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

// Architecture component icons
const architectureIcons = {
  llm: Brain,
  vectordb: Database,
  agent: GitBranch,
  data: Layers,
  vision: Eye,
  api: Cloud,
  compute: Cpu,
  server: Server
}

// Detailed descriptions for each use case
const useCaseDetails = {
  automotive_sales: {
    title: "Automotive Sales & Service Agent",
    subtitle: "End-to-end customer journey automation",
    description: "An autonomous AI agent that handles the complete customer journey—from initial inquiry, test drive scheduling, financing options, to after-sales service booking. It can access multiple systems, make decisions, and complete multi-step tasks without human intervention.",
    howItWorks: [
      "Customer initiates conversation with a vehicle inquiry",
      "AI identifies customer needs and preferences",
      "Presents matching vehicles from inventory with pricing",
      "Offers to schedule test drives with available slots",
      "Discusses financing options and calculates payments",
      "Books service appointments for existing customers"
    ],
    tryPrompts: [
      "Show me available vehicles under $50,000",
      "I want to schedule a test drive for the BMW 3 Series",
      "What financing options do you offer for a 5-year term?",
      "I need to book a brake service for my Toyota Camry"
    ],
    technologies: ["Agentic AI", "Tool Use", "Multi-step Reasoning", "CRM Integration"],
    businessValue: "Reduces sales cycle time by 40% and enables 24/7 customer engagement",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 / Claude for intent understanding and response generation" },
      { type: "agent", name: "Agent Framework", description: "LangGraph for multi-step workflow orchestration" },
      { type: "data", name: "Vehicle Inventory DB", description: "Real-time vehicle database with pricing and availability" },
      { type: "data", name: "CRM System", description: "Customer profiles, preferences, and interaction history" },
      { type: "api", name: "Scheduling API", description: "Calendar integration for test drives and service booking" },
      { type: "api", name: "Financing Calculator", description: "Loan/lease calculation service with rate APIs" }
    ],
    sampleData: {
      title: "Vehicle Inventory",
      description: "Sample vehicles with pricing and availability",
      items: [
        { id: "V001", name: "2024 Toyota Camry", details: "$35,000 - Silver - Available" },
        { id: "V002", name: "2024 Honda Accord", details: "$38,000 - White - Available" },
        { id: "V003", name: "2024 BMW 3 Series", details: "$55,000 - Black - Available" },
        { id: "V004", name: "2024 Mercedes C-Class", details: "$58,000 - Blue - Reserved" },
        { id: "V005", name: "2024 Lexus ES", details: "$48,000 - Pearl White - Available" }
      ]
    }
  },
  damage_assessment: {
    title: "Vehicle Damage Assessment",
    subtitle: "Vision AI for instant damage analysis",
    description: "Customers or mechanics upload photos or videos of vehicle damage, and AI instantly assesses repair needs, estimates costs, and can schedule service appointments. Useful for insurance claims and service centers.",
    howItWorks: [
      "User uploads photo of vehicle damage",
      "AI analyzes the image using vision models",
      "Identifies damage type, location, and severity",
      "Lists affected components requiring repair/replacement",
      "Provides cost estimate range",
      "Recommends repair vs. insurance claim decision"
    ],
    tryPrompts: [
      "Analyze this photo of my car's front bumper",
      "What type of damage can you assess?",
      "Can you estimate repair costs from a photo?",
      "Is this damage worth an insurance claim?"
    ],
    technologies: ["Vision AI", "Multimodal Models", "Real-time Analysis"],
    businessValue: "Increases service efficiency and speeds up insurance claim processing by 60%",
    architecture: [
      { type: "llm", name: "Vision Language Model", description: "GPT-4V / Claude Vision for image understanding" },
      { type: "vision", name: "Image Processing", description: "Pre-processing for damage detection and localization" },
      { type: "data", name: "Parts & Pricing DB", description: "Vehicle parts catalog with repair cost estimates" },
      { type: "vectordb", name: "Damage Examples DB", description: "Vector store of historical damage cases for comparison" },
      { type: "api", name: "Insurance Integration", description: "Claims submission and threshold verification" }
    ],
    sampleData: {
      title: "Parts & Repair Pricing",
      description: "Auto parts inventory with pricing for estimates",
      items: [
        { id: "P001", name: "Brake Pads (Front)", details: "$120 - 45 in stock" },
        { id: "P002", name: "Brake Rotors", details: "$180 - 20 in stock" },
        { id: "P003", name: "Timing Belt", details: "$250 - 15 in stock" }
      ]
    }
  },
  document_processing: {
    title: "Intelligent Document Processing",
    subtitle: "OCR and multilingual document extraction",
    description: "Automates extraction and processing of shipping documents, customs forms, invoices, and bills of lading. Handles multiple languages (Chinese, English) and handwritten notes with high accuracy.",
    howItWorks: [
      "Upload shipping document, invoice, or customs form",
      "AI performs OCR to extract all text",
      "Identifies document type automatically",
      "Extracts key fields: dates, amounts, parties, items",
      "Handles multilingual content (EN/CN)",
      "Validates completeness and flags missing info"
    ],
    tryPrompts: [
      "Process this shipping invoice",
      "What types of documents can you handle?",
      "Extract data from this bill of lading",
      "Can you process documents in Chinese?"
    ],
    technologies: ["Document AI", "OCR", "NLP", "Multilingual Processing"],
    businessValue: "Reduces manual data entry by 80% and processing errors by 95%",
    architecture: [
      { type: "llm", name: "Vision Language Model", description: "GPT-4V for document understanding and field extraction" },
      { type: "vision", name: "OCR Engine", description: "Multilingual OCR for text extraction (EN/CN/handwritten)" },
      { type: "agent", name: "Document Classifier", description: "Auto-detect document type (invoice, BOL, customs)" },
      { type: "data", name: "Document Templates", description: "Schema definitions for different document types" },
      { type: "api", name: "ERP Integration", description: "Push extracted data to enterprise systems" }
    ]
  },
  marketing_content: {
    title: "Marketing Content Studio",
    subtitle: "AI-generated marketing content",
    description: "Generates localized marketing content for different brands—including ad copy, social media posts, promotional video scripts, and product descriptions in multiple languages and styles.",
    howItWorks: [
      "Describe your product, campaign, or brand",
      "Specify target audience and platform",
      "Choose tone and style preferences",
      "AI generates multiple content variations",
      "Includes headlines, body copy, and CTAs",
      "Provides hashtag and visual recommendations"
    ],
    tryPrompts: [
      "Create an Instagram post for our new electric vehicle launch",
      "Write ad copy for a summer sale promotion",
      "Generate a 30-second video script for organic food products",
      "Create WeChat content for Korean food products in Hong Kong"
    ],
    technologies: ["Generative AI", "Content Generation", "Localization", "Multi-platform"],
    businessValue: "Reduces content creation time by 70% while maintaining brand consistency",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 / Claude for creative content generation" },
      { type: "agent", name: "Content Workflow", description: "LangGraph for multi-step content creation pipeline" },
      { type: "vectordb", name: "Brand Guidelines DB", description: "Vector store of brand voice, style guides, examples" },
      { type: "data", name: "Campaign Templates", description: "Pre-defined templates for different platforms" },
      { type: "api", name: "Image Generation", description: "DALL-E / Stable Diffusion for visual suggestions" },
      { type: "api", name: "Translation Service", description: "Multilingual localization (EN/CN/etc.)" }
    ]
  },
  compliance: {
    title: "Compliance Copilot",
    subtitle: "Healthcare regulatory compliance assistant",
    description: "Helps regulatory officers navigate complex, changing regulatory documents from health authorities. Compares new documents against internal SOPs and highlights exactly which processes need updating to remain compliant.",
    howItWorks: [
      "Upload new compliance PDF from health authority",
      "AI extracts and analyzes requirements",
      "Compares against current internal SOPs",
      "Identifies compliance gaps and conflicts",
      "Prioritizes action items by risk level",
      "Estimates implementation timeline"
    ],
    tryPrompts: [
      "What SOPs do we currently have in place?",
      "Analyze this new Department of Health regulation",
      "What are our compliance gaps for pharmaceutical storage?",
      "Generate action items for the new import requirements"
    ],
    technologies: ["NLP", "Document Understanding", "Risk Assessment"],
    businessValue: "Reduces compliance review time by 50% and regulatory risk exposure",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 / Claude for regulatory document analysis" },
      { type: "vectordb", name: "SOP Knowledge Base", description: "Vector DB of internal SOPs and procedures (RAG)" },
      { type: "vectordb", name: "Regulations DB", description: "Indexed regulatory documents for semantic search" },
      { type: "agent", name: "Gap Analysis Engine", description: "LangGraph workflow for comparison and gap detection" },
      { type: "vision", name: "PDF Parser", description: "Document extraction from regulatory PDFs" },
      { type: "data", name: "Risk Scoring Model", description: "Priority classification for compliance gaps" }
    ],
    sampleData: {
      title: "Internal SOPs",
      description: "Standard Operating Procedures for compliance comparison",
      items: [
        { id: "SOP-001", name: "Pharmaceutical Storage Guidelines", details: "v2.1 - Temperature & Humidity Control" },
        { id: "SOP-002", name: "Import Documentation Requirements", details: "v1.5 - Certificates & Customs" }
      ]
    }
  },
  sales_trainer: {
    title: "Role-Play Sales Trainer",
    subtitle: "AI-powered sales training scenarios",
    description: "Training tool for sales staff to practice handling difficult customers or negotiating prices. AI plays realistic customer roles with various objections, then provides detailed feedback and performance scores.",
    howItWorks: [
      "Say 'start training' to begin a scenario",
      "AI presents a challenging customer situation",
      "Practice your sales pitch and responses",
      "AI responds realistically as the customer",
      "Say 'give feedback' to end the session",
      "Receive detailed scorecard and improvement tips"
    ],
    tryPrompts: [
      "Start a new training scenario",
      "Practice handling price objections",
      "Give me a difficult customer to practice with",
      "I want to practice competitor comparison scenarios"
    ],
    technologies: ["Conversational AI", "Role-play Simulation", "Performance Analytics"],
    businessValue: "Scalable upskilling that reduces manager training time by 60%",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 / Claude for realistic customer role-play" },
      { type: "data", name: "Scenario Library", description: "Pre-defined training scenarios and personas" },
      { type: "agent", name: "Conversation Manager", description: "State tracking for multi-turn role-play sessions" },
      { type: "llm", name: "Evaluation Model", description: "LLM-as-judge for performance scoring" },
      { type: "data", name: "Scoring Rubrics", description: "Criteria for sales skill assessment" }
    ]
  },
  trend_spotter: {
    title: "Social Sentiment & Trend Spotter",
    subtitle: "Market trend analysis for FMCG",
    description: "Identifies trending food and beverage items in Hong Kong specifically, analyzing social media mentions across platforms. Cross-references trends with supplier databases to recommend sourcing opportunities.",
    howItWorks: [
      "Say 'show dashboard' for trending overview",
      "View real-time trend data across platforms",
      "See growth rates and sentiment analysis",
      "Get supplier recommendations for trending items",
      "Identify emerging opportunities before competitors",
      "Plan distribution strategy based on insights"
    ],
    tryPrompts: [
      "Show me the trends dashboard",
      "What's trending on Hong Kong Instagram right now?",
      "Which Korean food trends should we capitalize on?",
      "Find suppliers for trending organic products"
    ],
    technologies: ["Social Listening", "Sentiment Analysis", "Market Intelligence"],
    businessValue: "Keeps FMCG portfolio relevant with data-driven trend insights",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 for trend analysis and insights generation" },
      { type: "api", name: "Social Media APIs", description: "Instagram, TikTok, Xiaohongshu data feeds" },
      { type: "data", name: "Trend Database", description: "Historical trend data with growth metrics" },
      { type: "data", name: "Supplier Directory", description: "Supplier catalog matched to product categories" },
      { type: "agent", name: "Sentiment Analyzer", description: "NLP pipeline for sentiment classification" },
      { type: "vectordb", name: "Product Embeddings", description: "Vector matching for trend-to-supplier recommendations" }
    ],
    sampleData: {
      title: "Trending Items",
      description: "Current social media trend data in Hong Kong",
      items: [
        { id: "T001", name: "Korean Rosé Tteokbokki", details: "15,420 mentions (+340%) - Instagram" },
        { id: "T002", name: "Oat Milk Coffee", details: "8,900 mentions (+120%) - Instagram" },
        { id: "T003", name: "Matcha Desserts", details: "12,000 mentions (+200%) - TikTok" },
        { id: "T004", name: "Japanese Whisky", details: "4,200 mentions (+65%) - Instagram" }
      ]
    }
  },
  warranty_claims: {
    title: "Warranty Claims Processing",
    subtitle: "Automated claims with fraud detection",
    description: "Processes warranty claims for electrical appliances automatically. Uses OCR to extract receipt data, verifies warranty periods, checks for fraud indicators like duplicate claims, and auto-approves valid claims.",
    howItWorks: [
      "Upload photo of receipt and product serial number",
      "AI extracts text using OCR",
      "Verifies purchase date is within warranty",
      "Checks if serial number was claimed before",
      "Looks for fraud indicators",
      "Auto-approves or flags for manual review"
    ],
    tryPrompts: [
      "How do I process a warranty claim?",
      "Check warranty status for serial number SN-12345678",
      "What fraud indicators do you look for?",
      "Upload receipt for claim processing"
    ],
    technologies: ["OCR", "Fraud Detection AI", "Automation"],
    businessValue: "Streamlines after-sales service with 85% auto-approval rate",
    architecture: [
      { type: "llm", name: "Vision Language Model", description: "GPT-4V for receipt OCR and data extraction" },
      { type: "agent", name: "Claims Workflow", description: "LangGraph for multi-step claim processing" },
      { type: "data", name: "Warranty Database", description: "Product registrations with warranty periods" },
      { type: "data", name: "Claims History", description: "Past claims for duplicate detection" },
      { type: "agent", name: "Fraud Detection Model", description: "Rule-based + ML scoring for fraud indicators" },
      { type: "api", name: "CRM Integration", description: "Customer notification and case management" }
    ],
    sampleData: {
      title: "Warranty Records",
      description: "Sample product registrations with warranty status",
      items: [
        { id: "SN-12345678", name: "Smart Air Purifier", details: "Valid until 2026-06-15 - No claims" },
        { id: "SN-87654321", name: "Robot Vacuum", details: "Valid until 2025-12-01 - 1 previous claim" },
        { id: "SN-11111111", name: "Electric Kettle", details: "EXPIRED 2024-01-10 - No claims" }
      ]
    }
  },
  cross_selling: {
    title: "Cross-Selling Intelligence",
    subtitle: "Smart product recommendations",
    description: "Analyzes customer purchase history and current cart to recommend complementary products. Generates bundled pricing offers and ready-to-use sales pitches for account managers.",
    howItWorks: [
      "Specify current items in cart or service booked",
      "AI analyzes complementary products",
      "Generates bundle recommendations",
      "Calculates discounted bundle pricing",
      "Provides ready-to-use sales pitch",
      "Works for both automotive parts and FMCG"
    ],
    tryPrompts: [
      "I'm buying brake pads, what else do I need?",
      "Recommend products for a customer who only buys beverages",
      "Create a bundle offer for an oil change service",
      "What should I cross-sell with frozen dumplings?"
    ],
    technologies: ["Recommendation AI", "Pricing Optimization", "Sales Enablement"],
    businessValue: "Increases average order value by 25% with smart bundling",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 for sales pitch generation" },
      { type: "vectordb", name: "Product Embeddings", description: "Vector DB for product similarity matching" },
      { type: "data", name: "Purchase History", description: "Customer transaction data for pattern analysis" },
      { type: "data", name: "Product Catalog", description: "SKU database with pricing and categories" },
      { type: "agent", name: "Bundle Optimizer", description: "Pricing rules for discount calculations" },
      { type: "data", name: "Association Rules", description: "Frequently-bought-together patterns" }
    ]
  },
  order_fulfillment: {
    title: "Order Fulfillment Agent",
    subtitle: "Agentic warehouse and logistics management",
    description: "An AI agent that receives orders, checks stock across multiple warehouses, optimizes picking routes, allocates inventory from optimal locations, and coordinates deliveries with real-time updates.",
    howItWorks: [
      "Receive order with item details",
      "Check inventory across all warehouses",
      "Optimize allocation from best locations",
      "Generate picking list with route optimization",
      "Coordinate with delivery carriers",
      "Provide real-time status updates"
    ],
    tryPrompts: [
      "Process an order for 100 units of Oat Milk",
      "Check inventory for SKU001 across all warehouses",
      "How does the fulfillment workflow work?",
      "What's the delivery estimate for Hong Kong Central?"
    ],
    technologies: ["Agentic AI", "Warehouse Management", "Route Optimization"],
    businessValue: "Enhances logistics efficiency with 30% faster order processing",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 for order parsing and response generation" },
      { type: "agent", name: "Agent Framework", description: "LangGraph for multi-step fulfillment workflow" },
      { type: "data", name: "Inventory System", description: "Real-time stock levels across warehouses" },
      { type: "data", name: "Warehouse Layout", description: "Zone mapping for pick route optimization" },
      { type: "api", name: "Carrier APIs", description: "Shipping rate and tracking integrations" },
      { type: "agent", name: "Human-in-the-Loop", description: "Approval workflow for high-value orders" }
    ],
    sampleData: {
      title: "Warehouse Inventory",
      description: "Multi-warehouse inventory with zone mapping",
      items: [
        { id: "SKU001", name: "Organic Oat Milk 1L", details: "500 units (HK Central) + 300 units (Kowloon)" },
        { id: "SKU002", name: "Korean Rosé Tteokbokki", details: "200 units (HK Central) - Zone B3" },
        { id: "SKU003", name: "Premium Green Tea", details: "1,000 units (HK Central) - Zone A2" },
        { id: "SKU005", name: "Plant-Based Burger Patties", details: "150 units (Kowloon) - Frozen Zone F1" }
      ]
    }
  },
  voice_analytics: {
    title: "Voice Analytics",
    subtitle: "Customer service call sentiment analysis",
    description: "Analyzes customer service call recordings to extract sentiment, identify pain points, evaluate agent performance, and generate actionable insights for service improvement. Includes audio transcription and real-time sentiment journey tracking.",
    howItWorks: [
      "Upload or receive customer service call recording",
      "AI transcribes audio to text (or use existing transcript)",
      "Analyze sentiment throughout the conversation",
      "Identify key moments: positive peaks and negative triggers",
      "Evaluate agent communication and resolution effectiveness",
      "Generate insights and improvement recommendations"
    ],
    tryPrompts: [
      "Show me all calls overview",
      "Analyze call CALL-001",
      "What's the average sentiment score?",
      "Show calls about billing disputes"
    ],
    technologies: ["Speech-to-Text", "Sentiment Analysis", "NLP", "Agent Analytics"],
    businessValue: "Improves customer satisfaction by 25% with data-driven coaching",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 for transcript analysis and insights" },
      { type: "api", name: "Speech-to-Text API", description: "Whisper / Google STT for audio transcription" },
      { type: "agent", name: "Sentiment Analyzer", description: "NLP model for emotion and sentiment scoring" },
      { type: "data", name: "Call Recordings DB", description: "Audio files with metadata and transcripts" },
      { type: "data", name: "Agent Performance DB", description: "Historical performance metrics by agent" },
      { type: "vectordb", name: "Similar Cases", description: "Vector search for comparable call patterns" }
    ],
    sampleData: {
      title: "Sample Call Recordings",
      description: "Pre-loaded customer service call transcripts with sentiment labels",
      items: [
        { id: "CALL-001", name: "Product Return - Resolved", details: "4:32 duration, Positive outcome, CSAT 5/5" },
        { id: "CALL-002", name: "Billing Dispute - Resolved", details: "6:15 duration, Mixed sentiment, CSAT 3/5" },
        { id: "CALL-003", name: "Product Inquiry - Sale", details: "3:45 duration, Very positive, CSAT 5/5" },
        { id: "CALL-004", name: "Cancellation - Retained", details: "8:20 duration, Negative to positive, CSAT 4/5" }
      ]
    }
  },
  customer_segmentation: {
    title: "Customer Segmentation",
    subtitle: "ML-powered behavioral analysis and tagging",
    description: "Uses machine learning models to segment customers based on purchasing behavior using RFM (Recency, Frequency, Monetary) analysis. Predicts customer lifetime value, identifies churn risk, and generates personalized marketing recommendations.",
    howItWorks: [
      "Load customer transaction and behavior data",
      "Calculate RFM scores for each customer",
      "Apply ML model to predict segment and churn risk",
      "Generate customer lifetime value predictions",
      "Create personalized action recommendations",
      "Visualize segment distribution and trends"
    ],
    tryPrompts: [
      "Show all customers overview",
      "Analyze customer Alice Chan",
      "Show customers in the At Risk segment",
      "What is RFM analysis?"
    ],
    technologies: ["Machine Learning", "RFM Analysis", "Churn Prediction", "LTV Modeling"],
    businessValue: "Increases retention by 35% with targeted interventions",
    architecture: [
      { type: "llm", name: "Large Language Model", description: "GPT-4 for insight generation and recommendations" },
      { type: "agent", name: "RFM Calculator", description: "Rule-based RFM scoring engine" },
      { type: "agent", name: "ML Churn Model", description: "Gradient Boosting model for churn prediction" },
      { type: "agent", name: "LTV Predictor", description: "Regression model for lifetime value estimation" },
      { type: "data", name: "Transaction History", description: "Complete purchase history database" },
      { type: "data", name: "Customer Profiles", description: "Demographics and preferences data" }
    ],
    sampleData: {
      title: "Sample Customer Profiles",
      description: "Pre-loaded customer behavior data with RFM scores and segments",
      items: [
        { id: "CUS-A001", name: "Alice Chan - Champion", details: "$12,500 spend, 45 orders, VIP tier" },
        { id: "CUS-A002", name: "Bob Liu - Regular", details: "$890 spend, 8 orders, Standard tier" },
        { id: "CUS-A003", name: "Carol Wong - Champion", details: "$45,000 spend, 120 orders, Platinum tier" },
        { id: "CUS-A004", name: "David Ng - At Risk", details: "$250 spend, 3 orders, Inactive 90+ days" },
        { id: "CUS-A005", name: "Emily Lam - Growing", details: "$3,200 spend, 15 orders, Rising engagement" },
        { id: "CUS-A006", name: "Frank Ho - Declining", details: "$4,800 spend, 25 orders, Decreasing activity" }
      ]
    }
  }
}

function UseCaseDetail({ agent, onBack, onStartChat }) {
  const [showSampleData, setShowSampleData] = useState(false)
  
  const details = useCaseDetails[agent.id] || {
    title: agent.name,
    subtitle: agent.category,
    description: agent.description,
    howItWorks: [],
    tryPrompts: [],
    technologies: agent.features || [],
    businessValue: "Enterprise-ready AI solution"
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-gradient-to-br from-surface-100 via-white to-blue-50 overflow-y-auto">
      {/* Header */}
      <header className="sticky top-0 bg-white/80 backdrop-blur-md border-b border-surface-200 px-6 py-4 z-10">
        <div className="flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-surface-600 hover:text-surface-900 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Back to list</span>
          </button>
          <button
            onClick={onStartChat}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-md hover:shadow-lg transition-all"
          >
            <PlayCircle className="w-4 h-4" />
            Get Started
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 p-8 max-w-4xl mx-auto w-full">
        {/* Hero */}
        <div className="text-center mb-10 animate-fade-in">
          <div className="text-6xl mb-4">{agent.icon}</div>
          <h1 className="text-3xl font-bold text-surface-900 mb-2">{details.title}</h1>
          <p className="text-lg text-surface-500">{details.subtitle}</p>
          
          {/* Technologies */}
          <div className="flex flex-wrap justify-center gap-2 mt-4">
            {details.technologies.map((tech, i) => (
              <span 
                key={i}
                className="px-3 py-1 bg-accent-blue/10 text-accent-blue text-sm rounded-full border border-accent-blue/20"
              >
                {tech}
              </span>
            ))}
          </div>

          {/* Start Conversation CTA - Prominent at top */}
          <div className="mt-6">
            <button
              onClick={onStartChat}
              className="inline-flex items-center gap-3 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all"
            >
              <PlayCircle className="w-5 h-5" />
              Start Conversation
            </button>
          </div>
        </div>

        {/* Description */}
        <div className="bg-white rounded-2xl p-6 border border-surface-200 shadow-soft mb-6 animate-fade-in" style={{ animationDelay: '100ms' }}>
          <h2 className="text-lg font-semibold text-surface-800 mb-3 flex items-center gap-2">
            <FileText className="w-5 h-5 text-accent-blue" />
            About This Use Case
          </h2>
          <p className="text-surface-600 leading-relaxed">{details.description}</p>
          
          {agent.accepts_image && (
            <div className="mt-4 flex items-center gap-2 px-3 py-2 bg-purple-50 rounded-lg border border-purple-200">
              <Image className="w-4 h-4 text-purple-600" />
              <span className="text-sm text-purple-700">This agent supports image uploads for visual analysis</span>
            </div>
          )}
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-2xl p-6 border border-surface-200 shadow-soft mb-6 animate-fade-in" style={{ animationDelay: '200ms' }}>
          <h2 className="text-lg font-semibold text-surface-800 mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-accent-orange" />
            How It Works
          </h2>
          <div className="space-y-3">
            {details.howItWorks.map((step, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-accent-blue/10 text-accent-blue flex items-center justify-center flex-shrink-0 text-sm font-medium">
                  {i + 1}
                </div>
                <p className="text-surface-600">{step}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Architecture Requirements */}
        {details.architecture && details.architecture.length > 0 && (
          <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl p-6 border border-slate-200 shadow-soft mb-6 animate-fade-in" style={{ animationDelay: '250ms' }}>
            <h2 className="text-lg font-semibold text-surface-800 mb-4 flex items-center gap-2">
              <Server className="w-5 h-5 text-purple-600" />
              Architecture Requirements
            </h2>
            <p className="text-sm text-surface-500 mb-4">
              Key components needed to build this use case:
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              {details.architecture.map((component, i) => {
                const IconComponent = architectureIcons[component.type] || Server
                const colorClasses = {
                  llm: 'bg-blue-50 border-blue-200 text-blue-700',
                  vectordb: 'bg-purple-50 border-purple-200 text-purple-700',
                  agent: 'bg-green-50 border-green-200 text-green-700',
                  data: 'bg-amber-50 border-amber-200 text-amber-700',
                  vision: 'bg-pink-50 border-pink-200 text-pink-700',
                  api: 'bg-cyan-50 border-cyan-200 text-cyan-700',
                  compute: 'bg-red-50 border-red-200 text-red-700',
                  server: 'bg-slate-50 border-slate-200 text-slate-700'
                }
                const colorClass = colorClasses[component.type] || colorClasses.server
                const iconColors = {
                  llm: 'text-blue-600',
                  vectordb: 'text-purple-600',
                  agent: 'text-green-600',
                  data: 'text-amber-600',
                  vision: 'text-pink-600',
                  api: 'text-cyan-600',
                  compute: 'text-red-600',
                  server: 'text-slate-600'
                }
                const iconColor = iconColors[component.type] || iconColors.server
                
                return (
                  <div 
                    key={i} 
                    className={`flex items-start gap-3 p-3 rounded-xl border ${colorClass} transition-all hover:shadow-md`}
                  >
                    <div className={`w-8 h-8 rounded-lg bg-white flex items-center justify-center flex-shrink-0 shadow-sm`}>
                      <IconComponent className={`w-4 h-4 ${iconColor}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm text-surface-800 truncate">{component.name}</h4>
                      <p className="text-xs text-surface-500 leading-relaxed">{component.description}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Sample Data Section */}
        {details.sampleData && (
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border border-amber-200 shadow-soft mb-6 animate-fade-in overflow-hidden" style={{ animationDelay: '280ms' }}>
            <button
              onClick={() => setShowSampleData(!showSampleData)}
              className="w-full p-6 flex items-center justify-between hover:bg-amber-100/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Table className="w-5 h-5 text-amber-600" />
                <h2 className="text-lg font-semibold text-surface-800">
                  {details.sampleData.title}
                </h2>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm text-amber-700 bg-amber-100 px-3 py-1 rounded-full">
                  {details.sampleData.items.length} records
                </span>
                {showSampleData ? (
                  <ChevronUp className="w-5 h-5 text-amber-600" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-amber-600" />
                )}
              </div>
            </button>
            
            {showSampleData && (
              <div className="px-6 pb-6 border-t border-amber-200">
                <p className="text-sm text-surface-500 mt-4 mb-4">
                  {details.sampleData.description}
                </p>
                <div className="space-y-2">
                  {details.sampleData.items.map((item, i) => (
                    <div 
                      key={i}
                      className="flex items-center gap-3 p-3 bg-white rounded-xl border border-amber-100 hover:border-amber-300 transition-colors"
                    >
                      <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0">
                        <span className="text-xs font-mono font-medium text-amber-700">
                          {i + 1}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm text-surface-800">{item.name}</span>
                          <span className="text-xs text-surface-400 font-mono">{item.id}</span>
                        </div>
                        <p className="text-xs text-surface-500 truncate">{item.details}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Try These Prompts */}
        <div className="bg-white rounded-2xl p-6 border border-surface-200 shadow-soft mb-6 animate-fade-in" style={{ animationDelay: '300ms' }}>
          <h2 className="text-lg font-semibold text-surface-800 mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-accent-green" />
            Try These Prompts
          </h2>
          <div className="grid gap-2">
            {details.tryPrompts.map((prompt, i) => (
              <div 
                key={i}
                className="px-4 py-3 bg-surface-50 rounded-xl text-surface-700 text-sm border border-surface-200"
              >
                "{prompt}"
              </div>
            ))}
          </div>
        </div>

        {/* Business Value */}
        <div className="bg-blue-600 rounded-2xl p-6 text-white shadow-lg animate-fade-in" style={{ animationDelay: '400ms' }}>
          <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" />
            Business Value
          </h2>
          <p className="text-white">{details.businessValue}</p>
        </div>
      </div>
    </div>
  )
}

export default UseCaseDetail

