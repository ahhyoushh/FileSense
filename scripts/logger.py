import sys
from datetime import datetime
from pathlib import Path
import threading

class Logger:
    def __init__(self):
        self.terminal = sys.stdout
        self.log_buffer = []
        self.lock = threading.Lock()
        self.enabled = True
        
        # Create logs directory if it doesn't exist
        self.base_dir = Path(__file__).resolve().parent.parent
        self.logs_dir = self.base_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
    def write(self, message):
        """Write message to both terminal and buffer"""
        if self.enabled:
            self.terminal.write(message)
            with self.lock:
                self.log_buffer.append(message)
    
    def flush(self):
        """Flush the terminal output"""
        self.terminal.flush()
    
    def get_logs(self):
        """Get all logged messages as a single string"""
        with self.lock:
            return ''.join(self.log_buffer)
    
    def clear_buffer(self):
        """Clear the log buffer"""
        with self.lock:
            self.log_buffer.clear()
    
    def save_logs(self, filename=None):
        """
        Save the current log buffer to a file.
        
        Args:
            filename: Optional custom filename. If not provided, uses timestamp.
        
        Returns:
            Path to the saved log file, or None if save failed
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"run_{timestamp}.log"
        
        log_path = self.logs_dir / filename
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(self.get_logs())
            return log_path
        except Exception as e:
            self.terminal.write(f"\n[!] Error saving log file: {e}\n")
            return None
    
    def disable(self):
        """Temporarily disable logging to buffer (still prints to terminal)"""
        self.enabled = False
    
    def enable(self):
        """Re-enable logging to buffer"""
        self.enabled = True


# Global logger instance
_logger_instance = None

def setup_logger():
    """Initialize and install the global logger"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
        sys.stdout = _logger_instance
    return _logger_instance

def get_logger():
    """Get the global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        return setup_logger()
    return _logger_instance

def restore_stdout():
    """Restore original stdout"""
    global _logger_instance
    if _logger_instance is not None:
        sys.stdout = _logger_instance.terminal
