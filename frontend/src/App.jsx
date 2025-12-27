import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'
import WelcomePanel from './components/WelcomePanel'
import UseCaseDetail from './components/UseCaseDetail'
import { fetchAgents } from './api'

function App() {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [conversations, setConversations] = useState({})
  const [loading, setLoading] = useState(true)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [viewMode, setViewMode] = useState('welcome') // 'welcome', 'detail', 'chat'

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const data = await fetchAgents()
      setAgents(data.agents)
    } catch (error) {
      console.error('Failed to load agents:', error)
      setAgents(getFallbackAgents())
    } finally {
      setLoading(false)
    }
  }

  const getFallbackAgents = () => [
    { id: "automotive_sales", name: "Automotive Sales Agent", description: "End-to-end customer journey for vehicle sales and service", icon: "🚗", category: "Automotive", features: ["Sales Inquiry", "Test Drive Booking", "Financing Options"] },
    { id: "damage_assessment", name: "Vehicle Damage Assessment", description: "Vision AI for analyzing vehicle damage and repair estimates", icon: "📸", category: "Automotive", features: ["Image Analysis", "Cost Estimation"], accepts_image: true },
    { id: "document_processing", name: "Document Processing", description: "Intelligent extraction from shipping documents and invoices", icon: "📄", category: "Logistics", features: ["OCR", "Multilingual"], accepts_image: true },
    { id: "marketing_content", name: "Marketing Content Studio", description: "AI-generated marketing content in multiple languages", icon: "✨", category: "Marketing", features: ["Ad Copy", "Social Media"] },
    { id: "compliance", name: "Compliance Copilot", description: "Healthcare regulatory compliance and SOP comparison", icon: "⚕️", category: "Healthcare", features: ["Gap Detection", "Risk Assessment"], accepts_image: true },
    { id: "sales_trainer", name: "Sales Trainer", description: "Role-play training scenarios for sales staff", icon: "🎭", category: "HR & Training", features: ["Role-Play", "Scoring"] },
    { id: "trend_spotter", name: "Trend Spotter", description: "Social media trend analysis and market insights", icon: "📈", category: "Marketing", features: ["Trend Analysis", "Insights"] },
    { id: "warranty_claims", name: "Warranty Claims", description: "Automated warranty claim processing with fraud detection", icon: "🛡️", category: "Customer Service", features: ["Verification", "Fraud Detection"], accepts_image: true },
    { id: "cross_selling", name: "Cross-Selling Intelligence", description: "Smart product recommendations and bundle offers", icon: "🛒", category: "Sales", features: ["Recommendations", "Bundles"] },
    { id: "order_fulfillment", name: "Order Fulfillment Agent", description: "Agentic order processing and warehouse management", icon: "📦", category: "Logistics", features: ["Order Processing", "Tracking"] },
  ]

  const handleSelectAgent = (agent) => {
    setSelectedAgent(agent)
    setViewMode('detail')
    // Initialize conversation for this agent if not exists
    if (!conversations[agent.id]) {
      setConversations(prev => ({
        ...prev,
        [agent.id]: []
      }))
    }
  }

  const handleStartChat = () => {
    setViewMode('chat')
  }

  const handleBackToList = () => {
    setSelectedAgent(null)
    setViewMode('welcome')
  }

  const handleBackToDetail = () => {
    setViewMode('detail')
  }

  const handleNewMessage = (agentId, messages) => {
    setConversations(prev => ({
      ...prev,
      [agentId]: messages
    }))
  }

  const handleClearConversation = (agentId) => {
    setConversations(prev => ({
      ...prev,
      [agentId]: []
    }))
  }

  const renderMainContent = () => {
    if (!selectedAgent) {
      return <WelcomePanel agents={agents} onSelectAgent={handleSelectAgent} />
    }

    if (viewMode === 'detail') {
      return (
        <UseCaseDetail 
          agent={selectedAgent}
          onBack={handleBackToList}
          onStartChat={handleStartChat}
        />
      )
    }

    return (
      <ChatPanel
        agent={selectedAgent}
        messages={conversations[selectedAgent.id] || []}
        onNewMessage={(messages) => handleNewMessage(selectedAgent.id, messages)}
        onClearConversation={() => handleClearConversation(selectedAgent.id)}
        onBackToDetail={handleBackToDetail}
      />
    )
  }

  return (
    <div className="flex h-screen bg-surface-100 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        agents={agents}
        selectedAgent={selectedAgent}
        onSelectAgent={handleSelectAgent}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        loading={loading}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative">
        {renderMainContent()}
      </main>
    </div>
  )
}

export default App
