import os
from dotenv import load_dotenv
from agentic_os.agent_graph import create_agent_graph
from agentic_os.utils.logger import logger
from agentic_os.memory.memory_store import MemoryStore

load_dotenv()

class MockLLM:
    """Mock LLM for demonstration without an API key."""
    def invoke(self, prompt):
        class Content:
            content = '[]'
        return Content()

def main():
    logger.info("Starting Agentic OS...")
    
    # Initialize components
    llm = MockLLM()
    graph = create_agent_graph(llm)
    memory = MemoryStore()
    
    print("====================================")
    print("   AGENTIC AI OPERATING SYSTEM      ")
    print("====================================")
    print("Type 'exit' to quit.")
    
    while True:
        user_input = input("agent-os > ")
        
        if user_input.lower() == "exit":
            break
            
        # Record task in memory
        task_id = memory.record_task(user_input)
        
        # Initialize state
        initial_state = {
            "goal": user_input,
            "plan": [],
            "current_step_index": 0,
            "tool_outputs": [],
            "history": [],
            "status": "started",
            "final_result": None
        }
        
        # Run the graph
        logger.info(f"Running task: {user_input}")
        result_state = graph.invoke(initial_state)
        
        # Update memory and show result
        memory.update_task_status(task_id, result_state['status'])
        print(f"\nFinal Result: {result_state['final_result']}")
        print(f"Status: {result_state['status']}\n")

if __name__ == "__main__":
    main()
