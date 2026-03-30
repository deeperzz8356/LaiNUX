import json
from .state import AgentState
from .utils.logger import logger

class PlannerNode:
    def __init__(self, model, memory):
        self.model = model
        self.memory = memory

    def __call__(self, state: AgentState):
        logger.info(f"Planning for goal: {state['goal']}")
        
        # Load historical wisdom via RAG
        all_wisdom = self.memory.get_wisdom(query=state['goal'], limit=5)
        state['wisdom'] = all_wisdom if all_wisdom else ["No relevant neural synapses found for this context."]
            
        wisdom_context = "\n- ".join(state['wisdom'])
        
        # Load Knowledge Base context (shared across Docker agents)
        try:
            from .agents.researcher_agent import load_knowledge_context
            kb_context = load_knowledge_context(state['goal'])
        except Exception:
            kb_context = "Knowledge base not yet populated."
        
        # In a real scenario, we'd use the LLM to generate this.
        if not state['plan']:
            research_context = state.get('research_notes', 'No external research available.')
            
            prompt = f"""
            You are the Planner for LaiNUX - an elite Agentic AI Operating System.
            
            USER GOAL: {state['goal']}
            
            === NEURAL WISDOM (Past Lessons via RAG) ===
            - {wisdom_context}
            
            === EXTERNAL RESEARCH (Live Web Context) ===
            {research_context}
            
            === KNOWLEDGE BASE (Accumulated Intelligence Library) ===
            {kb_context}
            
            Break this goal into a list of SPECIFIC, EXECUTABLE steps using the tools below.
            
            TOOL CAPABILITIES:
            FILE MANAGEMENT:
            - list_files(directory) | read_file | create_file | delete_file | secure_delete
            - search_by_name | segregate_files | list_downloads | get_file_details
            
            SYSTEM CONTROL:
            - answer_question(response_text) | open_application(app_name)
            - get_system_stats | kill_process | run_shell_command(command)
            
            VISION (Screen Interaction):
            - screenshot() | locate_and_click(image_path) | type_text(text)
            
            NETWORKING:
            - check_site_status(url) | get_local_ip | scan_port(host, port)
            
            DOCKER INFRASTRUCTURE:
            - get_docker_stats() | run_in_sandbox(code) | build_sandbox_container()
            
            TESTING & INTEGRITY:
            - run_tests(test_file) | run_shell_command("python -m pytest ...")
            
            SELF-IMPROVEMENT:
            - Use run_shell_command to research, implement, and test new capabilities
            
            IMPORTANT: If the USER GOAL is just a conversational question or a request to summarize what you know or what you have learned, your only step should be: "answer the user's question using answer_question".
            IMPORTANT: Never use placeholder values like returned_file_list, [summarized file details], or variable names that do not contain real data.
            IMPORTANT: When a step needs outputs from a previous step, explicitly say to use the actual previous result.
            
            Return ONLY a JSON list of 3-6 concise steps (or 1 step if just answering).
            Example: ["answer the user's question using answer_question"] OR ["check system stats", "run tests"]
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
        
        try:
            from .service.api import broadcast_state
            broadcast_state(state)
        except ImportError:
            pass
            
        return state
