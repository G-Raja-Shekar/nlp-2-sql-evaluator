"""
SQL parsing utilities.
"""

import re
from typing import Dict, List, Optional


class SQLParser:
    """
    Handles SQL parsing and component extraction.
    """
    
    @staticmethod
    def parse_components(sql: str) -> Dict[str, str]:
        """
        Parse SQL into components (SELECT, FROM, WHERE, etc.)
        
        Args:
            sql: Normalized SQL string
            
        Returns:
            Dictionary with SQL components
        """
        components = {
            'select': '',
            'from': '',
            'where': '',
            'order_by': '',
            'group_by': '',
            'having': '',
            'limit': ''
        }
        
        if not sql:
            return components
        
        sql_upper = sql.upper()
        
        # Find SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)(?=\s+FROM|\s+$)', sql_upper)
        if select_match:
            components['select'] = select_match.group(1).strip()
        
        # Find FROM clause
        from_match = re.search(r'FROM\s+(.*?)(?=\s+WHERE|\s+GROUP|\s+ORDER|\s+LIMIT|\s+$)', sql_upper)
        if from_match:
            components['from'] = from_match.group(1).strip()
        
        # Find WHERE clause
        where_match = re.search(r'WHERE\s+(.*?)(?=\s+GROUP|\s+ORDER|\s+LIMIT|\s+$)', sql_upper)
        if where_match:
            components['where'] = where_match.group(1).strip()
        
        # Find GROUP BY clause
        group_match = re.search(r'GROUP\s+BY\s+(.*?)(?=\s+HAVING|\s+ORDER|\s+LIMIT|\s+$)', sql_upper)
        if group_match:
            components['group_by'] = group_match.group(1).strip()
        
        # Find HAVING clause
        having_match = re.search(r'HAVING\s+(.*?)(?=\s+ORDER|\s+LIMIT|\s+$)', sql_upper)
        if having_match:
            components['having'] = having_match.group(1).strip()
        
        # Find ORDER BY clause
        order_match = re.search(r'ORDER\s+BY\s+(.*?)(?=\s+LIMIT|\s+$)', sql_upper)
        if order_match:
            components['order_by'] = order_match.group(1).strip()
        
        # Find LIMIT clause
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
        if limit_match:
            components['limit'] = limit_match.group(1).strip()
        
        return components
    
    @staticmethod
    def extract_tables(sql: str) -> List[str]:
        """
        Extract table names from SQL query.
        
        Args:
            sql: SQL string
            
        Returns:
            List of table names
        """
        tables = []
        
        # Simple FROM clause extraction
        from_match = re.search(r'FROM\s+([^\\s]+)', sql.upper())
        if from_match:
            table_part = from_match.group(1)
            # Handle simple table names (not joins)
            if ',' in table_part:
                tables.extend([t.strip() for t in table_part.split(',')])
            else:
                tables.append(table_part.strip())
        
        # Extract from JOIN clauses
        join_matches = re.findall(r'JOIN\s+([^\\s]+)', sql.upper())
        tables.extend(join_matches)
        
        return list(set(tables))  # Remove duplicates
    
    @staticmethod
    def extract_columns(sql: str) -> List[str]:
        """
        Extract column names from SELECT clause.
        
        Args:
            sql: SQL string
            
        Returns:
            List of column names/expressions
        """
        columns = []
        
        select_match = re.search(r'SELECT\s+(.*?)(?=\s+FROM)', sql.upper())
        if select_match:
            select_part = select_match.group(1)
            
            # Handle simple comma-separated columns
            if ',' in select_part:
                columns.extend([col.strip() for col in select_part.split(',')])
            else:
                columns.append(select_part.strip())
        
        return columns
    
    @staticmethod
    def get_query_type(sql: str) -> str:
        """
        Determine the type of SQL query.
        
        Args:
            sql: SQL string
            
        Returns:
            Query type (SELECT, INSERT, UPDATE, DELETE, etc.)
        """
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        elif sql_upper.startswith('CREATE'):
            return 'CREATE'
        elif sql_upper.startswith('DROP'):
            return 'DROP'
        elif sql_upper.startswith('ALTER'):
            return 'ALTER'
        else:
            return 'UNKNOWN'
