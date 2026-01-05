import React from 'react'
import { 
  CheckCircle2, 
  Circle, 
  Loader2,
  ArrowRight,
  Package,
  Search,
  ClipboardCheck,
  Truck,
  FileText,
  Shield,
  AlertTriangle,
  Sparkles,
  Image,
  MessageSquare,
  UserCheck,
  XCircle,
  Bot,
  Brain,
  Users,
  Warehouse,
  CreditCard,
  Wrench,
  Target,
  Mic,
  PieChart,
  Receipt,
  BadgeCheck,
  DollarSign,
  ScanLine
} from 'lucide-react'

const stepIcons = {
  receive: Package,
  search: Search,
  check: ClipboardCheck,
  verify: Shield,
  process: Loader2,
  complete: CheckCircle2,
  deliver: Truck,
  analyze: Search,
  extract: FileText,
  validate: ClipboardCheck,
  generate: Sparkles,
  image: Image,
  review: MessageSquare,
  alert: AlertTriangle,
  approval: UserCheck,
  rejected: XCircle,
  // Multi-agent icons
  supervisor: Target,
  intent: Brain,
  inventory: Package,
  finance: CreditCard,
  finance_approval: DollarSign,
  service: Wrench,
  test_drive: Target,
  intake: Package,
  warehouse: Warehouse,
  shipping: Truck,
  human: Users,
  agent: Bot,
  voice: Mic,
  ml: PieChart,
  // Expense claim icons
  ocr: ScanLine,
  validation: BadgeCheck,
  manager_approval: UserCheck,
  receipt: Receipt,
  default: Circle
}

// Agent colors for visual distinction
const agentColors = {
  'Supervisor': 'purple',
  'Intent Analyzer': 'indigo',
  'Inventory Specialist': 'blue',
  'Inventory': 'blue',
  'Finance Specialist': 'emerald',
  'Service Advisor': 'orange',
  'Test Drive Coordinator': 'cyan',
  'Order Intake': 'teal',
  'Warehouse': 'amber',
  'Shipping': 'rose',
  'Human': 'violet',
  // Expense claim agents
  'OCR Agent': 'cyan',
  'Validation Agent': 'blue',
  'Manager': 'amber',
  'Finance': 'emerald',
  'default': 'gray'
}

function getAgentColor(agent) {
  return agentColors[agent] || agentColors['default']
}

