"""Floating task input dialog with voice toggle.

Dev 3 (Pratham) - UI & Demo
Implements task input dialog with:
- Floating dialog window for task input
- Text input field for typing tasks
- Voice input toggle button
- Integration with faster-whisper for voice transcription
- Recording indicator when voice is active
- Real-time transcribed text display
- Submit button to start agent
- Draggable window
- Modern UI design
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                              QLineEdit, QPushButton, QLabel, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QFont
import threading


class VoiceRecorder(QThread):
    """Background thread for voice recording and transcription."""
    
    transcription_ready = pyqtSignal(str)  # Signal when text is ready
    
    def __init__(self):
        """Initialize voice recorder."""
        super().__init__()
        self.recording = False
        self.model = None
        
    def run(self):
        """Run voice recording and transcription."""
        try:
            # Import faster-whisper (optional dependency)
            import pyaudio
            import numpy as np
            
            # Initialize audio recording
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
            
            audio_data = []
            
            # Record audio while recording flag is True
            while self.recording:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_data.append(np.frombuffer(data, dtype=np.int16))
            
            # Stop recording
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Transcribe with whisper (if available)
            if audio_data:
                try:
                    from faster_whisper import WhisperModel
                    
                    if self.model is None:
                        self.model = WhisperModel("base", device="cpu")
                    
                    # Convert audio to format whisper expects
                    audio_array = np.concatenate(audio_data)
                    audio_float = audio_array.astype(np.float32) / 32768.0
                    
                    # Transcribe
                    segments, info = self.model.transcribe(audio_float)
                    text = " ".join([segment.text for segment in segments])
                    
                    # Emit transcription
                    if text.strip():
                        self.transcription_ready.emit(text.strip())
                except ImportError:
                    # Whisper not available, emit placeholder
                    self.transcription_ready.emit("[Voice input - whisper not installed]")
        except Exception as e:
            # Handle any errors gracefully
            self.transcription_ready.emit(f"[Voice error: {str(e)}]")
    
    def start_recording(self):
        """Start voice recording."""
        self.recording = True
        self.start()
    
    def stop_recording(self):
        """Stop voice recording."""
        self.recording = False


class TaskInputDialog(QDialog):
    """Floating dialog for task input."""
    
    task_submitted = pyqtSignal(str)  # Signal when task is submitted
    
    def __init__(self):
        """Initialize the input dialog."""
        super().__init__()
        self.voice_recorder = None
        self.is_recording = False
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
        
        # Add voice toggle button
        self.voice_button = QPushButton("🎤 Voice")
        self.voice_button.setFont(QFont("Segoe UI", 10))
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 200, 255, 150);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgba(100, 200, 255, 200);
            }
            QPushButton:pressed {
                background-color: rgba(100, 200, 255, 100);
            }
        """)
        self.voice_button.clicked.connect(self.toggle_voice_input)
        button_layout.addWidget(self.voice_button)
        
        # Add submit button
        submit_button = QPushButton("▶ Start")
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
        cancel_button = QPushButton("✕ Cancel")
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
        
        # Add recording indicator (hidden by default)
        self.recording_label = QLabel("🔴 Recording...")
        self.recording_label.setFont(QFont("Segoe UI", 10))
        self.recording_label.setStyleSheet("color: rgba(255, 100, 100, 255); background: transparent; border: none;")
        self.recording_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recording_label.hide()
        inner_layout.addWidget(self.recording_label)
        
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
    
    def toggle_voice_input(self):
        """Toggle voice input on/off."""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.voice_button.setText("⏹ Stop")
            self.voice_button.setStyleSheet("""
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
            """)
            self.recording_label.show()
            
            # Start voice recorder
            self.voice_recorder = VoiceRecorder()
            self.voice_recorder.transcription_ready.connect(self.on_transcription_ready)
            self.voice_recorder.start_recording()
        else:
            # Stop recording
            self.is_recording = False
            self.voice_button.setText("🎤 Voice")
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(100, 200, 255, 150);
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: rgba(100, 200, 255, 200);
                }
            """)
            self.recording_label.hide()
            
            # Stop voice recorder
            if self.voice_recorder:
                self.voice_recorder.stop_recording()
    
    def on_transcription_ready(self, text):
        """Handle transcribed text from voice input.
        
        Args:
            text (str): Transcribed text
        """
        # Append text to input field
        current_text = self.task_input.text()
        if current_text:
            self.task_input.setText(current_text + " " + text)
        else:
            self.task_input.setText(text)
    
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


def create_voice_button():
    """Create a styled voice input button.
    
    Returns:
        QPushButton: Configured voice button
    """
    # Create button with microphone icon
    button = QPushButton("🎤")
    button.setFont(QFont("Segoe UI", 12))
    
    # Style with CSS
    button.setStyleSheet("""
        QPushButton {
            background-color: rgba(100, 200, 255, 150);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px;
            min-width: 40px;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: rgba(100, 200, 255, 200);
            transform: scale(1.1);
        }
        QPushButton:pressed {
            background-color: rgba(100, 200, 255, 100);
        }
    """)
    
    return button

# Made with Bob
