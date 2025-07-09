#!/usr/bin/env python3
"""
Blog Content Checker - View saved blog posts from the orchestrator workflow

This utility helps you inspect what content has been saved by the blog workflow.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def get_blog_posts_directory():
    """Get the blog posts directory path"""
    current_dir = Path(__file__).parent
    blog_posts_dir = current_dir.parent / "blog" / "blog_posts"
    return blog_posts_dir

def list_all_posts():
    """List all saved blog posts"""
    blog_dir = get_blog_posts_directory()
    
    if not blog_dir.exists():
        print("❌ Blog posts directory not found")
        return
    
    md_files = list(blog_dir.glob("*.md"))
    
    if not md_files:
        print("📭 No blog posts found")
        return
    
    print(f"📚 Found {len(md_files)} blog posts:")
    print("=" * 60)
    
    for md_file in sorted(md_files, reverse=True):
        post_id = md_file.stem
        meta_file = blog_dir / f"{post_id}_meta.txt"
        
        # Read metadata if available
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = f.read().strip().split('|')
                if len(metadata) >= 4:
                    print(f"🆔 ID: {post_id}")
                    print(f"📰 Title: {metadata[1]}")
                    print(f"👤 Author: {metadata[2]}")
                    print(f"📅 Date: {metadata[3]}")
                    if len(metadata) > 4 and metadata[4]:
                        print(f"🏷️  Tags: {metadata[4]}")
                else:
                    print(f"🆔 ID: {post_id} (metadata incomplete)")
        else:
            print(f"🆔 ID: {post_id} (no metadata)")
        
        # Show file size and modification time
        stat = md_file.stat()
        size_kb = stat.st_size / 1024
        mod_time = datetime.fromtimestamp(stat.st_mtime)
        print(f"📄 Size: {size_kb:.1f} KB | Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

def show_post_content(post_id: str):
    """Show the content of a specific post"""
    blog_dir = get_blog_posts_directory()
    md_file = blog_dir / f"{post_id}.md"
    
    if not md_file.exists():
        print(f"❌ Post with ID '{post_id}' not found")
        return
    
    print(f"📖 Content of post '{post_id}':")
    print("=" * 70)
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    print("=" * 70)
    
    # Show word count
    word_count = len(content.split())
    print(f"📊 Word count: {word_count}")

def show_recent_posts(count: int = 3):
    """Show the most recent posts"""
    blog_dir = get_blog_posts_directory()
    
    if not blog_dir.exists():
        print("❌ Blog posts directory not found")
        return
    
    md_files = list(blog_dir.glob("*.md"))
    
    if not md_files:
        print("📭 No blog posts found")
        return
    
    # Sort by modification time (most recent first)
    md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"🕐 {count} Most Recent Blog Posts:")
    print("=" * 70)
    
    for md_file in md_files[:count]:
        post_id = md_file.stem
        print(f"\n🆔 Post ID: {post_id}")
        
        # Show first few lines of content
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            preview_lines = lines[:10]  # First 10 lines
            print(''.join(preview_lines))
            
            if len(lines) > 10:
                print(f"... ({len(lines) - 10} more lines)")
        
        print("-" * 40)

def main():
    """Main function"""
    print("📚 Blog Content Checker")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python check_content.py list          - List all posts")
        print("  python check_content.py show <post_id> - Show specific post")
        print("  python check_content.py recent [count] - Show recent posts")
        print("\nRunning with default action: recent posts")
        show_recent_posts()
        return
    
    action = sys.argv[1].lower()
    
    if action == "list":
        list_all_posts()
    elif action == "show" and len(sys.argv) > 2:
        show_post_content(sys.argv[2])
    elif action == "recent":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        show_recent_posts(count)
    else:
        print("❌ Invalid action. Use 'list', 'show <post_id>', or 'recent [count]'")

if __name__ == "__main__":
    main()
