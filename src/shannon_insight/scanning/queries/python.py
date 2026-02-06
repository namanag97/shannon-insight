"""Tree-sitter queries for Python.

Extracts:
    - Function definitions (with async, decorators, nesting depth)
    - Class definitions (with bases, ABC/Protocol detection)
    - Import statements (import x, from x import y)
    - __main__ guard detection
"""

# Query for function definitions
# Captures: @function for function_definition nodes
FUNCTION_QUERY = """
(function_definition
    name: (identifier) @function.name
) @function

(decorated_definition
    (decorator) @decorator
    definition: (function_definition
        name: (identifier) @decorated_function.name
    ) @decorated_function
)
"""

# Query for class definitions
# Captures: @class for class_definition nodes
CLASS_QUERY = """
(class_definition
    name: (identifier) @class.name
    superclasses: (argument_list)? @class.bases
) @class

(decorated_definition
    (decorator) @class_decorator
    definition: (class_definition
        name: (identifier) @decorated_class.name
        superclasses: (argument_list)? @decorated_class.bases
    ) @decorated_class
)
"""

# Query for imports
IMPORT_QUERY = """
(import_statement
    name: (dotted_name) @import.module
) @import

(import_from_statement
    module_name: (dotted_name)? @from.module
    name: (dotted_name)? @from.name
) @from
"""

# Query for __main__ guard
# Matches: if __name__ == "__main__":
MAIN_GUARD_QUERY = """
(if_statement
    condition: (comparison_operator
        (identifier) @name_var
        (string) @main_str
    )
    (#eq? @name_var "__name__")
    (#match? @main_str "__main__")
) @main_guard
"""

# Query for call expressions (to extract call targets)
CALL_QUERY = """
(call
    function: (identifier) @call.function
) @call

(call
    function: (attribute
        object: (_) @call.object
        attribute: (identifier) @call.method
    )
) @call.attribute
"""

# Query for parameters
PARAMETER_QUERY = """
(parameters
    (identifier) @param
)

(parameters
    (typed_parameter
        (identifier) @typed_param
    )
)

(parameters
    (default_parameter
        name: (identifier) @default_param
    )
)

(parameters
    (typed_default_parameter
        name: (identifier) @typed_default_param
    )
)

(parameters
    (list_splat_pattern
        (identifier) @args_param
    )
)

(parameters
    (dictionary_splat_pattern
        (identifier) @kwargs_param
    )
)
"""


def get_all_queries() -> dict[str, str]:
    """Return all Python queries as a dict."""
    return {
        "function": FUNCTION_QUERY,
        "class": CLASS_QUERY,
        "import": IMPORT_QUERY,
        "main_guard": MAIN_GUARD_QUERY,
        "call": CALL_QUERY,
        "parameter": PARAMETER_QUERY,
    }
