from .state import AgentState
from .utils.logger import logger

class EvolverNode:
    """
    The Evolver node allows the Agentic OS to self-reflect and learn from its successes and failures.
    It identifies architectural weaknesses and stores 'wisdom' for the next run.
    """
    def __init__(self, model, memory):
        self.model = model
        self.memory = memory

    def __call__(self, state: AgentState):
        logger.info("Evolving... Analyzing task performance.")
        
        # Build context for reflection
        history_summary = "\n".join([f"Step: {s} -> Result: {r}" for s, r in zip(state['plan'], state['tool_outputs'])])
        
        reflection_prompt = f"""
        You are the 'Evolver'—the recursive self-improvement module of Agentic OS (LaiNUX).
        
        TASK GOAL: {state['goal']}
        EXECUTION HISTORY:
        {history_summary}
        
        FINAL RESULT: {state['final_result']}
        
        YOUR MISSION:
        1. Analyze if the goal was fully achieved.
        2. Identify any 'Unknown command' or tool failures.
        3. If there was a failure, specify why (e.g., 'The Planner used a word the Executor doesn't support').
        4. Create a concise 'Wisdom Nugget' (max 2 sentences) that the OS should remember to avoid this mistake again.
        5. If the failure was because a tool was missing (e.g., 'need to zip files but don't have a zip_files tool'), specify the missing tool.
        
        Return your reflection and the wisdom nugget in the following JSON format:
        {{
            "reflection": "Detailed analysis of what happened...",
            "wisdom_nugget": "...(how to use existing tools better)...",
            "missing_tool": "A brief description of a new tool I should build (e.g., 'a tool to search for strings inside files')" 
        }}
        """
        
        try:
            import json
            response = self.model.invoke(reflection_prompt).content.strip()
            
            # Clean Markdown
            if response.startswith("```json"):
                response = response[7:-3].strip()
            elif response.startswith("```"):
                response = response[3:-3].strip()
                
            data = json.loads(response)
            state['reflection'] = data.get("reflection")
            wisdom = data.get("wisdom_nugget")
            state['missing_tool'] = data.get("missing_tool")
            
            if wisdom:
                logger.info(f"Learned new wisdom: {wisdom}")
                self.memory.record_wisdom(wisdom)
                
        except Exception as e:
            logger.error(f"Evolution failed: {e}")
            state['reflection'] = "System failed to evolve after this run."
            
        return state
