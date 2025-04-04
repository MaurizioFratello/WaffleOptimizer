"""
Model description view for the Waffle Optimizer GUI.
"""
import os
from pathlib import Path
from PyQt6.QtWidgets import (QVBoxLayout, QScrollArea, 
                          QLabel, QTextBrowser)
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

from ..base_view import BaseView

class ModelDescriptionView(BaseView):
    """
    View for displaying the mathematical model description.
    Shows formatted content with MathJax for mathematical formulas.
    """
    
    def __init__(self, main_window=None):
        super().__init__(
            title="Mathematical Model Description",
            description="This section describes the mathematical formulation of the waffle production "
                       "optimization model used in this application.",
            main_window=main_window
        )
        
        print("Initializing ModelDescriptionView")
        
        # Initialize model description components
        self._init_model_description_components()
        
    def _init_model_description_components(self):
        """Initialize model description view specific components."""
        # Create web view for MathJax content
        self.web_view = QWebEngineView()
        
        # HTML content with MathJax
        html_content = r"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <script type="text/javascript" id="MathJax-script" async
          src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js">
        </script>
        <script type="text/x-mathjax-config">
          MathJax = {
            tex: {
              inlineMath: [['$', '$'], ['\\(', '\\)']],
              displayMath: [['$$', '$$'], ['\\[', '\\]']],
              processEscapes: true,
              packages: {'[+]': ['ams']}
            },
            svg: {
              fontCache: 'global'
            },
            startup: {
              ready: () => {
                MathJax.startup.defaultReady();
                MathJax.startup.promise.then(() => {
                  console.log('MathJax initialization complete');
                });
              }
            }
          };
        </script>
        <style>
            body { 
                font-family: '.AppleSystemUIFont', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
                color: #333; 
                margin: 20px;
                line-height: 1.6;
                text-align: justify;
            }
            h2 { 
                color: #2c3e50; 
                border-bottom: 1px solid #eee;
                padding-bottom: 8px;
                font-size: 1.6em;
                margin-top: 30px;
                font-weight: 600;
            }
            h3 { 
                color: #2c3e50; 
                margin-top: 25px;
                font-size: 1.4em;
                font-weight: 600;
            }
            h4 { 
                color: #2c3e50; 
                margin-top: 20px;
                font-size: 1.2em;
                font-weight: 600;
            }
            p { 
                margin: 12px 0; 
                text-align: justify;
            }
            ul, ol { 
                margin: 15px 0; 
                padding-left: 30px; 
            }
            li { 
                margin-bottom: 8px; 
                text-align: justify;
            }
            .example {
                background-color: #f8f9fa;
                border-left: 4px solid #2c3e50;
                padding: 15px;
                margin: 20px 0;
            }
            .definition {
                background-color: #eef7fa;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 20px 0;
            }
            .insight {
                background-color: #f0f7ee;
                border-left: 4px solid #27ae60;
                padding: 15px;
                margin: 20px 0;
            }
            .caution {
                background-color: #fff5eb;
                border-left: 4px solid #e67e22;
                padding: 15px;
                margin: 20px 0;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            .caption {
                font-style: italic;
                text-align: center;
                margin-top: 8px;
                font-size: 0.9em;
            }
            .math-container {
                margin: 25px 0;
                text-align: center;
            }
            .abstract {
                font-style: italic;
                border-left: 4px solid #95a5a6;
                padding: 15px;
                margin: 20px 0;
                background-color: #f8f9fa;
            }
            .section-number {
                font-weight: normal;
                color: #7f8c8d;
                margin-right: 8px;
            }
        </style>
        </head>
        <body>
        <h2>Mathematical Formulation of the Waffle Production Optimization Model</h2>
        
        <div class="abstract">
            <p><strong>Abstract:</strong> This document presents a comprehensive mathematical formulation of the Waffle Production Optimization Model. The model addresses the efficient allocation of waffle production across various pan types over a planning horizon. Using a mixed-integer linear programming approach, the model offers dual optimization capabilities: minimizing production costs while meeting demand requirements, or maximizing output under resource constraints. This formulation provides insights into optimal production scheduling for waffle manufacturing operations, contributing to improved operational efficiency and resource utilization.</p>
        </div>
        
        <h3><span class="section-number">1.</span>Introduction and Problem Context</h3>
        
        <p>Waffle production presents a complex resource allocation challenge that requires careful planning to achieve optimal outcomes. The problem involves determining how to allocate different types of waffle production across various pan types over a planning horizon (typically measured in weeks). This allocation must satisfy several operational constraints while optimizing business objectives.</p>
        
        <p>The primary considerations in waffle production planning include:</p>
        
        <ul>
            <li><strong>Demand Fulfillment:</strong> Meeting specific demand requirements for different waffle types over the planning horizon.</li>
            <li><strong>Resource Utilization:</strong> Efficiently utilizing available pan supplies, which may vary over time.</li>
            <li><strong>Production Compatibility:</strong> Accounting for the fact that certain waffle types can only be produced using specific pan types.</li>
            <li><strong>Cost Management:</strong> Minimizing the overall production cost while meeting operational requirements.</li>
            <li><strong>Output Maximization:</strong> Alternatively, maximizing the total number of waffles produced given the available resources.</li>
        </ul>
        
        <p>This formulation employs a mixed-integer linear programming (MILP) model, a mathematical approach widely used in operations research to address complex resource allocation problems. MILP models are particularly suited for manufacturing environments where decisions involve discrete quantities and multiple constraints.</p>
        
        <h3><span class="section-number">2.</span>Mathematical Notation and Definitions</h3>
        
        <p>To formulate the waffle production optimization problem mathematically, we first define the sets, parameters, and decision variables that compose the model. These components provide the foundation for expressing the optimization objectives and operational constraints.</p>
        
        <div class="definition">
        <h4>Sets and Indices</h4>
        <ul>
            <li>\(W = \{1, 2, \ldots, n_w\}\): Set of waffle types, indexed by \(w\). This represents the different varieties of waffles that the facility can produce (e.g., classic, chocolate, fruit-topped).</li>
            <li>\(P = \{1, 2, \ldots, n_p\}\): Set of pan types, indexed by \(p\). This represents the different types of pans that can be used in the production process (e.g., round, square, specialized shapes).</li>
            <li>\(T = \{1, 2, \ldots, n_t\}\): Set of time periods (weeks), indexed by \(t\). This represents the planning horizon over which production is scheduled.</li>
            <li>\(A \subseteq W \times P\): Set of allowed combinations of waffle types and pan types. This subset identifies which waffle types can be produced using which pan types, capturing production compatibility constraints.</li>
        </ul>
        
        <h4>Parameters</h4>
        <ul>
            <li>\(D_{wt}\): Demand for waffle type \(w\) in week \(t\) (measured in number of pans). This represents the quantity of each waffle type that must be produced to satisfy customer orders in each week.</li>
            <li>\(S_{pt}\): Supply of pan type \(p\) available in week \(t\). This represents the inventory or availability of each pan type in each week of the planning horizon.</li>
            <li>\(N_w\): Number of waffles of type \(w\) that can be produced per pan. This represents the production yield for each waffle type, which may vary based on waffle size or complexity.</li>
            <li>\(C_{wp}\): Cost per waffle for producing waffle type \(w\) using pan type \(p\) (in monetary units). This captures the production cost, which may vary depending on the combination of waffle type and pan type.</li>
            <li>\(A_{wp}\): Binary parameter indicating whether waffle type \(w\) can be produced using pan type \(p\) (equals 1 if allowed, 0 otherwise). This formally captures the compatibility constraints between waffle types and pan types.</li>
        </ul>
        
        <h4>Decision Variables</h4>
        <ul>
            <li>\(X_{wpt}\): Integer variable representing the number of pans of type \(p\) used to produce waffle type \(w\) in week \(t\). This is the primary decision variable that determines the production schedule.</li>
            <li>\(Y_{wpt}\): Binary variable indicating whether waffle type \(w\) is produced using pan type \(p\) in week \(t\) (equals 1 if produced, 0 otherwise). This variable can be used for tracking setup requirements or minimum batch sizes.</li>
        </ul>
        </div>
        
        <div class="insight">
        <h4>Interconnection of Model Components</h4>
        <p>The sets, parameters, and decision variables interconnect to form a comprehensive model of the waffle production system. The indices (\(w\), \(p\), and \(t\)) provide the dimensional structure, allowing us to represent production decisions across different waffle types, pan types, and time periods. The parameters capture the operational realities and constraints of the production environment, while the decision variables represent the choices to be optimized.</p>
        </div>
        
        <h3><span class="section-number">3.</span>Objective Functions</h3>
        
        <p>The model offers two alternative objective functions, representing different business priorities: cost minimization and output maximization. These objectives reflect common trade-offs in production planning between minimizing expenses and maximizing productivity.</p>
        
        <div class="math-container">
        <h4>Cost Minimization</h4>
        \[
        \min Z_{\text{cost}} = \sum_{w \in W} \sum_{p \in P} \sum_{t \in T} (C_{wp} \times N_w \times X_{wpt})
        \]
        </div>
        
        <p>The cost minimization objective function calculates the total cost of waffle production over the entire planning horizon. For each combination of waffle type (\(w\)), pan type (\(p\)), and week (\(t\)), it multiplies:</p>
        <ul>
            <li>The cost per waffle (\(C_{wp}\)) for producing waffle type \(w\) using pan type \(p\)</li>
            <li>The number of waffles per pan (\(N_w\)) for waffle type \(w\)</li>
            <li>The number of pans used (\(X_{wpt}\)) for this particular combination</li>
        </ul>
        
        <p>These individual costs are summed across all combinations to determine the total production cost. This objective is particularly relevant when operating under fixed demand requirements and seeking to minimize operational expenses.</p>
        
        <div class="example">
        <h4>Cost Minimization Example</h4>
        <p>Consider a simple scenario with the following parameters:</p>
        <ul>
            <li>Standard waffles (\(w=1\)) cost \($0.30\) per waffle using regular pans (\(p=1\)) and \($0.25\) per waffle using premium pans (\(p=2\)).</li>
            <li>Each regular pan produces 4 standard waffles, and each premium pan produces 6 standard waffles.</li>
            <li>In week 1, the production plan uses 50 regular pans and 30 premium pans for standard waffles.</li>
        </ul>
        <p>The cost calculation for just this component would be:</p>
        <p>\($0.30 \times 4 \times 50 + $0.25 \times 6 \times 30 = $60 + $45 = $105\)</p>
        <p>The complete objective function would sum similar calculations across all waffle types, pan types, and weeks.</p>
        </div>
        
        <div class="math-container">
        <h4>Output Maximization</h4>
        \[
        \max Z_{\text{output}} = \sum_{w \in W} \sum_{p \in P} \sum_{t \in T} (N_w \times X_{wpt})
        \]
        </div>
        
        <p>The output maximization objective function calculates the total number of waffles produced over the planning horizon. For each combination of waffle type (\(w\)), pan type (\(p\)), and week (\(t\)), it multiplies:</p>
        <ul>
            <li>The number of waffles per pan (\(N_w\)) for waffle type \(w\)</li>
            <li>The number of pans used (\(X_{wpt}\)) for this particular combination</li>
        </ul>
        
        <p>These individual quantities are summed across all combinations to determine the total production output. This objective is particularly relevant when operating with flexible demand requirements and seeking to maximize production volume under resource constraints.</p>
        
        <div class="example">
        <h4>Output Maximization Example</h4>
        <p>Using the same scenario as above:</p>
        <ul>
            <li>Each regular pan produces 4 standard waffles, and each premium pan produces 6 standard waffles.</li>
            <li>In week 1, the production plan uses 50 regular pans and 30 premium pans for standard waffles.</li>
        </ul>
        <p>The output calculation for just this component would be:</p>
        <p>\(4 \times 50 + 6 \times 30 = 200 + 180 = 380\) waffles</p>
        <p>The complete objective function would sum similar calculations across all waffle types, pan types, and weeks.</p>
        </div>
        
        <div class="insight">
        <h4>Objective Function Selection</h4>
        <p>The choice between cost minimization and output maximization depends on the specific business priorities and operational context:</p>
        <ul>
            <li><strong>Cost Minimization:</strong> Preferred when demand must be satisfied exactly and the primary goal is to reduce production expenses.</li>
            <li><strong>Output Maximization:</strong> Preferred when there is flexibility in demand fulfillment and the primary goal is to maximize production volume within resource constraints.</li>
        </ul>
        <p>These objectives represent different managerial perspectives on production optimization and typically lead to different optimal solutions.</p>
        </div>
        
        <h3><span class="section-number">4.</span>Constraints</h3>
        
        <p>The model incorporates several constraints to ensure that the production plan is feasible and meets all operational requirements. These constraints collectively define the boundaries of valid solutions and reflect the practical limitations of the production environment.</p>
        
        <h4>4.1 Demand Satisfaction Constraints</h4>
        <p>For each waffle type and each week, the number of pans used must exactly meet the demand:</p>
        \[
        \sum_{p \in P} X_{wpt} = D_{wt} \quad \forall w \in W, \forall t \in T
        \]
        
        <p>This constraint ensures that production quantities precisely match the required demand. For each waffle type and time period, the sum of pans used across all pan types must equal the demand for that waffle type in that week. This constraint is critical for maintaining customer satisfaction and preventing either shortages or excess inventory.</p>
        
        <div class="example">
        <h4>Demand Satisfaction Example</h4>
        <p>Suppose we have the following demand for Standard waffles (\(w=1\)) in week 1:</p>
        <p>\(D_{1,1} = 100\) pans</p>
        <p>If we have two types of pans available: Regular (\(p=1\)) and Premium (\(p=2\)), then the constraint would be:</p>
        <p>\(X_{1,1,1} + X_{1,2,1} = 100\)</p>
        <p>This means that the number of Regular pans plus the number of Premium pans used for Standard waffles in week 1 must equal 100. A valid solution might be \(X_{1,1,1} = 60\) and \(X_{1,2,1} = 40\), indicating that 60 Regular pans and 40 Premium pans are used to make Standard waffles in week 1.</p>
        </div>
        
        <h4>4.2 Supply Limitation Constraints</h4>
        <p>For each pan type and each week, the cumulative usage of pans up to that week cannot exceed the cumulative supply:</p>
        \[
        \sum_{w \in W} \sum_{t' \leq t} X_{wpt'} \leq \sum_{t' \leq t} S_{pt'} \quad \forall p \in P, \forall t \in T
        \]
        
        <p>This constraint tracks the cumulative usage of each pan type over time, ensuring that we don't use more pans than are available when considering the accumulated supply. This is particularly important for managing inventory and preventing resource overallocation.</p>
        
        <div class="example">
        <h4>Supply Limitation Example</h4>
        <p>Consider the following supply of Regular pans (\(p=1\)):</p>
        <ul>
            <li>Week 1: \(S_{1,1} = 120\) pans</li>
            <li>Week 2: \(S_{1,2} = 80\) pans</li>
        </ul>
        
        <p>For week 1, the constraint would be:</p>
        <p>\(\sum_{w \in W} X_{w,1,1} \leq 120\)</p>
        
        <p>This means that the total number of Regular pans used across all waffle types in week 1 cannot exceed 120.</p>
        
        <p>For week 2, the constraint would be:</p>
        <p>\(\sum_{w \in W} X_{w,1,1} + \sum_{w \in W} X_{w,1,2} \leq 120 + 80 = 200\)</p>
        
        <p>This means that the total number of Regular pans used across all waffle types in both weeks 1 and 2 combined cannot exceed 200.</p>
        </div>
        
        <h4>4.3 Compatibility Constraints</h4>
        <p>Some waffle types can only be produced using specific pan types. This is enforced through the compatibility constraints:</p>
        \[
        X_{wpt} = 0 \quad \forall(w,p) \notin A, \forall t \in T
        \]
        
        <p>This constraint ensures that waffles are only produced using compatible pan types. If a particular combination of waffle type and pan type is not allowed (i.e., not in the set \(A\)), then the number of pans used for that combination must be zero. This reflects manufacturing realities where certain product designs require specific production equipment.</p>
        
        <div class="example">
        <h4>Compatibility Example</h4>
        <p>Suppose that Deluxe waffles (\(w=2\)) can only be produced using Premium pans (\(p=2\)) and not using Regular pans (\(p=1\)). This means that the pair \((2,1)\) is not in the set \(A\) of allowed combinations.</p>
        
        <p>The resulting constraint would be:</p>
        <p>\(X_{2,1,t} = 0 \quad \forall t \in T\)</p>
        
        <p>This ensures that no Regular pans are used for producing Deluxe waffles in any week of the planning horizon.</p>
        </div>
        
        <h4>4.4 Non-negativity and Integrality Constraints</h4>
        <p>The number of pans used must be non-negative integers:</p>
        \[
        X_{wpt} \in \mathbb{Z}^+ \cup \{0\} \quad \forall w \in W, \forall p \in P, \forall t \in T
        \]
        
        <p>This constraint ensures that the decision variables take on realistic values. Production quantities can't be negative (we can't "un-produce" waffles), and they must be whole numbers (we can't use a fractional pan). This constraint is fundamental to the mixed-integer nature of the model.</p>
        
        <div class="caution">
        <h4>Integrality and Computational Complexity</h4>
        <p>The integrality constraints on the decision variables significantly increase the computational complexity of the model. While linear programs with continuous variables can often be solved efficiently, the addition of integer restrictions makes the problem NP-hard. This means that solution times may increase exponentially with the problem size.</p>
        
        <p>In practice, for large-scale production planning, it may be necessary to use specialized solvers, employ heuristic methods, or consider relaxing the integrality constraints in some cases to achieve solutions within reasonable computation times.</p>
        </div>
        
        <h3><span class="section-number">5.</span>Constraint Interactions and System Behavior</h3>
        
        <p>The constraints in the waffle production model do not operate in isolation; they interact to create a complex system of requirements that collectively shape the feasible solution space. Understanding these interactions is crucial for interpreting model behavior and results.</p>
        
        <div class="insight">
        <h4>Key Constraint Interactions</h4>
        <ol>
            <li><strong>Demand vs. Supply Interaction:</strong> The demand satisfaction constraints (4.1) and supply limitation constraints (4.2) interact to create a balance between what needs to be produced and what can be produced. In scenarios where supply is limited, it may not be possible to satisfy all demand, creating a tension that the optimization model must resolve based on the selected objective function.</li>
            <li><strong>Compatibility as a Constraint Modifier:</strong> The compatibility constraints (4.3) effectively modify the structure of the other constraints by removing certain variables from consideration. This reduces the degrees of freedom in the model and can significantly affect the optimal solution.</li>
            <li><strong>Temporal Coupling through Cumulative Supply:</strong> The supply limitation constraints (4.2) create temporal coupling in the model, where decisions in early time periods affect what's possible in later periods. This sequential dependency captures the reality of inventory management and resource utilization over time.</li>
        </ol>
        </div>
        
        <p>The behavior of the system under different parameter settings reveals important insights about waffle production operations:</p>
        
        <ul>
            <li><strong>Under Tight Supply Conditions:</strong> When pan supply is limited relative to demand, the model prioritizes efficient use of resources. In cost minimization mode, it allocates pans to the most cost-effective waffle-pan combinations first. In output maximization mode, it prioritizes waffle types with higher yields per pan.</li>
            <li><strong>With Varying Demand Patterns:</strong> When demand fluctuates over the planning horizon, the model may suggest different production strategies for different time periods, adapting to changing requirements while respecting cumulative supply constraints.</li>
            <li><strong>With Restrictive Compatibility:</strong> When many waffle types can only be produced on specific pan types, the system flexibility decreases. This can lead to suboptimal solutions in terms of cost or output compared to scenarios with greater compatibility.</li>
        </ul>
        
        <h3><span class="section-number">6.</span>Complete Model Summary</h3>
        
        <p>The complete mathematical model for waffle production optimization consists of:</p>
        
        <ol>
            <li><strong>Decision Variables:</strong> \(X_{wpt}\) for all combinations of \(w \in W\), \(p \in P\), \(t \in T\)</li>
            <li><strong>Objective Function:</strong> Either minimize \(Z_{cost}\) or maximize \(Z_{output}\)</li>
            <li><strong>Subject to:</strong>
                <ul>
                    <li>Demand Satisfaction: \(\sum_{p \in P} X_{wpt} = D_{wt}\) for all \(w\), \(t\)</li>
                    <li>Supply Limitations: \(\sum_{w \in W} \sum_{t' \leq t} X_{wpt'} \leq \sum_{t' \leq t} S_{pt'}\) for all \(p\), \(t\)</li>
                    <li>Compatibility: \(X_{wpt} = 0\) for all \((w,p) \notin A\), \(t\)</li>
                    <li>Non-negativity and Integrality: \(X_{wpt} \in \mathbb{Z}^+ \cup \{0\}\) for all \(w\), \(p\), \(t\)</li>
                </ul>
            </li>
        </ol>
        
        <h3><span class="section-number">7.</span>Practical Implications and Extensions</h3>
        
        <p>The waffle production optimization model provides a structured approach to production planning that can yield significant operational benefits:</p>
        
        <ul>
            <li><strong>Cost Reduction:</strong> By optimizing the allocation of waffle types to pan types, the model can identify cost-saving opportunities that might not be apparent through manual planning methods.</li>
            <li><strong>Improved Resource Utilization:</strong> The model ensures that limited pan supplies are used efficiently, maximizing either cost efficiency or production volume as needed.</li>
            <li><strong>Scenario Analysis:</strong> The model can be used to evaluate various what-if scenarios, such as changes in demand patterns, supply availability, or production costs, helping management make informed decisions.</li>
        </ul>
        
        <p>Potential extensions to the model could include:</p>
        
        <ul>
            <li><strong>Setup Costs and Times:</strong> Incorporating the costs and times associated with changing production from one waffle type to another.</li>
            <li><strong>Workforce Constraints:</strong> Adding limitations based on available labor hours or skills.</li>
            <li><strong>Inventory Holding Costs:</strong> Including costs associated with storing excess production from one period to the next.</li>
            <li><strong>Multi-objective Optimization:</strong> Developing approaches that balance cost minimization and output maximization simultaneously.</li>
        </ul>
        
        <div class="insight">
        <h4>Conclusion</h4>
        <p>The waffle production optimization model demonstrates the power of mathematical programming for addressing complex production planning challenges. By capturing the essential operational constraints and business objectives in a structured mathematical framework, the model provides a systematic approach to finding optimal production schedules. Whether the focus is on minimizing costs or maximizing output, the model delivers valuable insights that can guide effective decision-making in waffle manufacturing operations.</p>
        </div>
        </body>
        </html>
        """
        
        # Set HTML content
        self.web_view.setHtml(html_content)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(self.web_view)
        
        # Add scroll area to layout
        self.content_layout.addWidget(scroll_area, 1)  # 1 = stretch factor to take available space 