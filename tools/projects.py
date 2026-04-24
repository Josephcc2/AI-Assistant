import os
import shutil

PROJECT_DIR = "Projects"


# --- Path helpers ---

def _safe_project_path(project_name, filepath=None):
    """
    Resolve a safe path inside Projects/<project>, preventing traversal attacks.
    filepath may include subdirectory components (e.g. 'src/main.py') but must
    not contain '..' segments.
    """
    safe_project = os.path.basename(project_name)
    if not safe_project:
        return None, None, "Error: Invalid project name."

    project_path = os.path.join(PROJECT_DIR, safe_project)

    if filepath:
        # Reject any '..' segments
        parts = filepath.replace("\\", "/").split("/")
        if ".." in parts or "" in parts[:-1]:
            return None, None, "Error: Invalid filepath — '..' is not allowed."
        normalized = os.path.join(*parts)
        full_path = os.path.join(project_path, normalized)
        # Final check: resolved path must still be inside project_path
        if not os.path.realpath(full_path).startswith(os.path.realpath(project_path)):
            return None, None, "Error: Filepath escapes the project directory."
        return project_path, full_path, None

    return project_path, None, None


def _list_tree(root, prefix=""):
    """Recursively build an indented tree string of a directory."""
    lines = []
    try:
        entries = sorted(os.listdir(root))
    except PermissionError:
        return []
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        full = os.path.join(root, entry)
        lines.append(prefix + connector + entry)
        if os.path.isdir(full):
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(_list_tree(full, prefix + extension))
    return lines


# --- Tool functions ---

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
    with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
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
        subfolder = tool_input.get("subfolder")
        if not project_name:
            return "Error: 'project_name' is required for action='list_files'."
        project_path, _, err = _safe_project_path(project_name)
        if err:
            return err
        if not os.path.exists(project_path):
            return f"Error: Project '{project_name}' does not exist."

        if subfolder:
            _, scan_path, err = _safe_project_path(project_name, subfolder)
            if err:
                return err
            if not os.path.exists(scan_path):
                return f"Error: Subfolder '{subfolder}' does not exist in project '{project_name}'."
            if not os.path.isdir(scan_path):
                return f"Error: '{subfolder}' is a file, not a folder."
        else:
            scan_path = project_path

        entries = sorted(os.listdir(scan_path))
        if not entries:
            return "Empty."
        lines = []
        for e in entries:
            marker = "/" if os.path.isdir(os.path.join(scan_path, e)) else ""
            lines.append(e + marker)
        return "\n".join(lines)

    elif action == "tree":
        project_name = tool_input.get("project_name")
        if not project_name:
            return "Error: 'project_name' is required for action='tree'."
        project_path, _, err = _safe_project_path(project_name)
        if err:
            return err
        if not os.path.exists(project_path):
            return f"Error: Project '{project_name}' does not exist."
        lines = [project_name] + _list_tree(project_path)
        return "\n".join(lines)

    return f"Unknown action: {action}"


def create_subfolder(tool_input):
    project_name = tool_input.get("project_name")
    subfolder = tool_input.get("subfolder")

    if not project_name:
        return "Error: 'project_name' is required."
    if not subfolder:
        return "Error: 'subfolder' is required."

    project_path, folder_path, err = _safe_project_path(project_name, subfolder)
    if err:
        return err
    if not os.path.exists(project_path):
        return f"Error: Project '{project_name}' does not exist."
    if os.path.exists(folder_path):
        return f"Error: '{subfolder}' already exists in project '{project_name}'."

    os.makedirs(folder_path, exist_ok=True)
    return f"Subfolder '{subfolder}' created in project '{project_name}'."


def delete_subfolder(tool_input):
    project_name = tool_input.get("project_name")
    subfolder = tool_input.get("subfolder")
    confirm = tool_input.get("confirm")

    if not project_name:
        return "Error: 'project_name' is required."
    if not subfolder:
        return "Error: 'subfolder' is required."
    if confirm != "yes":
        return "Error: Set confirm='yes' to permanently delete a subfolder and all its contents."

    project_path, folder_path, err = _safe_project_path(project_name, subfolder)
    if err:
        return err
    if not os.path.exists(folder_path):
        return f"Error: '{subfolder}' does not exist in project '{project_name}'."
    if not os.path.isdir(folder_path):
        return f"Error: '{subfolder}' is a file, not a folder. Use delete_project_file instead."

    shutil.rmtree(folder_path)
    return f"Subfolder '{subfolder}' and all its contents deleted from project '{project_name}'."


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
    if os.path.isdir(file_path):
        return f"Error: '{filename}' is a folder, not a file."
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

    # Auto-create intermediate subdirectories
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

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


def move_project_file(tool_input):
    project_name = tool_input.get("project_name")
    src = tool_input.get("src")
    dst = tool_input.get("dst")

    if not project_name:
        return "Error: 'project_name' is required."
    if not src:
        return "Error: 'src' is required."
    if not dst:
        return "Error: 'dst' is required."

    project_path, src_path, err = _safe_project_path(project_name, src)
    if err:
        return err
    _, dst_path, err = _safe_project_path(project_name, dst)
    if err:
        return err

    if not os.path.exists(src_path):
        return f"Error: '{src}' not found in project '{project_name}'."
    if src == "README.md":
        return "Error: Cannot move README.md."
    if os.path.exists(dst_path):
        return f"Error: '{dst}' already exists. Delete it first if you want to overwrite."

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.move(src_path, dst_path)
    return f"Moved '{src}' → '{dst}' in project '{project_name}'."


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
    if os.path.isdir(file_path):
        return f"Error: '{filename}' is a folder. Use delete_subfolder instead."

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

    shutil.rmtree(project_path)
    return f"Project '{project_name}' and all its files have been deleted."


