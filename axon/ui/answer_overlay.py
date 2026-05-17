"""Transparent answer overlay for displaying context help responses.

Shows AI-generated help text in a semi-transparent overlay window
that can be dismissed by clicking or pressing Esc.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
import sys


class AnswerOverlay(QWidget):
    """Transparent overlay for displaying AI context help answers."""
    
    closed = pyqtSignal()  # Signal when overlay is closed
    
    def __init__(self):
        """Initialize the answer overlay."""
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Set up the overlay UI."""
        # Set window properties (frameless, always on top, transparent background)
        self.setWindowTitle("AXON - Context Help")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool  # Don't show in taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set size (responsive to screen size)
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        width = min(800, int(screen.width() * 0.6))
        height = min(600, int(screen.height() * 0.7))
        self.setFixedSize(width, height)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create container widget with styling
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(20, 20, 20, 230);
                border-radius: 15px;
                border: 3px solid rgba(100, 200, 255, 200);
            }
        """)
        
        # Create inner layout
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(25, 25, 25, 25)
        inner_layout.setSpacing(15)
        
        # Add header with title and close hint
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        title_label = QLabel("🤖 AI Context Help")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            color: rgba(100, 200, 255, 255);
            background: transparent;
            border: none;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        close_hint = QLabel("Click anywhere or press Esc to close")
        close_hint.setFont(QFont("Segoe UI", 9))
        close_hint.setStyleSheet("""
            color: rgba(150, 150, 150, 200);
            background: transparent;
            border: none;
        """)
        close_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(close_hint)
        
        inner_layout.addLayout(header_layout)
        
        # Add separator line
        separator = QLabel()
        separator.setFixedHeight(2)
        separator.setStyleSheet("""
            background-color: rgba(100, 200, 255, 100);
            border: none;
        """)
        inner_layout.addWidget(separator)
        
        # Create scroll area for answer text
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(40, 40, 40, 150);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 200, 255, 150);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(100, 200, 255, 200);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create answer text label
        self.answer_label = QLabel()
        self.answer_label.setFont(QFont("Segoe UI", 11))
        self.answer_label.setStyleSheet("""
            QLabel {
                color: rgba(240, 240, 240, 255);
                background: transparent;
                border: none;
                padding: 10px;
            }
        """)
        self.answer_label.setWordWrap(True)
        self.answer_label.setTextFormat(Qt.TextFormat.RichText)
        self.answer_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.answer_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        scroll_area.setWidget(self.answer_label)
        inner_layout.addWidget(scroll_area)
        
        # Add loading indicator (hidden by default)
        self.loading_label = QLabel("⏳ Thinking...")
        self.loading_label.setFont(QFont("Segoe UI", 12))
        self.loading_label.setStyleSheet("""
            color: rgba(100, 200, 255, 255);
            background: transparent;
            border: none;
        """)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()
        inner_layout.addWidget(self.loading_label)
        
        container.setLayout(inner_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Center on screen
        self.center_on_screen()
        
    def center_on_screen(self):
        """Center the overlay on screen."""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def show_loading(self):
        """Show loading indicator."""
        self.answer_label.hide()
        self.loading_label.show()
        self.show()
        self.raise_()
        self.activateWindow()
    
    def set_answer(self, answer_text: str):
        """Set the answer text to display.
        
        Args:
            answer_text: The AI-generated answer text
        """
        # Convert markdown-style formatting to HTML
        formatted_text = self._format_text(answer_text)
        
        self.loading_label.hide()
        self.answer_label.setText(formatted_text)
        self.answer_label.show()
        
        # Ensure window is visible and on top
        self.show()
        self.raise_()
        self.activateWindow()
    
    def _format_text(self, text: str) -> str:
        """Format text with basic HTML styling.
        
        Args:
            text: Plain text or markdown-style text
            
        Returns:
            HTML-formatted text
        """
        # Replace newlines with <br>
        text = text.replace('\n', '<br>')
        
        # Bold text: **text** or __text__
        import re
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        
        # Italic text: *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        
        # Code blocks: `code`
        text = re.sub(r'`(.+?)`', r'<code style="background-color: rgba(60, 60, 60, 150); padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace;">\1</code>', text)
        
        # Bullet points: - item or * item
        text = re.sub(r'<br>[-*] (.+?)(?=<br>|$)', r'<br>• \1', text)
        
        return text
    
    def mousePressEvent(self, event):
        """Handle mouse press to close overlay.
        
        Args:
            event: Mouse event
        """
        self.close_overlay()
    
    def keyPressEvent(self, event):
        """Handle key press events.
        
        Args:
            event: Key event
        """
        # Close on Esc key
        if event.key() == Qt.Key.Key_Escape:
            self.close_overlay()
        else:
            super().keyPressEvent(event)
    
    def close_overlay(self):
        """Close the overlay and emit signal."""
        self.hide()
        self.closed.emit()
    
    def show_with_fade(self):
        """Show overlay with fade-in effect."""
        self.setWindowOpacity(0.0)
        self.show()
        
        # Animate opacity
        self.fade_timer = QTimer()
        self.current_opacity = 0.0
        
        def fade_step():
            self.current_opacity += 0.1
            if self.current_opacity >= 1.0:
                self.current_opacity = 1.0
                self.fade_timer.stop()
            self.setWindowOpacity(self.current_opacity)
        
        self.fade_timer.timeout.connect(fade_step)
        self.fade_timer.start(30)  # 30ms intervals


def show_answer_overlay(answer_text: str):
    """Show the answer overlay with given text.
    
    Args:
        answer_text: The AI-generated answer text
        
    Returns:
        AnswerOverlay: The overlay instance
    """
    from PyQt6.QtWidgets import QApplication
    
    # Create QApplication if not exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create and show overlay
    overlay = AnswerOverlay()
    overlay.set_answer(answer_text)
    
    return overlay


# Made with Bob