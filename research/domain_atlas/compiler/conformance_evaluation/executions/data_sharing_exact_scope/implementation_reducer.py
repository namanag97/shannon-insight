from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class Refusal(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class ShareState:
    share: dict[str, Any] | None = None
    cuts: dict[str, dict[str, Any]] = field(default_factory=dict)
    recipients: set[str] = field(default_factory=set)
    purposes: set[str] = field(default_factory=set)
    grants: dict[str, dict[str, Any]] = field(default_factory=dict)
    subscriptions: dict[str, dict[str, Any]] = field(default_factory=dict)
    disclosures: dict[str, dict[str, Any]] = field(default_factory=dict)
    revocations: dict[str, dict[str, Any]] = field(default_factory=dict)
    recalls: dict[str, dict[str, Any]] = field(default_factory=dict)


class ReducerSharingContract:
    """Event-reducer implementation with state reconstructed from an append-only event log."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def _reduce(self) -> ShareState:
        state = ShareState()
        for event in self.events:
            kind = event["kind"]
            p = event["payload"]
            if kind == "share_drafted":
                state.share = dict(p)
            elif kind == "cut_resolved":
                state.cuts[p["cut_id"]] = dict(p)
            elif kind == "share_published":
                assert state.share is not None
                state.share.update({"status": "published", "cut_id": p["cut_id"], "policy_edition": p["policy_edition"]})
            elif kind == "recipient_registered":
                state.recipients.add(p["recipient_ref"])
            elif kind == "purpose_bound":
                state.purposes.add(p["purpose_ref"])
            elif kind == "grant_issued":
                state.grants[p["grant_id"]] = dict(p)
            elif kind == "subscription_created":
                state.subscriptions[p["subscription_id"]] = dict(p)
            elif kind == "disclosure_recorded":
                state.disclosures[p["receipt_id"]] = dict(p)
            elif kind == "grant_revoked":
                state.grants[p["grant_id"]]["revoked"] = True
                state.revocations[p["revocation_id"]] = dict(p)
            elif kind == "cut_recalled":
                state.cuts[p["cut_id"]]["recalled"] = True
                state.recalls[p["recall_id"]] = dict(p)
        return state

    def snapshot(self) -> dict[str, Any]:
        s = self._reduce()
        return {
            "share": None if s.share is None else dict(s.share),
            "cuts": {k: dict(v) for k, v in sorted(s.cuts.items())},
            "recipients": {k: {"recipient_ref": k} for k in sorted(s.recipients)},
            "purposes": {k: {"purpose_ref": k} for k in sorted(s.purposes)},
            "grants": {k: dict(v) for k, v in sorted(s.grants.items())},
            "subscriptions": {k: dict(v) for k, v in sorted(s.subscriptions.items())},
            "disclosures": {k: dict(v) for k, v in sorted(s.disclosures.items())},
            "revocations": {k: dict(v) for k, v in sorted(s.revocations.items())},
            "recalls": {k: dict(v) for k, v in sorted(s.recalls.items())},
        }

    def _append(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.events.append({"kind": kind, "payload": payload})
        return self.snapshot()

    def draft_share(self, *, share_id: str, edition: int, provider_ref: str, provider_authorized: bool, source_semantic_owner: str) -> dict[str, Any]:
        return self._append("share_drafted", {"share_id": share_id, "edition": edition, "provider_ref": provider_ref, "provider_authorized": bool(provider_authorized), "source_semantic_owner": source_semantic_owner, "status": "draft"})

    def resolve_shared_cut(self, *, cut_id: str, object_ids: list[str], source_semantic_owner: str, source_valid_cut: str, source_recording_cut: str) -> dict[str, Any]:
        s = self._reduce()
        if not cut_id or not object_ids or not source_valid_cut or not source_recording_cut or s.share is None or source_semantic_owner != s.share["source_semantic_owner"]:
            raise Refusal("shared_cut_unresolved")
        return self._append("cut_resolved", {"cut_id": cut_id, "object_ids": sorted(set(object_ids)), "source_semantic_owner": source_semantic_owner, "source_valid_cut": source_valid_cut, "source_recording_cut": source_recording_cut, "recalled": False})

    def publish_share(self, *, cut_id: str, policy_edition: str) -> dict[str, Any]:
        s = self._reduce()
        if s.share is None or not s.share.get("provider_authorized"):
            raise Refusal("provider_authority_missing")
        if cut_id not in s.cuts:
            raise Refusal("shared_cut_unresolved")
        return self._append("share_published", {"cut_id": cut_id, "policy_edition": policy_edition})

    def register_recipient(self, *, recipient_ref: str) -> dict[str, Any]:
        if not recipient_ref:
            raise Refusal("recipient_unresolved")
        return self._append("recipient_registered", {"recipient_ref": recipient_ref})

    def bind_purpose(self, *, purpose_ref: str) -> dict[str, Any]:
        if not purpose_ref:
            raise Refusal("purpose_unbound")
        return self._append("purpose_bound", {"purpose_ref": purpose_ref})

    def adjudicate_grant(self, *, grant_id: str, recipient_ref: str, purpose_ref: str, object_ids: list[str], policy_allowed: bool, expires_at: int) -> dict[str, Any]:
        s = self._reduce()
        if s.share is None or s.share.get("status") != "published":
            raise Refusal("provider_authority_missing")
        if recipient_ref not in s.recipients:
            raise Refusal("recipient_unresolved")
        if purpose_ref not in s.purposes:
            raise Refusal("purpose_unbound")
        if not policy_allowed:
            raise Refusal("policy_refused")
        cut = s.cuts.get(s.share["cut_id"])
        if cut is None:
            raise Refusal("shared_cut_unresolved")
        if cut["recalled"]:
            raise Refusal("recall_incomplete")
        requested = sorted(set(object_ids))
        if not set(requested).issubset(set(cut["object_ids"])):
            raise Refusal("policy_refused")
        return self._append("grant_issued", {"grant_id": grant_id, "recipient_ref": recipient_ref, "purpose_ref": purpose_ref, "object_ids": requested, "cut_id": cut["cut_id"], "policy_edition": s.share["policy_edition"], "expires_at": int(expires_at), "revoked": False})

    def create_subscription(self, *, subscription_id: str, grant_id: str) -> dict[str, Any]:
        s = self._reduce()
        grant = s.grants.get(grant_id)
        if grant is None or grant["revoked"]:
            raise Refusal("grant_expired_or_revoked")
        return self._append("subscription_created", {"subscription_id": subscription_id, "grant_id": grant_id, "cut_id": grant["cut_id"]})

    def record_disclosure(self, *, receipt_id: str, grant_id: str, recipient_ref: str, purpose_ref: str, cut_id: str, policy_edition: str, at_time: int) -> dict[str, Any]:
        s = self._reduce()
        grant = s.grants.get(grant_id)
        if grant is None or grant["revoked"] or int(at_time) >= grant["expires_at"]:
            raise Refusal("grant_expired_or_revoked")
        cut = s.cuts.get(cut_id)
        if cut is None:
            raise Refusal("shared_cut_unresolved")
        if cut["recalled"]:
            raise Refusal("recall_incomplete")
        if recipient_ref != grant["recipient_ref"]:
            raise Refusal("recipient_unresolved")
        if purpose_ref != grant["purpose_ref"]:
            raise Refusal("purpose_unbound")
        if cut_id != grant["cut_id"] or policy_edition != grant["policy_edition"]:
            raise Refusal("policy_refused")
        return self._append("disclosure_recorded", {"receipt_id": receipt_id, "grant_id": grant_id, "recipient_ref": recipient_ref, "purpose_ref": purpose_ref, "cut_id": cut_id, "policy_edition": policy_edition, "at_time": int(at_time), "source_semantic_owner": cut["source_semantic_owner"]})

    def revoke_grant(self, *, grant_id: str, revocation_id: str, at_time: int) -> dict[str, Any]:
        s = self._reduce()
        if grant_id not in s.grants:
            raise Refusal("grant_expired_or_revoked")
        return self._append("grant_revoked", {"revocation_id": revocation_id, "grant_id": grant_id, "at_time": int(at_time)})

    def recall_cut(self, *, cut_id: str, recall_id: str, at_time: int) -> dict[str, Any]:
        s = self._reduce()
        if cut_id not in s.cuts:
            raise Refusal("shared_cut_unresolved")
        recipients = sorted({d["recipient_ref"] for d in s.disclosures.values() if d["cut_id"] == cut_id})
        return self._append("cut_recalled", {"recall_id": recall_id, "cut_id": cut_id, "at_time": int(at_time), "unresolved_recipient_refs": recipients})

    def export_share(self) -> dict[str, Any]:
        s = self._reduce()
        if s.share is None or s.share.get("status") != "published":
            raise Refusal("export_incomplete")
        snap = self.snapshot()
        return {k: snap[k] for k in ("share", "cuts", "grants", "subscriptions", "disclosures", "revocations", "recalls")}
