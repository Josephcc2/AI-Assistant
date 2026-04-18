# AI-Assistant
Personal helper for your computer using Anthropic's API

Only tested on Windows

### Setup
Ensure you have Python latest release installed on your system.

First, set your Anthropic API key as an environment variable:

```bash
set ANTHROPIC_API_KEY=your_api_key_here
```

Next, navigate to your project directory and install the dependencies:
```bash
pip install rich
```
Rich is used for showing markdown formatting in the terminal.

### Customizing
Default name is John

- Modify `config.py` to change selected model, max tokens, and persona (User's name is also found here)
- Modify `tools.py` to modify the tools the AI has access to

## Running the Project
To run the project, run the `run_chat.bat` file
