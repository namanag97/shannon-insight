"""Tests for the visualization module."""

import sys

sys.path.insert(0, "src")

import os
import tempfile

from shannon_insight.snapshot.models import EvidenceRecord, FindingRecord, Snapshot
from shannon_insight.visualization.report import generate_report
from shannon_insight.visualization.treemap import build_treemap_data


class TestBuildTreemapData:
    def test_hierarchical_structure(self):
        data = build_treemap_data(
            {
                "src/core/engine.py": {"cognitive_load": 0.8, "lines": 200},
                "src/core/utils.py": {"cognitive_load": 0.3, "lines": 50},
                "src/api/routes.py": {"cognitive_load": 0.5, "lines": 100},
            }
        )
        assert data["name"] == "root"
        assert len(data["children"]) >= 1  # at least "src"

    def test_single_file(self):
        data = build_treemap_data({"main.py": {"cognitive_load": 0.5, "lines": 10}})
        assert data["name"] == "root"
        leaf = data["children"][0]
        assert leaf["name"] == "main.py"
        assert leaf["value"] == 10

    def test_color_value_is_percentile(self):
        data = build_treemap_data(
            {
                "a.py": {"cognitive_load": 0.1, "lines": 10},
                "b.py": {"cognitive_load": 0.5, "lines": 10},
                "c.py": {"cognitive_load": 0.9, "lines": 10},
            }
        )
        # Find leaves
        leaves = []

        def collect(node):
            if "children" in node:
                for c in node["children"]:
                    collect(c)
            else:
                leaves.append(node)

        collect(data)
        assert len(leaves) == 3
        # Highest cognitive_load should have highest color_value
        by_name = {l["name"]: l for l in leaves}
        assert by_name["c.py"]["color_value"] >= by_name["a.py"]["color_value"]

    def test_empty_signals(self):
        data = build_treemap_data({})
        assert data["name"] == "root"
        assert data["children"] == []


class TestGenerateReport:
    def test_creates_html_file(self):
        snap = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_count=2,
            file_signals={
                "a.py": {"cognitive_load": 0.5, "lines": 100},
                "b.py": {"cognitive_load": 0.3, "lines": 50},
            },
            codebase_signals={"fiedler_value": 0.1},
            findings=[
                FindingRecord(
                    "god_file",
                    "k1",
                    0.85,
                    "a.py is a god file",
                    ["a.py"],
                    [EvidenceRecord("cognitive_load", 0.5, 90.0, "top 10%")],
                    "split it",
                ),
            ],
        )
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            output = f.name
        try:
            result = generate_report(snap, output_path=output)
            assert os.path.exists(result)
            html = open(result).read()
            assert "<!DOCTYPE html>" in html
            assert "Shannon Insight Report" in html
            assert "renderTreemap" in html
            assert "god_file" in html or "god file" in html
        finally:
            os.unlink(output)

    def test_report_without_trends(self):
        snap = Snapshot(
            tool_version="0.6.0",
            timestamp="2025-01-01T00:00:00Z",
            analyzed_path="/tmp",
            file_count=1,
            file_signals={"a.py": {"lines": 10}},
        )
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            output = f.name
        try:
            result = generate_report(snap, output_path=output)
            html = open(result).read()
            assert "<!DOCTYPE html>" in html
        finally:
            os.unlink(output)
