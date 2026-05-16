"""Floating task input dialog with voice toggle.

Dev 3 (Pratham) - UI & Demo
Production-level implementation with:
- Floating dialog window for task input
- Text input field for typing tasks
- Voice input toggle button
- Integration with faster-whisper for voice transcription
- Recording indicator when voice is active
- Real-time transcribed text display
- Submit button to start agent
- Draggable window
- Modern UI design
- Comprehensive error handling and logging
- Input validation and history
- Keyboard shortcuts
- Auto-complete suggestions
"""

from typing import Optional, List
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                              QLineEdit, QPushButton, QLabel, QCompleter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QStringListModel
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
import threading
import time

from .logger import get_logger, log_error_with_context
from .exceptions import InputDialogException, ErrorCode, handle_exception
from .config_ui import get_config


# Initialize logger
logger = get_logger("input_dialog")


class VoiceRecorder(QThread):
    """Background thread for voice recording and transcription with production features."""
    
    transcription_ready = pyqtSignal(str)  # Signal when text is ready
    error_occurred = pyqtSignal(str)  # Signal when error occurs
    
    def __init__(self):
        """Initialize voice recorder with error handling."""
        try:
            super().__init__()
            self.recording = False
            self.model = None
            logger.info("VoiceRecorder initialized")
        except Exception as e:
            logger.error(f"Failed to initialize VoiceRecorder: {e}")
            raise InputDialogException(
                "Failed to initialize voice recorder",
                ErrorCode.VOICE_RECORDING_ERROR,
                {"error": str(e)}
            )
    
    def run(self):
        """Run voice recording and transcription with comprehensive error handling."""
        audio_data = []
        stream = None
        p = None
        
        try:
            logger.info("Starting voice recording")
            
            # Import dependencies
            try:
                import pyaudio
                import numpy as np
            except ImportError as e:
                error_msg = "PyAudio not installed. Please install: pip install pyaudio"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            # Initialize audio recording
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            try:
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                )
                logger.debug("Audio stream opened successfully")
            except Exception as e:
                error_msg = f"Failed to open audio stream: {str(e)}"
                logger.error(error_msg)
                self.error_occurred.emit("Microphone access denied or not available")
                return
            
            # Record audio while recording flag is True
            start_time = time.time()
            while self.recording:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    audio_data.append(np.frombuffer(data, dtype=np.int16))
                    
                    # Prevent excessive recording (max 60 seconds)
                    if time.time() - start_time > 60:
                        logger.warning("Recording exceeded 60 seconds, stopping")
                        break
                        
                except Exception as e:
                    logger.error(f"Error reading audio data: {e}")
                    break
            
            logger.info(f"Recording stopped, captured {len(audio_data)} chunks")
            
            # Transcribe with whisper (if available)
            if audio_data:
                self._transcribe_audio(audio_data)
            else:
                logger.warning("No audio data captured")
                self.error_occurred.emit("No audio captured")
                
        except Exception as e:
            error_msg = f"Voice recording error: {str(e)}"
            logger.error(error_msg)
            log_error_with_context("voice_recorder", e, {"audio_chunks": len(audio_data)})
            self.error_occurred.emit("Recording failed")
            
        finally:
            # Cleanup resources
            try:
                if stream:
                    stream.stop_stream()
                    stream.close()
                if p:
                    p.terminate()
                logger.debug("Audio resources cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up audio resources: {e}")
    
    def _transcribe_audio(self, audio_data: List):
        """Transcribe audio data using Whisper.
        
        Args:
            audio_data: List of audio chunks
        """
        try:
            logger.info("Starting transcription")
            
            # Import whisper
            try:
                from faster_whisper import WhisperModel
                import numpy as np
            except ImportError:
                logger.warning("faster-whisper not installed")
                self.transcription_ready.emit("[Voice input - whisper not installed]")
                return
            
            # Load model if not already loaded
            if self.model is None:
                config = get_config().input_dialog
                logger.info(f"Loading Whisper model: {config.whisper_model}")
                self.model = WhisperModel(
                    config.whisper_model,
                    device=config.whisper_device
                )
            
            # Convert audio to format whisper expects
            audio_array = np.concatenate(audio_data)
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            logger.debug(f"Transcribing audio array of length {len(audio_float)}")
            
            # Transcribe
            segments, info = self.model.transcribe(audio_float, language="en")
            text = " ".join([segment.text for segment in segments])
            
            # Emit transcription
            if text.strip():
                logger.info(f"Transcription complete: {text[:50]}...")
                self.transcription_ready.emit(text.strip())
            else:
                logger.warning("Transcription resulted in empty text")
                self.error_occurred.emit("No speech detected")
                
        except Exception as e:
            error_msg = f"Transcription error: {str(e)}"
            logger.error(error_msg)
            log_error_with_context("voice_recorder", e, {"audio_length": len(audio_data)})
            self.error_occurred.emit("Transcription failed")
    
    def start_recording(self):
        """Start voice recording."""
        try:
            logger.info("Starting recording")
            self.recording = True
            self.start()
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise InputDialogException(
                "Failed to start recording",
                ErrorCode.VOICE_RECORDING_ERROR,
                {"error": str(e)}
            )
    
    def stop_recording(self):
        """Stop voice recording."""
        try:
            logger.info("Stopping recording")
            self.recording = False
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")


