"""Tree-sitter queries for Ruby.

Extracts:
    - Method definitions (including singleton methods)
    - Class and module definitions
    - Require statements (imports)
"""

# Query for method definitions
FUNCTION_QUERY = """
(method
    name: (identifier) @method.name
    parameters: (method_parameters)? @method.params
) @method

(singleton_method
    object: (_) @singleton.object
    name: (identifier) @singleton.name
    parameters: (method_parameters)? @singleton.params
) @singleton
"""

# Query for class/module definitions
CLASS_QUERY = """
(class
    name: (constant) @class.name
    superclass: (superclass
        (scope_resolution)? @class.extends
    )?
) @class

(module
    name: (constant) @module.name
) @module
"""

# Query for imports
IMPORT_QUERY = """
(call
    method: (identifier) @require_method
    arguments: (argument_list
        (string
            (string_content) @require.path
        )
    )
    (#match? @require_method "^require")
) @require

(call
    method: (identifier) @require_relative_method
    arguments: (argument_list
        (string
            (string_content) @require_relative.path
        )
    )
    (#eq? @require_relative_method "require_relative")
) @require_relative
"""

# Query for call expressions
CALL_QUERY = """
(call
    method: (identifier) @call.method
) @call

(call
    receiver: (_) @call.receiver
    method: (identifier) @call.method_name
) @call.method_call
"""

# Query for parameters
PARAMETER_QUERY = """
(method_parameters
    (identifier) @param
)

(method_parameters
    (optional_parameter
        name: (identifier) @optional_param
    )
)

(method_parameters
    (splat_parameter
        name: (identifier) @splat_param
    )
)

(method_parameters
    (block_parameter
        name: (identifier) @block_param
    )
)
"""


def get_all_queries() -> dict[str, str]:
    """Return all Ruby queries as a dict."""
    return {
        "function": FUNCTION_QUERY,
        "class": CLASS_QUERY,
        "import": IMPORT_QUERY,
        "call": CALL_QUERY,
        "parameter": PARAMETER_QUERY,
    }
