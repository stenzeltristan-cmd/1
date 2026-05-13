# Setup Guide: Anthropic Directory Bridge

This repository bridges Anthropic's official Skills, Plugins, and other directories with your personal tools. **Private bridge for Claude Desktop + Claude Code only.**

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the MCP Server
```bash
python mcp_server/server.py
```

The server runs on `http://127.0.0.1:8000` (localhost only — no external access)

## Configuration

### Claude Desktop

Edit your Claude Desktop config file:
- **macOS/Linux**: `~/.claude/config.json`
- **Windows**: `%APPDATA%\Claude\config.json`

Add to `mcpServers`:
```json
{
  "anthropic-bridge": {
    "command": "python",
    "args": ["/path/to/this/repo/mcp_server/server.py"]
  }
}
```

### Claude Code (IDE)

Claude Code automatically detects MCP servers configured in your Claude Desktop config. Once configured above, Claude Code has immediate access to all tools.

## Using the Bridge

### Available Commands

**List Anthropic Skills**
```
Use the "list_anthropic_skills" tool to browse all official Anthropic skills
```

**List Anthropic Plugins**
```
Use the "list_anthropic_plugins" tool to browse all official plugins
```

**View Your Personal Skills**
```
Use the "list_personal_skills" tool to see skills you've created
```

**Add a New Personal Skill**
```
Use the "add_personal_skill" tool with:
- name: Your skill name
- description: What it does
```

**Search Everything**
```
Use the "search_all_tools" tool to search across all skills, plugins, and personal tools
```

## Personal Tools Storage

Personal skills are stored in `personal_tools.json` in the repo root. Edit it directly to add:
- Custom skills
- Prompts
- Tools

Example format:
```json
{
  "skills": [
    {
      "name": "My Custom Skill",
      "description": "Does something useful",
      "created_at": "2024-01-01"
    }
  ],
  "prompts": []
}
```

## Syncing Across Claude Desktop & Claude Code

- **Local changes**: Edit `personal_tools.json` and both interfaces will see updates
- **Anthropic directories**: Fetched live when you access tools
- **Keep in sync**: Push changes to your branch to share with other instances

## Privacy

- ✅ Localhost only — no external exposure
- ✅ Claude Desktop + Claude Code only — no web access
- ✅ Personal tools stored locally
- ✅ Completely private — zero external access
