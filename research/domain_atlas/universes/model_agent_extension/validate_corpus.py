#!/usr/bin/env python3
"""Validate the model/tool-agent optional extension corpus."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_jsonl(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []
    contexts = read_jsonl("contexts.jsonl")
    operations = read_jsonl("operations.jsonl")
    decisions = read_jsonl("decisions.jsonl")
    laws = read_jsonl("laws.jsonl")
    sources = read_jsonl("sources.jsonl")
    source_coverage = read_jsonl("source-coverage.jsonl")
    libraries = read_jsonl("library-boundaries.jsonl")
    innovations = read_jsonl("innovations-2021-2026.jsonl")
    gaps = read_jsonl("gaps.jsonl")
    mappings = read_jsonl("compiler-mappings.jsonl")
    proofs = read_jsonl("proof-contracts.jsonl")
    compiler_records = read_jsonl("compiler-requirements-offers.jsonl")
    qualification_profiles = read_jsonl("qualification-receipts.jsonl")
    imports = read_jsonl("core-imports.jsonl")
    twins = read_jsonl("examples/negative-twins.jsonl")
    examples = json.loads((HERE / "examples/useful-examples.json").read_text(encoding="utf-8"))
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    metamodel = json.loads((HERE / "metamodel.json").read_text(encoding="utf-8"))
    ml_boundary = json.loads((HERE / "classical-predictive-ml-boundary.json").read_text(encoding="utf-8"))

    thresholds = {
        "contexts": (len(contexts), 50),
        "operations+decisions+laws": (len(operations) + len(decisions) + len(laws), 180),
        "primary sources": (len(sources), 80),
        "library boundaries": (len(libraries), 25),
        "innovations": (len(innovations), 20),
        "gaps": (len(gaps), 20),
        "examples": (len(examples), 2),
        "negative twins": (len(twins), 4),
        "compiler requirements/offers": (len(compiler_records), 36),
        "qualification profiles": (len(qualification_profiles), 30),
    }
    for label, (actual, minimum) in thresholds.items():
        if actual < minimum:
            errors.append(f"{label}: {actual} < {minimum}")

    collections = [contexts, operations, decisions, laws, sources, source_coverage, libraries, innovations, gaps, mappings, proofs, compiler_records, qualification_profiles, imports, twins]
    all_ids: list[str] = []
    for rows in collections:
        for row in rows:
            identifier = next((value for key, value in row.items() if key.endswith("_id")), None)
            if not identifier:
                errors.append(f"record without identifier: {row}")
            else:
                all_ids.append(identifier)
    if len(all_ids) != len(set(all_ids)):
        errors.append("duplicate IDs across extension corpus")

    context_ids = {row["context_id"] for row in contexts}
    operation_ids = {row["operation_id"] for row in operations}
    decision_ids = {row["decision_id"] for row in decisions}
    law_ids = {row["law_id"] for row in laws}
    proof_ids = {row["proof_id"] for row in proofs}
    source_ids = {row["source_id"] for row in sources}
    library_ids = {row["library_id"] for row in libraries}
    requirements = {
        row["requirement_id"]: row for row in compiler_records if row.get("record_kind") == "capability_requirement"
    }
    offers = {
        row["offer_id"]: row for row in compiler_records if row.get("record_kind") == "capability_offer"
    }
    if len(requirements) + len(offers) != len(compiler_records):
        errors.append("compiler projection has unknown record kinds or duplicate IDs")
    for row in contexts:
        if not set(row["operation_refs"]) <= operation_ids:
            errors.append(f"{row['context_id']}: unresolved operations")
        if row["decision_ref"] not in decision_ids or row["law_ref"] not in law_ids:
            errors.append(f"{row['context_id']}: unresolved decision/law")
        if not set(row["evidence_refs"]) <= source_ids:
            errors.append(f"{row['context_id']}: unresolved evidence")
    for rows, key in [(operations, "operation_id"), (decisions, "decision_id"), (laws, "law_id"), (proofs, "proof_id"), (mappings, "mapping_id")]:
        for row in rows:
            if row["context_ref"] not in context_ids:
                errors.append(f"{row[key]}: unresolved context")
    for row in mappings:
        if not set(row["proof_refs"]) <= proof_ids:
            errors.append(f"{row['mapping_id']}: unresolved proof")
        if row["core_valid_without_extension"] is not True or row["fallback"] != "refuse_or_explicit_non_model_path":
            errors.append(f"{row['mapping_id']}: extension optionality violated")

    for row in sources:
        if row["authority"] != "primary" or not row["url"].startswith("https://"):
            errors.append(f"{row['source_id']}: non-primary or insecure source")
    if len({row["url"] for row in sources}) != len(sources):
        errors.append("duplicate evidence URLs")
    covered_sources: set[str] = set()
    for row in source_coverage:
        if row["source_ref"] not in source_ids:
            errors.append(f"{row['coverage_id']}: unresolved source")
        if not set(row["context_refs"]) <= context_ids:
            errors.append(f"{row['coverage_id']}: unresolved contexts")
        covered_sources.add(row["source_ref"])
    if covered_sources != source_ids:
        errors.append(f"source coverage is not total: missing={sorted(source_ids - covered_sources)}")
    for row in innovations:
        if not 2021 <= row["year"] <= 2026 or not set(row["evidence_refs"]) <= source_ids:
            errors.append(f"{row['innovation_id']}: invalid year/evidence")
    for row in libraries:
        if row["dependency_direction"] != "extension_to_core_only":
            errors.append(f"{row['library_id']}: invalid dependency direction")
    expected_requirements = {
        library_id.replace("library.mae.", "requirement.mae.") for library_id in library_ids
    }
    if set(requirements) != expected_requirements:
        errors.append(f"requirement coverage drift: {sorted(set(requirements) ^ expected_requirements)}")
    for requirement_id, row in requirements.items():
        if row.get("status") != "declared" or row.get("criticality") != "optional" or row.get("fallback_law") != "omit_optional":
            errors.append(f"{requirement_id}: optionality or status violated")
        if row.get("subject_ref") not in library_ids or row.get("owner_ref") not in context_ids:
            errors.append(f"{requirement_id}: unresolved library/context")
        if row.get("applicability", {}).get("when") != ["The declared intent explicitly requests this optional model/agent capability."]:
            errors.append(f"{requirement_id}: extension can be inserted without explicit intent")
        prohibited = set(row.get("prohibited_traits", []))
        if not {"ambient model insertion", "self-authorization", "self-validation", "direct protected effect"} <= prohibited:
            errors.append(f"{requirement_id}: deterministic boundary prohibitions missing")
    if len(offers) != 6:
        errors.append(f"provider offer coverage drift: {len(offers)}")
    for offer_id, row in offers.items():
        if row.get("status") != "declared" or row.get("conformance_receipts") != []:
            errors.append(f"{offer_id}: invented provider qualification")
        if not set(row.get("evidence_refs", [])) <= source_ids:
            errors.append(f"{offer_id}: unresolved evidence")
        if not set(row.get("decision_refs", [])) <= decision_ids:
            errors.append(f"{offer_id}: unresolved decisions")
        if "The offer does not satisfy any deterministic core contract." not in row.get("exclusions", []):
            errors.append(f"{offer_id}: provider offer leaks into deterministic core")
    profile_ids = {row.get("receipt_id") for row in qualification_profiles}
    expected_profiles = {library_id.replace("library.mae.", "receipt.mae.") for library_id in library_ids}
    if profile_ids != expected_profiles:
        errors.append(f"qualification-profile coverage drift: {sorted(profile_ids ^ expected_profiles)}")
    for row in qualification_profiles:
        if row.get("record_kind") != "qualification_profile" or row.get("status") != "template_not_executed":
            errors.append(f"{row.get('receipt_id')}: invalid qualification profile")
        if row.get("subject_ref") not in library_ids or row.get("results") != []:
            errors.append(f"{row.get('receipt_id')}: invented result or unresolved subject")
        if not row.get("fixtures") or not row.get("oracles"):
            errors.append(f"{row.get('receipt_id')}: non-executable profile")
        if not any("proves no provider or model capability" in item for item in row.get("limitations", [])):
            errors.append(f"{row.get('receipt_id')}: missing non-claim")
    for row in imports:
        if row["direction"] != "extension_to_core" or not row["core_valid_without_extension"] or row["extension_valid_without_core"]:
            errors.append(f"{row['import_id']}: core/extension direction violated")
        if not (HERE / row["core_path"]).resolve().exists():
            errors.append(f"{row['import_id']}: core path absent: {row['core_path']}")

    required_laws = {
        "plan != validated claim != effect intent != effect receipt",
        "tool definition != visibility != selection != authorization != execution",
        "retrieval result != trusted instruction != validated evidence",
        "schema conformance != domain validity != factual truth",
        "classical predictive ML remains a neighboring core universe",
        "absence of the extension leaves every deterministic compiler proof valid",
    }
    if not required_laws <= set(metamodel["constitutional_laws"]):
        errors.append("metamodel missing constitutional separation laws")
    if manifest["core_valid_without_extension"] is not True or manifest["classical_predictive_ml_owned_here"] is not False:
        errors.append("manifest optionality or ML boundary violated")
    if ml_boundary["owned_here"] is not False:
        errors.append("classical predictive ML incorrectly owned by extension")

    core_forbidden = ("execute tool directly", "self-authorizing", "autonomous application")
    corpus_text = "\n".join((HERE / name).read_text(encoding="utf-8").lower() for name in ["contexts.jsonl", "operations.jsonl", "decisions.jsonl", "laws.jsonl", "compiler-mappings.jsonl"])
    for phrase in core_forbidden:
        if phrase in corpus_text:
            errors.append(f"forbidden autonomous-core phrase present: {phrase}")
    if any(row["effect_posture"] not in {"pure", "read_observation", "proposal_only", "core_request", "evaluation", "control"} for row in operations):
        errors.append("operation bypasses typed proposal/core-request posture")

    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None
    if jsonschema:
        schema_files = {
            "contexts.jsonl": "context", "operations.jsonl": "operation", "decisions.jsonl": "decision",
            "laws.jsonl": "law", "sources.jsonl": "source", "source-coverage.jsonl": "source-coverage", "library-boundaries.jsonl": "library",
            "compiler-mappings.jsonl": "compiler-mapping", "proof-contracts.jsonl": "proof",
            "innovations-2021-2026.jsonl": "innovation", "gaps.jsonl": "gap", "core-imports.jsonl": "core-import",
            "examples/negative-twins.jsonl": "negative-twin",
        }
        for filename, schema_name in schema_files.items():
            schema = json.loads((HERE / "schemas" / f"{schema_name}.schema.json").read_text(encoding="utf-8"))
            for line_no, row in enumerate(read_jsonl(filename), 1):
                try:
                    jsonschema.validate(row, schema)
                except jsonschema.ValidationError as exc:
                    errors.append(f"{filename}:{line_no}: {exc.message}")
        binding_schema = json.loads((HERE.parents[1] / "compiler/requirement-offer-binding.schema.json").read_text(encoding="utf-8"))
        for line_no, row in enumerate(compiler_records, 1):
            try:
                jsonschema.validate(row, binding_schema)
            except jsonschema.ValidationError as exc:
                errors.append(f"compiler-requirements-offers.jsonl:{line_no}: {exc.message}")
        example_schema = json.loads((HERE / "schemas/useful-example.schema.json").read_text(encoding="utf-8"))
        for index, row in enumerate(examples):
            try:
                jsonschema.validate(row, example_schema)
            except jsonschema.ValidationError as exc:
                errors.append(f"examples/useful-examples.json:{index}: {exc.message}")

    regen = subprocess.run([sys.executable, str(HERE / "build_corpus.py"), "--check"], capture_output=True, text=True)
    if regen.returncode:
        errors.append(regen.stdout.strip() or regen.stderr.strip() or "deterministic regeneration failed")

    expected_counts = manifest["counts"]
    actual_counts = {
        "contexts": len(contexts), "operations": len(operations), "decisions": len(decisions), "laws": len(laws),
        "operations_decisions_laws": len(operations) + len(decisions) + len(laws), "primary_sources": len(sources),
        "source_coverage_mappings": len(source_coverage), "library_boundaries": len(libraries), "innovations_2021_2026": len(innovations), "gaps": len(gaps),
        "compiler_mappings": len(mappings), "proof_contracts": len(proofs), "core_imports": len(imports),
        "compiler_requirements_offers": len(compiler_records), "qualification_profiles": len(qualification_profiles),
        "useful_examples": len(examples), "negative_twins": len(twins),
    }
    if expected_counts != actual_counts:
        errors.append(f"manifest count drift: {expected_counts} != {actual_counts}")

    if errors:
        print("FAIL model/agent extension corpus")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS optional model/agent extension: {len(contexts)} contexts, {len(operations) + len(decisions) + len(laws)} operations/decisions/laws, {len(sources)} primary sources, {len(libraries)} libraries, {len(innovations)} innovations, {len(gaps)} gaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
