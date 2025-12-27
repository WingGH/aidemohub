/**
 * useWorkflow Hook
 * 
 * A reusable hook for managing workflow state in agentic AI demos.
 * This hook provides state management for step-by-step workflow visualization.
 * 
 * Usage:
 * ```jsx
 * import { useWorkflow } from '../hooks/useWorkflow'
 * import { AGENT_WORKFLOWS } from '../components/WorkflowVisualizer'
 * 
 * function MyComponent({ agentId }) {
 *   const { 
 *     steps, 
 *     updateSteps, 
 *     resetWorkflow, 
 *     initWorkflow,
 *     hasWorkflow 
 *   } = useWorkflow(agentId)
 *   
 *   // Initialize workflow when agent changes
 *   useEffect(() => {
 *     initWorkflow(agentId)
 *   }, [agentId])
 *   
 *   // Update steps from streaming API
 *   const handleStepUpdate = (newSteps) => {
 *     updateSteps(newSteps)
 *   }
 * }
 * ```
 */

import { useState, useCallback } from 'react'
import { AGENT_WORKFLOWS } from '../components/WorkflowVisualizer'

/**
 * List of agent IDs that have workflow visualization
 * Add new agentic agents here to enable workflow display
 */
export const WORKFLOW_AGENTS = [
  'order_fulfillment',
  'warranty_claims', 
  'document_processing',
  'marketing_content',
  'automotive_sales',
  'compliance'
]

/**
 * Hook for managing workflow state
 * @param {string} agentId - The agent identifier
 * @returns {Object} Workflow state and methods
 */
export function useWorkflow(agentId) {
  const [steps, setSteps] = useState([])
  
  /**
   * Check if agent has workflow visualization
   */
  const hasWorkflow = WORKFLOW_AGENTS.includes(agentId)
  
  /**
   * Initialize workflow with default steps for an agent
   */
  const initWorkflow = useCallback((id) => {
    if (AGENT_WORKFLOWS[id]) {
      setSteps(AGENT_WORKFLOWS[id].map(step => ({ ...step, status: 'pending' })))
    } else {
      setSteps([])
    }
  }, [])
  
  /**
   * Update steps from backend streaming response
   * Expects array of steps with { step, label, status } format
   */
  const updateSteps = useCallback((newSteps) => {
    if (!newSteps || newSteps.length === 0) return
    
    setSteps(newSteps.map(s => ({
      id: s.step,
      label: s.label,
      status: s.status,
      icon: s.step
    })))
  }, [])
  
  /**
   * Reset workflow to initial pending state
   */
  const resetWorkflow = useCallback(() => {
    if (agentId && AGENT_WORKFLOWS[agentId]) {
      setSteps(AGENT_WORKFLOWS[agentId].map(step => ({ ...step, status: 'pending' })))
    } else {
      setSteps([])
    }
  }, [agentId])
  
  /**
   * Clear all workflow steps
   */
  const clearWorkflow = useCallback(() => {
    setSteps([])
  }, [])
  
  /**
   * Get the title for workflow display based on agent
   */
  const getWorkflowTitle = useCallback((id) => {
    const titles = {
      order_fulfillment: 'Order Fulfillment Workflow',
      warranty_claims: 'Warranty Claims Workflow',
      document_processing: 'Document Processing Workflow',
      marketing_content: 'Marketing Content Studio Workflow',
      automotive_sales: 'Automotive Sales Workflow',
      compliance: 'Compliance Copilot Workflow'
    }
    return titles[id] || 'Workflow Progress'
  }, [])

  return {
    steps,
    setSteps,
    updateSteps,
    resetWorkflow,
    clearWorkflow,
    initWorkflow,
    hasWorkflow,
    getWorkflowTitle
  }
}

export default useWorkflow

