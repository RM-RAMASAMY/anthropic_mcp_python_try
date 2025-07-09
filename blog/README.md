# Blog MCP Server

A Model Context Protocol (MCP) server for managing blog posts. This server provides tools for creating, reading, searching, and managing blog posts stored as markdown files in the local `blog_posts` directory.

## Features

- **Create Blog Posts**: Create new blog posts with title, content, author, and tags
- **Retrieve Posts**: Get specific blog posts by ID
- **List Posts**: View all blog posts with basic information
- **Search Posts**: Search through blog posts by title, content, or tags
- **Delete Posts**: Remove blog posts by ID
- **Markdown Storage**: Blog posts are stored as readable markdown files
- **Local Storage**: All blog posts are stored in the `blog_posts` folder within the blog directory

## Storage Format

- Blog posts are stored as `.md` files in the `blog_posts` directory
- Metadata is stored in corresponding `_meta.txt` files
- Each blog post gets a unique timestamp-based ID (e.g., `20250708_143022`)

## Tools Available

### `create_blog_post`
Create a new blog post with the specified title, content, author, and tags.

### `get_blog_post`
Retrieve a specific blog post using its unique ID.

### `list_blog_posts`
Get a list of all blog posts with their basic information.

### `search_blog_posts`
Search through blog posts by matching query against titles, content, or tags.

### `delete_blog_post`
Delete a specific blog post by its ID.

## Usage

This server is designed to work with MCP-compatible clients. Blog posts are stored in the `blog_posts` directory relative to the server script location.

## Installation

Make sure you have the required dependencies installed:

```bash
uv sync
```

## Running

Run the server using:

```bash
python blog.py
```
