"""
Optimization status widget for displaying solver progress and status.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QCoreApplication
import logging

class OptimizationStatus(QWidget):
    """
    Widget for displaying the status of an optimization run.
    Shows progress bar, status messages, and provides cancel button.
    """
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Status message
        self.status_label = QLabel("Ready to optimize")
        self.status_label.setObjectName("statusLabel")
        self.layout.addWidget(self.status_label)
        
        # Progress bar and cancel button
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar, 4)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancelled)
        self.cancel_button.setEnabled(False)
        progress_layout.addWidget(self.cancel_button, 1)
        
        self.layout.addLayout(progress_layout)
        
        # Additional info labels for time, gap, etc.
        info_layout = QHBoxLayout()
        
        self.time_label = QLabel("Time: 0s")
        self.gap_label = QLabel("Gap: -")
        self.iterations_label = QLabel("Iterations: 0")
        
        info_layout.addWidget(self.time_label)
        info_layout.addWidget(self.gap_label)
        info_layout.addWidget(self.iterations_label)
        info_layout.addStretch()
        
        self.layout.addLayout(info_layout)
        
        # Timer for updating elapsed time
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1 second
        self.timer.timeout.connect(self._update_time)
        self.elapsed_seconds = 0
        
        # Status styling
        self.setStyleSheet("""
            #statusLabel {
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        # Initially hide additional info
        self.time_label.setVisible(False)
        self.gap_label.setVisible(False)
        self.iterations_label.setVisible(False)
    
    def start_optimization(self, time_limit=60):
        """
        Start the optimization display.
        
        Args:
            time_limit: Time limit in seconds for the progress bar
        """
        self.status_label.setText("Optimization in progress...")
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(True)
        
        # Make info labels visible
        self.time_label.setVisible(True)
        self.gap_label.setVisible(True)
        self.iterations_label.setVisible(True)
        
        # Reset and start timer
        self.elapsed_seconds = 0
        self.time_label.setText("Time: 0s")
        self.timer.start()
    
    def update_progress(self, value, status_text=None, gap=None, iterations=None):
        """
        Update the progress display.
        
        Args:
            value: Progress value (0-100)
            status_text: Optional status text to display
            gap: Optional optimality gap to display
            iterations: Optional iteration count to display
        """
        # Ensure progress value is within bounds
        value = max(0, min(100, value))
        
        self.progress_bar.setValue(value)
        
        if status_text:
            self.status_label.setText(status_text)
        
        if gap is not None:
            self.gap_label.setText(f"Gap: {gap:.2%}")
        
        if iterations is not None:
            self.iterations_label.setText(f"Iterations: {iterations}")
    
    def finish_optimization(self, success=True, message=None):
        """
        End the optimization display.
        
        Args:
            success: Whether the optimization succeeded
            message: Optional message to display
        """
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Finishing optimization - success: {success}, message: {message}")
        
        # Stop timer first
        self.timer.stop()
        self.cancel_button.setEnabled(False)
        
        # Ensure consistent state
        if success:
            logger.debug("Setting progress to 100% for successful optimization")
            # For successful optimizations, always ensure progress is 100%
            # This ensures consistency between progress bar and status message
            current_value = self.progress_bar.value()
            if current_value < 100:
                logger.debug(f"Updating progress from {current_value} to 100")
                self.progress_bar.setValue(100)
            
            # Update status message
            self.status_label.setText(message or "Optimization complete")
        else:
            # For failed optimizations, keep progress as is
            logger.debug(f"Keeping progress at {self.progress_bar.value()} for unsuccessful optimization")
            # Update status message for consistency
            self.status_label.setText(message or "Optimization failed")
        
        # Process events immediately to ensure UI update
        QCoreApplication.processEvents()
    
    def reset(self):
        """Reset the status widget to its initial state."""
        self.timer.stop()
        self.elapsed_seconds = 0
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready to optimize")
        self.cancel_button.setEnabled(False)
        self.time_label.setText("Time: 0s")
        self.gap_label.setText("Gap: -")
        self.iterations_label.setText("Iterations: 0")
        
        # Hide info labels
        self.time_label.setVisible(False)
        self.gap_label.setVisible(False)
        self.iterations_label.setVisible(False)
    
    def _update_time(self):
        """Update the elapsed time label."""
        self.elapsed_seconds += 1
        self.time_label.setText(f"Time: {self.elapsed_seconds}s") 