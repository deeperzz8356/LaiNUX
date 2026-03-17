from duckduckgo_search import DDGS
from .state import AgentState
from .utils.logger import logger

class ResearcherNode:
    """
    The Researcher node allows the OS to go beyond its local environment.
    It can look up facts, code snippets, or documentation to help the Planner.
    """
    def __init__(self, model):
        self.model = model

    def __call__(self, state: AgentState):
        # We only research if the goal seems to require external knowledge
        # or if the planner explicitly suggested a research step.
        research_needed_prompt = f"""
        Analyze this goal: "{state['goal']}"
        Does this require searching the internet for facts, documentation, or code help?
        Answer with ONLY 'YES' or 'NO'.
        """
        
        try:
            decision = self.model.invoke(research_needed_prompt).content.strip().upper()
            
            if "YES" in decision:
                logger.info("Researcher: Searching the web for context...")
                
                # Generate a search query
                query_prompt = f"Generate a single efficient search query for this goal: {state['goal']}"
                search_query = self.model.invoke(query_prompt).content.strip()
                
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(search_query, max_results=3)]
                
                state['research_notes'] = str(results)
                logger.info(f"Researcher found {len(results)} results.")
            else:
                state['research_notes'] = "No research required for this task."
                
        except Exception as e:
            logger.error(f"Researcher failed: {e}")
            state['research_notes'] = f"Failed to perform research: {str(e)}"
            
        return state
