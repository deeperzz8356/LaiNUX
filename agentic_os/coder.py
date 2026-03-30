import os
from pathlib import Path
from .state import AgentState
from .utils.logger import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class CoderNode:
    """
    The Coder node allows the OS to write its own tools.
    It takes a description of a missing capability and generates a Python function for it.
    """
    def __init__(self, model):
        self.model = model
        # Target the sandbox for "untested" tool creation (Phase 4)
        self.sandbox_path = str(PROJECT_ROOT / "sandbox")
        self.production_tools_path = os.path.join(os.path.dirname(__file__), "tools", "file_tools.py")

    def __call__(self, state: AgentState):
        if not state.get('missing_tool'):
            return state
            
        logger.info(f"Coder: Generating new tool in Sandbox for: {state['missing_tool']}")
        
        # Ensure sandbox exists
        if not os.path.exists(self.sandbox_path):
            os.makedirs(self.sandbox_path)

        # Read the existing tools for context
        with open(self.production_tools_path, 'r', encoding='utf-8') as f:
            existing_code = f.read()

        prompt = f"""
        You are the 'Coder'—the self-architecting module of Agentic OS.
        Your goal is to write a new Python tool function for: "{state['missing_tool']}"
        
        EXISTING TOOLS (for context):
        {existing_code}
        
        REQUIREMENTS:
        1. Return ONLY the new Python function.
        2. Ensure it has a clear docstring.
        3. Use standard libraries.
        4. Do NOT include any imports that already exist in the file.
        5. The function name should be descriptive.
        6. This code is currently going into the 'Sandbox' for testing.
        
        Return ONLY the code, no markdown blocks.
        """
        
        try:
            new_tool_code = self.model.invoke(prompt).content.strip()
            # Clean Markdown if LLM adds it
            if new_tool_code.startswith("```python"):
                new_tool_code = new_tool_code[9:-3].strip()
            elif new_tool_code.startswith("```"):
                new_tool_code = new_tool_code[3:-3].strip()
            
            # Write to a temporary file in the sandbox for Critic review
            sandbox_file = os.path.join(self.sandbox_path, "proposed_tool.py")
            with open(sandbox_file, 'w', encoding='utf-8') as f:
                f.write(new_tool_code)
                
            logger.info(f"Coder: Proposed tool written to {sandbox_file} for Architect review.")
            state['missing_tool'] = new_tool_code # Store the code here for the Critic to review
            
        except Exception as e:
            logger.error(f"Coder failed to generate tool in Sandbox: {e}")
            
        return state
