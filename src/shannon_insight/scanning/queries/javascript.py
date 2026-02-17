"""Tree-sitter queries for JavaScript.

Extracts:
    - Function definitions (including arrow functions, methods)
    - Class definitions
    - Import declarations (ES6 and CommonJS)
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

(generator_function_declaration
    name: (identifier) @generator.name
    parameters: (formal_parameters) @generator.params
    body: (statement_block) @generator.body
) @generator
"""

# Query for class definitions
CLASS_QUERY = """
(class_declaration
    name: (identifier) @class.name
    (class_heritage
        (extends_clause
            value: (identifier) @class.extends
        )?
    )?
    body: (class_body) @class.body
) @class
"""

# Query for imports (ES6 and CommonJS)
IMPORT_QUERY = """
(import_statement
    source: (string) @import.source
) @import

(call_expression
    function: (identifier) @require
    arguments: (arguments
        (string) @require.source
    )
    (#eq? @require "require")
) @require_call
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
    (identifier) @param
)

(formal_parameters
    (assignment_pattern
        left: (identifier) @default_param
    )
)

(formal_parameters
    (rest_pattern
        (identifier) @rest_param
    )
)
"""


def get_all_queries() -> dict[str, str]:
    """Return all JavaScript queries as a dict."""
    return {
        "function": FUNCTION_QUERY,
        "class": CLASS_QUERY,
        "import": IMPORT_QUERY,
        "call": CALL_QUERY,
        "parameter": PARAMETER_QUERY,
    }
