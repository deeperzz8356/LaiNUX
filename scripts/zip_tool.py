import os
import sys
import zipfile
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import zlib
        return True
    except ImportError:
        print("Error: zlib module not available. This is required for zip compression.")
        return False

def zip_directory(source_dir, output_path):
    """Zip a directory and its contents."""
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=source_dir)
                    zipf.write(file_path, arcname)
        print(f"Successfully created zip file: {output_path}")
        return True
    except Exception as e:
        print(f"Error zipping directory: {e}")
        return False

def zip_file(file_path, output_path):
    """Zip a single file."""
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, os.path.basename(file_path))
        print(f"Successfully created zip file: {output_path}")
        return True
    except Exception as e:
        print(f"Error zipping file: {e}")
        return False

def main():
    if not check_dependencies():
        print("Please install Python with zlib support.")
        sys.exit(1)

    if len(sys.argv) < 3:
        print("Usage: python zip_tool.py <source_path> <output_zip_path>")
        print("Example: python zip_tool.py ./my_folder ./output.zip")
        sys.exit(1)

    source_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(source_path):
        print(f"Error: Source path '{source_path}' does not exist.")
        sys.exit(1)

    try:
        if os.path.isdir(source_path):
            success = zip_directory(source_path, output_path)
        else:
            success = zip_file(source_path, output_path)

        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()"