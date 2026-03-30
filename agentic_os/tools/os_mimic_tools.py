import os
import shutil
import pathlib
import threading
import time
from pathlib import Path
from ..utils.logger import logger
from .model_segregator import FileExtensionModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OS_ROOT = os.getenv("LAINUX_OS_ROOT", str(PROJECT_ROOT / "os_root"))
DOWNLOADS_DIR = os.path.join(OS_ROOT, "Downloads")
SEGREGATED_DIRS = {
    "Images": os.path.join(OS_ROOT, "Images"),
    "Audio": os.path.join(OS_ROOT, "Audio"),
    "Documents": os.path.join(OS_ROOT, "Documents"),
    "Others": os.path.join(OS_ROOT, "Others")
}

# Deterministic fallback for common extensions before ML prediction.
EXTENSION_CATEGORY_FALLBACK = {
    ".png": "Images",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".gif": "Images",
    ".webp": "Images",
    ".bmp": "Images",
    ".svg": "Images",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".m4a": "Audio",
    ".aac": "Audio",
    ".ogg": "Audio",
    ".txt": "Documents",
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".md": "Documents",
    ".csv": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".dat": "Others",
    ".exe": "Others",
    ".zip": "Others",
    ".rar": "Others",
    ".7z": "Others",
    ".py": "Others",
    ".js": "Others",
    ".ts": "Others",
    ".json": "Others",
    ".yaml": "Others",
    ".yml": "Others",
}

CATEGORY_NORMALIZATION = {
    "image": "Images",
    "images": "Images",
    "audio": "Audio",
    "audios": "Audio",
    "document": "Documents",
    "documents": "Documents",
    "other": "Others",
    "others": "Others",
}
_watcher_thread = None
_watcher_active = False


def _get_watch_directories():
    """Returns downloads directories to monitor for auto-segregation."""
    return [DOWNLOADS_DIR]


def _normalize_category(category):
    if not category:
        return "Others"
    normalized = CATEGORY_NORMALIZATION.get(str(category).strip().lower())
    return normalized if normalized in SEGREGATED_DIRS else "Others"


def _predict_category(filename, model=None, allow_ml_fallback=False):
    """Deterministic extension routing first; optional ML fallback only when enabled."""
    ext = Path(filename).suffix.lower()
    category = EXTENSION_CATEGORY_FALLBACK.get(ext)
    if category:
        return category

    if allow_ml_fallback and model is not None:
        return _normalize_category(model.predict(filename))

    return "Others"


