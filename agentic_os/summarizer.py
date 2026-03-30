from .state import AgentState
from .utils.logger import logger
import json

class SummarizerNode:
    """
    Translates complex Agentic OS logs into a simple, human-readable summary.
    Explains what has been done and the final decision/result.
    """
    def __init__(self, model):
        self.model = model

    def __call__(self, state: AgentState):
        logger.info("Summarizer: Translating results to simple human language...")
        
        # Prepare context for the human-readable summary
        # Focus on the 'goal', 'history', 'tool_outputs', and 'final_result'.
        context = {
            "initial_goal": state["goal"],
            "steps_taken": state["plan"],
            "tool_outputs": state["tool_outputs"],
            "final_ai_output": state["final_result"],
            "status": state["status"]
        }
        
        prompt = f"""
        Given the following execution data from the Agentic AI Operating System, 
        provide a simple and concise explanation in FRIENDLY HUMAN LANGUAGE.
        
        Mention:
        1. What the user originally wanted.
        2. What the system actually did (the core actions).
        3. The final decision/result and if it was successful.
        4. Any major obstacles encountered (like missing tools or errors).
        
        CONTEXT:
        {json.dumps(context, indent=2)}
        
        Keep it to 2-3 short paragraphs. No jargon.
        """
        
        try:
            summary_res = self.model.invoke(prompt).content.strip()
            state["summary"] = summary_res
            logger.info("Summarizer complete.")
        except Exception as e:
            logger.error(f"Summarizer failed: {e}")
            state["summary"] = "The system encountered an error while summarizing the result, but the core task is complete."
            
        return state
