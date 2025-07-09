#!/usr/bin/env python3
"""
Example usage of the Blog Workflow Orchestrator

This script demonstrates different ways to use the orchestrator with various configurations.
"""

import asyncio
import os
from pathlib import Path
from blog_workflow import BlogWorkflowOrchestrator

def get_blog_server_path():
    """Get the path to the blog server script"""
    current_dir = Path(__file__).parent
    blog_server_path = current_dir.parent / "blog" / "blog.py"
    return str(blog_server_path)

async def example_basic_workflow():
    """Example: Basic workflow with default personas"""
    print("🚀 Example 1: Basic Blog Workflow")
    print("=" * 50)
    
    orchestrator = BlogWorkflowOrchestrator(
        blog_server_path=get_blog_server_path()
    )
    
    try:
        final_post = await orchestrator.start_workflow(
            theme="The Benefits of Morning Routines",
            author="Example Author",
            tags=["productivity", "lifestyle", "health"]
        )
        
        summary = orchestrator.get_workflow_summary()
        print(f"✅ Workflow completed! Post ID: {summary['post_id']}")
        
    finally:
        await orchestrator.cleanup()

async def example_custom_personas():
    """Example: Workflow with custom personas"""
    print("🚀 Example 2: Custom Persona Workflow")
    print("=" * 50)
    
    # Load custom personas
    current_dir = Path(__file__).parent
    creative_writer_path = current_dir / "personas" / "creative_writer.py"
    professional_editor_path = current_dir / "personas" / "professional_editor.py"
    
    def load_persona(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            start = content.find('"""') + 3
            end = content.find('"""', start)
            return content[start:end].strip()
    
    writer_persona = load_persona(creative_writer_path)
    reviewer_persona = load_persona(professional_editor_path)
    
    orchestrator = BlogWorkflowOrchestrator(
        blog_server_path=get_blog_server_path(),
        writer_persona=writer_persona,
        reviewer_persona=reviewer_persona
    )
    
    try:
        final_post = await orchestrator.start_workflow(
            theme="The Art of Digital Storytelling",
            author="Creative Team",
            tags=["storytelling", "digital", "creativity", "content"]
        )
        
        summary = orchestrator.get_workflow_summary()
        print(f"✅ Creative workflow completed! Post ID: {summary['post_id']}")
        
    finally:
        await orchestrator.cleanup()

async def example_technical_blog():
    """Example: Technical blog post workflow"""
    print("🚀 Example 3: Technical Blog Post")
    print("=" * 50)
    
    orchestrator = BlogWorkflowOrchestrator(
        blog_server_path=get_blog_server_path()
    )
    
    # Set more AI iterations for technical content
    orchestrator.max_ai_iterations = 3
    
    try:
        final_post = await orchestrator.start_workflow(
            theme="Understanding Machine Learning Model Deployment with Docker",
            author="Tech Team",
            tags=["machine-learning", "docker", "deployment", "devops", "technical"]
        )
        
        summary = orchestrator.get_workflow_summary()
        print(f"✅ Technical workflow completed! Post ID: {summary['post_id']}")
        
    finally:
        await orchestrator.cleanup()

def main():
    """Main function to run examples"""
    print("🎯 Blog Workflow Orchestrator Examples")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable is required")
        print("   Please set your Anthropic API key in a .env file or environment variable")
        return
    
    print("\nChoose an example to run:")
    print("1. Basic workflow (default personas)")
    print("2. Creative workflow (custom personas)")
    print("3. Technical blog workflow")
    print("0. Exit")
    
    while True:
        choice = input("\nEnter your choice (0-3): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            asyncio.run(example_basic_workflow())
            break
        elif choice == "2":
            asyncio.run(example_custom_personas())
            break
        elif choice == "3":
            asyncio.run(example_technical_blog())
            break
        else:
            print("❌ Invalid choice. Please enter 0, 1, 2, or 3.")

if __name__ == "__main__":
    main()
