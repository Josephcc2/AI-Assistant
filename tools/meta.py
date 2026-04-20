import os
import re

CREATE_TOOL_DIR = "SuggestedTools"

def create_tool_file(tool_input):
    tool_name = tool_input.get("name")
    code = tool_input.get("code")

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


tools = [
    {
        "type": "web_search_20250305",
        "name": "web_search"
    },
    {
        "name": "create_tool",
        "description": (
            "Propose a new tool by writing Python code that integrates with this project's "
            "tool system (which uses Anthropic's API). "
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
    }
]


def run(name, tool_input):
    if name == "create_tool":
        return create_tool_file(tool_input)
    return None
