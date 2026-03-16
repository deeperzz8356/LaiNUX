from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    """
    Represents the state of the agentic operating system.
    """
    goal: str
    plan: List[str]
    current_step_index: int
    tool_outputs: List[str]
    history: List[str]
    status: str
    final_result: Optional[str]
