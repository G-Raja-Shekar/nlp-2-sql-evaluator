"""
Data models for evaluation requests.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable


@dataclass
class EvaluationRequest:
    """
    Represents a request for evaluation.
    """
    input_query: str
    expected_output: str
    model_output: str
    evaluation_type: str = "SQL Semantic Equivalence"
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the request to a dictionary."""
        return {
            "input_query": self.input_query,
            "expected_output": self.expected_output,
            "model_output": self.model_output,
            "evaluation_type": self.evaluation_type,
            "session_id": self.session_id,
            "metadata": self.metadata or {}
        }


@dataclass 
class CustomEvaluationRequest:
    """
    Represents a custom evaluation request with a custom evaluation function.
    """
    evaluator_name: str
    input_data: str
    expected_output: str
    model_output: str
    evaluation_function: Callable[[str, str], float]
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the request to a dictionary (excluding the function)."""
        return {
            "evaluator_name": self.evaluator_name,
            "input_data": self.input_data,
            "expected_output": self.expected_output,
            "model_output": self.model_output,
            "session_id": self.session_id,
            "metadata": self.metadata or {}
        }


@dataclass
class BatchEvaluationItem:
    """
    Represents a single item in a batch evaluation.
    """
    natural_query: str
    expected_sql: str
    generated_sql: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_evaluation_request(self) -> EvaluationRequest:
        """Convert to an EvaluationRequest."""
        return EvaluationRequest(
            input_query=self.natural_query,
            expected_output=self.expected_sql,
            model_output=self.generated_sql,
            session_id=self.session_id,
            metadata=self.metadata
        )
