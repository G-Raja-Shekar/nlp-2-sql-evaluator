"""
Base exporter interface.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.evaluation_result import EvaluationResult


class BaseExporter(ABC):
    """
    Abstract base class for result exporters.
    """
    
    @abstractmethod
    def export(self, results: List[EvaluationResult], filename: Optional[str] = None) -> str:
        """
        Export evaluation results to a file.
        
        Args:
            results: List of evaluation results
            filename: Optional filename for export
            
        Returns:
            Path to the exported file
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get the file extension for this exporter.
        
        Returns:
            File extension (e.g., '.xlsx', '.json')
        """
        pass
    
    def _prepare_export_data(self, results: List[EvaluationResult]) -> List[Dict[str, Any]]:
        """
        Prepare data for export by converting results to dictionaries.
        
        Args:
            results: List of evaluation results
            
        Returns:
            List of dictionaries ready for export
        """
        return [result.to_dict() for result in results]
