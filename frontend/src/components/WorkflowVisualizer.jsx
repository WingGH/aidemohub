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
  XCircle
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
  default: Circle
}

function WorkflowVisualizer({ steps, currentStep, title }) {
  if (!steps || steps.length === 0) return null

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4 shadow-sm">
      <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-blue-600" />
        {title || 'Workflow Progress'}
      </h4>
      
      <div className="flex items-center gap-1 overflow-x-auto pb-2">
        {steps.map((step, index) => {
          const isActive = step.status === 'active'
          const isComplete = step.status === 'complete'
          const isPending = step.status === 'pending'
          const isRejected = step.status === 'rejected'
          const IconComponent = stepIcons[step.icon] || stepIcons.default
          
          return (
            <React.Fragment key={step.id || index}>
              <div 
                className={`
                  flex flex-col items-center min-w-[80px] p-2 rounded-lg transition-all
                  ${isActive ? 'bg-blue-50 border border-blue-200' : ''}
                  ${isRejected ? 'bg-red-50 border border-red-200' : ''}
                  ${isComplete ? 'opacity-100' : isPending ? 'opacity-50' : 'opacity-100'}
                `}
              >
                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center mb-1
                  ${isComplete ? 'bg-green-100 text-green-600' : ''}
                  ${isActive ? 'bg-blue-100 text-blue-600' : ''}
                  ${isPending ? 'bg-gray-100 text-gray-400' : ''}
                  ${isRejected ? 'bg-red-100 text-red-600' : ''}
                  ${!isComplete && !isActive && !isPending && !isRejected ? 'bg-gray-100 text-gray-500' : ''}
                `}>
                  {isActive ? (
                    step.id === 'approval' ? (
                      <UserCheck className="w-5 h-5 animate-pulse" />
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
                  text-xs text-center font-medium
                  ${isActive ? 'text-blue-700' : ''}
                  ${isComplete ? 'text-green-700' : ''}
                  ${isRejected ? 'text-red-700' : ''}
                  ${isPending ? 'text-gray-400' : 'text-gray-600'}
                `}>
                  {step.label}
                </span>
              </div>
              
              {index < steps.length - 1 && (
                <ArrowRight className={`
                  w-4 h-4 flex-shrink-0
                  ${isComplete ? 'text-green-400' : 'text-gray-300'}
                `} />
              )}
            </React.Fragment>
          )
        })}
      </div>
    </div>
  )
}

// Predefined workflows for different agents
export const AGENT_WORKFLOWS = {
  order_fulfillment: [
    { id: 'receive', label: 'Receive Order', icon: 'receive', status: 'pending' },
    { id: 'check', label: 'Check Stock', icon: 'search', status: 'pending' },
    { id: 'allocate', label: 'Allocate', icon: 'check', status: 'pending' },
    { id: 'approval', label: 'Manager Approval', icon: 'approval', status: 'pending' },
    { id: 'pick', label: 'Pick Items', icon: 'process', status: 'pending' },
    { id: 'deliver', label: 'Deliver', icon: 'deliver', status: 'pending' },
  ],
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
  automotive_sales: [
    { id: 'greet', label: 'Greet', icon: 'receive', status: 'pending' },
    { id: 'understand', label: 'Understand Needs', icon: 'search', status: 'pending' },
    { id: 'recommend', label: 'Recommend', icon: 'generate', status: 'pending' },
    { id: 'schedule', label: 'Schedule', icon: 'check', status: 'pending' },
  ],
  compliance: [
    { id: 'receive', label: 'Receive Doc', icon: 'receive', status: 'pending' },
    { id: 'extract', label: 'Extract Rules', icon: 'extract', status: 'pending' },
    { id: 'compare', label: 'Compare SOPs', icon: 'search', status: 'pending' },
    { id: 'gaps', label: 'Find Gaps', icon: 'alert', status: 'pending' },
    { id: 'report', label: 'Report', icon: 'complete', status: 'pending' },
  ],
  voice_analytics: [
    { id: 'receive', label: 'Receive Recording', icon: 'receive', status: 'pending' },
    { id: 'transcribe', label: 'Transcribe Audio', icon: 'extract', status: 'pending' },
    { id: 'sentiment', label: 'Analyze Sentiment', icon: 'search', status: 'pending' },
    { id: 'insights', label: 'Generate Insights', icon: 'generate', status: 'pending' },
  ],
  customer_segmentation: [
    { id: 'load', label: 'Load Data', icon: 'receive', status: 'pending' },
    { id: 'rfm', label: 'Calculate RFM', icon: 'search', status: 'pending' },
    { id: 'ml', label: 'ML Prediction', icon: 'generate', status: 'pending' },
    { id: 'insights', label: 'Generate Insights', icon: 'complete', status: 'pending' },
  ],
}

export default WorkflowVisualizer

