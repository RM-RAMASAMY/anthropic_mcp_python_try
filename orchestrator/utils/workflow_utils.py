"""
Utility functions for the blog workflow orchestrator
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import asdict
from blog_workflow import BlogPost

class WorkflowPersistence:
    """Handle saving and loading workflow state for resumability"""
    
    @staticmethod
    def save_workflow_state(post: BlogPost, workflow_state: str, filepath: str):
        """Save current workflow state to a JSON file"""
        state = {
            "post": {
                "content": post.content,
                "version": post.version,
                "created_at": post.created_at.isoformat(),
                "feedback_history": post.feedback_history,
                "post_id": post.post_id,
                "title": post.title
            },
            "workflow_state": workflow_state,
            "saved_at": datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_workflow_state(filepath: str) -> tuple[BlogPost, str]:
        """Load workflow state from a JSON file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Workflow state file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        post_data = state["post"]
        post = BlogPost(
            content=post_data["content"],
            version=post_data["version"],
            created_at=datetime.fromisoformat(post_data["created_at"]),
            feedback_history=post_data["feedback_history"],
            post_id=post_data.get("post_id"),
            title=post_data.get("title")
        )
        
        return post, state["workflow_state"]

class WorkflowLogger:
    """Logger for tracking workflow events and metrics"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or f"workflow_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.events = []
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log a workflow event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.events.append(event)
    
    def log_workflow_start(self, theme: str, author: str, tags: List[str]):
        """Log workflow start"""
        self.log_event("workflow_start", {
            "theme": theme,
            "author": author,
            "tags": tags
        })
    
    def log_post_creation(self, post: BlogPost):
        """Log post creation"""
        self.log_event("post_created", {
            "title": post.title,
            "version": post.version,
            "word_count": len(post.content.split()),
            "post_id": post.post_id
        })
    
    def log_review(self, reviewer_type: str, decision: str, feedback: str = None):
        """Log review event"""
        self.log_event("review", {
            "reviewer_type": reviewer_type,
            "decision": decision,
            "feedback": feedback[:100] + "..." if feedback and len(feedback) > 100 else feedback
        })
    
    def log_revision(self, version: int, feedback_source: str):
        """Log revision event"""
        self.log_event("revision", {
            "new_version": version,
            "feedback_source": feedback_source
        })
    
    def log_workflow_complete(self, final_post: BlogPost):
        """Log workflow completion"""
        self.log_event("workflow_complete", {
            "final_version": final_post.version,
            "total_revisions": len(final_post.feedback_history),
            "final_word_count": len(final_post.content.split()),
            "post_id": final_post.post_id
        })
    
    def save_log(self):
        """Save the log to file"""
        log_data = {
            "workflow_session": {
                "start_time": self.events[0]["timestamp"] if self.events else datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_events": len(self.events)
            },
            "events": self.events
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        if not self.events:
            return {}
        
        start_time = datetime.fromisoformat(self.events[0]["timestamp"])
        end_time = datetime.fromisoformat(self.events[-1]["timestamp"])
        duration = (end_time - start_time).total_seconds()
        
        review_events = [e for e in self.events if e["event_type"] == "review"]
        revision_events = [e for e in self.events if e["event_type"] == "revision"]
        
        ai_reviews = len([e for e in review_events if e["details"]["reviewer_type"] == "AI"])
        human_reviews = len([e for e in review_events if e["details"]["reviewer_type"] == "HUMAN"])
        
        return {
            "total_duration_seconds": duration,
            "total_events": len(self.events),
            "ai_reviews": ai_reviews,
            "human_reviews": human_reviews,
            "total_revisions": len(revision_events),
            "avg_time_per_event": duration / len(self.events) if self.events else 0
        }

class ContentAnalyzer:
    """Analyze blog content for various metrics"""
    
    @staticmethod
    def get_word_count(content: str) -> int:
        """Get word count of content"""
        return len(content.split())
    
    @staticmethod
    def get_reading_time(content: str, wpm: int = 200) -> int:
        """Estimate reading time in minutes"""
        word_count = ContentAnalyzer.get_word_count(content)
        return max(1, round(word_count / wpm))
    
    @staticmethod
    def get_content_structure(content: str) -> Dict[str, int]:
        """Analyze content structure"""
        lines = content.split('\n')
        
        return {
            "total_lines": len(lines),
            "paragraphs": len([line for line in lines if line.strip() and not line.startswith('#')]),
            "headings": len([line for line in lines if line.strip().startswith('#')]),
            "bullet_points": len([line for line in lines if line.strip().startswith(('- ', '* ', '+ '))]),
            "numbered_lists": len([line for line in lines if line.strip()[0].isdigit() if line.strip()])
        }
    
    @staticmethod
    def get_readability_score(content: str) -> Dict[str, float]:
        """Basic readability analysis"""
        words = content.split()
        sentences = content.split('.')
        
        if not sentences or not words:
            return {"avg_words_per_sentence": 0.0, "avg_chars_per_word": 0.0}
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_chars_per_word = sum(len(word) for word in words) / len(words)
        
        return {
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "avg_chars_per_word": round(avg_chars_per_word, 2)
        }
