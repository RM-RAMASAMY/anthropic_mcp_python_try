#!/usr/bin/env python3
"""
Persona Selection Helper for MCP Blog Client

This script helps you choose and run the blog client with different personas.
"""

import os
import sys
import subprocess
import asyncio

def list_available_personas():
    """List all available persona files"""
    persona_dir = "personas"
    personas = []
    
    if os.path.exists(persona_dir):
        for file in os.listdir(persona_dir):
            if file.endswith('.py'):
                personas.append(file)
    
    return sorted(personas)

def show_persona_preview(persona_file):
    """Show a preview of the persona"""
    try:
        with open(f"personas/{persona_file}", 'r', encoding='utf-8') as f:
            content = f.read()
            if '"""' in content:
                start = content.find('"""') + 3
                end = content.find('"""', start)
                if end != -1:
                    preview = content[start:end].strip()
                    # Show first few lines
                    lines = preview.split('\n')[:5]
                    return '\n'.join(lines) + "..."
    except Exception:
        return "Preview not available"
    
    return "Preview not available"

def main():
    print("🎭 MCP Blog Client - Persona Selection")
    print("=" * 50)
    
    # List available personas
    personas = list_available_personas()
    
    if not personas:
        print("No custom personas found. Using default BlogBot persona.")
        print("\nStarting client with default persona...")
        subprocess.run([sys.executable, "client.py", "../blog/blog.py"])
        return
    
    print("Available personas:")
    print("0. Default BlogBot (friendly blog assistant)")
    
    for i, persona in enumerate(personas, 1):
        name = persona.replace('.py', '').replace('_', ' ').title()
        print(f"{i}. {name}")
    
    print()
    
    while True:
        try:
            choice = input("Select a persona (0-{}) or 'q' to quit: ".format(len(personas)))
            
            if choice.lower() == 'q':
                return
            
            choice_num = int(choice)
            
            if choice_num == 0:
                print("\n🤖 Using default BlogBot persona")
                print("Starting client...")
                subprocess.run([sys.executable, "client.py", "../blog/blog.py"])
                break
            elif 1 <= choice_num <= len(personas):
                selected_persona = personas[choice_num - 1]
                print(f"\n🎭 Selected persona: {selected_persona}")
                print("\nPreview:")
                print("-" * 30)
                print(show_persona_preview(selected_persona))
                print("-" * 30)
                
                confirm = input("\nUse this persona? (y/n): ").lower()
                if confirm == 'y':
                    print("Starting client...")
                    subprocess.run([sys.executable, "client.py", "../blog/blog.py", f"personas/{selected_persona}"])
                    break
            else:
                print("Invalid selection. Please try again.")
                
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return

if __name__ == "__main__":
    main()
