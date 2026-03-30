import os
import argparse
import sys
import threading
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from agentic_os.agent_graph import create_agent_graph
from agentic_os.utils.logger import logger
from agentic_os.memory.memory_store import MemoryStore
from agentic_os.service.api import start_api_server, broadcast_state
from agentic_os.llm_factory import create_reasoning_llm, create_fast_llm
import asyncio

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

SELF_IMPROVEMENT_GOALS = [
    "Search for better ways to manage files in Python and add a secure_delete tool.",
    "Implement a directory_summary tool that lists file types and counts.",
    "Search for most useful Python automation scripts and implement one as a new tool.",
    "Review existing tools in file_tools.py for bugs or PEP8 violations and fix them.",
    "Establish a unit testing framework in tests and add tests for all core tools.",
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
            "missing_tool": None,
            "rejection_count": 0
        }
        
        broadcast_state(initial_state)
        result_state = graph.invoke(initial_state)
        broadcast_state(result_state)
        
        memory.update_task_status(task_id, result_state['status'])
        logger.info(f"Iteration {iteration} complete. Result: {result_state['final_result'][:100]}...")
        
        iteration += 1
        time.sleep(2) # Brief cooldown


def run_single_goal(graph, memory, goal: str):
    """Runs one goal once and returns the final graph state."""
    task_id = memory.record_task(goal)
    initial_state = {
        "goal": goal,
        "plan": [],
        "current_step_index": 0,
        "tool_outputs": [],
        "history": [],
        "status": "started",
        "final_result": None,
        "reflection": None,
        "wisdom": [],
        "research_notes": None,
        "missing_tool": None,
        "rejection_count": 0
    }

    logger.info(f"Running task: {goal}")
    broadcast_state(initial_state)
    result_state = graph.invoke(initial_state)
    broadcast_state(result_state)
    memory.update_task_status(task_id, result_state['status'])
    return result_state

def main(non_interactive=False, one_shot_goal=None, auto=False, auto_hours=1):
    logger.info("Starting Agentic OS with Mistral AI...")
    
    llm = create_reasoning_llm()  # OpenRouter — see llm_factory.py for model options
    memory = MemoryStore()
    graph = create_agent_graph(llm, memory)
    
    # Start the Neural Dashboard Backend in a background thread
    daemon_thread = threading.Thread(target=start_api_server, kwargs={"graph": graph, "memory": memory}, daemon=True)
    daemon_thread.start()
    logger.info("Neural Dashboard active at: http://localhost:8000")
    # Start the File Watcher (Smart Segregation)
    from .tools.os_mimic_tools import start_file_watcher
    start_file_watcher()
    
    print("====================================")
    print("   AGENTIC AI OPERATING SYSTEM      ")
    print("====================================")
    print("Commands: 'exit', 'auto' (1-hour loop)")

    if one_shot_goal:
        result_state = run_single_goal(graph, memory, one_shot_goal)
        print(f"\nFinal Result: {result_state['final_result']}")
        print(f"Status: {result_state['status']}\n")
        return 0

    if auto:
        run_autonomous_loop(graph, memory, duration_hours=auto_hours)
        return 0

    if non_interactive:
        logger.info("Non-interactive mode requested with no goal. Exiting cleanly.")
        return 0
    
    while True:
        try:
            user_input = input("agent-os > ")
        except EOFError:
            logger.info("EOF on stdin detected. Exiting interactive loop.")
            break
        
        if user_input.lower() == "exit":
            break
            
        if user_input.lower() == "auto":
            run_autonomous_loop(graph, memory, duration_hours=1)
            continue
            
        result_state = run_single_goal(graph, memory, user_input)
        print(f"\nFinal Result: {result_state['final_result']}")
        print(f"Status: {result_state['status']}\n")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Agentic OS interactive or one-shot modes.")
    parser.add_argument("--non-interactive", action="store_true", help="Run startup and exit without waiting for stdin.")
    parser.add_argument("--goal", type=str, help="Run one goal and exit.")
    parser.add_argument("--auto", action="store_true", help="Run autonomous loop and exit.")
    parser.add_argument("--auto-hours", type=int, default=1, help="Hours for autonomous loop when --auto is set.")
    args = parser.parse_args()
    sys.exit(main(non_interactive=args.non_interactive, one_shot_goal=args.goal, auto=args.auto, auto_hours=args.auto_hours))
