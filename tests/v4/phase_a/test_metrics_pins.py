"""Gate G3: metric math pins (exact values)."""

from shannon_insight.syntax.models import (
    FunctionDef,
    compute_impl_gini,
    compute_stub_ratio,
)


def _fn(body_tokens: int, sig_tokens: int = 10) -> FunctionDef:
    return FunctionDef(
        name="f",
        params=(),
        start_line=1,
        end_line=2,
        body_tokens=body_tokens,
        signature_tokens=sig_tokens,
        nesting_depth=0,
        cyclomatic=1,
    )


class TestStubScore:
    def test_saturated_body_is_not_stub(self):
        assert _fn(30, 10).stub_score == 0.0

    def test_empty_body_is_full_stub(self):
        assert _fn(0, 10).stub_score == 1.0

    def test_halfway_body(self):
        assert _fn(15, 10).stub_score == 0.5

    def test_zero_signature_saturates(self):
        # No signature tokens => ratio saturates instantly: body is
        # "infinitely implemented" relative to an empty declaration.
        fn = FunctionDef(
            name="f", params=(), start_line=1, end_line=1,
            body_tokens=5, signature_tokens=0,
            nesting_depth=0, cyclomatic=1,
        )
        assert fn.stub_score == 0.0


class TestGini:
    def test_equal_sizes_zero(self):
        fns = (_fn(50), _fn(50), _fn(50))
        assert compute_impl_gini(fns) == 0.0

    def test_known_pair_value(self):
        # [1, 2] => G = 1/6
        g = compute_impl_gini((_fn(1), _fn(2)))
        assert abs(g - 0.1667) <= 0.0005

    def test_bimodal_exact(self):
        # [100, 1, 1] => G = 198/306 = 0.647058...
        g = compute_impl_gini((_fn(100), _fn(1), _fn(1)))
        assert abs(g - 0.6471) <= 0.0005

    def test_single_function_zero(self):
        assert compute_impl_gini((_fn(999),)) == 0.0

    def test_all_empty_zero(self):
        assert compute_impl_gini((_fn(0), _fn(0))) == 0.0


class TestAggregates:
    def test_stub_ratio_mix(self):
        fns = (_fn(0), _fn(30), _fn(30))
        assert compute_stub_ratio(fns) == round((1.0 + 0 + 0) / 3, 4)
