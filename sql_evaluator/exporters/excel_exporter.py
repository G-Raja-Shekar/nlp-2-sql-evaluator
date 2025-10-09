"""
Excel export functionality.
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from .base_exporter import BaseExporter
from ..models.evaluation_result import EvaluationResult


class ExcelExporter(BaseExporter):
    """
    Exports evaluation results to Excel format.
    """
    
    def export(self, results: List[EvaluationResult], filename: Optional[str] = None) -> str:
        """
        Export batch evaluation results to Excel with question, score, and summary.
        
        Args:
            results: List of evaluation results from batch evaluation
            filename: Optional custom filename. If not provided, generates timestamp-based name
            
        Returns:
            String path of the created Excel file
        """
        if not results:
            print("⚠️  No results to export.")
            return ""
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sql_evaluation_results_{timestamp}.xlsx"
        
        try:
            # Create detailed results data
            detailed_data = []
            for i, result in enumerate(results, 1):
                detailed_data.append({
                    'ID': i,
                    'Natural Query': result.details.get('input', 'N/A'),
                    'Expected SQL': result.details.get('expected', 'N/A'),
                    'Generated SQL': result.details.get('actual', 'N/A'),
                    'Score': result.score,
                    'Passed': 'Yes' if result.passed else 'No',
                    'Evaluation Type': result.evaluation_type,
                    'Session ID': result.session_id or 'N/A',
                    'Timestamp': result.timestamp.strftime('%Y-%m-%d %H:%M:%S') if result.timestamp else 'N/A',
                    'Has Differences': result.details.get('analysis', {}).get('has_differences', 'N/A'),
                    'Exact Match': result.details.get('analysis', {}).get('exact_match', 'N/A')
                })
            
            # Create summary data
            summary_data = self._create_summary_data(results)
            
            # Write to Excel with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Write detailed results
                detailed_df = pd.DataFrame(detailed_data)
                detailed_df.to_excel(writer, sheet_name='Detailed Results', index=False)
                
                # Write summary
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Format worksheets
                workbook = writer.book
                self._format_worksheet(workbook['Detailed Results'])
                self._format_worksheet(workbook['Summary'])
            
            print(f"📊 Results exported to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
            return ""
    
    def get_file_extension(self) -> str:
        """Get the file extension for Excel files."""
        return '.xlsx'
    
    def _format_worksheet(self, worksheet, max_width: int = 50) -> None:
        """
        Format Excel worksheet for better readability.
        
        Args:
            worksheet: Excel worksheet object
            max_width: Maximum column width
        """
        try:
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, max_width)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        except Exception as e:
            print(f"Warning: Could not format worksheet: {str(e)}")
    
    def _create_summary_data(self, results: List[EvaluationResult]) -> List[Dict[str, Any]]:
        """
        Create summary data for Excel export.
        
        Args:
            results: List of evaluation results
            
        Returns:
            List of summary statistics
        """
        if not results:
            return []
        
        total_evaluations = len(results)
        passed_evaluations = sum(1 for r in results if r.passed)
        failed_evaluations = total_evaluations - passed_evaluations
        total_score = sum(r.score for r in results)
        average_score = total_score / total_evaluations
        
        # Score distribution
        excellent = sum(1 for r in results if 0.9 <= r.score <= 1.0)
        good = sum(1 for r in results if 0.8 <= r.score < 0.9)
        fair = sum(1 for r in results if 0.6 <= r.score < 0.8)
        poor = sum(1 for r in results if 0.0 <= r.score < 0.6)
        
        summary_data = [
            {'Metric': 'Total Evaluations', 'Value': total_evaluations},
            {'Metric': 'Passed Evaluations', 'Value': passed_evaluations},
            {'Metric': 'Failed Evaluations', 'Value': failed_evaluations},
            {'Metric': 'Pass Rate (%)', 'Value': f"{passed_evaluations/total_evaluations*100:.1f}%"},
            {'Metric': 'Average Score', 'Value': f"{average_score:.3f}"},
            {'Metric': 'Min Score', 'Value': f"{min(r.score for r in results):.3f}"},
            {'Metric': 'Max Score', 'Value': f"{max(r.score for r in results):.3f}"},
            {'Metric': '', 'Value': ''},  # Empty row
            {'Metric': 'Score Distribution', 'Value': ''},
            {'Metric': 'Excellent (0.9-1.0)', 'Value': f"{excellent} ({excellent/total_evaluations*100:.1f}%)"},
            {'Metric': 'Good (0.8-0.9)', 'Value': f"{good} ({good/total_evaluations*100:.1f}%)"},
            {'Metric': 'Fair (0.6-0.8)', 'Value': f"{fair} ({fair/total_evaluations*100:.1f}%)"},
            {'Metric': 'Poor (0.0-0.6)', 'Value': f"{poor} ({poor/total_evaluations*100:.1f}%)"},
        ]
        
        return summary_data
