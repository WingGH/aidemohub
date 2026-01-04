"""Voice Analytics Agent - Customer service call sentiment analysis."""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent, AgentState
from app.data.mock_data import MockDataStore
import asyncio

# Delay between workflow steps
STEP_DELAY = 1.0


class VoiceAnalyticsAgent(BaseAgent):
    """Agent for analyzing customer service call recordings."""
    
    def __init__(self):
        super().__init__(
            name="Voice Analytics Agent",
            description="Analyzes customer service calls for sentiment and insights"
        )
    
    def get_system_prompt(self) -> str:
        return """You are an expert voice analytics AI assistant specialized in customer service analysis.

Your capabilities include:
- Analyzing call transcripts for sentiment and emotion
- Identifying customer pain points and satisfaction drivers
- Evaluating agent performance and communication quality
- Tracking sentiment changes throughout conversations
- Providing actionable insights for service improvement

When analyzing calls, provide:
1. **Overall Sentiment Score**: 0-100 scale
2. **Sentiment Journey**: How sentiment changed during the call
3. **Key Moments**: Critical points that influenced the outcome
4. **Agent Performance**: Communication skills assessment
5. **Customer Insights**: Pain points, preferences, recommendations
6. **Action Items**: Specific improvements for training

Be specific with timestamps and quotes from the transcript."""

    def analyze_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a call recording with sentiment scoring."""
        transcript = call_data.get("transcript", [])
        
        # Simulate sentiment analysis
        sentiment_labels = {
            "very_positive": 1.0,
            "positive": 0.75,
            "neutral": 0.5,
            "negative": 0.25,
            "very_negative": 0.0
        }
        
        journey = call_data.get("sentiment_journey", [])
        journey_scores = [sentiment_labels.get(s, 0.5) for s in journey]
        
        # Find key moments
        key_moments = []
        for i, line in enumerate(transcript):
            text_lower = line["text"].lower()
            if any(word in text_lower for word in ["frustrated", "angry", "upset", "fed up"]):
                key_moments.append({
                    "timestamp": line["timestamp"],
                    "type": "negative_peak",
                    "text": line["text"][:50] + "...",
                    "speaker": line["speaker"]
                })
            elif any(word in text_lower for word in ["thank", "great", "wonderful", "appreciate", "helpful"]):
                key_moments.append({
                    "timestamp": line["timestamp"],
                    "type": "positive_peak",
                    "text": line["text"][:50] + "...",
                    "speaker": line["speaker"]
                })
        
        return {
            "call_id": call_data["id"],
            "overall_sentiment": call_data.get("sentiment_score", 0.5),
            "sentiment_journey": journey_scores,
            "key_moments": key_moments,
            "resolution": call_data.get("resolution"),
            "csat_score": call_data.get("csat_score"),
            "agent": call_data.get("agent"),
            "topic": call_data.get("topic"),
            "duration": call_data.get("duration")
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the voice analytics workflow."""
        
        async def analyze_voice(state: AgentState) -> AgentState:
            """Analyze voice/call data."""
            user_input = state["messages"][-1]["content"].lower()
            
            # Check if user wants to analyze a specific call
            call_id = None
            for call in MockDataStore.CALL_RECORDINGS:
                if call["id"].lower() in user_input:
                    call_id = call["id"]
                    break
            
            # Check for topic-based search
            topic_filter = None
            for topic in ["return", "billing", "inquiry", "cancel"]:
                if topic in user_input:
                    topic_filter = topic
                    break
            
            if "all calls" in user_input or "overview" in user_input or "dashboard" in user_input:
                # Show all calls summary
                calls = MockDataStore.get_call_recordings()
                analysis_results = [self.analyze_call(call) for call in calls]
                
                avg_sentiment = sum(r["overall_sentiment"] for r in analysis_results) / len(analysis_results)
                avg_csat = sum(r["csat_score"] for r in analysis_results) / len(analysis_results)
                
                response_parts = [
                    "## 🎙️ Voice Analytics Dashboard\n",
                    f"**Total Calls Analyzed:** {len(calls)}",
                    f"**Average Sentiment Score:** {avg_sentiment:.0%}",
                    f"**Average CSAT Score:** {avg_csat:.1f}/5\n",
                    "### Call Summary:\n"
                ]
                
                for result in analysis_results:
                    sentiment_emoji = "🟢" if result["overall_sentiment"] > 0.6 else "🟡" if result["overall_sentiment"] > 0.4 else "🔴"
                    response_parts.append(
                        f"{sentiment_emoji} **{result['call_id']}** - {result['topic']} ({result['duration']}) - Sentiment: {result['overall_sentiment']:.0%}"
                    )
                
                state["result"] = "\n".join(response_parts)
            
            elif call_id:
                # Analyze specific call
                calls = MockDataStore.get_call_recordings(call_id)
                if calls:
                    call = calls[0]
                    analysis = self.analyze_call(call)
                    
                    sentiment_emoji = "🟢" if analysis["overall_sentiment"] > 0.6 else "🟡" if analysis["overall_sentiment"] > 0.4 else "🔴"
                    
                    response_parts = [
                        f"## 🎙️ Call Analysis: {call_id}\n",
                        f"**Topic:** {analysis['topic']}",
                        f"**Agent:** {analysis['agent']}",
                        f"**Duration:** {analysis['duration']}",
                        f"**Resolution:** {analysis['resolution'].replace('_', ' ').title()}\n",
                        f"### Sentiment Analysis:",
                        f"{sentiment_emoji} **Overall Score:** {analysis['overall_sentiment']:.0%}",
                        f"**CSAT Rating:** {'⭐' * analysis['csat_score']} ({analysis['csat_score']}/5)\n",
                        "### Sentiment Journey:",
                        self._format_sentiment_journey(analysis['sentiment_journey']),
                        "\n### Transcript Highlights:\n"
                    ]
                    
                    for line in call["transcript"]:
                        emoji = "👤" if line["speaker"] == "Customer" else "🎧"
                        response_parts.append(f"{emoji} [{line['timestamp']}] **{line['speaker']}:** {line['text']}")
                    
                    if analysis["key_moments"]:
                        response_parts.append("\n### Key Moments:")
                        for moment in analysis["key_moments"]:
                            emoji = "✅" if moment["type"] == "positive_peak" else "⚠️"
                            response_parts.append(f"{emoji} [{moment['timestamp']}] {moment['text']}")
                    
                    state["result"] = "\n".join(response_parts)
                else:
                    state["result"] = f"Call {call_id} not found in records."
            
            else:
                # General inquiry - use LLM
                response = await self.llm_service.chat(
                    state["messages"],
                    self.get_system_prompt()
                )
                state["result"] = response
            
            state["messages"].append({"role": "assistant", "content": state["result"]})
            return state
        
        workflow = StateGraph(AgentState)
        workflow.add_node("analyze", analyze_voice)
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", END)
        
        return workflow
    
    def _format_sentiment_journey(self, scores: List[float]) -> str:
        """Format sentiment journey as visual bars."""
        bars = []
        for score in scores:
            if score >= 0.75:
                bars.append("🟢")
            elif score >= 0.5:
                bars.append("🟡")
            elif score >= 0.25:
                bars.append("🟠")
            else:
                bars.append("🔴")
        return " → ".join(bars)
    
    async def run_with_streaming(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, str]] = None
    ):
        """Run voice analytics with streaming step updates."""
        workflow_steps = []
        messages = self._build_messages_with_history(user_input, conversation_history)
        
        # Step 1: Receive Audio/Transcript
        step1 = {"step": "receive", "status": "active", "label": "Receive Recording"}
        workflow_steps.append(step1)
        yield {"type": "workflow_step", "step": step1, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 2: Transcribe (simulated)
        step2 = {"step": "transcribe", "status": "active", "label": "Transcribe Audio"}
        workflow_steps.append(step2)
        yield {"type": "workflow_step", "step": step2, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 3: Analyze Sentiment
        step3 = {"step": "sentiment", "status": "active", "label": "Analyze Sentiment"}
        workflow_steps.append(step3)
        yield {"type": "workflow_step", "step": step3, "all_steps": workflow_steps.copy()}
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        # Step 4: Generate Insights
        step4 = {"step": "insights", "status": "active", "label": "Generate Insights"}
        workflow_steps.append(step4)
        yield {"type": "workflow_step", "step": step4, "all_steps": workflow_steps.copy()}
        
        # Run the actual analysis
        result = await self.run(user_input, context, conversation_history)
        
        await asyncio.sleep(STEP_DELAY)
        workflow_steps[-1]["status"] = "complete"
        yield {"type": "workflow_step", "step": workflow_steps[-1], "all_steps": workflow_steps.copy()}
        
        yield {"type": "response", "content": result["response"]}

