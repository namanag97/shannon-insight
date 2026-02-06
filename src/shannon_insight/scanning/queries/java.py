"""Tree-sitter queries for Java.

Extracts:
    - Method definitions (including constructors)
    - Class definitions (with extends, implements, abstract)
    - Import declarations
"""

# Query for method definitions
FUNCTION_QUERY = """
(method_declaration
    name: (identifier) @method.name
    parameters: (formal_parameters) @method.params
    body: (block) @method.body
) @method

(constructor_declaration
    name: (identifier) @constructor.name
    parameters: (formal_parameters) @constructor.params
    body: (constructor_body) @constructor.body
) @constructor
"""

# Query for class definitions
CLASS_QUERY = """
(class_declaration
    name: (identifier) @class.name
    superclass: (superclass
        (type_identifier) @class.extends
    )?
    interfaces: (super_interfaces
        (type_list
            (type_identifier) @class.implements
        )
    )?
    body: (class_body) @class.body
) @class

(interface_declaration
    name: (identifier) @interface.name
    body: (interface_body) @interface.body
) @interface

(enum_declaration
    name: (identifier) @enum.name
    body: (enum_body) @enum.body
) @enum
"""

# Query for imports
IMPORT_QUERY = """
(import_declaration
    (scoped_identifier) @import.name
) @import
"""

# Query for call expressions
CALL_QUERY = """
(method_invocation
    name: (identifier) @call.method
    arguments: (argument_list) @call.args
) @call

(method_invocation
    object: (_) @call.object
    name: (identifier) @call.method_name
) @call.method_call
"""

# Query for parameters
PARAMETER_QUERY = """
(formal_parameters
    (formal_parameter
        name: (identifier) @param
    )
)

(formal_parameters
    (spread_parameter
        (variable_declarator
            name: (identifier) @varargs_param
        )
    )
)
"""

# Query for modifiers (to detect abstract)
MODIFIER_QUERY = """
(modifiers
    (modifier) @modifier
)
"""


def get_all_queries() -> dict[str, str]:
    """Return all Java queries as a dict."""
    return {
        "function": FUNCTION_QUERY,
        "class": CLASS_QUERY,
        "import": IMPORT_QUERY,
        "call": CALL_QUERY,
        "parameter": PARAMETER_QUERY,
        "modifier": MODIFIER_QUERY,
    }
