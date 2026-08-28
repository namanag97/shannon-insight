#!/usr/bin/env python3
"""Regression tests for the B07 authority-backed analytical tranche."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAPPER = ROOT / "research/domain_atlas/compiler/canonical_reference_mapper"
sys.path.insert(0, str(MAPPER))
import build_mapper  # noqa: E402


class B07CanonicalReferenceMapperTest(unittest.TestCase):
    def test_authority_ledger_is_primary_and_limited(self) -> None:
        records = build_mapper.load_authority_evidence()
        self.assertEqual(len(records), 5)
        self.assertEqual(len({record["authority_id"] for record in records}), 5)
        for record in records:
            self.assertEqual(record["record_kind"], "canonical_reference_authority_evidence")
            self.assertEqual(record["status"], "verified_primary_evidence")
            self.assertTrue(record["primary_url"].startswith("https://"))
            self.assertTrue(record["supports"])
            self.assertTrue(record["limitations"])

    def test_high_frequency_b07_refs_have_loss_aware_proposals(self) -> None:
        artifacts = build_mapper.build_outputs()
        mappings = [
            json.loads(line)
            for line in artifacts["candidate-mappings.jsonl"].decode("utf-8").splitlines()
            if line.strip()
        ]
        by_raw = {record["raw_ref"]: record for record in mappings}
        expected = {
            "method.process_mining": {
                "occurrences": 47,
                "target_refs": {
                    "analytics.process.process_discovery",
                    "analytics.process.process_conformance_checking",
                    "analytics.process.process_enhancement",
                },
                "authority": {"authority.ieee.process_mining_manifesto"},
            },
            "method.constrained_optimization": {
                "occurrences": 37,
                "target_refs": {"or.method.constraint_optimization"},
                "authority": {
                    "authority.google.or_tools.constraint_optimization",
                    "authority.google.or_tools.cp_sat",
                },
            },
            "method.causal_rca": {
                "occurrences": 35,
                "target_refs": {"analytics.diagnostic_rca.root_cause_analysis"},
                "authority": {"authority.pearl.causal_calculus"},
            },
            "method.temporal_network_analysis": {
                "occurrences": 29,
                "target_refs": {"analytics.graph_network.temporal_graph_analysis"},
                "authority": {"authority.holme_saramaki.temporal_networks"},
            },
        }
        for raw_ref, expectation in expected.items():
            with self.subTest(raw_ref=raw_ref):
                mapping = by_raw[raw_ref]
                self.assertEqual(
                    len(mapping["evidence"]["source_occurrence_refs"]), expectation["occurrences"]
                )
                self.assertEqual(set(mapping["target_refs"]), expectation["target_refs"])
                self.assertEqual(
                    set(mapping["evidence"]["authority_evidence_refs"]), expectation["authority"]
                )
                self.assertIn(mapping["proposed_relation"], {"narrower", "overlap"})
                self.assertEqual(mapping["status"], "proposed")
                self.assertFalse(mapping["adjudicated"])
                self.assertTrue(mapping["information_loss"])
                self.assertTrue(mapping["uncertainties"])


if __name__ == "__main__":
    unittest.main()
