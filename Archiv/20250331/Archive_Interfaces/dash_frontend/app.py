"""
Dash Frontend for Waffle Production Optimizer

This module provides a web-based frontend for the Waffle Production Optimization tool
using Dash by Plotly.
"""
import os
import sys
import base64
import io
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add parent directory to path to import waffle optimizer modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_processor import DataProcessor
from feasibility_check import FeasibilityChecker
from solver_interface import SolverFactory
from results_reporter import ResultsReporter

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# App title
app.title = "Waffle Production Optimizer"

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Waffle Production Optimizer", className="text-center my-4"),
            html.P("Optimize your waffle production planning", className="text-center lead"),
        ])
    ]),
    
    dbc.Tabs([
        # Data Upload Tab
        dbc.Tab(label="Data Upload", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Upload Data Files", className="mt-3"),
                    html.P("Upload your Excel files or use the default sample data."),
                    
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.P("Waffle Demand File:"),
                                    dcc.Upload(
                                        id='upload-demand',
                                        children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                                        style={
                                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                            'borderWidth': '1px', 'borderStyle': 'dashed',
                                            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                                        },
                                    ),
                                    html.P("Pan Supply File:"),
                                    dcc.Upload(
                                        id='upload-supply',
                                        children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                                        style={
                                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                            'borderWidth': '1px', 'borderStyle': 'dashed',
                                            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                                        },
                                    ),
                                    html.P("Waffle Cost File:"),
                                    dcc.Upload(
                                        id='upload-cost',
                                        children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                                        style={
                                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                            'borderWidth': '1px', 'borderStyle': 'dashed',
                                            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                                        },
                                    ),
                                ], width=6),
                                dbc.Col([
                                    html.P("Waffles Per Pan File:"),
                                    dcc.Upload(
                                        id='upload-wpp',
                                        children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                                        style={
                                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                            'borderWidth': '1px', 'borderStyle': 'dashed',
                                            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                                        },
                                    ),
                                    html.P("Allowed Combinations File:"),
                                    dcc.Upload(
                                        id='upload-combinations',
                                        children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                                        style={
                                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                            'borderWidth': '1px', 'borderStyle': 'dashed',
                                            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                                        },
                                    ),
                                    dbc.Checkbox(
                                        id="use-sample-data",
                                        label="Use sample data",
                                        value=True,
                                        className="mt-4"
                                    ),
                                ], width=6),
                            ]),
                            dbc.Button("Load Data", id="load-data-button", color="primary", className="mt-3"),
                            html.Div(id="load-data-output", className="mt-3"),
                        ])
                    ]),
                ], width=12)
            ]),
        ]),
        
        # Configuration Tab
        dbc.Tab(label="Configuration", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Feasibility Check", className="mt-3"),
                    html.P("Check if the optimization problem is feasible with the given constraints."),
                    dbc.Button("Check Feasibility", id="check-feasibility-button", color="primary", className="mr-2"),
                    html.Div(id="feasibility-output", className="mt-3"),
                    
                    html.H3("Optimization Settings", className="mt-4"),
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.P("Optimization Objective:"),
                                    dbc.RadioItems(
                                        id="objective-selection",
                                        options=[
                                            {"label": "Minimize Cost", "value": "minimize_cost"},
                                            {"label": "Maximize Output", "value": "maximize_output"}
                                        ],
                                        value="minimize_cost",
                                    ),
                                    html.Div(id="demand-limit-container", className="mt-3"),
                                ], width=6),
                                dbc.Col([
                                    html.P("Solver:"),
                                    dbc.Select(
                                        id="solver-selection",
                                        options=[
                                            {"label": "Google OR-Tools", "value": "ortools"}
                                        ],
                                        value="ortools",
                                    ),
                                    html.P("Time Limit (seconds):", className="mt-3"),
                                    dcc.Slider(
                                        id="time-limit-slider",
                                        min=10,
                                        max=300,
                                        step=10,
                                        value=60,
                                        marks={10: '10', 60: '60', 120: '120', 180: '180', 240: '240', 300: '300'},
                                    ),
                                ], width=6),
                            ]),
                            dbc.Button("Run Optimization", id="run-optimization-button", color="success", className="mt-3"),
                            html.Div(id="optimization-output", className="mt-3"),
                        ])
                    ]),
                ], width=12)
            ]),
        ]),
        
        # Results Tab
        dbc.Tab(label="Results", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Optimization Results", className="mt-3"),
                    html.Div(id="solution-summary"),
                    
                    html.H4("Production Visualization", className="mt-4"),
                    dbc.Tabs([
                        dbc.Tab(label="Waffle Production", children=[
                            dcc.Graph(id="waffle-production-chart")
                        ]),
                        dbc.Tab(label="Pan Usage", children=[
                            dcc.Graph(id="pan-usage-chart")
                        ]),
                        dbc.Tab(label="Supply vs Demand", children=[
                            dcc.Graph(id="supply-demand-chart")
                        ]),
                    ]),
                    
                    html.H4("Detailed Results", className="mt-4"),
                    html.Div(id="detailed-results-table"),
                    
                    html.H4("Export Solution", className="mt-4"),
                    dbc.InputGroup([
                        dbc.InputGroupText("Filename:"),
                        dbc.Input(id="export-filename", placeholder="waffle_solution.xlsx", value="waffle_solution.xlsx"),
                        dbc.Button("Export to Excel", id="export-button", color="primary"),
                    ]),
                    html.Div(id="export-output", className="mt-3"),
                ], width=12)
            ]),
        ]),
    ]),
    
    # Store components for keeping state
    dcc.Store(id="data-processor-store"),
    dcc.Store(id="feasibility-result-store"),
    dcc.Store(id="solution-store"),
    
    # Footer
    html.Footer(
        html.P("Waffle Production Optimizer - Dash Frontend", className="text-center text-muted mt-5"),
        className="mt-5"
    )
], fluid=True)

