const API_BASE = '/api'

export async function fetchAgents() {
  const response = await fetch(`${API_BASE}/agents`)
  if (!response.ok) throw new Error('Failed to fetch agents')
  return response.json()
}

export async function sendMessage(agentId, message, context = null, conversationHistory = null) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent_id: agentId,
      message,
      context,
      conversation_history: conversationHistory,
    }),
  })
  
  if (!response.ok) throw new Error('Failed to send message')
  return response.json()
}

export async function sendMessageStream(agentId, message, context = null, conversationHistory = null, onChunk) {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent_id: agentId,
      message,
      context,
      conversation_history: conversationHistory,
    }),
  })
  
  if (!response.ok) {
    // Fallback to non-streaming if streaming endpoint fails
    const fallbackResponse = await sendMessage(agentId, message, context, conversationHistory)
    onChunk(fallbackResponse.response)
    return fallbackResponse
  }
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    const chunk = decoder.decode(value, { stream: true })
    // Parse SSE format
    const lines = chunk.split('\n')
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') {
          return
        }
        try {
          const parsed = JSON.parse(data)
          if (parsed.content) {
            onChunk(parsed.content)
          }
        } catch (e) {
          // If it's not JSON, treat as raw text
          if (data.trim()) {
            onChunk(data)
          }
        }
      }
    }
  }
}

export async function sendMessageWithImage(agentId, message, imageFile, conversationHistory = null) {
  const formData = new FormData()
  formData.append('agent_id', agentId)
  formData.append('message', message)
  formData.append('image', imageFile)
  if (conversationHistory) {
    formData.append('conversation_history', JSON.stringify(conversationHistory))
  }

  const response = await fetch(`${API_BASE}/chat-with-image`, {
    method: 'POST',
    body: formData,
  })
  
  if (!response.ok) throw new Error('Failed to send message with image')
  return response.json()
}

export async function sendMessageWithImageStream(agentId, message, imageFile, onStepUpdate, onResponse, onApprovalRequired = null, conversationHistory = null) {
  const formData = new FormData()
  formData.append('agent_id', agentId)
  formData.append('message', message)
  formData.append('image', imageFile)
  if (conversationHistory) {
    formData.append('conversation_history', JSON.stringify(conversationHistory))
  }

  const response = await fetch(`${API_BASE}/chat-with-image/stream`, {
    method: 'POST',
    body: formData,
  })
  
  if (!response.ok) {
    // Fallback to non-streaming
    const fallbackResponse = await sendMessageWithImage(agentId, message, imageFile)
    if (fallbackResponse.workflow_steps) {
      onStepUpdate(fallbackResponse.workflow_steps)
    }
    onResponse(fallbackResponse.response)
    return fallbackResponse
  }
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    buffer += decoder.decode(value, { stream: true })
    
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') {
          return
        }
        try {
          const parsed = JSON.parse(data)
          if (parsed.type === 'workflow_step') {
            onStepUpdate(parsed.all_steps || [parsed.step])
          } else if (parsed.type === 'response') {
            onResponse(parsed.content)
          } else if (parsed.type === 'error') {
            onResponse(`❌ Error: ${parsed.content}`)
          } else if (parsed.type === 'approval_required' && onApprovalRequired) {
            // Human-in-the-loop approval required
            onStepUpdate(parsed.all_steps || [])
            onApprovalRequired(parsed)
          }
        } catch (e) {
          console.warn('Failed to parse SSE data:', data, e)
        }
      }
    }
  }
}

export async function sendMessageWithWorkflowStream(agentId, message, context = null, onStepUpdate, onResponse, onApprovalRequired = null, conversationHistory = null) {
  const response = await fetch(`${API_BASE}/chat/workflow-stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent_id: agentId,
      message,
      context,
      conversation_history: conversationHistory,
    }),
  })
  
  if (!response.ok) {
    // Fallback to non-streaming
    const fallbackResponse = await sendMessage(agentId, message, context)
    if (fallbackResponse.workflow_steps) {
      onStepUpdate(fallbackResponse.workflow_steps)
    }
    onResponse(fallbackResponse.response)
    return fallbackResponse
  }
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    buffer += decoder.decode(value, { stream: true })
    
    // Process complete lines
    const lines = buffer.split('\n')
    buffer = lines.pop() || '' // Keep incomplete line in buffer
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') {
          return
        }
        try {
          const parsed = JSON.parse(data)
          if (parsed.type === 'workflow_step') {
            // Send all steps to update the UI
            onStepUpdate(parsed.all_steps || [parsed.step])
          } else if (parsed.type === 'response') {
            onResponse(parsed.content)
          } else if (parsed.type === 'error') {
            onResponse(`❌ Error: ${parsed.content}`)
          } else if (parsed.type === 'approval_required' && onApprovalRequired) {
            // Human-in-the-loop approval required
            onStepUpdate(parsed.all_steps || [])
            onApprovalRequired(parsed)
          }
        } catch (e) {
          console.warn('Failed to parse SSE data:', data, e)
        }
      }
    }
  }
}

export async function getTrendsDashboard() {
  const response = await fetch(`${API_BASE}/trends/dashboard`)
  if (!response.ok) throw new Error('Failed to fetch trends')
  return response.json()
}

export async function getVehicles(brand = null) {
  const url = brand ? `${API_BASE}/vehicles?brand=${brand}` : `${API_BASE}/vehicles`
  const response = await fetch(url)
  if (!response.ok) throw new Error('Failed to fetch vehicles')
  return response.json()
}

export async function checkWarranty(serialNumber) {
  const response = await fetch(`${API_BASE}/warranty/${serialNumber}`)
  if (!response.ok) throw new Error('Failed to check warranty')
  return response.json()
}

export async function getTrainingScenarios() {
  const response = await fetch(`${API_BASE}/training/scenarios`)
  if (!response.ok) throw new Error('Failed to fetch scenarios')
  return response.json()
}

export async function processOrder(items, customerId = null) {
  const response = await fetch(`${API_BASE}/order/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      items,
      customer_id: customerId,
    }),
  })
  
  if (!response.ok) throw new Error('Failed to process order')
  return response.json()
}

export async function getCrossSellRecommendations(currentItems, customerId = null, domain = 'auto') {
  const response = await fetch(`${API_BASE}/cross-sell/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      current_items: currentItems,
      customer_id: customerId,
      domain,
    }),
  })
  
  if (!response.ok) throw new Error('Failed to get recommendations')
  return response.json()
}

export async function submitApprovalAndContinue(approvalId, approved, onStepUpdate, onResponse) {
  const response = await fetch(`${API_BASE}/approval/continue-stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      approval_id: approvalId,
      approved,
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to submit approval')
  }
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    buffer += decoder.decode(value, { stream: true })
    
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        if (data === '[DONE]') {
          return
        }
        try {
          const parsed = JSON.parse(data)
          if (parsed.type === 'workflow_step') {
            onStepUpdate(parsed.all_steps || [parsed.step])
          } else if (parsed.type === 'response') {
            onResponse(parsed.content)
          } else if (parsed.type === 'error') {
            onResponse(`❌ Error: ${parsed.content}`)
          }
        } catch (e) {
          console.warn('Failed to parse SSE data:', data, e)
        }
      }
    }
  }
}
