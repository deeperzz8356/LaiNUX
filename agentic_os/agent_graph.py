from langgraph.graph import StateGraph, END
from .state import AgentState
from .planner import PlannerNode
from .executor import ExecutorNode
from .evolver import EvolverNode
from .researcher import ResearcherNode
from .coder import CoderNode
from .debugger import DebuggerNode
from .critic import CriticNode
from .summarizer import SummarizerNode
from .ml_expert import MLExpertNode
from .utils.logger import logger

def create_agent_graph(llm, memory):
    # Initialize nodes
    researcher = ResearcherNode(llm)
    planner = PlannerNode(llm, memory)
    executor = ExecutorNode(llm)
    evolver = EvolverNode(llm, memory)
    coder = CoderNode(llm)
    debugger = DebuggerNode(llm)
    critic = CriticNode(llm)
    summarizer = SummarizerNode(llm)
    ml_expert = MLExpertNode(llm)
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("researcher", researcher)
    workflow.add_node("planner", planner)
    workflow.add_node("executor", executor)
    workflow.add_node("debugger", debugger)
    workflow.add_node("evolver", evolver)
    workflow.add_node("coder", coder)
    workflow.add_node("critic", critic)
    workflow.add_node("summarizer", summarizer)
    workflow.add_node("ml_expert", ml_expert)
    
    # Set entry point
    workflow.set_entry_point("researcher")
    
    # Define edges
    # New Flow: Researcher (External) -> ML Expert (Model Knowledge) -> Planner (Local Action)
    workflow.add_edge("researcher", "ml_expert")
    workflow.add_edge("ml_expert", "planner")
    workflow.add_edge("planner", "executor")
    
    def after_executor(state):
        if state['current_step_index'] >= len(state['plan']):
            return "debugger"
        return "executor"
    
    workflow.add_conditional_edges("executor", after_executor)
    
    # Flow: Debugger (Fix bugs) -> Evolver (Learn lessons) -> Coder (Write/Repair tools)
    workflow.add_edge("debugger", "evolver")
    workflow.add_edge("evolver", "coder")
    workflow.add_edge("coder", "critic")
    
    # Phase 6: Human Feedback Loop & Final Summary
    def after_critic(state):
        if state.get('rejection_count', 0) >= 3:
            logger.warning("Human Feedback Loop: AI has hit 3 rejections from Critic. Pausing for human wisdom.")
            return "summarizer"
        if state.get('status') == "failed_review":
            # Re-run coder or researcher if failed
            return "evolver" 
        return "summarizer"
        
    workflow.add_conditional_edges("critic", after_critic)
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()
