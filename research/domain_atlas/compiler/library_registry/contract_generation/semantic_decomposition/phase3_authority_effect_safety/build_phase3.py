#!/usr/bin/env python3
"""Build the Phase-3 authority/effect/privacy/security/safety constitution candidate."""

from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
AS_OF = "2026-08-26"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build() -> dict[str, Any]:
    sources = [
        {"source_id":"source.semantic-phase3.oasis.xacml","publisher":"OASIS","source_kind":"standard","title":"XACML 3.0 Core","url":"https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-en.html","claim_scope":"PAP/PDP/PIP/PEP roles, decisions, obligations and combining algorithms","authority_limit":"Defines its authorization processing model, not issuer legitimacy, resource truth, consent, effect completion or business acceptance."},
        {"source_id":"source.semantic-phase3.nist.abac","publisher":"NIST","source_kind":"special_publication","title":"SP 800-162 Guide to Attribute Based Access Control","url":"https://csrc.nist.gov/pubs/sp/800/162/upd2/final","claim_scope":"subject, object, operation and environment attributes evaluated against access policy","authority_limit":"ABAC guidance does not establish attribute truth, policy-authoring authority, enforcement completion or all data-use semantics."},
        {"source_id":"source.semantic-phase3.w3c.odrl","publisher":"W3C","source_kind":"recommendation","title":"ODRL Information Model 2.2","url":"https://www.w3.org/TR/odrl-model/","claim_scope":"permissions, prohibitions, duties, constraints, parties, assets and conflict strategy","authority_limit":"ODRL expresses policies; it does not establish assigner authority, duty completion, legal applicability or enforcement evidence."},
        {"source_id":"source.semantic-phase3.ietf.http","publisher":"IETF","source_kind":"internet_standard","title":"RFC 9110 HTTP Semantics","url":"https://www.rfc-editor.org/rfc/rfc9110.html","claim_scope":"safe/idempotent method semantics and retry constraints after connection failure","authority_limit":"HTTP method idempotency concerns intended server effect; it does not prove exactly-once execution, suppress incidental effects or establish business idempotency."},
        {"source_id":"source.semantic-phase3.ietf.revocation","publisher":"IETF","source_kind":"internet_standard","title":"RFC 7009 OAuth 2.0 Token Revocation","url":"https://www.rfc-editor.org/rfc/rfc7009.html","claim_scope":"token revocation requests and invalidation behavior","authority_limit":"Token revocation does not erase prior effects, revoke every derived authority automatically or prove propagation to every enforcement point."},
        {"source_id":"source.semantic-phase3.nist.privacy","publisher":"NIST","source_kind":"framework","title":"NIST Privacy Framework 1.0","url":"https://www.nist.gov/privacy-framework/privacy-framework","claim_scope":"privacy risk arising from data processing, organizational roles, profiles and outcomes","authority_limit":"Voluntary risk-management guidance; it does not decide applicable law, valid consent, individual acceptance or system-specific control effectiveness."},
        {"source_id":"source.semantic-phase3.nist.sse","publisher":"NIST","source_kind":"special_publication","title":"SP 800-160 Vol. 1 Rev. 1 Engineering Trustworthy Secure Systems","url":"https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final","claim_scope":"security engineering principles, protection needs, requirements, trustworthiness, verification and validation","authority_limit":"Systems-engineering guidance does not certify a system, choose acceptable risk or prove that a deployed control works."},
        {"source_id":"source.semantic-phase3.slsa","publisher":"OpenSSF / SLSA community","source_kind":"approved_open_specification","title":"SLSA Specification 1.2","url":"https://slsa.dev/spec/v1.2/","claim_scope":"source/build tracks, provenance, attestations, levels and verification expectations","authority_limit":"SLSA provenance and level verification cover defined supply-chain threats; they do not prove source correctness, artifact safety, semantic fitness or runtime authorization."},
    ]
    constitution = {
        "record_kind":"semantic_axis_phase_constitution_candidate",
        "constitution_id":"constitution.semantic-axis.phase3.authority-effect-safety.v1",
        "edition":1,"as_of":AS_OF,"status":"EVIDENCE_BACKED_CANDIDATE_PENDING_OWNER_RATIFICATION","completion_claim":False,
        "sovereign_question":"Under whose exact authority may which subject decide or perform which action over which resource for what purpose and interval, through which effect boundary, under what privacy, security and safety constraints?",
        "negative_mission":"Do not infer authorization from authentication, approval from recommendation, issuance from approval, enforcement from policy decision, effect completion from acknowledgement, privacy from encryption, safety from availability, or trust from attestation integrity.",
        "modules":[
            {
                "module_id":"module.semantic-axis.authority-trust.v1","axis":"authority_and_trust",
                "authority_coordinates":[
                    "authority source and mandate","principal/subject identity","decision or action","resource and exact cut","purpose","tenant/scope/jurisdiction profile","validity interval","delegation chain and depth","policy edition","facts/attributes and issuers","decision authority","issuance authority","effect authority","obligations/advice","revocation and propagation","appeal/review",
                ],
                "trust_coordinates":["claim","claimant/issuer","evidence set","verification method","verifier policy","freshness/time","scope","defeaters","residual uncertainty","relying decision and accepting owner"],
                "non_collapse_laws":[
                    "authentication is not authorization","authority is not responsibility ownership stewardship or accountability","recommendation is not decision","approval is not issuance","policy decision is not enforcement","permit is not entitlement capability or completed disclosure","obligation declaration is not obligation discharge","delegation is scoped time-bounded and revocable rather than transfer of identity","revocation is not deletion and cannot prove prior effects were unseen","attestation integrity is not claim truth authority or fitness","evidence strength is relative to a verifier policy and defeaters","indeterminate not-applicable deny and permit remain distinct",
                ],
                "required_outcomes":["permit","deny","not_applicable","indeterminate","challenge_or_more_evidence","permit_with_obligations","revoked","expired","authority_unresolved","refused"],
            },
            {
                "module_id":"module.semantic-axis.effect-boundary.v1","axis":"effect_boundary",
                "effect_coordinates":[
                    "intent identity","requested action and target","authority decision reference","configuration/policy editions","idempotency domain/key/retention","attempt identity and fence","provider capability edition","encoded request","start/accept/complete observations","partial outcome","unknown completion","receipt scope and issuer","consumer/business acceptance","retry/reconciliation policy","cancellation state","compensation/recall/supersession plan",
                ],
                "boundary_kinds":["pure_no_io","pure_effect_intent","effectful_runtime","provider_or_ffi_adapter","generated_boundary","unresolved_refuse"],
                "non_collapse_laws":[
                    "pure decision is not effect","intent is not attempt","attempt is not provider acceptance","acknowledgement is not durable completion","provider completion is not consumer or business acceptance","receipt is not outcome truth","idempotency is scoped to intended effect and does not imply exactly-once execution","retry after unknown completion requires reconciliation unless exact idempotency evidence permits it","cancellation request observed cancellation and rollback are distinct","partial success enumerates completed failed unknown and residual work","compensation is a new effect that can fail","generated or FFI code is an adapter boundary and never semantic authority",
                ],
                "required_outcomes":["intent_formed","not_started","started","accepted","completed","partially_completed","failed","cancel_requested","cancelled","unknown_completion","reconciled","compensated","compensation_failed","refused"],
            },
            {
                "module_id":"module.semantic-axis.privacy-security-safety.v1","axis":"privacy_security_safety",
                "privacy_coordinates":[
                    "data/people privacy unit","data action and lifecycle stage","purpose and compatibility","recipient/party role","permission/consent/legal-basis evidence reference","minimization and necessity policy","linkability/identifiability threat model","disclosure and cumulative exposure","retention/erasure policy","location/residency profile","individual/group impact","privacy risk owner and acceptance",
                ],
                "security_coordinates":[
                    "asset and protection need","trust boundaries","principal and least privilege","confidentiality integrity availability and authenticity requirements","secret/key purpose and custody","threat actor capability","abuse case and confused deputy","isolation/tenant boundary","supply-chain expectation","audit and incident evidence","degraded/fail-secure posture","residual security risk owner",
                ],
                "safety_coordinates":[
                    "stakeholders and unacceptable losses","hazardous system state","unsafe control action or missing action","operating context and assumptions","safety constraint","detection and response","safe/degraded state","human judgment/override authority","irreversibility and recovery","safety evidence and accepting owner",
                ],
                "non_collapse_laws":[
                    "privacy risk is not limited to confidentiality breach","security classification is not processing purpose or consent","encryption is not authorization purpose limitation or minimization","pseudonymization de-identification and release-context anonymity claims are distinct","retention expiry logical deletion physical reclamation and proof of erasure are distinct","residency of data keys processing control plane and support access are separate","integrity authenticity provenance truth and authorization are distinct","availability is not safety and fail-open is not graceful degradation","threat vulnerability hazard abuse incident and loss are distinct","supply-chain attestation is not artifact correctness safety or runtime trust","risk assessment mitigation verification acceptance and residual ownership are separate","a model or agent may propose evidence or actions but cannot waive privacy security or safety refusals",
                ],
                "required_outcomes":["satisfied","satisfied_with_obligations","degraded_with_authority","mitigation_required","risk_acceptance_required","prohibited","indeterminate","evidence_insufficient","unsafe","refused"],
            },
        ],
        "cross_module_laws":[
            "Privacy security and safety requirements constrain both policy decisions and effect execution; neither layer silently satisfies the other.",
            "Every protected effect binds the exact authority decision and rechecks freshness revocation obligations and provider capability at its declared binding phase.",
            "Unknown identity purpose authority threat/hazard posture or completion fails according to an explicit fail-closed or separately authorized degraded policy.",
            "Evidence and receipts preserve issuer scope edition time coverage and defeaters; no integrity mechanism upgrades a bounded claim into universal truth.",
            "Replay backfill migration and compensation are new effects requiring renewed authority privacy budget retention and safety evaluation.",
        ],
        "imported_foundation_refs":[
            "library.csp.authority.authority-scope","library.csp.authority.delegation-graph","library.csp.authority.entitlement","library.csp.authority.approval-ledger","library.csp.authority.issuance","library.csp.authority.revocation","library.csp.authority.policy-algebra","library.csp.authority.policy-decision","library.csp.authority.enforcement-port","library.csp.decision.action-proposal","library.csp.decision.action-authorizer","library.csp.decision.effect-port","library.csp.decision.compensation","library.spt.privacy_vocabulary","library.spt.use_policy_compiler","library.spt.retention_calculus","library.spt.secret_handles","library.spt.crypto_types","library.spt.policy_evaluator","library.lpe.attestation-core","library.lpe.evidence-evaluation","library.runtime-resource.attempt-state","library.runtime-resource.runtime-receipts",
        ],
        "prohibited_new_facades":["universal_authority","universal_policy_result","universal_effect","universal_security_context","universal_privacy_flag","universal_risk_score","universal_safety_status"],
        "ratification_gate":"Named authority, privacy, security, safety, evidence and runtime owners accept coordinates, outcomes, non-collapse laws and imports; all family matrices bind explicit applicability and exceptions.",
    }
    claims = [
        {"claim_id":"claim.phase3.xacml-role-separation","source_ref":"source.semantic-phase3.oasis.xacml","bounded_claim":"XACML separates policy administration, information, decision and enforcement roles and preserves four top-level decision states with explicit combining behavior.","supports_module_refs":["module.semantic-axis.authority-trust.v1"],"authority_limit":sources[0]["authority_limit"]},
        {"claim_id":"claim.phase3.abac-coordinates","source_ref":"source.semantic-phase3.nist.abac","bounded_claim":"NIST ABAC determines authorization by evaluating subject, object, requested-operation and possibly environment attributes against policies, rules or relationships.","supports_module_refs":["module.semantic-axis.authority-trust.v1"],"authority_limit":sources[1]["authority_limit"]},
        {"claim_id":"claim.phase3.odrl-rules-duties","source_ref":"source.semantic-phase3.w3c.odrl","bounded_claim":"ODRL keeps permissions, prohibitions and duties distinct and binds assets, parties, actions, constraints and conflict strategies.","supports_module_refs":["module.semantic-axis.authority-trust.v1","module.semantic-axis.privacy-security-safety.v1"],"authority_limit":sources[2]["authority_limit"]},
        {"claim_id":"claim.phase3.http-idempotency","source_ref":"source.semantic-phase3.ietf.http","bounded_claim":"RFC 9110 defines idempotency over the intended effect of repeated identical requests and restricts automatic retry when a non-idempotent request may have been applied.","supports_module_refs":["module.semantic-axis.effect-boundary.v1"],"authority_limit":sources[3]["authority_limit"]},
        {"claim_id":"claim.phase3.revocation-is-not-erasure","source_ref":"source.semantic-phase3.ietf.revocation","bounded_claim":"RFC 7009 specifies a revocation request that invalidates a token and may affect related tokens according to authorization-server policy.","supports_module_refs":["module.semantic-axis.authority-trust.v1"],"authority_limit":sources[4]["authority_limit"]},
        {"claim_id":"claim.phase3.privacy-risk-beyond-breach","source_ref":"source.semantic-phase3.nist.privacy","bounded_claim":"The NIST Privacy Framework treats privacy risk as problems people may experience from data processing across the lifecycle, including pathways unrelated to cybersecurity incidents.","supports_module_refs":["module.semantic-axis.privacy-security-safety.v1"],"authority_limit":sources[5]["authority_limit"]},
        {"claim_id":"claim.phase3.trustworthy-system-engineering","source_ref":"source.semantic-phase3.nist.sse","bounded_claim":"NIST SP 800-160 frames trustworthiness through explicit protection needs, requirements, architecture, verification, validation and lifecycle engineering rather than product labels.","supports_module_refs":["module.semantic-axis.privacy-security-safety.v1"],"authority_limit":sources[6]["authority_limit"]},
        {"claim_id":"claim.phase3.slsa-provenance-bounds","source_ref":"source.semantic-phase3.slsa","bounded_claim":"SLSA 1.2 defines source/build tracks, levels and provenance verification expectations with scoped supply-chain guarantees.","supports_module_refs":["module.semantic-axis.authority-trust.v1","module.semantic-axis.privacy-security-safety.v1"],"authority_limit":sources[7]["authority_limit"]},
    ]
    projection = {
        "record_kind":"semantic_axis_compiler_projection_candidate","projection_id":"projection.compiler.semantic-axis.phase3.v1","edition":1,"status":"STRUCTURAL_PROJECTION_NOT_IR_AUTHORITY",
        "required_ir_roles":[
            "AuthoritySourceRef","MandateRef","PrincipalRef","DelegationChainRef","PolicyEditionRef","PolicyFactsRef","DecisionOutcome","ObligationSet","RevocationState","TrustAssessmentRef","EffectIntentRef","AttemptRef","IdempotencyProfileRef","ProviderObservationRef","ReceiptRef","AcceptanceRef","PrivacyProfileRef","SecurityProfileRef","SafetyProfileRef","ThreatModelRef","HazardModelRef","RiskAcceptanceRef","Residual",
        ],
        "binding_sequence":[
            "bind Phase-1 subject identity grain and Phase-2 time/state/partiality","bind authority source mandate principal action resource purpose interval and delegation","evaluate exact policy edition and facts without inventing attributes","bind obligations revocation freshness and effect authority","form immutable effect intent","qualify provider capability idempotency and reconciliation semantics","execute through explicit runtime/adapter and classify observations","seal receipt without promoting it to acceptance","evaluate privacy security and safety constraints before and after effect","emit residual risks obligations appeals and recovery ownership",
        ],
        "required_adapter_proofs":["principal/resource/action/purpose preservation","authority and revocation freshness","obligation support","intent-to-attempt binding","idempotency and unknown-completion behavior","receipt issuer/scope integrity","privacy-purpose and minimization preservation","security trust-boundary preservation","safety constraint and degraded-state preservation","supply-chain expectation verification"],
        "refusal_roles":["principal_unresolved","authority_source_unbound","delegation_invalid","policy_missing","facts_untrusted","decision_indeterminate","obligation_unsupported","revoked_or_expired","effect_authority_missing","provider_capability_stale","idempotency_unproved","unknown_completion","receipt_unbound","privacy_purpose_unbound","minimization_unproved","security_requirement_unsatisfied","hazard_uncontrolled","risk_acceptance_missing","supply_chain_evidence_insufficient"],
        "generation_prohibition":"Do not generate grants, effect calls, retries, disclosure, degradation or risk acceptance from authentication, approval, policy labels, provider acknowledgements, encryption flags, attestations or model recommendations alone.",
    }
    summary = {"program_id":"program.semantic-axis.phase3.authority-effect-safety.v1","edition":1,"as_of":AS_OF,"status":"ACTIVE_PENDING_OWNER_RATIFICATION","completion_claim":False,"modules":3,"primary_sources":len(sources),"bounded_primary_evidence_claims":len(claims),"authority_coordinates":16,"effect_coordinates":16,"privacy_security_safety_coordinates":34,"canonical_exact_gaps_closed":0,"remaining_gate":constitution["ratification_gate"]}
    return {"sources":sources,"constitution":constitution,"claims":claims,"projection":projection,"summary":summary}


