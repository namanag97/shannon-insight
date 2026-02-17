"""Regression tests for finders using temporal signals.

Ensures temporal signal changes (trajectory enum, thresholds) don't break finders.
"""

import json

from shannon_insight.temporal.models import Trajectory


class TestTrajectoryEnumCompatibility:
    """Test that Trajectory enum is backward-compatible with string comparisons."""

    def test_enum_equals_string(self):
        """Trajectory enum should equal its string value."""
        assert Trajectory.DORMANT == "DORMANT"
        assert Trajectory.STABILIZING == "STABILIZING"
        assert Trajectory.STABLE == "STABLE"
        assert Trajectory.CHURNING == "CHURNING"
        assert Trajectory.SPIKING == "SPIKING"

    def test_string_equals_enum(self):
        """String should equal Trajectory enum (symmetric)."""
        assert "DORMANT" == Trajectory.DORMANT
        assert "SPIKING" == Trajectory.SPIKING

    def test_enum_in_string_set(self):
        """Trajectory enum should work with set membership (string sets)."""
        high_churn = {"CHURNING", "SPIKING"}

        assert Trajectory.CHURNING in high_churn
        assert Trajectory.SPIKING in high_churn
        assert Trajectory.STABLE not in high_churn
        assert Trajectory.STABILIZING not in high_churn
        assert Trajectory.DORMANT not in high_churn

    def test_string_in_enum_set(self):
        """Strings should work with sets containing Trajectory enums."""
        high_churn = {Trajectory.CHURNING, Trajectory.SPIKING}

        assert "CHURNING" in high_churn
        assert "SPIKING" in high_churn
        assert "STABLE" not in high_churn

    def test_enum_json_serialization(self):
        """Trajectory enum should serialize to JSON as string."""
        data = {"trajectory": Trajectory.CHURNING}
        serialized = json.dumps(data)

        # Should serialize as string value
        assert '"trajectory": "CHURNING"' in serialized

        # Deserialize and compare
        deserialized = json.loads(serialized)
        assert deserialized["trajectory"] == "CHURNING"
        assert deserialized["trajectory"] == Trajectory.CHURNING

    def test_enum_hash_matches_string(self):
        """Trajectory enum should have same hash as its string value."""
        # This is important for dict/set operations
        assert hash(Trajectory.CHURNING) == hash("CHURNING")
        assert hash(Trajectory.DORMANT) == hash("DORMANT")

    def test_enum_as_dict_key(self):
        """Trajectory enum should work as dict key interchangeably with strings."""
        d = {Trajectory.CHURNING: "high_churn"}

        # Access with string
        assert d["CHURNING"] == "high_churn"

        # Access with enum
        assert d[Trajectory.CHURNING] == "high_churn"

    def test_all_values_are_uppercase(self):
        """All Trajectory values should be uppercase."""
        for traj in Trajectory:
            assert traj.value == traj.value.upper()
            assert traj == traj.value.upper()


class TestTrajectoryEnumValues:
    """Test Trajectory enum has correct values per v2 spec."""

    def test_all_five_values_exist(self):
        """All five trajectory values should exist."""
        assert hasattr(Trajectory, "DORMANT")
        assert hasattr(Trajectory, "STABILIZING")
        assert hasattr(Trajectory, "STABLE")
        assert hasattr(Trajectory, "CHURNING")
        assert hasattr(Trajectory, "SPIKING")

    def test_no_extra_values(self):
        """Should have exactly five values."""
        assert len(Trajectory) == 5

    def test_values_match_spec(self):
        """Values should match v2 spec (temporal-operators.md)."""
        expected = {"DORMANT", "STABILIZING", "STABLE", "CHURNING", "SPIKING"}
        actual = {t.value for t in Trajectory}
        assert actual == expected


class TestFinderConditionPatterns:
    """Test common patterns used in finder conditions with Trajectory."""

    def test_high_churn_check_pattern(self):
        """Common pattern: trajectory in {CHURNING, SPIKING}."""
        high_churn_values = {Trajectory.CHURNING, Trajectory.SPIKING}

        # Both enum and string should work
        assert Trajectory.CHURNING in high_churn_values
        assert "CHURNING" in high_churn_values
        assert Trajectory.STABLE not in high_churn_values
        assert "STABLE" not in high_churn_values

    def test_dormant_check_pattern(self):
        """Common pattern: trajectory == 'DORMANT'."""
        trajectory = Trajectory.DORMANT

        # String comparison should work
        assert trajectory == "DORMANT"
        assert not (trajectory == "CHURNING")

    def test_instability_factor_pattern(self):
        """Pattern used in risk_score: instability_factor based on trajectory."""

        def compute_instability_factor(trajectory):
            """Mimic the pattern from composites.py."""
            return 1.0 if trajectory in ("CHURNING", "SPIKING") else 0.3

        assert compute_instability_factor(Trajectory.CHURNING) == 1.0
        assert compute_instability_factor(Trajectory.SPIKING) == 1.0
        assert compute_instability_factor(Trajectory.STABLE) == 0.3
        assert compute_instability_factor(Trajectory.STABILIZING) == 0.3
        assert compute_instability_factor(Trajectory.DORMANT) == 0.3