class TaskInputDialog(QDialog):
    """Floating dialog for task input with production features."""
    
    task_submitted = pyqtSignal(str)  # Signal when task is submitted
    
    def __init__(self):
        """Initialize the input dialog with error handling."""
        try:
            logger.info("Initializing TaskInputDialog")
            super().__init__()
            
            # Load configuration
            self.config = get_config().input_dialog
            
            # State
            self.voice_recorder: Optional[VoiceRecorder] = None
            self.is_recording = False
            self.drag_position = QPoint()
            
            # Input history
            self.input_history: List[str] = []
            self.history_index = -1
            
            # Initialize UI
            self.init_ui()
            
            logger.info("TaskInputDialog initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TaskInputDialog: {e}")
            raise InputDialogException(
                "Failed to initialize input dialog",
                ErrorCode.INPUT_DIALOG_ERROR,
                {"error": str(e)}
            )
    
    def init_ui(self):
        """Set up the dialog UI with error handling."""
        try:
            logger.debug("Setting up input dialog UI")
            
            # Set window properties
            self.setWindowTitle("AXON - Task Input")
            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint | 
                Qt.WindowType.FramelessWindowHint
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            
            # Set size from config
            self.setFixedSize(self.config.width, self.config.height)
            
            # Create main layout
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create container widget with styling
            container = QLabel()
            container.setStyleSheet(f"""
                QLabel {{
                    background-color: rgba(30, 30, 30, {self.config.opacity});
                    border-radius: {self.config.border_radius}px;
                    border: 2px solid rgba(100, 200, 255, 180);
                }}
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
            self.task_input.setFont(QFont("Segoe UI", self.config.font_size))
            self.task_input.setMaxLength(self.config.max_input_length)
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
            
            # Set up auto-complete if history is enabled
            if self.config.enable_history:
                self._setup_autocomplete()
            
            # Create button layout
            button_layout = QHBoxLayout()
            
            # Add voice toggle button (if enabled)
            if self.config.voice_enabled:
                self.voice_button = self._create_voice_button()
                button_layout.addWidget(self.voice_button)
            
            # Add submit button
            submit_button = self._create_submit_button()
            button_layout.addWidget(submit_button)
            
            # Add cancel button
            cancel_button = self._create_cancel_button()
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
            
            # Set up keyboard shortcuts
            self._setup_shortcuts()
            
            # Center on screen
            self.center_on_screen()
            
            logger.debug("Input dialog UI setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup input dialog UI: {e}")
            raise InputDialogException(
                "Failed to setup input dialog UI",
                ErrorCode.INPUT_DIALOG_ERROR,
                {"error": str(e)}
            )
    
    def _setup_autocomplete(self):
        """Set up auto-complete for input field."""
        try:
            self.completer = QCompleter()
            self.completer_model = QStringListModel()
            self.completer.setModel(self.completer_model)
            self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.task_input.setCompleter(self.completer)
            logger.debug("Auto-complete setup complete")
        except Exception as e:
            logger.warning(f"Failed to setup auto-complete: {e}")
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        try:
            # Escape to cancel
            escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
            escape_shortcut.activated.connect(self.reject)
            
            # Ctrl+Enter to submit
            submit_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
            submit_shortcut.activated.connect(self.submit_task)
            
            logger.debug("Keyboard shortcuts setup complete")
        except Exception as e:
            logger.warning(f"Failed to setup shortcuts: {e}")
    
    def _create_voice_button(self) -> QPushButton:
        """Create voice toggle button.
        
        Returns:
            Configured voice button
        """
        button = QPushButton("🎤 Voice")
        button.setFont(QFont("Segoe UI", 10))
        button.setStyleSheet("""
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
        button.clicked.connect(self.toggle_voice_input)
        return button
    
    def _create_submit_button(self) -> QPushButton:
        """Create submit button.
        
        Returns:
            Configured submit button
        """
        button = QPushButton("▶ Start")
        button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        button.setStyleSheet("""
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
        button.clicked.connect(self.submit_task)
        return button
    
    def _create_cancel_button(self) -> QPushButton:
        """Create cancel button.
        
        Returns:
            Configured cancel button
        """
        button = QPushButton("✕ Cancel")
        button.setFont(QFont("Segoe UI", 10))
        button.setStyleSheet("""
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
        button.clicked.connect(self.reject)
        return button
    
    def center_on_screen(self):
        """Center the dialog on screen."""
        try:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
            logger.debug(f"Dialog centered at ({x}, {y})")
        except Exception as e:
            logger.warning(f"Failed to center dialog: {e}")
    
    def toggle_voice_input(self):
        """Toggle voice input on/off with error handling."""
        try:
            if not self.is_recording:
                self._start_voice_recording()
            else:
                self._stop_voice_recording()
        except Exception as e:
            logger.error(f"Error toggling voice input: {e}")
            handle_exception(
                InputDialogException(
                    "Failed to toggle voice input",
                    ErrorCode.VOICE_RECORDING_ERROR,
                    {"error": str(e)}
                ),
                logger,
                "input_dialog"
            )
    
    def _start_voice_recording(self):
        """Start voice recording."""
        try:
            logger.info("Starting voice recording")
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
            self.voice_recorder.error_occurred.connect(self.on_voice_error)
            self.voice_recorder.start_recording()
            
        except Exception as e:
            logger.error(f"Failed to start voice recording: {e}")
            self.is_recording = False
            self.recording_label.hide()
            raise
    
    def _stop_voice_recording(self):
        """Stop voice recording."""
        try:
            logger.info("Stopping voice recording")
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
                
        except Exception as e:
            logger.error(f"Error stopping voice recording: {e}")
    
    def on_transcription_ready(self, text: str):
        """Handle transcribed text from voice input.
        
        Args:
            text: Transcribed text
        """
        try:
            logger.info(f"Transcription received: {text[:50]}...")
            
            # Append text to input field
            current_text = self.task_input.text()
            if current_text:
                self.task_input.setText(current_text + " " + text)
            else:
                self.task_input.setText(text)
                
        except Exception as e:
            logger.error(f"Error handling transcription: {e}")
    
    def on_voice_error(self, error_msg: str):
        """Handle voice recording error.
        
        Args:
            error_msg: Error message
        """
        try:
            logger.warning(f"Voice error: {error_msg}")
            self.recording_label.setText(f"⚠ {error_msg}")
            self.recording_label.setStyleSheet("color: rgba(255, 200, 100, 255); background: transparent; border: none;")
            
            # Reset after 3 seconds
            threading.Timer(3.0, lambda: self.recording_label.hide()).start()
            
        except Exception as e:
            logger.error(f"Error handling voice error: {e}")
    
    def submit_task(self):
        """Submit the task and close dialog with validation."""
        try:
            # Get text from input field
            task_text = self.task_input.text().strip()
            
            # Validate text is not empty
            if not task_text:
                logger.warning("Empty task submitted")
                self.task_input.setStyleSheet("""
                    QLineEdit {
                        background-color: rgba(50, 50, 50, 200);
                        color: white;
                        border: 2px solid rgba(255, 100, 100, 200);
                        border-radius: 5px;
                        padding: 10px;
                    }
                """)
                return
            
            # Validate length
            if len(task_text) > self.config.max_input_length:
                logger.warning(f"Task too long: {len(task_text)} chars")
                return
            
            logger.info(f"Task submitted: {task_text[:50]}...")
            
            # Add to history
            if self.config.enable_history:
                self._add_to_history(task_text)
            
            # Emit task_submitted signal
            self.task_submitted.emit(task_text)
            
            # Clear input field
            self.task_input.clear()
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            handle_exception(
                InputDialogException(
                    "Failed to submit task",
                    ErrorCode.INPUT_VALIDATION_ERROR,
                    {"error": str(e)}
                ),
                logger,
                "input_dialog"
            )
    
    def _add_to_history(self, task: str):
        """Add task to history.
        
        Args:
            task: Task text
        """
        try:
            if task not in self.input_history:
                self.input_history.append(task)
                
                # Limit history size
                if len(self.input_history) > self.config.history_size:
                    self.input_history.pop(0)
                
                # Update completer
                if hasattr(self, 'completer_model'):
                    self.completer_model.setStringList(self.input_history)
                
                logger.debug(f"Added to history: {task[:30]}...")
        except Exception as e:
            logger.warning(f"Failed to add to history: {e}")
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging.
        
        Args:
            event: Mouse event
        """
        try:
            if event.button() == Qt.MouseButton.LeftButton and self.config.draggable:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        except Exception as e:
            logger.debug(f"Error in mouse press: {e}")
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging.
        
        Args:
            event: Mouse event
        """
        try:
            if event.buttons() == Qt.MouseButton.LeftButton and self.config.draggable:
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
        except Exception as e:
            logger.debug(f"Error in mouse move: {e}")
    
    def __del__(self):
        """Cleanup resources."""
        try:
            logger.info("TaskInputDialog destroyed")
            if self.voice_recorder and self.is_recording:
                self.voice_recorder.stop_recording()
        except:
            pass


def show_task_input_dialog() -> Optional[str]:
    """Show the task input dialog and return the task.
    
    Returns:
        User's task description or None if cancelled
    """
    try:
        logger.info("Showing task input dialog")
        
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
        
        logger.info(f"Dialog closed, result: {result[0][:30] if result[0] else 'None'}...")
        
        # Return task text or None
        return result[0]
        
    except Exception as e:
        logger.error(f"Error showing task input dialog: {e}")
        raise InputDialogException(
            "Failed to show input dialog",
            ErrorCode.INPUT_DIALOG_ERROR,
            {"error": str(e)}
        )


def create_voice_button() -> QPushButton:
    """Create a styled voice input button.
    
    Returns:
        Configured voice button
    """
    try:
        button = QPushButton("🎤")
        button.setFont(QFont("Segoe UI", 12))
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
    except Exception as e:
        logger.error(f"Error creating voice button: {e}")
        raise InputDialogException(
            "Failed to create voice button",
            ErrorCode.INPUT_DIALOG_ERROR,
            {"error": str(e)}
        )


# Made with Bob
