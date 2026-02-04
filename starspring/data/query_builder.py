"""
Query method parser and SQL generator

Parses repository method names and generates SQL queries automatically.
Similar to Spring Data JPA's query derivation.
"""

import re
from typing import List, Tuple, Any, Optional, Type
from enum import Enum


class QueryOperation(Enum):
    """Query operation types"""
    FIND = "find"
    COUNT = "count"
    DELETE = "delete"
    EXISTS = "exists"


class QueryCondition(Enum):
    """Query condition operators"""
    EQUALS = ""
    AND = "And"
    OR = "Or"
    GREATER_THAN = "GreaterThan"
    LESS_THAN = "LessThan"
    GREATER_THAN_EQUAL = "GreaterThanEqual"
    LESS_THAN_EQUAL = "LessThanEqual"
    LIKE = "Like"
    CONTAINING = "Containing"
    STARTING_WITH = "StartingWith"
    ENDING_WITH = "EndingWith"
    BETWEEN = "Between"
    IN = "In"
    NOT = "Not"
    IS_NULL = "IsNull"
    IS_NOT_NULL = "IsNotNull"
    TRUE = "True"
    FALSE = "False"


class QueryPart:
    """Represents a part of a query"""
    
    def __init__(
        self,
        field: str,
        operator: QueryCondition,
        connector: Optional[str] = None
    ):
        self.field = field
        self.operator = operator
        self.connector = connector  # AND or OR


class ParsedQuery:
    """Parsed query information"""
    
    def __init__(
        self,
        operation: QueryOperation,
        parts: List[QueryPart],
        order_by: Optional[List[Tuple[str, str]]] = None
    ):
        self.operation = operation
        self.parts = parts
        self.order_by = order_by or []


