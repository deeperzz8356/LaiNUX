import json
import os
import traceback
from .state import AgentState
from .utils.logger import logger

class DebuggerNode:
    """
    The Debugger node provides 'Self-Healing' capabilities.
    If a tool or node fails with a traceback, the Debugger analyzes the source code,
    identifies the bug, and passes a fix request to the Coder.
    """
    def __init__(self, model):
        self.model = model

    def __call__(self, state: AgentState):
        has_error = any("Error" in str(out) or "traceback" in str(out).lower() for out in state['tool_outputs'])
        
        if not has_error:
            return state
            
        logger.info("Debugger: Identifying a failure in the system. Initiating Self-Healing...")
        
        # Gather context: The failed output and the tools involved
        failure_context = "\n".join([str(out) for out in state['tool_outputs'] if "Error" in str(out)])
        
        prompt = f"""
        You are the 'Self-Healing Debugger' for Agentic OS.
        A failure has occurred during execution.
        
        FAILURE LOG:
        {failure_context}
        
        YOUR MISSION:
        1. Determine if this is a code bug in the tools or a logic error.
        2. If it's a code bug, identify which tool/file is likely broken.
        3. Formulate a 'Fix Request' for the Coder Node.
        
        Return ONLY a JSON object:
        {{
            "is_fixable": true/false,
            "target_file": "path/to/file.py",
            "issue_description": "What is wrong...",
            "fix_instruction": "Specific instruction for the Coder to repair the code."
        }}
        """
        
        try:
            response = self.model.invoke(prompt).content.strip()
            if "```" in response: response = response.split("```")[1].strip("json\n ")
            
            data = json.loads(response)
            if data.get("is_fixable"):
                logger.info(f"Debugger: Found a fixable issue in {data['target_file']}. Routing to Coder.")
                state['missing_tool'] = f"REPAIR: {data['target_file']} - {data['fix_instruction']}"
                state['reflection'] = f"SELF-HEAL INITIATED: {data['issue_description']}"
            
        except Exception as e:
            logger.error(f"Debugger failed: {e}")
            
        return state
