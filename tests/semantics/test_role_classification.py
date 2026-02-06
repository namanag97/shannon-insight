"""Tests for role classification decision tree."""

from shannon_insight.scanning.models_v2 import ClassDef, FileSyntax, FunctionDef, ImportDecl
from shannon_insight.semantics import Role, classify_role


def make_syntax(
    path: str = "test.py",
    functions: list[FunctionDef] | None = None,
    classes: list[ClassDef] | None = None,
    imports: list[ImportDecl] | None = None,
    language: str = "python",
    has_main_guard: bool = False,
) -> FileSyntax:
    """Helper to create FileSyntax for testing."""
    return FileSyntax(
        path=path,
        functions=functions or [],
        classes=classes or [],
        imports=imports or [],
        language=language,
        has_main_guard=has_main_guard,
    )


def make_function(
    name: str = "foo",
    decorators: list[str] | None = None,
    params: list[str] | None = None,
) -> FunctionDef:
    """Helper to create FunctionDef for testing."""
    return FunctionDef(
        name=name,
        params=params or [],
        body_tokens=10,
        signature_tokens=5,
        nesting_depth=1,
        start_line=1,
        end_line=5,
        call_targets=None,
        decorators=decorators or [],
    )


def make_class(
    name: str = "Foo",
    bases: list[str] | None = None,
    methods: list[FunctionDef] | None = None,
    fields: list[str] | None = None,
    is_abstract: bool = False,
) -> ClassDef:
    """Helper to create ClassDef for testing."""
    return ClassDef(
        name=name,
        bases=bases or [],
        methods=methods or [],
        fields=fields or [],
        is_abstract=is_abstract,
    )


class TestRoleClassificationTestFiles:
    """Test TEST role classification."""

    def test_test_prefix(self):
        """Files starting with test_ are TEST."""
        syntax = make_syntax(path="test_something.py")
        assert classify_role(syntax) == Role.TEST

    def test_test_suffix(self):
        """Files ending with _test.py are TEST."""
        syntax = make_syntax(path="something_test.py")
        assert classify_role(syntax) == Role.TEST

    def test_tests_directory(self):
        """Files in tests/ directory are TEST."""
        syntax = make_syntax(path="tests/test_foo.py")
        assert classify_role(syntax) == Role.TEST

    def test_spec_directory(self):
        """Files in spec/ directory are TEST."""
        syntax = make_syntax(path="spec/foo_spec.py")
        assert classify_role(syntax) == Role.TEST


class TestRoleClassificationEntryPoint:
    """Test ENTRY_POINT role classification."""

    def test_main_guard(self):
        """Files with __main__ guard are ENTRY_POINT."""
        syntax = make_syntax(has_main_guard=True)
        assert classify_role(syntax) == Role.ENTRY_POINT

    def test_click_command(self):
        """Files with @click.command are ENTRY_POINT."""
        fn = make_function(decorators=["click.command"])
        syntax = make_syntax(functions=[fn])
        assert classify_role(syntax) == Role.ENTRY_POINT

    def test_main_decorator(self):
        """Files with @main decorator are ENTRY_POINT."""
        fn = make_function(decorators=["main"])
        syntax = make_syntax(functions=[fn])
        assert classify_role(syntax) == Role.ENTRY_POINT


class TestRoleClassificationInterface:
    """Test INTERFACE role classification."""

    def test_abc_base(self):
        """Classes inheriting from ABC are INTERFACE."""
        cls = make_class(bases=["ABC"])
        syntax = make_syntax(classes=[cls])
        assert classify_role(syntax) == Role.INTERFACE

    def test_protocol_base(self):
        """Classes inheriting from Protocol are INTERFACE."""
        cls = make_class(bases=["Protocol"])
        syntax = make_syntax(classes=[cls])
        assert classify_role(syntax) == Role.INTERFACE

    def test_is_abstract_flag(self):
        """Classes with is_abstract=True are INTERFACE."""
        cls = make_class(is_abstract=True)
        syntax = make_syntax(classes=[cls])
        assert classify_role(syntax) == Role.INTERFACE

    def test_abstractmethod_decorator(self):
        """Functions with @abstractmethod are INTERFACE."""
        fn = make_function(decorators=["abstractmethod"])
        syntax = make_syntax(functions=[fn])
        assert classify_role(syntax) == Role.INTERFACE


