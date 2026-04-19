import os
import re

# --- Config ---
memoryPath = os.path.join("Memory", "long_term_memory.md")

CONTEXT_DIR = "Context"
CREATE_TOOL_DIR = "SuggestedTools"
PROJECT_DIR = "Projects"

def _safe_project_path(project_name, filename=None):
    """Resolve a safe path inside Projects/, preventing traversal attacks."""
    safe_project = os.path.basename(project_name)
    if not safe_project:
        return None, None, "Error: Invalid project name."
    project_path = os.path.join(PROJECT_DIR, safe_project)
    if filename:
        safe_file = os.path.basename(filename)
        if not safe_file:
            return None, None, "Error: Invalid filename."
        return project_path, os.path.join(project_path, safe_file), None
    return project_path, None, None

READABLE_FILES = {
    "chat.py": "chat.py",
    "tools.py": "tools.py",
    "config.py": "config.py"
}

# --- Tool Functions ---
def save_response_to_md(tool_input):
    response_text = tool_input.get("response")
    filename = tool_input.get("filename", "saved_responses.md")

    if not response_text:
        return "Error: 'response' is required but was not provided."

    with open(filename, "a", encoding="utf-8") as f:
        f.write(response_text + "\n\n---\n\n")
    return f"Response written to {filename}"

def create_tool_file(tool_input):
    tool_name = tool_input["name"]
    code = tool_input["code"]

    if not tool_name:
        return "Error: 'name' is required."
    if not code:
        return "Error: 'code' is required but was not provided. Please retry with the full function and schema code."
    
    safe_name = re.sub(r'[<>:"/\\|?*\s]+', "_", tool_name).strip("_")
    os.makedirs(CREATE_TOOL_DIR, exist_ok=True)
    filename = os.path.join(CREATE_TOOL_DIR, f"generated_{safe_name}.py")

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

# Context
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

# Projects
def create_project(tool_input):
    project_name = tool_input.get("project_name")
    readme = tool_input.get("readme")
 
    if not project_name:
        return "Error: 'project_name' is required."
    if not readme:
        return "Error: 'readme' is required. Describe what this project is."
 
    project_path, _, err = _safe_project_path(project_name)
    if err:
        return err
 
    if os.path.exists(project_path):
        return f"Error: Project '{project_name}' already exists."
 
    os.makedirs(project_path, exist_ok=True)
    readme_path = os.path.join(project_path, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    return f"Project '{project_name}' created with README.md."
 
def list_projects(tool_input):
    action = tool_input.get("action", "list_projects")
 
    if action == "list_projects":
        if not os.path.exists(PROJECT_DIR):
            return "No projects found."
        projects = [d for d in os.listdir(PROJECT_DIR) if os.path.isdir(os.path.join(PROJECT_DIR, d))]
        return "\n".join(projects) if projects else "No projects found."
 
    elif action == "list_files":
        project_name = tool_input.get("project_name")
        if not project_name:
            return "Error: 'project_name' is required for action='list_files'."
        project_path, _, err = _safe_project_path(project_name)
        if err:
            return err
        if not os.path.exists(project_path):
            return f"Error: Project '{project_name}' does not exist."
        files = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))]
        return "\n".join(files) if files else "Project folder is empty."
 
    return f"Unknown action: {action}"
 
def read_project_file(tool_input):
    project_name = tool_input.get("project_name")
    filename = tool_input.get("filename")
 
    if not project_name:
        return "Error: 'project_name' is required."
    if not filename:
        return "Error: 'filename' is required."
 
    project_path, file_path, err = _safe_project_path(project_name, filename)
    if err:
        return err
    if not os.path.exists(file_path):
        return f"Error: '{filename}' not found in project '{project_name}'."
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
 
def write_project_file(tool_input):
    project_name = tool_input.get("project_name")
    filename = tool_input.get("filename")
    content = tool_input.get("content")
    old_str = tool_input.get("old_str")
    new_str = tool_input.get("new_str")
 
    if not project_name:
        return "Error: 'project_name' is required."
    if not filename:
        return "Error: 'filename' is required."
 
    project_path, file_path, err = _safe_project_path(project_name, filename)
    if err:
        return err
    if not os.path.exists(project_path):
        return f"Error: Project '{project_name}' does not exist. Create it first with create_project."
 
    # Patch mode
    if old_str is not None and content is None:
        if not os.path.exists(file_path):
            return f"Error: '{filename}' not found in project '{project_name}', cannot patch."
        with open(file_path, "r", encoding="utf-8") as f:
            current = f.read()
        if old_str not in current:
            return f"Error: old_str not found in '{filename}'."
        updated = current.replace(old_str, new_str or "", 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)
        return f"'{filename}' patched successfully in project '{project_name}'."
 
    # Full overwrite mode
    if content is None:
        return "Error: 'content' is required for full overwrite, or provide 'old_str'/'new_str' for patch mode."
 
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"'{filename}' written to project '{project_name}'."
 
