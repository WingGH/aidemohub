import React from 'react'
import { Sparkles, Zap, Brain, Layers, ArrowRight } from 'lucide-react'

function WelcomePanel({ agents, onSelectAgent }) {
  const featuredAgents = agents.slice(0, 6)

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 overflow-y-auto bg-gradient-to-br from-surface-100 via-white to-blue-50">
      <div className="max-w-4xl w-full animate-fade-in">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-surface-200 shadow-soft mb-6">
            <Sparkles className="w-4 h-4 text-accent-blue" />
            <span className="text-sm text-surface-600">Enterprise AI Platform</span>
          </div>
          
          <h1 className="text-5xl font-bold mb-4">
            <span className="gradient-text">AI Hub</span>
          </h1>
          
          <p className="text-xl text-surface-600 max-w-2xl mx-auto">
            Experience the power of AI across multiple business domains. 
            Select a use case from the sidebar to start exploring.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-3 gap-4 mb-12">
          <FeatureCard
            icon={<Brain className="w-6 h-6" />}
            title="Agentic AI"
            description="Autonomous agents that handle complex multi-step workflows"
            gradient="from-purple-500 to-pink-500"
            bgColor="bg-purple-50"
          />
          <FeatureCard
            icon={<Zap className="w-6 h-6" />}
            title="Multimodal"
            description="Vision and text understanding for document and image analysis"
            gradient="from-cyan-500 to-blue-500"
            bgColor="bg-cyan-50"
          />
          <FeatureCard
            icon={<Layers className="w-6 h-6" />}
            title="Enterprise Ready"
            description="Modular architecture designed for business integration"
            gradient="from-orange-500 to-red-500"
            bgColor="bg-orange-50"
          />
        </div>

        {/* Quick Start Agents */}
        <div className="bg-white rounded-2xl p-6 border border-surface-200 shadow-soft">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-surface-900">Quick Start</h2>
            <span className="text-sm text-surface-500">{agents.length} use cases available</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {featuredAgents.map((agent, index) => (
              <button
                key={agent.id}
                onClick={() => onSelectAgent(agent)}
                className="
                  group p-4 rounded-xl
                  bg-surface-50 hover:bg-white
                  border border-surface-200 hover:border-accent-blue/30
                  hover:shadow-medium
                  transition-all duration-300
                  text-left
                "
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl group-hover:scale-110 transition-transform">
                    {agent.icon}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm text-surface-800 group-hover:text-accent-blue transition-colors flex items-center gap-1">
                      {agent.name}
                      <ArrowRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <div className="text-xs text-surface-500 mt-1 line-clamp-2">
                      {agent.description}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mt-8 flex items-center justify-center gap-4 text-sm text-surface-400">
          <span>Built with</span>
          <div className="flex items-center gap-3">
            <span className="px-2 py-1 rounded bg-surface-100 text-surface-600">LangGraph</span>
            <span className="px-2 py-1 rounded bg-surface-100 text-surface-600">FastAPI</span>
            <span className="px-2 py-1 rounded bg-surface-100 text-surface-600">React</span>
            <span className="px-2 py-1 rounded bg-surface-100 text-surface-600">OpenRouter</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description, gradient, bgColor }) {
  return (
    <div className={`${bgColor} rounded-xl p-5 border border-surface-200 group hover:shadow-medium transition-all duration-300`}>
      <div className={`
        w-12 h-12 rounded-xl mb-4
        bg-gradient-to-br ${gradient}
        flex items-center justify-center text-white
        group-hover:scale-110 transition-transform duration-300
        shadow-soft
      `}>
        {icon}
      </div>
      <h3 className="font-semibold text-surface-800 mb-2">{title}</h3>
      <p className="text-sm text-surface-500">{description}</p>
    </div>
  )
}

export default WelcomePanel
