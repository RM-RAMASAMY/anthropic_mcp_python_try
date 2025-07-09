# Orchestrator Utils

This directory contains utility modules for the blog workflow orchestrator.

## Modules

### `workflow_utils.py`
Core utility functions including:

- **WorkflowPersistence**: Save and load workflow state for resumability
- **WorkflowLogger**: Track workflow events and performance metrics  
- **ContentAnalyzer**: Analyze blog content for readability and structure

## Usage Examples

### Saving/Loading Workflow State
```python
from utils.workflow_utils import WorkflowPersistence

# Save current state
WorkflowPersistence.save_workflow_state(
    post=current_post, 
    workflow_state="AI_REVIEW", 
    filepath="saved_workflows/my_workflow.json"
)

# Load saved state
post, state = WorkflowPersistence.load_workflow_state(
    filepath="saved_workflows/my_workflow.json"
)
```

### Logging Workflow Events
```python
from utils.workflow_utils import WorkflowLogger

logger = WorkflowLogger("my_workflow.log")
logger.log_workflow_start("AI in Healthcare", "BlogBot", ["AI", "healthcare"])
logger.log_post_creation(blog_post)
logger.save_log()

# Get metrics
metrics = logger.get_workflow_metrics()
```

### Content Analysis
```python
from utils.workflow_utils import ContentAnalyzer

word_count = ContentAnalyzer.get_word_count(content)
reading_time = ContentAnalyzer.get_reading_time(content)
structure = ContentAnalyzer.get_content_structure(content)
readability = ContentAnalyzer.get_readability_score(content)
```
