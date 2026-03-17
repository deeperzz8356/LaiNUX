import sqlite3
import os

def get_session_summary(db_path="f:/LaiNUX/agent_memory.db"):
    """Reads the agent memory and extracts a high-level summary of the last tasks."""
    if not os.path.exists(db_path):
        return "Memory database not found yet. The AI is still warming up."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get last 5 tasks
        cursor.execute("SELECT id, goal, status, timestamp FROM tasks ORDER BY id DESC LIMIT 5")
        tasks = cursor.fetchall()
        
        # Get last 5 wisdom nuggets
        cursor.execute("SELECT learned_lesson, timestamp FROM wisdom ORDER BY id DESC LIMIT 5")
        wisdom = cursor.fetchall()
        
        conn.close()
        
        summary = "--- 🧬 LAINUX PARTNER BRIEFING ---\n\n"
        summary += "Recent Self-Evolution Tasks:\n"
        for t in tasks:
            summary += f"[{t[3]}] ID:{t[0]} | {t[1][:50]}... | STATUS: {t[2]}\n"
        
        summary += "\nNeural Wisdom Gained:\n"
        if not wisdom:
            summary += "- No wisdom nuggets recorded in this cycle yet.\n"
        for w in wisdom:
            summary += f"- {w[0]}\n"
            
        return summary
    except Exception as e:
        return f"Error reading memory: {str(e)}"

if __name__ == "__main__":
    print(get_session_summary())
