"""Floating task input dialog.

Dev 3 (Pratham) - UI & Demo
Implements task input dialog with:
- Floating dialog window for task input
- Text input field for typing tasks
- Submit button to start agent
- Draggable window
- Modern UI design
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                              QLineEdit, QPushButton, QLabel, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont
import sys
import os

# Import LLM functions for model switching
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.llm import switch_provider, get_current_provider, get_current_model, get_model_display_name
except ImportError:
    # Fallback if import fails
    def switch_provider(provider): return True
    def get_current_provider(): return "gemini"
    def get_current_model(): return "flash"
    def get_model_display_name(): return "Gemini 2.0 Flash"


class TaskInputDialog(QDialog):
    """Floating dialog for task input."""
    
    task_submitted = pyqtSignal(str)  # Signal when task is submitted
    
    def __init__(self):
        """Initialize the input dialog."""
        super().__init__()
        self.drag_position = QPoint()
        self.init_ui()
        
    def init_ui(self):
        """Set up the dialog UI."""
        # Set window properties (frameless, always on top)
        self.setWindowTitle("AXON - Task Input")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set fixed size
        self.setFixedSize(500, 200)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container widget with styling
        container = QLabel()
        container.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 10px;
                border: 2px solid rgba(100, 200, 255, 180);
            }
        """)
        
        # Create inner layout
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title label
        title_label = QLabel("AXON Task Input")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: rgba(100, 200, 255, 255); background: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(title_label)
        
        # Add model selection dropdown
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        model_label.setFont(QFont("Segoe UI", 10))
        model_label.setStyleSheet("color: rgba(200, 200, 200, 255); background: transparent; border: none;")
        model_layout.addWidget(model_label)
        
        self.model_selector = QComboBox()
        
        # Add Gemini models
        self.model_selector.addItem("Gemini 2.5 Flash (Faster)", "gemini:flash")
        self.model_selector.addItem("Gemini 2.5 Pro (Smarter)", "gemini:pro")
        
        # Add Claude models
        self.model_selector.addItem("Claude 3.5 Sonnet (Balanced)", "claude:sonnet")
        self.model_selector.addItem("Claude 3.5 Haiku (Fastest)", "claude:haiku")
        self.model_selector.addItem("Claude 3 Opus (Most Capable)", "claude:opus")
        
        # Add OpenRouter model
        self.model_selector.addItem("OpenRouter: Claude 3.5 Haiku", "openrouter:anthropic/claude-3.5-haiku")
        
        # Add NVIDIA models
        self.model_selector.addItem("NVIDIA: Llama 3.2 90B Vision", "nvidia:meta/llama-3.2-90b-vision-instruct")
        
        # Add Ollama models
        self.model_selector.addItem("Ollama Local: llama3.2-vision:11b", "ollama:llama3.2-vision:11b")
        self.model_selector.addItem("Ollama Local: llama3.2-vision:90b", "ollama:llama3.2-vision:90b")
        
        self.model_selector.setFont(QFont("Segoe UI", 10))
        self.model_selector.setStyleSheet("""
            QComboBox {
                background-color: rgba(50, 50, 50, 200);
                color: white;
                border: 1px solid rgba(100, 200, 255, 100);
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 2px solid rgba(100, 200, 255, 150);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(40, 40, 40, 240);
                color: white;
                selection-background-color: rgba(100, 200, 255, 150);
                border: 1px solid rgba(100, 200, 255, 100);
            }
        """)
        
        # Set current model based on provider and model
        current_model = get_current_model()
        current_display = get_model_display_name()
        
        # Find matching index in dropdown
        for i in range(self.model_selector.count()):
            item_data = self.model_selector.itemData(i)
            if item_data:
                provider, model = item_data.split(":", 1)
                # Match based on current provider and model
                if provider == "gemini" and current_model in ["gemini-2.5-flash", "flash"]:
                    if model == "flash":
                        self.model_selector.setCurrentIndex(i)
                        break
                elif provider == "gemini" and current_model in ["gemini-2.5-pro", "pro"]:
                    if model == "pro":
                        self.model_selector.setCurrentIndex(i)
                        break
                elif provider == "claude" and current_model.startswith("claude"):
                    if model in current_model:
                        self.model_selector.setCurrentIndex(i)
                        break
                elif provider == "openrouter" and current_model in item_data:
                    self.model_selector.setCurrentIndex(i)
                    break
                elif provider == "nvidia" and current_model in item_data:
                    self.model_selector.setCurrentIndex(i)
                    break
                elif provider == "ollama" and current_model in item_data:
                    self.model_selector.setCurrentIndex(i)
                    break
        
        # Connect model change signal
        self.model_selector.currentIndexChanged.connect(self.on_model_changed)
        
        model_layout.addWidget(self.model_selector)
        model_layout.addStretch()
        inner_layout.addLayout(model_layout)
        
        # Add text input field
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter your task here...")
        self.task_input.setFont(QFont("Segoe UI", 11))
        self.task_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(50, 50, 50, 200);
                color: white;
                border: 1px solid rgba(100, 200, 255, 100);
                border-radius: 5px;
                padding: 10px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(100, 200, 255, 200);
            }
        """)
        self.task_input.returnPressed.connect(self.submit_task)
        inner_layout.addWidget(self.task_input)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Add submit button
        submit_button = QPushButton("Start")
        submit_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 255, 150, 150);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(100, 255, 150, 200);
            }
            QPushButton:pressed {
                background-color: rgba(100, 255, 150, 100);
            }
        """)
        submit_button.clicked.connect(self.submit_task)
        button_layout.addWidget(submit_button)
        
        # Add cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(QFont("Segoe UI", 10))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 100, 100, 150);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 200);
            }
            QPushButton:pressed {
                background-color: rgba(255, 100, 100, 100);
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        inner_layout.addLayout(button_layout)
        
        container.setLayout(inner_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Center on screen
        self.center_on_screen()
    
    def center_on_screen(self):
        """Center the dialog on screen."""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def on_model_changed(self, index):
        """Handle model selection change.
        
        Args:
            index (int): Selected index in combo box
        """
        # Get selected model key (format: "provider:model")
        model_key = self.model_selector.itemData(index)
        
        if not model_key:
            return
        
        # Parse provider and model from the key
        try:
            provider, model = model_key.split(":", 1)
            
            # Display information about the selected model
            print(f"\n{'='*60}")
            print(f"[UI] Model Change Requested")
            print(f"[UI] Provider: {provider}")
            print(f"[UI] Model: {model}")
            print(f"{'='*60}\n")
            
            # Switch to the new provider
            success = switch_provider(provider)
            
            if success:
                # Update the config module's model variables based on provider
                import config
                if provider == "claude":
                    config.CLAUDE_MODEL = model if model.startswith("claude") else f"claude-3-5-{model}-20241022"
                elif provider == "gemini":
                    config.CURRENT_MODEL = model
                elif provider == "openrouter":
                    config.OPENROUTER_MODEL = model
                elif provider == "nvidia":
                    config.NVIDIA_MODEL = model
                elif provider == "ollama":
                    config.OLLAMA_MODEL = model
                
                print(f"[UI] ✓ Successfully switched to {self.model_selector.currentText()}")
                print(f"[UI] Current provider: {get_current_provider()}")
                print(f"[UI] Current model: {get_current_model()}")
            else:
                print(f"[UI] ✗ Failed to switch to {provider}")
            
        except ValueError:
            print(f"[UI] Invalid model key format: {model_key}")
        except Exception as e:
            print(f"[UI] Error switching model: {e}")
    
    def submit_task(self):
        """Submit the task and close dialog."""
        # Get text from input field
        task_text = self.task_input.text().strip()
        
        # Validate text is not empty
        if not task_text:
            return
        
        # Emit task_submitted signal
        self.task_submitted.emit(task_text)
        
        # Clear input field
        self.task_input.clear()
        
        # Close dialog
        self.accept()
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging.
        
        Args:
            event: Mouse event
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


def show_task_input_dialog():
    """Show the task input dialog and return the task.
    
    Returns:
        str: User's task description or None if cancelled
    """
    from PyQt6.QtWidgets import QApplication
    import sys
    
    # Create QApplication if not exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create TaskInputDialog instance
    dialog = TaskInputDialog()
    
    # Store result
    result = [None]
    
    def on_task_submitted(task):
        result[0] = task
    
    dialog.task_submitted.connect(on_task_submitted)
    
    # Show dialog modally
    dialog.exec()
    
    # Return task text or None
    return result[0]


# Made with Bob
