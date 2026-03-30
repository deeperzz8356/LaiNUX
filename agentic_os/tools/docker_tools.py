import subprocess
import os
from ..utils.logger import logger

def get_docker_stats():
    """Returns the resource usage of currently running Docker containers."""
    try:
        # Get usage stats (ID, Name, CPU, RAM)
        cmd = ["docker", "stats", "--no-stream", "--format", "table {{.ID}}\t{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Neural Infrastructure (Docker):\n{result.stdout}"
    except Exception as e:
        return f"Docker Interface Error: {str(e)}\nMake sure Docker Desktop is active."

def build_sandbox_container(image_name="lainux_sandbox"):
    """Command to build the current OS into a dedicated Docker image for safe multi-evolution."""
    try:
        logger.info(f"Docker: Starting build for {image_name}...")
        cmd = ["docker", "build", "-t", image_name, "."]
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return f"System: Triggered background Docker build for '{image_name}'. I will soon be able to 'fork' myself for parallel testing."
    except Exception as e:
        return f"Build System Failure: {str(e)}"

def run_in_sandbox(command):
    """Executes a command inside the isolated 'lainux_sandbox' container (Phase 4 Extreme)."""
    try:
        # This allows the AI to run any dangerous script (like the new tool it wrote)
        # without touching your real Windows F:\ drive files.
        cmd = ["docker", "run", "--rm", "lainux_sandbox", "python", "-c", command]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return f"Isolated Execution Output (Docker):\n{result.stdout or '[No Stdout]'}\nErrors: {result.stderr or '[None]'}"
    except Exception as e:
        return f"Sandbox Escape Failure: {str(e)}"
