# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository is an **Anthropic Directory Bridge** — a unified interface to access Anthropic's official Skills, Plugins, and other directories alongside your personal tools. Available in both Claude.ai and Claude Desktop.

## Architecture

- **mcp_server/** — MCP (Model Context Protocol) server that exposes:
  - Anthropic's official directories (live, fetched on-demand)
  - Personal skills and tools storage
  - Search/browse across all tools
- **personal_tools.json** — Storage for your custom skills, prompts, and tools
- **SETUP.md** — Configuration guide for Claude Desktop and Claude.ai

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start the MCP server (runs on http://127.0.0.1:8000)
python mcp_server/server.py
```

## Development Workflow

1. All changes should be on `claude/websetup-6wHNA` branch
2. Update `personal_tools.json` to add new tools/skills
3. Modify `mcp_server/server.py` for new functionality
4. Commit and push: `git push -u origin claude/websetup-6wHNA`

## Git Operations

- **Pushing changes**: `git push -u origin <branch-name>`
- **Fetching updates**: `git fetch origin <branch-name>`
- **Current development branch**: `claude/websetup-6wHNA`

## Available Tools (via MCP)

- `list_anthropic_skills` — Browse Anthropic's official skills
- `list_anthropic_plugins` — Browse Anthropic's plugins
- `list_personal_skills` — View your custom tools
- `add_personal_skill` — Add new personal skill
- `search_all_tools` — Search across everything

See SETUP.md for platform configuration and usage details.
