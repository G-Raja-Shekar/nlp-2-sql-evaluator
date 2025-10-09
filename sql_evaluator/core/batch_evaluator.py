"""
Batch evaluation functionality.
"""

from typing import List, Dict, Any, Optional
from ..models.evaluation_result import EvaluationResult
from ..models.evaluation_request import BatchEvaluationItem, EvaluationRequest
from .evaluator import SQLEvaluator


class BatchEvaluator:
    """
    Handles batch evaluation of SQL queries.
    """
    
    def __init__(self, passing_threshold: float = 0.8):
        """
        Initialize the batch evaluator.
        
        Args:
            passing_threshold: Minimum score for evaluation to pass
        """
        self.evaluator = SQLEvaluator(passing_threshold)
    
    def evaluate_batch(self, evaluations: List[Dict[str, Any]]) -> List[EvaluationResult]:
        """
        Perform batch evaluation of SQL queries from test data.
        
        Args:
            evaluations: List of evaluation dictionaries with keys:
                - natural_query: The natural language question
                - expected_sql: The expected/golden SQL query
                - generated_sql: The generated SQL query to evaluate
                - session_id: Optional session ID for grouping
                - metadata: Optional additional metadata
        
        Returns:
            List of evaluation results
        """
        if not evaluations:
            print("⚠️  No evaluations provided.")
            return []
        
        print(f"🚀 Starting batch evaluation of {len(evaluations)} SQL queries...")
        print("=" * 70)
        
        results = []
        
        for i, eval_data in enumerate(evaluations, 1):
            try:
                # Create evaluation request
                request = EvaluationRequest(
                    input_query=eval_data.get('natural_query', ''),
                    expected_output=eval_data.get('expected_sql', ''),
                    model_output=eval_data.get('generated_sql', ''),
                    session_id=eval_data.get('session_id'),
                    metadata=eval_data.get('metadata', {})
                )
                
                # Perform evaluation
                result = self.evaluator.evaluate_sql_semantic_equivalence(request)
                results.append(result)
                
                # Print progress
                status_icon = "✅" if result.passed else "❌"
                print(f"{status_icon} [{i:3d}/{len(evaluations)}] "
                      f"Score: {result.score:.3f} | "
                      f"Query: {eval_data.get('natural_query', 'N/A')[:50]}...")
                
            except Exception as e:
                print(f"❌ [{i:3d}/{len(evaluations)}] Error processing evaluation: {str(e)}")
                # Create a failed result
                failed_result = EvaluationResult(
                    evaluation_type="SQL Semantic Equivalence",
                    score=0.0,
                    passed=False,
                    session_id=eval_data.get('session_id'),
                    metadata=eval_data.get('metadata', {}),
                    details={
                        "error": str(e),
                        "input": eval_data.get('natural_query', ''),
                        "expected": eval_data.get('expected_sql', ''),
                        "actual": eval_data.get('generated_sql', '')
                    }
                )
                results.append(failed_result)
        
        return results
    
    def evaluate_batch_items(self, items: List[BatchEvaluationItem]) -> List[EvaluationResult]:
        """
        Evaluate a list of BatchEvaluationItem objects.
        
        Args:
            items: List of BatchEvaluationItem objects
            
        Returns:
            List of evaluation results
        """
        # Convert items to dictionaries
        evaluations = []
        for item in items:
            evaluations.append({
                'natural_query': item.natural_query,
                'expected_sql': item.expected_sql,
                'generated_sql': item.generated_sql,
                'session_id': item.session_id,
                'metadata': item.metadata
            })
        
        return self.evaluate_batch(evaluations)
    
    def print_batch_summary(self, results: List[EvaluationResult]) -> None:
        """
        Print a comprehensive summary of batch evaluation results.
        
        Args:
            results: List of evaluation results
        """
        if not results:
            print("No results to summarize.")
            return
        
        print("\n" + "=" * 70)
        print("📈 BATCH EVALUATION SUMMARY")
        print("=" * 70)
        
        total_evaluations = len(results)
        passed_evaluations = sum(1 for r in results if r.passed)
        failed_evaluations = total_evaluations - passed_evaluations
        
        total_score = sum(r.score for r in results)
        average_score = total_score / total_evaluations
        
        print(f"📊 Total Evaluations: {total_evaluations}")
        print(f"✅ Passed: {passed_evaluations}")
        print(f"❌ Failed: {failed_evaluations}")
        print(f"📈 Pass Rate: {passed_evaluations/total_evaluations:.1%}")
        print(f"⭐ Average Score: {average_score:.3f}")
        
        # Score distribution
        score_ranges = {
            "Excellent (0.9-1.0)": sum(1 for r in results if 0.9 <= r.score <= 1.0),
            "Good (0.8-0.9)": sum(1 for r in results if 0.8 <= r.score < 0.9),
            "Fair (0.6-0.8)": sum(1 for r in results if 0.6 <= r.score < 0.8),
            "Poor (0.0-0.6)": sum(1 for r in results if 0.0 <= r.score < 0.6)
        }
        
        print(f"\n📊 Score Distribution:")
        for range_name, count in score_ranges.items():
            percentage = count / total_evaluations * 100
            print(f"   {range_name}: {count} ({percentage:.1f}%)")
        
        # Show top failures if any
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            print(f"\n❌ Top Failed Evaluations:")
            # Sort by score (ascending) to show worst first
            failed_results.sort(key=lambda x: x.score)
            
            for i, result in enumerate(failed_results[:5], 1):
                input_query = result.details.get('input', 'N/A')[:40]
                print(f"   {i}. Score: {result.score:.3f} | Query: {input_query}...")
        
        print("=" * 70)
    
    def get_summary_statistics(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Get detailed summary statistics.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {}
        
        total_evaluations = len(results)
        passed_evaluations = sum(1 for r in results if r.passed)
        total_score = sum(r.score for r in results)
        
        return {
            'total_evaluations': total_evaluations,
            'passed_evaluations': passed_evaluations,
            'failed_evaluations': total_evaluations - passed_evaluations,
            'pass_rate': passed_evaluations / total_evaluations,
            'average_score': total_score / total_evaluations,
            'min_score': min(r.score for r in results),
            'max_score': max(r.score for r in results),
            'score_distribution': {
                'excellent': sum(1 for r in results if 0.9 <= r.score <= 1.0),
                'good': sum(1 for r in results if 0.8 <= r.score < 0.9),
                'fair': sum(1 for r in results if 0.6 <= r.score < 0.8),
                'poor': sum(1 for r in results if 0.0 <= r.score < 0.6)
            }
        }
