import anthropic
import os

from rich.console import Console
from rich.markdown import Markdown

from config import selected_model, max_tokens, persona, consolidation_prompt
from tools import tools, run_tool

console = Console()

memoryPath = os.path.join("Memory", "long_term_memory.md")

# --- Memory ---
def LoadMemory():
    if os.path.exists(memoryPath):
        with open(memoryPath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content:
            return content
    return None

def BuildSystemPrompt():
    memory = LoadMemory()
    if memory:
        return (
            persona
            + "\n\n---\n\n"
            + "## Long-term memory (previous conversations)\n\n"
            + memory
        )
    return persona

# --- Prompt ---
def AIRespond(client, messages, systemPrompt):
    return client.messages.create(
        model=selected_model,
        max_tokens=max_tokens,
        system=systemPrompt,
        messages=messages,
        tools=tools
    )

# --- Helper Functions ---
def ClearConsole():
    os.system("cls" if os.name == "nt" else "clear")

def PrintResponse(content):
    full_text = "".join(block.text for block in content if block.type == "text")
    if full_text:
        console.print("[bold cyan]AI:[/bold cyan]")
        console.print(Markdown(full_text))
        console.print()
    return full_text

def ConsolidateMemory(client, messages, systemPrompt):
    console.print("[dim]Updating memory...[/dim]")
 
    # Append the consolidation instruction as a final user turn
    consolidation_messages = messages + [{
        "role": "user",
        "content": consolidation_prompt
    }]
 
    # Run agentic loop until the AI finishes updating memory
    while True:
        response = AIRespond(client, consolidation_messages, systemPrompt)
        consolidation_messages.append({"role": "assistant", "content": response.content})
 
        if response.stop_reason == "end_turn":
            orphaned = [
                {"type": "tool_result", "tool_use_id": block.id, "content": ""}
                for block in response.content if block.type == "tool_use"
            ]
            if orphaned:
                consolidation_messages.append({"role": "user", "content": orphaned})
                continue
            break
 
        elif response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            consolidation_messages.append({"role": "user", "content": tool_results})
 
        else:
            break
 
    console.print("[dim]Memory saved.[/dim]\n")


def main():
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    systemPrompt = BuildSystemPrompt()

    ClearConsole()
    memoryExists = os.path.exists(memoryPath)
    console.print("Chatbot started (type 'exit' to quit)\n")
    if memoryExists:
        console.print("[dim](Long-term memory loaded.)[/dim]\n")

    messages = []

    # Chat Loop
    while True:
        # User Input
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            ClearConsole()
            if messages:
                ConsolidateMemory(client, messages, systemPrompt)
            console.print("Goodbye!")
            break
        
        if not user_input:
            continue

        messages.append({
            "role": "user",
            "content": user_input
        })
        ClearConsole()

        # Agentic Loop
        while True:
            response = AIRespond(client, messages, systemPrompt)
            messages.append({"role": "assistant", "content": response.content})
            
            # Collect And Execute Any Tool Calls In This Response
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    console.print(f"[dim][Calling tool: {block.name}][/dim]\n")
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
                elif block.type == "server_tool_use" and block.name == "web_search":
                    console.print(f"[dim][Calling tool: web_search][/dim]\n")

            if tool_results:
                messages.append({"role": "user", "content": tool_results})
                continue

            # No tool calls — print response and exit loop
            PrintResponse(response.content)
            break

if __name__ == "__main__":
    main()