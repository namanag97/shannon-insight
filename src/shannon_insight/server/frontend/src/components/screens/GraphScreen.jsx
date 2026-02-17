/**
 * Graph Screen - Dependency graph visualization
 *
 * Key insight: Use MODULES as primary grouping, not raw Louvain communities.
 * Raw communities create 100+ tiny clusters. Modules give ~30 meaningful groups.
 *
 * Data model:
 * - dependency_edges: [[source, target], ...] - import relationships
 * - node_community: {path: communityId} - Louvain clustering (too granular)
 * - modules: {path: {...}} - directory-based grouping (better for viz)
 * - files[path].signals.is_orphan - files with no imports/importers
 */

import { useEffect, useRef, useState, useCallback, useMemo } from "preact/hooks";
import useStore from "../../state/store.js";
import cytoscape from "cytoscape";
import dagre from "cytoscape-dagre";

cytoscape.use(dagre);

// Bright, high-contrast colors (not dark/muted)
const MODULE_COLORS = [
  "#60a5fa", // bright blue
  "#f87171", // bright red
  "#4ade80", // bright green
  "#fbbf24", // bright amber
  "#a78bfa", // bright purple
  "#22d3ee", // bright cyan
  "#fb923c", // bright orange
  "#e879f9", // bright pink
  "#34d399", // bright emerald
  "#f472b6", // bright rose
  "#38bdf8", // sky blue
  "#a3e635", // lime
  "#facc15", // yellow
  "#818cf8", // indigo
  "#2dd4bf", // teal
];
const ISOLATED_COLOR = "#6b7280"; // gray for isolated
const EDGE_COLOR = "#64748b"; // visible gray for edges
const FINDING_BORDER = "#fbbf24"; // amber for files with issues