# Callbacks
@callback(
    Output("demand-limit-container", "children"),
    Input("objective-selection", "value")
)
def update_demand_limit_option(objective):
    if objective == "maximize_output":
        return dbc.Checkbox(
            id="limit-to-demand",
            label="Limit production to exactly meet demand",
            value=False,
            className="mt-2"
        )
    return html.Div()

@callback(
    [Output("load-data-output", "children"),
     Output("data-processor-store", "data")],
    Input("load-data-button", "n_clicks"),
    [State("use-sample-data", "value")],
    prevent_initial_call=True
)
def load_data(n_clicks, use_sample_data):
    if n_clicks is None:
        return html.Div(), None
    
    try:
        if use_sample_data:
            # Use default files
            demand_path = "../WaffleDemand.xlsx"
            supply_path = "../PanSupply.xlsx"
            cost_path = "../WaffleCostPerPan.xlsx"
            wpp_path = "../WafflesPerPan.xlsx"
            combinations_path = "../WafflePanCombinations.xlsx"
            
            # Create new data processor
            data_processor = DataProcessor()
            data_processor.load_data(
                demand_path, supply_path, cost_path, wpp_path, combinations_path
            )
            
            return dbc.Alert("Data loaded successfully!", color="success"), {"loaded": True}
        else:
            # For uploaded files (in a real app, you would save and process these)
            return dbc.Alert("Upload functionality would be implemented here.", color="warning"), None
    except Exception as e:
        return dbc.Alert(f"Error loading data: {str(e)}", color="danger"), None

