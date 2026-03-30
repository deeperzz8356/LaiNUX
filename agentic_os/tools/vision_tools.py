try:
    import pyautogui
except ImportError:
    pyautogui = None
import os
from pathlib import Path
from ..utils.logger import logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def screenshot(filename=None):
    """Takes a full screen capture and saves it to the OS logs folder."""
    try:
        if pyautogui is None:
            return "Vision Error: pyautogui is not installed or unavailable in this environment."

        if filename is None:
            filename = str(PROJECT_ROOT / "logs" / "vision_captured.png")

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Vision: Screen captured at {filename}. I can now see your workspace."
    except Exception as e:
        return f"Vision Error: {str(e)}"

def locate_and_click(image_path):
    """Searches for a specific visual pattern on screen and clicks it if found."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=0.8)
        if location:
            center = pyautogui.center(location)
            pyautogui.click(center)
            return f"Vision: Successfully clicked pattern at {center}."
        else:
            return f"Vision: Pattern '{image_path}' not found on active screen."
    except Exception as e:
        return f"Vision Interaction Error: {str(e)}"

def type_text(text):
    """Types text directly into the active window at normal human speed."""
    try:
        pyautogui.write(text, interval=0.1)
        return f"Vision Interface: Typed '{text}' into the system focus."
    except Exception as e:
        return f"Focus Error: {str(e)}"
