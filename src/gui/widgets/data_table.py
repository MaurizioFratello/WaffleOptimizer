"""
Data table widget for displaying tabular data from pandas DataFrames.
"""
from PyQt6.QtWidgets import QTableView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class DataTable(QTableView):
    """
    A table view widget for displaying pandas DataFrames.
    Provides methods for loading and formatting table data.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up table properties
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        
        # Create empty model
        self.model = QStandardItemModel()
        self.setModel(self.model)
    
    def load_dataframe(self, df, max_rows=1000):
        """
        Load a pandas DataFrame into the table view.
        
        Args:
            df: pandas DataFrame to display
            max_rows: Maximum number of rows to show (for performance)
        """
        if df is None or df.empty:
            self.model.clear()
            return
        
        # Limit rows for performance
        if len(df) > max_rows:
            df = df.head(max_rows)
        
        # Set headers
        self.model.clear()
        self.model.setColumnCount(len(df.columns))
        self.model.setHorizontalHeaderLabels(df.columns)
        
        # Add data rows
        self.model.setRowCount(len(df))
        
        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = str(df.iloc[row, col])
                item = QStandardItem(value)
                self.model.setItem(row, col, item)
        
        # Resize columns to content
        self.resizeColumnsToContents()
    
    def clear(self):
        """Clear all data from the table."""
        self.model.clear() 