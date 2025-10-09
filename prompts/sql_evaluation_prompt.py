"""
SQL Evaluation Prompt Template for OpenAI GPT model.
Used to evaluate semantic equivalence and result consistency between expected and generated SQL queries.
"""

def get_sql_evaluation_prompt(natural_query: str, expected_sql: str, generated_sql: str) -> str:
    """
    Generate the SQL evaluation prompt for OpenAI.
    
    Args:
        natural_query: The original natural language question
        expected_sql: The expected/golden SQL query
        generated_sql: The generated SQL query to evaluate
        
    Returns:
        Formatted prompt string for OpenAI evaluation
    """
    return f"""
You are an expert SQL evaluator. Analyze these SQL queries in the context of the natural language question.

Natural Language Question: "{natural_query}"
Expected SQL Query: {expected_sql}
Generated SQL Query: {generated_sql}

Evaluate the generated SQL against the expected SQL considering:

1. SEMANTIC EQUIVALENCE:
   - Do both queries logically answer the same question?
   - Are the table references, columns, and joins equivalent?
   - Are WHERE conditions logically equivalent?
   - Are GROUP BY, ORDER BY, and aggregations equivalent?

2. RESULT CONSISTENCY:
   - Would both queries return the same results when executed?
   - Consider that dynamic values (dates, IDs) may vary but structure should match
   - Do both queries answer the original natural language question correctly?

3. SYNTAX AND STRUCTURE:
   - Are there any syntax errors in the generated query?
   - Is the query structure appropriate for the question?

Provide your response in this exact JSON format:
{{
    "score": <float between 0.0 and 1.0>,
    "semantic_equivalence": <float between 0.0 and 1.0>,
    "result_consistency": <float between 0.0 and 1.0>,
    "syntax_correctness": <float between 0.0 and 1.0>,
    "comments": "<detailed explanation justifying the score>",
    "issues_found": ["<list of specific issues if any>"],
    "recommendation": "<suggestions for improvement if score < 0.8>"
}}

Score Guidelines:
- 1.0: Perfect equivalence, identical results expected
- 0.8-0.9: Very good, minor differences that don't affect results
- 0.6-0.7: Good but some differences that might affect results
- 0.4-0.5: Partially correct but significant issues
- 0.0-0.3: Poor, major issues or incorrect query
"""
