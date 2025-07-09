from typing import Any, List, Dict
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("blog")

# Blog storage directory - relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_DIR = os.path.join(SCRIPT_DIR, "blog_posts")

def ensure_blog_directory():
    """Ensure the blog posts directory exists."""
    if not os.path.exists(BLOG_DIR):
        os.makedirs(BLOG_DIR)

def get_blog_post_path(post_id: str) -> str:
    """Get the file path for a blog post."""
    return os.path.join(BLOG_DIR, f"{post_id}.md")

def get_metadata_path(post_id: str) -> str:
    """Get the file path for a blog post's metadata."""
    return os.path.join(BLOG_DIR, f"{post_id}_meta.txt")

def format_blog_post(post: dict) -> str:
    """Format a blog post for display."""
    return f"""
# {post.get('title', 'Untitled')}

**Author:** {post.get('author', 'Unknown')}  
**Date:** {post.get('date', 'Unknown')}  
**Tags:** {', '.join(post.get('tags', []))}

{post.get('content', 'No content')}
"""

def write_blog_post(post_id: str, title: str, content: str, author: str, date: str, tags: List[str]):
    """Write a blog post as markdown file with metadata."""
    post_path = get_blog_post_path(post_id)
    meta_path = get_metadata_path(post_id)
    
    # Write markdown content
    markdown_content = f"""# {title}

**Author:** {author}  
**Date:** {date}  
**Tags:** {', '.join(tags)}

{content}
"""
    
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # Write metadata
    metadata = f"{post_id}|{title}|{author}|{date}|{','.join(tags)}"
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(metadata)

def read_blog_post_metadata(post_id: str) -> dict:
    """Read blog post metadata from metadata file."""
    meta_path = get_metadata_path(post_id)
    
    if not os.path.exists(meta_path):
        return None
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        metadata = f.read().strip()
    
    parts = metadata.split('|')
    if len(parts) >= 5:
        return {
            'id': parts[0],
            'title': parts[1],
            'author': parts[2],
            'date': parts[3],
            'tags': parts[4].split(',') if parts[4] else []
        }
    return None

def read_blog_post_content(post_id: str) -> str:
    """Read blog post content from markdown file."""
    post_path = get_blog_post_path(post_id)
    
    if not os.path.exists(post_path):
        return None
    
    with open(post_path, 'r', encoding='utf-8') as f:
        return f.read()

@mcp.tool()
async def create_blog_post(title: str, content: str, author: str = "Anonymous", tags: List[str] = None) -> str:
    """Create a new blog post.

    Args:
        title: The title of the blog post
        content: The content of the blog post
        author: The author of the blog post (default: Anonymous)
        tags: List of tags for the blog post
    """
    ensure_blog_directory()
    
    if tags is None:
        tags = []
    
    # Generate a simple ID based on timestamp
    post_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    date = datetime.now().isoformat()
    
    try:
        write_blog_post(post_id, title, content, author, date, tags)
        return f"Blog post created successfully with ID: {post_id}"
    except Exception as e:
        return f"Error creating blog post: {str(e)}"

@mcp.tool()
async def get_blog_post(post_id: str) -> str:
    """Get a specific blog post by ID.

    Args:
        post_id: The ID of the blog post to retrieve
    """
    post_path = get_blog_post_path(post_id)
    
    if not os.path.exists(post_path):
        return f"Blog post with ID '{post_id}' not found."
    
    try:
        content = read_blog_post_content(post_id)
        return content
    except Exception as e:
        return f"Error reading blog post: {str(e)}"

@mcp.tool()
async def list_blog_posts() -> str:
    """List all blog posts with their basic information."""
    ensure_blog_directory()
    
    try:
        post_files = [f for f in os.listdir(BLOG_DIR) if f.endswith('.md')]
        
        if not post_files:
            return "No blog posts found."
        
        posts_info = []
        for post_file in sorted(post_files, reverse=True):  # Most recent first
            post_id = post_file[:-3]  # Remove .md extension
            metadata = read_blog_post_metadata(post_id)
            
            if metadata:
                posts_info.append(f"ID: {metadata['id']} | Title: {metadata['title']} | Author: {metadata['author']} | Date: {metadata['date']}")
        
        return "\n".join(posts_info)
    except Exception as e:
        return f"Error listing blog posts: {str(e)}"

@mcp.tool()
async def search_blog_posts(query: str) -> str:
    """Search blog posts by title, content, or tags.

    Args:
        query: The search query to match against titles, content, or tags
    """
    ensure_blog_directory()
    
    try:
        post_files = [f for f in os.listdir(BLOG_DIR) if f.endswith('.md')]
        
        if not post_files:
            return "No blog posts found."
        
        matching_posts = []
        query_lower = query.lower()
        
        for post_file in post_files:
            post_id = post_file[:-3]  # Remove .md extension
            metadata = read_blog_post_metadata(post_id)
            content = read_blog_post_content(post_id)
            
            if metadata and content:
                # Search in title, content, and tags
                if (query_lower in metadata.get('title', '').lower() or
                    query_lower in content.lower() or
                    any(query_lower in tag.lower() for tag in metadata.get('tags', []))):
                    matching_posts.append(content)
        
        if not matching_posts:
            return f"No blog posts found matching '{query}'."
        
        return "\n" + "="*50 + "\n".join(matching_posts)
    except Exception as e:
        return f"Error searching blog posts: {str(e)}"

@mcp.tool()
async def delete_blog_post(post_id: str) -> str:
    """Delete a blog post by ID.

    Args:
        post_id: The ID of the blog post to delete
    """
    post_path = get_blog_post_path(post_id)
    meta_path = get_metadata_path(post_id)
    
    if not os.path.exists(post_path):
        return f"Blog post with ID '{post_id}' not found."
    
    try:
        os.remove(post_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
        return f"Blog post '{post_id}' deleted successfully."
    except Exception as e:
        return f"Error deleting blog post: {str(e)}"

@mcp.tool()
async def update_blog_post(post_id: str, title: str = None, content: str = None, author: str = None, tags: List[str] = None) -> str:
    """Update an existing blog post.

    Args:
        post_id: The ID of the blog post to update
        title: New title for the blog post (optional)
        content: New content for the blog post (optional) 
        author: New author for the blog post (optional)
        tags: New tags for the blog post (optional)
    """
    post_path = get_blog_post_path(post_id)
    meta_path = get_metadata_path(post_id)
    
    if not os.path.exists(post_path):
        return f"Blog post with ID '{post_id}' not found."
    
    try:
        # Read existing metadata
        existing_metadata = read_blog_post_metadata(post_id)
        if not existing_metadata:
            return f"Could not read metadata for post '{post_id}'."
        
        # Use existing values if new ones not provided
        new_title = title if title is not None else existing_metadata['title']
        new_author = author if author is not None else existing_metadata['author']
        new_tags = tags if tags is not None else existing_metadata['tags']
        
        if content is not None:
            new_content = content
        else:
            # Read existing content
            existing_content = read_blog_post_content(post_id)
            if existing_content:
                # Extract content without the header
                lines = existing_content.split('\n')
                content_start = 0
                for i, line in enumerate(lines):
                    if line.startswith('**Tags:**'):
                        content_start = i + 2  # Skip the tags line and empty line
                        break
                new_content = '\n'.join(lines[content_start:]).strip()
            else:
                return f"Could not read existing content for post '{post_id}'."
        
        # Update the post
        write_blog_post(post_id, new_title, new_content, new_author, existing_metadata['date'], new_tags)
        
        return f"Blog post '{post_id}' updated successfully."
    except Exception as e:
        return f"Error updating blog post: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