function WorkflowVisualizer({ steps, currentStep, title, showAgentLabels = true }) {
  if (!steps || steps.length === 0) return null

  // Check if this is a multi-agent workflow (has agent property)
  const isMultiAgent = steps.some(step => step.agent)

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4 shadow-sm">
      <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        {isMultiAgent ? (
          <>
            <Bot className="w-4 h-4 text-purple-600" />
            {title || 'Multi-Agent Workflow'}
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4 text-blue-600" />
            {title || 'Workflow Progress'}
          </>
        )}
      </h4>
      
      <div className="flex items-center gap-1 overflow-x-auto pb-2">
        {steps.map((step, index) => {
          const isActive = step.status === 'active'
          const isComplete = step.status === 'complete'
          const isPending = step.status === 'pending'
          const isRejected = step.status === 'rejected'
          const IconComponent = stepIcons[step.icon] || stepIcons[step.step] || stepIcons.default
          const agentColor = step.agent ? getAgentColor(step.agent) : null
          
          // Dynamic agent-based styling
          const agentBgActive = agentColor ? `bg-${agentColor}-50 border border-${agentColor}-200` : 'bg-blue-50 border border-blue-200'
          const agentIconBg = agentColor ? `bg-${agentColor}-100 text-${agentColor}-600` : 'bg-blue-100 text-blue-600'
          const agentTextColor = agentColor ? `text-${agentColor}-700` : 'text-blue-700'
          
          return (
            <React.Fragment key={step.id || step.step || index}>
              <div 
                className={`
                  flex flex-col items-center min-w-[90px] p-2 rounded-lg transition-all relative
                  ${isActive ? 'bg-blue-50 border border-blue-200 shadow-sm' : ''}
                  ${isRejected ? 'bg-red-50 border border-red-200' : ''}
                  ${isComplete ? 'opacity-100' : isPending ? 'opacity-50' : 'opacity-100'}
                `}
              >
                {/* Agent badge for multi-agent workflows */}
                {step.agent && showAgentLabels && (
                  <span className={`
                    absolute -top-2 left-1/2 -translate-x-1/2 
                    text-[9px] font-bold px-1.5 py-0.5 rounded-full whitespace-nowrap
                    ${isComplete ? 'bg-green-100 text-green-700' : ''}
                    ${isActive ? 'bg-blue-100 text-blue-700' : ''}
                    ${isPending ? 'bg-gray-100 text-gray-500' : ''}
                    ${isRejected ? 'bg-red-100 text-red-700' : ''}
                    ${!isComplete && !isActive && !isPending && !isRejected ? 'bg-gray-100 text-gray-600' : ''}
                  `}>
                    {step.agent}
                  </span>
                )}
                
                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center mb-1 mt-${step.agent ? '2' : '0'}
                  ${isComplete ? 'bg-green-100 text-green-600' : ''}
                  ${isActive ? 'bg-blue-100 text-blue-600' : ''}
                  ${isPending ? 'bg-gray-100 text-gray-400' : ''}
                  ${isRejected ? 'bg-red-100 text-red-600' : ''}
                  ${!isComplete && !isActive && !isPending && !isRejected ? 'bg-gray-100 text-gray-500' : ''}
                `}>
                  {isActive ? (
                    step.step === 'approval' || step.id === 'approval' ? (
                      <UserCheck className="w-5 h-5 animate-pulse" />
                    ) : step.agent ? (
                      <Bot className="w-5 h-5 animate-pulse" />
                    ) : (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    )
                  ) : isComplete ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : isRejected ? (
                    <XCircle className="w-5 h-5" />
                  ) : (
                    <IconComponent className="w-5 h-5" />
                  )}
                </div>
                <span className={`
                  text-xs text-center font-medium leading-tight
                  ${isActive ? 'text-blue-700' : ''}
                  ${isComplete ? 'text-green-700' : ''}
                  ${isRejected ? 'text-red-700' : ''}
                  ${isPending ? 'text-gray-400' : 'text-gray-600'}
                `}>
                  {step.label}
                </span>
                
                {/* Show result preview if available */}
                {step.result && isComplete && (
                  <span className="text-[10px] text-gray-400 mt-0.5 max-w-[80px] truncate">
                    {step.result.handoff ? `→ ${step.result.handoff.split(' ')[0]}` : ''}
                    {step.result.vehicles_found !== undefined ? `${step.result.vehicles_found} found` : ''}
                    {step.result.intent ? step.result.intent : ''}
                  </span>
                )}
              </div>
              
              {index < steps.length - 1 && (
                <div className="flex flex-col items-center">
                  <ArrowRight className={`
                    w-4 h-4 flex-shrink-0
                    ${isComplete ? 'text-green-400' : 'text-gray-300'}
                  `} />
                  {/* Show agent handoff indicator */}
                  {steps[index + 1]?.agent && step.agent && steps[index + 1].agent !== step.agent && (
                    <span className="text-[8px] text-gray-400 -mt-1">handoff</span>
                  )}
                </div>
              )}
            </React.Fragment>
          )
        })}
      </div>
      
      {/* Multi-agent legend */}
      {isMultiAgent && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Bot className="w-3 h-3" /> Multi-Agent System
            </span>
            <span className="flex items-center gap-1">
              <ArrowRight className="w-3 h-3" /> Agent Handoff
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

// Predefined workflows for different agents - updated for multi-agent architecture
export const AGENT_WORKFLOWS = {
  // Multi-Agent: Automotive Sales (Supervisor Pattern)
  automotive_sales: [
    { id: 'supervisor', step: 'supervisor', label: 'Supervisor', icon: 'supervisor', status: 'pending', agent: 'Supervisor' },
    { id: 'intent', step: 'intent', label: 'Analyze Intent', icon: 'intent', status: 'pending', agent: 'Intent Analyzer' },
    { id: 'specialist', step: 'specialist', label: 'Specialist', icon: 'agent', status: 'pending', agent: 'Specialist' },
    { id: 'respond', step: 'respond', label: 'Response', icon: 'complete', status: 'pending', agent: 'Supervisor' },
  ],
  
  // Multi-Agent: Order Fulfillment (Chain Pattern)
  order_fulfillment: [
    { id: 'intake', step: 'intake', label: 'Order Intake', icon: 'intake', status: 'pending', agent: 'Order Intake' },
    { id: 'inventory', step: 'inventory', label: 'Inventory', icon: 'inventory', status: 'pending', agent: 'Inventory' },
    { id: 'approval', step: 'approval', label: 'Approval', icon: 'approval', status: 'pending', agent: 'Human' },
    { id: 'warehouse', step: 'warehouse', label: 'Warehouse', icon: 'warehouse', status: 'pending', agent: 'Warehouse' },
    { id: 'shipping', step: 'shipping', label: 'Shipping', icon: 'shipping', status: 'pending', agent: 'Shipping' },
  ],
  
  // Single Agent Workflows
  warranty_claims: [
    { id: 'receive', label: 'Receive Claim', icon: 'receive', status: 'pending' },
    { id: 'extract', label: 'Extract Data', icon: 'extract', status: 'pending' },
    { id: 'verify', label: 'Verify Warranty', icon: 'verify', status: 'pending' },
    { id: 'fraud', label: 'Fraud Check', icon: 'alert', status: 'pending' },
    { id: 'decide', label: 'Decision', icon: 'complete', status: 'pending' },
  ],
  document_processing: [
    { id: 'receive', label: 'Receive Doc', icon: 'receive', status: 'pending' },
    { id: 'ocr', label: 'OCR Scan', icon: 'search', status: 'pending' },
    { id: 'extract', label: 'Extract Fields', icon: 'extract', status: 'pending' },
    { id: 'validate', label: 'Validate', icon: 'validate', status: 'pending' },
    { id: 'complete', label: 'Complete', icon: 'complete', status: 'pending' },
  ],
  marketing_content: [
    { id: 'brief', label: 'Analyze Brief', icon: 'receive', status: 'pending' },
    { id: 'generate', label: 'Generate Copy', icon: 'generate', status: 'pending' },
    { id: 'image', label: 'Suggest Image', icon: 'image', status: 'pending' },
    { id: 'review', label: 'Review', icon: 'review', status: 'pending' },
  ],
  compliance: [
    { id: 'receive', label: 'Receive Doc', icon: 'receive', status: 'pending' },
    { id: 'extract', label: 'Extract Rules', icon: 'extract', status: 'pending' },
    { id: 'compare', label: 'Compare SOPs', icon: 'search', status: 'pending' },
    { id: 'gaps', label: 'Find Gaps', icon: 'alert', status: 'pending' },
    { id: 'report', label: 'Report', icon: 'complete', status: 'pending' },
  ],
  voice_analytics: [
    { id: 'receive', label: 'Receive Recording', icon: 'voice', status: 'pending' },
    { id: 'transcribe', label: 'Transcribe Audio', icon: 'extract', status: 'pending' },
    { id: 'sentiment', label: 'Analyze Sentiment', icon: 'search', status: 'pending' },
    { id: 'insights', label: 'Generate Insights', icon: 'generate', status: 'pending' },
  ],
  customer_segmentation: [
    { id: 'load', label: 'Load Data', icon: 'receive', status: 'pending' },
    { id: 'rfm', label: 'Calculate RFM', icon: 'search', status: 'pending' },
    { id: 'ml', label: 'ML Prediction', icon: 'ml', status: 'pending' },
    { id: 'insights', label: 'Generate Insights', icon: 'complete', status: 'pending' },
  ],
  
  // Multi-Agent: Expense Claim (Chain Pattern with Dual Approval)
  expense_claim: [
    { id: 'ocr', step: 'ocr', label: 'Extract Receipt', icon: 'ocr', status: 'pending', agent: 'OCR Agent' },
    { id: 'validation', step: 'validation', label: 'Validate Claim', icon: 'validation', status: 'pending', agent: 'Validation Agent' },
    { id: 'manager_approval', step: 'manager_approval', label: 'Manager Approval', icon: 'manager_approval', status: 'pending', agent: 'Manager' },
    { id: 'finance_approval', step: 'finance_approval', label: 'Finance Approval', icon: 'finance_approval', status: 'pending', agent: 'Finance' },
  ],
}

export default WorkflowVisualizer
