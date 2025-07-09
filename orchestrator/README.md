# Blog Workflow Orchestrator

A sophisticated agentic workflow system for blog creation, review, and publication using Anthropic's Model Context Protocol (MCP).

## Features

- **Multi-Agent Workflow**: Coordinated blog writer and reviewer agents
- **Iterative Improvement**: AI and human review loops with feedback
- **State Management**: Track workflow progress and post versions
- **MCP Integration**: Uses existing blog MCP server for content management
- **Human-in-the-Loop**: Final human approval step

## Workflow Process

1. **Blog Creation**: AI writer creates initial blog post on given theme
2. **AI Review Loop**: AI reviewer evaluates and provides feedback until approved
3. **Human Review**: Human reviewer makes final approval decision
4. **Revision Cycle**: If rejected, writer revises based on feedback and process repeats

## Usage

```bash
# Start the orchestrator
python main.py "Your Blog Theme"

# With custom personas
python main.py "Your Blog Theme" --writer-persona personas/creative_writer.py --reviewer-persona personas/professional_editor.py
```

## Components

- `blog_workflow.py`: Main orchestrator class
- `main.py`: CLI interface for running workflows
- `personas/`: Custom agent personas for different writing styles
- `utils/`: Helper utilities for workflow management

## Requirements

- Python 3.11+
- Anthropic API key
- Access to blog MCP server
