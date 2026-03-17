import subprocess
import os

def run_tests(test_file="f:/LaiNUX/tests/run_all.py"):
    """Runs automated tests and returns the output."""
    try:
        if not os.path.exists(test_file):
            return "Test file not found. Create f:/LaiNUX/tests/run_all.py first."
        
        result = subprocess.run(['python', test_file], capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            return f"Tests Passed: \n{output}"
        else:
            return f"Tests Failed: \n{output}"
    except Exception as e:
        return f"Testing error: {str(e)}"