@callback(
    [Output("feasibility-output", "children"),
     Output("feasibility-result-store", "data")],
    Input("check-feasibility-button", "n_clicks"),
    [State("data-processor-store", "data")],
    prevent_initial_call=True
)
def check_feasibility(n_clicks, data_processor_data):
    if n_clicks is None or data_processor_data is None:
        return html.Div(), None
    
    try:
        # Create a new processor since we can't store the actual object in dcc.Store
        data_processor = DataProcessor()
        demand_path = "../WaffleDemand.xlsx"
        supply_path = "../PanSupply.xlsx"
        cost_path = "../WaffleCostPerPan.xlsx"
        wpp_path = "../WafflesPerPan.xlsx"
        combinations_path = "../WafflePanCombinations.xlsx"
        data_processor.load_data(
            demand_path, supply_path, cost_path, wpp_path, combinations_path
        )
        
        # Check feasibility
        data = data_processor.get_feasibility_data()
        checker = FeasibilityChecker(data)
        is_feasible = checker.check_feasibility()
        result_summary = checker.get_result_summary()
        
        # Display results
        if is_feasible:
            status = dbc.Alert("✅ Problem is feasible!", color="success")
        else:
            status = dbc.Alert("❌ Problem may be infeasible. Check details below.", color="warning")
        
        stats = html.Div([
            html.H5("Summary Statistics:"),
            html.Ul([
                html.Li(f"Total Demand: {result_summary.get('total_demand', 0):,} waffles"),
                html.Li(f"Maximum Production Capacity: {result_summary.get('max_capacity', 0):,} waffles"),
                html.Li(f"Capacity Utilization: {result_summary.get('capacity_utilization', 0):.2f}%")
            ])
        ])
        
        issues_div = html.Div()
        if not is_feasible and 'issues' in result_summary:
            issues = result_summary['issues']
            issues_div = html.Div([
                html.H5("Potential Issues:"),
                html.Ul([html.Li(issue) for issue in issues])
            ])
        
        # This would be a placeholder for a more detailed network visualization
        network_viz = dbc.Card(
            dbc.CardBody([
                html.H5("Supply-Demand Network"),
                html.P("A network visualization would be shown here in the full implementation.")
            ])
        )
        
        return html.Div([status, stats, issues_div, network_viz]), {"is_feasible": is_feasible}
    except Exception as e:
        return dbc.Alert(f"Error checking feasibility: {str(e)}", color="danger"), None

@callback(
    [Output("optimization-output", "children"),
     Output("solution-store", "data")],
    Input("run-optimization-button", "n_clicks"),
    [State("data-processor-store", "data"),
     State("feasibility-result-store", "data"),
     State("objective-selection", "value"),
     State("solver-selection", "value"),
     State("time-limit-slider", "value"),
     State("limit-to-demand", "value")],
    prevent_initial_call=True
)
def run_optimization(n_clicks, data_processor_data, feasibility_data, objective, 
                    solver_name, time_limit, limit_to_demand):
    if n_clicks is None or data_processor_data is None:
        return html.Div(), None
    
    if feasibility_data is None:
        return dbc.Alert("Please run feasibility check first!", color="warning"), None
    
    try:
        # Re-create data processor (same as above)
        data_processor = DataProcessor()
        demand_path = "../WaffleDemand.xlsx"
        supply_path = "../PanSupply.xlsx"
        cost_path = "../WaffleCostPerPan.xlsx"
        wpp_path = "../WafflesPerPan.xlsx"
        combinations_path = "../WafflePanCombinations.xlsx"
        data_processor.load_data(
            demand_path, supply_path, cost_path, wpp_path, combinations_path
        )
        
        # Get optimization data
        data = data_processor.get_optimization_data()
        
        # Create solver
        solver = SolverFactory.create_solver(solver_name, time_limit=time_limit)
        
        # Build and solve model
        if objective == 'minimize_cost':
            solver.build_minimize_cost_model(data)
        else:  # maximize_output
            limit_demand = limit_to_demand if limit_to_demand is not None else False
            solver.build_maximize_output_model(data, limit_to_demand=limit_demand)
            
        result = solver.solve_model()
        
        # Display result
        if result['status'] in ['OPTIMAL', 'FEASIBLE']:
            solution = solver.get_solution()
            
            status_alert = dbc.Alert(f"✅ Optimization completed with status: {result['status']}", color="success")
            solve_time = html.P(f"Solve time: {result['wall_time']:.2f} seconds")
            
            # This would store minimal data to signal that we have a solution
            # In a full implementation, we'd handle the solution data transfer differently
            return html.Div([status_alert, solve_time]), {"status": result['status']}
        else:
            return dbc.Alert(f"❌ No feasible solution found. Status: {result['status']}", color="danger"), None
    except Exception as e:
        return dbc.Alert(f"Error during optimization: {str(e)}", color="danger"), None

