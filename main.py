from enum import Enum
from typing import Optional, Dict, List, Union, Callable, Any, Tuple
from dataclasses import dataclass
import re
from datetime import datetime

# Define enums first
class NodeType(Enum):
    OPERATOR = "operator"
    COMPARISON = "comparison"
    FUNCTION = "function"

class Operator(Enum):
    AND = "AND"
    OR = "OR"
    GT = ">"
    LT = "<"
    EQ = "="
    NE = "!="
    GTE = ">="
    LTE = "<="
    IN = "IN"
    NOT_IN = "NOT IN"

# Define custom exceptions
class RuleValidationError(Exception):
    """Custom exception for rule validation errors"""
    pass

class AttributeValidationError(Exception):
    """Custom exception for attribute validation errors"""
    pass

# Define data classes
@dataclass
class AttributeDefinition:
    """Definition for valid attributes and their constraints"""
    name: str
    data_type: type
    constraints: Optional[Dict[str, Any]] = None
    description: str = ""
    required: bool = True

@dataclass
class Node:
    """Node class for building the Abstract Syntax Tree"""
    type: NodeType
    value: Optional[Union[str, int, float, List]] = None
    left: Optional['Node'] = None
    right: Optional['Node'] = None
    operator: Optional[Operator] = None
    field: Optional[str] = None
    function: Optional[str] = None
    args: Optional[List[Any]] = None

