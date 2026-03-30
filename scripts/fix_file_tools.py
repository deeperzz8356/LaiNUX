with open('f:/LaiNUX/agentic_os/tools/file_tools.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    # Skip lines that are plain text or markdown markers
    if line.strip() in ["```python", "```", "Here are the two requested functions:", "Here are the requested functions:"]:
        continue
    if "Here are the two requested functions:" in line:
        continue
    clean_lines.append(line)

with open('f:/LaiNUX/agentic_os/tools/file_tools.py', 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)
