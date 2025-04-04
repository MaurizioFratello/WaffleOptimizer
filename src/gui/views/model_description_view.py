"""
Model description view for the Waffle Optimizer GUI.
"""
import os
import markdown
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, 
                          QLabel, QTextBrowser)
from PyQt6.QtCore import Qt

class ModelDescriptionView(QWidget):
    """
    View for displaying the mathematical model description.
    Shows formatted content from the README.md file.
    """
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        
        print("Initializing ModelDescriptionView")
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        header = QLabel("Mathematical Model Description")
        header.setObjectName("viewHeader")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        self.layout.addWidget(header)
        
        # Description
        description = QLabel(
            "This section describes the mathematical formulation of the waffle production "
            "optimization model used in this application."
        )
        description.setWordWrap(True)
        self.layout.addWidget(description)
        
        # Create text browser with improved configuration
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setMinimumHeight(500)  # Ensure minimum height
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(self.text_browser)
        
        # Add scroll area to layout
        self.layout.addWidget(scroll_area, 1)  # 1 = stretch factor to take available space
        
        print("About to load README content")
        # Load content directly with hardcoded description for reliability
        self._use_hardcoded_description()
        print("Description content loading completed")
    
    def _load_readme_content(self):
        """Load and format the model description from README.md."""
        readme_path = "README.md"
        
        print(f"Looking for README at: {os.path.abspath(readme_path)}")
        
        if not os.path.exists(readme_path):
            # Try to look for README in different locations
            alternative_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "README.md"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "README.md"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
            ]
            
            for alt_path in alternative_paths:
                print(f"Trying alternative path: {alt_path}")
                if os.path.exists(alt_path):
                    readme_path = alt_path
                    print(f"Found README at: {readme_path}")
                    break
            else:
                print("README.md file not found in any location, using hardcoded fallback")
                self._use_hardcoded_description()
                return
        
        try:
            # Read README content
            print(f"Opening README from: {readme_path}")
            with open(readme_path, 'r') as file:
                content = file.read()
            
            print(f"README content length: {len(content)}")
            
            # Extract the model description sections
            model_content = ""
            
            # First try to get the Mathematical Formulation section
            if "## Mathematical Formulation" in content:
                print("Found Mathematical Formulation section")
                sections = content.split('## Mathematical Formulation')
                if len(sections) > 1:
                    math_section = sections[1]
                    # Find the end of the section (next ## heading or end of file)
                    next_section = math_section.find('## ')
                    if next_section != -1:
                        math_section = math_section[:next_section]
                    model_content = "## Mathematical Formulation" + math_section
                    print(f"Math section length: {len(model_content)}")
            else:
                print("Mathematical Formulation section not found")
            
            # If no Mathematical Formulation section, include all relevant model sections
            if not model_content:
                print("Looking for relevant sections")
                sections = content.split('## ')
                for section in sections:
                    if any(keyword in section.lower()[:50] for keyword in 
                          ['mathematical', 'model', 'formulation', 'optimization', 'features']):
                        print(f"Found relevant section: {section[:30]}...")
                        next_section = section.find('## ')
                        if next_section != -1:
                            section = section[:next_section]
                        model_content += "## " + section + "\n\n"
            
            # If still no content, use the Overview and Features sections
            if not model_content:
                print("Looking for Overview and Features sections")
                if "## Overview" in content:
                    print("Found Overview section")
                    sections = content.split('## Overview')
                    if len(sections) > 1:
                        overview = sections[1]
                        next_section = overview.find('## ')
                        if next_section != -1:
                            overview = overview[:next_section]
                        model_content = "## Overview" + overview
                
                if "## Features" in content:
                    print("Found Features section")
                    sections = content.split('## Features')
                    if len(sections) > 1:
                        features = sections[1]
                        next_section = features.find('## ')
                        if next_section != -1:
                            features = features[:next_section]
                        model_content += "\n\n## Features" + features
            
            # If still no content, use the whole README
            if not model_content:
                print("Using entire README content")
                model_content = content
            
            print(f"Final model content length: {len(model_content)}")
            
            # Check if markdown module is available
            try:
                import markdown
                print("Markdown module is available")
            except ImportError:
                print("Markdown module is not available")
                self.text_browser.setHtml("<p>Error: The markdown module is not installed. Please install it with 'pip install markdown'.</p>")
                return
                
            # Convert markdown to HTML
            print("Converting markdown to HTML")
            try:
                html_content = markdown.markdown(
                    model_content,
                    extensions=['tables', 'fenced_code']
                )
                print(f"HTML content length: {len(html_content)}")
            except Exception as md_error:
                print(f"Error in markdown conversion: {str(md_error)}")
                self._use_hardcoded_description()
                return
            
            # Add CSS styling with proper HTML structure
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                body {{
                    font-family: sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 20px;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    margin-top: 24px;
                    margin-bottom: 16px;
                }}
                h2 {{
                    padding-bottom: 8px;
                    border-bottom: 1px solid #eee;
                }}
                code {{
                    background-color: #f6f8fa;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: monospace;
                }}
                pre {{
                    background-color: #f6f8fa;
                    padding: 16px;
                    border-radius: 3px;
                    overflow: auto;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                blockquote {{
                    margin-left: 0;
                    padding-left: 16px;
                    border-left: 4px solid #ddd;
                    color: #555;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 16px;
                }}
                table th, table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                    text-align: left;
                }}
                table th {{
                    background-color: #f6f8fa;
                }}
                p {{ margin: 10px 0; }}
                ul, ol {{ margin: 10px 0; padding-left: 25px; }}
                li {{ margin-bottom: 5px; }}
            </style>
            </head>
            <body>
            {html_content}
            </body>
            </html>
            """
            
            # Set HTML content
            print("Setting HTML content in text browser")
            self.text_browser.setHtml(styled_html)
            print("HTML content set successfully")
            
        except Exception as e:
            print(f"Error in _load_readme_content: {str(e)}")
            import traceback
            traceback.print_exc()
            self._use_hardcoded_description()
            
    def _use_hardcoded_description(self):
        """Fallback method to use a hardcoded model description if README.md loading fails."""
        print("Using hardcoded model description")
        
        # Enhanced HTML content with better mathematical formatting and more detailed explanations
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body { 
                font-family: 'Times New Roman', Times, serif; 
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
            }
            h3 { 
                color: #2c3e50; 
                margin-top: 25px;
                font-size: 1.4em;
            }
            h4 { 
                color: #2c3e50; 
                margin-top: 20px;
                font-size: 1.2em;
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
            .math {
                font-style: italic;
                font-family: 'Times New Roman', Times, serif;
                font-size: 1.1em;
                display: block;
                margin: 15px 0;
                text-align: center;
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
        </style>
        </head>
        <body>
        <h2>Mathematical Formulation of the Waffle Production Optimization Model</h2>
        
        <p>This document provides a comprehensive mathematical description of the Waffle Production Optimization Model. The formulation is presented in a structured manner suitable for both practitioners in operations research and individuals with limited mathematical background.</p>
        
        <h3>1. Problem Overview</h3>
        
        <p>The Waffle Production Optimization model addresses the efficient allocation of resources in waffle manufacturing operations. Specifically, it determines how to allocate different types of waffle production across various pan types over a planning horizon (typically measured in weeks). The model is designed to address two primary optimization objectives:</p>
        
        <ol>
            <li><strong>Cost Minimization</strong>: Determining the production schedule that satisfies all waffle demand at the minimum possible cost.</li>
            <li><strong>Output Maximization</strong>: Determining the production schedule that maximizes the total number of waffles produced, given available resources.</li>
        </ol>
        
        <p>This formulation represents a mixed-integer linear programming (MILP) model, which is a widely used mathematical approach for solving complex resource allocation problems in manufacturing environments.</p>
        
        <h3>2. Mathematical Notation and Definitions</h3>
        
        <div class="definition">
        <h4>Sets and Indices</h4>
        <ul>
            <li><em>W</em> = {1, 2, ..., <em>n<sub>w</sub></em>}: Set of waffle types, indexed by <em>w</em></li>
            <li><em>P</em> = {1, 2, ..., <em>n<sub>p</sub></em>}: Set of pan types, indexed by <em>p</em></li>
            <li><em>T</em> = {1, 2, ..., <em>n<sub>t</sub></em>}: Set of time periods (weeks), indexed by <em>t</em></li>
            <li><em>A</em> ⊆ <em>W</em> × <em>P</em>: Set of allowed combinations of waffle types and pan types</li>
        </ul>
        
        <h4>Parameters</h4>
        <ul>
            <li><em>D<sub>wt</sub></em>: Demand for waffle type <em>w</em> in week <em>t</em> (measured in number of pans)</li>
            <li><em>S<sub>pt</sub></em>: Supply of pan type <em>p</em> available in week <em>t</em></li>
            <li><em>N<sub>w</sub></em>: Number of waffles of type <em>w</em> that can be produced per pan</li>
            <li><em>C<sub>wp</sub></em>: Cost per waffle for producing waffle type <em>w</em> using pan type <em>p</em> (in monetary units)</li>
            <li><em>A<sub>wp</sub></em>: Binary parameter indicating whether waffle type <em>w</em> can be produced using pan type <em>p</em> (equals 1 if allowed, 0 otherwise)</li>
        </ul>
        
        <h4>Decision Variables</h4>
        <ul>
            <li><em>X<sub>wpt</sub></em>: Integer variable representing the number of pans of type <em>p</em> used to produce waffle type <em>w</em> in week <em>t</em></li>
        </ul>
        </div>
        
        <h3>3. Objective Functions</h3>
        
        <p>The model can be optimized using either of two distinct objective functions, depending on the primary goal of the production planning process:</p>
        
        <h4>3.1 Cost Minimization Objective</h4>
        
        <p>The cost minimization objective seeks to minimize the total production cost across all waffle types, pan types, and time periods:</p>
        
        <div class="math">
            Minimize Z<sub>cost</sub> = ∑<sub>w∈W</sub> ∑<sub>p∈P</sub> ∑<sub>t∈T</sub> (C<sub>wp</sub> × N<sub>w</sub> × X<sub>wpt</sub>)
        </div>
        
        <p>In this formula, the term (C<sub>wp</sub> × N<sub>w</sub>) represents the total cost of using one pan of type <em>p</em> to produce waffle type <em>w</em>. This is multiplied by the number of pans used (X<sub>wpt</sub>) and summed across all combinations of waffle types, pan types, and time periods.</p>
        
        <div class="example">
        <h4>Example: Cost Calculation</h4>
        <p>Consider a scenario with the following parameters:</p>
        <ul>
            <li>Standard waffles (w=1) cost $0.50 per waffle when made on Regular pans (p=1)</li>
            <li>10 standard waffles can be produced per Regular pan (N<sub>1</sub> = 10)</li>
            <li>If we use 20 Regular pans for Standard waffles in week 1 (X<sub>1,1,1</sub> = 20)</li>
        </ul>
        <p>The contribution to the total cost would be:</p>
        <p>C<sub>1,1</sub> × N<sub>1</sub> × X<sub>1,1,1</sub> = $0.50 × 10 × 20 = $100</p>
        <p>This means the cost of producing Standard waffles on Regular pans in week 1 is $100. This calculation would be repeated for all combinations of waffle types, pan types, and weeks, and the results would be summed to get the total cost.</p>
        </div>
        
        <h4>3.2 Output Maximization Objective</h4>
        
        <p>The output maximization objective seeks to maximize the total number of waffles produced across all types and time periods:</p>
        
        <div class="math">
            Maximize Z<sub>output</sub> = ∑<sub>w∈W</sub> ∑<sub>p∈P</sub> ∑<sub>t∈T</sub> (N<sub>w</sub> × X<sub>wpt</sub>)
        </div>
        
        <p>This formula calculates the total number of waffles produced by multiplying the number of waffles per pan (N<sub>w</sub>) by the number of pans used (X<sub>wpt</sub>) for each combination, and then summing across all waffle types, pan types, and time periods.</p>
        
        <h3>4. Constraints</h3>
        
        <p>The model incorporates several constraints to ensure the solution is feasible and meets all operational requirements:</p>
        
        <h4>4.1 Demand Satisfaction Constraints</h4>
        
        <p>For each waffle type and each week, the number of pans used must exactly meet the demand:</p>
        
        <div class="math">
            ∑<sub>p∈P</sub> X<sub>wpt</sub> = D<sub>wt</sub>   ∀w∈W, ∀t∈T
        </div>
        
        <p>This constraint ensures that production quantities precisely match the required demand. For each waffle type and time period, the sum of pans used across all pan types must equal the demand for that waffle type in that week.</p>
        
        <div class="example">
        <h4>Example: Demand Satisfaction</h4>
        <p>Suppose we have the following demand for Standard waffles (w=1) in week 1:</p>
        <p>D<sub>1,1</sub> = 100 pans</p>
        <p>If we have two types of pans available: Regular (p=1) and Premium (p=2), then the constraint would be:</p>
        <p>X<sub>1,1,1</sub> + X<sub>1,2,1</sub> = 100</p>
        <p>This means that the number of Regular pans plus the number of Premium pans used for Standard waffles in week 1 must equal 100. A valid solution might be X<sub>1,1,1</sub> = 60 and X<sub>1,2,1</sub> = 40, indicating that 60 Regular pans and 40 Premium pans are used to make Standard waffles in week 1.</p>
        </div>
        
        <h4>4.2 Supply Limitation with Cumulative Tracking Constraints</h4>
        
        <p>A distinctive feature of this model is the cumulative tracking of pan supply. Unused pans from earlier weeks can be used in later weeks. For each pan type and each week, the cumulative usage up to and including that week cannot exceed the cumulative supply:</p>
        
        <div class="math">
            ∑<sub>w∈W</sub> ∑<sub>t'≤t</sub> X<sub>wpt'</sub> ≤ ∑<sub>t'≤t</sub> S<sub>pt'}   ∀p∈P, ∀t∈T
        </div>
        
        <p>In this constraint, t'≤t represents all weeks up to and including week t. The left side of the inequality sums the usage of pan type p across all waffle types and all weeks up to and including week t. The right side sums the supply of pan type p across all weeks up to and including week t.</p>
        
        <div class="example">
        <h4>Example: Cumulative Supply Tracking</h4>
        <p>Consider the following scenario for Regular pans (p=1) over a 2-week period:</p>
        <ul>
            <li>Week 1 supply: S<sub>1,1</sub> = 120 pans</li>
            <li>Week 2 supply: S<sub>1,2</sub> = 80 pans</li>
        </ul>
        
        <p>For week 1, the constraint would be:</p>
        <p>∑<sub>w∈W</sub> X<sub>w,1,1</sub> ≤ 120</p>
        
        <p>This means that the total number of Regular pans used across all waffle types in week 1 cannot exceed 120.</p>
        
        <p>For week 2, the constraint would be:</p>
        <p>∑<sub>w∈W</sub> X<sub>w,1,1</sub> + ∑<sub>w∈W</sub> X<sub>w,1,2</sub> ≤ 120 + 80 = 200</p>
        
        <p>This means that the total number of Regular pans used across all waffle types in both weeks 1 and 2 combined cannot exceed 200.</p>
        
        <p>If we used only 100 pans in week 1, then we would have (120 - 100) = 20 pans carried over to week 2, plus the new supply of 80 pans, giving a total of 100 pans available for use in week 2.</p>
        </div>
        
        <h4>4.3 Allowed Combinations Constraints</h4>
        
        <p>Waffle types can only be produced using compatible pan types:</p>
        
        <div class="math">
            X<sub>wpt</sub> = 0   ∀(w,p)∉A, ∀t∈T
        </div>
        
        <p>This constraint ensures that production is only allowed for compatible combinations of waffle types and pan types. If a particular waffle type cannot be produced on a certain pan type, the corresponding decision variable is forced to be zero.</p>
        
        <div class="example">
        <h4>Example: Allowed Combinations</h4>
        <p>Suppose we have the following compatibility matrix:</p>
        <table>
            <tr>
                <th>Waffle Type / Pan Type</th>
                <th>Regular Pan (p=1)</th>
                <th>Premium Pan (p=2)</th>
            </tr>
            <tr>
                <td>Standard Waffle (w=1)</td>
                <td>Compatible (A<sub>1,1</sub>=1)</td>
                <td>Compatible (A<sub>1,2</sub>=1)</td>
            </tr>
            <tr>
                <td>Deluxe Waffle (w=2)</td>
                <td>Not Compatible (A<sub>2,1</sub>=0)</td>
                <td>Compatible (A<sub>2,2</sub>=1)</td>
            </tr>
        </table>
        
        <p>This means Deluxe waffles cannot be made on Regular pans. The constraint would force:</p>
        <p>X<sub>2,1,t</sub> = 0 for all time periods t</p>
        <p>As a result, in the optimal solution, we would never see Deluxe waffles being produced on Regular pans.</p>
        </div>
        
        <h4>4.4 Non-negativity and Integrality Constraints</h4>
        
        <p>All decision variables must be non-negative integers:</p>
        
        <div class="math">
            X<sub>wpt</sub> ∈ ℤ<sup>+</sup> ∪ {0}   ∀w∈W, ∀p∈P, ∀t∈T
        </div>
        
        <p>This constraint ensures that the decision variables represent realistic production quantities, which must be whole numbers (you cannot use a fraction of a pan) and cannot be negative.</p>
        
        <h3>5. Model Variants and Considerations</h3>
        
        <h4>5.1 Output Maximization with Demand as Lower Bound</h4>
        
        <p>In the output maximization variant, the model can be adjusted to allow production to exceed demand, changing the demand satisfaction constraint to:</p>
        
        <div class="math">
            ∑<sub>p∈P</sub> X<sub>wpt</sub> ≥ D<sub>wt</sub>   ∀w∈W, ∀t∈T
        </div>
        
        <p>This modification turns the demand from an equality constraint (exact satisfaction) into a lower bound, allowing the model to produce more than the required amount if doing so maximizes the overall output.</p>
        
        <h4>5.2 Boundary Conditions and Edge Cases</h4>
        
        <p>The model handles several important boundary conditions and edge cases:</p>
        
        <ul>
            <li><strong>Zero Demand</strong>: If D<sub>wt</sub> = 0 for some waffle type and time period, the model will automatically allocate zero production for that waffle type in that period.</li>
            <li><strong>Zero Supply</strong>: If S<sub>pt</sub> = 0 for some pan type and time period, the model will not be able to use that pan type in that period or carry any supply forward from that period.</li>
            <li><strong>Infeasible Problems</strong>: The model may become infeasible if the total supply is insufficient to meet the total demand, or if there are incompatibilities between waffle types and pan types that prevent demand satisfaction.</li>
        </ul>
        
        <div class="example">
        <h4>Example: Complete Scenario</h4>
        <p>Consider a comprehensive scenario with:</p>
        <ul>
            <li>Two waffle types: Standard (w=1) and Deluxe (w=2)</li>
            <li>Two pan types: Regular (p=1) and Premium (p=2)</li>
            <li>Two time periods (weeks)</li>
        </ul>
        
        <p><strong>Parameters:</strong></p>
        <table>
            <tr>
                <th colspan="3">Demand (D<sub>wt</sub>) in number of pans</th>
            </tr>
            <tr>
                <th>Waffle Type / Week</th>
                <th>Week 1</th>
                <th>Week 2</th>
            </tr>
            <tr>
                <td>Standard</td>
                <td>100</td>
                <td>150</td>
            </tr>
            <tr>
                <td>Deluxe</td>
                <td>50</td>
                <td>75</td>
            </tr>
        </table>
        
        <table>
            <tr>
                <th colspan="3">Supply (S<sub>pt</sub>) in number of pans</th>
            </tr>
            <tr>
                <th>Pan Type / Week</th>
                <th>Week 1</th>
                <th>Week 2</th>
            </tr>
            <tr>
                <td>Regular</td>
                <td>120</td>
                <td>100</td>
            </tr>
            <tr>
                <td>Premium</td>
                <td>80</td>
                <td>90</td>
            </tr>
        </table>
        
        <table>
            <tr>
                <th colspan="2">Waffles per Pan (N<sub>w</sub>)</th>
            </tr>
            <tr>
                <th>Waffle Type</th>
                <th>Number of Waffles</th>
            </tr>
            <tr>
                <td>Standard</td>
                <td>10</td>
            </tr>
            <tr>
                <td>Deluxe</td>
                <td>8</td>
            </tr>
        </table>
        
        <table>
            <tr>
                <th colspan="3">Cost per Waffle (C<sub>wp</sub>) in dollars</th>
            </tr>
            <tr>
                <th>Waffle Type / Pan Type</th>
                <th>Regular</th>
                <th>Premium</th>
            </tr>
            <tr>
                <td>Standard</td>
                <td>0.50</td>
                <td>0.60</td>
            </tr>
            <tr>
                <td>Deluxe</td>
                <td>0.70</td>
                <td>0.65</td>
            </tr>
        </table>
        
        <p>All combinations are allowed (A<sub>wp</sub> = 1 for all w,p).</p>
        
        <p><strong>Model Constraints in Action:</strong></p>
        <ol>
            <li><strong>Demand Satisfaction:</strong>
                <ul>
                    <li>X<sub>1,1,1</sub> + X<sub>1,2,1</sub> = 100 (Standard waffles, Week 1)</li>
                    <li>X<sub>2,1,1</sub> + X<sub>2,2,1</sub> = 50 (Deluxe waffles, Week 1)</li>
                    <li>X<sub>1,1,2</sub> + X<sub>1,2,2</sub> = 150 (Standard waffles, Week 2)</li>
                    <li>X<sub>2,1,2</sub> + X<sub>2,2,2</sub> = 75 (Deluxe waffles, Week 2)</li>
                </ul>
            </li>
            <li><strong>Supply Limitations:</strong>
                <ul>
                    <li>Week 1, Regular pans: X<sub>1,1,1</sub> + X<sub>2,1,1</sub> ≤ 120</li>
                    <li>Week 1, Premium pans: X<sub>1,2,1</sub> + X<sub>2,2,1</sub> ≤ 80</li>
                    <li>Weeks 1-2, Regular pans: X<sub>1,1,1</sub> + X<sub>2,1,1</sub> + X<sub>1,1,2</sub> + X<sub>2,1,2</sub> ≤ 120 + 100 = 220</li>
                    <li>Weeks 1-2, Premium pans: X<sub>1,2,1</sub> + X<sub>2,2,1</sub> + X<sub>1,2,2</sub> + X<sub>2,2,2</sub> ≤ 80 + 90 = 170</li>
                </ul>
            </li>
        </ol>
        
        <p><strong>Sample Optimal Solution (Cost Minimization):</strong></p>
        <p>For week 1:</p>
        <ul>
            <li>X<sub>1,1,1</sub> = 100 (Use 100 Regular pans for Standard waffles)</li>
            <li>X<sub>2,2,1</sub> = 50 (Use 50 Premium pans for Deluxe waffles)</li>
        </ul>
        
        <p>For week 2:</p>
        <ul>
            <li>X<sub>1,1,2</sub> = 120 (Use all 120 remaining Regular pans for Standard waffles)</li>
            <li>X<sub>1,2,2</sub> = 30 (Use 30 Premium pans for Standard waffles)</li>
            <li>X<sub>2,2,2</sub> = 75 (Use 75 Premium pans for Deluxe waffles)</li>
        </ul>
        
        <p>This solution minimizes the total cost while satisfying all demands and respecting all supply constraints. The total cost would be:</p>
        <p>(0.50 × 10 × 100) + (0.65 × 8 × 50) + (0.50 × 10 × 120) + (0.60 × 10 × 30) + (0.65 × 8 × 75) = $500 + $260 + $600 + $180 + $390 = $1,930</p>
        </div>
        
        <h3>6. Computational Considerations</h3>
        
        <p>The waffle production optimization model is a mixed-integer linear program (MILP) that can be solved using various mathematical optimization solvers. The implementation in this software utilizes industry-standard solvers like OR-Tools (Google) and various PuLP backends (CBC, GLPK, etc.).</p>
        
        <p>For large instances with many waffle types, pan types, and time periods, the computational complexity increases significantly. In such cases, the solver may employ advanced techniques such as branch-and-bound, cutting planes, and heuristics to find good solutions within reasonable time limits.</p>
        
        <p>The model is particularly well-suited for planning horizons of several weeks to months, allowing manufacturers to optimize their production schedule and resource allocation decisions in advance.</p>
        </body>
        </html>
        """
        
        # Set content directly without complex formatting
        self.text_browser.setHtml(html_content)
        print("Enhanced model description set successfully") 