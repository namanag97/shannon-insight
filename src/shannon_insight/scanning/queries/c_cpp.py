"""Tree-sitter queries for C and C++.

Extracts:
    - Function definitions
    - Struct/class definitions (C++ classes)
    - Include directives (imports)

Note: Uses C grammar which handles most C++ constructs.
C++ specific features (namespaces, templates) use the cpp grammar.
"""

# Query for function definitions (works for both C and C++)
FUNCTION_QUERY = """
(function_definition
    declarator: (function_declarator
        declarator: (identifier) @function.name
        parameters: (parameter_list) @function.params
    )
    body: (compound_statement) @function.body
) @function

(function_definition
    declarator: (pointer_declarator
        declarator: (function_declarator
            declarator: (identifier) @ptr_function.name
            parameters: (parameter_list) @ptr_function.params
        )
    )
    body: (compound_statement) @ptr_function.body
) @ptr_function
"""

# C++ specific function query
FUNCTION_QUERY_CPP = """
(function_definition
    declarator: (function_declarator
        declarator: (qualified_identifier
            name: (identifier) @method.name
        )
        parameters: (parameter_list) @method.params
    )
    body: (compound_statement) @method.body
) @method
"""

# Query for struct/class definitions
CLASS_QUERY = """
(struct_specifier
    name: (type_identifier) @struct.name
    body: (field_declaration_list) @struct.body
) @struct

(union_specifier
    name: (type_identifier) @union.name
    body: (field_declaration_list) @union.body
) @union

(enum_specifier
    name: (type_identifier) @enum.name
    body: (enumerator_list) @enum.body
) @enum
"""

# C++ class query
CLASS_QUERY_CPP = """
(class_specifier
    name: (type_identifier) @class.name
    body: (field_declaration_list) @class.body
) @class

(class_specifier
    name: (type_identifier) @derived.name
    (base_class_clause
        (type_identifier) @derived.base
    )
    body: (field_declaration_list) @derived.body
) @derived
"""

# Query for includes
IMPORT_QUERY = """
(preproc_include
    path: (system_lib_string) @include.system
) @include_system

(preproc_include
    path: (string_literal) @include.local
) @include_local
"""

# Query for call expressions
CALL_QUERY = """
(call_expression
    function: (identifier) @call.function
    arguments: (argument_list) @call.args
) @call

(call_expression
    function: (field_expression
        argument: (_) @call.object
        field: (field_identifier) @call.method
    )
) @call.method_call
"""

# Query for parameters
PARAMETER_QUERY = """
(parameter_list
    (parameter_declaration
        declarator: (identifier) @param
    )
)

(parameter_list
    (parameter_declaration
        declarator: (pointer_declarator
            declarator: (identifier) @ptr_param
        )
    )
)
"""


def get_all_queries() -> dict[str, str]:
    """Return all C/C++ queries as a dict."""
    return {
        "function": FUNCTION_QUERY,
        "function_cpp": FUNCTION_QUERY_CPP,
        "class": CLASS_QUERY,
        "class_cpp": CLASS_QUERY_CPP,
        "import": IMPORT_QUERY,
        "call": CALL_QUERY,
        "parameter": PARAMETER_QUERY,
    }
