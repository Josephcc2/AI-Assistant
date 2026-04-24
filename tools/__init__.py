from tools import meta, memory, files, context, projects, custom, implement

# All tool schemas assembled in one list for the API
_modules = [meta, memory, files, context, projects, custom, implement]

tools = []
for _mod in _modules:
    tools.extend(_mod.tools)


def run_tool(name, tool_input):
    for mod in _modules:
        result = mod.run(name, tool_input)
        if result is not None:
            return result

    all_names = [t["name"] for t in tools]
    return f"Error: Unknown tool '{name}'. Available tools: {', '.join(all_names)}."