def delete_project_file(tool_input):
    project_name = tool_input.get("project_name")
    filename = tool_input.get("filename")
 
    if not project_name:
        return "Error: 'project_name' is required."
    if not filename:
        return "Error: 'filename' is required."
    if filename == "README.md":
        return "Error: Cannot delete README.md. Every project must have a README."
 
    project_path, file_path, err = _safe_project_path(project_name, filename)
    if err:
        return err
    if not os.path.exists(file_path):
        return f"Error: '{filename}' not found in project '{project_name}'."
 
    os.remove(file_path)
    return f"'{filename}' deleted from project '{project_name}'."
 
def delete_project(tool_input):
    project_name = tool_input.get("project_name")
    confirm = tool_input.get("confirm")
 
    if not project_name:
        return "Error: 'project_name' is required."
    if confirm != "yes":
        return "Error: Set confirm='yes' to permanently delete a project and all its files."
 
    project_path, _, err = _safe_project_path(project_name)
    if err:
        return err
    if not os.path.exists(project_path):
        return f"Error: Project '{project_name}' does not exist."
 
    import shutil
    shutil.rmtree(project_path)
    return f"Project '{project_name}' and all its files have been deleted."

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
            "Read or update your long-term memory about John. "
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
    # Context
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
    },
    # Projects
    {
        "name": "create_project",
        "description": (
            "Create a new project folder inside the Projects directory. "
            "Each project must have a README describing what it is and its purpose. "
            "Use this before writing any project files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project (used as the folder name)"
                },
                "readme": {
                    "type": "string",
                    "description": "Markdown content for the project's README.md file. Describe the project's purpose, structure, and any relevant notes."
                }
            },
            "required": ["project_name", "readme"]
        }
    },
    {
        "name": "list_projects",
        "description": (
            "List all projects or list files within a specific project. "
            "Use action='list_projects' to see all available projects. "
            "Use action='list_files' with a project_name to see files inside a project."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "'list_projects' to see all projects, 'list_files' to see files in a specific project"
                },
                "project_name": {
                    "type": "string",
                    "description": "The project to list files for (only required for action='list_files')"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "read_project_file",
        "description": (
            "Read a file from inside a project folder. "
            "Use list_projects with action='list_files' first if unsure what files exist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project"
                },
                "filename": {
                    "type": "string",
                    "description": "The file to read inside the project folder"
                }
            },
            "required": ["project_name", "filename"]
        }
    },
    {
        "name": "write_project_file",
        "description": (
            "Write or edit a file inside a project folder. Two modes available:\n\n"
            "**Full overwrite** — provide 'project_name', 'filename', and 'content' to write the entire file.\n\n"
            "**Patch mode** — provide 'project_name', 'filename', 'old_str', and 'new_str' to replace a specific "
            "section. Prefer this for small edits. 'old_str' must exactly match the current file content.\n\n"
            "The project must already exist. Use create_project first if needed. "
            "Always read the file first with read_project_file before doing a full overwrite."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project"
                },
                "filename": {
                    "type": "string",
                    "description": "The filename to write inside the project folder"
                },
                "content": {
                    "type": "string",
                    "description": "Full file content (full overwrite mode only)"
                },
                "old_str": {
                    "type": "string",
                    "description": "Exact string to find and replace (patch mode only)"
                },
                "new_str": {
                    "type": "string",
                    "description": "Replacement string (patch mode only, omit to delete)"
                }
            },
            "required": ["project_name", "filename"]
        }
    },
    {
        "name": "delete_project_file",
        "description": (
            "Delete a specific file from a project folder. "
            "Cannot delete README.md — every project must keep its README. "
            "Use list_projects with action='list_files' to confirm the filename before deleting."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project"
                },
                "filename": {
                    "type": "string",
                    "description": "The file to delete inside the project folder"
                }
            },
            "required": ["project_name", "filename"]
        }
    },
    {
        "name": "delete_project",
        "description": (
            "Permanently delete an entire project folder and all its files. "
            "This is irreversible. You must set confirm='yes' to proceed. "
            "Use list_projects to confirm the project name before deleting."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "The name of the project to delete"
                },
                "confirm": {
                    "type": "string",
                    "description": "Must be 'yes' to confirm permanent deletion"
                }
            },
            "required": ["project_name", "confirm"]
        }
    }
]

def run_tool(name, tool_input):
    if name == "save_response":
        return save_response_to_md(tool_input)
    elif name == "create_tool":
        return create_tool_file(tool_input)
    elif name == "memory":
        return manage_memory(tool_input)
    elif name == "read_code":
        return read_code(tool_input)
    # Context
    elif name == "read_context":
        return read_context(tool_input)
    elif name == "write_context":
        return write_context(tool_input)
    # Projects
    elif name == "create_project":
        return create_project(tool_input)
    elif name == "list_projects":
        return list_projects(tool_input)
    elif name == "read_project_file":
        return read_project_file(tool_input)
    elif name == "write_project_file":
        return write_project_file(tool_input)
    elif name == "delete_project_file":
        return delete_project_file(tool_input)
    elif name == "delete_project":
        return delete_project(tool_input)
    return (
        f"Error: Unknown tool '{name}'. Available tools: save_response, create_tool, memory, read_code, read_context, write_context, "
        "create_project, list_projects, read_project_file, write_project_file, delete_project_file, delete_project."
    )
