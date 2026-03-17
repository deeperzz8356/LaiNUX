import os
import threading
from dotenv import load_dotenv
from agentic_os.agent_graph import create_agent_graph
from agentic_os.utils.logger import logger
from agentic_os.memory.memory_store import MemoryStore
from agentic_os.service.api import start_api_server, broadcast_state
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

load_dotenv()

def main():
    logger.info("Starting Agentic OS with Gemini...")
    
    # Start the Neural Dashboard Backend in a background thread
    daemon_thread = threading.Thread(target=start_api_server, daemon=True)
    daemon_thread.start()
    logger.info("Neural Dashboard active at: http://localhost:8000")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    memory = MemoryStore()
    graph = create_agent_graph(llm, memory)
    
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
            "final_result": None,
            "reflection": None,
            "wisdom": [],
            "research_notes": None,
            "missing_tool": None
        }
        
        # Run the graph
        logger.info(f"Running task: {user_input}")
        asyncio.run(broadcast_state(initial_state))
        
        result_state = graph.invoke(initial_state)
        
        # Broadcast the final evolved state to the dashboard
        asyncio.run(broadcast_state(result_state))
        
        # Update memory and show result
        memory.update_task_status(task_id, result_state['status'])
        print(f"\nFinal Result: {result_state['final_result']}")
        print(f"Status: {result_state['status']}\n")

if __name__ == "__main__":
    main()
