# Rule Engine with Abstract Syntax Tree (AST)

This project is a 3-tier Rule Engine application designed to determine user eligibility based on various attributes such as age, department, income, and spending. The system utilizes an Abstract Syntax Tree (AST) to represent conditional rules, allowing for dynamic creation, combination, and evaluation of these rules.

## Features

- **AST-based Rule Representation**: Efficiently represents complex logical rules using an Abstract Syntax Tree (AST).
- **Dynamic Rule Creation**: Allows for the dynamic creation and modification of rules using string-based expressions.
- **Rule Combination**: Combines multiple rules into a single AST structure for optimized evaluation.
- **Custom Evaluation**: Evaluates user data against defined rules to determine eligibility.
- **Simple API Design**: Provides a straightforward API for creating rules, combining them, and evaluating user data.


## Technologies Used

- **Programming Language**: Python 3.7+
- **Libraries**:
  - `enum` and `dataclass` for structured data representation
  - `re` module for rule string tokenization

## Setup Instructions

1. **Clone the repository**:
   Download the project from GitHub using the repository URL and navigate into the project directory.

2. **Install Dependencies**:
   Ensure you have Python 3.7 or above installed on your system. No external dependencies are required beyond the standard library.

3. **Run the Program**:
   Execute the Python script to test the rule engine's functionality and evaluate test cases.

## API Overview

### 1. `create_rule(rule_string)`

- **Purpose**: This function takes a string representing a rule and returns an Abstract Syntax Tree (AST) object that represents the rule.
- **Parameters**: A rule string in a format similar to logical expressions (e.g., `age > 30 AND department = 'Sales'`).
- **Output**: The root node of the AST representing the rule.

### 2. `combine_rules(rules)`

- **Purpose**: Combines a list of rule strings into a single AST, optimizing for efficiency by reducing redundant checks.
- **Parameters**: A list of rule strings.
- **Output**: A single root node representing the combined AST of all the rules.

### 3. `evaluate_rule(node, data)`

- **Purpose**: This function evaluates an AST against user-provided data to determine if the rule conditions are met.
- **Parameters**: 
  - The root node of the AST.
  - A dictionary containing the user's attributes (such as age, department, salary, etc.).
- **Output**: Boolean result (`True` or `False`) based on whether the conditions in the rule match the user's data.

## Example Rules

Some example rules that can be defined and evaluated in the system:

1. Rule 1:  
   "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
   
2. Rule 2:  
   "((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)"

These rules can be dynamically created and combined to evaluate user eligibility based on various attributes.
