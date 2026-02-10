"""Grouped finding display configuration for Rich terminal output."""

from ..insights import Finding

MAX_FILES_PER_GROUP = 15


def _hub_oneliner(finding: Finding) -> str:
    blast = next(
        (e for e in finding.evidence if "affected" in e.description.lower() or "blast" in e.signal),
        None,
    )
    importers = next(
        (e for e in finding.evidence if "import" in e.description.lower()),
        None,
    )
    if blast:
        return blast.description
    if importers:
        return importers.description
    return finding.title


def _god_oneliner(finding: Finding) -> str:
    desc = next(
        (
            e
            for e in finding.evidence
            if "function" in e.description.lower() or "complex" in e.description.lower()
        ),
        None,
    )
    return desc.description if desc else finding.title


def _coupling_oneliner(finding: Finding) -> str:
    cochange = next(
        (e for e in finding.evidence if "changed" in e.description.lower()),
        None,
    )
    files_str = " \u2194 ".join(finding.files)
    return f"{files_str} \u2014 {cochange.description}" if cochange else files_str


def _boundary_oneliner(finding: Finding) -> str:
    cluster = next(
        (
            e
            for e in finding.evidence
            if "cluster" in e.description.lower() or "distinct" in e.description.lower()
        ),
        None,
    )
    return cluster.description if cluster else finding.title


def _unstable_oneliner(finding: Finding) -> str:
    return finding.evidence[0].description if finding.evidence else finding.title


def _dead_dep_oneliner(finding: Finding) -> str:
    return (
        " \u2192 ".join(finding.files)
        + " \u2014 "
        + (finding.evidence[0].description if finding.evidence else "never co-changed")
    )


FINDING_DISPLAY = {
    "high_risk_hub": {
        "label": "HIGH RISK HUBS",
        "color": "red",
        "summary": "These files have many dependents. A bug ripples widely.",
        "suggestion": "Split into smaller modules or add interfaces to reduce coupling.",
        "oneliner": _hub_oneliner,
    },
    "god_file": {
        "label": "GOD FILES",
        "color": "magenta",
        "summary": "These files are complex and unfocused \u2014 too many responsibilities.",
        "suggestion": "Extract clusters of related functions into separate modules.",
        "oneliner": _god_oneliner,
    },
    "hidden_coupling": {
        "label": "HIDDEN COUPLING",
        "color": "yellow",
        "summary": "These file pairs always change together but share no import.",
        "suggestion": "Make the dependency explicit or extract shared logic.",
        "oneliner": _coupling_oneliner,
    },
    "boundary_mismatch": {
        "label": "BOUNDARY MISMATCHES",
        "color": "cyan",
        "summary": "These directories don't match actual dependency patterns.",
        "suggestion": "Reorganize files to match how they're actually connected.",
        "oneliner": _boundary_oneliner,
    },
    "unstable_file": {
        "label": "UNSTABLE FILES",
        "color": "yellow",
        "summary": "These files keep changing without stabilizing.",
        "suggestion": "Stabilize the interface or split volatile parts.",
        "oneliner": _unstable_oneliner,
    },
    "dead_dependency": {
        "label": "DEAD DEPENDENCIES",
        "color": "dim",
        "summary": "These imports exist but the files never actually change together.",
        "suggestion": "Verify the import is still needed; remove if dead.",
        "oneliner": _dead_dep_oneliner,
    },
}
