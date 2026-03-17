import os
import threading
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from agentic_os.agent_graph import create_agent_graph
from agentic_os.utils.logger import logger
from agentic_os.memory.memory_store import MemoryStore
from agentic_os.service.api import start_api_server, broadcast_state
from langchain_mistralai import ChatMistralAI
import asyncio

load_dotenv()

SELF_IMPROVEMENT_GOALS = [
    "Search for better ways to manage files in Python and add a secure_delete tool.",
    "Implement a directory_summary tool that lists file types and counts.",
    "Search for most useful Python automation scripts and implement one as a new tool.",
    "Review existing tools in file_tools.py for bugs or PEP8 violations and fix them.",
    "Establish a unit testing framework in f:/LaiNUX/tests and add tests for all core tools.",
    "Research Agentic AI trends and implement a 'Wisdom Nugget' generation feature in memory.",
    "Optimize code in executor.py to handle more edge cases.",
    "Enhance system_tools.py to include CPU/RAM/Network monitoring as a persistent log."
]

def run_autonomous_loop(graph, memory, duration_hours=1):
    end_time = datetime.now() + timedelta(hours=duration_hours)
    logger.info(f"AUTONOMOUS EVOLUTION STARTED. Running until: {end_time}")
    
    iteration = 1
    while datetime.now() < end_time:
        import random
        goal = random.choice(SELF_IMPROVEMENT_GOALS)
        logger.info(f"--- EVOLUTION ITERATION {iteration} ---")
        logger.info(f"Self-Assigned Goal: {goal}")
        
        # Record and init state
        task_id = memory.record_task(f"SELF_EVO_{iteration}: {goal}")
        initial_state = {
            "goal": goal,
            "plan": [],
            "current_step_index": 0,
            "tool_outputs": [],
            "history": [],
            "status": "started",
            "final_result": None,
            "reflection": None,
            "wisdom": [f"Running Autonomous Evolution Cycle {iteration}"],
            "research_notes": None,
            "missing_tool": None
        }
        
        asyncio.run(broadcast_state(initial_state))
        result_state = graph.invoke(initial_state)
        asyncio.run(broadcast_state(result_state))
        
        memory.update_task_status(task_id, result_state['status'])
        logger.info(f"Iteration {iteration} complete. Result: {result_state['final_result'][:100]}...")
        
        iteration += 1
        time.sleep(2) # Brief cooldown

def main():
    logger.info("Starting Agentic OS with Mistral AI...")
    
    # Start the Neural Dashboard Backend in a background thread
    daemon_thread = threading.Thread(target=start_api_server, daemon=True)
    daemon_thread.start()
    logger.info("Neural Dashboard active at: http://localhost:8000")
    
    llm = ChatMistralAI(model="mistral-large-latest")
    memory = MemoryStore()
    graph = create_agent_graph(llm, memory)
    
    print("====================================")
    print("   AGENTIC AI OPERATING SYSTEM      ")
    print("====================================")
    print("Commands: 'exit', 'auto' (1-hour loop)")
    
    while True:
        user_input = input("agent-os > ")
        
        if user_input.lower() == "exit":
            break
            
        if user_input.lower() == "auto":
            run_autonomous_loop(graph, memory, duration_hours=1)
            continue
            
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
