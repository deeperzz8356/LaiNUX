from langgraph.graph import StateGraph, END
from .state import AgentState
from .planner import PlannerNode
from .executor import ExecutorNode
from .utils.logger import logger

def create_agent_graph(llm):
    # Initialize nodes
    planner = PlannerNode(llm)
    executor = ExecutorNode()
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner)
    workflow.add_node("executor", executor)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Define edges
    # After planning, always go to executor
    workflow.add_edge("planner", "executor")
    
    # After executor, check if we should continue or end
    def should_continue(state):
        if state['status'] == "finished":
            return END
        return "executor"
    
    workflow.add_conditional_edges(
        "executor",
        should_continue
    )
    
    return workflow.compile()
