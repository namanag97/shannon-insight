"""Tree-sitter queries for Go.

Extracts:
    - Function definitions (top-level and methods)
    - Struct definitions (Go's class equivalent)
    - Import declarations
"""

# Query for function definitions
FUNCTION_QUERY = """
(function_declaration
    name: (identifier) @function.name
    parameters: (parameter_list) @function.params
    body: (block) @function.body
) @function

(method_declaration
    receiver: (parameter_list) @method.receiver
    name: (field_identifier) @method.name
    parameters: (parameter_list) @method.params
    body: (block) @method.body
) @method
"""

# Query for struct definitions (class equivalent)
CLASS_QUERY = """
(type_declaration
    (type_spec
        name: (type_identifier) @struct.name
        type: (struct_type) @struct.body
    )
) @struct

(type_declaration
    (type_spec
        name: (type_identifier) @interface.name
        type: (interface_type) @interface.body
    )
) @interface
"""

# Query for imports
IMPORT_QUERY = """
(import_declaration
    (import_spec
        path: (interpreted_string_literal) @import.path
    )
) @import

(import_declaration
    (import_spec_list
        (import_spec
            path: (interpreted_string_literal) @import_list.path
        )
    )
) @import_list
"""

# Query for call expressions
CALL_QUERY = """
(call_expression
    function: (identifier) @call.function
) @call

(call_expression
    function: (selector_expression
        operand: (_) @call.object
        field: (field_identifier) @call.method
    )
) @call.method_call
"""

# Query for parameters
PARAMETER_QUERY = """
(parameter_list
    (parameter_declaration
        name: (identifier) @param
    )
)
"""


def get_all_queries() -> dict[str, str]:
    """Return all Go queries as a dict."""
    return {
        "function": FUNCTION_QUERY,
        "class": CLASS_QUERY,
        "import": IMPORT_QUERY,
        "call": CALL_QUERY,
        "parameter": PARAMETER_QUERY,
    }
