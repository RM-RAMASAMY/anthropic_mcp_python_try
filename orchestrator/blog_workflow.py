import asyncio
import sys
import os
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
from datetime import datetime
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BlogPost:
    content: str
    version: int
    created_at: datetime
    feedback_history: List[str]
    post_id: Optional[str] = None
    title: Optional[str] = None

@dataclass
class ReviewResult:
    decision: Literal["APPROVE", "REJECT"]
    feedback: Optional[str] = None
    reviewer_type: Literal["AI", "HUMAN"] = "AI"

class BlogWorkflowOrchestrator:
    def __init__(self, blog_server_path: str, writer_persona: str = None, reviewer_persona: str = None):
        self.blog_server_path = blog_server_path
        self.current_post: Optional[BlogPost] = None
        self.workflow_state = "INIT"
        self.max_ai_iterations = 5
        
        # Initialize connections
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        
        # Load personas
        self.writer_persona = writer_persona or self._get_default_writer_persona()
        self.reviewer_persona = reviewer_persona or self._get_default_reviewer_persona()
        
    def _get_default_writer_persona(self) -> str:
        """Default blog writer persona"""
        return """You are BlogBot, a skilled blog writer with these characteristics:

🖋️ **Writing Style**: 
- Clear, engaging, and accessible writing
- Strong introductions that hook readers
- Well-structured content with smooth transitions
- Compelling conclusions that leave readers satisfied

📝 **Content Expertise**:
- Research-driven accuracy
- SEO-friendly structure
- Reader-focused approach
- Appropriate tone for target audience

💡 **Process**:
- Create comprehensive, well-researched blog posts
- Address feedback constructively and thoroughly
- Maintain consistency in voice and quality
- Focus on value delivery to readers

When creating or revising blog posts, ensure high quality, clarity, and engagement throughout."""

    def _get_default_reviewer_persona(self) -> str:
        """Default blog reviewer persona"""
        return """You are an experienced blog content reviewer with these responsibilities:

🔍 **Evaluation Criteria**:
- **Quality**: Is the content well-written, accurate, and valuable?
- **Clarity**: Is the message clear and easy to understand?
- **Structure**: Does it flow logically with good organization?
- **Engagement**: Will it capture and hold reader attention?

📋 **Review Process**:
- Provide APPROVE or REJECT decision
- Give specific, actionable feedback for improvements
- Focus on the most impactful changes needed
- Consider the target audience and purpose

✅ **Standards for Approval**:
- Error-free grammar and spelling
- Logical flow and structure
- Engaging and valuable content
- Appropriate length and depth
- Clear call-to-action or conclusion

Always provide constructive, specific feedback that helps improve the content."""

    async def connect_to_blog_server(self):
        """Connect to the blog MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.blog_server_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        print("✅ Connected to blog MCP server")

    async def start_workflow(self, theme: str, author: str = "BlogBot", tags: List[str] = None) -> BlogPost:
        """Start the blog creation workflow"""
        print(f"🚀 Starting blog workflow for theme: {theme}")
        
        # Connect to blog server
        await self.connect_to_blog_server()
        
        # Step 1: Initial blog creation
        self.current_post = await self._create_initial_post(theme, author, tags or [])
        self.workflow_state = "AI_REVIEW"
        
        # Step 2: AI Review Loop
        await self._ai_review_loop()
        
        # Step 3: Human Review
        if self.workflow_state == "HUMAN_REVIEW":
            await self._human_review_loop()
            
        return self.current_post
    
    async def _create_initial_post(self, theme: str, author: str, tags: List[str]) -> BlogPost:
        """Create initial blog post using writer persona"""
        print("📝 Creating initial blog post...")
        
        writer_prompt = f"""Create a blog post on the theme: "{theme}"

Requirements:
- Write a complete, engaging blog post
- Include a compelling title
- Structure: Introduction, main content sections, conclusion
- Target length: 800-1200 words
- Make it informative and valuable to readers
- Use a professional yet approachable tone

