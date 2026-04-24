import os

TOOLS_DIR = os.path.join(os.path.dirname(__file__))
SAVED_RESPONSES_DIR = "SavedResponses"

STATIC_FILES = {
    "chat.py": "chat.py",
    "config.py": "config.py",
}

def _readable_files():
    """Build the full map of readable files at call time, including all tools/*.py modules."""
    files = dict(STATIC_FILES)
    if os.path.isdir(TOOLS_DIR):
        for fname in os.listdir(TOOLS_DIR):
            if fname.endswith(".py"):
                display = f"tools/{fname}"
                files[display] = os.path.join(TOOLS_DIR, fname)
    return files


def save_response_to_md(tool_input):
    response_text = tool_input.get("response")
    filename = tool_input.get("filename", "saved_responses.md")
 
    if not response_text:
        return "Error: 'response' is required but was not provided."
 
    os.makedirs(SAVED_RESPONSES_DIR, exist_ok=True)
    path = os.path.join(SAVED_RESPONSES_DIR, os.path.basename(filename))
 
    with open(path, "a", encoding="utf-8") as f:
        f.write(response_text + "\n\n---\n\n")
    return f"Response written to {path}"



def read_code(tool_input):
    filename = tool_input.get("filename")
    readable = _readable_files()
    if filename not in readable:
        return f"'{filename}' is not readable. Available files: {', '.join(sorted(readable))}"
    path = readable[filename]
    if not os.path.exists(path):
        return f"File '{filename}' not found on disk."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


tools = [
    {
        "name": "save_response",
        "description": "Save the assistant's response to a markdown file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "Text containing the assistant's response"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional filename to save to (default: saved_responses.md)"
                }
            },
            "required": ["response"]
        }
    },
    {
        "name": "read_code",
        "description": (
            "Read one of your own source files to understand how you work. "
            "Use this when asked to suggest improvements, explain your own behavior, "
            "diagnose a bug, or when you need to understand your current implementation "
            "before proposing changes. "
            "Available files: chat.py, config.py, and all modules under tools/ "
            "(e.g. tools/__init__.py, tools/files.py, tools/projects.py, etc). "
            "If unsure of the exact filename, call this tool with an invalid name "
            "and the error response will list all available files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The file to read, e.g. 'chat.py' or 'tools/projects.py'"
                }
            },
            "required": ["filename"]
        }
    }
]


def run(name, tool_input):
    if name == "save_response":
        return save_response_to_md(tool_input)
    if name == "read_code":
        return read_code(tool_input)
    return None
