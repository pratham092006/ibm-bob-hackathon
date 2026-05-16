"""Main control loop for AXON agent.

Dev 1 (Joshua) - Vision & Brain
TODO: Implement main agent loop
- Run continuous loop that captures screen, calls LLM, executes actions
- Check kill_event from config.py on each iteration
- Respect MAX_LOOP_DELAY from config.py between iterations
- Update status_queue with current state for UI
- Handle exceptions gracefully and log errors
- Coordinate between capture, LLM, and executor modules
- Maintain conversation history for context
"""

import time
from config import kill_event, status_queue, MAX_LOOP_DELAY
from core.capture import capture_screen
from core.llm import call_llm
# from executor.actions import execute_action  # Will be implemented by Dev 2


def run_agent_loop(task_description):
    """Main agent loop that runs until task completion or kill signal.
    
    Args:
        task_description (str): User's goal/task to accomplish
    """
    # TODO: Implement main agent loop
    # 1. Initialize conversation history
    # 2. Start loop:
    #    a. Check kill_event - if set, break loop
    #    b. Capture screen using capture.capture_screen()
    #    c. Call LLM with screen and task using llm.call_llm()
    #    d. Parse action from LLM response
    #    e. If action is 'done', break loop
    #    f. Execute action using executor.actions.execute_action()
    #    g. Update status_queue with current state
    #    h. Sleep for MAX_LOOP_DELAY
    # 3. Clean up and exit
    
    print(f"Starting agent loop for task: {task_description}")
    conversation_history = []
    
    while not kill_event.is_set():
        try:
            # TODO: Implement loop body
            status_queue.put({"status": "running", "message": "Processing..."})
            time.sleep(MAX_LOOP_DELAY)
            
        except Exception as e:
            print(f"Error in agent loop: {e}")
            status_queue.put({"status": "error", "message": str(e)})
            break
    
    print("Agent loop stopped")
    status_queue.put({"status": "stopped", "message": "Agent stopped"})


def stop_agent():
    """Signal the agent loop to stop."""
    # TODO: Set kill_event to stop the loop
    kill_event.set()
    print("Stop signal sent to agent")

# Made with Bob
