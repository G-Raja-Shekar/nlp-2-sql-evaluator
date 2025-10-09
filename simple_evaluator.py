import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()


class SimpleEvaluator:
    """
    A simple evaluator for SQL semantic equivalence and other evaluation tasks.
    This version focuses on evaluation logic without complex Langfuse integration.
    """
    
    def __init__(self):
        self.evaluation_results = []
    
    def evaluate_sql_semantic_equivalence(
        self,
        input_query: str,
        expected_output: str,
        model_output: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate SQL semantic equivalence between expected and model output.
        """
        # Perform SQL equivalence check
        equivalence_score = self._calculate_sql_equivalence(expected_output, model_output)
        
        # Create evaluation result
        evaluation_result = {
            "evaluation_type": "SQL Semantic Equivalence",
            "score": equivalence_score,
            "passed": equivalence_score >= 0.8,
            "session_id": session_id,
            "metadata": metadata or {},
            "details": {
                "input": input_query,
                "expected": expected_output,
                "actual": model_output,
                "equivalence_score": equivalence_score,
                "analysis": self._analyze_sql_differences(expected_output, model_output)
            }
        }
        
        # Store result
        self.evaluation_results.append(evaluation_result)
        
        return evaluation_result
    
    def evaluate_custom(
        self,
        evaluator_name: str,
        input_data: str,
        expected_output: str,
        model_output: str,
        evaluation_function: callable,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generic evaluator that accepts a custom evaluation function.
        """
        # Run custom evaluation
        score = evaluation_function(expected_output, model_output)
        
        evaluation_result = {
            "evaluation_type": evaluator_name,
            "score": score,
            "passed": score >= 0.8,
            "session_id": session_id,
            "metadata": metadata or {},
            "details": {
                "evaluator": evaluator_name,
                "input": input_data,
                "expected": expected_output,
                "actual": model_output,
                "score": score
            }
        }
        
        # Store result
        self.evaluation_results.append(evaluation_result)
        
        return evaluation_result
    
    def _calculate_sql_equivalence(self, expected: str, actual: str) -> float:
        """
        Calculate SQL semantic equivalence with improved logic.
        """
        # Normalize SQL strings
        expected_normalized = self._normalize_sql(expected)
        actual_normalized = self._normalize_sql(actual)
        
        # Exact match gets perfect score
        if expected_normalized == actual_normalized:
            return 1.0
        
        # Parse SQL components for better comparison
        expected_components = self._parse_sql_components(expected_normalized)
        actual_components = self._parse_sql_components(actual_normalized)
        
        # Calculate component-wise similarity
        similarity_scores = []
        
        # Check SELECT clause
        if expected_components['select'] and actual_components['select']:
            select_sim = self._calculate_component_similarity(
                expected_components['select'], actual_components['select']
            )
            similarity_scores.append(select_sim * 0.3)  # 30% weight
        
        # Check FROM clause
        if expected_components['from'] and actual_components['from']:
            from_sim = self._calculate_component_similarity(
                expected_components['from'], actual_components['from']
            )
            similarity_scores.append(from_sim * 0.3)  # 30% weight
        
        # Check WHERE clause
        if expected_components['where'] and actual_components['where']:
            where_sim = self._calculate_component_similarity(
                expected_components['where'], actual_components['where']
            )
            similarity_scores.append(where_sim * 0.4)  # 40% weight
        elif not expected_components['where'] and not actual_components['where']:
            similarity_scores.append(0.4)  # Both have no WHERE clause
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _normalize_sql(self, sql: str) -> str:
        """
        Normalize SQL string for comparison.
        """
        # Remove extra whitespace and convert to lowercase
        normalized = " ".join(sql.strip().lower().split())
        
        # Remove semicolon at the end if present
        if normalized.endswith(";"):
            normalized = normalized[:-1]
        
        return normalized
    
    def _parse_sql_components(self, sql: str) -> Dict[str, str]:
        """
        Parse SQL into components (SELECT, FROM, WHERE, etc.)
        """
        components = {
            'select': '',
            'from': '',
            'where': '',
            'order_by': '',
            'group_by': ''
        }
        
        # Simple parsing (in production, use a proper SQL parser)
        sql_upper = sql.upper()
        
        # Find SELECT clause
        select_start = sql_upper.find('SELECT')
        if select_start != -1:
            from_start = sql_upper.find('FROM', select_start)
            if from_start != -1:
                components['select'] = sql[select_start:from_start].strip()
                
                # Find FROM clause
                where_start = sql_upper.find('WHERE', from_start)
                order_start = sql_upper.find('ORDER BY', from_start)
                group_start = sql_upper.find('GROUP BY', from_start)
                
                # Find the earliest next clause
                next_clause = min([pos for pos in [where_start, order_start, group_start] if pos != -1] or [len(sql)])
                
                components['from'] = sql[from_start:next_clause].strip()
                
                # Find WHERE clause
                if where_start != -1:
                    order_start = sql_upper.find('ORDER BY', where_start)
                    group_start = sql_upper.find('GROUP BY', where_start)
                    
                    # Find the earliest next clause after WHERE
                    next_clause_after_where = min([pos for pos in [order_start, group_start] if pos != -1] or [len(sql)])
                    
                    components['where'] = sql[where_start:next_clause_after_where].strip()
                    where_end = min([pos for pos in [order_start, group_start] if pos > where_start and pos != -1] or [len(sql)])
                    components['where'] = sql[where_start:where_end].strip()
        
        return components
    
    def _calculate_component_similarity(self, comp1: str, comp2: str) -> float:
        """
        Calculate similarity between SQL components.
        """
        words1 = set(comp1.lower().split())
        words2 = set(comp2.lower().split())
        
        if len(words1) == 0 and len(words2) == 0:
            return 1.0
        
        if len(words1) == 0 or len(words2) == 0:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if len(union) > 0 else 0.0
    
    def _analyze_sql_differences(self, expected: str, actual: str) -> Dict[str, Any]:
        """
        Analyze differences between expected and actual SQL.
        """
        expected_norm = self._normalize_sql(expected)
        actual_norm = self._normalize_sql(actual)
        
        expected_comp = self._parse_sql_components(expected_norm)
        actual_comp = self._parse_sql_components(actual_norm)
        
        differences = {}
        
        for component in ['select', 'from', 'where']:
            if expected_comp[component] != actual_comp[component]:
                differences[component] = {
                    'expected': expected_comp[component],
                    'actual': actual_comp[component]
                }
        
        return {
            'has_differences': len(differences) > 0,
            'differences': differences,
            'exact_match': expected_norm == actual_norm
        }
    
    def batch_evaluate_sql(
        self,
        evaluations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
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
            return []
        
        print(f"🚀 Starting batch evaluation of {len(evaluations)} SQL queries...")
        print("=" * 70)
        
        results = []
        
        for i, eval_data in enumerate(evaluations):
            print(f"\n📊 Evaluating Query {i + 1}/{len(evaluations)}...")
            
            # Extract required fields
            natural_query = eval_data.get("natural_query", "")
            expected_sql = eval_data.get("expected_sql", "")
            generated_sql = eval_data.get("generated_sql", "")
            session_id = eval_data.get("session_id", f"batch_session_{i}")
            metadata = eval_data.get("metadata", {})
            
            if not all([natural_query, expected_sql, generated_sql]):
                print(f"⚠️  Skipping evaluation {i + 1}: Missing required fields")
                results.append({
                    "evaluation_id": i + 1,
                    "score": 0.0,
                    "passed": False,
                    "natural_query": natural_query,
                    "error": "Missing required fields",
                    "session_id": session_id,
                    "metadata": metadata
                })
                continue
            
            # Perform SQL evaluation
            evaluation_result = self.evaluate_sql_semantic_equivalence(
                input_query=natural_query,
                expected_output=expected_sql,
                model_output=generated_sql,
                session_id=session_id,
                metadata=metadata
            )
            
            # Add evaluation ID for tracking
            evaluation_result["evaluation_id"] = i + 1
            evaluation_result["natural_query"] = natural_query
            
            results.append(evaluation_result)
            
            # Print immediate result
            status = "✅ PASSED" if evaluation_result["passed"] else "❌ FAILED"
            print(f"{status} - Score: {evaluation_result['score']:.3f}")
            print(f"Question: {natural_query[:80]}...")
        
        return results
    
    def export_to_excel(
        self,
        results: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> str:
        """
        Export batch evaluation results to Excel with question, score, and summary.
        
        Args:
            results: List of evaluation results from batch_evaluate_sql
            filename: Optional custom filename. If not provided, generates timestamp-based name
            
        Returns:
            String path of the created Excel file
        """
        if not results:
            print("No results to export.")
            return ""
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sql_evaluation_results_{timestamp}.xlsx"
        
        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        try:
            # Prepare data for Excel export
            excel_data = []
            for result in results:
                row = {
                    'ID': result.get('evaluation_id', 'N/A'),
                    'Question': result.get('natural_query', 'N/A'),
                    'Score': result.get('score', 0.0),
                    'Passed': 'Yes' if result.get('passed', False) else 'No',
                    'Session_ID': result.get('session_id', 'N/A')
                }
                excel_data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(excel_data)
            
            # Create Excel writer object
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Write main results
                df.to_excel(writer, sheet_name='Evaluation Results', index=False)
                
                # Format main worksheet
                worksheet = writer.sheets['Evaluation Results']
                self._format_worksheet(worksheet)
                
                # Create and format summary sheet
                summary_data = self._create_summary_data(results)
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                summary_worksheet = writer.sheets['Summary']
                self._format_worksheet(summary_worksheet, max_width=30)
            
            print(f"✅ Results exported successfully to: {filename}")
            print(f"📊 Exported {len(results)} evaluation results")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            return ""
    
    def _format_worksheet(self, worksheet, max_width: int = 50) -> None:
        """
        Format worksheet columns with auto-width adjustment.
        """
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    cell_length = len(str(cell.value)) if cell.value is not None else 0
                    if cell_length > max_length:
                        max_length = cell_length
                except (TypeError, AttributeError):
                    pass
            
            # Set column width with padding and cap
            adjusted_width = min(max_length + 2, max_width)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _create_summary_data(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create summary data for the Excel export.
        """
        if not results:
            return []
        
        total_evaluations = len(results)
        passed_evaluations = sum(1 for r in results if r.get("passed", False))
        failed_evaluations = total_evaluations - passed_evaluations
        avg_score = sum(r.get("score", 0.0) for r in results) / total_evaluations
        
        # Calculate score distribution
        score_ranges = {
            "Excellent (0.9-1.0)": 0,
            "Good (0.8-0.89)": 0,
            "Fair (0.6-0.79)": 0,
            "Poor (0.4-0.59)": 0,
            "Very Poor (0.0-0.39)": 0
        }
        
        for result in results:
            score = result.get("score", 0.0)
            if score >= 0.9:
                score_ranges["Excellent (0.9-1.0)"] += 1
            elif score >= 0.8:
                score_ranges["Good (0.8-0.89)"] += 1
            elif score >= 0.6:
                score_ranges["Fair (0.6-0.79)"] += 1
            elif score >= 0.4:
                score_ranges["Poor (0.4-0.59)"] += 1
            else:
                score_ranges["Very Poor (0.0-0.39)"] += 1
        
        summary_data = [
            {"Metric": "Total Evaluations", "Value": total_evaluations},
            {"Metric": "Passed (Score ≥ 0.8)", "Value": f"{passed_evaluations} ({passed_evaluations/total_evaluations*100:.1f}%)"},
            {"Metric": "Failed (Score < 0.8)", "Value": f"{failed_evaluations} ({failed_evaluations/total_evaluations*100:.1f}%)"},
            {"Metric": "Average Score", "Value": f"{avg_score:.3f}"},
            {"Metric": "", "Value": ""},  # Empty row for spacing
            {"Metric": "Score Distribution", "Value": ""},
        ]
        
        for range_name, count in score_ranges.items():
            percentage = (count / total_evaluations * 100) if total_evaluations > 0 else 0
            summary_data.append({
                "Metric": range_name,
                "Value": f"{count} ({percentage:.1f}%)"
            })
        
        return summary_data
    
    def print_batch_summary(self, results: List[Dict[str, Any]]) -> None:
        """
        Print a comprehensive summary of batch evaluation results.
        """
        if not results:
            print("No results to summarize.")
            return
        
        print("\n" + "=" * 80)
        print("📈 BATCH EVALUATION SUMMARY")
        print("=" * 80)
        
        total_evaluations = len(results)
        passed_evaluations = sum(1 for r in results if r.get("passed", False))
        failed_evaluations = total_evaluations - passed_evaluations
        
        avg_score = sum(r.get("score", 0.0) for r in results) / total_evaluations
        
        print(f"Total Evaluations: {total_evaluations}")
        print(f"Passed (Score ≥ 0.8): {passed_evaluations} ({passed_evaluations/total_evaluations*100:.1f}%)")
        print(f"Failed (Score < 0.8): {failed_evaluations} ({failed_evaluations/total_evaluations*100:.1f}%)")
        print(f"Average Score: {avg_score:.3f}")
        
        print("\n📊 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in results:
            status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
            print(f"\nQuery {result.get('evaluation_id', 'N/A')}: {status} (Score: {result.get('score', 0.0):.3f})")
            print(f"Question: {result.get('natural_query', 'N/A')[:80]}...")
            
            if not result.get("passed", False):
                analysis = result.get('details', {}).get('analysis', {})
                if analysis.get('differences'):
                    print(f"Issues found in: {', '.join(analysis['differences'].keys())}")
        
        print("\n" + "=" * 80)
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all evaluations performed.
        """
        if not self.evaluation_results:
            return {"message": "No evaluations performed yet"}
        
        total_evaluations = len(self.evaluation_results)
        passed_evaluations = sum(1 for result in self.evaluation_results if result['passed'])
        average_score = sum(result['score'] for result in self.evaluation_results) / total_evaluations
        
        evaluation_types = {}
        for result in self.evaluation_results:
            eval_type = result['evaluation_type']
            if eval_type not in evaluation_types:
                evaluation_types[eval_type] = {'count': 0, 'passed': 0, 'total_score': 0}
            
            evaluation_types[eval_type]['count'] += 1
            evaluation_types[eval_type]['total_score'] += result['score']
            if result['passed']:
                evaluation_types[eval_type]['passed'] += 1
        
        # Calculate averages for each type
        for eval_type in evaluation_types:
            count = evaluation_types[eval_type]['count']
            evaluation_types[eval_type]['average_score'] = evaluation_types[eval_type]['total_score'] / count
            evaluation_types[eval_type]['pass_rate'] = evaluation_types[eval_type]['passed'] / count
        
        return {
            "total_evaluations": total_evaluations,
            "passed_evaluations": passed_evaluations,
            "pass_rate": passed_evaluations / total_evaluations,
            "average_score": average_score,
            "evaluation_types": evaluation_types,
            "individual_results": self.evaluation_results
        }


def run_batch_evaluation_from_test_data():
    """
    Run batch evaluation using test data and export results to Excel.
    """
    # Import test data
    try:
        from test_data import BATCH_EVALUATIONS
    except ImportError:
        print("❌ Error: test_data.py not found or BATCH_EVALUATIONS not available")
        return
    
    print("🚀 Starting Batch SQL Evaluation from Test Data")
    print("=" * 60)
    
    # Initialize evaluator
    evaluator = SimpleEvaluator()
    
    # Run batch evaluation
    results = evaluator.batch_evaluate_sql(BATCH_EVALUATIONS)
    
    # Print summary
    evaluator.print_batch_summary(results)
    
    # Export to Excel
    excel_filename = evaluator.export_to_excel(results)
    
    if excel_filename:
        print("\n✅ Evaluation completed successfully!")
        print(f"📄 Excel report saved as: {excel_filename}")
        print("📊 The Excel file contains:")
        print("   - Evaluation Results sheet with questions and scores")
        print("   - Summary sheet with overall statistics")
    
    return results, excel_filename


def demonstrate_evaluations():
    """
    Demonstrate various evaluation scenarios.
    """
    evaluator = SimpleEvaluator()
    
    # SQL query constants
    SEEKERS_QUERY = "SELECT COUNT(*) FROM seekers WHERE placement_status = 'Placed';"
    
    print("🚀 Advanced Langfuse SQL Evaluator Demo")
    print("=" * 60)
    
    # Test Case 1: Perfect SQL match
    print("\n📊 Test Case 1: Perfect SQL Match")
    result1 = evaluator.evaluate_sql_semantic_equivalence(
        input_query="How many seekers are placed?",
        expected_output=SEEKERS_QUERY,
        model_output=SEEKERS_QUERY,
        session_id="demo_session_1",
        metadata={"model": "gpt-4", "temperature": 0.0}
    )
    print(f"Score: {result1['score']:.2f} | Passed: {result1['passed']}")
    print(f"Analysis: {json.dumps(result1['details']['analysis'], indent=2)}")
    
    # Test Case 2: Slightly different SQL (different formatting)
    print("\n📊 Test Case 2: Different Formatting")
    result2 = evaluator.evaluate_sql_semantic_equivalence(
        input_query="Count placed seekers",
        expected_output=SEEKERS_QUERY,
        model_output="select count(*) from seekers where placement_status='Placed'",
        session_id="demo_session_1",
        metadata={"model": "gpt-3.5", "temperature": 0.3}
    )
    print(f"Score: {result2['score']:.2f} | Passed: {result2['passed']}")
    print(f"Analysis: {json.dumps(result2['details']['analysis'], indent=2)}")
    
    # Test Case 3: Semantically similar but different structure
    print("\n📊 Test Case 3: Different Structure")
    result3 = evaluator.evaluate_sql_semantic_equivalence(
        input_query="Get all active users",
        expected_output="SELECT * FROM users WHERE status = 'active';",
        model_output="SELECT user_id, name, email FROM users WHERE status = 'active';",
        session_id="demo_session_2",
        metadata={"model": "claude-3", "temperature": 0.5}
    )
    print(f"Score: {result3['score']:.2f} | Passed: {result3['passed']}")
    print(f"Analysis: {json.dumps(result3['details']['analysis'], indent=2)}")
    
    # Test Case 4: Completely different SQL
    print("\n📊 Test Case 4: Completely Different")
    result4 = evaluator.evaluate_sql_semantic_equivalence(
        input_query="Find user names",
        expected_output="SELECT name FROM users;",
        model_output="SELECT COUNT(*) FROM products;",
        session_id="demo_session_2",
        metadata={"model": "gpt-4", "temperature": 0.8}
    )
    print(f"Score: {result4['score']:.2f} | Passed: {result4['passed']}")
    print(f"Analysis: {json.dumps(result4['details']['analysis'], indent=2)}")
    
    # Test Case 5: Custom Text Similarity Evaluator
    print("\n📊 Test Case 5: Custom Text Evaluator")
    def advanced_text_similarity(expected, actual):
        """Advanced text similarity with semantic understanding."""
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        
        # Jaccard similarity
        intersection = expected_words.intersection(actual_words)
        union = expected_words.union(actual_words)
        jaccard = len(intersection) / len(union) if len(union) > 0 else 0.0
        
        # Length similarity penalty
        len_diff = abs(len(expected.split()) - len(actual.split()))
        len_penalty = max(0, 1 - (len_diff * 0.1))
        
        return jaccard * len_penalty
    
    result5 = evaluator.evaluate_custom(
        evaluator_name="Advanced Text Similarity",
        input_data="Explain the benefits of regular exercise",
        expected_output="Regular exercise improves cardiovascular health, builds muscle strength, and enhances mental wellbeing",
        model_output="Exercise helps improve heart health, increases muscle strength, and boosts mental wellness",
        evaluation_function=advanced_text_similarity,
        session_id="demo_session_3",
        metadata={"model": "gpt-4", "evaluation_method": "advanced_similarity"}
    )
    print(f"Score: {result5['score']:.2f} | Passed: {result5['passed']}")
    
    # Test Case 6: Exact Match Evaluator
    print("\n📊 Test Case 6: Exact Match Evaluator")
    result6 = evaluator.evaluate_custom(
        evaluator_name="Exact Match",
        input_data="What is 2 + 2?",
        expected_output="4",
        model_output="4",
        evaluation_function=lambda exp, act: 1.0 if exp.strip() == act.strip() else 0.0,
        session_id="demo_session_3"
    )
    print(f"Score: {result6['score']:.2f} | Passed: {result6['passed']}")
    
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
    # Run batch evaluation from test data
    run_batch_evaluation_from_test_data()
