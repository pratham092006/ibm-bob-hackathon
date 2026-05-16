"""Comprehensive Integration Test Suite for Dev 2's Executor Module.

⚠️ WARNING: Running this test will:
- Move your mouse cursor (small movements)
- Type text (safe test strings)
- Trigger keyboard shortcuts
- Create log files

Please ensure you're ready before running this test.
Close any important applications that might be affected.

This test suite verifies:
1. Integration Contract (PRD lines 134-149)
2. End-to-End Action Flow
3. Kill Switch Integration
4. Cross-Module Integration
5. Action Logging Integration
6. Stuck-Loop Detection Integration
"""

import unittest
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime

# Add axon to path
sys.path.insert(0, str(Path(__file__).parent))

from executor.actions import execute_action, action_history, log_action_to_file
from executor.kill_switch import start_kill_switch, stop_kill_switch, KillSwitch
from executor.win_api import get_active_window
from executor.app_handlers import get_app_shortcuts, execute_app_shortcut
from config import status_queue, kill_event
import pyautogui


class TestExecutorIntegration(unittest.TestCase):
    """Integration tests for Dev 2's executor module."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test suite - runs once before all tests."""
        print("\n" + "="*70)
        print("EXECUTOR MODULE INTEGRATION TEST SUITE")
        print("="*70)
        print("\n⚠️  WARNING: This test will move your mouse and type text!")
        print("Please ensure you're ready before continuing.\n")
        print("="*70 + "\n")
        
        # Store original screen size for validation
        cls.screen_width, cls.screen_height = pyautogui.size()
        print(f"Screen size detected: {cls.screen_width}x{cls.screen_height}")
        
        # Clean up any existing log file
        cls.log_file = Path(__file__).parent / "session_log.json"
        if cls.log_file.exists():
            cls.log_file.unlink()
            print(f"Cleaned up existing log file: {cls.log_file}")
    
    def setUp(self):
        """Reset state before each test."""
        # Clear kill_event
        kill_event.clear()
        
        # Clear status_queue
        while not status_queue.empty():
            try:
                status_queue.get_nowait()
            except:
                break
        
        # Clear action history
        action_history.clear()
        
        # Small delay to ensure clean state
        time.sleep(0.1)
    
    def tearDown(self):
        """Clean up after each test."""
        # Ensure kill_event is cleared
        kill_event.clear()
        time.sleep(0.1)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        print("\n" + "="*70)
        print("TEST SUITE COMPLETE")
        print("="*70 + "\n")
    
    # ========================================================================
    # 1. INTEGRATION CONTRACT VERIFICATION (PRD lines 134-149)
    # ========================================================================
    
    def test_01_integration_contract_kill_event(self):
        """Verify kill_event is accessible from executor.kill_switch."""
        print("\n[TEST 1.1] Integration Contract: kill_event accessibility")
        
        # Import kill_event from kill_switch module
        from executor.kill_switch import kill_event as ks_kill_event
        
        # Verify it's a threading.Event
        self.assertIsInstance(kill_event, threading.Event,
                            "kill_event should be a threading.Event")
        
        # Verify it's the same object as in config
        self.assertIs(kill_event, ks_kill_event,
                     "kill_event should be the same object across modules")
        
        # Verify it can be set and cleared
        kill_event.set()
        self.assertTrue(kill_event.is_set(), "kill_event should be settable")
        
        kill_event.clear()
        self.assertFalse(kill_event.is_set(), "kill_event should be clearable")
        
        print("✓ kill_event is accessible and functional")
    
    def test_02_integration_contract_execute_function(self):
        """Verify execute_action function exists and accepts action dicts."""
        print("\n[TEST 1.2] Integration Contract: execute_action function")
        
        # Verify function exists
        from executor.actions import execute_action
        self.assertTrue(callable(execute_action),
                       "execute_action should be callable")
        
        # Verify it accepts action dict (test with safe mouse_move)
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        
        action_dict = {
            "action": "mouse_move",
            "coordinate": [safe_x, safe_y]
        }
        
        result = execute_action(action_dict)
        self.assertIsInstance(result, bool,
                            "execute_action should return bool")
        self.assertTrue(result, "execute_action should succeed for valid action")
        
        print("✓ execute_action exists and accepts action dicts")
    
    def test_03_integration_contract_all_action_types(self):
        """Verify all action types from PRD work correctly."""
        print("\n[TEST 1.3] Integration Contract: All action types")
        
        # Safe coordinates for testing
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        
        # Test each action type from PRD (lines 68-74)
        action_types = [
            {"action": "left_click", "coordinate": [safe_x, safe_y]},
            {"action": "right_click", "coordinate": [safe_x, safe_y]},
            {"action": "type", "text": "test"},
            {"action": "key", "text": "escape"},  # Safe key
            {"action": "scroll", "coordinate": [safe_x, safe_y], 
             "direction": "down", "amount": 1},
            {"action": "mouse_move", "coordinate": [safe_x + 10, safe_y + 10]},
        ]
        
        for action_dict in action_types:
            with self.subTest(action=action_dict["action"]):
                result = execute_action(action_dict)
                self.assertTrue(result, 
                              f"Action {action_dict['action']} should succeed")
                time.sleep(0.2)  # Small delay between actions
        
        print("✓ All action types from PRD work correctly")
    
    # ========================================================================
    # 2. END-TO-END ACTION FLOW
    # ========================================================================
    
    def test_04_end_to_end_left_click(self):
        """Test complete flow: action dict → execute → result for left_click."""
        print("\n[TEST 2.1] End-to-End: left_click action")
        
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        
        action_dict = {"action": "left_click", "coordinate": [safe_x, safe_y]}
        
        # Execute action
        result = execute_action(action_dict)
        
        # Verify result
        self.assertTrue(result, "left_click should succeed")
        
        # Verify action was logged
        self.assertTrue(self.log_file.exists(), "Log file should be created")
        
        print("✓ left_click end-to-end flow works")
    
    def test_05_end_to_end_type_action(self):
        """Test complete flow for type action."""
        print("\n[TEST 2.2] End-to-End: type action")
        
        action_dict = {"action": "type", "text": "Hello AXON"}
        
        result = execute_action(action_dict)
        self.assertTrue(result, "type action should succeed")
        
        print("✓ type action end-to-end flow works")
    
    def test_06_end_to_end_key_combination(self):
        """Test complete flow for key combination."""
        print("\n[TEST 2.3] End-to-End: key combination")
        
        # Use safe key combination (escape)
        action_dict = {"action": "key", "text": "escape"}
        
        result = execute_action(action_dict)
        self.assertTrue(result, "key action should succeed")
        
        print("✓ key combination end-to-end flow works")
    
    def test_07_end_to_end_scroll_action(self):
        """Test complete flow for scroll action."""
        print("\n[TEST 2.4] End-to-End: scroll action")
        
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        
        action_dict = {
            "action": "scroll",
            "coordinate": [safe_x, safe_y],
            "direction": "down",
            "amount": 2
        }
        
        result = execute_action(action_dict)
        self.assertTrue(result, "scroll action should succeed")
        
        print("✓ scroll action end-to-end flow works")
    
    def test_08_end_to_end_done_action(self):
        """Test complete flow for done action (sets kill_event)."""
        print("\n[TEST 2.5] End-to-End: done action")
        
        # Ensure kill_event is clear
        kill_event.clear()
        self.assertFalse(kill_event.is_set(), "kill_event should start clear")
        
        action_dict = {"action": "done"}
        
        result = execute_action(action_dict)
        self.assertTrue(result, "done action should succeed")
        
        # Verify kill_event is set
        self.assertTrue(kill_event.is_set(), 
                       "done action should set kill_event")
        
        print("✓ done action end-to-end flow works")
    
    # ========================================================================
    # 3. KILL SWITCH INTEGRATION
    # ========================================================================
    
    def test_09_kill_switch_start_stop(self):
        """Test kill switch can start and stop cleanly."""
        print("\n[TEST 3.1] Kill Switch: Start and Stop")
        
        # Start kill switch
        kill_switch = start_kill_switch()
        self.assertIsNotNone(kill_switch, "Kill switch should start")
        self.assertIsInstance(kill_switch, KillSwitch,
                            "Should return KillSwitch instance")
        
        # Verify it's running
        if kill_switch:
            self.assertTrue(kill_switch.is_running,
                           "Kill switch should be running")
            
            # Stop kill switch
            stop_kill_switch(kill_switch)
            self.assertFalse(kill_switch.is_running,
                            "Kill switch should stop")
        
        print("✓ Kill switch starts and stops cleanly")
    
    def test_10_kill_switch_programmatic_trigger(self):
        """Test kill switch can be triggered programmatically."""
        print("\n[TEST 3.2] Kill Switch: Programmatic Trigger")
        
        # Start kill switch
        kill_switch = start_kill_switch()
        self.assertIsNotNone(kill_switch, "Kill switch should start")
        
        # Clear kill_event and status_queue
        kill_event.clear()
        while not status_queue.empty():
            status_queue.get_nowait()
        
        # Trigger kill switch programmatically
        if kill_switch:
            kill_switch.trigger()
            
            # Verify kill_event is set
            self.assertTrue(kill_event.is_set(),
                           "Trigger should set kill_event")
        else:
            self.fail("Kill switch failed to start")
        
        # Verify status_queue receives message
        self.assertFalse(status_queue.empty(),
                        "Status queue should have message")
        
        status_msg = status_queue.get()
        self.assertIn("status", status_msg,
                     "Status message should have 'status' key")
        self.assertEqual(status_msg["status"], "killed",
                        "Status should be 'killed'")
        
        # Clean up
        stop_kill_switch(kill_switch)
        
        print("✓ Kill switch programmatic trigger works")
    
    # ========================================================================
    # 4. CROSS-MODULE INTEGRATION
    # ========================================================================
    
    def test_11_cross_module_imports(self):
        """Test that modules can import from each other."""
        print("\n[TEST 4.1] Cross-Module: Import Integration")
        
        # Test actions.py can import from kill_switch.py
        try:
            from executor.actions import kill_event as actions_kill_event
            self.assertIsNotNone(actions_kill_event,
                               "actions.py should import kill_event")
        except ImportError as e:
            self.fail(f"actions.py failed to import from kill_switch: {e}")
        
        # Test app_handlers.py can use win_api.py
        try:
            from executor.app_handlers import get_app_shortcuts
            shortcuts = get_app_shortcuts("notepad")
            self.assertIsInstance(shortcuts, dict,
                                "app_handlers should use win_api")
        except Exception as e:
            self.fail(f"app_handlers failed to use win_api: {e}")
        
        # Test all modules can access config.py
        try:
            from executor.actions import status_queue as actions_queue
            from executor.kill_switch import kill_event as ks_kill_event
            
            self.assertIs(actions_queue, status_queue,
                         "All modules should share config.status_queue")
            self.assertIs(ks_kill_event, kill_event,
                         "All modules should share config.kill_event")
        except Exception as e:
            self.fail(f"Modules failed to access config: {e}")
        
        print("✓ Cross-module imports work correctly")
    
    def test_12_cross_module_shared_state(self):
        """Test that shared state works across modules."""
        print("\n[TEST 4.2] Cross-Module: Shared State")
        
        # Test kill_event is shared
        from executor.actions import kill_event as actions_kill_event
        from executor.kill_switch import kill_event as ks_kill_event
        
        # Set in one module
        actions_kill_event.set()
        
        # Check in another module
        self.assertTrue(ks_kill_event.is_set(),
                       "kill_event should be shared across modules")
        
        # Clear and verify
        ks_kill_event.clear()
        self.assertFalse(actions_kill_event.is_set(),
                        "Changes should propagate across modules")
        
        print("✓ Shared state works across modules")
    
    # ========================================================================
    # 5. ACTION LOGGING INTEGRATION
    # ========================================================================
    
    def test_13_action_logging_creates_file(self):
        """Test that executing actions creates session_log.json."""
        print("\n[TEST 5.1] Action Logging: File Creation")
        
        # Remove log file if exists
        if self.log_file.exists():
            self.log_file.unlink()
        
        # Execute an action
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        action_dict = {"action": "mouse_move", "coordinate": [safe_x, safe_y]}
        
        execute_action(action_dict)
        
        # Verify log file is created
        self.assertTrue(self.log_file.exists(),
                       "session_log.json should be created")
        
        print("✓ Action logging creates log file")
    
    def test_14_action_logging_format(self):
        """Test that log entries have correct format."""
        print("\n[TEST 5.2] Action Logging: Entry Format")
        
        # Execute multiple actions
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        
        actions = [
            {"action": "mouse_move", "coordinate": [safe_x, safe_y]},
            {"action": "left_click", "coordinate": [safe_x, safe_y]},
            {"action": "type", "text": "test"}
        ]
        
        for action in actions:
            execute_action(action)
            time.sleep(0.1)
        
        # Read log file
        with open(self.log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        self.assertIsInstance(logs, list, "Log should be a list")
        self.assertGreaterEqual(len(logs), 3, "Should have at least 3 entries")
        
        # Verify format of last entry
        last_entry = logs[-1]
        
        required_keys = ["timestamp", "action", "details", "success", 
                        "execution_time_ms"]
        for key in required_keys:
            self.assertIn(key, last_entry,
                         f"Log entry should have '{key}' field")
        
        # Verify timestamp is valid ISO format
        try:
            datetime.fromisoformat(last_entry["timestamp"])
        except ValueError:
            self.fail("Timestamp should be valid ISO format")
        
        print("✓ Log entries have correct format")
    
    def test_15_action_logging_timestamps(self):
        """Test that timestamps are valid and sequential."""
        print("\n[TEST 5.3] Action Logging: Timestamp Validation")
        
        # Execute actions with delays
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        
        action_dict = {"action": "mouse_move", "coordinate": [safe_x, safe_y]}
        
        execute_action(action_dict)
        time.sleep(0.2)
        execute_action(action_dict)
        
        # Read log file
        with open(self.log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        # Get last two entries
        if len(logs) >= 2:
            entry1 = logs[-2]
            entry2 = logs[-1]
            
            time1 = datetime.fromisoformat(entry1["timestamp"])
            time2 = datetime.fromisoformat(entry2["timestamp"])
            
            self.assertLess(time1, time2,
                          "Timestamps should be sequential")
        
        print("✓ Timestamps are valid and sequential")
    
    # ========================================================================
    # 6. STUCK-LOOP DETECTION INTEGRATION
    # ========================================================================
    
    def test_16_stuck_loop_detection(self):
        """Test that executing same action 3 times triggers stuck detection."""
        print("\n[TEST 6.1] Stuck-Loop Detection: Trigger")
        
        # Clear state
        kill_event.clear()
        action_history.clear()
        while not status_queue.empty():
            status_queue.get_nowait()
        
        # Execute same action 3 times
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        action_dict = {"action": "left_click", "coordinate": [safe_x, safe_y]}
        
        # First two should succeed
        result1 = execute_action(action_dict)
        self.assertTrue(result1, "First action should succeed")
        time.sleep(0.1)
        
        result2 = execute_action(action_dict)
        self.assertTrue(result2, "Second action should succeed")
        time.sleep(0.1)
        
        # Third should trigger stuck loop
        result3 = execute_action(action_dict)
        self.assertFalse(result3, "Third action should fail (stuck loop)")
        
        # Verify kill_event is set
        self.assertTrue(kill_event.is_set(),
                       "Stuck loop should set kill_event")
        
        # Verify status_queue receives "stuck" message
        self.assertFalse(status_queue.empty(),
                        "Status queue should have stuck message")
        
        status_msg = status_queue.get()
        self.assertEqual(status_msg["type"], "stuck",
                        "Message type should be 'stuck'")
        
        print("✓ Stuck-loop detection triggers correctly")
    
    def test_17_stuck_loop_action_history(self):
        """Test that action history is tracked correctly."""
        print("\n[TEST 6.2] Stuck-Loop Detection: Action History")
        
        # Clear history
        action_history.clear()
        kill_event.clear()
        
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        
        # Execute different actions
        actions = [
            {"action": "mouse_move", "coordinate": [safe_x, safe_y]},
            {"action": "left_click", "coordinate": [safe_x + 10, safe_y]},
            {"action": "type", "text": "test"}
        ]
        
        for action in actions:
            execute_action(action)
            time.sleep(0.1)
        
        # Verify history has 3 entries
        self.assertEqual(len(action_history), 3,
                        "Action history should track last 3 actions")
        
        # Verify no stuck loop detected (different actions)
        self.assertFalse(kill_event.is_set(),
                        "Different actions should not trigger stuck loop")
        
        print("✓ Action history tracking works correctly")
    
    def test_18_stuck_loop_coordinate_tolerance(self):
        """Test that stuck loop detection has coordinate tolerance."""
        print("\n[TEST 6.3] Stuck-Loop Detection: Coordinate Tolerance")
        
        # Clear state
        action_history.clear()
        kill_event.clear()
        
        safe_x = self.screen_width // 2
        safe_y = self.screen_height // 2
        
        # Execute clicks with small coordinate differences (within 5px)
        actions = [
            {"action": "left_click", "coordinate": [safe_x, safe_y]},
            {"action": "left_click", "coordinate": [safe_x + 2, safe_y + 2]},
            {"action": "left_click", "coordinate": [safe_x + 4, safe_y + 3]}
        ]
        
        for i, action in enumerate(actions):
            result = execute_action(action)
            if i < 2:
                self.assertTrue(result, f"Action {i+1} should succeed")
            else:
                self.assertFalse(result, "Third action should fail (stuck)")
            time.sleep(0.1)
        
        # Should trigger stuck loop (within tolerance)
        self.assertTrue(kill_event.is_set(),
                       "Similar coordinates should trigger stuck loop")
        
        print("✓ Coordinate tolerance works correctly")


def run_integration_tests():
    """Run the integration test suite with detailed output."""
    print("\n" + "="*70)
    print("STARTING EXECUTOR MODULE INTEGRATION TESTS")
    print("="*70)
    print("\nThis will test:")
    print("  1. Integration Contract Verification")
    print("  2. End-to-End Action Flow")
    print("  3. Kill Switch Integration")
    print("  4. Cross-Module Integration")
    print("  5. Action Logging Integration")
    print("  6. Stuck-Loop Detection Integration")
    print("\n" + "="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestExecutorIntegration)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
        print("\nDev 2's executor module is ready to integrate with:")
        print("  - Dev 1's loop (core/loop.py)")
        print("  - Dev 3's UI (ui/overlay.py, ui/tray.py)")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please review the failures above and fix the issues.")
    
    print("="*70 + "\n")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_integration_tests())

# Made with Bob