# MVC Pattern with Signal-Slot Mechanism

## Overview

This document describes the implementation of the Model-View-Controller (MVC) pattern with signal-slot mechanism in the Waffle Optimizer application. The goal of this architecture is to ensure that all parameters are synchronized between the GUI and underlying code, providing a consistent user experience and reliable data flow.

## Architecture

The implementation follows these main components:

1. **Model**: Stores parameters and emits signals when they change
2. **View**: Displays the UI and binds UI components to parameters
3. **Controller**: Mediates between models and views, handling business logic

### Key Components

#### Parameter Model (`ParameterModel`)

- Centralized storage for parameter values
- Validates parameter values before storage
- Emits signals when parameters change
- Supports parameter locking to prevent changes

```python
# Example parameter model usage
from src.models.parameter_registry import ParameterRegistry

# Get or create a parameter model
param_registry = ParameterRegistry.get_instance()
optimization_params = param_registry.get_model("optimization")

# Set a parameter
optimization_params.set_parameter("time_limit", 60)

# Get a parameter
time_limit = optimization_params.get_parameter("time_limit", default=30)
```

#### Parameter Registry (`ParameterRegistry`)

- Singleton registry for accessing parameter models
- Provides named parameter models
- Ensures parameter models are consistently accessed

```python
# Example parameter registry usage
from src.models.parameter_registry import ParameterRegistry

# Get registry instance
registry = ParameterRegistry.get_instance()

# Get parameter models
data_params = registry.get_model("data")
optimization_params = registry.get_model("optimization")
```

#### Parameter-Aware View (`ParameterAwareView`)

- Base view with parameter binding capabilities
- Binds UI components to parameter model values
- Updates UI when parameters change

```python
# Example parameter binding in a view
class OptimizationView(ParameterAwareView):
    def _setup_parameter_bindings(self):
        # Bind combo box to parameter
        self._bind_combo_box(self.solver_combo, "solver")
        
        # Bind spin box to parameter
        self._bind_spin_box(self.time_limit, "time_limit")
        
        # Bind checkbox to parameter
        self._bind_check_box(self.debug_mode, "debug_mode")
```

#### Data Model Service (`DataModelService`)

- Manages data loading and processing
- Updates parameter models based on loaded data
- Emits signals when data is loaded or errors occur

```python
# Example data model service usage
from src.models.data_model_service import DataModelService

# Create data model service
data_service = DataModelService()

# Load data
data_service.load_data()

# Connect to signals
data_service.data_loaded.connect(self._on_data_loaded)
data_service.data_error.connect(self._on_data_error)
```

## Signal-Slot Mechanism

The signal-slot mechanism enables loose coupling between components by allowing communication without direct dependencies:

1. **Parameters emit signals** when they change
2. **Views connect slots** to parameter change signals
3. **Controllers connect slots** to handle business logic

This bidirectional communication ensures that:
- UI reflects the latest parameter values
- Parameter changes from code update the UI
- Parameter changes from UI update the code

## Parameter Synchronization Flow

1. **User changes UI**: UI component → Parameter binding → Parameter model → Parameter signal → Connected components update
2. **Code changes parameter**: Code → Parameter model → Parameter signal → UI components update via bindings

## Benefits

1. **Centralized Parameter Storage**: All parameters have a single source of truth
2. **Automatic UI Updates**: UI always reflects the latest parameter values
3. **Bidirectional Synchronization**: Changes in either UI or code propagate automatically
4. **Validation and Constraints**: Parameters can be validated before storage
5. **Loose Coupling**: Components communicate through signals without direct dependencies

## Implementation Details

### New Files

- `src/models/parameter_model.py`: Parameter model implementation
- `src/models/parameter_registry.py`: Parameter model registry
- `src/models/data_model_service.py`: Data processing service
- `src/gui/parameter_aware_view.py`: Base view with parameter binding

### Modified Files

- `src/gui/views/optimization_view.py`: Updated to use parameter binding
- `src/gui/views/data_view.py`: Updated to use parameter binding
- `src/gui/controllers/optimization_controller.py`: Updated to use parameter model
- `src/gui/main_window.py`: Updated to initialize parameter registry and data service

### Testing

Unit tests for parameter synchronization are available in:

- `src/tests/test_parameter_sync.py`

## Usage Guidelines

### Creating a New View with Parameter Binding

1. Extend `ParameterAwareView` instead of `BaseView`
2. Specify the parameter model name in the constructor
3. Set up parameter bindings for UI components
4. Connect to parameter change signals as needed

```python
class MyView(ParameterAwareView):
    def __init__(self, main_window=None):
        super().__init__(
            title="My View",
            description="Description of my view",
            main_window=main_window,
            action_button_text="Apply",
            model_name="my_model"  # Parameter model name
        )
        
        # Initialize UI components
        self._init_components()
        
        # Set up parameter bindings
        self._setup_parameter_bindings()
        
        # Connect to parameter changes
        self.param_model.parameter_changed.connect(self._on_parameter_changed)
    
    def _setup_parameter_bindings(self):
        # Bind UI components to parameters
        self._bind_combo_box(self.my_combo, "my_parameter")
        self._bind_spin_box(self.my_spinner, "my_value")
    
    def _on_parameter_changed(self, name, value):
        # React to parameter changes
        if name == "my_parameter":
            # Do something when my_parameter changes
            pass
```

### Accessing Parameters from Controllers

```python
class MyController(QObject):
    def __init__(self):
        super().__init__()
        
        # Get parameter models
        self.param_registry = ParameterRegistry.get_instance()
        self.my_params = self.param_registry.get_model("my_model")
        
        # Connect to parameter changes
        self.my_params.parameter_changed.connect(self._on_parameter_changed)
    
    def _on_parameter_changed(self, name, value):
        # React to parameter changes
        pass
    
    def do_something(self):
        # Get parameter values
        value = self.my_params.get_parameter("my_parameter")
        
        # Use parameter values
        # ...
        
        # Update parameters
        self.my_params.set_parameter("result", result)
``` 