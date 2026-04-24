import os
import re
import ast
from datetime import datetime

SUGGESTED_DIR = "SuggestedTools"
CUSTOM_PATH = os.path.join(os.path.dirname(__file__), "custom.py")
LOG_PATH = os.path.join("Logs", "implement_log.md")


# --- Parsing ---

def _extract_parts(source):
    """
    Extract the tool function source, schema dict source, tool name, and function name
    from a generated tool file. Returns (func_source, schema_source, tool_name, func_name)
    or raises ValueError on parse failure.
    """
    tree = ast.parse(source)

    # Find the single top-level function definition
    func_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and
                  isinstance(n, ast.stmt) and n in tree.body]
    if not func_nodes:
        raise ValueError("No top-level function definition found in file.")
    if len(func_nodes) > 1:
        raise ValueError("Multiple top-level functions found. File must define exactly one tool function.")

    func_node = func_nodes[0]
    func_name = func_node.name

    # Extract function source lines
    lines = source.splitlines()
    func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

    # Find assignment like: my_tool_schema = { ... }
    schema_nodes = [
        n for n in tree.body
        if isinstance(n, ast.Assign) and
        any(isinstance(t, ast.Name) and t.id.endswith("schema") for t in n.targets)
    ]
    if not schema_nodes:
        raise ValueError("No schema assignment (e.g. my_tool_schema = {...}) found in file.")

    schema_node = schema_nodes[0]
    schema_source = "\n".join(lines[schema_node.lineno - 1 : schema_node.end_lineno])

    # Evaluate just the schema dict to pull the tool name
    schema_dict = ast.literal_eval(schema_node.value)
    tool_name = schema_dict.get("name")
    if not tool_name:
        raise ValueError("Schema dict is missing a 'name' field.")

    # Return the raw dict source (right-hand side of the assignment)
    rhs_source = "\n".join(lines[schema_node.lineno - 1 : schema_node.end_lineno])
    # Strip "varname = " prefix to get just the dict literal
    rhs_source = re.sub(r"^\s*\w+\s*=\s*", "", rhs_source, count=1)

    return func_source, rhs_source, tool_name, func_name


# --- Custom.py patching ---

def _is_already_implemented(tool_name):
    with open(CUSTOM_PATH, "r", encoding="utf-8") as f:
        return f'"{tool_name}"' in f.read()


def _patch_custom(func_source, schema_source, tool_name, func_name):
    with open(CUSTOM_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "# <<FUNCTIONS>>" not in content:
        raise ValueError("custom.py is missing the # <<FUNCTIONS>> sentinel. It may have been manually edited.")
    if "# <<SCHEMAS>>" not in content:
        raise ValueError("custom.py is missing the # <<SCHEMAS>> sentinel.")
    if "# <<DISPATCH>>" not in content:
        raise ValueError("custom.py is missing the # <<DISPATCH>> sentinel.")

    content = content.replace(
        "# <<FUNCTIONS>>",
        f"# <<FUNCTIONS>>\n\n{func_source}\n"
    )
    content = content.replace(
        "# <<SCHEMAS>>",
        f"# <<SCHEMAS>>\n    {schema_source},"
    )
    content = content.replace(
        "# <<DISPATCH>>",
        f'# <<DISPATCH>>\n    "{tool_name}": {func_name},'
    )

    with open(CUSTOM_PATH, "w", encoding="utf-8") as f:
        f.write(content)


# --- Logging ---

def _write_log(tool_name, filename, success, note=""):
    os.makedirs("Logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "✅ Success" if success else "❌ Failed"
    entry = (
        f"## {timestamp}\n"
        f"- **Tool:** `{tool_name}`\n"
        f"- **Source file:** `{filename}`\n"
        f"- **Status:** {status}\n"
    )
    if note:
        entry += f"- **Note:** {note}\n"
    entry += "\n---\n\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


# --- Main tool function ---

def implement_tool(tool_input):
    filename = tool_input.get("filename")
    if not filename:
        return "Error: 'filename' is required. Use list_suggested to see available files."

    safe_filename = os.path.basename(filename)
    filepath = os.path.join(SUGGESTED_DIR, safe_filename)

    if not os.path.exists(filepath):
        available = os.listdir(SUGGESTED_DIR) if os.path.exists(SUGGESTED_DIR) else []
        return f"Error: '{safe_filename}' not found in SuggestedTools. Available: {', '.join(available) or 'none'}"

    # Parse the file before asking the user, so we can show them what they're approving
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        func_source, schema_source, tool_name, func_name = _extract_parts(source)
    except ValueError as e:
        _write_log(safe_filename, safe_filename, success=False, note=str(e))
        return f"Error parsing '{safe_filename}': {e}"

    if _is_already_implemented(tool_name):
        return f"Error: Tool '{tool_name}' is already implemented in custom.py."

    # Hard-coded user confirmation — cannot be bypassed by the AI
    print(f"\n{'='*60}")
    print(f"  implement_tool — USER CONFIRMATION REQUIRED")
    print(f"{'='*60}")
    print(f"  Tool name : {tool_name}")
    print(f"  Source    : {safe_filename}")
    print(f"  Function  : {func_name}()")
    print(f"\n  --- Function preview ---")
    preview = func_source[:500] + ("..." if len(func_source) > 500 else "")
    for line in preview.splitlines():
        print(f"  {line}")
    print(f"{'='*60}")
    confirmation = input("  Type 'implement' to confirm, anything else to cancel: ").strip()
    print(f"{'='*60}\n")

    if confirmation != "implement":
        _write_log(tool_name, safe_filename, success=False, note="Cancelled by user.")
        return f"Cancelled. Tool '{tool_name}' was not implemented."

    try:
        _patch_custom(func_source, schema_source, tool_name, func_name)
    except Exception as e:
        _write_log(tool_name, safe_filename, success=False, note=str(e))
        return f"Error writing to custom.py: {e}"

    _write_log(tool_name, safe_filename, success=True)
    return (
        f"Tool '{tool_name}' successfully implemented into tools/custom.py. "
        f"Restart the assistant for it to become active."
    )


def list_suggested(tool_input):
    if not os.path.exists(SUGGESTED_DIR):
        return "SuggestedTools folder does not exist or is empty."
    files = [f for f in os.listdir(SUGGESTED_DIR) if f.endswith(".py")]
    return "\n".join(files) if files else "No suggested tools found."


tools = [
    {
        "name": "list_suggested",
        "description": (
            "List all tool files available in the SuggestedTools folder. "
            "Use this before implement_tool to see what can be implemented."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "implement_tool",
        "description": (
            "Implement a suggested tool from the SuggestedTools folder into the live codebase. "
            "The tool will be added to tools/custom.py and become active after the assistant restarts. "
            "This requires explicit confirmation from the user at the terminal — it cannot be auto-approved. "
            "Use list_suggested first to see available files. "
            "A log of all implement_tool actions is kept in Logs/implement_log.md."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The filename in SuggestedTools to implement (e.g. 'generated_my_tool.py')"
                }
            },
            "required": ["filename"]
        }
    }
]


def run(name, tool_input):
    if name == "implement_tool":
        return implement_tool(tool_input)
    if name == "list_suggested":
        return list_suggested(tool_input)
    return None
