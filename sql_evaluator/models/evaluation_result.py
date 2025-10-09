"""
Data models for evaluation results and requests.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class EvaluationResult:
    """
    Represents the result of an evaluation.
    """
    evaluation_type: str
    score: float
    passed: bool
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        return {
            "evaluation_type": self.evaluation_type,
            "score": self.score,
            "passed": self.passed,
            "session_id": self.session_id,
            "metadata": self.metadata or {},
            "details": self.details or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationResult':
        """Create an EvaluationResult from a dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            evaluation_type=data["evaluation_type"],
            score=data["score"],
            passed=data["passed"],
            session_id=data.get("session_id"),
            metadata=data.get("metadata"),
            details=data.get("details"),
            timestamp=timestamp
        )
