import json
from .state import AgentState
from .utils.logger import logger

class PlannerNode:
    def __init__(self, model, memory):
        self.model = model
        self.memory = memory

    def __call__(self, state: AgentState):
        logger.info(f"Planning for goal: {state['goal']}")
        
        # Load historical wisdom and perform 'Neural Attention'
        all_wisdom = self.memory.get_wisdom()
        
        if all_wisdom:
            attention_prompt = f"""
            Goal: "{state['goal']}"
            Wisdom Bank: {all_wisdom}
            Identify the top 3 MOST RELEVANT lessons to help achieve this goal.
            Return ONLY a comma-separated list of the lesson IDs or text.
            """
            try:
                state['wisdom'] = self.model.invoke(attention_prompt).content.strip().split("\n")
            except:
                state['wisdom'] = all_wisdom[:5]
        else:
            state['wisdom'] = ["No neural synapses formed yet."]
            
        wisdom_context = "\n- ".join(state['wisdom'])
        
        # In a real scenario, we'd use the LLM to generate this.
        if not state['plan']:
            research_context = state.get('research_notes', 'No external research available.')
            
            prompt = f"""
            You are the Planner for an Agentic OS. 
            User Goal: {state['goal']}
            
            NEURAL ATTENTION (Relevant Lessons):
            - {wisdom_context}
            
            EXTERNAL RESEARCH (Fresh info/documentation/code from web):
            - {research_context}
            
            Break this into a list of executable steps.
            Capabilities:
            - List files in a directory with full details (size, date)
            - Show recent downloads specifically
            - Segregate/group files by extension/type
            - Read, Create, and DELETE text files
            - Search for files by name across all folders
            - Open computer applications (e.g., notepad, calculator)
            - Check system health (CPU, RAM, usage)
            
            Return ONLY a JSON list of strings.
            Example: ["list downloads", "segregate files in current folder", "read file hello.txt"]
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
