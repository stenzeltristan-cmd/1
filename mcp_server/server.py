#!/usr/bin/env python3
import json
import os
from pathlib import Path
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

app = Server("anthropic-bridge")

# Path for personal tools/skills
PERSONAL_TOOLS_PATH = Path(__file__).parent.parent / "personal_tools.json"

def load_personal_tools():
    if PERSONAL_TOOLS_PATH.exists():
        with open(PERSONAL_TOOLS_PATH) as f:
            return json.load(f)
    return {"skills": [], "prompts": []}

def save_personal_tools(tools):
    with open(PERSONAL_TOOLS_PATH, "w") as f:
        json.dump(tools, f, indent=2)

@app.call_tool()
async def handle_tool_call(name: str, arguments: dict) -> ToolResult:
    if name == "list_anthropic_skills":
        return await list_anthropic_skills()
    elif name == "list_anthropic_plugins":
        return await list_anthropic_plugins()
    elif name == "list_personal_skills":
        return await list_personal_skills()
    elif name == "add_personal_skill":
        return await add_personal_skill(arguments)
    elif name == "search_all_tools":
        return await search_all_tools(arguments)
    else:
        return ToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            is_error=True,
        )

async def list_anthropic_skills():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.anthropic.com/v1/directory/skills",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
        return ToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error fetching skills: {str(e)}")],
            is_error=True,
        )

async def list_anthropic_plugins():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.anthropic.com/v1/directory/plugins",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
        return ToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]
        )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error fetching plugins: {str(e)}")],
            is_error=True,
        )

async def list_personal_skills():
    tools = load_personal_tools()
    return ToolResult(
        content=[TextContent(
            type="text",
            text=json.dumps(tools.get("skills", []), indent=2)
        )]
    )

async def add_personal_skill(arguments: dict):
    name = arguments.get("name")
    description = arguments.get("description")

    if not name or not description:
        return ToolResult(
            content=[TextContent(type="text", text="Name and description required")],
            is_error=True,
        )

    tools = load_personal_tools()
    tools["skills"].append({
        "name": name,
        "description": description,
        "created_at": str(Path(__file__).stat().st_mtime)
    })
    save_personal_tools(tools)

    return ToolResult(
        content=[TextContent(type="text", text=f"Added skill: {name}")]
    )

async def search_all_tools(arguments: dict):
    query = arguments.get("query", "").lower()

    results = {
        "anthropic_skills": [],
        "anthropic_plugins": [],
        "personal_skills": []
    }

    personal = load_personal_tools()

    for skill in personal.get("skills", []):
        if query in skill.get("name", "").lower() or query in skill.get("description", "").lower():
            results["personal_skills"].append(skill)

    return ToolResult(
        content=[TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )]
    )

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="list_anthropic_skills",
            description="List all available skills from Anthropic's official directory",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_anthropic_plugins",
            description="List all available plugins from Anthropic's official directory",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_personal_skills",
            description="List all personal skills and tools you've created",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="add_personal_skill",
            description="Add a new personal skill or tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the skill"},
                    "description": {"type": "string", "description": "Description of what the skill does"}
                },
                "required": ["name", "description"]
            }
        ),
        Tool(
            name="search_all_tools",
            description="Search across Anthropic's directories and personal skills",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        )
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
