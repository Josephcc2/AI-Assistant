import os

MEMORY_PATH = os.path.join("Memory", "long_term_memory.md")


def manage_memory(tool_input):
    action = tool_input.get("action")

    if action == "read":
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
            return content if content else "Memory file is empty."
        return "No memory file found."

    elif action == "write":
        content = tool_input.get("content", "")
        os.makedirs("Memory", exist_ok=True)
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        return "Memory updated successfully."

    return f"Unknown action: {action}"


tools = [
    {
        "name": "memory",
        "description": (
            "Read or update your long-term memory about the user. "
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
    }
]


def run(name, tool_input):
    if name == "memory":
        return manage_memory(tool_input)
    return None