Please provide:
1. A clear, engaging title
2. The complete blog post content

Format your response as:
TITLE: [Your title here]

CONTENT:
[Your blog post content here]"""

        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=self.writer_persona,
            messages=[{"role": "user", "content": writer_prompt}]
        )
        
        content = response.content[0].text
        title, blog_content = self._parse_blog_response(content)
        
        # Save to blog server
        try:
            result = await self.session.call_tool("create_blog_post", {
                "title": title,
                "content": blog_content,
                "author": author,
                "tags": tags
            })
            
            # Extract post ID from result
            post_id = self._extract_post_id(result.content[0].text)
            
            print(f"✅ Created blog post with ID: {post_id}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not save to blog server: {e}")
            post_id = None
        
        return BlogPost(
            content=blog_content,
            version=1,
            created_at=datetime.now(),
            feedback_history=[],
            post_id=post_id,
            title=title
        )
    
    def _parse_blog_response(self, response: str) -> tuple[str, str]:
        """Parse the blog response to extract title and content"""
        lines = response.strip().split('\n')
        title = "Untitled Blog Post"
        content = response
        
        for i, line in enumerate(lines):
            if line.strip().startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                # Find content after title
                content_start = i + 1
                while content_start < len(lines) and not lines[content_start].strip():
                    content_start += 1
                if content_start < len(lines) and lines[content_start].strip().startswith("CONTENT:"):
                    content_start += 1
                content = '\n'.join(lines[content_start:]).strip()
                break
        
        return title, content
    
    def _extract_post_id(self, result_text: str) -> Optional[str]:
        """Extract post ID from blog server response"""
        if "ID:" in result_text:
            # Extract ID from "Blog post created successfully with ID: 20250708_123456"
            parts = result_text.split("ID:")
            if len(parts) > 1:
                return parts[1].strip()
        return None

    async def _ai_review_loop(self):
        """Handle AI reviewer feedback loop"""
        iteration_count = 0
        
        while iteration_count < self.max_ai_iterations:
            print(f"🤖 AI Review iteration {iteration_count + 1}")
            
            # Get AI review
            review = await self._get_ai_review()
            
            if review.decision == "APPROVE":
                print("✅ AI Reviewer approved! Moving to human review.")
                self.workflow_state = "HUMAN_REVIEW"
                break
            else:
                print(f"❌ AI Reviewer rejected. Feedback: {review.feedback}")
                # Revise post based on feedback
                await self._revise_post(review.feedback, "AI")
                iteration_count += 1
        
        if iteration_count >= self.max_ai_iterations:
            print("⚠️ Max AI iterations reached. Moving to human review.")
            self.workflow_state = "HUMAN_REVIEW"
    
    async def _get_ai_review(self) -> ReviewResult:
        """Get review from AI reviewer"""
        reviewer_prompt = f"""Review this blog post for quality, clarity, relevance, and structure.

Title: {self.current_post.title}

Content:
{self.current_post.content}

Evaluate based on:
1. Writing quality and clarity
2. Structure and organization
3. Content value and relevance
4. Grammar and style
5. Engagement factor

