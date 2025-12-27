import React, { useState } from 'react'
import { Image, Download, RefreshCw, ZoomIn, X } from 'lucide-react'

function GeneratedImage({ imageData, onRegenerate }) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  if (!imageData) return null

  return (
    <>
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-4 max-w-xl">
        <div className="relative">
          <img 
            src={imageData.url} 
            alt={imageData.alt_text || 'Generated marketing image'}
            className="w-full object-contain max-h-96 cursor-pointer hover:opacity-95 transition-opacity"
            onClick={() => setIsExpanded(true)}
          />
          <div className="absolute top-2 right-2 flex gap-2">
            <button 
              onClick={() => setIsExpanded(true)}
              className="p-2 bg-white/90 rounded-lg hover:bg-white shadow-sm transition-all"
              title="View full size"
            >
              <ZoomIn className="w-4 h-4 text-gray-600" />
            </button>
            <button 
              onClick={onRegenerate}
              className="p-2 bg-white/90 rounded-lg hover:bg-white shadow-sm transition-all"
              title="Generate new image"
            >
              <RefreshCw className="w-4 h-4 text-gray-600" />
            </button>
            <a 
              href={imageData.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="p-2 bg-white/90 rounded-lg hover:bg-white shadow-sm transition-all"
              title="Download image"
            >
              <Download className="w-4 h-4 text-gray-600" />
            </a>
          </div>
        </div>
        <div className="p-3 bg-gray-50">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Image className="w-3 h-3" />
            <span>Suggested placement: <strong>{imageData.suggested_placement}</strong></span>
          </div>
          {imageData.prompt && (
            <p className="text-xs text-gray-400 mt-1 line-clamp-2">
              Prompt: {imageData.prompt}
            </p>
          )}
        </div>
      </div>

      {/* Fullscreen Modal */}
      {isExpanded && (
        <div 
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
          onClick={() => setIsExpanded(false)}
        >
          <button 
            className="absolute top-4 right-4 p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-all"
            onClick={() => setIsExpanded(false)}
          >
            <X className="w-6 h-6 text-white" />
          </button>
          <img 
            src={imageData.url} 
            alt={imageData.alt_text || 'Generated marketing image'}
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  )
}

export default GeneratedImage

