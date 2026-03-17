# Structured Input Parser with Fallback Mechanisms
import json
import sys
from typing import Any, Dict, Optional


def parse_input(input_data: str) -> Optional[Dict[str, Any]]:
    """Parse input with fallback mechanisms for non-JSON or malformed data."""
    try:
        # First try direct JSON parsing
        return json.loads(input_data)
    except json.JSONDecodeError:
        try:
            # Fallback 1: Try to extract JSON from between curly braces
            start = input_data.find('{')
            end = input_data.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(input_data[start:end])
        except json.JSONDecodeError:
            pass
        
        # Fallback 2: Try to parse as key=value pairs
        result = {}
        for pair in input_data.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                result[key.strip()] = value.strip()
        if result:
            return result
        
        # Fallback 3: Return as raw string if all else fails
        return {"raw_input": input_data}
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read()
    
    parsed = parse_input(input_data)
    print(json.dumps(parsed, indent=2))


if __name__ == "__main__":
    main()