import subprocess
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def run_tests(test_file=None):
    """Runs automated tests and returns the output."""
    try:
        if test_file is None:
            test_file = str(PROJECT_ROOT / "tests" / "run_all.py")

        if not os.path.exists(test_file):
            return f"Test file not found at {test_file}."
        
        result = subprocess.run([sys.executable, test_file], capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            return f"Tests Passed: \n{output}"
        else:
            return f"Tests Failed: \n{output}"
    except Exception as e:
        return f"Testing error: {str(e)}"