class TestRoleClassificationConstant:
    """Test CONSTANT role classification."""

    def test_all_upper_snake(self):
        """Files with all UPPER_SNAKE_CASE names are CONSTANT."""
        fn1 = make_function(name="MAX_VALUE")
        fn2 = make_function(name="MIN_VALUE")
        syntax = make_syntax(functions=[fn1, fn2])
        assert classify_role(syntax) == Role.CONSTANT

    def test_mixed_case_not_constant(self):
        """Files with mixed case names are not CONSTANT."""
        fn1 = make_function(name="MAX_VALUE")
        fn2 = make_function(name="helper_function")
        syntax = make_syntax(functions=[fn1, fn2])
        assert classify_role(syntax) != Role.CONSTANT


class TestRoleClassificationException:
    """Test EXCEPTION role classification."""

    def test_exception_base(self):
        """Classes inheriting from Exception are EXCEPTION."""
        cls1 = make_class(name="MyError", bases=["Exception"])
        cls2 = make_class(name="OtherError", bases=["Exception"])
        syntax = make_syntax(classes=[cls1, cls2])
        assert classify_role(syntax) == Role.EXCEPTION

    def test_error_suffix_base(self):
        """Classes with Error in base are EXCEPTION."""
        cls = make_class(name="CustomError", bases=["ValueError"])
        syntax = make_syntax(classes=[cls])
        assert classify_role(syntax) == Role.EXCEPTION


class TestRoleClassificationModel:
    """Test MODEL role classification."""

    def test_basemodel_inheritance(self):
        """Classes inheriting from BaseModel are MODEL."""
        cls = make_class(bases=["BaseModel"])
        syntax = make_syntax(classes=[cls])
        assert classify_role(syntax) == Role.MODEL

    def test_field_heavy_class(self):
        """Classes with many fields and few methods are MODEL."""
        cls = make_class(
            fields=["field1", "field2", "field3", "field4"],
            methods=[make_function(name="__init__")],
        )
        syntax = make_syntax(classes=[cls])
        assert classify_role(syntax) == Role.MODEL


class TestRoleClassificationCLI:
    """Test CLI role classification."""

    def test_route_decorator(self):
        """Files with @app.route are CLI."""
        fn = make_function(decorators=["app.route"])
        syntax = make_syntax(functions=[fn])
        assert classify_role(syntax) == Role.CLI


class TestRoleClassificationService:
    """Test SERVICE role classification."""

    def test_handler_inheritance(self):
        """Classes inheriting from Handler are SERVICE."""
        cls = make_class(bases=["BaseHTTPRequestHandler"])
        syntax = make_syntax(classes=[cls])
        assert classify_role(syntax) == Role.SERVICE

    def test_stateful_class(self):
        """Classes with methods (non-dunder) are SERVICE."""
        cls = make_class(methods=[make_function(name="process")])
        syntax = make_syntax(classes=[cls])
        assert classify_role(syntax) == Role.SERVICE


class TestRoleClassificationUtility:
    """Test UTILITY role classification."""

    def test_functions_only(self):
        """Files with only functions (no classes) are UTILITY."""
        fn1 = make_function(name="helper1")
        fn2 = make_function(name="helper2")
        syntax = make_syntax(functions=[fn1, fn2])
        assert classify_role(syntax) == Role.UTILITY


class TestRoleClassificationConfig:
    """Test CONFIG role classification."""

    def test_init_file(self):
        """__init__.py files are CONFIG."""
        syntax = make_syntax(path="package/__init__.py")
        assert classify_role(syntax) == Role.CONFIG

    def test_imports_only(self):
        """Files with only imports are CONFIG."""
        imports = [ImportDecl(source="os", names=["path"])]
        syntax = make_syntax(imports=imports)
        assert classify_role(syntax) == Role.CONFIG

    def test_config_filename(self):
        """Files named config.py are CONFIG."""
        syntax = make_syntax(path="config.py")
        assert classify_role(syntax) == Role.CONFIG


class TestRoleClassificationUnknown:
    """Test UNKNOWN role classification."""

    def test_empty_file(self):
        """Empty files are UNKNOWN."""
        syntax = make_syntax()
        assert classify_role(syntax) == Role.UNKNOWN


class TestRoleClassificationPriority:
    """Test priority order of role classification."""

    def test_test_over_main_guard(self):
        """TEST takes priority over ENTRY_POINT."""
        syntax = make_syntax(path="test_main.py", has_main_guard=True)
        assert classify_role(syntax) == Role.TEST

    def test_entry_point_over_interface(self):
        """ENTRY_POINT takes priority over INTERFACE."""
        cls = make_class(bases=["ABC"])
        syntax = make_syntax(classes=[cls], has_main_guard=True)
        assert classify_role(syntax) == Role.ENTRY_POINT

    def test_interface_over_utility(self):
        """INTERFACE takes priority over UTILITY."""
        fn = make_function(decorators=["abstractmethod"])
        syntax = make_syntax(functions=[fn])
        assert classify_role(syntax) == Role.INTERFACE