Provide your decision and feedback in this format:
DECISION: APPROVE or REJECT
FEEDBACK: [If REJECT, provide specific, actionable feedback. If APPROVE, you can omit this or provide brief positive comments.]"""

        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=self.reviewer_persona,
            messages=[{"role": "user", "content": reviewer_prompt}]
        )
        
        review_response = response.content[0].text
        return self._parse_review_response(review_response)
    
    async def _human_review_loop(self):
        """Handle human review process"""
        while True:
            print("\n" + "="*70)
            print("👤 HUMAN REVIEW REQUIRED")
            print("="*70)
            print(f"Title: {self.current_post.title}")
            print(f"Version: {self.current_post.version}")
            print(f"Word count: ~{len(self.current_post.content.split())} words")
            print("-"*70)
            print(self.current_post.content)
            print("\n" + "="*70)
            
            # Get human input
            decision = input("Do you approve this post? (approve/reject): ").lower().strip()
            
            if decision == "approve":
                print("🎉 Human approved! Workflow complete.")
                self.workflow_state = "COMPLETED"
                
                # Update the post on the server if we have a post_id
                if self.current_post.post_id:
                    try:
                        # Save the final version to the blog server
                        await self._save_current_post_to_server()
                        print(f"✅ Final post saved with ID: {self.current_post.post_id}")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not update post on server: {e}")
                break
            elif decision == "reject":
                feedback = input("Please provide specific feedback for revision: ")
                print(f"📝 Human feedback received: {feedback}")
                await self._revise_post(feedback, "HUMAN")
                # Continue loop for another human review
            else:
                print("Please enter 'approve' or 'reject'")
    
    async def _revise_post(self, feedback: str, reviewer_type: str):
        """Revise post based on feedback"""
        print(f"✏️ Revising post based on {reviewer_type} feedback...")
        
        revision_prompt = f"""Revise this blog post based on the following feedback:

FEEDBACK: {feedback}

CURRENT TITLE: {self.current_post.title}

CURRENT CONTENT:
{self.current_post.content}

Requirements:
- Address all points in the feedback thoroughly
- Maintain overall quality and readability
- Keep the core theme and message
- Provide a complete, polished revision
- Update the title if needed

Format your response as:
TITLE: [Updated or original title]

CONTENT:
[Your revised blog post content]"""

        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=self.writer_persona,
            messages=[{"role": "user", "content": revision_prompt}]
        )
        
        revised_response = response.content[0].text
        revised_title, revised_content = self._parse_blog_response(revised_response)
        
        # Update post with revision
        self.current_post.content = revised_content
        self.current_post.title = revised_title
        self.current_post.version += 1
        self.current_post.feedback_history.append(f"{reviewer_type}: {feedback}")
        
        # Save the revised version to the server
        await self._save_current_post_to_server()
        
        print(f"📄 Post revised to version {self.current_post.version}")
    
    def _parse_review_response(self, response: str) -> ReviewResult:
        """Parse AI reviewer response into structured format"""
        lines = response.strip().split('\n')
        decision = "REJECT"  # Default to reject for safety
        feedback = None
        
        for line in lines:
            line_upper = line.upper()
            if "DECISION:" in line_upper:
                if "APPROVE" in line_upper:
                    decision = "APPROVE"
                elif "REJECT" in line_upper:
                    decision = "REJECT"
            elif "FEEDBACK:" in line_upper:
                feedback = line.split(":", 1)[1].strip()
                # Continue reading subsequent lines as part of feedback
                line_idx = lines.index(line)
                for subsequent_line in lines[line_idx + 1:]:
                    if subsequent_line.strip() and not subsequent_line.upper().startswith(("DECISION:", "FEEDBACK:")):
                        feedback += " " + subsequent_line.strip()
        
        return ReviewResult(decision=decision, feedback=feedback)
    
    async def _save_current_post_to_server(self):
        """Save the current post version to the blog server"""
        if not self.current_post.post_id:
            return
        
        try:
            result = await self.session.call_tool("update_blog_post", {
                "post_id": self.current_post.post_id,
                "title": self.current_post.title,
                "content": self.current_post.content
            })
            print(f"📁 Post updated on server: {result.content[0].text}")
        except Exception as e:
            print(f"⚠️ Could not update post on server: {e}")
    
    def get_workflow_summary(self) -> Dict:
        """Get summary of current workflow state"""
        return {
            "state": self.workflow_state,
            "post_version": self.current_post.version if self.current_post else 0,
            "feedback_count": len(self.current_post.feedback_history) if self.current_post else 0,
            "post_id": self.current_post.post_id if self.current_post else None,
            "title": self.current_post.title if self.current_post else None,
            "last_updated": self.current_post.created_at.isoformat() if self.current_post else None
        }
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
