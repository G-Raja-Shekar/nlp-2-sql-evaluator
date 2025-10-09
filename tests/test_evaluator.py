"""
Test cases for the SQL evaluator.
"""

import unittest
from sql_evaluator import SQLEvaluator
from sql_evaluator.models import EvaluationRequest


class TestSQLEvaluator(unittest.TestCase):
    """Test cases for SQL evaluator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = SQLEvaluator()
    
    def test_perfect_match(self):
        """Test evaluation with perfect SQL match."""
        request = EvaluationRequest(
            input_query="Count all users",
            expected_output="SELECT COUNT(*) FROM users;",
            model_output="SELECT COUNT(*) FROM users;",
            session_id="test_session"
        )
        
        result = self.evaluator.evaluate_sql_semantic_equivalence(request)
        
        self.assertEqual(result.score, 1.0)
        self.assertTrue(result.passed)
        self.assertEqual(result.evaluation_type, "SQL Semantic Equivalence")
    
    def test_formatting_differences(self):
        """Test evaluation with different formatting."""
        request = EvaluationRequest(
            input_query="Count all users",
            expected_output="SELECT COUNT(*) FROM users;",
            model_output="select count(*) from users",
            session_id="test_session"
        )
        
        result = self.evaluator.evaluate_sql_semantic_equivalence(request)
        
        # Should have high score due to semantic equivalence
        self.assertGreater(result.score, 0.8)
        self.assertTrue(result.passed)
    
    def test_completely_different_queries(self):
        """Test evaluation with completely different queries."""
        request = EvaluationRequest(
            input_query="Count users",
            expected_output="SELECT COUNT(*) FROM users;",
            model_output="SELECT name FROM products;",
            session_id="test_session"
        )
        
        result = self.evaluator.evaluate_sql_semantic_equivalence(request)
        
        # Should have low score due to different semantics
        self.assertLess(result.score, 0.5)
        self.assertFalse(result.passed)
    
    def test_custom_threshold(self):
        """Test evaluator with custom passing threshold."""
        evaluator = SQLEvaluator(passing_threshold=0.9)
        
        request = EvaluationRequest(
            input_query="Count users",
            expected_output="SELECT COUNT(*) FROM users;",
            model_output="select count(*) from users",  # Slight formatting difference
            session_id="test_session"
        )
        
        result = evaluator.evaluate_sql_semantic_equivalence(request)
        
        # With higher threshold, this might not pass
        if result.score < 0.9:
            self.assertFalse(result.passed)
        else:
            self.assertTrue(result.passed)


if __name__ == '__main__':
    unittest.main()
