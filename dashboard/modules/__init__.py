"""
Dashboard modules - Module-specific implementations.

Each module corresponds to one of the 10 dashboard pages:
1. overview.py - Module 1: Overview
2. data_explorer.py - Module 2: Data Explorer
3. promotion_effectiveness.py - Module 3: Promotion Effectiveness
4. price_elasticity.py - Module 4: Price Elasticity
5. scenario_simulator.py - Module 5: Scenario Simulator
6. demand_forecasting.py - Module 6: Demand Forecasting
7. promotion_lift_model.py - Module 7: Promotion Lift Model
8. chat_interface.py - Module 8: Chat Interface
9. critical_reflection.py - Module 9: Critical Reflection
10. appendix_export.py - Module 10: Appendix & Export
"""

# Implemented modules. Modules 4 (price_elasticity) & 5 (scenario_simulator)
# are still pending (require the elasticity model to be built first).

__all__ = [
    "overview",                 # Module 1
    "data_explorer",            # Module 2
    "promotion_effectiveness",  # Module 3
    "demand_forecasting",       # Module 6
    "promotion_lift_model",     # Module 7
    "chat_interface",           # Module 8
    "critical_reflection",      # Module 9
    "appendix_export",          # Module 10
]
