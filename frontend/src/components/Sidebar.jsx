import React, { useState } from 'react'
import { 
  ChevronLeft, 
  ChevronRight, 
  Sparkles,
  Layers
} from 'lucide-react'

const categoryColors = {
  'Automotive': 'from-orange-500 to-red-500',
  'Logistics': 'from-blue-500 to-cyan-500',
  'Marketing': 'from-pink-500 to-purple-500',
  'Healthcare': 'from-green-500 to-emerald-500',
  'HR & Training': 'from-yellow-500 to-orange-500',
  'Customer Service': 'from-indigo-500 to-blue-500',
  'Sales': 'from-purple-500 to-pink-500',
  'Finance': 'from-emerald-500 to-teal-500',
  'Analytics': 'from-violet-500 to-purple-500',
}

const categoryBgColors = {
  'Automotive': 'bg-orange-50 border-orange-200 hover:bg-orange-100',
  'Logistics': 'bg-blue-50 border-blue-200 hover:bg-blue-100',
  'Marketing': 'bg-pink-50 border-pink-200 hover:bg-pink-100',
  'Healthcare': 'bg-green-50 border-green-200 hover:bg-green-100',
  'HR & Training': 'bg-yellow-50 border-yellow-200 hover:bg-yellow-100',
  'Customer Service': 'bg-indigo-50 border-indigo-200 hover:bg-indigo-100',
  'Sales': 'bg-purple-50 border-purple-200 hover:bg-purple-100',
  'Finance': 'bg-emerald-50 border-emerald-200 hover:bg-emerald-100',
  'Analytics': 'bg-violet-50 border-violet-200 hover:bg-violet-100',
}

function Sidebar({ agents, selectedAgent, onSelectAgent, collapsed, onToggleCollapse, loading }) {
  const [filterCategory, setFilterCategory] = useState('All')
  
  const categories = ['All', ...new Set(agents.map(a => a.category))]
  
  const filteredAgents = filterCategory === 'All' 
    ? agents 
    : agents.filter(a => a.category === filterCategory)

  const groupedAgents = filteredAgents.reduce((acc, agent) => {
    const cat = agent.category
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(agent)
    return acc
  }, {})

  return (
    <aside 
      className={`
        ${collapsed ? 'w-20' : 'w-80'} 
        h-full flex flex-col
        bg-white border-r border-surface-300
        transition-all duration-300 ease-in-out
        relative z-20
      `}
    >
      {/* Header */}
      <div className="p-4 border-b border-surface-200">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center shadow-soft">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-surface-900">AI Hub</h1>
                <p className="text-xs text-surface-500">Enterprise AI Demos</p>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="w-10 h-10 mx-auto rounded-xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center shadow-soft">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
          )}
          <button
            onClick={onToggleCollapse}
            className="p-2 rounded-lg hover:bg-surface-100 text-surface-500 hover:text-surface-700 transition-colors"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Category Filter */}
      {!collapsed && (
        <div className="p-3 border-b border-surface-200">
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`
                  px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap
                  transition-all duration-200 border
                  ${filterCategory === cat 
                    ? 'bg-accent-blue text-white border-accent-blue shadow-soft' 
                    : 'bg-surface-100 text-surface-600 hover:bg-surface-200 border-surface-200'
                  }
                `}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin w-6 h-6 border-2 border-accent-blue border-t-transparent rounded-full" />
          </div>
        ) : (
          Object.entries(groupedAgents).map(([category, categoryAgents]) => (
            <div key={category} className="space-y-2">
              {!collapsed && (
                <div className="flex items-center gap-2 px-2">
                  <Layers className="w-3 h-3 text-surface-400" />
                  <span className="text-xs font-medium text-surface-500 uppercase tracking-wider">
                    {category}
                  </span>
                </div>
              )}
              <div className="space-y-1">
                {categoryAgents.map(agent => (
                  <AgentItem
                    key={agent.id}
                    agent={agent}
                    isSelected={selectedAgent?.id === agent.id}
                    onClick={() => onSelectAgent(agent)}
                    collapsed={collapsed}
                    categoryColor={categoryColors[agent.category] || 'from-gray-500 to-gray-600'}
                    categoryBgColor={categoryBgColors[agent.category] || 'bg-gray-50 border-gray-200 hover:bg-gray-100'}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-surface-200">
          <div className="text-xs text-surface-400 text-center">
            Powered by LangGraph + OpenRouter
          </div>
        </div>
      )}
    </aside>
  )
}

function AgentItem({ agent, isSelected, onClick, collapsed, categoryColor, categoryBgColor }) {
  return (
    <button
      onClick={onClick}
      className={`
        w-full rounded-xl transition-all duration-200 border
        ${collapsed ? 'p-2' : 'p-3'}
        ${isSelected 
          ? `bg-gradient-to-r ${categoryColor} text-white shadow-medium border-transparent` 
          : `${categoryBgColor}`
        }
      `}
      title={collapsed ? agent.name : undefined}
    >
      <div className={`flex items-center ${collapsed ? 'justify-center' : 'gap-3'}`}>
        <span className="text-2xl">{agent.icon}</span>
        {!collapsed && (
          <div className="flex-1 text-left">
            <div className={`font-medium text-sm ${isSelected ? 'text-white' : 'text-surface-800'}`}>
              {agent.name}
            </div>
            <div className={`text-xs mt-0.5 line-clamp-1 ${isSelected ? 'text-white/80' : 'text-surface-500'}`}>
              {agent.description}
            </div>
          </div>
        )}
      </div>
      {!collapsed && agent.accepts_image && (
        <div className="mt-2 flex gap-1">
          <span className={`
            text-[10px] px-2 py-0.5 rounded-full
            ${isSelected ? 'bg-white/20 text-white' : 'bg-white text-surface-600 border border-surface-200'}
          `}>
            📷 Vision
          </span>
        </div>
      )}
    </button>
  )
}

export default Sidebar
