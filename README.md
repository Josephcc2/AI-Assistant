# AI-Assistant
Personal helper for your computer using Anthropic's API

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

Finally, create a folder named `Context`. In this folder, you can add files that the AI can read or write to.

### Customizing
Default name is John and default Timezone is EST

- Modify `config.py` to change selected model, max tokens, and persona (User's name is also found here)
- Modify `tools.py` to modify the tools the AI has access to

## Running the Project
To run the project, run the `run_chat.bat` file

## Tools
- `web_search` Allows the AI to use Anthropic's built in web search
- `save_resposne` Allows the AI to save text to a markdown file at the user's discretion
- `create_tool` Creates a markdown file with the layout for a new tool. Only runs when user asks and the tool must be implemented by the user before it is functional
- `memory` Dynamically stores memory about the user. Runs whenever the user exits out of the program. (Only works if the user types "exit" or "quit" to leave instead of closing the terminal from the close button)
- `read_code` Allows the AI to read, but not write to, its own source code when asked by the user or if necessary
**Context**
- `read_context` Allows the AI to read context that has been given to the use in the `Context` folder
- `write_context` Allows the AI to write to/create new files in the `Context` folder
**Projects**
- `create_project`
- `list_projects`
- `read_project_file`
- `write_project_file`
- `delete_project_file`
- `delete_project`