# Main Rule Engine class
class RuleEngine:
    def __init__(self):
        self.operators = {
            'AND': Operator.AND,
            'OR': Operator.OR,
            '>': Operator.GT,
            '<': Operator.LT,
            '=': Operator.EQ,
            '!=': Operator.NE,
            '>=': Operator.GTE,
            '<=': Operator.LTE,
            'IN': Operator.IN,
            'NOT IN': Operator.NOT_IN
        }
        
        self.attribute_catalog: Dict[str, AttributeDefinition] = {}
        self.function_registry: Dict[str, Callable] = {
            'length': len,
            'today': lambda: datetime.now().date(),
            'lowercase': str.lower,
            'uppercase': str.upper,
        }

    def register_attribute(self, definition: AttributeDefinition):
        """Register a new attribute definition in the catalog"""
        self.attribute_catalog[definition.name] = definition

    def register_function(self, name: str, func: Callable):
        """Register a new user-defined function"""
        self.function_registry[name] = func

    def tokenize(self, rule_string: str) -> List[str]:
        """
        Tokenize a rule string into a list of tokens.
        Handles quoted strings, parentheses, operators, and values.
        """
        if not rule_string:
            raise RuleValidationError("Empty rule string")

        pattern = r'''
            (?:[^\s"'()]+)|    # Match non-space characters except quotes and parentheses
            (?:"[^"]*")|       # Match double-quoted strings
            (?:'[^']*')|       # Match single-quoted strings
            (?:[()])           # Match parentheses
        '''
        
        tokens = [token.strip() for token in re.findall(pattern, rule_string, re.VERBOSE)]
        processed_tokens = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            # Handle quoted strings
            if (token.startswith('"') and token.endswith('"')) or \
               (token.startswith("'") and token.endswith("'")):
                processed_tokens.append(token[1:-1])
                i += 1
                continue
            
            # Handle function calls
            if i + 1 < len(tokens) and tokens[i + 1] == '(':
                processed_tokens.append(f"{token}(")
                i += 2
                continue
            
            # Handle operators
            if token.upper() in {'AND', 'OR', 'IN', 'NOT IN'}:
                processed_tokens.append(token.upper())
            elif token in {'>', '<', '=', '!=', '>=', '<='}:
                processed_tokens.append(token)
            else:
                # Handle numeric values
                try:
                    if '.' in token:
                        processed_tokens.append(float(token))
                    else:
                        processed_tokens.append(int(token))
                except ValueError:
                    processed_tokens.append(token)
            
            i += 1
        
        return processed_tokens

    def parse_expression(self, tokens: List[str], pos: int) -> Tuple[Node, int]:
        """Parse an expression from tokens starting at the given position"""
        if pos >= len(tokens):
            raise RuleValidationError("Unexpected end of expression")

        token = tokens[pos]

        # Handle parenthesized expressions
        if token == '(':
            node, next_pos = self.parse_expression(tokens, pos + 1)
            if next_pos >= len(tokens) or tokens[next_pos] != ')':
                raise RuleValidationError("Missing closing parenthesis")
            return node, next_pos + 1

        # Handle function calls
        if isinstance(token, str) and '(' in token:
            return self.parse_function(tokens, pos)

        # Handle field comparisons
        if pos + 2 < len(tokens) and tokens[pos + 1] in self.operators:
            field = token
            operator = self.operators[tokens[pos + 1]]
            value = tokens[pos + 2]

            # Validate field exists in catalog
            if field not in self.attribute_catalog:
                raise AttributeValidationError(f"Unknown attribute: {field}")

            return Node(
                type=NodeType.COMPARISON,
                field=field,
                operator=operator,
                value=value
            ), pos + 3

        raise RuleValidationError(f"Invalid expression at position {pos}: {token}")

    def parse_function(self, tokens: List[str], pos: int) -> Tuple[Node, int]:
        """Parse a function call in the rule"""
        func_name = tokens[pos][:-1]  # Remove trailing parenthesis
        if func_name not in self.function_registry:
            raise RuleValidationError(f"Unknown function: {func_name}")
        
        args = []
        current_pos = pos + 1
        
        while current_pos < len(tokens) and tokens[current_pos] != ')':
            if tokens[current_pos] == ',':
                current_pos += 1
                continue
            
            if isinstance(tokens[current_pos], str) and '(' in tokens[current_pos]:
                arg_node, new_pos = self.parse_function(tokens, current_pos)
                args.append(arg_node)
                current_pos = new_pos
            else:
                args.append(tokens[current_pos])
                current_pos += 1
        
        return Node(
            type=NodeType.FUNCTION,
            function=func_name,
            args=args
        ), current_pos + 1

    def create_rule(self, rule_string: str) -> Node:
        """Create an AST from a rule string with validation"""
        tokens = self.tokenize(rule_string)
        self.validate_rule_syntax(tokens)
        node, pos = self.parse_expression(tokens, 0)
        
        if pos < len(tokens):
            next_token = tokens[pos]
            if next_token in {'AND', 'OR'}:
                operator = self.operators[next_token]
                right_node, final_pos = self.parse_expression(tokens, pos + 1)
                return Node(
                    type=NodeType.OPERATOR,
                    operator=operator,
                    left=node,
                    right=right_node
                )
        return node

    def validate_rule_syntax(self, tokens: List[str]) -> None:
        """Validate rule syntax before parsing"""
        stack = []
        for token in tokens:
            if token == '(':
                stack.append(token)
            elif token == ')':
                if not stack:
                    raise RuleValidationError("Unmatched closing parenthesis")
                stack.pop()
            elif token in self.operators:
                if not (len(tokens) > tokens.index(token) + 1):
                    raise RuleValidationError(f"Operator {token} missing right operand")
        
        if stack:
            raise RuleValidationError("Unmatched opening parenthesis")

    def validate_attribute(self, name: str, value: Any) -> Any:
        """Validate an attribute value against its definition"""
        if name not in self.attribute_catalog:
            raise AttributeValidationError(f"Unknown attribute: {name}")
        
        definition = self.attribute_catalog[name]
        
        # Check type
        if not isinstance(value, definition.data_type):
            try:
                value = definition.data_type(value)
            except:
                raise AttributeValidationError(
                    f"Invalid type for {name}. Expected {definition.data_type.__name__}"
                )
        
        # Check constraints
        if definition.constraints:
            for constraint, constraint_value in definition.constraints.items():
                if constraint == "min" and value < constraint_value:
                    raise AttributeValidationError(
                        f"Value for {name} below minimum: {constraint_value}"
                    )
                elif constraint == "max" and value > constraint_value:
                    raise AttributeValidationError(
                        f"Value for {name} above maximum: {constraint_value}"
                    )
                elif constraint == "pattern" and not re.match(constraint_value, str(value)):
                    raise AttributeValidationError(
                        f"Value for {name} does not match pattern: {constraint_value}"
                    )
                elif constraint == "enum" and value not in constraint_value:
                    raise AttributeValidationError(
                        f"Value for {name} must be one of: {constraint_value}"
                    )
        
        return value

    def evaluate_rule(self, node: Node, data: Dict) -> bool:
        """Evaluate a rule against provided data with validation"""
        try:
            if node.type == NodeType.COMPARISON:
                if node.field not in data:
                    if node.field in self.attribute_catalog and \
                       self.attribute_catalog[node.field].required:
                        raise AttributeValidationError(f"Required attribute missing: {node.field}")
                    return False
                
                value = self.validate_attribute(node.field, data[node.field])
                
                if node.operator == Operator.GT:
                    return value > node.value
                elif node.operator == Operator.LT:
                    return value < node.value
                elif node.operator == Operator.EQ:
                    return value == node.value
                elif node.operator == Operator.NE:
                    return value != node.value
                elif node.operator == Operator.GTE:
                    return value >= node.value
                elif node.operator == Operator.LTE:
                    return value <= node.value
                elif node.operator == Operator.IN:
                    return value in node.value
                elif node.operator == Operator.NOT_IN:
                    return value not in node.value
            
            elif node.type == NodeType.OPERATOR:
                left_result = self.evaluate_rule(node.left, data)
                right_result = self.evaluate_rule(node.right, data)
                
                if node.operator == Operator.AND:
                    return left_result and right_result
                elif node.operator == Operator.OR:
                    return left_result or right_result
            
            elif node.type == NodeType.FUNCTION:
                return bool(self.evaluate_function(node, data))
            
            return False
            
        except Exception as e:
            raise RuleValidationError(f"Error evaluating rule: {str(e)}")

    def evaluate_function(self, node: Node, data: Dict) -> Any:
        """Evaluate a function node"""
        if node.function not in self.function_registry:
            raise RuleValidationError(f"Unknown function: {node.function}")
        
        evaluated_args = []
        for arg in node.args:
            if isinstance(arg, Node):
                evaluated_args.append(self.evaluate_function(arg, data))
            elif isinstance(arg, str) and arg in data:
                evaluated_args.append(data[arg])
            else:
                evaluated_args.append(arg)
        
        return self.function_registry[node.function](*evaluated_args)

def test_rule_engine():
    """Test the rule engine with various scenarios"""
    engine = RuleEngine()
    
    # Register attribute definitions
    engine.register_attribute(AttributeDefinition(
        name="age",
        data_type=int,
        constraints={"min": 0, "max": 120}
    ))
    
    engine.register_attribute(AttributeDefinition(
        name="department",
        data_type=str,
        constraints={"enum": ["Sales", "Marketing", "Engineering"]}
    ))
    
    # Test simple rule
    rule = "age > 30 AND department = 'Sales'"
    try:
        ast = engine.create_rule(rule)
        result = engine.evaluate_rule(ast, {
            "age": 35,
            "department": "Sales"
        })
        print(f"Rule evaluation result: {result}")
    except (RuleValidationError, AttributeValidationError) as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_rule_engine()