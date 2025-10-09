"""
SQL Evaluator - A modular SQL semantic equivalence evaluation library.

This package provides tools for evaluating SQL queries for semantic equivalence,
batch processing, and exporting results in various formats.
"""

# Import main classes for easy access
try:
    from .core.evaluator import SQLEvaluator
    from .core.batch_evaluator import BatchEvaluator
    from .models.evaluation_result import EvaluationResult
    from .models.evaluation_request import EvaluationRequest
except ImportError:
    # During initial setup, modules might not be fully available
    pass

__version__ = "1.0.0"
__author__ = "Your Name"

# Only export if imports succeeded
import sys
current_module = sys.modules[__name__]
if hasattr(current_module, 'SQLEvaluator'):
    __all__ = [
        "SQLEvaluator",
        "BatchEvaluator", 
        "EvaluationResult",
        "EvaluationRequest"
    ]
else:
    __all__ = []
