# 🎭 Persona System for MCP Blog Client

This system allows you to give your blog assistant different personalities and expertise areas.

## 🚀 Quick Start

### Option 1: Use the Persona Selector (Recommended)
```bash
cd mcp-client
uv run python select_persona.py
```

### Option 2: Direct Command Line
```bash
cd mcp-client
# Default persona
uv run python client.py "../blog/blog.py"

# With custom persona
uv run python client.py "../blog/blog.py" "personas/creative_writer.py"
```

## 📝 Available Personas

### 1. **BlogBot** (Default)
- 🖋️ **Style**: Warm, engaging, approachable
- 🎯 **Focus**: General blogging assistance
- 💡 **Best for**: Beginners, general blog management

### 2. **Professional Editor**
- 📊 **Style**: Strategic, data-driven, professional
- 🎯 **Focus**: Content strategy, SEO, business goals
- 💡 **Best for**: Business blogs, professional content

### 3. **Creative Writer**
- 🎨 **Style**: Artistic, imaginative, expressive
- 🎯 **Focus**: Storytelling, creative expression
- 💡 **Best for**: Personal blogs, artistic content, storytelling

## 🛠️ Creating Custom Personas

### Step 1: Create a Persona File
Create a new `.py` file in the `personas/` directory:

```python
"""
Your Custom Persona Name

Describe your persona here. This text will be used as the system prompt.

Include:
- Personality traits
- Writing style
- Areas of expertise
- How they should interact with users
- Their role and purpose

Example formatting with emojis and structure helps!
"""
```

### Step 2: Use Your Custom Persona
```bash
uv run python client.py "../blog/blog.py" "personas/your_custom_persona.py"
```

## 📋 Persona Template

Copy this template to create new personas:

```python
"""
[Persona Name] - [Brief Description]

You are [persona name], a [description]. Your characteristics:

🎯 **Role**: [What they do]

✍️ **Writing Style**: [How they write and communicate]

📚 **Expertise**: [Their areas of knowledge]

💡 **Personality Traits**:
- [Trait 1]
- [Trait 2]
- [Trait 3]

🚀 **Your Mission**: [What they help users achieve]

When working with blog posts, you [specific approach or focus].
"""
```

## 🎨 Examples of Persona Variations

- **Tech Blogger**: Focused on programming, tutorials, technical content
- **Travel Writer**: Emphasizes storytelling, adventure, cultural insights
- **Food Blogger**: Enthusiastic about recipes, restaurant reviews, culinary experiences
- **Business Coach**: Strategic, goal-oriented, focused on growth and success
- **Lifestyle Influencer**: Trendy, social media savvy, engagement-focused

## 🔧 How It Works

1. **System Prompt**: The persona content becomes Claude's system prompt
2. **Consistent Behavior**: The AI maintains the persona throughout the conversation
3. **Tool Integration**: The persona influences how the AI uses blog management tools
4. **Contextual Responses**: All responses are filtered through the persona's perspective

## 💡 Tips for Effective Personas

1. **Be Specific**: Clear personality traits and expertise areas
2. **Include Examples**: Show how they should respond or behave
3. **Define Scope**: What they focus on and what they avoid
4. **Use Formatting**: Emojis and structure make personas more engaging
5. **Test and Iterate**: Try different approaches and refine based on results

Enjoy creating unique AI assistants for your blogging needs! 🚀
