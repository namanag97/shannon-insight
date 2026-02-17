"""Tree-sitter queries for TSX (TypeScript/JavaScript with JSX).

These queries work with the TSX grammar from tree-sitter-typescript.
Supports JSX syntax in addition to standard TypeScript/JavaScript.

Extracts:
    - Function definitions (including arrow functions, methods, exported functions)
    - Class definitions (with extends, implements)
    - Import declarations (ES6 imports)
"""

# Query for function definitions
FUNCTION_QUERY = """
(function_declaration
    name: (identifier) @function.name
    parameters: (formal_parameters) @function.params
    body: (statement_block) @function.body
) @function

(export_statement
    declaration: (function_declaration
        name: (identifier) @export_function.name
        parameters: (formal_parameters) @export_function.params
        body: (statement_block) @export_function.body
    )
) @export_function

(method_definition
    name: (property_identifier) @method.name
    parameters: (formal_parameters) @method.params
    body: (statement_block) @method.body
) @method

(arrow_function
    parameters: (formal_parameters) @arrow.params
    body: (_) @arrow.body
) @arrow

(variable_declarator
    name: (identifier) @var_func.name
    value: (arrow_function) @var_func.arrow
) @var_func
"""

# Query for class definitions
CLASS_QUERY = """
(class_declaration
    name: (type_identifier) @class.name
    (class_heritage
        (extends_clause
            value: (identifier) @class.extends
        )?
        (implements_clause
            (type_identifier) @class.implements
        )?
    )?
    body: (class_body) @class.body
) @class

(interface_declaration
    name: (type_identifier) @interface.name
    body: (interface_body) @interface.body
) @interface

(abstract_class_declaration
    name: (type_identifier) @abstract.name
    body: (class_body) @abstract.body
) @abstract
"""

# Query for imports
IMPORT_QUERY = """
(import_statement
    source: (string) @import.source
) @import
"""

# Query for call expressions
CALL_QUERY = """
(call_expression
    function: (identifier) @call.function
) @call

(call_expression
    function: (member_expression
        object: (_) @call.object
        property: (property_identifier) @call.method
    )
) @call.method_call
"""

# Query for parameters
PARAMETER_QUERY = """
(formal_parameters
    (required_parameter
        pattern: (identifier) @param
    )
)

(formal_parameters
    (optional_parameter
        pattern: (identifier) @optional_param
    )
)
"""


def get_all_queries() -> dict[str, str]:
    """Return all TypeScript queries as a dict."""
    return {
        "function": FUNCTION_QUERY,
        "class": CLASS_QUERY,
        "import": IMPORT_QUERY,
        "call": CALL_QUERY,
        "parameter": PARAMETER_QUERY,
    }
