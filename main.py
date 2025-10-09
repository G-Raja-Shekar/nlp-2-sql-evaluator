"""
Main entry point for running SQL evaluations.
"""

import json
from typing import List, Dict, Any
from sql_evaluator import SQLEvaluator, BatchEvaluator
from sql_evaluator.models import EvaluationRequest, CustomEvaluationRequest
from sql_evaluator.exporters import ExcelExporter
from sql_evaluator.utils import SimilarityCalculator


def run_batch_evaluation_from_test_data():
    """
    Run batch evaluation using test data and export results to Excel.
    """
    # Import test data
    try:
        from test_data import BATCH_EVALUATIONS
    except ImportError:
        print("❌ Error: Could not import BATCH_EVALUATIONS from test_data.py")
        print("Make sure test_data.py exists and contains BATCH_EVALUATIONS list")
        return
    
    print("🚀 Starting Batch SQL Evaluation from Test Data")
    print("=" * 60)
    
    # Initialize batch evaluator
    batch_evaluator = BatchEvaluator()
    
    # Run batch evaluation
    results = batch_evaluator.evaluate_batch(BATCH_EVALUATIONS)
    
    # Print summary
    batch_evaluator.print_batch_summary(results)
    
    # Export to Excel
    exporter = ExcelExporter()
    excel_filename = exporter.export(results)
    
    if excel_filename:
        print(f"\n✅ Batch evaluation completed successfully!")
        print(f"📊 Results exported to: {excel_filename}")
    
    return results


def demonstrate_evaluations():
    """
    Demonstrate various evaluation scenarios.
    """
    evaluator = SQLEvaluator()
    
    # SQL query constants
    SEEKERS_QUERY = "SELECT COUNT(*) FROM seekers WHERE placement_status = 'Placed';"
    
    print("🚀 Advanced SQL Evaluator Demo")
    print("=" * 60)
    
    # Test Case 1: Perfect SQL match
    print("\n📊 Test Case 1: Perfect SQL Match")
    request1 = EvaluationRequest(
        input_query="How many seekers are placed?",
        expected_output=SEEKERS_QUERY,
        model_output=SEEKERS_QUERY,
        session_id="demo_session_1",
        metadata={"model": "gpt-4", "temperature": 0.0}
    )
    result1 = evaluator.evaluate_sql_semantic_equivalence(request1)
    print(f"Score: {result1.score:.2f} | Passed: {result1.passed}")
    print(f"Analysis: {json.dumps(result1.details['analysis'], indent=2)}")
    
    # Test Case 2: Slightly different SQL (different formatting)
    print("\n📊 Test Case 2: Different Formatting")
    request2 = EvaluationRequest(
        input_query="Count placed seekers",
        expected_output=SEEKERS_QUERY,
        model_output="select count(*) from seekers where placement_status='Placed'",
        session_id="demo_session_1",
        metadata={"model": "gpt-3.5", "temperature": 0.3}
    )
    result2 = evaluator.evaluate_sql_semantic_equivalence(request2)
    print(f"Score: {result2.score:.2f} | Passed: {result2.passed}")
    print(f"Analysis: {json.dumps(result2.details['analysis'], indent=2)}")
    
    # Test Case 3: Semantically similar but different structure
    print("\n📊 Test Case 3: Different Structure")
    request3 = EvaluationRequest(
        input_query="Get all active users",
        expected_output="SELECT * FROM users WHERE status = 'active';",
        model_output="SELECT user_id, name, email FROM users WHERE status = 'active';",
        session_id="demo_session_2",
        metadata={"model": "claude-3", "temperature": 0.5}
    )
    result3 = evaluator.evaluate_sql_semantic_equivalence(request3)
    print(f"Score: {result3.score:.2f} | Passed: {result3.passed}")
    print(f"Analysis: {json.dumps(result3.details['analysis'], indent=2)}")
    
    # Test Case 4: Completely different SQL
    print("\n📊 Test Case 4: Completely Different")
    request4 = EvaluationRequest(
        input_query="Find user names",
        expected_output="SELECT name FROM users;",
        model_output="SELECT COUNT(*) FROM products;",
        session_id="demo_session_2",
        metadata={"model": "gpt-4", "temperature": 0.8}
    )
    result4 = evaluator.evaluate_sql_semantic_equivalence(request4)
    print(f"Score: {result4.score:.2f} | Passed: {result4.passed}")
    print(f"Analysis: {json.dumps(result4.details['analysis'], indent=2)}")
    
    # Test Case 5: Custom Text Similarity Evaluator
    print("\n📊 Test Case 5: Custom Text Evaluator")
    def advanced_text_similarity(expected, actual):
        return SimilarityCalculator.advanced_text_similarity(expected, actual)
    
    custom_request = CustomEvaluationRequest(
        evaluator_name="Advanced Text Similarity",
        input_data="Explain the benefits of regular exercise",
        expected_output="Regular exercise improves cardiovascular health, builds muscle strength, and enhances mental wellbeing",
        model_output="Exercise helps improve heart health, increases muscle strength, and boosts mental wellness",
        evaluation_function=advanced_text_similarity,
        session_id="demo_session_3",
        metadata={"model": "gpt-4", "evaluation_method": "advanced_similarity"}
    )
    result5 = evaluator.evaluate_custom(custom_request)
    print(f"Score: {result5.score:.2f} | Passed: {result5.passed}")
    
    # Test Case 6: Exact Match Evaluator
    print("\n📊 Test Case 6: Exact Match Evaluator")
    exact_match_request = CustomEvaluationRequest(
        evaluator_name="Exact Match",
        input_data="What is 2 + 2?",
        expected_output="4",
        model_output="4",
        evaluation_function=lambda exp, act: 1.0 if exp.strip() == act.strip() else 0.0,
        session_id="demo_session_3"
    )
    result6 = evaluator.evaluate_custom(exact_match_request)
    print(f"Score: {result6.score:.2f} | Passed: {result6.passed}")
    
    # Display comprehensive summary
    print("\n" + "=" * 60)
    print("📈 EVALUATION SUMMARY")
    print("=" * 60)
    
    summary = evaluator.get_evaluation_summary()
    print(f"Total Evaluations: {summary['total_evaluations']}")
    print(f"Passed Evaluations: {summary['passed_evaluations']}")
    print(f"Overall Pass Rate: {summary['pass_rate']:.1%}")
    print(f"Average Score: {summary['average_score']:.2f}")
    
    print("\n📊 By Evaluation Type:")
    for eval_type, stats in summary['evaluation_types'].items():
        print(f"  {eval_type}:")
        print(f"    Count: {stats['count']}")
        print(f"    Pass Rate: {stats['pass_rate']:.1%}")
        print(f"    Avg Score: {stats['average_score']:.2f}")
    
    return summary


if __name__ == "__main__":
    # Choose which demo to run
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demonstrate_evaluations()
    else:
        # Run batch evaluation from test data by default
        run_batch_evaluation_from_test_data()
