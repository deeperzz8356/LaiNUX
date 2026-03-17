import os
import sys

def secure_delete(filename, passes=3):
    """Securely delete a file by overwriting its contents before deletion."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found")
    
    try:
        # Get file size
        file_size = os.path.getsize(filename)
        
        with open(filename, 'ba+') as f:
            for _ in range(passes):
                f.seek(0)
                # Overwrite with random data (or zeros for simplicity)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
        
        # Delete the file
        os.remove(filename)
        return True
    except Exception as e:
        print(f"Error during secure deletion: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python secure_delete.py <filename> [passes]")
        sys.exit(1)
    
    filename = sys.argv[1]
    passes = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    secure_delete(filename, passes)