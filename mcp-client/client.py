import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self, persona: str = None):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.persona = persona or self.get_default_persona()
    
    def get_default_persona(self) -> str:
        """Get the default persona for the agent"""
        return """You are BlogBot, a friendly and knowledgeable blog assistant. You have the following characteristics:

🖋️ **Writing Style**: You write in a warm, engaging tone that makes blogging feel approachable and fun.

📝 **Expertise**: You're passionate about helping people create, organize, and manage their blog content effectively.

💡 **Personality Traits**:
- Encouraging and supportive
- Detail-oriented but not overwhelming
- Creative and inspiring
- Patient with beginners
- Enthusiastic about good content

🎯 **Your Role**: Help users create amazing blog posts, organize their content, and make the most of their blogging journey. Always suggest improvements and offer creative ideas when appropriate.

When users ask you to create, search, or manage blog posts, you'll use your specialized blog management tools to help them efficiently."""
    
    def load_persona_from_file(self, persona_file: str) -> str:
        """Load persona from a file"""
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract the persona from the docstring if it's a Python file
                if persona_file.endswith('.py') and '"""' in content:
                    start = content.find('"""') + 3
                    end = content.find('"""', start)
                    if end != -1:
                        return content[start:end].strip()
                return content.strip()
        except Exception as e:
            print(f"Error loading persona from {persona_file}: {e}")
            return self.get_default_persona()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call with system message (persona)
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=self.persona,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                      "role": "assistant",
                      "content": content.text
                    })
                messages.append({
                    "role": "user", 
                    "content": result.content
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    system=self.persona,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    def get_persona_name(self) -> str:
        """Extract the persona name from the persona text"""
        try:
            lines = self.persona.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('🖋️') and not line.startswith('📝'):
                    # Look for "You are [Name]," pattern
                    if line.startswith('You are'):
                        # Extract name after "You are "
                        start = line.find('You are') + 8
                        # Find the end - look for comma or "who"
                        end = line.find(',', start)
                        if end == -1:
                            end = line.find(' who', start)
                        if end == -1:
                            end = line.find(' with', start)
                        if end != -1:
                            name = line[start:end].strip()
                            # Clean up common prefixes
                            if name.startswith('a '):
                                name = name[2:]
                            if name.startswith('an '):
                                name = name[3:]
                            return name
            
            # Fallback to looking for patterns in the content
            if "Professional Editor" in self.persona:
                return "Professional Editor"
            elif "Creative Writer" in self.persona:
                return "Creative Writer"
            else:
                return "BlogBot"
        except Exception:
            return "BlogBot"

    async def chat_loop(self):
        """Run an interactive chat loop"""
        persona_name = self.get_persona_name()
        print("\n🤖 MCP Client Started!")
        print(f"📝 Persona: {persona_name}")
        
        # Show appropriate intro based on persona
        if "Professional Editor" in persona_name:
            print("💼 I'm your professional content strategist, focused on results-driven content!")
        elif "Creative Writer" in persona_name:
            print("🎨 I'm your creative writing companion, here to unleash your artistic expression!")
        else:
            print("💡 I'm here to help you create, manage, and organize amazing blog content!")
        
        print("Type your queries or 'quit' to exit.")
        print("-" * 60)
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script> [persona_file]")
        print("Example: python client.py ../blog/blog.py")
        print("Example: python client.py ../blog/blog.py personas/creative_writer.py")
        sys.exit(1)
    
    # Load custom persona if provided
    persona = None
    if len(sys.argv) >= 3:
        persona_file = sys.argv[2]
        client_temp = MCPClient()
        persona = client_temp.load_persona_from_file(persona_file)
        print(f"🎭 Loaded persona from: {persona_file}")
    
    client = MCPClient(persona=persona)
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())