class QueryMethodParser:
    """
    Parses repository method names into query components
    
    Supports patterns like:
    - findByName
    - findByEmailAndActive
    - findByAgeGreaterThan
    - findByNameContaining
    - countByActive
    - deleteByEmail
    - existsByUsername
    """
    
    # Regex patterns for parsing
    OPERATION_PATTERN = r'^(find|count|delete|exists)By'
    CONDITION_PATTERNS = {
        'GreaterThanEqual': r'GreaterThanEqual',
        'LessThanEqual': r'LessThanEqual',
        'GreaterThan': r'GreaterThan',
        'LessThan': r'LessThan',
        'Containing': r'Containing',
        'StartingWith': r'StartingWith',
        'EndingWith': r'EndingWith',
        'Between': r'Between',
        'Like': r'Like',
        'In': r'In',
        'IsNull': r'IsNull',
        'IsNotNull': r'IsNotNull',
        'True': r'True',
        'False': r'False',
        'Not': r'Not',
    }
    
    def parse(self, method_name: str) -> ParsedQuery:
        """
        Parse a repository method name into query components
        
        Args:
            method_name: Method name to parse
            
        Returns:
            ParsedQuery object
            
        Raises:
            ValueError: If method name cannot be parsed
        """
        # Extract operation
        operation_match = re.match(self.OPERATION_PATTERN, method_name)
        if not operation_match:
            raise ValueError(f"Invalid query method name: {method_name}")
        
        operation_str = operation_match.group(1)
        operation = QueryOperation(operation_str)
        
        # Remove operation prefix
        remainder = method_name[len(operation_match.group(0)):]
        
        # Check for OrderBy clause
        order_by = []
        if 'OrderBy' in remainder:
            parts = remainder.split('OrderBy')
            remainder = parts[0]
            order_clause = parts[1]
            order_by = self._parse_order_by(order_clause)
        
        # Parse conditions
        query_parts = self._parse_conditions(remainder)
        
        return ParsedQuery(operation, query_parts, order_by)
    
    def _parse_conditions(self, condition_str: str) -> List[QueryPart]:
        """Parse condition string into query parts"""
        parts = []
        
        # Split by And/Or
        tokens = re.split(r'(And|Or)', condition_str)
        
        current_connector = None
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token in ['And', 'Or']:
                current_connector = token.upper()
                i += 1
                continue
            
            if not token:
                i += 1
                continue
            
            # Parse this condition
            field, operator = self._parse_single_condition(token)
            parts.append(QueryPart(field, operator, current_connector))
            
            i += 1
        
        return parts
    
    def _parse_single_condition(self, condition: str) -> Tuple[str, QueryCondition]:
        """Parse a single condition into field and operator"""
        # Check for operators
        for op_name, op_pattern in self.CONDITION_PATTERNS.items():
            if condition.endswith(op_name):
                field = condition[:-len(op_name)]
                return self._camel_to_snake(field), QueryCondition[op_name.upper().replace('THAN', '_THAN')]
        
        # No operator means equals
        return self._camel_to_snake(condition), QueryCondition.EQUALS
    
    def _parse_order_by(self, order_str: str) -> List[Tuple[str, str]]:
        """Parse OrderBy clause"""
        orders = []
        parts = re.split(r'(And)', order_str)
        
        for part in parts:
            if part == 'And' or not part:
                continue
            
            # Check for Asc/Desc
            if part.endswith('Desc'):
                field = part[:-4]
                direction = 'DESC'
            elif part.endswith('Asc'):
                field = part[:-3]
                direction = 'ASC'
            else:
                field = part
                direction = 'ASC'
            
            orders.append((self._camel_to_snake(field), direction))
        
        return orders
    
    def _camel_to_snake(self, name: str) -> str:
        """Convert CamelCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class SQLQueryGenerator:
    """
    Generates SQL queries from parsed query information
    """
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def generate(self, parsed_query: ParsedQuery) -> Tuple[str, List[str]]:
        """
        Generate SQL query from parsed query
        
        Args:
            parsed_query: Parsed query information
            
        Returns:
            Tuple of (SQL query string, list of parameter placeholders)
        """
        if parsed_query.operation == QueryOperation.FIND:
            return self._generate_select(parsed_query)
        elif parsed_query.operation == QueryOperation.COUNT:
            return self._generate_count(parsed_query)
        elif parsed_query.operation == QueryOperation.DELETE:
            return self._generate_delete(parsed_query)
        elif parsed_query.operation == QueryOperation.EXISTS:
            return self._generate_exists(parsed_query)
        
        raise ValueError(f"Unsupported operation: {parsed_query.operation}")
    
    def _generate_select(self, parsed_query: ParsedQuery) -> Tuple[str, List[str]]:
        """Generate SELECT query"""
        sql = f"SELECT * FROM {self.table_name}"
        params = []
        
        if parsed_query.parts:
            where_clause, params = self._build_where_clause(parsed_query.parts)
            sql += f" WHERE {where_clause}"
        
        if parsed_query.order_by:
            order_parts = [f"{field} {direction}" for field, direction in parsed_query.order_by]
            sql += f" ORDER BY {', '.join(order_parts)}"
        
        return sql, params
    
    def _generate_count(self, parsed_query: ParsedQuery) -> Tuple[str, List[str]]:
        """Generate COUNT query"""
        sql = f"SELECT COUNT(*) FROM {self.table_name}"
        params = []
        
        if parsed_query.parts:
            where_clause, params = self._build_where_clause(parsed_query.parts)
            sql += f" WHERE {where_clause}"
        
        return sql, params
    
    def _generate_delete(self, parsed_query: ParsedQuery) -> Tuple[str, List[str]]:
        """Generate DELETE query"""
        sql = f"DELETE FROM {self.table_name}"
        params = []
        
        if parsed_query.parts:
            where_clause, params = self._build_where_clause(parsed_query.parts)
            sql += f" WHERE {where_clause}"
        
        return sql, params
    
    def _generate_exists(self, parsed_query: ParsedQuery) -> Tuple[str, List[str]]:
        """Generate EXISTS query"""
        sql = f"SELECT EXISTS(SELECT 1 FROM {self.table_name}"
        params = []
        
        if parsed_query.parts:
            where_clause, params = self._build_where_clause(parsed_query.parts)
            sql += f" WHERE {where_clause}"
        
        sql += ")"
        return sql, params
    
    def _build_where_clause(self, parts: List[QueryPart]) -> Tuple[str, List[str]]:
        """Build WHERE clause from query parts"""
        conditions = []
        params = []
        
        for part in parts:
            condition, part_params = self._build_condition(part)
            
            if part.connector and conditions:
                conditions.append(f" {part.connector} {condition}")
            else:
                conditions.append(condition)
            
            params.extend(part_params)
        
        return ''.join(conditions), params
    
    def _build_condition(self, part: QueryPart) -> Tuple[str, List[str]]:
        """Build a single condition"""
        field = part.field
        operator = part.operator
        
        if operator == QueryCondition.EQUALS:
            return f"{field} = ?", [field]
        elif operator == QueryCondition.GREATER_THAN:
            return f"{field} > ?", [field]
        elif operator == QueryCondition.LESS_THAN:
            return f"{field} < ?", [field]
        elif operator == QueryCondition.GREATER_THAN_EQUAL:
            return f"{field} >= ?", [field]
        elif operator == QueryCondition.LESS_THAN_EQUAL:
            return f"{field} <= ?", [field]
        elif operator == QueryCondition.LIKE:
            return f"{field} LIKE ?", [field]
        elif operator == QueryCondition.CONTAINING:
            return f"{field} LIKE ?", [field]  # Will add % in executor
        elif operator == QueryCondition.STARTING_WITH:
            return f"{field} LIKE ?", [field]  # Will add % in executor
        elif operator == QueryCondition.ENDING_WITH:
            return f"{field} LIKE ?", [field]  # Will add % in executor
        elif operator == QueryCondition.BETWEEN:
            return f"{field} BETWEEN ? AND ?", [field, field]
        elif operator == QueryCondition.IN:
            return f"{field} IN (?)", [field]
        elif operator == QueryCondition.IS_NULL:
            return f"{field} IS NULL", []
        elif operator == QueryCondition.IS_NOT_NULL:
            return f"{field} IS NOT NULL", []
        elif operator == QueryCondition.TRUE:
            return f"{field} = TRUE", []
        elif operator == QueryCondition.FALSE:
            return f"{field} = FALSE", []
        elif operator == QueryCondition.NOT:
            return f"{field} != ?", [field]
        
        raise ValueError(f"Unsupported operator: {operator}")