export function GraphScreen() {
  const data = useStore((s) => s.data);
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  const [viewMode, setViewMode] = useState("modules"); // modules | communities | all
  const [showIsolated, setShowIsolated] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [highlightedGroup, setHighlightedGroup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ nodes: 0, edges: 0, groups: 0 });

  // Derive module groupings from file paths
  const moduleGroups = useMemo(() => {
    if (!data?.files) return { groups: [], fileToGroup: {}, groupColors: {} };

    const modules = data.modules || {};
    const fileToGroup = {};
    const groupCounts = {};

    // Assign each file to its module
    for (const path of Object.keys(data.files)) {
      // Find the module this file belongs to
      let assignedModule = "other";
      for (const modPath of Object.keys(modules)) {
        if (path.startsWith(modPath + "/") || path === modPath) {
          // Use the most specific (longest) matching module
          if (modPath.length > assignedModule.length || assignedModule === "other") {
            assignedModule = modPath;
          }
        }
      }
      fileToGroup[path] = assignedModule;
      groupCounts[assignedModule] = (groupCounts[assignedModule] || 0) + 1;
    }

    // Sort groups by size
    const groups = Object.entries(groupCounts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);

    // Assign colors
    const groupColors = {};
    groups.forEach((g, i) => {
      groupColors[g.name] = MODULE_COLORS[i % MODULE_COLORS.length];
    });

    return { groups, fileToGroup, groupColors };
  }, [data]);

  // Derive community groupings (original Louvain)
  const communityGroups = useMemo(() => {
    if (!data?.files) return { groups: [], fileToGroup: {}, groupColors: {} };

    const nodeCommunity = data.node_community || {};
    const fileToGroup = {};
    const groupCounts = {};

    for (const path of Object.keys(data.files)) {
      const comm = nodeCommunity[path] ?? data.files[path].signals?.community ?? -1;
      fileToGroup[path] = `c${comm}`;
      groupCounts[`c${comm}`] = (groupCounts[`c${comm}`] || 0) + 1;
    }

    // Filter to only communities with 2+ files
    const groups = Object.entries(groupCounts)
      .filter(([_, count]) => count >= 2)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);

    const groupColors = {};
    groups.forEach((g, i) => {
      groupColors[g.name] = MODULE_COLORS[i % MODULE_COLORS.length];
    });

    return { groups, fileToGroup, groupColors };
  }, [data]);

  // Get active grouping based on view mode
  const activeGrouping = viewMode === "modules" ? moduleGroups : communityGroups;

  // Build graph
  const initGraph = useCallback(() => {
    if (!data?.files || !containerRef.current) return;

    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    setLoading(true);
    setSelectedNode(null);

    const files = data.files;
    const edges = data.dependency_edges || [];
    const { fileToGroup, groupColors } = activeGrouping;

    // Determine which files to show
    let nodePaths = Object.keys(files);

    // Filter out isolated if not showing them
    if (!showIsolated) {
      const connectedFiles = new Set();
      for (const [src, tgt] of edges) {
        connectedFiles.add(src);
        connectedFiles.add(tgt);
      }
      nodePaths = nodePaths.filter((p) => connectedFiles.has(p));
    }

    const nodeSet = new Set(nodePaths);

    // Build nodes
    let maxPagerank = 0;
    for (const path of nodePaths) {
      const pr = files[path].pagerank || 0;
      if (pr > maxPagerank) maxPagerank = pr;
    }

    const nodes = nodePaths.map((path) => {
      const f = files[path];
      const group = fileToGroup[path] || "other";
      const color = groupColors[group] || ISOLATED_COLOR;
      const hasFindings = (f.finding_count || 0) > 0;
      const isOrphan = f.is_orphan || f.signals?.is_orphan;

      return {
        data: {
          id: path,
          label: path.split("/").pop(),
          group,
          nodeColor: isOrphan ? ISOLATED_COLOR : color,
          nodeSize: maxPagerank > 0
            ? Math.max(14, Math.sqrt((f.pagerank || 0) / maxPagerank) * 40 + 10)
            : 18,
          hasBorder: hasFindings,
          isOrphan,
          pagerank: f.pagerank || 0,
          risk_score: f.risk_score || 0,
          finding_count: f.finding_count || 0,
        },
      };
    });

    // Build edges (only between visible nodes)
    const edgeElements = edges
      .filter(([src, tgt]) => nodeSet.has(src) && nodeSet.has(tgt))
      .map(([src, tgt], i) => ({
        data: { id: `e${i}`, source: src, target: tgt },
      }));

    // Count groups actually in view
    const groupsInView = new Set(nodes.map((n) => n.data.group));

    setStats({
      nodes: nodes.length,
      edges: edgeElements.length,
      groups: groupsInView.size,
    });

    if (nodes.length === 0) {
      setLoading(false);
      return;
    }

    requestAnimationFrame(() => {
      if (!containerRef.current) return;

      const cy = cytoscape({
        container: containerRef.current,
        elements: [...nodes, ...edgeElements],
        layout: {
          name: "dagre",
          rankDir: "LR",
          nodeSep: 40,
          rankSep: 80,
          animate: false,
        },
        style: getStyles(),
        minZoom: 0.1,
        maxZoom: 3,
        wheelSensitivity: 0.2,
        pixelRatio: 1, // Performance optimization
      });

      // Node click
      cy.on("tap", "node", (evt) => {
        const node = evt.target;
        const d = node.data();
        const fileData = data.files[d.id] || {};
        const signals = fileData.signals || {};

        // Get findings for this file
        const findings = [];
        for (const cat of Object.values(data.categories || {})) {
          for (const f of cat.findings || []) {
            if (f.files?.includes(d.id)) findings.push(f);
          }
        }

        setSelectedNode({
          path: d.id,
          group: d.group,
          groupColor: d.nodeColor,
          health: fileData.health,
          role: fileData.role,
          lines: fileData.lines,
          pagerank: d.pagerank,
          riskScore: d.risk_score,
          findingCount: d.finding_count,
          inDegree: signals.in_degree,
          outDegree: signals.out_degree,
          blastRadius: fileData.blast_radius,
          isOrphan: d.isOrphan,
          findings: findings.slice(0, 5),
        });

        // Highlight neighborhood
        cy.batch(() => {
          cy.elements().removeClass("faded highlighted");
          const neighborhood = node.neighborhood().add(node);
          cy.elements().not(neighborhood).addClass("faded");
          neighborhood.addClass("highlighted");
        });
      });

      // Background click
      cy.on("tap", (evt) => {
        if (evt.target === cy) {
          setSelectedNode(null);
          setHighlightedGroup(null);
          cy.elements().removeClass("faded highlighted dimmed");
        }
      });

      cyRef.current = cy;

      setTimeout(() => {
        cy.fit(null, 30);
        setLoading(false);
      }, 100);
    });
  }, [data, viewMode, showIsolated, activeGrouping]);

  // Highlight group from legend
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    if (highlightedGroup === null) {
      cy.elements().removeClass("dimmed highlighted");
      return;
    }

    cy.batch(() => {
      cy.nodes().forEach((node) => {
        if (node.data("group") === highlightedGroup) {
          node.removeClass("dimmed").addClass("highlighted");
        } else {
          node.removeClass("highlighted").addClass("dimmed");
        }
      });

      cy.edges().forEach((edge) => {
        const srcGroup = edge.source().data("group");
        const tgtGroup = edge.target().data("group");
        if (srcGroup === highlightedGroup || tgtGroup === highlightedGroup) {
          edge.removeClass("dimmed");
        } else {
          edge.addClass("dimmed");
        }
      });
    });
  }, [highlightedGroup]);

  useEffect(() => {
    initGraph();
    return () => cyRef.current?.destroy();
  }, [initGraph]);

  // Zoom controls
  const zoomIn = () => {
    const cy = cyRef.current;
    if (cy) cy.zoom({ level: cy.zoom() * 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  };
  const zoomOut = () => {
    const cy = cyRef.current;
    if (cy) cy.zoom({ level: cy.zoom() / 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  };
  const fitGraph = () => cyRef.current?.fit(undefined, 30);

  if (!data) return null;

  const globalSignals = data.global_signals || {};
  const totalFiles = Object.keys(data.files || {}).length;
  const isolatedCount = Object.values(data.files || {}).filter(
    (f) => f.is_orphan || f.signals?.is_orphan
  ).length;

  return (
    <div className="graph-screen-v2">
      {/* Toolbar */}
      <header className="graph-toolbar">
        <div className="graph-toolbar-section">
          <span className="graph-toolbar-label">Group by</span>
          <div className="graph-btn-group">
            <button
              className={viewMode === "modules" ? "active" : ""}
              onClick={() => setViewMode("modules")}
            >
              Modules ({moduleGroups.groups.length})
            </button>
            <button
              className={viewMode === "communities" ? "active" : ""}
              onClick={() => setViewMode("communities")}
            >
              Communities ({communityGroups.groups.length})
            </button>
          </div>
        </div>

        <div className="graph-toolbar-section">
          <label className="graph-checkbox">
            <input
              type="checkbox"
              checked={showIsolated}
              onChange={(e) => setShowIsolated(e.target.checked)}
            />
            <span>Show isolated ({isolatedCount})</span>
          </label>
        </div>

        <div className="graph-toolbar-stats">
          <span>{stats.nodes} / {totalFiles} files</span>
          <span>{stats.edges} edges</span>
          <span>{stats.groups} groups</span>
          {globalSignals.modularity != null && (
            <span title="Louvain modularity">Q={globalSignals.modularity.toFixed(2)}</span>
          )}
        </div>
      </header>

      {/* Main */}
      <div className="graph-content">
        {/* Legend sidebar */}
        <aside className="graph-sidebar">
          <div className="graph-legend-v2">
            <h3>{viewMode === "modules" ? "Modules" : "Communities"}</h3>
            <p className="graph-legend-subtitle">
              Click to highlight group
            </p>

            <div className="graph-legend-items">
              {activeGrouping.groups.slice(0, 15).map((g) => (
                <button
                  key={g.name}
                  className={`graph-legend-row ${highlightedGroup === g.name ? "active" : ""}`}
                  onClick={() => setHighlightedGroup(highlightedGroup === g.name ? null : g.name)}
                >
                  <span
                    className="graph-legend-color"
                    style={{ background: activeGrouping.groupColors[g.name] }}
                  />
                  <span className="graph-legend-label" title={g.name}>
                    {g.name.length > 25 ? "..." + g.name.slice(-22) : g.name}
                  </span>
                  <span className="graph-legend-count">{g.count}</span>
                </button>
              ))}

              {activeGrouping.groups.length > 15 && (
                <div className="graph-legend-more">
                  +{activeGrouping.groups.length - 15} more
                </div>
              )}
            </div>

            {highlightedGroup && (
              <button
                className="graph-legend-clear"
                onClick={() => setHighlightedGroup(null)}
              >
                Clear highlight
              </button>
            )}
          </div>

          {/* Metrics */}
          <div className="graph-metrics">
            <h3>Graph Metrics</h3>
            <div className="graph-metrics-list">
              <div className="graph-metric-row">
                <span>Centrality Gini</span>
                <span>{globalSignals.centrality_gini?.toFixed(3) || "—"}</span>
              </div>
              <div className="graph-metric-row">
                <span>Orphan Ratio</span>
                <span>{globalSignals.orphan_ratio != null ? (globalSignals.orphan_ratio * 100).toFixed(1) + "%" : "—"}</span>
              </div>
              <div className="graph-metric-row">
                <span>Cycles</span>
                <span>{globalSignals.cycle_count ?? "—"}</span>
              </div>
              <div className="graph-metric-row">
                <span>Connectivity</span>
                <span>{globalSignals.fiedler_value?.toFixed(3) || "—"}</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Graph canvas */}
        <main className="graph-viewport-v2">
          {loading && (
            <div className="graph-loading-overlay">
              <div className="graph-spinner" />
              <span>Laying out graph...</span>
            </div>
          )}

          <div
            ref={containerRef}
            className="graph-canvas"
            style={{ opacity: loading ? 0 : 1 }}
          />

          {/* Zoom controls */}
          <div className="graph-zoom">
            <button onClick={zoomIn} title="Zoom in">+</button>
            <button onClick={zoomOut} title="Zoom out">−</button>
            <button onClick={fitGraph} title="Fit">⊡</button>
          </div>

          {/* Empty state */}
          {!loading && stats.nodes === 0 && (
            <div className="graph-empty-state">
              <div className="graph-empty-icon">🔗</div>
              <h3>No connected files</h3>
              <p>
                {showIsolated
                  ? "No files found."
                  : `${isolatedCount} isolated files hidden. Enable "Show isolated" to see them.`}
              </p>
            </div>
          )}

          {/* Selected node panel */}
          {selectedNode && (
            <div className="graph-node-panel">
              <header className="graph-panel-header">
                <span className="graph-panel-path" title={selectedNode.path}>
                  {selectedNode.path}
                </span>
                <button
                  className="graph-panel-close"
                  onClick={() => {
                    setSelectedNode(null);
                    cyRef.current?.elements().removeClass("faded highlighted");
                  }}
                >
                  ×
                </button>
              </header>

              <div className="graph-panel-meta">
                {selectedNode.role && (
                  <span className="graph-panel-tag">{selectedNode.role}</span>
                )}
                {selectedNode.isOrphan && (
                  <span className="graph-panel-tag orphan">Orphan</span>
                )}
                <span
                  className="graph-panel-tag"
                  style={{ background: selectedNode.groupColor, color: "#000" }}
                >
                  {selectedNode.group.length > 20
                    ? "..." + selectedNode.group.slice(-17)
                    : selectedNode.group}
                </span>
              </div>

              <div className="graph-panel-grid">
                {selectedNode.health != null && (
                  <div className="graph-panel-stat">
                    <span className="value">{selectedNode.health.toFixed(1)}</span>
                    <span className="label">Health</span>
                  </div>
                )}
                <div className="graph-panel-stat">
                  <span className="value">{selectedNode.riskScore?.toFixed(2) || "—"}</span>
                  <span className="label">Risk</span>
                </div>
                <div className="graph-panel-stat">
                  <span className="value">{selectedNode.inDegree ?? "—"}</span>
                  <span className="label">In</span>
                </div>
                <div className="graph-panel-stat">
                  <span className="value">{selectedNode.outDegree ?? "—"}</span>
                  <span className="label">Out</span>
                </div>
              </div>

              {selectedNode.findings.length > 0 && (
                <div className="graph-panel-findings">
                  <strong>Issues ({selectedNode.findingCount})</strong>
                  {selectedNode.findings.map((f, i) => (
                    <div key={i} className="graph-panel-finding">
                      <span className={`dot sev-${f.severity_label?.toLowerCase() || "info"}`} />
                      {f.label || f.finding_type}
                    </div>
                  ))}
                </div>
              )}

              <a
                href={`#files/${encodeURIComponent(selectedNode.path)}`}
                className="graph-panel-link"
              >
                View details →
              </a>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

/**
 * Cytoscape styles - HIGH CONTRAST
 */
function getStyles() {
  return [
    {
      selector: "node",
      style: {
        "background-color": "data(nodeColor)",
        width: "data(nodeSize)",
        height: "data(nodeSize)",
        label: "data(label)",
        "font-size": "10px",
        "font-family": "'JetBrains Mono', monospace",
        "font-weight": "500",
        color: "#f8fafc", // Very light text
        "text-valign": "bottom",
        "text-margin-y": 4,
        "text-halign": "center",
        "text-max-width": "80px",
        "text-wrap": "ellipsis",
        "text-outline-color": "#0f172a",
        "text-outline-width": 2,
        "border-width": (ele) => (ele.data("hasBorder") ? 3 : 0),
        "border-color": FINDING_BORDER,
        opacity: 0.95,
      },
    },
    {
      selector: "edge",
      style: {
        width: 1.5,
        "line-color": EDGE_COLOR,
        "target-arrow-color": EDGE_COLOR,
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        opacity: 0.6,
        "arrow-scale": 0.7,
      },
    },
    {
      selector: "node.highlighted",
      style: {
        opacity: 1,
        "border-width": 3,
        "border-color": "#ffffff",
        "z-index": 999,
      },
    },
    {
      selector: "node.faded, node.dimmed",
      style: {
        opacity: 0.15,
        "text-opacity": 0,
      },
    },
    {
      selector: "edge.faded, edge.dimmed",
      style: {
        opacity: 0.08,
      },
    },
  ];
}
