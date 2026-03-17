import json
from .state import AgentState
from .utils.logger import logger

class PlannerNode:
    def __init__(self, model):
        self.model = model

    def __call__(self, state: AgentState):
        logger.info(f"Planning for goal: {state['goal']}")
        
        # In a real scenario, we'd use the LLM to generate this.
        # For the prototype, we simulate a plan if it doesn't exist.
        if not state['plan']:
            prompt = f"""
            You are the Planner for an Agentic OS. 
            User Goal: {state['goal']}
            Break this into a list of executable steps.
            Return ONLY a JSON list of strings.
            Example: ["list files", "read file test.txt"]
            """
            # Use the LLM to generate a plan
            result = self.model.invoke(prompt)
            try:
                # Clean the content in case of markdown blocks
                content = result.content.strip()
                if content.startswith("```json"):
                    content = content[7:-3].strip()
                elif content.startswith("```"):
                    content = content[3:-3].strip()
                state['plan'] = json.loads(content)
            except Exception as e:
                logger.error(f"Failed to parse plan: {e}")
                state['plan'] = ["list files in current directory"]
        
        state['status'] = "planned"
        return state
