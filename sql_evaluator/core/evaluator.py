"""
Core SQL evaluation logic.
"""

from typing import Dict, Any, Optional, List, Callable
from ..models.evaluation_result import EvaluationResult
from ..models.evaluation_request import EvaluationRequest, CustomEvaluationRequest
from ..sql.normalizer import SQLNormalizer
from ..sql.parser import SQLParser
from ..utils.similarity import SimilarityCalculator


class SQLEvaluator:
    """
    Core SQL semantic equivalence evaluator.
    """
    
    def __init__(self, passing_threshold: float = 0.8):
        """
        Initialize the evaluator.
        
        Args:
            passing_threshold: Minimum score for evaluation to pass
        """
        self.passing_threshold = passing_threshold
        self.evaluation_results: List[EvaluationResult] = []
        self.normalizer = SQLNormalizer()
        self.parser = SQLParser()
        self.similarity = SimilarityCalculator()
    
    def evaluate_sql_semantic_equivalence(self, request: EvaluationRequest) -> EvaluationResult:
        """
        Evaluate SQL semantic equivalence between expected and model output.
        
        Args:
            request: Evaluation request containing input and expected/actual outputs
            
        Returns:
            EvaluationResult with score and analysis
        """
        # Calculate SQL equivalence score
        equivalence_score = self._calculate_sql_equivalence(
            request.expected_output, 
            request.model_output
        )
        
        # Create evaluation result
        result = EvaluationResult(
            evaluation_type=request.evaluation_type,
            score=equivalence_score,
            passed=equivalence_score >= self.passing_threshold,
            session_id=request.session_id,
            metadata=request.metadata,
            details={
                "input": request.input_query,
                "expected": request.expected_output,
                "actual": request.model_output,
                "equivalence_score": equivalence_score,
                "analysis": self._analyze_sql_differences(
                    request.expected_output, 
                    request.model_output
                )
            }
        )
        
        # Store result
        self.evaluation_results.append(result)
        
        return result
    
    def evaluate_custom(self, request: CustomEvaluationRequest) -> EvaluationResult:
        """
        Generic evaluator that accepts a custom evaluation function.
        
        Args:
            request: Custom evaluation request
            
        Returns:
            EvaluationResult with custom evaluation score
        """
        # Run custom evaluation function
        score = request.evaluation_function(request.expected_output, request.model_output)
        
        result = EvaluationResult(
            evaluation_type=request.evaluator_name,
            score=score,
            passed=score >= self.passing_threshold,
            session_id=request.session_id,
            metadata=request.metadata,
            details={
                "evaluator": request.evaluator_name,
                "input": request.input_data,
                "expected": request.expected_output,
                "actual": request.model_output,
                "score": score
            }
        )
        
        # Store result
        self.evaluation_results.append(result)
        
        return result
    
    def _calculate_sql_equivalence(self, expected: str, actual: str) -> float:
        """
        Calculate SQL semantic equivalence with improved logic.
        
        Args:
            expected: Expected SQL query
            actual: Actual SQL query
            
        Returns:
            Equivalence score between 0.0 and 1.0
        """
        # Normalize SQL strings
        expected_normalized = self.normalizer.normalize(expected)
        actual_normalized = self.normalizer.normalize(actual)
        
        # Exact match gets perfect score
        if expected_normalized == actual_normalized:
            return 1.0
        
        # Parse SQL components for better comparison
        expected_components = self.parser.parse_components(expected_normalized)
        actual_components = self.parser.parse_components(actual_normalized)
        
        # Calculate component-wise similarity
        similarity_scores = []
        
        # Check SELECT clause (weighted heavily)
        if expected_components['select'] and actual_components['select']:
            select_sim = self.similarity.component_similarity(
                expected_components['select'], 
                actual_components['select']
            )
            similarity_scores.append(select_sim * 0.4)  # 40% weight
        
        # Check FROM clause (high importance)
        if expected_components['from'] and actual_components['from']:
            from_sim = self.similarity.component_similarity(
                expected_components['from'], 
                actual_components['from']
            )
            similarity_scores.append(from_sim * 0.3)  # 30% weight
        
        # Check WHERE clause (medium importance)
        if expected_components['where'] and actual_components['where']:
            where_sim = self.similarity.component_similarity(
                expected_components['where'], 
                actual_components['where']
            )
            similarity_scores.append(where_sim * 0.2)  # 20% weight
        elif not expected_components['where'] and not actual_components['where']:
            similarity_scores.append(0.2)  # Both have no WHERE clause
        
        # Check ORDER BY clause (lower importance)
        if expected_components['order_by'] and actual_components['order_by']:
            order_sim = self.similarity.component_similarity(
                expected_components['order_by'], 
                actual_components['order_by']
            )
            similarity_scores.append(order_sim * 0.1)  # 10% weight
        elif not expected_components['order_by'] and not actual_components['order_by']:
            similarity_scores.append(0.1)  # Both have no ORDER BY clause
        
        return min(sum(similarity_scores), 1.0) if similarity_scores else 0.0
    
    def _analyze_sql_differences(self, expected: str, actual: str) -> Dict[str, Any]:
        """
        Analyze differences between expected and actual SQL.
        
        Args:
            expected: Expected SQL query
            actual: Actual SQL query
            
        Returns:
            Analysis of differences
        """
        expected_norm = self.normalizer.normalize(expected)
        actual_norm = self.normalizer.normalize(actual)
        
        expected_comp = self.parser.parse_components(expected_norm)
        actual_comp = self.parser.parse_components(actual_norm)
        
        differences = {}
        
        for component in ['select', 'from', 'where', 'order_by', 'group_by']:
            exp_comp = expected_comp.get(component, '')
            act_comp = actual_comp.get(component, '')
            
            if exp_comp != act_comp:
                differences[component] = {
                    'expected': exp_comp,
                    'actual': act_comp,
                    'similarity': self.similarity.component_similarity(exp_comp, act_comp)
                }
        
        return {
            'has_differences': len(differences) > 0,
            'differences': differences,
            'exact_match': expected_norm == actual_norm,
            'expected_tables': self.parser.extract_tables(expected_norm),
            'actual_tables': self.parser.extract_tables(actual_norm),
            'expected_columns': self.parser.extract_columns(expected_norm),
            'actual_columns': self.parser.extract_columns(actual_norm)
        }
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of all evaluations.
        
        Returns:
            Summary statistics
        """
        if not self.evaluation_results:
            return {
                'total_evaluations': 0,
                'passed_evaluations': 0,
                'pass_rate': 0.0,
                'average_score': 0.0,
                'evaluation_types': {}
            }
        
        total_evaluations = len(self.evaluation_results)
        passed_evaluations = sum(1 for r in self.evaluation_results if r.passed)
        total_score = sum(r.score for r in self.evaluation_results)
        
        # Group by evaluation type
        evaluation_types = {}
        for result in self.evaluation_results:
            eval_type = result.evaluation_type
            if eval_type not in evaluation_types:
                evaluation_types[eval_type] = {
                    'count': 0,
                    'passed': 0,
                    'total_score': 0.0
                }
            
            evaluation_types[eval_type]['count'] += 1
            evaluation_types[eval_type]['total_score'] += result.score
            if result.passed:
                evaluation_types[eval_type]['passed'] += 1
        
        # Calculate averages for each type
        for eval_type in evaluation_types:
            stats = evaluation_types[eval_type]
            stats['pass_rate'] = stats['passed'] / stats['count']
            stats['average_score'] = stats['total_score'] / stats['count']
        
        return {
            'total_evaluations': total_evaluations,
            'passed_evaluations': passed_evaluations,
            'pass_rate': passed_evaluations / total_evaluations,
            'average_score': total_score / total_evaluations,
            'evaluation_types': evaluation_types
        }
    
    def clear_results(self):
        """Clear all stored evaluation results."""
        self.evaluation_results.clear()
