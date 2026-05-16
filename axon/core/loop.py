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
import os
import cv2
import numpy as np
from config import kill_event, status_queue, ui_queue, task_queue, MAX_LOOP_DELAY, DEBUG_MODE, FAST_MODE
from core.capture import capture_screen
from core.llm import call_llm, get_screen_elements
from executor.actions import execute_action


def _is_simple_task(task):
    """Check if task is simple enough to skip OCR.
    
    Simple tasks like "Open Chrome" don't need OCR since we use
    the atomic open_app action.
    
    Args:
        task (str): Task description
        
    Returns:
        bool: True if task is simple (skip OCR)
    """
    simple_keywords = ['open', 'launch', 'start', 'close', 'run']
    task_lower = task.lower()
    return any(keyword in task_lower for keyword in simple_keywords)


def _broadcast_status(status_dict):
    """Push status update to both tray and UI queues.
    
    This prevents the race condition where one consumer steals
    messages meant for the other.
    
    Args:
        status_dict (dict): Status update to broadcast
    """
    status_queue.put(status_dict)
    ui_queue.put(status_dict)


def _save_debug_screenshot(screen_image, action_dict, action_count):
    """Save annotated screenshot showing where the LLM wants to click.
    
    Args:
        screen_image: Screenshot bytes (JPEG)
        action_dict: Action dictionary with coordinate info
        action_count: Current action number
    """
    if not DEBUG_MODE:
        return
    
    try:
        # Create debug directory if it doesn't exist
        debug_dir = os.path.join('bob-reports', 'debug_screenshots')
        os.makedirs(debug_dir, exist_ok=True)
        
        # Convert bytes to numpy array for OpenCV
        nparr = np.frombuffer(screen_image, np.uint8)
        debug_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if debug_image is None:
            print("[DEBUG] Failed to decode image for debug screenshot")
            return
        
        # Get action info
        action_type = action_dict.get('action', 'unknown')
        reasoning = action_dict.get('reasoning', 'No reasoning')
        confidence = action_dict.get('confidence', 0.0)
        
        # Draw coordinate marker if present
        if 'coordinate' in action_dict:
            x, y = action_dict['coordinate']
            
            # Draw red circle at click point
            cv2.circle(debug_image, (x, y), 15, (0, 0, 255), 3)
            cv2.circle(debug_image, (x, y), 3, (0, 0, 255), -1)
            
            # Draw crosshair
            cv2.line(debug_image, (x-25, y), (x+25, y), (0, 0, 255), 2)
            cv2.line(debug_image, (x, y-25), (x, y+25), (0, 0, 255), 2)
            
            # Add coordinate label
            label = f"({x}, {y})"
            cv2.putText(debug_image, label, (x+20, y-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Add action info overlay at top
        overlay_height = 100
        overlay = debug_image.copy()
        cv2.rectangle(overlay, (0, 0), (debug_image.shape[1], overlay_height),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, debug_image, 0.3, 0, debug_image)
        
        # Add text info
        y_offset = 25
        cv2.putText(debug_image, f"Action #{action_count}: {action_type}",
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30
        cv2.putText(debug_image, f"Confidence: {confidence:.2f}",
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_offset += 25
        # Truncate reasoning if too long
        reasoning_short = reasoning[:80] + "..." if len(reasoning) > 80 else reasoning
        cv2.putText(debug_image, f"Reasoning: {reasoning_short}",
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Save with timestamp
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        filename = f"action_{action_count:03d}_{action_type}_{timestamp}.jpg"
        filepath = os.path.join(debug_dir, filename)
        cv2.imwrite(filepath, debug_image)
        
        print(f"[DEBUG] Saved debug screenshot: {filepath}")
        
    except Exception as e:
        print(f"[DEBUG] Error saving debug screenshot: {e}")
        import traceback
        traceback.print_exc()


def run_agent_loop(task_description):
    """Main agent loop that runs until task completion or kill signal.
    
    Args:
        task_description (str): User's goal/task to accomplish
    """
    print(f"[AGENT LOOP] Starting for task: {task_description}")
    conversation_history = []
    action_count = 0
    
    # Clear kill_event at start
    kill_event.clear()
    print("[AGENT LOOP] Kill event cleared")
    
    # Create debug directory if DEBUG_MODE is enabled
    if DEBUG_MODE:
        debug_dir = os.path.join('bob-reports', 'debug_screenshots')
        os.makedirs(debug_dir, exist_ok=True)
        print(f"[AGENT LOOP] Debug mode enabled - screenshots will be saved to {debug_dir}")
    
    # Send initial status
    _broadcast_status({
        "type": "task_start",
        "task": task_description,
        "message": "Starting task..."
    })
    print("[AGENT LOOP] Initial status sent to UI")
    
    while not kill_event.is_set():
        try:
            print(f"\n[AGENT LOOP] === Iteration {action_count + 1} ===")
            
            # Update status - thinking
            _broadcast_status({
                "type": "thinking",
                "message": "Analyzing screen...",
                "task": task_description,
                "action_count": action_count
            })
            print("[AGENT LOOP] Status: Thinking...")
            
            # Capture screen
            print("[AGENT LOOP] Capturing screen...")
            screen_image = capture_screen()
            if screen_image is None:
                print("[AGENT LOOP] ERROR: Failed to capture screen")
                _broadcast_status({
                    "type": "error",
                    "message": "Failed to capture screen"
                })
                break
            
            # Call LLM with screen and task
            print("[AGENT LOOP] Calling Gemini API...")
            start_time = time.time()
            try:
                action_dict = call_llm(screen_image, task_description, conversation_history)
                response_time = time.time() - start_time
                print(f"[AGENT LOOP] API response received in {response_time:.2f}s")
            except Exception as e:
                print(f"[AGENT LOOP] ERROR calling LLM: {e}")
                import traceback
                traceback.print_exc()
                action_dict = {
                    "action": "error",
                    "reasoning": f"LLM call failed: {str(e)}",
                    "outcome": "error"
                }
                response_time = time.time() - start_time
            
            # Get action type
            action_type = action_dict.get('action', 'unknown')
            reasoning = action_dict.get('reasoning', 'No reasoning provided')
            confidence = action_dict.get('confidence', 0.0)
            
            # VERBOSE LOGGING - Show what the model is thinking
            print(f"\n{'='*80}")
            print(f"[ITERATION {action_count + 1}] MODEL DECISION:")
            print(f"{'='*80}")
            print(f"🎯 Action: {action_type}")
            print(f"💭 Reasoning: {reasoning}")
            print(f"📊 Confidence: {confidence:.2%}")
            if 'coordinate' in action_dict:
                coord = action_dict['coordinate']
                print(f"📍 Target: ({coord[0]}, {coord[1]})")
            if 'text' in action_dict:
                print(f"⌨️  Text: '{action_dict['text']}'")
            print(f"{'='*80}\n")
            
            # Save debug screenshot with annotation BEFORE executing action
            if DEBUG_MODE and action_type not in ['error', 'wait']:
                _save_debug_screenshot(screen_image, action_dict, action_count + 1)
            
            # Update status with action (includes coordinate info for reticle)
            # This broadcasts BEFORE execution so cursor moves to position first
            _broadcast_status({
                "type": "action",
                "action": action_dict,
                "message": f"Action: {action_type}",
                "reasoning": reasoning,
                "task": task_description,
                "response_time": response_time,
                "action_count": action_count
            })
            
            # Small delay to allow overlay to update position before action executes
            time.sleep(0.1)
            
            # Check if task is done
            if action_type == 'done':
                print("[AGENT LOOP] Task completed successfully!")
                _broadcast_status({
                    "type": "task_complete",
                    "message": "Task completed!",
                    "task": task_description,
                    "action_count": action_count
                })
                break
            
            # Check if error occurred
            if action_type == 'error':
                print(f"[AGENT LOOP] Error: {reasoning}")
                _broadcast_status({
                    "type": "error",
                    "message": reasoning,
                    "task": task_description,
                    "action_count": action_count
                })
                break
            
            # Handle "wait" (malformed LLM response — just retry next iteration)
            if action_type == 'wait':
                print("[AGENT LOOP] LLM returned wait, retrying in 1s...")
                time.sleep(1.0)
                continue
            
            # Execute the action
            print(f"[AGENT LOOP] Executing action: {action_type}")
            success = execute_action(action_dict)
            action_count += 1
            
            # Determine outcome for progress tracking
            if not success:
                print(f"[AGENT LOOP] WARNING: Failed to execute action: {action_type}")
                action_dict['outcome'] = 'warning'
            else:
                print(f"[AGENT LOOP] Action executed successfully")
                action_dict['outcome'] = 'success'
            
            # Add to conversation history with outcome
            conversation_history.append(action_dict)
            
            # Sleep before next iteration (allow screen to update)
            # Different actions need different wait times
            if action_type == 'open_app':
                delay = 3.0  # Apps need time to launch and render UI
            elif action_type in ['click', 'left_click', 'right_click', 'double_click']:
                delay = 1.5  # Clicks trigger UI changes that take time
            elif action_type == 'key' and action_dict.get('text', '') == 'enter':
                delay = 2.0  # Enter often launches apps, needs more time
            elif action_type == 'type':
                delay = 0.5  # Typing is fast
            else:
                delay = 0.8  # Other actions
            print(f"[AGENT LOOP] Sleeping for {delay}s...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"[AGENT LOOP] ERROR: {e}")
            import traceback
            traceback.print_exc()
            _broadcast_status({
                "type": "error",
                "message": str(e),
                "task": task_description,
                "action_count": action_count
            })
            break
    
    print("[AGENT LOOP] Stopped")
    _broadcast_status({
        "type": "stopped",
        "message": "Agent stopped",
        "task": task_description,
        "action_count": action_count
    })


def stop_agent():
    """Signal the agent loop to stop."""
    kill_event.set()
    print("Stop signal sent to agent")


def start_monitoring():
    """Start the monitoring loop (for background thread).
    
    This function waits for tasks to be submitted via task_queue
    and starts the agent loop when a task is received.
    """
    print("[MONITORING] Loop started, waiting for tasks...")
    
    while True:
        try:
            # Check for tasks in task_queue (blocking with timeout)
            try:
                task = task_queue.get(timeout=0.5)
                if task:
                    print(f"[MONITORING] Received task: {task}")
                    try:
                        run_agent_loop(task)
                    except Exception as e:
                        print(f"[MONITORING] ERROR in agent loop: {e}")
                        import traceback
                        traceback.print_exc()
                        # Send error to both queues
                        _broadcast_status({
                            "type": "error",
                            "message": f"Agent loop crashed: {str(e)}"
                        })
            except:
                # Timeout, continue waiting
                pass
            
        except Exception as e:
            print(f"[MONITORING] Error in monitoring loop: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(1)


def activate_agent(task_description):
    """Activate the agent with a new task.
    
    Args:
        task_description (str): User's goal/task to accomplish
    """
    print(f"[ACTIVATE] Activating agent with task: {task_description}")
    
    # Clear kill_event
    kill_event.clear()
    
    # Put task in task_queue for monitoring loop to pick up
    task_queue.put(task_description)
    print(f"[ACTIVATE] Task added to queue")
    
    # Also send initial status to both queues
    _broadcast_status({
        'type': 'task_start',
        'task': task_description,
        'message': 'Task submitted...'
    })

# Made with Bob
