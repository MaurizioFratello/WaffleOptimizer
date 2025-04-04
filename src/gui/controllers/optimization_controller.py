"""
Controller for managing optimization processes.
"""
import os
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from src.data.processor import DataProcessor
from src.data.validator import DataValidator
from src.solvers.base import SolverFactory

class OptimizationWorker(QObject):
    """
    Worker thread for running optimization processes.
    """
    progress = pyqtSignal(int, str, float, int)  # value, status, gap, iterations
    error = pyqtSignal(str)
    result = pyqtSignal(dict)
    finished = pyqtSignal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.cancelled = False
    
    def run(self):
        """Execute the optimization process."""
        try:
            # Create data processor
            data_processor = DataProcessor(debug_mode=self.config.get('debug', False))
            
            # Load data
            self.progress.emit(10, "Loading input data...", 0, 0)
            data_processor.load_data(
                demand_file=self.config.get('demand', ''),
                supply_file=self.config.get('supply', ''),
                cost_file=self.config.get('cost', ''),
                wpp_file=self.config.get('wpp', ''),
                combinations_file=self.config.get('combinations', '')
            )
            
            # Check if cancelled
            if self.cancelled:
                self.finished.emit()
                return
            
            # Get optimization data
            self.progress.emit(30, "Preparing optimization model...", 0, 0)
            optimization_data = data_processor.get_optimization_data()
            
            # Validate data
            data_validator = DataValidator(debug_mode=self.config.get('debug', False))
            is_feasible, critical_issues, warnings = data_validator.check_basic_feasibility(optimization_data)
            
            if not is_feasible:
                error_msg = "Data validation failed: " + "; ".join(critical_issues)
                self.error.emit(error_msg)
                self.finished.emit()
                return
            
            # Check if cancelled
            if self.cancelled:
                self.finished.emit()
                return
            
            # Create solver with consistent parameter naming
            self.progress.emit(40, "Initializing solver...", 0, 0)
            solver_factory = SolverFactory()
            
            # All solver constructors accept optimality_gap, not gap
            solver = solver_factory.create_solver(
                solver_name=self.config.get('solver', 'ortools'),
                time_limit=self.config.get('time_limit', 60),
                optimality_gap=self.config.get('gap', 0.01)  # This must be optimality_gap for all solvers
            )
            
            # Set up the model
            self.progress.emit(50, "Building optimization model...", 0, 0)
            # Choose which model to build based on the objective
            if self.config.get('objective', 'cost') == 'cost':
                solver.build_minimize_cost_model(optimization_data)
            else:
                solver.build_maximize_output_model(
                    optimization_data,
                    limit_to_demand=self.config.get('limit_to_demand', False)
                )
            
            # Check if cancelled
            if self.cancelled:
                self.finished.emit()
                return
            
            # Solve the model
            self.progress.emit(60, "Solving optimization model...", 0, 0)
            solution = solver.solve_model()
            
            # Process results
            self.progress.emit(90, "Processing results...", solution.get('gap', 0), 
                              solution.get('iterations', 0))
            
            # Get the full solution
            full_solution = solver.get_solution()
            
            # Return results
            self.result.emit(full_solution)
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit()
    
    def cancel(self):
        """Cancel the optimization process."""
        self.cancelled = True


class OptimizationController(QObject):
    """
    Controller for managing the optimization process between GUI and backend.
    """
    # Signals for updating UI
    optimization_started = pyqtSignal()
    optimization_progress = pyqtSignal(int, str, float, int)  # value, status, gap, iterations
    optimization_error = pyqtSignal(str)
    optimization_completed = pyqtSignal(dict)  # results dictionary
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.thread = None
        self.results = None
    
    def start_optimization(self, config):
        """
        Start an optimization process with the given configuration.
        
        Args:
            config: Dictionary of configuration options
        """
        # Create worker and thread
        self.thread = QThread()
        self.worker = OptimizationWorker(config)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.optimization_progress)
        self.worker.error.connect(self.optimization_error)
        self.worker.result.connect(self._store_results)
        self.worker.finished.connect(self.thread.quit)
        
        # Clean up when done
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start the thread
        self.optimization_started.emit()
        self.thread.start()
    
    def cancel_optimization(self):
        """Cancel the current optimization process."""
        if self.worker:
            self.worker.cancel()
    
    def _store_results(self, results):
        """Store the optimization results and emit completion signal."""
        self.results = results
        self.optimization_completed.emit(results)
    
    def export_results(self, file_path, format='xlsx'):
        """
        Export the optimization results to a file.
        
        Args:
            file_path: Path to save the results
            format: File format (xlsx, csv)
        """
        if not self.results:
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Export the results
            if format == 'xlsx':
                # Create a Pandas Excel writer
                writer = pd.ExcelWriter(file_path, engine='openpyxl')
                
                # Write each DataFrame to a different worksheet
                if 'production' in self.results:
                    self.results['production'].to_excel(writer, sheet_name='Production')
                
                if 'metrics' in self.results:
                    pd.DataFrame([self.results['metrics']]).to_excel(writer, sheet_name='Metrics')
                
                # Save the Excel file
                writer.close()
                
            elif format == 'csv':
                # Write the main production data to CSV
                if 'production' in self.results:
                    self.results['production'].to_csv(file_path)
            
            return True
            
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False 