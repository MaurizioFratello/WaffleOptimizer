#!/usr/bin/env python3
"""
Solver Installation Script for Waffle Production Optimization.

This script helps install and check the availability of optimization solvers
used in the Waffle Production Optimization project.
"""
import os
import sys
import subprocess
import platform
from typing import Dict, List, Tuple
import importlib.util

def check_pulp_installation() -> bool:
    """Check if PuLP is installed."""
    try:
        import pulp
        print(f"✅ PuLP is installed (version {pulp.__version__})")
        return True
    except ImportError:
        print("❌ PuLP is not installed.")
        return False

def check_available_solvers() -> Dict[str, bool]:
    """Check which solvers are available in the current environment."""
    try:
        import pulp
        all_solvers = pulp.listSolvers(onlyAvailable=False)
        available_solvers = pulp.listSolvers(onlyAvailable=True)
        
        result = {}
        for solver in all_solvers:
            result[solver] = solver in available_solvers
            
        return result
    except ImportError:
        print("❌ PuLP is not installed. Cannot check solvers.")
        return {}

def print_solver_status(solver_status: Dict[str, bool]) -> None:
    """Print the status of available solvers."""
    print("\nSolver Status:")
    print("-------------")
    
    for solver, available in solver_status.items():
        status = "✅ Available" if available else "❌ Not available"
        print(f"{solver}: {status}")

def install_solver(solver_name: str) -> bool:
    """
    Install the specified solver.
    
    Args:
        solver_name: Name of the solver to install
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    system = platform.system()
    
    # Installation instructions by solver and platform
    instructions: Dict[str, Dict[str, Tuple[List[str], str]]] = {
        "GLPK_CMD": {
            "Linux": (
                ["sudo apt-get install -y glpk-utils"], 
                "GLPK should now be installed."
            ),
            "Darwin": (
                ["brew install glpk"], 
                "GLPK should now be installed."
            ),
            "Windows": (
                [], 
                "Manual installation required. Please visit https://winglpk.sourceforge.net/ to download and install GLPK."
            )
        },
        "COIN_CMD": {
            "Linux": (
                ["sudo apt-get install -y coinor-cbc"], 
                "COIN-OR CBC should now be installed."
            ),
            "Darwin": (
                ["brew install cbc"], 
                "COIN-OR CBC should now be installed."
            ),
            "Windows": (
                [], 
                "Manual installation required. Please visit https://github.com/coin-or/Cbc to download and install CBC."
            )
        },
        "COINMP_DLL": {
            "Linux": (
                ["pip install coinmp"], 
                "COINMP_DLL should now be installed."
            ),
            "Darwin": (
                ["pip install coinmp"], 
                "COINMP_DLL should now be installed."
            ),
            "Windows": (
                ["pip install coinmp"], 
                "COINMP_DLL should now be installed."
            )
        },
        "SCIP_CMD": {
            "Linux": (
                ["sudo apt-get install -y scip"], 
                "SCIP should now be installed."
            ),
            "Darwin": (
                ["brew install scip"], 
                "SCIP should now be installed."
            ),
            "Windows": (
                [], 
                "Manual installation required. Please visit https://www.scipopt.org/index.php#download to download and install SCIP."
            )
        },
        "CHOCO_CMD": {
            "all": (
                ["pip install choco"], 
                "Choco-solver is a Java-based solver. Please visit https://choco-solver.org/ for more information on how to install and configure it for your system."
            )
        },
        "MIPCL_CMD": {
            "all": (
                [], 
                "MIPCL requires manual installation. Please visit http://mipcl-cpp.appspot.com/ for more information."
            )
        },
        "HiGHS_CMD": {
            "Linux": (
                ["pip install highspy"], 
                "HiGHS should now be installed."
            ),
            "Darwin": (
                ["pip install highspy"], 
                "HiGHS should now be installed."
            ),
            "Windows": (
                ["pip install highspy"], 
                "HiGHS should now be installed."
            )
        },
    }
    
    print(f"\nInstalling {solver_name}...")
    
    # Check if solver is in our instructions
    if solver_name not in instructions:
        print(f"❌ No installation instructions available for {solver_name}.")
        return False
    
    # Get platform-specific instructions or fallback to 'all'
    if system in instructions[solver_name]:
        commands, message = instructions[solver_name][system]
    elif "all" in instructions[solver_name]:
        commands, message = instructions[solver_name]["all"]
    else:
        print(f"❌ No installation instructions available for {solver_name} on {system}.")
        return False
    
    # Run the commands
    for cmd in commands:
        print(f"Running: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            return False
    
    print(message)
    return True

def main():
    """Main function."""
    print("=== Waffle Production Optimization Solver Installer ===")
    
    # Check PuLP installation
    if not check_pulp_installation():
        install_pulp = input("Would you like to install PuLP? (y/n): ")
        if install_pulp.lower() == 'y':
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pulp"], check=True)
                print("✅ PuLP installed successfully.")
            except subprocess.CalledProcessError:
                print("❌ Failed to install PuLP.")
                return
        else:
            print("PuLP is required for solver management. Exiting.")
            return
    
    # Check available solvers
    solver_status = check_available_solvers()
    print_solver_status(solver_status)
    
    # Install additional solvers if needed
    install_more = input("\nWould you like to install additional solvers? (y/n): ")
    if install_more.lower() == 'y':
        # Create a list of unavailable solvers
        unavailable_solvers = [solver for solver, available in solver_status.items() if not available]
        
        if not unavailable_solvers:
            print("All solvers are already available!")
            return
        
        print("\nUnavailable solvers:")
        for i, solver in enumerate(unavailable_solvers):
            print(f"{i+1}. {solver}")
        
        selection = input("\nEnter the numbers of the solvers you want to install (comma-separated, or 'all'): ")
        
        if selection.lower() == 'all':
            solvers_to_install = unavailable_solvers
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                solvers_to_install = [unavailable_solvers[i] for i in indices if 0 <= i < len(unavailable_solvers)]
            except (ValueError, IndexError):
                print("Invalid selection.")
                return
        
        for solver in solvers_to_install:
            install_solver(solver)
        
        # Check availability again
        print("\nUpdated solver status:")
        updated_status = check_available_solvers()
        print_solver_status(updated_status)
    
    print("\nSolver installation process completed.")

if __name__ == "__main__":
    main()