# --- Tool schemas ---

tools = [
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
                "project_name": {"type": "string", "description": "The name of the project (used as the folder name)"},
                "readme": {"type": "string", "description": "Markdown content for the project's README.md."}
            },
            "required": ["project_name", "readme"]
        }
    },
    {
        "name": "list_projects",
        "description": (
            "List projects or inspect their contents.\n\n"
            "action='list_projects' — list all projects.\n"
            "action='list_files' — list files and subfolders in a project root or a specific subfolder "
            "(provide 'subfolder' to look inside a subfolder). Folders are shown with a trailing '/'.\n"
            "action='tree' — show the full recursive file tree of a project."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "'list_projects', 'list_files', or 'tree'"},
                "project_name": {"type": "string", "description": "Required for 'list_files' and 'tree'"},
                "subfolder": {"type": "string", "description": "Optional subfolder path to list (for 'list_files' only)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "create_subfolder",
        "description": (
            "Create a subfolder inside a project. Supports nested paths (e.g. 'src/utils'). "
            "The project must already exist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "The name of the project"},
                "subfolder": {"type": "string", "description": "Subfolder path to create (e.g. 'src' or 'src/utils')"}
            },
            "required": ["project_name", "subfolder"]
        }
    },
    {
        "name": "delete_subfolder",
        "description": (
            "Permanently delete a subfolder and all its contents from a project. "
            "Requires confirm='yes'. Use list_projects with action='tree' to review contents before deleting."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "The name of the project"},
                "subfolder": {"type": "string", "description": "Subfolder path to delete (e.g. 'src/utils')"},
                "confirm": {"type": "string", "description": "Must be 'yes' to confirm deletion"}
            },
            "required": ["project_name", "subfolder", "confirm"]
        }
    },
    {
        "name": "read_project_file",
        "description": (
            "Read a file from inside a project. "
            "'filename' may include a subfolder path (e.g. 'src/main.py'). "
            "Use list_projects with action='tree' to find files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "The name of the project"},
                "filename": {"type": "string", "description": "File path relative to the project root (e.g. 'src/main.py')"}
            },
            "required": ["project_name", "filename"]
        }
    },
    {
        "name": "write_project_file",
        "description": (
            "Write or edit a file inside a project. 'filename' may include a subfolder path "
            "(e.g. 'src/main.py') — intermediate folders are created automatically.\n\n"
            "**Full overwrite** — provide 'filename' and 'content'.\n"
            "**Patch mode** — provide 'filename', 'old_str', and 'new_str' for targeted edits. "
            "Prefer patch mode for small changes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "The name of the project"},
                "filename": {"type": "string", "description": "File path relative to the project root (e.g. 'src/main.py')"},
                "content": {"type": "string", "description": "Full file content (full overwrite mode only)"},
                "old_str": {"type": "string", "description": "Exact string to find and replace (patch mode only)"},
                "new_str": {"type": "string", "description": "Replacement string (patch mode only, omit to delete)"}
            },
            "required": ["project_name", "filename"]
        }
    },
    {
        "name": "move_project_file",
        "description": (
            "Move or rename a file within a project. Both 'src' and 'dst' are paths relative to "
            "the project root and may include subfolders (e.g. src='main.py', dst='src/main.py'). "
            "Intermediate destination folders are created automatically. Cannot move README.md."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "The name of the project"},
                "src": {"type": "string", "description": "Current file path relative to the project root"},
                "dst": {"type": "string", "description": "Destination file path relative to the project root"}
            },
            "required": ["project_name", "src", "dst"]
        }
    },
    {
        "name": "delete_project_file",
        "description": (
            "Delete a file from a project. 'filename' may include a subfolder path. "
            "Cannot delete README.md. Use delete_subfolder to remove entire folders."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "The name of the project"},
                "filename": {"type": "string", "description": "File path relative to the project root"}
            },
            "required": ["project_name", "filename"]
        }
    },
    {
        "name": "delete_project",
        "description": (
            "Permanently delete an entire project and all its contents. "
            "Irreversible — requires confirm='yes'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "The name of the project to delete"},
                "confirm": {"type": "string", "description": "Must be 'yes' to confirm permanent deletion"}
            },
            "required": ["project_name", "confirm"]
        }
    }
]


def run(name, tool_input):
    dispatch = {
        "create_project":     create_project,
        "list_projects":      list_projects,
        "create_subfolder":   create_subfolder,
        "delete_subfolder":   delete_subfolder,
        "read_project_file":  read_project_file,
        "write_project_file": write_project_file,
        "move_project_file":  move_project_file,
        "delete_project_file": delete_project_file,
        "delete_project":     delete_project,
    }
    if name in dispatch:
        return dispatch[name](tool_input)
    return None