@callback(
    [Output("solution-summary", "children"),
     Output("waffle-production-chart", "figure"),
     Output("pan-usage-chart", "figure"),
     Output("supply-demand-chart", "figure"),
     Output("detailed-results-table", "children")],
    Input("solution-store", "data"),
    [State("data-processor-store", "data")],
    prevent_initial_call=True
)
def update_results(solution_data, data_processor_data):
    if solution_data is None or data_processor_data is None:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No data available")
        return html.Div("No solution available. Please run optimization first."), empty_fig, empty_fig, empty_fig, html.Div()
    
    try:
        # This is a placeholder for actual solution visualization
        # In a real implementation, we would need to save and load the actual solution data
        
        # Re-create everything for demonstration purposes
        data_processor = DataProcessor()
        demand_path = "../WaffleDemand.xlsx"
        supply_path = "../PanSupply.xlsx"
        cost_path = "../WaffleCostPerPan.xlsx"
        wpp_path = "../WafflesPerPan.xlsx"
        combinations_path = "../WafflePanCombinations.xlsx"
        data_processor.load_data(
            demand_path, supply_path, cost_path, wpp_path, combinations_path
        )
        
        # Create some sample metrics for the demo
        metrics = dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4("Total Production", className="card-title"),
                html.H2("10,500", className="text-primary"),
                html.P("Waffles", className="text-muted")
            ])), width=4),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4("Total Cost", className="card-title"),
                html.H2("$15,750", className="text-primary"),
                html.P("USD", className="text-muted")
            ])), width=4),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4("Avg. Cost/Waffle", className="card-title"),
                html.H2("$1.50", className="text-primary"),
                html.P("USD per waffle", className="text-muted")
            ])), width=4)
        ])
        
        # Sample production chart
        waffle_fig = go.Figure()
        waffle_types = ['Belgian', 'American', 'Chocolate', 'Fruit']
        weeks = [f"Week {i+1}" for i in range(4)]
        
        for waffle in waffle_types:
            waffle_fig.add_trace(go.Bar(
                x=weeks,
                y=[500 + 100*i for i in range(4)],
                name=waffle
            ))
        
        waffle_fig.update_layout(
            title="Waffle Production by Week",
            xaxis_title="Week",
            yaxis_title="Number of Waffles",
            barmode='stack'
        )
        
        # Sample pan usage chart
        pan_fig = go.Figure()
        pan_types = ['Round', 'Square', 'Heart', 'Star']
        
        for pan in pan_types:
            pan_fig.add_trace(go.Bar(
                x=weeks,
                y=[50 + 10*i for i in range(4)],
                name=pan
            ))
        
        pan_fig.update_layout(
            title="Pan Usage by Week",
            xaxis_title="Week",
            yaxis_title="Number of Pans",
            barmode='stack'
        )
        
        # Sample supply vs demand chart
        supply_demand_fig = go.Figure()
        
        supply_demand_fig.add_trace(go.Bar(
            x=weeks,
            y=[3000, 3200, 3400, 3600],
            name='Supply'
        ))
        
        supply_demand_fig.add_trace(go.Bar(
            x=weeks,
            y=[2800, 3000, 3200, 3400],
            name='Demand'
        ))
        
        supply_demand_fig.update_layout(
            title="Supply vs Demand Comparison",
            xaxis_title="Week",
            yaxis_title="Waffles",
            barmode='group'
        )
        
        # Sample detailed results table
        sample_data = pd.DataFrame({
            'Week': ['Week 1', 'Week 1', 'Week 2', 'Week 2'],
            'Waffle Type': ['Belgian', 'American', 'Belgian', 'American'],
            'Pan Type': ['Round', 'Square', 'Round', 'Square'],
            'Pans Used': [25, 30, 28, 32],
            'Waffles Produced': [250, 300, 280, 320],
            'Cost': ['$375', '$450', '$420', '$480']
        })
        
        detailed_table = dash_table.DataTable(
            id='detailed-results',
            columns=[{"name": i, "id": i} for i in sample_data.columns],
            data=sample_data.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
        
        return metrics, waffle_fig, pan_fig, supply_demand_fig, detailed_table
        
    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Error loading results")
        error_div = dbc.Alert(f"Error loading results: {str(e)}", color="danger")
        return error_div, empty_fig, empty_fig, empty_fig, html.Div()


if __name__ == '__main__':
    app.run(debug=True, port=8050) 