import os
import re

# --- Config ---
memoryPath = os.path.join("Memory", "long_term_memory.md")

CONTEXT_DIR = "Context"

READABLE_FILES = {
    "chat.py": "chat.py",
    "tools.py": "tools.py",
    "config.py": "config.py"
}

# --- Tool Functions ---
def save_response_to_md(response_text, filename="saved_responses.md"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(response_text + "\n\n---\n\n")
    return f"Response written to {filename}"

def create_tool_file(tool_input):
    tool_name = tool_input["name"]
    code = tool_input["code"]
    
    safe_name = re.sub(r'[<>:"/\\|?*\s]+', "_", tool_name).strip("_")
    filename = f"generated_{safe_name}.py"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    return f"Tool '{tool_name}' saved to {filename} (not yet active)"

def manage_memory(tool_input):
    action = tool_input.get("action")
 
    if action == "read":
        if os.path.exists(memoryPath):
            with open(memoryPath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            return content if content else "Memory file is empty."
        return "No memory file found."
 
    elif action == "write":
        content = tool_input.get("content", "")
        os.makedirs("Memory", exist_ok=True)
        with open(memoryPath, "w", encoding="utf-8") as f:
            f.write(content)
        return "Memory updated successfully."
 
    return f"Unknown action: {action}"

def read_code(tool_input):
    filename = tool_input.get("filename")
    if filename not in READABLE_FILES:
        return f"'{filename}' is not readable. Available files: {', '.join(READABLE_FILES)}"
    path = READABLE_FILES[filename]
    if not os.path.exists(path):
        return f"File '{filename}' not found on disk."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def read_context(tool_input):
    action = tool_input.get("action")

    if action == "list":
        if not os.path.exists(CONTEXT_DIR):
            return "Context folder does not exist or is empty."
        files = [f for f in os.listdir(CONTEXT_DIR) if os.path.isfile(os.path.join(CONTEXT_DIR, f))]
        return "\n".join(files) if files else "Context folder is empty."

    elif action == "read":
        filename = tool_input.get("filename")
        path = os.path.join(CONTEXT_DIR, filename)
        if not os.path.exists(path):
            return f"'{filename}' not found in Context folder."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    return f"Unknown action: {action}"

def write_context(tool_input):
    filename = tool_input.get("filename")
    content = tool_input.get("content")

    if not filename:
        return "Error: 'filename' is required."
    if content is None:
        return "Error: 'content' is required."

    # Prevent Path Traversal
    safe_filename = os.path.basename(filename)
    path = os.path.join(CONTEXT_DIR, safe_filename)

    os.makedirs(CONTEXT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"'{safe_filename}' written to Context folder."

# --- Define Tool Schema ---
tools = [
    {
        "type": "web_search_20250305",
        "name": "web_search"
    },
    {
        "name": "save_response",
        "description": "Save the assistant's response to a markdown file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "Text containing the assistant's response"
                }
            },
            "required": ["response"]
        }
    },
    {
        "name": "create_tool",
        "description": (
            "Propose a new tool by writing Python code that integrates with this project's "
            "tool system (which uses Antrhopic's API). "
            "The code field must contain two things: a Python function that performs the action, "
            "and a tool schema dict. Follow this exact format:\n\n"
            "def my_tool_name(tool_input):\n"
            "    # use tool_input['param_name'] to access inputs\n"
            "    return 'result string'\n\n"
            "my_tool_schema = {\n"
            "    'name': 'my_tool_name',\n"
            "    'description': 'What this tool does.',\n"
            "    'input_schema': {\n"
            "        'type': 'object',\n"
            "        'properties': {\n"
            "            'param_name': {'type': 'string', 'description': 'What this param is'}\n"
            "        },\n"
            "        'required': ['param_name']\n"
            "    }\n"
            "}\n\n"
            "Do not include imports, classes, or anything outside these two definitions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "code": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["name", "code"]
        }
    },
    {
        "name": "memory",
        "description": (
            "Read or update your long-term memory about Joseph. "
            "Use action='read' to retrieve current memory before updating. "
            "Use action='write' to overwrite the memory file with updated content. "
            "Always read first, then merge existing memory with new information before writing. "
            "Store information as structured facts, not raw conversation transcripts. "
            "Example format:\n\n"
            "## Projects\n"
            "- AdvancedCombat: C# console RPG (active)\n\n"
            "## Preferences\n"
            "- Prefers concise, technical responses\n\n"
            "## Context\n"
            "- Timezone: EST"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "'read' to load memory, 'write' to overwrite with updated content"
                },
                "content": {
                    "type": "string",
                    "description": "The full memory content to write (only required for action='write')"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "read_code",
        "description": (
            "Read one of your own source files to understand how you work. "
            "Use this when asked to suggest improvements, explain your own behavior, "
            "diagnose a bug, or when you need to understand your current implementation "
            "before proposing changes. Available files: chat.py, tools.py, config.py."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The file to read. One of: chat.py, tools.py, config.py"
                }
            },
            "required": ["filename"]
        }
    },
    {
        "name": "read_context",
        "description": (
            "List or read files from the Context folder. "
            "Use action='list' to see what files are available. "
            "Use action='read' with a filename to read a specific file. "
            "Use this when the user references a document or file they have placed in Context, "
            "or when a task might benefit from available context files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "'list' to see available files, 'read' to retrieve a specific file"
                },
                "filename": {
                    "type": "string",
                    "description": "The file to read (only required for action='read')"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "write_context",
        "description": (
            "Write or overwrite a file in the Context folder. "
            "Use this to edit code or documents the user has placed there. "
            "Always read the file first with read_context before editing, "
            "so you have the full current content before overwriting it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The filename to write inside the Context folder"
                },
                "content": {
                    "type": "string",
                    "description": "The full file content to write"
                }
            },
            "required": ["filename", "content"]
        }
    }
]

def run_tool(name, tool_input):
    if name == "save_response":
        return save_response_to_md(tool_input["response"])
    elif name == "create_tool":
        return create_tool_file(tool_input)
    elif name == "memory":
        return manage_memory(tool_input)
    elif name == "read_code":
        return read_code(tool_input)
    elif name == "read_context":
        return read_context(tool_input)
    elif name == "write_context":
        return write_context(tool_input)
    raise ValueError(f"Unknown tool: {name}")