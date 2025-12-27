import React from 'react'
import { Sparkles, Clock, Tag, Megaphone } from 'lucide-react'

function PromotionCard({ promotion, onSelect }) {
  return (
    <div 
      onClick={() => onSelect(promotion)}
      className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md hover:border-blue-300 cursor-pointer transition-all"
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-semibold text-gray-800">{promotion.name}</h4>
        <div 
          className="w-6 h-6 rounded-full" 
          style={{ background: `linear-gradient(135deg, ${promotion.colors[0]}, ${promotion.colors[1]})` }}
        />
      </div>
      
      <p className="text-sm text-gray-600 mb-3">{promotion.description}</p>
      
      <div className="flex flex-wrap gap-2 mb-3">
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
          <Tag className="w-3 h-3" />
          {promotion.discount}
        </span>
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-50 text-orange-700 text-xs rounded-full">
          <Clock className="w-3 h-3" />
          {promotion.duration}
        </span>
      </div>
      
      <div className="flex items-center gap-1 text-xs text-gray-500">
        <Megaphone className="w-3 h-3" />
        {promotion.channels.join(' • ')}
      </div>
    </div>
  )
}

export function PromotionSelector({ promotions, onSelect }) {
  return (
    <div className="bg-gray-50 rounded-xl p-4 mb-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-blue-600" />
        Suggested Promotion Templates
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {promotions.map(promo => (
          <PromotionCard key={promo.id} promotion={promo} onSelect={onSelect} />
        ))}
      </div>
    </div>
  )
}

export default PromotionCard

