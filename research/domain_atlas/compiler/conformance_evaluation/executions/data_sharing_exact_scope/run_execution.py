from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any, Callable

from implementation_functional import FunctionalSharingContract, Refusal as FunctionalRefusal
from implementation_reducer import ReducerSharingContract, Refusal as ReducerRefusal

HERE = Path(__file__).resolve().parent


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode()).hexdigest()


def source_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def setup(impl: Any, *, authorized: bool = True) -> None:
    impl.draft_share(share_id="share.orders", edition=1, provider_ref="provider.acme", provider_authorized=authorized, source_semantic_owner="semantic.orders")
    impl.resolve_shared_cut(cut_id="cut.orders.2026-08-27", object_ids=["orders", "order_lines"], source_semantic_owner="semantic.orders", source_valid_cut="2026-08-27T00:00:00Z", source_recording_cut="2026-08-27T00:05:00Z")
    if authorized:
        impl.publish_share(cut_id="cut.orders.2026-08-27", policy_edition="policy.share.v1")
        impl.register_recipient(recipient_ref="recipient.analytics")
        impl.bind_purpose(purpose_ref="purpose.demand_forecast")


def case_happy_path(impl: Any) -> dict[str, Any]:
    setup(impl)
    impl.adjudicate_grant(grant_id="grant.1", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", object_ids=["orders"], policy_allowed=True, expires_at=100)
    impl.create_subscription(subscription_id="sub.1", grant_id="grant.1")
    impl.record_disclosure(receipt_id="receipt.1", grant_id="grant.1", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", cut_id="cut.orders.2026-08-27", policy_edition="policy.share.v1", at_time=10)
    return impl.export_share()


def case_revocation_monotone(impl: Any) -> dict[str, Any]:
    setup(impl)
    impl.adjudicate_grant(grant_id="grant.1", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", object_ids=["orders"], policy_allowed=True, expires_at=100)
    impl.record_disclosure(receipt_id="receipt.before", grant_id="grant.1", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", cut_id="cut.orders.2026-08-27", policy_edition="policy.share.v1", at_time=10)
    impl.revoke_grant(grant_id="grant.1", revocation_id="revoke.1", at_time=20)
    try:
        impl.record_disclosure(receipt_id="receipt.after", grant_id="grant.1", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", cut_id="cut.orders.2026-08-27", policy_edition="policy.share.v1", at_time=30)
    except Exception as exc:
        if getattr(exc, "code", None) != "grant_expired_or_revoked":
            raise
    else:
        raise AssertionError("revoked grant authorized a new disclosure")
    exported = impl.export_share()
    assert "receipt.before" in exported["disclosures"] and "receipt.after" not in exported["disclosures"]
    return exported


def case_recall_residuals(impl: Any) -> dict[str, Any]:
    setup(impl)
    impl.adjudicate_grant(grant_id="grant.1", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", object_ids=["orders"], policy_allowed=True, expires_at=100)
    impl.record_disclosure(receipt_id="receipt.1", grant_id="grant.1", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", cut_id="cut.orders.2026-08-27", policy_edition="policy.share.v1", at_time=10)
    impl.recall_cut(cut_id="cut.orders.2026-08-27", recall_id="recall.1", at_time=20)
    exported = impl.export_share()
    assert exported["recalls"]["recall.1"]["unresolved_recipient_refs"] == ["recipient.analytics"]
    try:
        impl.record_disclosure(receipt_id="receipt.2", grant_id="grant.1", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", cut_id="cut.orders.2026-08-27", policy_edition="policy.share.v1", at_time=30)
    except Exception as exc:
        if getattr(exc, "code", None) != "recall_incomplete":
            raise
    else:
        raise AssertionError("recalled cut authorized a new disclosure")
    return exported


def refusal_case(factory: Callable[[], Any], setup_fn: Callable[[Any], None], action: Callable[[Any], None], expected: str) -> str:
    impl = factory()
    setup_fn(impl)
    try:
        action(impl)
    except Exception as exc:
        code = getattr(exc, "code", None)
        if code != expected:
            raise AssertionError(f"expected {expected}, got {code}") from exc
        return code
    raise AssertionError(f"expected refusal {expected}")


def run_for(name: str, factory: Callable[[], Any]) -> dict[str, Any]:
    cases = []
    for case_id, fn in [("happy_path", case_happy_path), ("revocation_monotone", case_revocation_monotone), ("recall_retains_residuals", case_recall_residuals)]:
        impl = factory()
        value = fn(impl)
        cases.append({"case_id": case_id, "verdict": "PASS", "result_digest": digest(value)})

    negatives = [
        ("provider_authority_missing", lambda i: setup(i, authorized=False), lambda i: i.publish_share(cut_id="cut.orders.2026-08-27", policy_edition="policy.share.v1"), "provider_authority_missing"),
        ("recipient_unresolved", setup, lambda i: i.adjudicate_grant(grant_id="g", recipient_ref="missing", purpose_ref="purpose.demand_forecast", object_ids=["orders"], policy_allowed=True, expires_at=100), "recipient_unresolved"),
        ("purpose_unbound", lambda i: (setup(i), i.register_recipient(recipient_ref="r")), lambda i: i.adjudicate_grant(grant_id="g", recipient_ref="r", purpose_ref="missing", object_ids=["orders"], policy_allowed=True, expires_at=100), "purpose_unbound"),
        ("policy_refused", setup, lambda i: i.adjudicate_grant(grant_id="g", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", object_ids=["orders"], policy_allowed=False, expires_at=100), "policy_refused"),
        ("shared_cut_unresolved", lambda i: i.draft_share(share_id="s", edition=1, provider_ref="p", provider_authorized=True, source_semantic_owner="semantic.orders"), lambda i: i.publish_share(cut_id="missing", policy_edition="p1"), "shared_cut_unresolved"),
        ("grant_expired_or_revoked", lambda i: (setup(i), i.adjudicate_grant(grant_id="g", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", object_ids=["orders"], policy_allowed=True, expires_at=10)), lambda i: i.record_disclosure(receipt_id="r", grant_id="g", recipient_ref="recipient.analytics", purpose_ref="purpose.demand_forecast", cut_id="cut.orders.2026-08-27", policy_edition="policy.share.v1", at_time=10), "grant_expired_or_revoked"),
        ("export_incomplete", lambda i: i.draft_share(share_id="s", edition=1, provider_ref="p", provider_authorized=True, source_semantic_owner="semantic.orders"), lambda i: i.export_share(), "export_incomplete"),
    ]
    for case_id, setup_fn, action, expected in negatives:
        code = refusal_case(factory, setup_fn, action, expected)
        cases.append({"case_id": case_id, "verdict": "PASS", "refusal": code})

    owner = case_happy_path(factory())["cuts"]["cut.orders.2026-08-27"]["source_semantic_owner"]
    if owner != "semantic.orders":
        raise AssertionError("source semantic ownership transferred")
    cases.append({"case_id": "source_semantic_owner_preserved", "verdict": "PASS", "owner": owner})

    first = case_happy_path(factory())
    second = case_happy_path(factory())
    if digest(first) != digest(second):
        raise AssertionError("deterministic replay mismatch")
    cases.append({"case_id": "deterministic_replay", "verdict": "PASS", "result_digest": digest(first)})
    return {"implementation": name, "case_count": len(cases), "cases": cases, "verdict": "PASS"}


def main() -> int:
    impls = [run_for("functional_copy_on_write", FunctionalSharingContract), run_for("append_only_event_reducer", ReducerSharingContract)]
    differential = []
    for case_id, fn in [("happy_path", case_happy_path), ("revocation_monotone", case_revocation_monotone), ("recall_retains_residuals", case_recall_residuals)]:
        a = fn(FunctionalSharingContract())
        b = fn(ReducerSharingContract())
        if canonical(a) != canonical(b):
            raise AssertionError(f"differential mismatch: {case_id}")
        differential.append({"case_id": case_id, "verdict": "PASS", "result_digest": digest(a)})

    receipt = {
        "record_kind": "data_sharing_exact_scope_execution_receipt",
        "edition": 1,
        "as_of": "2026-08-27",
        "contract_ref": "library.data_sharing_contract",
        "canonical_projection_ref": "library.persistence.sharing_contract",
        "product_ref": "product.data_sharing_exchange",
        "scope": {
            "contract_decisions": ["cut_resolution_policy", "recipient_binding_policy", "purpose_binding_policy", "grant_scope_policy", "revocation_policy", "recall_policy", "export_policy"],
            "operations": ["draft_share", "publish_share", "resolve_shared_cut", "adjudicate_grant", "create_subscription", "record_disclosure", "revoke_grant", "recall_cut", "export_share"],
            "invariants": ["share grant subscription disclosure and consumption are distinct", "every disclosure binds exact cut recipient purpose grant and policy", "revoked grants authorize no new disclosure", "source semantic ownership never transfers", "recall retains unresolved downstream residuals"],
            "refusals_exercised": ["provider_authority_missing", "shared_cut_unresolved", "recipient_unresolved", "purpose_unbound", "policy_refused", "grant_expired_or_revoked", "recall_incomplete", "export_incomplete"]
        },
        "implementation_controls": {"independently_controlled": False, "reason": "Both reference implementations are authored in this one research execution campaign; this evidence cannot satisfy the second-independent-implementation or independent-appraisal gates."},
        "environment": {"python": sys.version.split()[0], "implementation": platform.python_implementation(), "platform": platform.platform()},
        "source_digests": {
            "implementation_functional.py": source_digest(HERE / "implementation_functional.py"),
            "implementation_reducer.py": source_digest(HERE / "implementation_reducer.py"),
            "run_execution.py": source_digest(HERE / "run_execution.py")
        },
        "implementations": impls,
        "differential": differential,
        "verdict": "PASS_EXECUTED_TESTS_NOT_QUALIFIED",
        "promotion_claims": {"implementation_qualified": False, "portable_offer": False, "product_build_ready": False, "product_ratified": False}
    }
    out = HERE / "runs" / "run-20260827-linux-x86_64-python3_13-001" / "receipt.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tracked = [HERE / "README.md", HERE / "implementation_functional.py", HERE / "implementation_reducer.py", HERE / "protocol.json", HERE / "qualification-binding.json", HERE / "run_execution.py", HERE / "validate_execution.py", out]
    manifest = {
        "manifest_id": "manifest.data_sharing_exact_scope.edition1",
        "edition": 1,
        "as_of": "2026-08-27",
        "files": {str(path.relative_to(HERE)): {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": len(path.read_bytes())} for path in tracked},
        "counts": {"implementations": len(impls), "implementation_cases": sum(x["case_count"] for x in impls), "differential_cases": len(differential), "refusal_classes": len(receipt["scope"]["refusals_exercised"])},
        "qualification_claim": False
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {sum(x['case_count'] for x in impls)} implementation cases + {len(differential)} differential cases; not qualified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
