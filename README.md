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
Enter your prompts. Type 'exit' or 'quit' to end the session.
Press Ctrl+C to interrupt a response.

> What movie is this quote from? "that still only counts as one"
LLM response here...
> When was that movie released?
```

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
   model = gpt-4.1

   [anthropic]
   api_key = your-api-key-here
   model = claude-3-opus-20240229

   [aws]
   model_id = anthropic.claude-3-sonnet-20240229-v1:0
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
smart_command = auto  # auto, true, or false
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
