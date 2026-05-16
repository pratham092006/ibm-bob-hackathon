"""Production-level logging configuration for AXON UI components.

Dev 3 (Pratham) - UI & Demo
Provides centralized logging with:
- File rotation for log management
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Formatted output with timestamps
- Separate loggers for different components
- Debug mode support
- Performance logging
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class UILogger:
    """Centralized logger for UI components."""
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    _instance: Optional['UILogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger (only once)."""
        if not UILogger._initialized:
            self._setup_logging()
            UILogger._initialized = True
    
    def _setup_logging(self):
        """Set up logging configuration."""
        # Create logs directory
        log_dir = Path("axon/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file path with timestamp
        log_file = log_dir / f"ui_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure root logger
        self.logger = logging.getLogger("AXON.UI")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create rotating file handler (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Set formatters
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log initialization
        self.logger.info("=" * 80)
        self.logger.info("AXON UI Logger initialized")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("=" * 80)
    
    def get_logger(self, component: str) -> logging.Logger:
        """Get a logger for a specific component.
        
        Args:
            component: Component name (e.g., 'reticle', 'overlay')
            
        Returns:
            Logger instance for the component
        """
        return logging.getLogger(f"AXON.UI.{component}")
    
    def set_level(self, level: int):
        """Set the logging level.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(level)
    
    def enable_debug_mode(self):
        """Enable debug mode with verbose logging."""
        self.set_level(logging.DEBUG)
        self.logger.info("Debug mode enabled")
    
    def disable_debug_mode(self):
        """Disable debug mode, return to INFO level."""
        self.set_level(logging.INFO)
        self.logger.info("Debug mode disabled")


# Global logger instance
_ui_logger = UILogger()


def get_logger(component: str = "general") -> logging.Logger:
    """Get a logger for a component.
    
    Args:
        component: Component name
        
    Returns:
        Logger instance
    """
    return _ui_logger.get_logger(component)


def enable_debug_mode():
    """Enable debug mode."""
    _ui_logger.enable_debug_mode()


def disable_debug_mode():
    """Disable debug mode."""
    _ui_logger.disable_debug_mode()


def log_performance(component: str, operation: str, duration: float):
    """Log performance metrics.
    
    Args:
        component: Component name
        operation: Operation description
        duration: Duration in seconds
    """
    logger = get_logger(component)
    if duration > 0.1:  # Log if operation takes more than 100ms
        logger.warning(f"Performance: {operation} took {duration:.3f}s")
    else:
        logger.debug(f"Performance: {operation} took {duration:.3f}s")


def log_error_with_context(component: str, error: Exception, context: dict):
    """Log error with additional context.
    
    Args:
        component: Component name
        error: Exception that occurred
        context: Additional context dictionary
    """
    logger = get_logger(component)
    logger.error(f"Error: {str(error)}")
    logger.error(f"Context: {context}")
    logger.exception("Full traceback:")


# Made with Bob