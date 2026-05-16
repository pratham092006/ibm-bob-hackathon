"""Task planning and decomposition module.

Dev 1 (Joshua) - Vision & Brain
TODO: Implement task planning functionality
- Break down high-level user goals into subtasks
- Use LLM to analyze task complexity
- Generate step-by-step plan for complex tasks
- Track progress through subtasks
- Adapt plan based on execution results
- Handle task dependencies and prerequisites
"""

from core.llm import call_llm


def decompose_task(task_description):
    """Break down a high-level task into subtasks.
    
    For opening applications, uses Windows Search (Win key + type + Enter)
    which is MORE RELIABLE than clicking taskbar icons.
    
    Args:
        task_description (str): User's high-level goal
        
    Returns:
        list: List of subtask descriptions in execution order
    """
    task_lower = task_description.lower()
    
    # Detect application opening requests
    app_keywords = ['open', 'launch', 'start', 'run']
    if any(keyword in task_lower for keyword in app_keywords):
        # Extract app name
        app_name = None
        
        # Common applications
        if 'chrome' in task_lower:
            app_name = 'chrome'
        elif 'firefox' in task_lower:
            app_name = 'firefox'
        elif 'notepad' in task_lower:
            app_name = 'notepad'
        elif 'edge' in task_lower:
            app_name = 'edge'
        elif 'explorer' in task_lower or 'file explorer' in task_lower:
            app_name = 'explorer'
        elif 'calculator' in task_lower or 'calc' in task_lower:
            app_name = 'calculator'
        elif 'paint' in task_lower:
            app_name = 'paint'
        elif 'word' in task_lower:
            app_name = 'word'
        elif 'excel' in task_lower:
            app_name = 'excel'
        elif 'powerpoint' in task_lower:
            app_name = 'powerpoint'
        elif 'vscode' in task_lower or 'visual studio code' in task_lower:
            app_name = 'code'
        else:
            # Try to extract app name from task
            for keyword in app_keywords:
                if keyword in task_lower:
                    parts = task_lower.split(keyword)
                    if len(parts) > 1:
                        app_name = parts[1].strip().split()[0] if parts[1].strip() else None
                    break
        
        # If we identified an app, use Windows Search method
        if app_name:
            return [
                f"Press Windows key to open search",
                f"Type '{app_name}' in search box",
                f"Press Enter to launch {app_name}",
                f"Wait for {app_name} to open"
            ]
    
    # For other tasks, return as single step
    # Can be enhanced with LLM-based decomposition later
    return [task_description]


def create_task_plan(task_description, screen_context=None):
    """Create a detailed execution plan for a task.
    
    Args:
        task_description (str): User's goal
        screen_context (bytes, optional): Current screen capture for context
        
    Returns:
        dict: Task plan with subtasks and metadata
            {
                'task': str,
                'subtasks': list of str,
                'estimated_steps': int,
                'complexity': 'simple' | 'medium' | 'complex'
            }
    """
    # TODO: Implement task planning
    # 1. Capture screen if not provided
    # 2. Use LLM to analyze task and screen
    # 3. Generate subtasks
    # 4. Estimate complexity and steps
    # 5. Return structured plan
    pass


def update_plan_progress(plan, completed_subtask_index):
    """Update plan with completed subtask.
    
    Args:
        plan (dict): Current task plan
        completed_subtask_index (int): Index of completed subtask
        
    Returns:
        dict: Updated plan with progress
    """
    # TODO: Implement progress tracking
    pass

# Made with Bob
