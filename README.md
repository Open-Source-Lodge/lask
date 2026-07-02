# [lask](https://pypi.org/project/lask/)

Ask LLMs right from the terminal.

## Features

- CLI for multiple LLM providers (OpenAI, Anthropic, AWS Bedrock, Azure)
- Customizable models and parameters
- Minimal dependencies (`requests`, `boto3` for AWS)
- Streaming responses
- Repl mode for interactive use, with temporary chat history
- Pipe input support
- **Smart command mode**: describe what you want in plain English and lask translates it into a shell command, with confirmation before execution

## Installation

```bash
pip install lask
```

## Usage
With `OPENAI_API_KEY` in your environment or in `~/.lask-config`:

```bash
lask What movie is this quote from\? \"that still only counts as one\"
```

Or as a repl:

```bash
lask

==== Lask REPL Mode ====
Using provider: openai
Smart command: auto

> What movie is this quote from? "that still only counts as one"
LLM response here...
> When was that movie released?
```

Smart command mode also works in the REPL. When `smart_command` is `auto` or `true`, the REPL automatically detects command requests and handles them the same way — propose, confirm, execute:

```
> show disk usage for the current directory

  du -sh .

Press Enter to run, or any other key to abort.

> explain what du does
The `du` command estimates file space usage...
```

REPL commands:

| Command   | Description |
|-----------|-------------|
| `!help`   | Show available REPL commands |
| `!clear`  | Clear the screen |
| `!history` | Show prompt history |
| `!vi`     | Switch to Vi editing mode |
| `!emacs`  | Switch to Emacs editing mode |
| `exit` / `quit` | Exit the REPL |
| `Ctrl+C`  | Interrupt a running command or response |
| `Ctrl+D`  | Exit the REPL |

Or via pipe:

```bash
echo "What movie is this quote from? \"that still only counts as one\"" | lask
```

### Smart Command Mode

By default, lask automatically detects if your prompt is asking for a shell command. When it is, it translates your natural language into a command, shows it to you, and waits for confirmation:

```bash
$ lask show diff between current branch and main

  git diff HEAD..main

Press Enter to run, or any other key to abort.
```

Press **Enter** to execute, or any other key to abort. The executed command is added to your shell history, so you can press **↑** to recall and re-run or edit it.

The behaviour is controlled by the `smart_command` setting (default: `auto`):

| Value   | Behaviour |
|---------|-----------|
| `auto`  | LLM decides if the prompt is a command request or a general question |
| `true`  | Always treat the prompt as a command request |
| `false` | Never use smart command mode, always answer normally |

In REPL mode, smart command keeps a rolling history of your interactions so you
can reference them naturally ("do the same but with `-v`", "now compress that",
etc.). Two settings control what is included:

| Setting                  | Default | Description |
|--------------------------|---------|-------------|
| `smart_context_commands` | `true`  | Include previous prompts and commands in context |
| `smart_context_output`   | `false` | Also capture and include command output |

## Setup

1. Get API keys from your provider:
   - [OpenAI](https://platform.openai.com/api-keys)
   - [Anthropic](https://console.anthropic.com/)
   - AWS Bedrock (uses AWS credentials)

2. Create `~/.lask-config`:

   ```ini
   [default]
   provider = openai  # openai, anthropic, aws, azure
   system_prompt = Always answer questions concisely.

   [openai]
   api_key = your-api-key-here
   model = gpt-5

   [anthropic]
   api_key = your-api-key-here
   model = claude-opus-4-8

   [aws]
   model_id = anthropic.claude-opus-4-8
   region = us-east-1

   [azure]
   api_key = your-azure-api-key
   resource_name = your-resource-name
   deployment_id = your-deployment-id
   ```

   See `examples/example.lask-config` for a full example.

3. Or use environment variables:

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   export ANTHROPIC_API_KEY='your-api-key-here'
   # AWS uses standard AWS credentials
   export AZURE_OPENAI_API_KEY='your-api-key-here'
   ```

## Configuration Options

### Provider Selection
```ini
[default]
provider = openai  # openai, anthropic, aws, azure
```

### Streaming
```ini
[openai]
streaming = false  # Disable streaming (true by default)
```

### System Prompts
```ini
[default]
system_prompt = Always answer questions concisely.

[openai]
system_prompt = You are a helpful AI assistant.  # Provider-specific
```

### Smart Command
```ini
[default]
smart_command = auto              # auto, true, or false
smart_context_commands = true      # include command history in context
smart_context_output = false       # include command output in context
```

### Provider-Specific Settings
Each provider supports model, temperature, max_tokens, and other parameters.

See `examples/example.lask-config` for all options.

## Development

This repo uses `uv`:

```bash
# Install dependencies
uv sync

# Build
uv build

# Install for development
pip install -e .

# For AWS Bedrock
pip install boto3
```

## License

GNU General Public License v3.0 (GPL-3.0)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
