from .state import AgentState
from .tools.file_tools import list_files, create_file, read_file
from .utils.logger import logger

class ExecutorNode:
    def __call__(self, state: AgentState):
        idx = state['current_step_index']
        if idx >= len(state['plan']):
            state['status'] = "finished"
            return state
        
        step = state['plan'][idx]
        logger.info(f"Executing step: {step}")
        
        result = "Unknown command"
        
        # Simple string matching for tool selection in prototype
        if "list" in step.lower():
            result = list_files()
        elif "create" in step.lower():
            # Mocking name extraction
            result = create_file("hello.txt", "Hello from Agentic OS!")
        elif "read" in step.lower():
            result = read_file("hello.txt")
            
        state['tool_outputs'].append(result)
        state['current_step_index'] += 1
        
        if state['current_step_index'] >= len(state['plan']):
            state['status'] = "finished"
            state['final_result'] = result
            
        return state
