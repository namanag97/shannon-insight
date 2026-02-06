"""Tree-sitter queries for Rust.

Extracts:
    - Function definitions (including methods, async)
    - Struct and enum definitions
    - Use declarations (imports)
"""

# Query for function definitions
FUNCTION_QUERY = """
(function_item
    name: (identifier) @function.name
    parameters: (parameters) @function.params
    body: (block) @function.body
) @function

(function_signature_item
    name: (identifier) @fn_sig.name
    parameters: (parameters) @fn_sig.params
) @fn_sig
"""

# Query for struct/enum definitions
CLASS_QUERY = """
(struct_item
    name: (type_identifier) @struct.name
    body: (field_declaration_list)? @struct.body
) @struct

(enum_item
    name: (type_identifier) @enum.name
    body: (enum_variant_list) @enum.body
) @enum

(impl_item
    trait: (type_identifier)? @impl.trait
    type: (type_identifier) @impl.type
    body: (declaration_list) @impl.body
) @impl

(trait_item
    name: (type_identifier) @trait.name
    body: (declaration_list) @trait.body
) @trait
"""

# Query for imports (use declarations)
IMPORT_QUERY = """
(use_declaration
    argument: (use_wildcard
        (scoped_identifier) @use.path
    )
) @use_wildcard

(use_declaration
    argument: (scoped_identifier) @use.scoped
) @use_scoped

(use_declaration
    argument: (identifier) @use.simple
) @use_simple

(use_declaration
    argument: (use_as_clause
        path: (scoped_identifier) @use_as.path
        alias: (identifier) @use_as.alias
    )
) @use_as
"""

# Query for call expressions
CALL_QUERY = """
(call_expression
    function: (identifier) @call.function
) @call

(call_expression
    function: (field_expression
        value: (_) @call.object
        field: (field_identifier) @call.method
    )
) @call.method_call

(call_expression
    function: (scoped_identifier) @call.scoped
) @call.scoped_call
"""

# Query for parameters
PARAMETER_QUERY = """
(parameters
    (parameter
        pattern: (identifier) @param
    )
)

(parameters
    (self_parameter) @self_param
)
"""


def get_all_queries() -> dict[str, str]:
    """Return all Rust queries as a dict."""
    return {
        "function": FUNCTION_QUERY,
        "class": CLASS_QUERY,
        "import": IMPORT_QUERY,
        "call": CALL_QUERY,
        "parameter": PARAMETER_QUERY,
    }
