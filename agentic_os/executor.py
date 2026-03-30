import json
import importlib
import inspect
import os
import re
from .state import AgentState
from .tools import file_tools, system_tools, tester_tools, vision_tools, network_tools, shell_tools, docker_tools, os_mimic_tools
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
            importlib.reload(docker_tools)
            importlib.reload(os_mimic_tools)
            logger.info("Hot-Reload: Tools updated successfully.")
        except Exception as e:
            logger.error(f"Hot-Reload failed: {e}")
    def _extract_files_from_output(self, output):
        """Extract file names from a list_files style tool output."""
        if not isinstance(output, list):
            return []

        files = []
        for item in output:
            if isinstance(item, dict) and item.get("type") == "file" and item.get("name"):
                files.append(item["name"])
            elif isinstance(item, str):
                files.append(item)
        return files

    def _extract_paths_from_output(self, output):
        """Extract file paths from common tool output shapes."""
        if output is None:
            return []

        if isinstance(output, str):
            extracted = []
            for raw in output.splitlines():
                line = raw.strip()
                if line.startswith("- "):
                    line = line[2:].strip()
                if line.startswith(("f:", "F:", "c:", "C:", "/", ".\\", "./")):
                    extracted.append(line)
            return extracted

        if isinstance(output, list):
            paths = []
            for item in output:
                if isinstance(item, str):
                    paths.append(item)
                elif isinstance(item, dict):
                    if item.get("abspath"):
                        paths.append(item["abspath"])
                    elif item.get("path") and "error" not in item:
                        paths.append(item["path"])
            return [p for p in paths if isinstance(p, str) and p.strip()]

        return []

    def _extract_filename_from_goal(self, goal_text):
        """Extract a likely filename from user goal text."""
        if not goal_text:
            return None

        patterns = [
            r"([\w\-.]+\.[a-zA-Z0-9]{1,8})",
            r"find\s+([\w\-.]+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, goal_text)
            if m:
                return m.group(1)
        return None

    def _build_documents_summary(self):
        """Build a concrete summary for files in the Documents category."""
        documents_dir = os_mimic_tools.SEGREGATED_DIRS.get("Documents")
        if not documents_dir or not os.path.exists(documents_dir):
            return "I could not find the Documents folder in your OS root."

        files = [f for f in os.listdir(documents_dir) if os.path.isfile(os.path.join(documents_dir, f))]
        if not files:
            return "Your Documents folder is currently empty."

        files.sort()
        lines = [f"I found {len(files)} document(s) in your Documents folder:"]
        for name in files[:20]:
            path = os.path.join(documents_dir, name)
            st = os.stat(path)
            lines.append(f"- {name} ({st.st_size} bytes)")

        if len(files) > 20:
            lines.append(f"- ...and {len(files) - 20} more files")

        return "\n".join(lines)

    def _build_audio_summary(self):
        """Build a concrete summary for files in the Audio category."""
        audio_dir = os_mimic_tools.SEGREGATED_DIRS.get("Audio")
        if not audio_dir or not os.path.exists(audio_dir):
            return "I could not find the Audio folder in your OS root."

        files = [f for f in os.listdir(audio_dir) if os.path.isfile(os.path.join(audio_dir, f))]
        if not files:
            return "I did not find audio files in your Audio folder."

        files.sort()
        lines = [f"I found {len(files)} audio file(s):"]
        for name in files[:20]:
            path = os.path.join(audio_dir, name)
            st = os.stat(path)
            lines.append(f"- {name} ({st.st_size} bytes)")

        if len(files) > 20:
            lines.append(f"- ...and {len(files) - 20} more files")

        return "\n".join(lines)

    def _format_fallback_answer(self, output):
        """Format arbitrary tool output into human-readable text."""
        if output is None:
            return "I do not have tool output yet."
        if isinstance(output, str):
            return output
        try:
            return json.dumps(output, indent=2)
        except Exception:
            return str(output)

    def _build_find_summary(self, output, goal_text):
        """Build a clean summary for find/search goals."""
        paths = self._extract_paths_from_output(output)
        if not paths and isinstance(output, list):
            paths = [p for p in output if isinstance(p, str)]

        target = self._extract_filename_from_goal(goal_text or "") or "the file"
        if not paths:
            return f"I could not find {target}."

        lines = [f"I found {target} at:"]
        for p in paths[:10]:
            lines.append(f"- {p}")
        if len(paths) > 10:
            lines.append(f"- ...and {len(paths) - 10} more matches")
        return "\n".join(lines)

    def _resolve_args(self, tool_name, tool_args, state):
        """Resolve common placeholder values using prior tool outputs."""
        resolved = dict(tool_args or {})
        last_output = state['tool_outputs'][-1] if state['tool_outputs'] else None

        if tool_name == "get_file_details":
            placeholder_values = {"returned_file_list", "file_list", "last_output", "previous_output"}

            if isinstance(resolved.get("file_paths"), str):
                value = resolved["file_paths"].strip().lower()
                if value in placeholder_values:
                    extracted = self._extract_files_from_output(last_output)
                    if extracted:
                        resolved["file_paths"] = extracted
                    else:
                        resolved.pop("file_paths", None)

            if isinstance(resolved.get("filename"), str):
                value = resolved["filename"].strip().lower()
                if value in placeholder_values:
                    extracted = self._extract_files_from_output(last_output)
                    if extracted:
                        resolved["filename"] = extracted[0]
                    else:
                        resolved.pop("filename", None)

            if not resolved.get("filename") and not resolved.get("file_paths"):
                extracted = self._extract_files_from_output(last_output)
                if extracted:
                    resolved["file_paths"] = extracted

        if tool_name == "search_by_name":
            if not resolved.get("name"):
                inferred = self._extract_filename_from_goal(state.get("goal", ""))
                if inferred:
                    resolved["name"] = inferred
            if not resolved.get("root_dir"):
                resolved["root_dir"] = "."

        if tool_name == "read_file":
            filename = str(resolved.get("filename", "")).strip()
            placeholder_bits = [
                "actual file path",
                "actual_file_path",
                "previous_search_results",
                "search results",
                "returned_file",
                "returned_file_list",
                "/path/to/",
            ]
            is_placeholder = (not filename) or any(bit in filename.lower() for bit in placeholder_bits) or ("<" in filename and ">" in filename)

            if is_placeholder:
                paths = self._extract_paths_from_output(last_output)
                if paths:
                    resolved["filename"] = paths[0]
                else:
                    inferred = self._extract_filename_from_goal(state.get("goal", ""))
                    if inferred:
                        resolved["filename"] = inferred

        if tool_name == "answer_question":
            response_text = str(resolved.get("response_text", ""))
            lower_text = response_text.lower()
            goal_text = state.get('goal', '').lower()
            has_placeholder = (
                not response_text.strip()
                or "summarized file details" in lower_text
                or "returned_file_list" in lower_text
                or "formatted_file_details" in lower_text
                or "[" in response_text and "]" in response_text
            )
            if has_placeholder:
                if "document" in goal_text:
                    resolved["response_text"] = self._build_documents_summary()
                elif "audio" in goal_text or "music" in goal_text or "song" in goal_text:
                    resolved["response_text"] = self._build_audio_summary()
                elif "find" in goal_text or "search" in goal_text:
                    resolved["response_text"] = self._build_find_summary(last_output, state.get("goal", ""))
                else:
                    resolved["response_text"] = self._format_fallback_answer(last_output)

        return resolved

    def _apply_goal_overrides(self, tool_data, step, state):
        """Apply deterministic routing for common user intents."""
        data = dict(tool_data or {})
        goal_text = state.get("goal", "").lower()
        step_text = (step or "").lower()

        t_name = data.get("tool")
        args = dict(data.get("args", {}))

        if "document" in goal_text and t_name == "list_files":
            directory = str(args.get("directory", "")).strip().lower()
            if directory in {"/documents", "documents", "~/documents", "/home/user/documents"}:
                return {"tool": "find_by_type", "args": {"category": "Documents"}}

        if any(k in goal_text for k in ["audio", "music", "song"]):
            if t_name == "run_shell_command":
                command = str(args.get("command", "")).lower()
                linux_markers = ["/dev/snd", "~/music", "/music", "ls "]
                if any(marker in command for marker in linux_markers):
                    return {"tool": "find_by_type", "args": {"category": "Audio"}}
            if t_name == "get_system_stats" and ("audio" in step_text or "music" in step_text):
                return {"tool": "find_by_type", "args": {"category": "Audio"}}

        if "find" in goal_text:
            inferred_name = self._extract_filename_from_goal(state.get("goal", ""))
            last_output = state['tool_outputs'][-1] if state['tool_outputs'] else None
            found_paths = self._extract_paths_from_output(last_output)
            current_idx = int(state.get("current_step_index", 0))

            if current_idx > 0 and t_name in {"list_files", "search_by_name"}:
                return {"tool": "answer_question", "args": {"response_text": ""}}

            if found_paths and t_name in {"list_files", "search_by_name"}:
                return {"tool": "answer_question", "args": {"response_text": ""}}

            if inferred_name and t_name == "list_files" and "search" not in step_text:
                return {"tool": "search_by_name", "args": {"name": inferred_name, "root_dir": "."}}

        return {"tool": t_name, "args": args}

    def _fallback_tool_selection(self, step):
        """Infer a tool call from free-form planner text when JSON tool selection fails."""
        text = step.strip()
        lower = text.lower()

        if "answer_question" in lower or "answer the user's question" in lower or "answer the user" in lower:
            return {"tool": "answer_question", "args": {"response_text": ""}}

        if "search_by_name" in lower or "search by name" in lower:
            m = re.search(r"['\"]([^'\"]+\.[a-zA-Z0-9]{1,8})['\"]", text)
            file_name = m.group(1) if m else None
            args = {"root_dir": "."}
            if file_name:
                args["name"] = file_name
            return {"tool": "search_by_name", "args": args}

        if "read_file" in lower and ("actual file path" in lower or "search results" in lower):
            return {"tool": "read_file", "args": {"filename": "actual_file_path_from_previous_search_results"}}

        if "find" in lower and "audio" in lower:
            return {"tool": "find_by_type", "args": {"category": "Audio"}}

        if "find" in lower and "document" in lower:
            return {"tool": "find_by_type", "args": {"category": "Documents"}}

        if "get_file_details" in lower:
            args = {}
            if "returned_file_list" in lower:
                args["file_paths"] = "returned_file_list"
            return {"tool": "get_file_details", "args": args}

        if "list_files" in lower:
            m = re.search(r"directory\s*=\s*['\"]([^'\"]+)['\"]", text)
            directory = m.group(1) if m else "."
            return {"tool": "list_files", "args": {"directory": directory}}

        if "find_by_type" in lower and "documents" in lower:
            return {"tool": "find_by_type", "args": {"category": "Documents"}}

        return None

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
        - answer_question(response_text): Provide a direct textual answer/summary to the user.
        - get_local_ip(): System network interface IP address.
        - get_docker_stats(): CPU/RAM usage of current Docker containers.
        - run_in_sandbox(python_code): Execute risky code inside an ISOLATED Docker container.
        - run_tests(test_file): Run automated tests (default: tests/run_all.py).
        - screenshot(): Capture active screen for 'Vision'.
        - type_text(text): Type into the focused window.
        - locate_and_click(image_path): Click a visual UI element.
        - smart_segregate(): Automatically move 'Downloaded' files into themed folders (Images, Audio, Documents).
        - smart_search(query): Perform a cross-folder smart search for a file within the OS-Root.
        - find_by_type(category): List files by category (Images, Audio, Documents, Others).
        - get_os_file_summary(): Get a birds-eye view of all organized files.
        - fine_tune_file_model(extension, category): Train the segregation model on a new extension.
        - start_file_watcher(): ACTIVATE the background automatic file manager.
        - get_file_manager_status(): Check if the auto-organizer is running.
        - stop_file_watcher(): DEACTIVATE the background cleaner.
        
        IMPORTANT: Never use placeholders such as returned_file_list, previous_output, or [summarized file details].
        Use concrete values from actual previous tool results.
        
        Return JSON: {{"tool": "name", "args": {{...}}}}
        """
        
        try:
            res = self.model.invoke(f"{tool_selection_prompt}\nStep: {step}").content.strip()
            if "```" in res: res = res.split("```")[1].strip("json\n ")
            try:
                data = json.loads(res)
            except Exception:
                data = self._fallback_tool_selection(step)
                if data is None:
                    raise

            data = self._apply_goal_overrides(data, step, state)
            
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
                "answer_question": system_tools.answer_question,
                "run_tests": tester_tools.run_tests,
                "get_docker_stats": docker_tools.get_docker_stats,
                "run_in_sandbox": docker_tools.run_in_sandbox,
                "run_shell_command": shell_tools.run_shell_command,
                "check_site_status": network_tools.check_site_status,
                "get_local_ip": network_tools.get_local_ip,
                "screenshot": vision_tools.screenshot,
                "type_text": vision_tools.type_text,
                "locate_and_click": vision_tools.locate_and_click,
                "mock_download": os_mimic_tools.mock_download,
                "smart_segregate": os_mimic_tools.smart_segregate,
                "smart_search": os_mimic_tools.smart_search,
                "find_by_type": os_mimic_tools.find_by_type,
                "get_os_file_summary": os_mimic_tools.get_os_file_summary,
                "fine_tune_file_model": os_mimic_tools.fine_tune_file_model,
                "start_file_watcher": os_mimic_tools.start_file_watcher,
                "stop_file_watcher": os_mimic_tools.stop_file_watcher,
                "get_file_manager_status": os_mimic_tools.get_file_manager_status
            }
            
            t_name = data.get("tool")
            if t_name in all_tools:
                logger.info(f"Running: {t_name}")
                tool_func = all_tools[t_name]
                tool_args = self._resolve_args(t_name, data.get("args", {}), state)
                
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
        
        try:
            from .service.api import broadcast_state
            broadcast_state(state)
        except ImportError:
            pass
            
        if state['current_step_index'] >= len(state['plan']):
            state['status'] = "finished"
            state['final_result'] = result
            
        return state
