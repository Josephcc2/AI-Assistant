import os
import shutil

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

    shutil.rmtree(project_path)
    return f"Project '{project_name}' and all its files have been deleted."


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
                "project_name": {
                    "type": "string",
                    "description": "The name of the project (used as the folder name)"
                },
                "readme": {
                    "type": "string",
                    "description": "Markdown content for the project's README.md. Describe the project's purpose, structure, and any relevant notes."
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
                "project_name": {"type": "string", "description": "The name of the project"},
                "filename": {"type": "string", "description": "The file to read inside the project folder"}
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
                "project_name": {"type": "string", "description": "The name of the project"},
                "filename": {"type": "string", "description": "The filename to write inside the project folder"},
                "content": {"type": "string", "description": "Full file content (full overwrite mode only)"},
                "old_str": {"type": "string", "description": "Exact string to find and replace (patch mode only)"},
                "new_str": {"type": "string", "description": "Replacement string (patch mode only, omit to delete)"}
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
                "project_name": {"type": "string", "description": "The name of the project"},
                "filename": {"type": "string", "description": "The file to delete inside the project folder"}
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
                "project_name": {"type": "string", "description": "The name of the project to delete"},
                "confirm": {"type": "string", "description": "Must be 'yes' to confirm permanent deletion"}
            },
            "required": ["project_name", "confirm"]
        }
    }
]


def run(name, tool_input):
    dispatch = {
        "create_project": create_project,
        "list_projects": list_projects,
        "read_project_file": read_project_file,
        "write_project_file": write_project_file,
        "delete_project_file": delete_project_file,
        "delete_project": delete_project,
    }
    if name in dispatch:
        return dispatch[name](tool_input)
    return None
