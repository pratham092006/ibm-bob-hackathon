"""Custom exceptions for AXON UI components.

Dev 3 (Pratham) - UI & Demo
Provides custom exception classes with:
- Specific error types for different failure modes
- Error codes for programmatic handling
- Recovery strategies
- User-friendly error messages
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """Error codes for UI components."""
    
    # General errors (1000-1099)
    UNKNOWN_ERROR = 1000
    INITIALIZATION_ERROR = 1001
    CONFIGURATION_ERROR = 1002
    
    # Reticle errors (1100-1199)
    RETICLE_RENDER_ERROR = 1100
    RETICLE_ANIMATION_ERROR = 1101
    RETICLE_STATE_ERROR = 1102
    
    # Overlay errors (1200-1299)
    OVERLAY_CREATION_ERROR = 1200
    OVERLAY_RENDER_ERROR = 1201
    OVERLAY_UPDATE_ERROR = 1202
    OVERLAY_MULTIMONITOR_ERROR = 1203
    
    # Input dialog errors (1300-1399)
    INPUT_DIALOG_ERROR = 1300
    VOICE_RECORDING_ERROR = 1301
    VOICE_TRANSCRIPTION_ERROR = 1302
    INPUT_VALIDATION_ERROR = 1303
    
    # Tray icon errors (1400-1499)
    TRAY_CREATION_ERROR = 1400
    TRAY_MENU_ERROR = 1401
    TRAY_NOTIFICATION_ERROR = 1402
    TRAY_ICON_ERROR = 1403
    
    # Resource errors (1500-1599)
    RESOURCE_ALLOCATION_ERROR = 1500
    RESOURCE_CLEANUP_ERROR = 1501
    MEMORY_ERROR = 1502
    
    # Performance errors (1600-1699)
    PERFORMANCE_DEGRADATION = 1600
    FRAME_DROP_ERROR = 1601
    TIMEOUT_ERROR = 1602


class UIException(Exception):
    """Base exception for all UI-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ):
        """Initialize UI exception.
        
        Args:
            message: Human-readable error message
            error_code: Specific error code
            context: Additional context about the error
            recoverable: Whether the error is recoverable
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.recoverable = recoverable
    
    def __str__(self) -> str:
        """String representation of the exception."""
        return f"[{self.error_code.name}] {self.message}"
    
    def get_user_message(self) -> str:
        """Get user-friendly error message.
        
        Returns:
            User-friendly error message
        """
        return self.message
    
    def get_recovery_suggestion(self) -> str:
        """Get recovery suggestion for the error.
        
        Returns:
            Recovery suggestion
        """
        if not self.recoverable:
            return "This error is not recoverable. Please restart the application."
        return "Please try again. If the problem persists, check the logs."


class ReticleException(UIException):
    """Exception for reticle-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.RETICLE_RENDER_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, recoverable=True)
    
    def get_recovery_suggestion(self) -> str:
        """Get recovery suggestion."""
        if self.error_code == ErrorCode.RETICLE_RENDER_ERROR:
            return "The reticle will attempt to recover. Visual effects may be temporarily disabled."
        elif self.error_code == ErrorCode.RETICLE_ANIMATION_ERROR:
            return "Animation will be disabled temporarily. Functionality is not affected."
        return super().get_recovery_suggestion()


class OverlayException(UIException):
    """Exception for overlay-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.OVERLAY_RENDER_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, recoverable=True)
    
    def get_recovery_suggestion(self) -> str:
        """Get recovery suggestion."""
        if self.error_code == ErrorCode.OVERLAY_CREATION_ERROR:
            return "Failed to create overlay. Check if another instance is running."
        elif self.error_code == ErrorCode.OVERLAY_MULTIMONITOR_ERROR:
            return "Multi-monitor setup detected. Overlay will use primary monitor."
        return super().get_recovery_suggestion()


class InputDialogException(UIException):
    """Exception for input dialog errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INPUT_DIALOG_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, recoverable=True)
    
    def get_recovery_suggestion(self) -> str:
        """Get recovery suggestion."""
        if self.error_code == ErrorCode.VOICE_RECORDING_ERROR:
            return "Voice recording failed. Please check microphone permissions and try again."
        elif self.error_code == ErrorCode.VOICE_TRANSCRIPTION_ERROR:
            return "Voice transcription failed. You can still type your task manually."
        elif self.error_code == ErrorCode.INPUT_VALIDATION_ERROR:
            return "Please enter a valid task description."
        return super().get_recovery_suggestion()


class TrayIconException(UIException):
    """Exception for tray icon errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.TRAY_CREATION_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, recoverable=True)
    
    def get_recovery_suggestion(self) -> str:
        """Get recovery suggestion."""
        if self.error_code == ErrorCode.TRAY_CREATION_ERROR:
            return "Failed to create system tray icon. The application will continue without it."
        elif self.error_code == ErrorCode.TRAY_NOTIFICATION_ERROR:
            return "Notifications are not supported on this system."
        return super().get_recovery_suggestion()


class ResourceException(UIException):
    """Exception for resource-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.RESOURCE_ALLOCATION_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, recoverable=False)
    
    def get_recovery_suggestion(self) -> str:
        """Get recovery suggestion."""
        if self.error_code == ErrorCode.MEMORY_ERROR:
            return "Out of memory. Please close other applications and restart AXON."
        return "Critical resource error. Please restart the application."


class PerformanceException(UIException):
    """Exception for performance-related issues."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.PERFORMANCE_DEGRADATION,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, recoverable=True)
    
    def get_recovery_suggestion(self) -> str:
        """Get recovery suggestion."""
        if self.error_code == ErrorCode.PERFORMANCE_DEGRADATION:
            return "Performance mode activated. Some visual effects may be reduced."
        elif self.error_code == ErrorCode.FRAME_DROP_ERROR:
            return "Frame drops detected. Reducing animation complexity."
        elif self.error_code == ErrorCode.TIMEOUT_ERROR:
            return "Operation timed out. Please try again."
        return super().get_recovery_suggestion()


def handle_exception(exception: Exception, logger, component: str) -> bool:
    """Handle an exception with appropriate logging and recovery.
    
    Args:
        exception: The exception to handle
        logger: Logger instance
        component: Component name where error occurred
        
    Returns:
        True if error was handled and recovery is possible, False otherwise
    """
    if isinstance(exception, UIException):
        # Log with appropriate level
        if exception.recoverable:
            logger.warning(f"{component}: {exception}")
            logger.info(f"Recovery: {exception.get_recovery_suggestion()}")
        else:
            logger.error(f"{component}: {exception}")
            logger.error(f"Recovery: {exception.get_recovery_suggestion()}")
        
        # Log context if available
        if exception.context:
            logger.debug(f"Error context: {exception.context}")
        
        return exception.recoverable
    else:
        # Unknown exception
        logger.exception(f"{component}: Unexpected error: {str(exception)}")
        return False


# Made with Bob