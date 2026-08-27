from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


class Refusal(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _initial_state() -> dict[str, Any]:
    return {
        "share": None,
        "cuts": {},
        "recipients": {},
        "purposes": {},
        "grants": {},
        "subscriptions": {},
        "disclosures": {},
        "revocations": {},
        "recalls": {},
    }


class FunctionalSharingContract:
    """Pure copy-on-write implementation of the abstract data-sharing contract."""

    def __init__(self) -> None:
        self.state = _initial_state()

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self.state)

    def _commit(self, state: dict[str, Any]) -> dict[str, Any]:
        self.state = state
        return self.snapshot()

    def draft_share(self, *, share_id: str, edition: int, provider_ref: str, provider_authorized: bool, source_semantic_owner: str) -> dict[str, Any]:
        state = self.snapshot()
        state["share"] = {
            "share_id": share_id,
            "edition": edition,
            "provider_ref": provider_ref,
            "provider_authorized": bool(provider_authorized),
            "source_semantic_owner": source_semantic_owner,
            "status": "draft",
        }
        return self._commit(state)

    def resolve_shared_cut(self, *, cut_id: str, object_ids: list[str], source_semantic_owner: str, source_valid_cut: str, source_recording_cut: str) -> dict[str, Any]:
        if not cut_id or not object_ids or not source_valid_cut or not source_recording_cut:
            raise Refusal("shared_cut_unresolved")
        state = self.snapshot()
        share = state.get("share")
        if not share:
            raise Refusal("shared_cut_unresolved")
        if source_semantic_owner != share["source_semantic_owner"]:
            raise Refusal("shared_cut_unresolved")
        state["cuts"][cut_id] = {
            "cut_id": cut_id,
            "object_ids": sorted(set(object_ids)),
            "source_semantic_owner": source_semantic_owner,
            "source_valid_cut": source_valid_cut,
            "source_recording_cut": source_recording_cut,
            "recalled": False,
        }
        return self._commit(state)

    def publish_share(self, *, cut_id: str, policy_edition: str) -> dict[str, Any]:
        state = self.snapshot()
        share = state.get("share")
        if not share or not share.get("provider_authorized"):
            raise Refusal("provider_authority_missing")
        if cut_id not in state["cuts"]:
            raise Refusal("shared_cut_unresolved")
        share["status"] = "published"
        share["cut_id"] = cut_id
        share["policy_edition"] = policy_edition
        return self._commit(state)

    def register_recipient(self, *, recipient_ref: str) -> dict[str, Any]:
        state = self.snapshot()
        if not recipient_ref:
            raise Refusal("recipient_unresolved")
        state["recipients"][recipient_ref] = {"recipient_ref": recipient_ref}
        return self._commit(state)

    def bind_purpose(self, *, purpose_ref: str) -> dict[str, Any]:
        state = self.snapshot()
        if not purpose_ref:
            raise Refusal("purpose_unbound")
        state["purposes"][purpose_ref] = {"purpose_ref": purpose_ref}
        return self._commit(state)

    def adjudicate_grant(self, *, grant_id: str, recipient_ref: str, purpose_ref: str, object_ids: list[str], policy_allowed: bool, expires_at: int) -> dict[str, Any]:
        state = self.snapshot()
        share = state.get("share")
        if not share or share.get("status") != "published":
            raise Refusal("provider_authority_missing")
        if recipient_ref not in state["recipients"]:
            raise Refusal("recipient_unresolved")
        if purpose_ref not in state["purposes"]:
            raise Refusal("purpose_unbound")
        if not policy_allowed:
            raise Refusal("policy_refused")
        cut = state["cuts"].get(share["cut_id"])
        if not cut:
            raise Refusal("shared_cut_unresolved")
        if cut["recalled"]:
            raise Refusal("recall_incomplete")
        requested = sorted(set(object_ids))
        if not set(requested).issubset(set(cut["object_ids"])):
            raise Refusal("policy_refused")
        state["grants"][grant_id] = {
            "grant_id": grant_id,
            "recipient_ref": recipient_ref,
            "purpose_ref": purpose_ref,
            "object_ids": requested,
            "cut_id": cut["cut_id"],
            "policy_edition": share["policy_edition"],
            "expires_at": int(expires_at),
            "revoked": False,
        }
        return self._commit(state)

    def create_subscription(self, *, subscription_id: str, grant_id: str) -> dict[str, Any]:
        state = self.snapshot()
        grant = state["grants"].get(grant_id)
        if not grant or grant["revoked"]:
            raise Refusal("grant_expired_or_revoked")
        state["subscriptions"][subscription_id] = {
            "subscription_id": subscription_id,
            "grant_id": grant_id,
            "cut_id": grant["cut_id"],
        }
        return self._commit(state)

    def record_disclosure(self, *, receipt_id: str, grant_id: str, recipient_ref: str, purpose_ref: str, cut_id: str, policy_edition: str, at_time: int) -> dict[str, Any]:
        state = self.snapshot()
        grant = state["grants"].get(grant_id)
        if not grant or grant["revoked"] or int(at_time) >= grant["expires_at"]:
            raise Refusal("grant_expired_or_revoked")
        cut = state["cuts"].get(cut_id)
        if not cut:
            raise Refusal("shared_cut_unresolved")
        if cut["recalled"]:
            raise Refusal("recall_incomplete")
        if recipient_ref != grant["recipient_ref"]:
            raise Refusal("recipient_unresolved")
        if purpose_ref != grant["purpose_ref"]:
            raise Refusal("purpose_unbound")
        if cut_id != grant["cut_id"] or policy_edition != grant["policy_edition"]:
            raise Refusal("policy_refused")
        state["disclosures"][receipt_id] = {
            "receipt_id": receipt_id,
            "grant_id": grant_id,
            "recipient_ref": recipient_ref,
            "purpose_ref": purpose_ref,
            "cut_id": cut_id,
            "policy_edition": policy_edition,
            "at_time": int(at_time),
            "source_semantic_owner": cut["source_semantic_owner"],
        }
        return self._commit(state)

    def revoke_grant(self, *, grant_id: str, revocation_id: str, at_time: int) -> dict[str, Any]:
        state = self.snapshot()
        grant = state["grants"].get(grant_id)
        if not grant:
            raise Refusal("grant_expired_or_revoked")
        grant["revoked"] = True
        state["revocations"][revocation_id] = {
            "revocation_id": revocation_id,
            "grant_id": grant_id,
            "at_time": int(at_time),
        }
        return self._commit(state)

    def recall_cut(self, *, cut_id: str, recall_id: str, at_time: int) -> dict[str, Any]:
        state = self.snapshot()
        cut = state["cuts"].get(cut_id)
        if not cut:
            raise Refusal("shared_cut_unresolved")
        cut["recalled"] = True
        recipients = sorted({d["recipient_ref"] for d in state["disclosures"].values() if d["cut_id"] == cut_id})
        state["recalls"][recall_id] = {
            "recall_id": recall_id,
            "cut_id": cut_id,
            "at_time": int(at_time),
            "unresolved_recipient_refs": recipients,
        }
        return self._commit(state)

    def export_share(self) -> dict[str, Any]:
        state = self.snapshot()
        if not state.get("share") or state["share"].get("status") != "published":
            raise Refusal("export_incomplete")
        return {
            "share": deepcopy(state["share"]),
            "cuts": deepcopy(state["cuts"]),
            "grants": deepcopy(state["grants"]),
            "subscriptions": deepcopy(state["subscriptions"]),
            "disclosures": deepcopy(state["disclosures"]),
            "revocations": deepcopy(state["revocations"]),
            "recalls": deepcopy(state["recalls"]),
        }
