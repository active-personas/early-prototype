import logging
import sys
import os
from pathlib import Path
from typing import Optional

class Logger:
    """
    Static logger class for consistent logging across all components.
    
    Provides direct logging methods that write to file with automatic
    logger management and consistent formatting. Log file path and minimum
    log level are configured via environment variables.
    
    Usage:
        Logger.info("Application started")
        Logger.error("Failed to process request") 
        Logger.debug("Processing user input")
    
    Environment Variables:
        LOG_FILE: Path to log file (default: ./logs/app.log)
        LOG_LEVEL: Minimum log level (default: INFO)
    
    Format: YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message
    """
    
    _loggers = {}
    _formatter = None
    _log_level = None
    
    @staticmethod
    def _get_log_level():
        """Get the minimum log level from environment variable."""
        if Logger._log_level is None:
            Logger._log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        return Logger._log_level
    
    @staticmethod
    def get_logger(name: str = __name__, level: str = None) -> logging.Logger:
        """
        Get or create a logger instance for the specified name.
        
        Args:
            name: Logger identifier (typically __name__)
            level: Logging level override (uses LOG_LEVEL env var if None)
        
        Returns:
            Configured logger instance with file handler
        """
        # Return existing logger if already created
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        # Use environment log level if not specified
        if level is None:
            level = Logger._get_log_level()
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Avoid adding multiple handlers if logger already configured
        if not logger.handlers:
            # Get log file path from environment variable
            log_file = os.getenv("LOG_FILE", "./logs/app.log")
            
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file handler with environment log level
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, level.upper()))
            
            # Create formatter if not exists
            if Logger._formatter is None:
                Logger._formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            file_handler.setFormatter(Logger._formatter)
            
            # Add handler to logger
            logger.addHandler(file_handler)
        
        # Cache the logger
        Logger._loggers[name] = logger
        return logger
    
    @staticmethod
    def info(message: str, name: str = __name__):
        """Log an informational message for general status and progress updates."""
        Logger.get_logger(name).info(message)
    
    @staticmethod
    def debug(message: str, name: str = __name__):
        """Log a debug message for detailed troubleshooting information."""
        Logger.get_logger(name).debug(message)
    
    @staticmethod
    def error(message: str, name: str = __name__):
        """Log an error message for failures and exceptions."""
        Logger.get_logger(name).error(message)
