import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agentic_os.tools import file_tools

def test_file_tools():
    print("Running File Tools Tests...")
    try:
        files = file_tools.list_files(".")
        print(f"List files test: SUCCESS (Found {len(files)} items)")
        return True
    except Exception as e:
        print(f"List files test: FAILED - {e}")
        return False

if __name__ == "__main__":
    success = test_file_tools()
    sys.exit(0 if success else 1)
