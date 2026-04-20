import os

CONTEXT_DIR = "Context"


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
    old_str = tool_input.get("old_str")
    new_str = tool_input.get("new_str")

    if not filename:
        return "Error: 'filename' is required."

    safe_filename = os.path.basename(filename)
    path = os.path.join(CONTEXT_DIR, safe_filename)

    # Patch mode
    if old_str is not None and content is None:
        if not os.path.exists(path):
            return f"Error: '{safe_filename}' not found, cannot patch."
        with open(path, "r", encoding="utf-8") as f:
            current = f.read()
        if old_str not in current:
            return f"Error: old_str not found in '{safe_filename}'."
        updated = current.replace(old_str, new_str or "", 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
        return f"'{safe_filename}' patched successfully."

    # Full overwrite mode
    if content is None:
        return "Error: 'content' is required for full overwrite, or provide 'old_str'/'new_str' for patch mode."

    os.makedirs(CONTEXT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"'{safe_filename}' written to Context folder."


tools = [
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
            "Write or edit a file in the Context folder. Two modes are available:\n\n"
            "**Full overwrite** — provide 'filename' and 'content' to replace the entire file. "
            "Always read the file first with read_context before using this mode.\n\n"
            "**Patch mode** — provide 'filename', 'old_str', and 'new_str' to replace a specific "
            "section without rewriting the whole file. Prefer this mode for small edits, as it is "
            "more reliable and requires less output. 'old_str' must exactly match the current file content."
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
                    "description": "The full file content to write (full overwrite mode only)"
                },
                "old_str": {
                    "type": "string",
                    "description": "The exact string to find and replace (patch mode only)"
                },
                "new_str": {
                    "type": "string",
                    "description": "The string to replace old_str with (patch mode only, omit to delete)"
                }
            },
            "required": ["filename"]
        }
    }
]


def run(name, tool_input):
    if name == "read_context":
        return read_context(tool_input)
    if name == "write_context":
        return write_context(tool_input)
    return None
