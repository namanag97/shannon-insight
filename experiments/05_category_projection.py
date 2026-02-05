#!/usr/bin/env python3
"""Experiment 05 — Category Theory: File-to-Module Projection Functor.

Verifies whether the projection functor F: Files -> Modules preserves
dependency structure. Checks edge preservation, phantom edges,
and composition preservation.
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import load_analysis


def module_of(file_path):
    """Projection functor: file -> its containing directory (module)."""
    return str(Path(file_path).parent)


def main():
    codebase = sys.argv[1] if len(sys.argv) > 1 else "."
    result, file_metrics = load_analysis(codebase)

    graph = result.graph

    print("=" * 72)
    print("EXPERIMENT 05 — CATEGORY PROJECTION: FILE -> MODULE FUNCTOR")
    print("=" * 72)
    print()

    # ── Build file-level edge set ───────────────────────────────
    file_edges = set()
    for src, targets in graph.adjacency.items():
        for tgt in targets:
            file_edges.add((src, tgt))

    all_modules = set(module_of(f) for f in graph.all_nodes)
    print(f"Files: {len(graph.all_nodes)}")
    print(f"Modules (directories): {len(all_modules)}")
    print(f"File-level edges: {len(file_edges)}")
    print()

    # ── 1. Project each file edge to module edge ────────────────
    module_edges = set()          # Projected module-level edges
    internal_edges = []           # File edges within same module (-> identity)
    cross_module_edges = []       # File edges across modules
    file_support = defaultdict(list)  # module_edge -> list of file edges supporting it

    for src, tgt in file_edges:
        m_src = module_of(src)
        m_tgt = module_of(tgt)

        if m_src == m_tgt:
            internal_edges.append((src, tgt))
        else:
            module_edges.add((m_src, m_tgt))
            cross_module_edges.append((src, tgt))
            file_support[(m_src, m_tgt)].append((src, tgt))

    print("1. EDGE PROJECTION")
    print("-" * 72)
    print(f"  Internal edges (same module, map to identity):  {len(internal_edges)}")
    print(f"  Cross-module edges:                              {len(cross_module_edges)}")
    print(f"  Distinct module-level edges:                     {len(module_edges)}")
    print()

    # ── 2. Check for phantom edges ──────────────────────────────
    # Build the actual module-level graph from the engine results
    # A "real" module edge has at least one file-edge supporting it
    # A "phantom" edge would be a module edge without file support
    # Since we BUILD module edges FROM file edges, there can't be phantoms
    # UNLESS the engine's module analysis reports edges differently

    engine_module_edges = set()
    for mod_path, ma in result.modules.items():
        # Module has external_edges_out — to which modules?
        mod_files = set(ma.files)
        for f in ma.files:
            for dep in graph.adjacency.get(f, []):
                dep_mod = module_of(dep)
                if dep_mod != mod_path:
                    engine_module_edges.add((mod_path, dep_mod))

    phantom = engine_module_edges - module_edges
    unsupported_projected = module_edges - engine_module_edges

    print("2. PHANTOM EDGES (module edges without file-level support)")
    print("-" * 72)
    if not phantom:
        print("  None — every module-level edge has file-level support. Functor is surjective on edges.")
    else:
        print(f"  {len(phantom)} phantom edges found:")
        for m_src, m_tgt in sorted(phantom)[:10]:
            print(f"    {m_src} -> {m_tgt}")
    print()

    # ── 3. Edge preservation ratio ──────────────────────────────
    print("3. EDGE PRESERVATION")
    print("-" * 72)
    if file_edges:
        preservation = len(cross_module_edges) / len(file_edges)
        collapse = len(internal_edges) / len(file_edges)
        print(f"  Cross-module (preserved as distinct edges): {preservation:.1%}")
        print(f"  Internal (collapsed to identity):           {collapse:.1%}")
    else:
        print("  No edges to analyze.")

    # Fan-out: how many file edges map to each module edge
    if file_support:
        support_counts = [len(v) for v in file_support.values()]
        avg_support = sum(support_counts) / len(support_counts)
        max_support = max(support_counts)
        print(f"  Average file-edges per module-edge: {avg_support:.1f}")
        print(f"  Maximum file-edges for one module-edge: {max_support}")
    print()

    # ── 4. Composition preservation ─────────────────────────────
    print("4. COMPOSITION PRESERVATION")
    print("-" * 72)
    print("  Checking: if A->B->C at file level, does F(A)->F(B)->F(C) hold?")
    print()

    total_compositions = 0
    preserved_compositions = 0
    broken_compositions = []

    for mid in graph.all_nodes:
        # mid has incoming edges (sources) and outgoing edges (targets)
        sources = [src for src, tgt in file_edges if tgt == mid]
        targets = graph.adjacency.get(mid, [])

        for src in sources:
            for tgt in targets:
                if src == tgt:
                    continue
                total_compositions += 1

                m_src = module_of(src)
                m_mid = module_of(mid)
                m_tgt = module_of(tgt)

                # Check: does the composed path exist at module level?
                # F(src)->F(mid) should exist AND F(mid)->F(tgt) should exist
                first_ok = (m_src == m_mid) or (m_src, m_mid) in module_edges
                second_ok = (m_mid == m_tgt) or (m_mid, m_tgt) in module_edges

                if first_ok and second_ok:
                    preserved_compositions += 1
                else:
                    if len(broken_compositions) < 10:
                        broken_compositions.append(
                            (src, mid, tgt, m_src, m_mid, m_tgt, first_ok, second_ok)
                        )

    if total_compositions > 0:
        ratio = preserved_compositions / total_compositions
        print(f"  Total 2-step compositions checked: {total_compositions}")
        print(f"  Preserved at module level:         {preserved_compositions} ({ratio:.1%})")
        print(f"  Broken compositions:               {total_compositions - preserved_compositions}")
    else:
        print("  No 2-step compositions found (graph is too sparse).")

    if broken_compositions:
        print()
        print("  Examples of broken compositions:")
        for src, mid, tgt, ms, mm, mt, f1, f2 in broken_compositions[:5]:
            ss = Path(src).name
            sm = Path(mid).name
            st = Path(tgt).name
            print(f"    {ss} -> {sm} -> {st}")
            print(f"      modules: {ms} -> {mm} -> {mt}")
            leg1 = "OK" if f1 else "MISSING"
            leg2 = "OK" if f2 else "MISSING"
            print(f"      first leg: {leg1}, second leg: {leg2}")
    print()

    # ── 5. Functoriality Report ─────────────────────────────────
    print("5. FUNCTORIALITY SUMMARY")
    print("-" * 72)

    issues = []
    if phantom:
        issues.append(f"{len(phantom)} phantom module edges (no file support)")
    if total_compositions > 0 and preserved_compositions < total_compositions:
        broken = total_compositions - preserved_compositions
        issues.append(f"{broken} composition violations")

    if not issues:
        print("  The file->module projection is a valid functor:")
        print("  - Every file-level edge maps to a module-level edge (or identity)")
        print("  - No phantom edges")
        print("  - All compositions preserved")
    else:
        print("  Functor violations detected:")
        for issue in issues:
            print(f"  - {issue}")
        print()
        print("  This means the module structure doesn't fully respect")
        print("  the dependency structure — some abstractions leak.")

    print()


if __name__ == "__main__":
    main()
