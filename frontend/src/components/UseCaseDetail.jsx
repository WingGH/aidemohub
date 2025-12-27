import React from 'react'
import { 
  ArrowLeft, 
  MessageSquare, 
  Image, 
  FileText, 
  Zap,
  CheckCircle2,
  PlayCircle
} from 'lucide-react'

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
    businessValue: "Reduces sales cycle time by 40% and enables 24/7 customer engagement"
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
    businessValue: "Increases service efficiency and speeds up insurance claim processing by 60%"
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
    businessValue: "Reduces manual data entry by 80% and processing errors by 95%"
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
    businessValue: "Reduces content creation time by 70% while maintaining brand consistency"
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
    businessValue: "Reduces compliance review time by 50% and regulatory risk exposure"
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
    businessValue: "Scalable upskilling that reduces manager training time by 60%"
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
    businessValue: "Keeps FMCG portfolio relevant with data-driven trend insights"
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
    businessValue: "Streamlines after-sales service with 85% auto-approval rate"
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
    businessValue: "Increases average order value by 25% with smart bundling"
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
    businessValue: "Enhances logistics efficiency with 30% faster order processing"
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

