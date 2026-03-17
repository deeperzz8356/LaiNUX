from langgraph.graph import StateGraph, END
from .state import AgentState
from .planner import PlannerNode
from .executor import ExecutorNode
from .evolver import EvolverNode
from .researcher import ResearcherNode
from .coder import CoderNode
from .debugger import DebuggerNode
from .utils.logger import logger

def create_agent_graph(llm, memory):
    # Initialize nodes
    researcher = ResearcherNode(llm)
    planner = PlannerNode(llm, memory)
    executor = ExecutorNode(llm)
    evolver = EvolverNode(llm, memory)
    coder = CoderNode(llm)
    debugger = DebuggerNode(llm)
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("researcher", researcher)
    workflow.add_node("planner", planner)
    workflow.add_node("executor", executor)
    workflow.add_node("debugger", debugger)
    workflow.add_node("evolver", evolver)
    workflow.add_node("coder", coder)
    
    # Set entry point
    workflow.set_entry_point("researcher")
    
    # Define edges
    workflow.add_edge("researcher", "planner")
    workflow.add_edge("planner", "executor")
    
    def after_executor(state):
        if state['current_step_index'] >= len(state['plan']):
            return "debugger"
        return "executor"
    
    workflow.add_conditional_edges("executor", after_executor)
    
    # Flow: Debugger (Fix bugs) -> Evolver (Learn lessons) -> Coder (Write/Repair tools)
    workflow.add_edge("debugger", "evolver")
    workflow.add_edge("evolver", "coder")
    workflow.add_edge("coder", END)
    
    return workflow.compile()