def _safe_destination_path(target_dir, filename):
    """Builds a non-colliding destination path by suffixing a counter if needed."""
    base_name, ext = os.path.splitext(filename)
    candidate = os.path.join(target_dir, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(target_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    return candidate

def mock_download(file_name, file_type):
    """
    Simulates a file download by creating a mock file in the Downloads folder.
    file_type: 'image', 'audio', 'text', 'other'
    """
    try:
        if not os.path.exists(DOWNLOADS_DIR):
            os.makedirs(DOWNLOADS_DIR)
            
        file_path = os.path.join(DOWNLOADS_DIR, file_name)
        
        # Add appropriate extensions if missing
        ext_map = {
            'image': '.png',
            'audio': '.mp3',
            'text': '.txt',
            'other': '.dat'
        }
        
        if not Path(file_name).suffix and file_type in ext_map:
            file_path += ext_map[file_type]
            
        content = f"Mock {file_type} content for {file_name}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"Download Complete: {os.path.basename(file_path)} saved to Downloads."
    except Exception as e:
        return f"Download Error: {str(e)}"

def smart_segregate(directory=DOWNLOADS_DIR, allow_ml_fallback=False):
    """
    Automatically moves files from a source directory to themed subfolders.
    Logic: Uses extensions initially, but could be 'trained' for more.
    """
    try:
        if not os.path.exists(directory):
            return f"Error: Source directory '{directory}' does not exist."
            
        # Ensure target folders exist
        for folder in SEGREGATED_DIRS.values():
            if not os.path.exists(folder):
                os.makedirs(folder)
                
        entries = [f for f in os.listdir(directory) if os.path.exists(os.path.join(directory, f))]
        moved_files = 0
        moved_dirs = 0
        
        model = FileExtensionModel() if allow_ml_fallback else None
        
        for entry in entries:
            entry_path = os.path.join(directory, entry)

            if os.path.isfile(entry_path):
                category = _predict_category(entry, model=model, allow_ml_fallback=allow_ml_fallback)
                target_folder = SEGREGATED_DIRS[_normalize_category(category)]
                shutil.move(entry_path, os.path.join(target_folder, entry))
                moved_files += 1
                continue

            if os.path.isdir(entry_path):
                # Folders have no extension signal, so route to Others.
                target_folder = SEGREGATED_DIRS["Others"]
                target_path = _safe_destination_path(target_folder, entry)
                shutil.move(entry_path, target_path)
                moved_dirs += 1

        return (
            f"Segregation Complete: Organized {moved_files} files and {moved_dirs} folders "
            f"into themed folders within {OS_ROOT}."
        )
    except Exception as e:
        return f"Segregation Error: {str(e)}"


def repair_misplaced_files(allow_ml_fallback=False):
    """Re-checks already segregated files and moves them to the correct folders."""
    try:
        model = FileExtensionModel() if allow_ml_fallback else None
        moved = 0

        for category_name, category_dir in SEGREGATED_DIRS.items():
            if not os.path.exists(category_dir):
                continue

            files = [f for f in os.listdir(category_dir) if os.path.isfile(os.path.join(category_dir, f))]
            for file in files:
                current_path = os.path.join(category_dir, file)
                predicted_category = _predict_category(file, model=model, allow_ml_fallback=allow_ml_fallback)
                normalized_category = _normalize_category(predicted_category)

                if normalized_category != category_name:
                    target_dir = SEGREGATED_DIRS[normalized_category]
                    target_path = _safe_destination_path(target_dir, file)
                    shutil.move(current_path, target_path)
                    moved += 1

        return f"Repair Complete: Moved {moved} misplaced files to their correct folders."
    except Exception as e:
        return f"Repair Error: {str(e)}"

def smart_search(query, search_root=OS_ROOT):
    """
    Searches across all segregated folders for a file matching the query.
    Returns path, size, and last modified date for a 'smart' feel.
    """
    try:
        matches = []
        for root, dirs, files in os.walk(search_root):
            for file in files:
                if query.lower() in file.lower():
                    full_path = os.path.join(root, file)
                    stats = os.stat(full_path)
                    size_kb = round(stats.st_size / 1024, 2)
                    mtime = time.ctime(stats.st_mtime)
                    rel_path = os.path.relpath(full_path, start=OS_ROOT)
                    matches.append(f"- {rel_path} ({size_kb} KB, Modified: {mtime})")
                    
        if not matches:
            return f"Search Result: No files found matching '{query}' in {OS_ROOT}."
            
        results = "\n".join(matches)
        return f"Smart Search Results for '{query}':\n{results}"
    except Exception as e:
        return f"Search Error: {str(e)}"

def find_by_type(category):
    """Lists all files in a specific category (Images, Audio, Documents, Others)."""
    if category not in SEGREGATED_DIRS:
        return f"Invalid category. Choose from: {list(SEGREGATED_DIRS.keys())}"
    
    dir_path = SEGREGATED_DIRS[category]
    try:
        if not os.path.exists(dir_path):
            return f"Category folder '{category}' is empty/missing."
        
        files = os.listdir(dir_path)
        if not files:
            return f"No files found in {category}."
            
        return f"Files in {category}:\n" + "\n".join([f"- {f}" for f in files])
    except Exception as e:
        return f"Error listing {category}: {str(e)}"

def get_os_file_summary():
    """Provides a high-level summary of all organized files across the OS."""
    summary = ["--- OS File Management Summary ---"]
    total_files = 0
    for cat, path in SEGREGATED_DIRS.items():
        if os.path.exists(path):
            count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            summary.append(f"{cat}: {count} files")
            total_files += count
        else:
            summary.append(f"{cat}: 0 files (Folder missing)")
    
    summary.append(f"Total Organized Files: {total_files}")
    summary.append(f"Watcher Location: {DOWNLOADS_DIR}")
    return "\n".join(summary)

def fine_tune_file_model(extension, category):
    """Exposes the model training functionality to the agent."""
    try:
        model = FileExtensionModel()
        return model.update_weights(extension, category)
    except Exception as e:
        return f"Training Error: {str(e)}"

def start_file_watcher():
    """Starts a background process to automatically segregate 'Downloads' folder."""
    global _watcher_active, _watcher_thread
    if _watcher_active:
        return "File Watcher is already running."
    
    _watcher_active = True
    
    def watch_loop():
        logger.info("AGENTIC OS: File Watcher Thread Started.")
        watch_dirs = _get_watch_directories()
        while _watcher_active:
            try:
                for watch_dir in watch_dirs:
                    if not os.path.exists(watch_dir):
                        continue

                    entries = [f for f in os.listdir(watch_dir) if os.path.exists(os.path.join(watch_dir, f))]
                    if entries:
                        logger.info(f"AGENTIC OS: Detected {len(entries)} new item(s) in {watch_dir}. Segregating...")
                        res = smart_segregate(directory=watch_dir)
                        logger.info(f"AGENTIC OS: {res}")
                time.sleep(5) # Poll every 5 seconds
            except Exception as e:
                logger.error(f"Watcher Loop Error: {e}")
                time.sleep(10)
                
    _watcher_thread = threading.Thread(target=watch_loop, daemon=True)
    _watcher_thread.start()
    return "Agentic File Watcher Activated: Now monitoring 'Downloads' for automatic segregation."

def stop_file_watcher():
    """Stops the background file watcher."""
    global _watcher_active
    _watcher_active = False
    return "Agentic File Watcher Deactivated."

def get_file_manager_status():
    """Returns the status of the smart file management background tasks."""
    status = "Active" if _watcher_active else "Inactive"
    watch_dirs = _get_watch_directories()
    return f"Smart File Manager Status: [Watcher: {status}] Monitoring: {', '.join(watch_dirs)}"


