import React from 'react'
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
  GitBranch
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
    ]
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
    ]
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
    ]
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
    ]
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
    ]
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
    ]
  }
}

function UseCaseDetail({ agent, onBack, onStartChat }) {
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

