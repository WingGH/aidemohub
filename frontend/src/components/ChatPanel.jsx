import React, { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { 
  Send, 
  Image as ImageIcon, 
  Trash2, 
  Loader2,
  User,
  Bot,
  Lightbulb,
  X,
  ArrowLeft,
  Info,
  Sparkles
} from 'lucide-react'
import { sendMessage, sendMessageWithImage, sendMessageWithImageStream, sendMessageWithWorkflowStream, submitApprovalAndContinue } from '../api'
import WorkflowVisualizer, { AGENT_WORKFLOWS } from './WorkflowVisualizer'
import { WORKFLOW_AGENTS } from '../hooks/useWorkflow'
import { PromotionSelector } from './PromotionCard'
import GeneratedImage from './GeneratedImage'

// Promotion templates for marketing
const PROMOTIONS = [
  {
    id: "summer_sale",
    name: "Summer Sale Campaign",
    description: "Hot summer deals with urgency messaging",
    discount: "Up to 30% off",
    duration: "Limited time",
    channels: ["Instagram", "Facebook", "Email"],
    tone: "Exciting and urgent",
    cta: "Shop Now",
    colors: ["#FF6B35", "#F7C59F", "#EFEFEF"]
  },
  {
    id: "new_arrival",
    name: "New Arrival Launch",
    description: "Exclusive first-look at new products",
    discount: "Early bird 15% off",
    duration: "First 48 hours",
    channels: ["Instagram Stories", "WeChat", "SMS"],
    tone: "Exclusive and premium",
    cta: "Be First",
    colors: ["#2D3047", "#93B7BE", "#E0CA3C"]
  },
  {
    id: "flash_sale",
    name: "Flash Sale",
    description: "24-hour mega savings event",
    discount: "50% off selected items",
    duration: "24 hours only",
    channels: ["Push Notification", "Email", "Social"],
    tone: "Urgent and exciting",
    cta: "Grab It Now",
    colors: ["#E63946", "#F1FAEE", "#1D3557"]
  },
  {
    id: "korean_food",
    name: "K-Food Festival",
    description: "Korean food trends celebration",
    discount: "Buy 2 Get 1 Free",
    duration: "This weekend",
    channels: ["Instagram", "Xiaohongshu", "TikTok"],
    tone: "Fun and trendy",
    cta: "Join the Trend",
    colors: ["#E94560", "#0F3460", "#16213E"]
  }
]

// Demo images for marketing content
const DEMO_IMAGES = {
  car: { url: "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=600", alt_text: "Luxury car", suggested_placement: "hero" },
  food: { url: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600", alt_text: "Delicious food", suggested_placement: "hero" },
  korean: { url: "https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=600", alt_text: "Korean cuisine", suggested_placement: "banner" },
  sale: { url: "https://images.unsplash.com/photo-1607083206869-4c7672e72a8a?w=600", alt_text: "Sale promotion", suggested_placement: "hero" },
  organic: { url: "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600", alt_text: "Organic products", suggested_placement: "hero" },
  default: { url: "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=600", alt_text: "Marketing visual", suggested_placement: "banner" }
}

const agentPrompts = {
  automotive_sales: [
    "Show me available vehicles under $50,000",
    "I want to schedule a test drive for the BMW 3 Series",
    "What financing options do you offer for a 5-year term?",
    "I need to book a brake service for my Toyota"
  ],
  damage_assessment: [
    "What types of damage can you assess?",
    "How does the damage assessment process work?",
    "Can you estimate repair costs for a dented fender?"
  ],
  document_processing: [
    "What types of documents can you process?",
    "Can you extract data from Chinese documents?",
    "How do you handle handwritten notes?"
  ],
  marketing_content: [
    "Create a social media post for our new electric vehicle launch",
    "Write ad copy for a summer sale promotion",
    "Generate a video script for our organic food product",
    "Create Instagram captions for our Korean food products"
  ],
  compliance: [
    "What SOPs do we currently have in place?",
    "How do I check if we're compliant with new regulations?",
    "What are the key areas for pharmaceutical storage compliance?"
  ],
  sales_trainer: [
    "Start a new training scenario",
    "Practice handling price objections",
    "Give me a difficult customer to practice with"
  ],
  trend_spotter: [
    "Show me the trends dashboard",
    "What's trending on Hong Kong social media right now?",
    "Which Korean food trends should we capitalize on?",
    "Find suppliers for trending organic products"
  ],
  warranty_claims: [
    "Process a warranty claim for serial number SN-12345678",
    "Check warranty status for SN-87654321",
    "Process claim for expired product SN-11111111",
    "What fraud indicators do you look for?"
  ],
  cross_selling: [
    "I'm buying brake pads, what else do I need?",
    "Recommend products for a customer who only buys beverages",
    "Create a bundle offer for an oil change service"
  ],
  order_fulfillment: [
    "Process an order for 100 units of Oat Milk",
    "Process order for 50 Korean Tteokbokki and 75 Green Tea",
    "Check inventory for SKU001 across all warehouses",
    "How does the fulfillment workflow work?"
  ],
  voice_analytics: [
    "Show me all calls overview",
    "Analyze call CALL-001",
    "Show me calls about product returns",
    "What's the average sentiment score?"
  ],
  customer_segmentation: [
    "Show all customers overview",
    "Analyze customer Alice Chan",
    "Show customers in the At Risk segment",
    "What is RFM analysis?"
  ]
}

// WORKFLOW_AGENTS is now imported from '../hooks/useWorkflow'
// This makes it easier to maintain workflow agent list in one place

function ChatPanel({ agent, messages, onNewMessage, onClearConversation, onBackToDetail }) {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [workflowSteps, setWorkflowSteps] = useState([])
  const [showPromotions, setShowPromotions] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [pendingApproval, setPendingApproval] = useState(null) // Human-in-the-loop approval
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    inputRef.current?.focus()
    // Show promotions for marketing agent on first load
    if (agent.id === 'marketing_content' && messages.length === 0) {
      setShowPromotions(true)
    } else {
      setShowPromotions(false)
    }
    // Clear workflow when switching agents
    setWorkflowSteps([])
    setGeneratedImage(null)
    setPendingApproval(null)
  }, [agent.id])

  const getRelevantImage = (content) => {
    const lowerContent = content.toLowerCase()
    if (lowerContent.includes('korean') || lowerContent.includes('k-food')) return DEMO_IMAGES.korean
    if (lowerContent.includes('car') || lowerContent.includes('vehicle') || lowerContent.includes('electric')) return DEMO_IMAGES.car
    if (lowerContent.includes('food') || lowerContent.includes('organic')) return DEMO_IMAGES.food
    if (lowerContent.includes('sale') || lowerContent.includes('discount')) return DEMO_IMAGES.sale
    return DEMO_IMAGES.default
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() && !imageFile) return

    const userMessage = { role: 'user', content: input, image: imagePreview }
    const newMessages = [...messages, userMessage]
    onNewMessage(newMessages)
    
    const currentInput = input
    setInput('')
    setIsLoading(true)
    setShowPromotions(false)

    // Clear workflow steps at start - let backend drive the workflow visualization
    // This fixes the issue where follow-up queries show stuck "pending" steps
    setWorkflowSteps([])

    try {
      let response
      if (imageFile && WORKFLOW_AGENTS.includes(agent.id)) {
        // Use streaming for image uploads with workflow agents
        // Build conversation history for context
        const conversationHistory = messages.map(m => ({
          role: m.role,
          content: m.content
        }))
        
        await sendMessageWithImageStream(
          agent.id,
          currentInput || 'Analyze this image',
          imageFile,
          (steps) => {
            setWorkflowSteps(steps.map(s => ({
              id: s.step,
              label: s.label,
              status: s.status,
              icon: s.step
            })))
          },
          (content) => {
            const assistantMessage = { role: 'assistant', content }
            onNewMessage([...newMessages, assistantMessage])
          },
          conversationHistory
        )
      } else if (imageFile) {
        // Non-workflow agents with images
        const conversationHistory = messages.map(m => ({
          role: m.role,
          content: m.content
        }))
        response = await sendMessageWithImage(agent.id, currentInput || 'Analyze this image', imageFile, conversationHistory)
        const assistantMessage = { role: 'assistant', content: response.response }
        onNewMessage([...newMessages, assistantMessage])
      } else if (WORKFLOW_AGENTS.includes(agent.id)) {
        // Use streaming workflow for agentic agents
        // Build conversation history for context
        const conversationHistory = messages.map(m => ({
          role: m.role,
          content: m.content
        }))
        
        await sendMessageWithWorkflowStream(
          agent.id,
          currentInput,
          null,
          // onStepUpdate - called each time a step changes
          (steps) => {
            setWorkflowSteps(steps.map(s => ({
              id: s.step,
              label: s.label,
              status: s.status,
              icon: s.step
            })))
          },
          // onResponse - called when final response is ready
          (content) => {
            const assistantMessage = { role: 'assistant', content }
            onNewMessage([...newMessages, assistantMessage])
          },
          // onApprovalRequired - called when human approval is needed
          (approvalData) => {
            setPendingApproval(approvalData)
            setIsLoading(false)
          },
          // Pass conversation history for multi-turn context
          conversationHistory
        )
      } else {
        // Regular non-workflow agents
        const conversationHistory = messages.map(m => ({
          role: m.role,
          content: m.content
        }))
        response = await sendMessage(agent.id, currentInput, null, conversationHistory)
        const assistantMessage = { role: 'assistant', content: response.response }
        onNewMessage([...newMessages, assistantMessage])
      }

      // Generate image for marketing content
      if (agent.id === 'marketing_content') {
        setGeneratedImage(getRelevantImage(currentInput))
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setWorkflowSteps([])
      const errorMessage = { 
        role: 'assistant', 
        content: '❌ Sorry, there was an error processing your request. Please make sure the backend server is running on port 8000.' 
      }
      onNewMessage([...newMessages, errorMessage])
    } finally {
      setIsLoading(false)
      setImageFile(null)
      setImagePreview(null)
    }
  }

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handlePromptClick = (prompt) => {
    setInput(prompt)
    inputRef.current?.focus()
  }

  const handlePromotionSelect = (promotion) => {
    const prompt = `Create marketing content for a "${promotion.name}" campaign. 
Details:
- Discount: ${promotion.discount}
- Duration: ${promotion.duration}
- Channels: ${promotion.channels.join(', ')}
- Tone: ${promotion.tone}
- CTA: ${promotion.cta}

Please generate engaging copy for all specified channels.`
    setInput(prompt)
    setShowPromotions(false)
    inputRef.current?.focus()
  }

  const handleClearConversation = () => {
    setWorkflowSteps([])
    setGeneratedImage(null)
    setPendingApproval(null)
    onClearConversation()
  }

  const handleApprovalDecision = async (approved) => {
    if (!pendingApproval) return
    
    setIsLoading(true)
    const approvalData = pendingApproval
    setPendingApproval(null)
    
    try {
      await submitApprovalAndContinue(
        approvalData.approval_id,
        approved,
        // onStepUpdate
        (steps) => {
          setWorkflowSteps(steps.map(s => ({
            id: s.step,
            label: s.label,
            status: s.status,
            icon: s.step
          })))
        },
        // onResponse
        (content) => {
          const assistantMessage = { role: 'assistant', content }
          onNewMessage([...messages, assistantMessage])
        }
      )
    } catch (error) {
      console.error('Error submitting approval:', error)
      const errorMessage = { 
        role: 'assistant', 
        content: '❌ Failed to process approval decision. Please try again.' 
      }
      onNewMessage([...messages, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const prompts = agentPrompts[agent.id] || []
  const hasWorkflow = WORKFLOW_AGENTS.includes(agent.id)

  return (
    <div className="flex-1 flex flex-col h-full bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBackToDetail}
              className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
              title="Back to details"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div className="text-3xl">{agent.icon}</div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{agent.name}</h2>
              <p className="text-sm text-gray-500">{agent.category}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {hasWorkflow && (
              <span className="px-3 py-1 rounded-full text-xs bg-blue-50 text-blue-700 border border-blue-200">
                ⚡ Agentic Workflow
              </span>
            )}
            {agent.accepts_image && (
              <span className="px-3 py-1 rounded-full text-xs bg-purple-50 text-purple-700 border border-purple-200">
                📷 Vision
              </span>
            )}
            {agent.id === 'marketing_content' && (
              <span className="px-3 py-1 rounded-full text-xs bg-pink-50 text-pink-700 border border-pink-200">
                🎨 Image Gen
              </span>
            )}
            <button
              onClick={onBackToDetail}
              className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
              title="View use case details"
            >
              <Info className="w-4 h-4" />
            </button>
            <button
              onClick={handleClearConversation}
              className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-red-600 transition-colors"
              title="Clear conversation"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Persistent Workflow Visualizer - Shows when there are steps */}
      {workflowSteps.length > 0 && (
        <div className="px-6 pt-4">
          <WorkflowVisualizer 
            steps={workflowSteps} 
            currentStep={workflowSteps.find(s => s.status === 'active')?.id}
            title={`${agent.name} Workflow`}
          />
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center animate-fade-in">
            <div className="text-6xl mb-4">{agent.icon}</div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">Start a conversation</h3>
            <p className="text-gray-500 max-w-md mb-6">
              {agent.description}
            </p>

            {/* Show promotion templates for marketing */}
            {showPromotions && (
              <div className="w-full max-w-2xl mb-6">
                <PromotionSelector 
                  promotions={PROMOTIONS} 
                  onSelect={handlePromotionSelect} 
                />
              </div>
            )}
            
            {prompts.length > 0 && (
              <div className="w-full max-w-lg">
                <div className="flex items-center gap-2 mb-3 text-sm text-gray-500">
                  <Lightbulb className="w-4 h-4 text-amber-500" />
                  <span>{showPromotions ? 'Or try these prompts:' : 'Try these prompts:'}</span>
                </div>
                <div className="grid gap-2">
                  {prompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => handlePromptClick(prompt)}
                      className="
                        px-4 py-3 rounded-xl text-left
                        bg-white hover:bg-gray-50
                        border border-gray-200 hover:border-blue-300
                        text-sm text-gray-700 hover:text-gray-900
                        shadow-sm hover:shadow-md
                        transition-all duration-200
                      "
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageBubble key={index} message={message} />
            ))}

            {/* Generated Image for Marketing */}
            {generatedImage && agent.id === 'marketing_content' && !isLoading && (
              <div className="ml-11">
                <GeneratedImage 
                  imageData={generatedImage}
                  onRegenerate={() => setGeneratedImage(getRelevantImage(messages[messages.length - 1]?.content || ''))}
                />
              </div>
            )}

            {isLoading && !pendingApproval && (
              <div className="flex items-start gap-3 animate-fade-in">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white rounded-2xl rounded-tl-md px-4 py-3 border border-gray-200 shadow-sm">
                  <div className="flex items-center gap-2 text-gray-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>{hasWorkflow ? 'Executing workflow...' : 'Processing...'}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Human-in-the-Loop Approval Dialog */}
            {pendingApproval && (
              <div className="flex items-start gap-3 animate-fade-in">
                <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="max-w-md bg-white rounded-2xl rounded-tl-md border-2 border-amber-400 shadow-lg overflow-hidden">
                  <div className="bg-amber-50 px-4 py-3 border-b border-amber-200">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">🧑‍💼</span>
                      <span className="font-semibold text-amber-800">{pendingApproval.title}</span>
                    </div>
                  </div>
                  <div className="p-4">
                    <p className="text-gray-700 text-sm mb-4">{pendingApproval.message}</p>
                    
                    {pendingApproval.details && (
                      <div className="bg-gray-50 rounded-lg p-3 mb-4 text-sm">
                        <div className="grid gap-2">
                          <div className="flex justify-between">
                            <span className="text-gray-500">Order ID:</span>
                            <span className="font-medium text-gray-800">{pendingApproval.details.order_id}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Total Items:</span>
                            <span className="font-medium text-gray-800">{pendingApproval.details.total_items}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Est. Value:</span>
                            <span className="font-medium text-green-600">{pendingApproval.details.estimated_value}</span>
                          </div>
                          {pendingApproval.details.items_summary && (
                            <div className="mt-2 pt-2 border-t border-gray-200">
                              <span className="text-gray-500 text-xs">Items:</span>
                              <ul className="mt-1 text-xs text-gray-700">
                                {pendingApproval.details.items_summary.map((item, i) => (
                                  <li key={i}>• {item}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex gap-3">
                      <button
                        onClick={() => handleApprovalDecision(true)}
                        className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
                      >
                        ✓ Approve
                      </button>
                      <button
                        onClick={() => handleApprovalDecision(false)}
                        className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
                      >
                        ✗ Reject
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Image Preview */}
      {imagePreview && (
        <div className="px-6 py-3 border-t border-gray-200 bg-white">
          <div className="flex items-center gap-3">
            <div className="relative inline-block">
              <img 
                src={imagePreview} 
                alt="Upload preview" 
                className="h-20 rounded-lg object-cover border border-gray-200"
              />
              <button
                onClick={() => { setImageFile(null); setImagePreview(null) }}
                className="absolute -top-2 -right-2 p-1 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors shadow-sm"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
            {agent.id === 'marketing_content' && (
              <div className="text-sm text-gray-500">
                <span className="font-medium text-gray-700">📎 Reference image</span>
                <p className="text-xs">This image will be used as style reference</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-6 border-t border-gray-200 bg-white">
        <form onSubmit={handleSubmit} className="flex items-end gap-3">
          {(agent.accepts_image || agent.id === 'marketing_content') && (
            <>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageSelect}
                accept="image/*"
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="
                  p-3 rounded-xl
                  bg-gray-100 hover:bg-gray-200
                  border border-gray-200 hover:border-purple-300
                  text-gray-500 hover:text-purple-600
                  transition-all duration-200
                "
                title={agent.id === 'marketing_content' ? 'Add reference image' : 'Upload image'}
              >
                <ImageIcon className="w-5 h-5" />
              </button>
            </>
          )}
          
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Message ${agent.name}...`}
              className="
                w-full px-4 py-3 pr-12
                bg-gray-50 
                border border-gray-200 focus:border-blue-500
                rounded-xl
                text-gray-900 placeholder-gray-400
                focus:outline-none focus:ring-2 focus:ring-blue-500/20
                transition-all duration-200
              "
              disabled={isLoading}
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading || (!input.trim() && !imageFile)}
            className="
              p-3 rounded-xl
              bg-blue-600 hover:bg-blue-700
              shadow-md hover:shadow-lg
              disabled:opacity-50 disabled:cursor-not-allowed
              text-white font-medium
              transition-all duration-200
            "
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex items-start gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`
        w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0
        ${isUser 
          ? 'bg-gray-200' 
          : 'bg-blue-600'
        }
      `}>
        {isUser ? (
          <User className="w-4 h-4 text-gray-600" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>
      
      <div className={`
        max-w-[75%] rounded-2xl px-4 py-3 shadow-sm
        ${isUser 
          ? 'bg-blue-600 text-white rounded-tr-md' 
          : 'bg-white border border-gray-200 rounded-tl-md'
        }
      `}>
        {message.image && (
          <img 
            src={message.image} 
            alt="User uploaded" 
            className="max-h-48 rounded-lg mb-2 object-cover"
          />
        )}
        <div className={`message-content text-sm ${isUser ? 'text-white' : 'text-gray-700'}`}>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}

export default ChatPanel
