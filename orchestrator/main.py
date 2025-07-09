import asyncio
import sys
import os
import argparse
from pathlib import Path
from blog_workflow import BlogWorkflowOrchestrator

def load_persona_from_file(persona_file: str) -> str:
    """Load persona from a file"""
    try:
        with open(persona_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract persona from Python docstring if it's a .py file
            if persona_file.endswith('.py') and '"""' in content:
                start = content.find('"""') + 3
                end = content.find('"""', start)
                if end != -1:
                    return content[start:end].strip()
            return content.strip()
    except Exception as e:
        print(f"❌ Error loading persona from {persona_file}: {e}")
        return None

def get_blog_server_path():
    """Get the path to the blog server script"""
    # Assume it's in the sibling blog directory
    current_dir = Path(__file__).parent
    blog_server_path = current_dir.parent / "blog" / "blog.py"
    
    if not blog_server_path.exists():
        raise FileNotFoundError(f"Blog server not found at: {blog_server_path}")
    
    return str(blog_server_path)

async def main():
    parser = argparse.ArgumentParser(description="Blog Workflow Orchestrator")
    parser.add_argument("theme", help="The theme/topic for the blog post")
    parser.add_argument("--author", default="BlogBot", help="Author name for the blog post")
    parser.add_argument("--tags", nargs="*", default=[], help="Tags for the blog post")
    parser.add_argument("--writer-persona", help="Path to custom writer persona file")
    parser.add_argument("--reviewer-persona", help="Path to custom reviewer persona file")
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum AI review iterations")
    
    args = parser.parse_args()
    
    print("🚀 Blog Workflow Orchestrator")
    print("=" * 50)
    print(f"Theme: {args.theme}")
    print(f"Author: {args.author}")
    print(f"Tags: {', '.join(args.tags) if args.tags else 'None'}")
    
    # Load custom personas if provided
    writer_persona = None
    reviewer_persona = None
    
    if args.writer_persona:
        writer_persona = load_persona_from_file(args.writer_persona)
        if writer_persona:
            print(f"🎭 Loaded writer persona from: {args.writer_persona}")
        else:
            print(f"⚠️ Failed to load writer persona, using default")
    
    if args.reviewer_persona:
        reviewer_persona = load_persona_from_file(args.reviewer_persona)
        if reviewer_persona:
            print(f"🎭 Loaded reviewer persona from: {args.reviewer_persona}")
        else:
            print(f"⚠️ Failed to load reviewer persona, using default")
    
    print("=" * 50)
    
    # Get blog server path
    try:
        blog_server_path = get_blog_server_path()
        print(f"📡 Blog server: {blog_server_path}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Create and run orchestrator
    orchestrator = BlogWorkflowOrchestrator(
        blog_server_path=blog_server_path,
        writer_persona=writer_persona,
        reviewer_persona=reviewer_persona
    )
    
    # Set max iterations if specified
    orchestrator.max_ai_iterations = args.max_iterations
    
    try:
        # Start the workflow
        final_post = await orchestrator.start_workflow(
            theme=args.theme,
            author=args.author,
            tags=args.tags
        )
        
        # Print final summary
        print("\n" + "🎉" * 20)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("🎉" * 20)
        
        summary = orchestrator.get_workflow_summary()
        print(f"📄 Final Post Details:")
        print(f"   Title: {summary['title']}")
        print(f"   Version: {summary['post_version']}")
        print(f"   Post ID: {summary['post_id']}")
        print(f"   Total Revisions: {summary['feedback_count']}")
        print(f"   Workflow State: {summary['state']}")
        
        print(f"\n📝 Final Content Preview:")
        print("-" * 50)
        content_preview = final_post.content[:300] + "..." if len(final_post.content) > 300 else final_post.content
        print(content_preview)
        print("-" * 50)
        
        if final_post.post_id:
            print(f"\n💾 Your blog post has been saved with ID: {final_post.post_id}")
            print(f"   You can retrieve it using the blog MCP server tools")
        
    except KeyboardInterrupt:
        print("\n⏹️ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up resources
        await orchestrator.cleanup()
        print("\n🧹 Cleaned up resources")

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable is required")
        print("   Please set your Anthropic API key in a .env file or environment variable")
        sys.exit(1)
    
    asyncio.run(main())
