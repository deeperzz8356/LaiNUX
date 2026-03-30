import os
import sys

# Add project root to path
sys.path.append("f:/LaiNUX")

from agentic_os.tools.os_mimic_tools import mock_download, smart_segregate, smart_search

print("--- PHASE 1: MOCK DOWNLOADS ---")
print(mock_download("beach_photo", "image"))
print(mock_download("favorite_song", "audio"))
print(mock_download("meeting_notes", "text"))
print(mock_download("unknown_script", "other"))

print("\n--- PHASE 2: AUTOMATIC SEGREGATION ---")
print(smart_segregate())

print("\n--- PHASE 3: SMART SEARCH ---")
print(smart_search("beach"))
print(smart_search("favorite"))
print(smart_search("notes"))
