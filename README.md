# AI-Assistant
Agentic AI Agent and personal helper for your computer using Anthropic's API

Only tested on Windows

## Setup
Ensure you have Python latest release installed on your system.

First, set your Anthropic API key as an environment variable:

```bash
set ANTHROPIC_API_KEY=your_api_key_here
```

Next, navigate to your project directory and install the dependency:
```bash
pip install rich
```
Rich is used for showing markdown formatting in the terminal.

---
Additionally, create a folder named `Context`. In this folder, you can add files that the assistant can read or write to.

Finally, create a folder named `Projects` if you would like to import your own projects that the assistant can manage. The assistant will automatically create this folder if it ever builds a project on its own.

## Customizing
Default name is John and default Timezone is EST

- Modify `config.py` to change selected model, max tokens, and persona (User's name is also found here)
- Modify `tools/` to modify the tools the assistant has access to

## Running the Project
To run the project, run the `run_chat.bat` file

## Features
- Ability to dynamically write to memory
- Can create Projects, which are self-contained file systems that the assistant can read/write/delete to, but cannot execute
- User can input files into a Context folder, which the assistant can reference and read/write to
- Assistant can search the web
- Assistant can suggest tool implementations
- Dynamic tool integration with assistant
- Assistant can save responses when asked
- Assistant can read, but not write to, its own source code

## Tools
- `web_search` Allows the assistant to use Anthropic's built in web search
- `save_resposne` Allows the assistant to save text to a markdown file at the user's discretion
- `create_tool` Creates a markdown file with the layout for a new tool. Only runs when user asks and the tool must be implemented by the user before it is functional
- `list_suggested` Shows the assistant all tools created in `SuggestedTools/` (not yet active)
- `implement_tool` Implement a suggested tool into the live codebase at the user's approval
- `memory` Dynamically stores memory about the user. Runs whenever the user exits out of the program. (Only works if the user types "exit" or "quit" to leave instead of closing the terminal from the close button)
- `read_code` Allows the assistant to read, but not write to, its own source code when asked by the user or if necessary

**Context**
  
- `read_context` Allows the assistant to read context that has been given by the user in `Context/`
- `write_context` Allows the assistant to write to/create new files in `Context/`

**Projects**

- `create_project` Creates a new project folder with a README
- `list_projects` Shows the assistant all projects or all files within a project
- `read_project_file` Reads a selected file within a project
- `write_project_file` Writes or patches to a file within a project
- `delete_project_file` Deletes a file within a project
- `delete_project` Deletes a whole project, requires hard-coded user verification
