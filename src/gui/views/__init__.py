"""
View modules for the Waffle Optimizer GUI.
"""
from .dashboard_view import DashboardView
from .data_view import DataView
from .optimization_view import OptimizationView
from .results_view import ResultsView
from .model_description_view import ModelDescriptionView
from .validation_dashboard_view import ValidationDashboardView

__all__ = [
    'DashboardView',
    'DataView',
    'ValidationDashboardView',
    'OptimizationView',
    'ResultsView',
    'ModelDescriptionView'
] 