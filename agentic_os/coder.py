import os
from .state import AgentState
from .utils.logger import logger

class CoderNode:
    """
    The Coder node allows the OS to write its own tools.
    It takes a description of a missing capability and generates a Python function for it.
    """
    def __init__(self, model):
        self.model = model
        self.tools_path = os.path.join(os.path.dirname(__file__), "tools", "file_tools.py")

    def __call__(self, state: AgentState):
        if not state.get('missing_tool'):
            return state
            
        logger.info(f"Coder: Generating new tool for: {state['missing_tool']}")
        
        # Read the existing tools to avoid duplicate imports
        with open(self.tools_path, 'r') as f:
            existing_code = f.read()

        prompt = f"""
        You are the 'Coder'—the self-architecting module of Agentic OS.
        Your goal is to write a new Python tool function for: "{state['missing_tool']}"
        
        EXISTING TOOLS (for context):
        {existing_code}
        
        REQUIREMENTS:
        1. Return ONLY the new Python function.
        2. Ensure it has a clear docstring.
        3. Use standard libraries already available (os, pathlib, datetime, etc.).
        4. Do NOT include any imports that already exist in the file.
        5. The function name should be descriptive.
        
        Return ONLY the code, no markdown blocks.
        """
        
        try:
            new_tool_code = self.model.invoke(prompt).content.strip()
            # Clean Markdown if LLM adds it
            if new_tool_code.startswith("```python"):
                new_tool_code = new_tool_code[9:-3].strip()
            elif new_tool_code.startswith("```"):
                new_tool_code = new_tool_code[3:-3].strip()
                
            # Append to the tools file
            with open(self.tools_path, 'a') as f:
                f.write("\n\n" + new_tool_code + "\n")
                
            logger.info("Coder: Successfully expanded architecture with new tool.")
            state['wisdom'].append(f"Successfully added a new tool: {state['missing_tool']}. I can now use it in future tasks.")
            state['missing_tool'] = None # Reset
            
        except Exception as e:
            logger.error(f"Coder failed to expand architecture: {e}")
            
        return state
