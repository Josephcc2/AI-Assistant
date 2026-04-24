# AUTO-GENERATED — managed by implement_tool. Do not edit manually.

# <<FUNCTIONS>>

tools = [
# <<SCHEMAS>>
]

_dispatch = {
# <<DISPATCH>>
}


def run(name, tool_input):
    if name in _dispatch:
        return _dispatch[name](tool_input)
    return None