def outputs() -> dict[str,str]:
    b=build(); files={
        "sources.jsonl":"".join(canonical(x)+"\n" for x in b["sources"]),
        "constitution.json":json.dumps(b["constitution"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        "evidence-claims.jsonl":"".join(canonical(x)+"\n" for x in b["claims"]),
        "compiler-projection.json":json.dumps(b["projection"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        "summary.json":json.dumps(b["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
    }; manifest={n:{"sha256":hashlib.sha256(t.encode()).hexdigest(),"bytes":len(t.encode())} for n,t in files.items()}; files["manifest.json"]=json.dumps({"manifest_id":"manifest.semantic-axis.phase3.v1","as_of":AS_OF,"files":manifest},sort_keys=True,indent=2)+"\n"; return files


def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();stale=[]
    for n,t in outputs().items():
        q=HERE/n
        if a.check:
            if not q.is_file() or q.read_text()!=t:stale.append(n)
        else:q.write_text(t)
    if stale:print("STALE "+", ".join(stale));return 1
    s=build()["summary"];print(f"{'CHECK' if a.check else 'BUILD'} PASS Phase 3 semantic constitution: {s['modules']} modules, {s['primary_sources']} sources, {s['bounded_primary_evidence_claims']} claims, zero canonical gaps closed");return 0


if __name__=="__main__":raise SystemExit(main())
