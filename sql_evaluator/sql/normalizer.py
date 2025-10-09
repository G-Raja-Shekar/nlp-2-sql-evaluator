"""
SQL normalization utilities.
"""

import re
from typing import Dict, Any


class SQLNormalizer:
    """
    Handles SQL string normalization for comparison.
    """
    
    @staticmethod
    def normalize(sql: str) -> str:
        """
        Normalize SQL string for comparison.
        
        Args:
            sql: Raw SQL string
            
        Returns:
            Normalized SQL string
        """
        if not sql:
            return ""
            
        # Remove extra whitespace and convert to lowercase
        normalized = " ".join(sql.strip().lower().split())
        
        # Remove semicolon at the end if present
        if normalized.endswith(";"):
            normalized = normalized[:-1]
        
        # Normalize quotes (convert single quotes to double quotes for consistency)
        normalized = re.sub(r"'([^']*)'", r'"\1"', normalized)
        
        # Normalize whitespace around operators
        normalized = re.sub(r'\s*=\s*', ' = ', normalized)
        normalized = re.sub(r'\s*,\s*', ', ', normalized)
        
        return normalized.strip()
    
    @staticmethod
    def remove_comments(sql: str) -> str:
        """
        Remove SQL comments from the query.
        
        Args:
            sql: SQL string that may contain comments
            
        Returns:
            SQL string without comments
        """
        # Remove single-line comments (-- style)
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        
        # Remove multi-line comments (/* */ style)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        return sql.strip()
    
    @staticmethod
    def standardize_keywords(sql: str) -> str:
        """
        Standardize SQL keywords to uppercase.
        
        Args:
            sql: SQL string
            
        Returns:
            SQL string with standardized keywords
        """
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER',
            'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'LIKE', 'BETWEEN',
            'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'DISTINCT',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'AS', 'ASC', 'DESC'
        ]
        
        result = sql
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + keyword.lower() + r'\b'
            result = re.sub(pattern, keyword, result, flags=re.IGNORECASE)
        
        return result
