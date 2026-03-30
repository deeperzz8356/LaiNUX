import json
import importlib
import inspect
from .state import AgentState
from .tools import file_tools, system_tools, tester_tools, vision_tools, network_tools, shell_tools
from .utils.logger import logger

class ExecutorNode:
    def __init__(self, model):
        self.model = model

    def hot_reload_tools(self):
        """Reloads modules to pick up new tools written by the Coder Node."""
        try:
            importlib.reload(file_tools)
            importlib.reload(system_tools)
            importlib.reload(tester_tools)
            importlib.reload(vision_tools)
            importlib.reload(network_tools)
            importlib.reload(shell_tools)
            logger.info("Hot-Reload: Tools updated successfully.")
        except Exception as e:
            logger.error(f"Hot-Reload failed: {e}")

    def __call__(self, state: AgentState):
        self.hot_reload_tools() # Always look for new code before running
        idx = state['current_step_index']
        if idx >= len(state['plan']):
            state['status'] = "finished"
            return state
        
        step = state['plan'][idx]
        logger.info(f"Executing step: {step}")
        
        # Mapping prompt
        tool_selection_prompt = f"""
        Select the MOST APPROPRIATE tool:
        - list_files(directory="."): Generic file list.
        - read_file(filename): Read text contents.
        - create_file(filename, content=""): Make a new file.
        - delete_file(filename): Standard file delete.
        - secure_delete(filename): SECURELY shred a file (multi-pass overwrite).
        - list_downloads(): Show recent downloads folder.
        - segregate_files(directory="."): Group by extension.
        - get_file_details(filename): Metadata for 1 file.
        - search_by_name(name, root_dir='.'): Find file location across folders.
        - open_application(app_name): Launch an app (notepad, calc, etc).
        - get_system_stats(): CPU, RAM, Disk usage.
        - kill_process(process_name): Force stop an app/process.
        - run_shell_command(command): Run a PowerShell/Bash command and get text output.
        - check_site_status(url): Check if a website or API is UP (HTTP 200).
        - get_local_ip(): System network interface IP address.
        - run_tests(test_file): Run automated tests (f:/LaiNUX/tests/run_all.py).
        - screenshot(): Capture active screen for 'Vision'.
        - type_text(text): Type into the focused window.
        - locate_and_click(image_path): Click a visual UI element.
        
        Return JSON: {{"tool": "name", "args": {{...}}}}
        """
        
        try:
            res = self.model.invoke(f"{tool_selection_prompt}\nStep: {step}").content.strip()
            if "```" in res: res = res.split("```")[1].strip("json\n ")
            data = json.loads(res)
            
            # Master tools map
            all_tools = {
                "list_files": file_tools.list_files,
                "read_file": file_tools.read_file,
                "create_file": file_tools.create_file,
                "delete_file": file_tools.delete_file,
                "secure_delete": file_tools.secure_delete,
                "list_downloads": file_tools.list_downloads,
                "segregate_files": file_tools.segregate_files,
                "get_file_details": file_tools.get_file_details,
                "search_by_name": file_tools.search_by_name,
                "get_drive_properties": file_tools.get_drive_properties,
                "parse_robust_response": file_tools.parse_robust_response,
                "open_application": system_tools.open_application,
                "get_system_stats": system_tools.get_system_stats,
                "kill_process": system_tools.kill_process,
                "run_tests": tester_tools.run_tests,
                "run_shell_command": shell_tools.run_shell_command,
                "check_site_status": network_tools.check_site_status,
                "get_local_ip": network_tools.get_local_ip,
                "screenshot": vision_tools.screenshot,
                "type_text": vision_tools.type_text,
                "locate_and_click": vision_tools.locate_and_click
            }
            
            t_name = data.get("tool")
            if t_name in all_tools:
                logger.info(f"Running: {t_name}")
                tool_func = all_tools[t_name]
                tool_args = data.get("args", {})
                
                # Filter args based on function signature (Security & Error Prevention)
                sig = inspect.signature(tool_func)
                filtered_args = {k: v for k, v in tool_args.items() if k in sig.parameters}
                
                result = tool_func(**filtered_args)
            else:
                result = f"Error: Tool '{t_name}' is not in my core library."
                
        except Exception as e:
            result = f"Execution error: {str(e)}"
            
        state['tool_outputs'].append(result)
        state['current_step_index'] += 1
        if state['current_step_index'] >= len(state['plan']):
            state['status'] = "finished"
            state['final_result'] = result
            
        return state
